// Toggle navigation menu
function toggleMenu() {
    const nav = document.querySelector('.navbar-nav');
    nav.style.display = nav.style.display === 'block' ? 'none' : 'block';
  }

  // Auto-dismiss flash messages
  // document.addEventListener('DOMContentLoaded', () => {
  //   const flashMessages = document.querySelectorAll('.flash-message');
  //   flashMessages.forEach((message) => {
  //     setTimeout(() => {
  //       message.style.display = 'none';
  //     }, 5000);
  //   });
  // });