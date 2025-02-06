document.getElementById('addPage').addEventListener('click', async () => {
  // Ruft die aktive Registerkarte ab
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  let title = encodeURIComponent(tab.title);
  let url = encodeURIComponent(tab.url);
  // Optional: Hier könnte auch ausgewählter Text erfasst werden; vorerst setzen wir ihn leer
  let text = '';
  
  // Hier wurde der Link zu Eurer App eingefügt
  let targetURL = `https://smithmind.streamlit.app/?title=${title}&text=${text}&url=${url}`;
  
  // Öffnet die SmithMind-App in einem neuen Tab
  chrome.tabs.create({ url: targetURL });
});

  