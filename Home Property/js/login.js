console.log("✅ login.js is loaded and running!");

// Ensure script runs after the page is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Checking login status...");

    let isLoggedIn = localStorage.getItem("isLoggedIn");

    if (isLoggedIn === "true") {
        console.log("✅ User is logged in, hiding Register/Login.");

        // Check if Register and Login links exist before trying to modify them
        let registerLink = document.getElementById("register-link");
        let loginLink = document.getElementById("login-link");
        let logoutLink = document.getElementById("logout-link");

        if (registerLink) registerLink.style.display = "none";
        if (loginLink) loginLink.style.display = "none";
        if (logoutLink) logoutLink.style.display = "inline-block";

        // Show a welcome message (Optional)
        let username = localStorage.getItem("username");
        alert(`Welcome back, ${username}!`);
    }

    // Handle Logout
    let logoutButton = document.getElementById("logout-link");
    if (logoutButton) {
        logoutButton.addEventListener("click", function () {
            console.log("✅ Logging out...");
            localStorage.clear(); // Clear all stored login data
            location.reload(); // Reload page to reflect changes
        });
    }

    // Attach login validation only if the form exists
    let form = document.querySelector(".contactform");
    if (form) {
        console.log("✅ Login form found, attaching event listener...");
        form.addEventListener("submit", validateForm);
    } else {
        console.log("ℹ No login form on this page.");
    }
});

function validateForm(event) {
    event.preventDefault(); // Prevent default form submission
    console.log("✅ validateForm() triggered!");

    let accountType = document.getElementById("account-type").value;
    let username = document.getElementById("username").value.trim();
    let password = document.getElementById("password").value.trim();

    if (username === "") {
        alert("❌ Please enter your username.");
        return;
    }

    if (password === "") {
        alert("❌ Please enter your password.");
        return;
    }

    if (accountType === "") {
        alert("❌ Please select your account type.");
        return;
    }

    // Store login state in localStorage
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("userType", accountType);
    localStorage.setItem("username", username);

    // Redirect users based on their selected account type
    let redirectURL = accountType === "seller" ? "index.html" : "properties.html";

    console.log("✅ Redirecting to:", redirectURL);
    window.location.href = redirectURL;
}
