function copyToClipboard(elementId) {
  const text = document.getElementById(elementId).textContent;

  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-9999px";
  document.body.appendChild(textArea);
  textArea.select();

  try {
    const successful = document.execCommand("copy");

    if (successful) {
      const button = document.querySelector(
        `button[onclick="copyToClipboard('${elementId}')"]`
      );
      if (button) showCheckIcon(button);
    } else {
      console.warn("Falha ao copiar");
    }
  } catch (err) {
    console.error("Erro ao copiar:", err);
  }

  document.body.removeChild(textArea);
}

function showCheckIcon(triggerElement) {
  // Já existe o ícone?
  if (triggerElement.querySelector(".copy-check")) return;

  const icon = document.createElement("span");
  icon.textContent = "✔️";
  icon.className = "copy-check";
  icon.style.color = "green";
  icon.style.marginLeft = "6px";
  icon.style.fontSize = "12px";
  icon.style.opacity = "0.85";
  icon.style.transition = "opacity 0.3s ease";

  triggerElement.appendChild(icon);

  setTimeout(() => {
    icon.style.opacity = "0";
    setTimeout(() => {
      triggerElement.removeChild(icon);
    }, 300);
  }, 1200);
}
