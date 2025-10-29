// static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("TicketiFy is ready!");

  // Add subtle page fade-in effect
  document.body.style.opacity = 0;
  setTimeout(() => {
    document.body.style.transition = "opacity 1s";
    document.body.style.opacity = 1;
  }, 100);

  // Flash message auto-hide
  const flashes = document.querySelectorAll(".flash");
  if (flashes) {
    setTimeout(() => {
      flashes.forEach(f => f.style.display = "none");
    }, 4000);
  }

  // Color change animation on buttons
  const buttons = document.querySelectorAll("button, .btn");
  buttons.forEach(btn => {
    btn.addEventListener("mouseover", () => {
      btn.style.transform = "scale(1.05)";
    });
    btn.addEventListener("mouseout", () => {
      btn.style.transform = "scale(1)";
    });
  });
});
