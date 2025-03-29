// To populate List-Property Town and Street name from DATA.GOV API
document.addEventListener("DOMContentLoaded", function () {
    const datasetId = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"; 
    const url = `https://data.gov.sg/api/action/datastore_search?resource_id=${datasetId}&limit=10000`;

    const townDropdown = document.getElementById("town");
    const streetDropdown = document.getElementById("street_name");

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const records = data.result.records;
            const townNames = new Set();
            const streetNames = new Set();

            // Extract unique values
            records.forEach(record => {
                if (record.town) townNames.add(record.town.trim().toUpperCase());
                if (record.street_name) streetNames.add(record.street_name.trim().toUpperCase());
            });

            // Populate dropdowns independently
            populateDropdown(townDropdown, [...townNames].sort());
            populateDropdown(streetDropdown, [...streetNames].sort());
        })
        .catch(error => console.error("Error fetching data:", error));
});

function populateDropdown(dropdown, items) {
    dropdown.innerHTML = `<option value="">Select an option</option>`;
    items.forEach(item => {
        let option = document.createElement("option");
        option.value = item;
        option.textContent = item;
        dropdown.appendChild(option);
    });
}