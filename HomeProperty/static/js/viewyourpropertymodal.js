document.addEventListener('DOMContentLoaded', function () {
    console.log("✅ JS script loaded!");

    window.loadPropertyDetails = function (propertyId) {
      console.log("🚀 loadPropertyDetails triggered for property ID:", propertyId);

      fetch(`/get_property_details/${propertyId}`)
        .then(response => response.json())
        .then(data => {
          const property = data.property;
          const bidders = data.bidders;

          console.log("📦 Property:", property);
          console.log("👥 Bidders:", bidders);

          // Fill in modal details
          $('#modal-flat-type').text(property.flat_type);
          $('#modal-town').text(property.town);
          $('#modal-street-name').text(property.street_name);
          $('#modal-floor-area').text(property.floor_area);
          $('#modal-max-com-bid').text(property.max_com_bid);
          $('#modal-years-remaining').text(property.years_remaining);
          $('#modal-listing-price').text(property.listing_price);

          // Clear bidder list
          const $bidderList = $('#bidder-list');
          $bidderList.empty();

          if (Array.isArray(bidders) && bidders.length > 0) {
            bidders.sort((a, b) => a.bid_percent - b.bid_percent);

            bidders.forEach(bid => {
              console.log("🧪 Bidder raw data:", bid);

              const username = bid.agent_username;
              const percent = bid.bid_percent;

              if (!username || percent === undefined || percent === null) {
                console.warn("⚠️ Skipping invalid bid:", bid);
                return;
              }

              $bidderList.append(`
                <tr>
                  <td>${username}</td>
                  <td>${percent.toFixed(1)}%</td>
                  <td>
                    <button class="btn btn-success btn-sm" onclick="acceptBid(${property.id}, '${username}')">
                      Accept
                    </button>
                    <button class="btn btn-primary btn-sm ml-2" onclick="viewAgentProfile('${username}')">
                      View Profile
                    </button>
                  </td>

                </tr>
              `);
            });
          } else {
            $bidderList.append(`<tr><td colspan="3" class="text-center">No bids yet</td></tr>`);
          }

          $('#propertyModal').modal('show');
        })
        .catch(error => console.error("❌ Error fetching property details:", error));
    };

    window.acceptBid = function (propertyId, agentUsername) {
      fetch('/accept_bid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          property_id: propertyId,
          agent_username: agentUsername
        })
      })
        .then(res => res.json())
        .then(response => {
          alert(response.message);

          // ✅ Save selected data for marking sold
          window.selectedPropertyId = propertyId;
          window.selectedAgent = agentUsername;

          document.getElementById('selected-agent-name').textContent = agentUsername;
          document.getElementById('review-rating').value = '';
          document.getElementById('review-text').value = '';
          document.getElementById('review-section').style.display = 'block';
        })

        .catch(err => console.error("❌ Error accepting bid:", err));
    };
  });

  function viewAgentProfile(username) {
    fetch(`/agent_profile/${username}`)
      .then(response => response.text())
      .then(html => {
        // Create a new window or modal for the profile
        const newWindow = window.open("", "_blank");
        newWindow.document.write(html);
      })
      .catch(error => console.error("❌ Failed to load profile:", error));
  }
  
window.submitMarkAsSold = function () {
  const propertyId = window.selectedPropertyId;
  const agentUsername = window.selectedAgent;
  const rating = parseInt(document.getElementById('review-rating').value);
  const review = document.getElementById('review-text').value;

  if (!rating || rating < 1 || rating > 5) {
    alert("Please enter a valid rating between 1 and 5.");
    return;
  }

  fetch('/mark_as_sold', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      property_id: propertyId,
      agent_username: agentUsername,
      rating: rating,
      review: review
    })
  })
    .then(res => res.json())
    .then(response => {
      alert(response.message);
      location.reload();
    })
    .catch(err => console.error("❌ Error submitting review:", err));
};