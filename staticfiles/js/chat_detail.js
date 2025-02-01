// Inicializa a conexão WebSocket para o chat
function initializeWebSocket(recipientId) {
    const socket = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/' + recipientId + '/'
    );

    socket.onopen = function () {
        console.log("Conexão WebSocket estabelecida com sucesso!");
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("Mensagem recebida:", data);  // Log para verificar os dados recebidos

        if (data.sender && data.message && data.recipient) {
            const messageContainer = document.getElementById("messages");

            // Criando o novo elemento de mensagem
            const messageElement = document.createElement("div");
            messageElement.innerHTML = `
                <strong>${data.sender}:</strong> ${data.message}
                ${data.read ? '<span class="text-sm text-green-500">(Lido)</span>' : ''}
            `;

            // Adiciona a nova mensagem ao contêiner
            messageContainer.appendChild(messageElement);

            // Forçar a atualização do contêiner de mensagens
            messageContainer.scrollTop = messageContainer.scrollHeight;

            // Forçar reflow para garantir que a interface se atualize imediatamente
            messageContainer.offsetHeight;  // Force reflow

            // Alternativamente, podemos usar `requestAnimationFrame` para garantir que o layout seja recalculado
            window.requestAnimationFrame(function() {
                messageContainer.scrollTop = messageContainer.scrollHeight;
            });
        } else {
            console.log("Erro: Dados incompletos recebidos:", data);
        }
    };



    socket.onclose = function () {
        console.log("Conexão WebSocket fechada!");
    };

    socket.onerror = function (error) {
        console.error("Erro WebSocket:", error);
    };

    return socket;
}

// Adiciona a nova mensagem ao chat
function addMessageToChat(sender, message, read) {
    const messagesDiv = document.getElementById('messages');
    const newMessageDiv = document.createElement('div');
    newMessageDiv.innerHTML = `
        <strong>${sender}:</strong> ${message}
        ${read ? '<span class="text-sm text-green-500">(Lido)</span>' : ''}
    `;
    messagesDiv.appendChild(newMessageDiv);  // Adiciona a nova mensagem ao chat
    messagesDiv.scrollTop = messagesDiv.scrollHeight;  // Rolagem automática para a última mensagem
    console.log("Mensagem adicionada ao chat:", newMessageDiv); // Verifica se a mensagem foi adicionada ao DOM
}

// Lida com o envio de mensagens
function setupMessageForm(socket) {
    const form = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-content');

    form.onsubmit = function (e) {
        e.preventDefault();  // Evita o envio padrão do formulário
        const message = messageInput.value;

        if (message.trim() !== "") {  // Verifica se a mensagem não está vazia
            sendMessage(socket, message); // Envia a mensagem pelo WebSocket
            messageInput.value = '';  // Limpa o campo de texto após o envio
        }
    };
}

// Envia uma mensagem pelo WebSocket
function sendMessage(socket, message) {
    console.log("Enviando mensagem:", message);  // Log para mostrar a mensagem enviada
    const recipientId = document.getElementById('recipient-id').value;
    socket.send(JSON.stringify({
        'message': message,
        'recipient': recipientId  // Envia o recipientId
    }));
}

// Função principal para inicializar a página e o chat
function initializeChat(recipientId) {
    console.log("Inicializando chat com o recipientId:", recipientId);  // Log do recipientId
    const socket = initializeWebSocket(recipientId);
    setupMessageForm(socket);
}
