const datasetId = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc";
const url = "https://data.gov.sg/api/action/datastore_search?resource_id=" + datasetId;

const dataContainer = document.getElementById("data-container");

fetch(url)
  .then(response => {
    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }
    return response.json();
  })
  .then(data => {
    // Extract relevant records
    const records = data.result.records;

    if (records.length === 0) {
      dataContainer.innerHTML = "<p>No data available.</p>";
      return;
    }

    // Create an HTML table for the dataset
    let table = "<table border='1'><tr>";

    // Dynamically get table headers
    Object.keys(records[0]).forEach(header => {
      table += `<th>${header}</th>`;
    });
    table += "</tr>";

    // Add table rows with data
    records.forEach(record => {
      table += "<tr>";
      Object.values(record).forEach(value => {
        table += `<td>${value}</td>`;
      });
      table += "</tr>";
    });

    table += "</table>";

    // Inject the table into the webpage
    dataContainer.innerHTML = table;
  })
  .catch(error => {
    console.error("Error fetching data:", error);
    dataContainer.innerHTML = "<p>Failed to load data.</p>";
  });
