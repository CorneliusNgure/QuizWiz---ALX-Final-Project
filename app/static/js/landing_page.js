// scroll to top button
const scrollToTopBtn = document.getElementById("scrollToTop");
window.addEventListener("scroll", () => {
  scrollToTopBtn.style.display = window.scrollY > 200 ? "block" : "none";
});
scrollToTopBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});
