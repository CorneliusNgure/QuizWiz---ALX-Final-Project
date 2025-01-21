document.getElementById("signupForm").addEventListener("submit", function (e) {
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const errorMsg = document.getElementById("errorMsg");

  if (password !== confirmPassword) {
    e.preventDefault(); // Prevent submission
    errorMsg.classList.remove("d-none");
  } else {
    errorMsg.classList.add("d-none");
  }
});