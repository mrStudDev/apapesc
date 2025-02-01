// static/js/copy_to_clipboard.js

function copyToClipboard(elementId) {
  var text = document.getElementById(elementId).textContent;

  var textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed"; // Evita rolagem da página
  textArea.style.left = "-9999px";
  document.body.appendChild(textArea);
  textArea.select();

  try {
    var successful = document.execCommand('copy');
    if (successful) {
      alert("Texto copiado: " + text);
    } else {
      alert("Falha ao copiar o texto.");
    }
  } catch (err) {
    console.error("Erro ao copiar: ", err);
    alert("Erro ao copiar o texto.");
  }

  document.body.removeChild(textArea);
}
