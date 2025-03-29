
      let currentPropertyId = null;
      let maxCommission = 0;
    
      function handleBidClick(btn) {
        const title = btn.dataset.title;
        const max = parseFloat(btn.dataset.max);
        const id = btn.dataset.propertyId;
        const status = btn.dataset.status;
        
        if (status == 'C') {
          alert("This property has been sold. You cannot place a bid.");
          return;  // Prevent the modal from opening if the property is sold
      }

        currentPropertyId = id;
        maxCommission = max;
    
        document.getElementById('property-name').innerText = `Bidding for: ${title}`;
        document.getElementById('final-commission').value = '';
        document.getElementById('final-commission').max = max;
        document.getElementById('bidModal').style.display = 'block';
      }
    
      function closeBidModal() {
        document.getElementById('bidModal').style.display = 'none';
      }
      function handleRebidClick(button) {
        const title = button.dataset.title;
        const max = parseFloat(button.dataset.max);
        const id = button.dataset.propertyId;
        const status = btn.dataset.status;

        if (status == 'C') {
          alert("This property has been sold. You cannot place a bid.");
          return;  // Prevent the modal from opening if the property is sold
      }
      
        currentPropertyId = id;
        maxCommission = max;
      
        document.getElementById('property-name').innerText = `Rebidding for: ${title}`;
        document.getElementById('final-commission').value = '';
        document.getElementById('final-commission').max = max;
        document.getElementById('bidModal').style.display = 'block';
      }
    
      async function placeBid() {
        const commission = parseFloat(document.getElementById('final-commission').value);
        if (isNaN(commission) || commission <= 0 || commission > maxCommission) {
          alert(`Please enter a valid commission percentage (max: ${maxCommission}%)`);
          return;
        }
    
        try {
          const response = await fetch('/submit_bid', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              property_id: currentPropertyId,
              commission: commission
            })
          });
    
          const result = await response.json();
          if (result.success) {
            alert(result.message);
            closeBidModal();
            location.reload(); // Reload to reflect bid
          } else {
            alert(result.message || "Something went wrong.");
          }
        } catch (error) {
          console.error("Error submitting bid:", error);
          alert("Failed to submit bid.");
        }

        
      }