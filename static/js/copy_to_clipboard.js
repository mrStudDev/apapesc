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
      showToast("Texto copiado!");
    } else {
      showToast("Falha ao copiar o texto.");
    }
  } catch (err) {
    console.error("Erro ao copiar: ", err);
    showToast("Erro ao copiar o texto.");
  }

  document.body.removeChild(textArea);
}

// ✅ Exibe a mensagem no centro da tela
function showToast(message) {
  var toast = document.createElement("div");
  toast.textContent = message;
  toast.style.position = "fixed";
  toast.style.top = "50%";
  toast.style.left = "50%";
  toast.style.transform = "translate(-50%, -50%)"; // 🔥 Centraliza na tela
  toast.style.background = "#333";
  toast.style.color = "#fff";
  toast.style.padding = "15px 30px";
  toast.style.borderRadius = "8px";
  toast.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.2)";
  toast.style.opacity = "0.9";
  toast.style.fontSize = "16px";
  toast.style.textAlign = "center";
  toast.style.transition = "opacity 0.5s ease-in-out";

  document.body.appendChild(toast);

  // 🔥 Remove a mensagem após 2 segundos
  setTimeout(function () {
    toast.style.opacity = "0";
    setTimeout(function () {
      document.body.removeChild(toast);
    }, 500);
  }, 2300);
}

