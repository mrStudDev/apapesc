    function exibirCampoNome(tipoDoc) {
        var campoNome = document.querySelector('[name="nome"]');
        if (tipoDoc === 'Nomear documento...') {
            campoNome.style.display = 'block';
        } else {
            campoNome.style.display = 'none';
            campoNome.value = '';  // Limpa o campo `nome` quando não está em uso
        }
    }