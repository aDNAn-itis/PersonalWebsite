(() => {
    const button = document.querySelector('.raj-audio-toggle');
    const audio = document.getElementById('raj-audio');
    const status = document.querySelector('.raj-audio-status');
    function syncState() {
        const playing = !audio.paused && !audio.ended;
        button.setAttribute('aria-pressed', String(playing));
        button.setAttribute('aria-label', `${playing ? 'Pause' : 'Play'} Raj’s audio`);
        button.title = `Click to ${playing ? 'pause' : 'play'} Raj’s audio`;
    }
    audio.addEventListener('play', syncState);
    audio.addEventListener('pause', syncState);
    audio.addEventListener('ended', syncState);
    button.addEventListener('click', async () => {
        status.textContent = '';
        if (!audio.paused) {
            audio.pause();
            return;
        }
        if (audio.ended) audio.currentTime = 0;
        try {
            await audio.play();
        } catch {
            status.textContent = 'Audio could not play. Please try again.';
            syncState();
        }
    });
    window.addEventListener('pagehide', () => audio.pause());
})();
