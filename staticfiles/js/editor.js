const MainEditor = (() => {
    const editorId = "editor";
    const hiddenInputId = "hidden-editor";

    function formatText(command, value = null) {
        const editor = document.getElementById(editorId);
        if (!editor) return;
        editor.focus();
        document.execCommand(command, false, value);
    }

    // Ajustado para limpar cor/fundo/estilos inline.
    function returnToParagraph() {
        formatText("formatBlock", "p");
        const editor = document.getElementById(editorId);
        if (!editor) return;
        editor.focus();
        // removeFormat afeta apenas a seleção ou o bloco do cursor.
        document.execCommand("removeFormat", false, null);
    }

    function createLink() {
        const url = prompt("Digite uma URL:");
        if (url) {
            document.execCommand("createLink", false, url.startsWith("http") ? url : `https://${url}`);
            
            // Adiciona o atributo target="_blank" ao link recém-criado
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const linkElement = selection.anchorNode.parentElement;
                if (linkElement && linkElement.tagName === "A") {
                    linkElement.setAttribute("target", "_blank");
                }
            }
        }
    }
    

    function addBlockquote() {
        const editor = document.getElementById(editorId);
        if (!editor) return;
        editor.focus();
        document.execCommand("formatBlock", false, "BLOCKQUOTE");
    }

    function changeTextColor(color) {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const span = document.createElement("span");
            span.style.color = color;
            const range = selection.getRangeAt(0);
            range.surroundContents(span);
        }
    }

    function changeBackgroundColor(color) {
        const editor = document.getElementById(editorId);
        if (!editor) return;
        editor.focus();
        document.execCommand("backColor", false, color);
    }

    function syncContent() {
        const editor = document.getElementById(editorId);
        const hiddenInput = document.getElementById(hiddenInputId);
        if (editor && hiddenInput) {
            hiddenInput.value = editor.innerHTML;
        }
    }

    function init() {
        const editor = document.getElementById(editorId);
        const hiddenInput = document.getElementById(hiddenInputId);
        if (editor && hiddenInput) {
            editor.addEventListener("input", syncContent);
            editor.innerHTML = hiddenInput.value || "";
        }
    }

    return {
        init,
        formatText,
        returnToParagraph,
        createLink,
        addBlockquote,
        changeTextColor,
        changeBackgroundColor
    };
})();

document.addEventListener("DOMContentLoaded", MainEditor.init);
