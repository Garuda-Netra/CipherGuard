// ANIMATION 2: Parchment Scroll Unfurl
function unfurlPanel(panelElement) {
    // 1. Set initial states immediately
    panelElement.style.transform = 'scaleY(0)';
    panelElement.style.opacity = '0';
    // 2. Set transform-origin
    panelElement.style.transformOrigin = 'top center';
    
    // 3 & 4. On next frame, transition to full
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            panelElement.style.transition = 'transform 0.6s ease-out, opacity 0.4s ease-out';
            panelElement.style.transform = 'scaleY(1)';
            panelElement.style.opacity = '1';
            
            // Clean up transition after it's done so it doesn't affect other dynamic sizing
            setTimeout(() => {
                panelElement.style.transition = '';
            }, 600);
        });
    });
}

// ANIMATION 4: Typing Effect on Headings
function typeHeading(element, text) {
    // 1. Clear textContent
    element.textContent = '';
    let index = 0;
    
    // 2 & 3. Append character by character
    const interval = setInterval(() => {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
        } else {
            // 4. Clear interval when done
            clearInterval(interval);
        }
    }, 50);
}

// ANIMATION 5: Floating Dust Particles
function initDustParticles() {
    const canvas = document.getElementById('dustCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    
    // Resize canvas to match window
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    window.addEventListener('resize', resize);
    resize();
    
    // 1. Create array of 35 particle objects
    for (let i = 0; i < 35; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 2 + 1, // 1 to 3
            speed: Math.random() * 0.6 + 0.2, // 0.2 to 0.8
            opacity: Math.random() * 0.5 + 0.1, // 0.1 to 0.6
            opacityDirection: Math.random() > 0.5 ? 1 : -1,
            color: Math.random() > 0.5 ? '#C9A84C' : '#D4A853'
        });
    }
    
    // 2. Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(p => {
            // Move y upward
            p.y -= p.speed;
            
            // Oscillate opacity
            p.opacity += 0.005 * p.opacityDirection;
            if (p.opacity <= 0.1) {
                p.opacityDirection = 1;
                p.opacity = 0.1;
            } else if (p.opacity >= 0.7) {
                p.opacityDirection = -1;
                p.opacity = 0.7;
            }
            
            // Reset if goes off top
            if (p.y < 0) {
                p.y = canvas.height;
                p.x = Math.random() * canvas.width;
            }
            
            // Draw
            ctx.globalAlpha = p.opacity;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// ANIMATION 6: Number Counter Animation
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        // Easing function (easeOutExpo)
        const easeOut = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        
        // Calculate current value
        const current = Math.floor(start + (end - start) * easeOut);
        obj.innerHTML = current.toLocaleString();
        
        // Glow effect during animation
        obj.style.textShadow = `0 0 ${10 * easeOut}px rgba(201, 168, 76, ${0.8 * easeOut})`;
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            // Final subtle glow state
            obj.style.textShadow = '0 0 5px rgba(201, 168, 76, 0.4)';
        }
    };
    window.requestAnimationFrame(step);
}
