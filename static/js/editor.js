function formatText(command, value = null) {
    const editor = document.getElementById("editor");
    if (!editor) return;
    editor.focus();
    try {
        document.execCommand(command, false, value);
        console.log(`Comando ${command} executado com sucesso.`);
    } catch (error) {
        console.error(`Erro ao executar ${command}:`, error);
    }
}

function addBlockquote() {
    const editor = document.getElementById("editor");
    if (!editor) return;
    editor.focus();
    document.execCommand("formatBlock", false, "<blockquote>");
}

function returnToParagraph() {
    const editor = document.getElementById("editor");
    if (!editor) return;
    editor.focus();
    document.execCommand("formatBlock", false, "<p>");
}

document.addEventListener("DOMContentLoaded", function () {
    const editor = document.getElementById("editor");
    const hiddenInput = document.getElementById("hidden-editor");

    if (editor && hiddenInput) {
        editor.addEventListener("input", function () {
            hiddenInput.value = editor.innerHTML;
        });

        if (hiddenInput.value) {
            editor.innerHTML = hiddenInput.value;
        }
    }
});


document.addEventListener("keydown", function (event) {
    const editor = document.getElementById("editor");
    if (editor && event.key === "Enter") {
        const selection = window.getSelection();
        if (selection && selection.anchorNode && selection.anchorNode.parentElement) {
            const parentElement = selection.anchorNode.parentElement;
            if (parentElement.tagName === "BLOCKQUOTE") {
                setTimeout(() => returnToParagraph(), 0);
            }
        }
    }
});

function changeTextColor(color) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const span = document.createElement("span");
        span.style.color = color;
        selection.getRangeAt(0).surroundContents(span);
    }
}



function changeBackgroundColor(color) {
    const editor = document.getElementById("editor");
    if (!editor) return;
    editor.focus();
    document.execCommand("backColor", false, color);
}
function createLink() {
    const url = prompt("Digite uma URL:");
    if (url) {
        formatText("createLink", url.startsWith("http") ? url : `https://${url}`);
    }
}