document.getElementById('addPage').addEventListener('click', async () => {
  // Ruft die aktive Registerkarte ab
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  let title = tab.title;
  let url = tab.url;

  // Lese den aktuell ausgewählten Text aus der Seite
  let [result] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => window.getSelection().toString(),
  });
  let selectedText = result.result || document.querySelector("meta[name='description']")?.content || "";


  // URL-Kodierung der Parameter
  let targetURL = `https://neefmind-pwstwe23bs7eeqw3tsgvxf.streamlit.app/?title=${encodeURIComponent(title)}&text=${encodeURIComponent(selectedText)}&url=${encodeURIComponent(url)}`;
  
  // Öffnet eure SmithMind-App in einem neuen Tab
  chrome.tabs.create({ url: targetURL });alert("Seite erfolgreich zu SmithMind hinzugefügt!");

});
