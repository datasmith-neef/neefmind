import streamlit as st
import re
import urllib.parse
from collections import Counter
from llm import WebpageSummarizer  # Importiere die Klasse für Zusammenfassungen

# Seitenkonfiguration
st.set_page_config(
    page_title="SmithMind POC",
    page_icon=":memo:",
    layout="wide"
)

# OpenAI API-Key aus Streamlit Secrets
api_key = st.secrets["secrets"].get("openaikey")

# Initialisiere den Summarizer
summarizer = WebpageSummarizer(api_key)

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

# 🎯 Sidebar für das Hinzufügen neuer Notizen
with st.sidebar:
    st.header("📝 Neue Notiz hinzufügen")
    # Widgets mit eigenen Keys, sodass die Werte über session_state abrufbar und änderbar sind
    title = st.text_input("Titel der Notiz", value=st.session_state.get("title", default_title), key="title")
    content = st.text_area("Inhalt der Notiz", value=st.session_state.get("content", default_content), key="content")
    link = st.text_input("Link (optional)", value=st.session_state.get("link", default_link), key="link")
    uploaded_file = st.file_uploader("Dokument hochladen (optional)", type=["txt", "pdf"], key="uploaded_file")

    if st.button("➕ Notiz speichern"):
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
        st.success("✅ Notiz wurde gespeichert.")

        # Nach dem Speichern die Eingabefelder zurücksetzen:
        st.session_state.title = ""
        st.session_state.content = ""
        st.session_state.link = ""
        # Das Zurücksetzen des File Uploaders funktioniert nicht immer, hier könnte ein
        # st.experimental_rerun() helfen, wenn Sie die komplette Seite neu laden möchten.
        # st.experimental_rerun()

# 📌 Hauptinhalt: Anzeige der gespeicherten Notizen
st.title("📚 SmithMind Notizen")

st.header("🔍 Suche nach Notizen")
query = st.text_input("Suchbegriff eingeben...")

# 🔎 Suchfunktion
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

# 📌 Alle Notizen anzeigen
st.header("📌 Gespeicherte Notizen")
for note in st.session_state.notes:
    st.subheader(note["title"])
    st.write(note["content"])
    if note["link"]:
        st.write("🔗 Link:", note["link"])
    st.write("🏷 Tags:", ", ".join(note["tags"]))
