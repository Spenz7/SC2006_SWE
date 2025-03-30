document.getElementById("get-otp").addEventListener("click", function() {
    var phoneNumber = document.getElementById("phone_number").value.trim();

    if (phoneNumber.length === 8) {
        // Add +65 for Singapore phone number
        phoneNumber = '+65' + phoneNumber;
        
        // Make an AJAX request to send the OTP
        fetch('/send_otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone_number: phoneNumber })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("OTP sent to " + phoneNumber);
                // Show OTP input field after successful OTP send
                var otpInput = document.getElementById("otp");
                if (otpInput) {
                    otpInput.style.display = "block";
                }
            } else {
                alert("Failed to send OTP: " + data.message);
            }
        })
        .catch(err => {
            alert("Error: " + err);
        });
    } else {
        alert("Please enter a valid 8-digit phone number.");
    }
    
  });