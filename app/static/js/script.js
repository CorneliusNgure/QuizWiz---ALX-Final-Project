// Handle opening and closing of the dropdown menu
document.querySelector(".menu-btn").addEventListener("click", () => {
  document.querySelector(".dropdown-menu").classList.toggle("show");
});

document.querySelector(".close-btn").addEventListener("click", () => {
  document.querySelector(".dropdown-menu").classList.remove("show");
});

// Close the dropdown if the user clicks outside of it
window.onclick = function (event) {
  const dropdown = document.querySelector(".dropdown-menu");
  if (!dropdown.contains(event.target) && !event.target.matches(".menu-btn")) {
    dropdown.classList.remove("show");
  }
};

// Dark mode toggle
const modeSwitch = document.getElementById("mode-switch");
modeSwitch.addEventListener("change", () => {
  document.body.classList.toggle("dark-mode");
});
