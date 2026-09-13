// Petals land on a persistent ground layer beneath the desk assets.
(() => {
    const scene = document.querySelector('.scene-container');
    const makeLayer = (name) => {
        const canvas = document.createElement('canvas');
        canvas.width = 1080;
        canvas.height = 723;
        canvas.className = `sakura-layer ${name}`;
        canvas.setAttribute('aria-hidden', 'true');
        scene.appendChild(canvas);
        return canvas;
    };
    const ground = makeLayer('sakura-ground');
    const air = makeLayer('sakura-air');
    const soil = ground.getContext('2d');
    const sky = air.getContext('2d');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const colors = ['#f6bbcf', '#ffdce6', '#e99bb9', '#fff0f3'];
    let particles = [], raf = 0, last = 0, spawn = 0, age = 0, running = false;
    let carpetBudget = 0;
    const drifts = [];

    function petal(ctx, p, landed = false) {
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.angle);
        ctx.scale(p.size, p.size * (landed ? .48 : .4 + .6 * Math.abs(Math.cos(p.phase))));
        ctx.fillStyle = p.color;
        ctx.beginPath();
        // A single narrow, asymmetric blossom petal, with a tiny tip cleft.
        ctx.moveTo(-.18, 1.35);
        ctx.bezierCurveTo(-.85, .55, -.75, -.65, -.25, -1.05);
        ctx.quadraticCurveTo(-.05, -1.2, .08, -.98);
        ctx.lineTo(.18, -1.12);
        ctx.bezierCurveTo(.9, -.65, .68, .72, -.18, 1.35);
        ctx.fill();
        ctx.restore();
    }

    function seed() {
        const depth = Math.random();
        return {
            x: Math.random() * 1180 - 50, y: -15,
            target: 15 + depth * 700,
            size: 2 + depth * 2.6, speed: 38 + depth * 35,
            angle: Math.random() * Math.PI * 2,
            phase: Math.random() * Math.PI * 2,
            color: colors[Math.floor(Math.random() * colors.length)]
        };
    }

    function settle(p) {
        petal(soil, p, true);
        // Landings seed loose drifts, which gradually spread into one carpet.
        if (drifts.length < 160 && Math.random() < .22) {
            drifts.push({ x: p.x, y: p.y, radius: 8 });
        }
    }

    function buildCarpet(dt) {
        if (age < 5) return;
        carpetBudget += dt * Math.min(1500, (age - 5) * 35);
        while (carpetBudget >= 1) {
            carpetBudget--;
            const p = seed();
            const drift = drifts[Math.floor(Math.random() * drifts.length)];
            if (drift && Math.random() < .75) {
                const angle = Math.random() * Math.PI * 2;
                const radius = Math.sqrt(Math.random()) * drift.radius;
                p.x = drift.x + Math.cos(angle) * radius;
                p.y = drift.y + Math.sin(angle) * radius * .65;
                drift.radius = Math.min(230, drift.radius + .045);
            } else {
                p.y = p.target;
            }
            p.size = 2.4 + p.y / 723 * 2.2;
            soil.globalAlpha = .32;
            petal(soil, p, true);
        }
        soil.globalAlpha = 1;
    }

    function tick(now) {
        if (!running) return;
        const dt = last ? Math.min((now - last) / 1000, .05) : 0;
        last = now;
        if (!document.hidden) {
            age += dt;
            // Passing gusts release small showers from the canopy overhead.
            spawn += dt * (20 + 22 * Math.pow(.5 + .5 * Math.sin(age * .48), 3));
            while (spawn >= 1 && particles.length < 600) {
                particles.push(seed());
                spawn--;
            }
            sky.clearRect(0, 0, 1080, 723);
            buildCarpet(dt);
            particles = particles.filter(p => {
                p.phase += dt * 1.7;
                p.angle += dt * .65;
                p.x += (10 + Math.sin(age * .4) * 12 + Math.sin(p.phase) * 17) * dt;
                p.y += p.speed * dt;
                if (p.x > 1090) p.x = -10;
                if (p.y >= p.target) {
                    p.y = p.target;
                    settle(p);
                    return false;
                }
                petal(sky, p);
                return true;
            });
        }
        raf = requestAnimationFrame(tick);
    }

    function stop() {
        running = false;
        cancelAnimationFrame(raf);
        particles = [];
        last = spawn = age = 0;
        carpetBudget = 0;
        drifts.length = 0;
        sky.clearRect(0, 0, 1080, 723);
        soil.clearRect(0, 0, 1080, 723);
    }
    window.sakura = {
        stop,
        start() {
            stop();
            if (reduced.matches) {
                for (let i = 0; i < 24000; i++) {
                    const p = seed();
                    p.y = p.target;
                    petal(soil, p, true);
                }
                return;
            }
            running = true;
            raf = requestAnimationFrame(tick);
        }
    };
    reduced.addEventListener('change', () => {
        if (document.body.classList.contains('grass-relax-active')) window.sakura.start();
    });
})();
