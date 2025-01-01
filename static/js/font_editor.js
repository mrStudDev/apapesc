const FontEditor = (() => {
    const editorId = "font-editor";
    const hiddenInputId = "hidden-font-editor";

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

    function init() {
        const editor = document.getElementById(editorId);
        const hiddenInput = document.getElementById(hiddenInputId);

        if (editor && hiddenInput) {
            editor.addEventListener("input", () => {
                hiddenInput.value = editor.innerHTML;
            });

            if (hiddenInput.value) {
                editor.innerHTML = hiddenInput.value;
            }
        }
    }

    return { init, formatText, returnToParagraph, createLink };
})();

document.addEventListener("DOMContentLoaded", FontEditor.init);
document.addEventListener("DOMContentLoaded", () => {
    const editor = document.getElementById("font-editor");
    if (!editor) {
        console.error("Font Editor not found on the page!");
    } else {
        console.log("Font Editor initialized successfully.");
    }
});
