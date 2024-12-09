document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("alertModal");
    const closeModal = document.getElementById("closeModal");
    const modalMessage = document.getElementById("modalMessage");

    // Verifica se há mensagens no contexto (vindo do Django)
    const messageElement = document.querySelector(".django-message");
    if (messageElement) {
        modalMessage.textContent = messageElement.textContent; // Define a mensagem no modal
        modal.classList.remove("hidden"); // Mostra o modal
    }

    // Fecha o modal ao clicar no botão
    closeModal.addEventListener("click", function () {
        modal.classList.add("hidden");
    });
});
