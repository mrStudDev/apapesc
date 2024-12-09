// Função para obter o CSRF token dos cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Verifica se o cookie começa com o nome desejado
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function alterarStatus(tarefaId, novoStatus) {
    const csrfToken = getCookie('csrftoken');
    const url = `/tarefas/board/${tarefaId}/alterar-status/`;
    const data = { status: novoStatus };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data),
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(data => {
                throw new Error(data.message || 'Erro ao alterar o status.');
            });
        }
    })
    .then(result => {
        if (result.success) {
            moverTarefaParaColuna(tarefaId, novoStatus);
        } else {
            alert(result.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert(error.message || 'Erro ao alterar o status.');
    });
}

function moverTarefaParaColuna(tarefaId, novoStatus) {
    const card = document.getElementById('card-' + tarefaId);
    if (card) {
        card.parentNode.removeChild(card);
        const coluna = document.getElementById('coluna-' + novoStatus);
        if (coluna) {
            coluna.querySelector('.coluna-conteudo').appendChild(card);
        }
    }
}



function moverTarefaParaColuna(tarefaId, novoStatus) {
    const card = document.getElementById('card-' + tarefaId);
    if (card) {
        card.parentNode.removeChild(card);
        const coluna = document.getElementById('coluna-' + novoStatus);
        if (coluna) {
            coluna.querySelector('.coluna-conteudo').insertAdjacentElement('afterbegin', card);
            // Atualiza os botões de status no card
            atualizarBotoesStatus(card, novoStatus);
        }
    }
}
function atualizarBotoesStatus(card, novoStatus) {
    // Implementar lógica para atualizar os botões no card
    // Por exemplo, remover o botão do status atual e adicionar os outros
    // Isso pode ser complexo e pode ser mais simples recarregar a página
    location.reload(); // Recarrega a página para atualizar os botões
}
