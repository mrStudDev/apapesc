// mascara_quantidades.js
document.addEventListener("DOMContentLoaded", function () {
    const quantidadeFields = document.querySelectorAll("input[name^='quantidade']");

    quantidadeFields.forEach(function (field) {
        const mask = new Inputmask({
            alias: "numeric",
            groupSeparator: ".",
            radixPoint: ",",
            digits: 2, // Duas casas decimais
            autoGroup: true, // Adiciona o separador de milhares automaticamente
            allowMinus: false, // Impede números negativos
            rightAlign: false, // Digitação fluida
            placeholder: "0", // Mostra zeros como placeholder
            removeMaskOnSubmit: true, // Remove a máscara antes de enviar ao backend
        });
        mask.mask(field);
    });
});
