import streamlit as st
import re
from collections import Counter
# test
# Seitenkonfiguration
st.set_page_config(
    page_title="SmithMind POC",
    page_icon=":memo:",
    layout="wide"
)

# Manifest-Link in den HTML-Code einfügen
st.markdown(
    """
    <link rel="manifest" href="/manifest.json">
    """,
    unsafe_allow_html=True
)

# Funktion zur Tag-Generierung
def generate_tags(text, num_tags=5):
    words = re.findall(r'\w+', text.lower())
    stopwords = {"der", "die", "das", "und", "oder", "aber", "mit", "auf", "für", "von", "in",
                 "den", "dem", "ein", "eine", "als", "auch", "an", "ist", "im", "am"}
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    freq = Counter(filtered)
    return [word for word, count in freq.most_common(num_tags)]


# URL-Parameter (vom Share Target) auslesen
import urllib.parse

query_params = st.query_params

# Sicherstellen, dass Werte als Strings verarbeitet werden
default_title = urllib.parse.unquote(query_params.get("title", ""))
default_content = urllib.parse.unquote(query_params.get("text", ""))
default_link = urllib.parse.unquote(query_params.get("url", ""))


text_list = query_params.get("text", [])
default_content = text_list[0] if len(text_list) > 0 else ""

url_list = query_params.get("url", [])
default_link = url_list[0] if len(url_list) > 0 else ""


# Session-State initialisieren
if "notes" not in st.session_state:
    st.session_state.notes = []

# Anwendungstitel
st.title("SmithMind POC")

# Notizerfassung
st.header("Neue Notiz hinzufügen")
title = st.text_input("Titel der Notiz", default_title)
content = st.text_area("Inhalt der Notiz", default_content)
link = st.text_input("Link (optional)", default_link)
uploaded_file = st.file_uploader("Dokument hochladen (optional)", type=["txt", "pdf"])

if st.button("Notiz speichern"):
    full_text = content
if uploaded_file is not None:
    try:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception:
        file_content = ""
    full_text += "\n" + file_content

    tags = generate_tags(full_text + " " + link)  # Tags auch aus der URL generieren
    note = {"title": title, "content": content, "link": link, "tags": tags}
    st.session_state.notes.append(note)
    st.success("Notiz wurde gespeichert.")

# Anzeige der gespeicherten Notizen
st.header("Gespeicherte Notizen")
for note in st.session_state.notes:
    st.subheader(note["title"])
    st.write(note["content"])
    if note["link"]:
        st.write("Link:", note["link"])
    st.write("Tags:", ", ".join(note["tags"]))

# Einfache Suchfunktion
st.header("Suche")
query = st.text_input("Suchbegriff")
if query:
    results = []
    for note in st.session_state.notes:
        if (query.lower() in note["title"].lower() or 
            query.lower() in note["content"].lower() or 
            query.lower() in " ".join(note["tags"]).lower()):
            results.append(note)
    st.subheader("Ergebnisse")
    for note in results:
        st.subheader(note["title"])
        st.write(note["content"])
        if note["link"]:
            st.write("Link:", note["link"])
        st.write("Tags:", ", ".join(note["tags"]))
