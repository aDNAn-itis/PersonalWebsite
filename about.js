(() => {
    const button = document.querySelector('.raj-audio-toggle');
    const audio = document.getElementById('raj-reel');
    const status = document.querySelector('.raj-audio-status');
    const caption = document.querySelector('.leonard-caption');
    const note = document.querySelector('.raj-note');
    function fitReel() {
        // Preserve the original placement; shrink only if the reel would clip.
        if (window.matchMedia('(max-width: 1050px)').matches || audio.hidden) {
            audio.style.maxHeight = '';
            audio.style.maxWidth = '';
            return;
        }
        const availableHeight = Math.max(0, note.getBoundingClientRect().top - 40);
        audio.style.maxHeight = `${availableHeight}px`;
        audio.style.maxWidth = audio.videoHeight
            ? `${availableHeight * audio.videoWidth / audio.videoHeight}px`
            : '';
    }
    new ResizeObserver(fitReel).observe(note);
    window.addEventListener('resize', fitReel);
    audio.addEventListener('loadedmetadata', fitReel);
    function syncState() {
        const playing = !audio.paused && !audio.ended;
        caption.hidden = !playing;
        audio.hidden = !playing;
        fitReel();
        button.setAttribute('aria-pressed', String(playing));
        button.setAttribute('aria-label', `${playing ? 'Pause' : 'Play'}`);
        button.title = `Click to ${playing ? 'pause' : 'play'}`;
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
