function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function deletarDocumento(element) {
    if (!confirm('Tem certeza de que deseja excluir este documento?')) {
        return;
    }

    const url = element.getAttribute('data-url');
    const documentoId = element.closest('li').dataset.id;

    const csrfToken = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            document.getElementById(`documento-${documentoId}`).remove();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Erro ao excluir documento:', error);
        alert('Ocorreu um erro ao tentar excluir o documento.');
    });
}
