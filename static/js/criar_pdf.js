// static/js/criar_pdf.js

// Função para criar uma cópia em PDF
function criarCopiaPDF(documentoId) {
    fetch(`/documentos/criar_pdf/${documentoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken, // Pega o token do script injetado
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload(); // Atualiza a página se necessário
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Erro ao criar PDF:', error);
        alert('Ocorreu um erro ao tentar criar o PDF.');
    });
}
