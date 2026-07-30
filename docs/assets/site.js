(() => {
  "use strict";

  const canvas = document.getElementById("coherence-field");
  if (!(canvas instanceof HTMLCanvasElement)) {
    return;
  }

  const context = canvas.getContext("2d", { alpha: true });
  if (!context) {
    return;
  }

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const pointer = { x: 0, y: 0, active: false };
  const nodes = [];
  const palette = {
    node: "rgba(197, 255, 212, 0.74)",
    nodeSoft: "rgba(114, 215, 206, 0.46)",
    link: "rgba(137, 219, 173, 0.15)",
    pulse: "rgba(255, 201, 120, 0.7)"
  };

  let width = 0;
  let height = 0;
  let ratio = 1;
  let animationFrame = 0;
  let lastTime = 0;

  function seeded(index, salt) {
    const value = Math.sin((index + 1) * 9187.13 + salt * 3719.41) * 43758.5453;
    return value - Math.floor(value);
  }

  function buildField() {
    const count = Math.max(28, Math.min(86, Math.round((width * height) / 23000)));
    nodes.length = 0;

    for (let index = 0; index < count; index += 1) {
      nodes.push({
        x: seeded(index, 1) * width,
        y: seeded(index, 2) * height,
        radius: 0.7 + seeded(index, 3) * 1.9,
        driftX: (seeded(index, 4) - 0.5) * 0.035,
        driftY: (seeded(index, 5) - 0.5) * 0.035,
        phase: seeded(index, 6) * Math.PI * 2,
        depth: 0.45 + seeded(index, 7) * 0.75
      });
    }
  }

  function resize() {
    const bounds = canvas.getBoundingClientRect();
    width = Math.max(1, Math.round(bounds.width));
    height = Math.max(1, Math.round(bounds.height));
    ratio = Math.min(window.devicePixelRatio || 1, 2);

    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);

    pointer.x = width * 0.72;
    pointer.y = height * 0.45;
    buildField();
    draw(0);
  }

  function drawLink(first, second, distance, limit) {
    const opacity = Math.max(0, 1 - distance / limit);
    context.strokeStyle = palette.link.replace("0.15", String(0.03 + opacity * 0.15));
    context.lineWidth = 0.55 + opacity * 0.45;
    context.beginPath();
    context.moveTo(first.x, first.y);
    context.lineTo(second.x, second.y);
    context.stroke();
  }

  function draw(timestamp) {
    const elapsed = lastTime ? Math.min(32, timestamp - lastTime) : 16;
    lastTime = timestamp;
    context.clearRect(0, 0, width, height);

    const connectionLimit = Math.max(90, Math.min(155, width * 0.12));

    for (let firstIndex = 0; firstIndex < nodes.length; firstIndex += 1) {
      const first = nodes[firstIndex];

      if (!reducedMotion.matches) {
        first.x += first.driftX * elapsed * first.depth;
        first.y += first.driftY * elapsed * first.depth;

        if (first.x < -20) first.x = width + 20;
        if (first.x > width + 20) first.x = -20;
        if (first.y < -20) first.y = height + 20;
        if (first.y > height + 20) first.y = -20;
      }

      for (let secondIndex = firstIndex + 1; secondIndex < nodes.length; secondIndex += 1) {
        const second = nodes[secondIndex];
        const deltaX = first.x - second.x;
        const deltaY = first.y - second.y;
        const distance = Math.hypot(deltaX, deltaY);

        if (distance < connectionLimit) {
          drawLink(first, second, distance, connectionLimit);
        }
      }
    }

    if (pointer.active) {
      for (const node of nodes) {
        const distance = Math.hypot(node.x - pointer.x, node.y - pointer.y);
        if (distance < 170) {
          context.strokeStyle = `rgba(255, 201, 120, ${Math.max(0, 0.24 - distance / 900)})`;
          context.lineWidth = 0.8;
          context.beginPath();
          context.moveTo(pointer.x, pointer.y);
          context.lineTo(node.x, node.y);
          context.stroke();
        }
      }
    }

    for (const node of nodes) {
      const pulse = reducedMotion.matches ? 0.5 : (Math.sin(timestamp * 0.0011 + node.phase) + 1) / 2;
      const radius = node.radius + pulse * 0.65;
      context.fillStyle = node.depth > 0.85 ? palette.node : palette.nodeSoft;
      context.beginPath();
      context.arc(node.x, node.y, radius, 0, Math.PI * 2);
      context.fill();
    }

    if (pointer.active) {
      const halo = context.createRadialGradient(pointer.x, pointer.y, 0, pointer.x, pointer.y, 84);
      halo.addColorStop(0, "rgba(255, 201, 120, 0.2)");
      halo.addColorStop(1, "rgba(255, 201, 120, 0)");
      context.fillStyle = halo;
      context.beginPath();
      context.arc(pointer.x, pointer.y, 84, 0, Math.PI * 2);
      context.fill();
    }

    if (!reducedMotion.matches) {
      animationFrame = window.requestAnimationFrame(draw);
    }
  }

  function start() {
    window.cancelAnimationFrame(animationFrame);
    lastTime = 0;
    if (reducedMotion.matches) {
      draw(0);
    } else {
      animationFrame = window.requestAnimationFrame(draw);
    }
  }

  canvas.addEventListener("pointermove", (event) => {
    const bounds = canvas.getBoundingClientRect();
    pointer.x = event.clientX - bounds.left;
    pointer.y = event.clientY - bounds.top;
    pointer.active = true;
  });

  canvas.addEventListener("pointerleave", () => {
    pointer.active = false;
  });

  window.addEventListener("resize", resize, { passive: true });
  reducedMotion.addEventListener("change", start);

  resize();
  start();
})();
