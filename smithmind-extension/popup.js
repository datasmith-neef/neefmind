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
  let selectedText = result.result; // Falls nichts ausgewählt wurde, ist dies ein leerer String

  // URL-Kodierung der Parameter
  let targetURL = `https://smithmind.streamlit.app/?title=${encodeURIComponent(title)}&text=${encodeURIComponent(selectedText)}&url=${encodeURIComponent(url)}`;
  
  // Öffnet eure SmithMind-App in einem neuen Tab
  chrome.tabs.create({ url: targetURL });
});
