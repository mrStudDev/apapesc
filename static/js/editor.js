const MainEditor = (() => {
    const editorId = "editor";
    const hiddenInputId = "hidden-editor";

    function formatText(command, value = null) {
        const editor = document.getElementById(editorId);
        if (!editor) return;
        editor.focus();
        document.execCommand(command, false, value);
    }

    function returnToParagraph() {
        formatText("formatBlock", "p");
    }

    function createLink() {
        const url = prompt("Digite uma URL:");
        if (url) {
            formatText("createLink", url.startsWith("http") ? url : `https://${url}`);
        }
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

    return { init, formatText, returnToParagraph, createLink };
})();

document.addEventListener("DOMContentLoaded", MainEditor.init);
