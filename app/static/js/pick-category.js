function toggleMenu() {
  const nav = document.querySelector(".navbar-nav");
  nav.style.display = nav.style.display === "block" ? "none" : "block";
}

function startQuiz() {
  const category = document.getElementById("category").value;
  const difficulty = document.getElementById("difficulty").value;
  const type = document.getElementById("type").value;

  if (!category || !difficulty || !type) {
    alert("Please select a category, difficulty, and type.");
    return;
  }

  alert(
    `Starting quiz in ${category} category with ${difficulty} difficulty and ${type} type!`
  );
}