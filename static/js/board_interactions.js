// board_interactions.js

function getCSRFToken() {
    // Busca o csrftoken no cookie (típico em Django)
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
  }
  
  // Exemplo simples de clique para mudar status
  function alterarStatus(tarefaId, novoStatus) {
    const url = `/tarefas/board/${tarefaId}/alterar-status-board/`;
    const csrfToken = getCSRFToken();
  
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ status: novoStatus }),
      credentials: 'same-origin',
    })
    .then(response => {
      if (!response.ok) {
        // Tenta extrair JSON de erro
        return response.json().then(data => {
          throw new Error(data.message || 'Erro ao alterar o status');
        });
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        moverCardParaNovaColuna(tarefaId, novoStatus);
      } else {
        alert(data.message);
      }
    })
    .catch(error => {
      console.error(error);
      alert('Ocorreu um erro: ' + error.message);
    });
  }
  
  function moverCardParaNovaColuna(tarefaId, novoStatus) {
    // Remove o card da coluna antiga
    const card = document.getElementById('card-' + tarefaId);
    if (!card) return;
  
    // Remove o card do DOM
    card.parentNode.removeChild(card);
  
    // Encontra a coluna alvo (exemplo: "coluna-pendente", "coluna-em_andamento"...)
    const colunaDestino = document.getElementById('coluna-' + novoStatus);
    if (!colunaDestino) return;
  
    // Move o card para a coluna destino
    const colunaConteudo = colunaDestino.querySelector('.coluna-conteudo');
    colunaConteudo.insertAdjacentElement('afterbegin', card);
    
    // Opcional: atualizar botões, recarregar página, etc.
    //location.reload(); // se quiser forçar recarregar e atualizar tudo
  }
  