console.log("✅ logout.js is loaded!");

// Ensure script runs after the page is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Checking login status...");

    let isLoggedIn = localStorage.getItem("isLoggedIn");

    if (isLoggedIn === "true") {
        console.log("✅ User is logged in, updating UI...");

        let registerLink = document.getElementById("register-link");
        let loginLink = document.getElementById("login-link");
        let logoutLink = document.getElementById("logout-link");

        if (registerLink) registerLink.style.display = "none";
        if (loginLink) loginLink.style.display = "none";
        if (logoutLink) logoutLink.style.display = "inline-block";

        let username = localStorage.getItem("username");
        alert(`Welcome back, ${username}!`);
    }

    // Handle Logout
    let logoutButton = document.getElementById("logout-link");
    if (logoutButton) {
        logoutButton.addEventListener("click", function () {
            console.log("✅ Logging out...");
            localStorage.clear(); // Clear all login data
            location.reload(); // Reload to reflect logout
        });
    }
});
