document.addEventListener("DOMContentLoaded", function () {
    const datasetId = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"; 
    const url = `https://data.gov.sg/api/action/datastore_search?resource_id=${datasetId}&limit=10000`;

    const townDropdown = document.getElementById("town");
    const streetDropdown = document.getElementById("street_name");

    let streetToTownMap = {};  // Will map street_name -> town

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const records = data.result.records;
            const townNames = new Set();
            const streetNames = new Set();

            // Extract and build mappings
            records.forEach(record => {
                const town = record.town?.trim().toUpperCase();
                const street = record.street_name?.trim().toUpperCase();

                if (town && street) {
                    townNames.add(town);
                    streetNames.add(street);

                    // If a street maps to multiple towns, only keep the first or last
                    streetToTownMap[street] = town;
                }
            });

            // Populate both dropdowns
            populateDropdown(townDropdown, [...townNames].sort());
            populateDropdown(streetDropdown, [...streetNames].sort());

            // Add event listener for street selection
            streetDropdown.addEventListener("change", function () {
                const selectedStreet = this.value;
                const mappedTown = streetToTownMap[selectedStreet];
                if (mappedTown) {
                    townDropdown.value = mappedTown;
                }
            });
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
