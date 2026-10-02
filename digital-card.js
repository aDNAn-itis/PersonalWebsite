(() => {
    const dialog = document.getElementById('digital-card');
    document.getElementById('share-card').addEventListener('click', event => {
        event.preventDefault();
        dialog.showModal();
    });
    dialog.addEventListener('click', event => {
        if (event.target !== dialog) return;
        const bounds = dialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right ||
            event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
})();
