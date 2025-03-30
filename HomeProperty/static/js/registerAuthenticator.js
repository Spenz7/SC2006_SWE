document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.contactform');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm-password');
  
    form.addEventListener('submit', function (e) {
      if (password.value !== confirmPassword.value) {
        e.preventDefault();
        alert("❗ Passwords do not match.");
      } else if (!isStrongPassword(password.value)) {
        e.preventDefault();
        alert("❗ Password does not meet criteria.");
      }
    });
  
    function isStrongPassword(pw) {
      const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
      return regex.test(pw);
    }
  });
  