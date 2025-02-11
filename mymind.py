import streamlit as st
import sqlite3
import hashlib
import re
import urllib.parse
from collections import Counter
from llm import WebpageSummarizer  # Importiere die Klasse für Zusammenfassungen

# Seitenkonfiguration
st.set_page_config(page_title="SmithMind POC", page_icon=":memo:", layout="wide")

# ─────────────────────────────────────────────────────────────
# SQLite Datenbankfunktionen zur persistente Speicherung der Nutzer
# ─────────────────────────────────────────────────────────────
def create_connection(db_file="users.db"):
    # check_same_thread=False erlaubt den DB-Zugriff aus verschiedenen Threads
    conn = sqlite3.connect(db_file, check_same_thread=False)
    return conn

def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    );
    """
    conn.execute(sql)
    conn.commit()

def add_user(username, hashed_password, conn):
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

# Hilfsfunktion zum Hashen von Passwörtern
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# SQLite-Datenbank initialisieren
conn = create_connection()
create_table(conn)

# ─────────────────────────────────────────────────────────────
# Session-State initialisieren für Login-Status und aktuellen Nutzer
# ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# ─────────────────────────────────────────────────────────────
# Kopfzeile: Linke Spalte zeigt den App-Titel, rechte Spalte den Authentifizierungsbereich
# ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📚 SmithMind Notizen")
with col2:
    if st.session_state["logged_in"]:
        st.markdown(f"**Angemeldet als:** {st.session_state['current_user']}")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["current_user"] = None
    else:
        st.subheader("Login / Signup")
        # Auswahl zwischen Login und Signup per horizontalem Radio-Button
        auth_mode = st.radio("", ["Login", "Signup"], key="auth_mode", horizontal=True)
        if auth_mode == "Signup":
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Passwort", type="password", key="signup_password")
            if st.button("Konto erstellen", key="signup_button"):
                if not new_username or not new_password:
                    st.error("Bitte beide Felder ausfüllen.")
                else:
                    hashed_pw = hash_password(new_password)
                    if add_user(new_username, hashed_pw, conn):
                        st.success("Konto erfolgreich erstellt!")
                    else:
                        st.error("Username existiert bereits!")
        else:  # Login
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")
            if st.button("Einloggen", key="login_button"):
                user = get_user(username, conn)
                if user and user[1] == hash_password(password):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = username
                    st.success("Erfolgreich eingeloggt!")
                else:
                    st.error("Ungültige Anmeldedaten.")

# ─────────────────────────────────────────────────────────────
# Hauptinhalt: Notizenverwaltung (nur für eingeloggte Nutzer sichtbar)
# ─────────────────────────────────────────────────────────────
if st.session_state["logged_in"]:
    # OpenAI API-Key aus Streamlit Secrets
    api_key = st.secrets["secrets"].get("openaikey")
    # Initialisiere den Webpage-Summarizer
    summarizer = WebpageSummarizer(api_key)

    # Hilfsfunktion zur Tag-Generierung
    def generate_tags(text, num_tags=5):
        words = re.findall(r'\w+', text.lower())
        stopwords = {"der", "die", "das", "und", "oder", "aber", "mit", "auf", "für", "von", "in",
                     "den", "dem", "ein", "eine", "als", "auch", "an", "ist", "im", "am"}
        filtered = [w for w in words if w not in stopwords and len(w) > 3]
        freq = Counter(filtered)
        return [word for word, count in freq.most_common(num_tags)]

    # URL-Parameter auslesen
    query_params = st.query_params
    # Sidebar-Zähler initialisieren: Wird genutzt, um dynamische Widget-Keys zu erzeugen
    if "sidebar_counter" not in st.session_state:
        st.session_state.sidebar_counter = 0

    if st.session_state.sidebar_counter == 0:
        default_title = urllib.parse.unquote(query_params.get("title", ""))
        default_content = urllib.parse.unquote(query_params.get("text", ""))
        default_link = urllib.parse.unquote(query_params.get("url", ""))
    else:
        default_title = ""
        default_content = ""
        default_link = ""

    # Falls kein Inhalt übergeben wurde, kann (optional) eine Zusammenfassung generiert werden
    if not default_content and default_link:
        default_content = summarizer.summarize(default_link)

    if "notes" not in st.session_state:
        st.session_state.notes = []

    # ───────────────────────────────
    # Sidebar: Neue Notiz hinzufügen (mit dynamischen Keys, um die Felder nach dem Speichern zu leeren)
    # ───────────────────────────────
    with st.sidebar:
        st.header("📝 Neue Notiz hinzufügen")
        counter = st.session_state.sidebar_counter
        title = st.text_input("Titel der Notiz", value=default_title, key=f"title_{counter}")
        content = st.text_area("Inhalt der Notiz", value=default_content, key=f"content_{counter}")
        link = st.text_input("Link (optional)", value=default_link, key=f"link_{counter}")
        uploaded_file = st.file_uploader("Dokument hochladen (optional)", type=["txt", "pdf"], key=f"uploaded_file_{counter}")
        if st.button("➕ Notiz speichern", key="save_note"):
            full_text = content
            if uploaded_file is not None:
                try:
                    file_content = uploaded_file.read().decode("utf-8", errors="ignore")
                except Exception:
                    file_content = ""
                full_text += "\n" + file_content
            tags = generate_tags(full_text + " " + link)
            note = {"title": title, "content": full_text, "link": link, "tags": tags}
            st.session_state.notes.append(note)
            st.success("✅ Notiz wurde gespeichert.")
            st.session_state.sidebar_counter += 1

    # ───────────────────────────────
    # Hauptinhalt: Suche und Anzeige der Notizen
    # ───────────────────────────────
    st.header("🔍 Suche nach Notizen")
    query = st.text_input("Suchbegriff eingeben...", key="search_query")
    if query:
        results = []
        for note in st.session_state.notes:
            if (query.lower() in note["title"].lower() or
                query.lower() in note["content"].lower() or
                query.lower() in " ".join(note["tags"]).lower()):
                results.append(note)
        st.subheader("🔎 Suchergebnisse")
        for note in results:
            st.subheader(note["title"])
            st.write(note["content"])
            if note["link"]:
                st.write("🔗 Link:", note["link"])
            st.write("🏷 Tags:", ", ".join(note["tags"]))

    st.header("📌 Gespeicherte Notizen")
    for note in st.session_state.notes:
        st.subheader(note["title"])
        st.write(note["content"])
        if note["link"]:
            st.write("🔗 Link:", note["link"])
        st.write("🏷 Tags:", ", ".join(note["tags"]))
else:
    st.info("Bitte loggen Sie sich oben rechts ein, um die App zu nutzen.")
