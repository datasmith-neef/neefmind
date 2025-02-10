import streamlit as st
import re
import urllib.parse
import json
from collections import Counter
from llm import WebpageSummarizer  # Importiere die Klasse für Zusammenfassungen

# Seitenkonfiguration
st.set_page_config(
    page_title="SmithMind POC",
    page_icon=":memo:",
    layout="wide"
)

# OpenAI API-Key aus Streamlit Secrets
api_key = st.secrets["secrets"].get("openai_api_key")
summarizer = WebpageSummarizer(api_key)  # Summarizer initialisieren

# Funktion zur Tag-Generierung
def generate_tags(text, num_tags=5):
    words = re.findall(r'\w+', text.lower())
    stopwords = {"der", "die", "das", "und", "oder", "aber", "mit", "auf", "für", "von", "in",
                 "den", "dem", "ein", "eine", "als", "auch", "an", "ist", "im", "am"}
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    freq = Counter(filtered)
    return [word for word, count in freq.most_common(num_tags)]


# URL-Parameter auslesen
query_params = st.query_params
default_title = urllib.parse.unquote(query_params.get("title", ""))
default_content = urllib.parse.unquote(query_params.get("text", ""))
default_link = urllib.parse.unquote(query_params.get("url", ""))

# Falls kein Inhalt übergeben wurde, erstelle eine Zusammenfassung der Webseite
if not default_content and default_link:
    default_content = summarizer.summarize(default_link)

# Session-State initialisieren
if "notes" not in st.session_state:
    st.session_state.notes = []

# Funktion zum Speichern von Notizen als JSON
def save_notes_to_file():
    with open("notizen.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.notes, f, ensure_ascii=False, indent=4)

# Funktion zum Laden von Notizen beim Start
def load_notes_from_file():
    try:
        with open("notizen.json", "r", encoding="utf-8") as f:
            st.session_state.notes = json.load(f)
    except FileNotFoundError:
        st.session_state.notes = []

# Lade gespeicherte Notizen beim Start
load_notes_from_file()

# 🔹 **Seitenleiste für neue Notizen**
with st.sidebar:
    st.header("Neue Notiz hinzufügen")
    title = st.text_input("Titel der Notiz", value=default_title)
    content = st.text_area("Inhalt der Notiz", value=default_content)  
    link = st.text_input("Link (optional)", value=default_link)
    uploaded_file = st.file_uploader("Dokument hochladen (optional)", type=["txt", "pdf"])

    if st.button("Notiz speichern"):
        full_text = content  # Stelle sicher, dass der Inhalt immer initialisiert wird

        if uploaded_file is not None:
            try:
                file_content = uploaded_file.read().decode("utf-8", errors="ignore")
            except Exception:
                file_content = ""
            full_text += "\n" + file_content

        tags = generate_tags(full_text + " " + link)  # Tags auch aus der URL generieren
        note = {"title": title, "content": full_text, "link": link, "tags": tags}
        st.session_state.notes.append(note)
        save_notes_to_file()  # Notiz speichern
        st.success("Notiz wurde gespeichert.")

# 🔹 **Hauptfenster: Anzeige der gespeicherten Notizen**
st.title("Gespeicherte Notizen")

# Einfache Suchfunktion
query = st.text_input("🔍 Suchbegriff eingeben")
if query:
    results = [note for note in st.session_state.notes if 
               query.lower() in note["title"].lower() or 
               query.lower() in note["content"].lower() or 
               query.lower() in " ".join(note["tags"]).lower()]
    
    if results:
        st.subheader(f"🔎 {len(results)} Ergebnisse gefunden:")
        for note in results:
            st.subheader(note["title"])
            st.write(note["content"])
            if note["link"]:
                st.write("🔗 Link:", note["link"])
            st.write("🏷 Tags:", ", ".join(note["tags"]))
    else:
        st.warning("Keine passenden Notizen gefunden.")
else:
    # Falls keine Suche aktiv ist, zeige alle Notizen an
    for note in st.session_state.notes:
        st.subheader(note["title"])
        st.write(note["content"])
        if note["link"]:
            st.write("🔗 Link:", note["link"])
        st.write("🏷 Tags:", ", ".join(note["tags"]))

# 🔹 **Download gespeicherter Notizen**
st.sidebar.subheader("📥 Notizen herunterladen")
if st.sidebar.button("Notizen als JSON speichern"):
    with open("notizen.json", "rb") as f:
        st.sidebar.download_button("📂 JSON herunterladen", f, file_name="notizen.json")

if st.sidebar.button("Notizen als TXT speichern"):
    with open("notizen.txt", "w", encoding="utf-8") as f:
        for note in st.session_state.notes:
            f.write(f"🔹 {note['title']}\n{note['content']}\n🔗 {note['link']}\n🏷 {', '.join(note['tags'])}\n\n")
    with open("notizen.txt", "rb") as f:
        st.sidebar.download_button("📂 TXT herunterladen", f, file_name="notizen.txt")
