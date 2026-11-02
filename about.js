(() => {
    const loadingStartTime = performance.now();
    const MIN_LOADING_MS = 1050;
    const isPreview = new URLSearchParams(window.location.search).has('preview-loading');
    const barEl = document.getElementById('loading-progress-bar');
    const pctEl = document.getElementById('loading-status-pct');
    const pageImages = Array.from(document.querySelectorAll('main img, .raj-note img'));
    const totalAssets = Math.max(1, pageImages.length);
    let loadedAssets = 0;
    let pageLoaded = false;
    let displayedPct = 0;
    let revealed = false;

    const countAsset = () => {
        loadedAssets = Math.min(totalAssets, loadedAssets + 1);
    };
    pageImages.forEach(img => {
        if (img.complete) {
            countAsset();
        } else {
            img.addEventListener('load', countAsset, { once: true });
            img.addEventListener('error', countAsset, { once: true });
        }
    });

    window.addEventListener('load', () => {
        pageLoaded = true;
        loadedAssets = totalAssets;
    });

    function tickProgress(now) {
        const elapsed = now - loadingStartTime;
        const timeRatio = Math.min(1, elapsed / MIN_LOADING_MS);
        const assetRatio = loadedAssets / totalAssets;
        const targetPct = isPreview
            ? 18 + Math.round(((Math.sin(now / 900) + 1) / 2) * 74)
            : (pageLoaded ? Math.round(timeRatio * 100) : Math.min(94, Math.round(assetRatio * 75 + timeRatio * 20)));

        displayedPct += (targetPct - displayedPct) * 0.22;
        const shown = pageLoaded && timeRatio >= 1 && !isPreview ? 100 : Math.min(100, Math.round(displayedPct));

        if (barEl) barEl.style.width = `${shown}%`;
        if (pctEl) pctEl.textContent = `${shown}%`;

        if (!isPreview && pageLoaded && timeRatio >= 1 && shown >= 100) {
            if (!revealed) {
                revealed = true;
                requestAnimationFrame(() => {
                    document.body.classList.remove('page-loading');
                    const loader = document.getElementById('loading-screen');
                    if (loader) {
                        window.setTimeout(() => loader.setAttribute('aria-hidden', 'true'), 500);
                    }
                });
            }
            return;
        }
        requestAnimationFrame(tickProgress);
    }
    requestAnimationFrame(tickProgress);

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
