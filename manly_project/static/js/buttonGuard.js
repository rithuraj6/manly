function disableButton(btn, loadingText = "Processing...") {
    if (!btn || btn.disabled) return false;

    btn.dataset.originalText = btn.innerText;
    btn.innerText = loadingText;
    btn.disabled = true;
    btn.classList.add("loading");

    return true;
}

function enableButton(btn) {
    if (!btn) return;

    btn.innerText = btn.dataset.originalText || btn.innerText;
    btn.disabled = false;
    btn.classList.remove("loading");
}
