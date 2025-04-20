# 2006-SCSB-T4
Project Codes are currently using the HomeProperty Refactored Branch 

Youtube Link for Demo Video : https://www.youtube.com/watch?v=f1LLvvwkYbs

# Table of Contents

- [PropBidder Platform – 2006-SCSB-T4](#propbidder-platform--2006-scsb-t4)
- [Overview](#overview)
- [Demo Video](#demo-video)
- [Supporting Documents](#supporting-documents)
- [Getting Started](#getting-started)
  - [Step 1: Navigate to the Project Directory](#step-1-navigate-to-the-project-directory)
  - [Step 2: Install Dependencies](#step-2-install-dependencies)
  - [Step 3: Run the Flask Backend](#step-3-run-the-flask-backend)
- [Pre-configured Test Account](#pre-configured-test-account)
- [Features](#features)
  - [For Sellers](#for-sellers)
  - [For Agents](#for-agents)
  - [Common Features](#common-features)
- [Technologies Used](#technologies-used)
  - [Frontend](#frontend)
  - [Backend](#backend)
  - [APIs](#apis)
- [Team](#team)

#  PropBidder Platform – 2006-SCSB-T4

A Flask-based web application for property listing and bidding. Built for SC2006 Software Engineering with features for sellers to list properties and agents to bid for them. PropBidder enables homeowners to list their flats for resale while property agents can bid for commission. The system features real-time price suggestion using Singapore's public resale data and OTP-secured registration

## Overview

HomeProperty bridges sellers and property agents on a digital platform with secure logins, agent bidding features, and helpful insights from resale price trends. It emphasizes:

- Transparent agent selection based on bids and reviews  
- Real-time price data from Data.gov.sg  
- OTP verification using Twilio API  
- Clean dashboards for seller and agent interactions

---

<details>
<summary>Demo Video</summary>

https://www.youtube.com/watch?v=f1LLvvwkYbs <br>
<a href="https://github.com/softwarelab3/2006-SCSB-T4/blob/main/Lab4/SC2006%20Demo%20Flow%20Script.pdf> Live Demo Script </a>


</details>

<details>
<summary>Supporting Documents</summary>
<br>
<a href="https://github.com/softwarelab3/2006-SCSB-T4/blob/main/Lab4/SC2006_SRS_Group4.pdf">1. Software Requirements Specification (SRS) </a> <br>
<a href="https://github.com/softwarelab3/2006-SCSB-T4/blob/main/Lab3/ClassDiagramSC2006.jpg">2. Class Diagram </a> <br>
<a href="https://github.com/softwarelab3/2006-SCSB-T4/blob/main/Lab3/Use%20Case%20Diagram.png">3. System Architecture </a> <br>
<a href="https://github.com/softwarelab3/2006-SCSB-T4/blob/main/Lab3/Use%20Case%20Diagram.png">4. Use Case Diagram </a> <br>
<a href="https://github.com/softwarelab3/2006-SCSB-T4/blob/main/Lab4/Updated-Sequence-Diagrams.pdf">5. Sequence Diagram </a>

</details>

---

##  Getting Started

Follow the steps below to set up and run the application on your local machine.

###  Step 1: Navigate to the Project Directory
Open up the terminal in Visual Studio Code or any Codespace within Github
Key this into the terminal to access the directory of the files:
```
cd 2006-SCSB-T4/HomeProperty
```

### Step 2: Install Dependencies
Make sure you have Python and pip installed use ```python --version``` and ```pip --version```. Then run:
```
pip install -r requirements.txt
```

### Step 3: Run the Flask Backend
In the terminal in Visual Studio Code or any Codespace within Github
```
python app.py
```
Once the server starts, visit http://127.0.0.1:5000 in your browser to access the platform.

## Pre-configured Test Account

OTP-secured registration using Twilio SMS, note that due to Twilio free-account limitations, only 1 phone number works (Use 93898718, Spencer's phone number) for account
registration
**Note:** The OTP will be printed on the console as well once app.py is run and the GET OTP button is pressed from the website. The tester can then use the OTP printed on the console as the OTP to key into the website. Reason being tester won't have access to the phone with the phone number 93898718.

## Features

### For Sellers

- List HDB apartments with specifications  
- View bids from property agents  
- Accept best bid and submit agent feedback  
- Real-time price comparison using data.gov.sg API

### For Agents

- View all listed properties  
- Place and update commission bids  
- Monitor bidding outcomes  
- Build reputation through seller reviews

### Common Features

- OTP-secured registration (Twilio)  
- Role-based dashboard views  
- Integrated bidding management and tracking

---


## Technologies Used

### Frontend

- HTML5, CSS3, Bootstrap  
- JavaScript (Vanilla)

### Backend

- Python, Flask  
- SQLite  
- Jinja2

### APIs

- Twilio API – OTP authentication  
- [Data.gov.sg](https://data.gov.sg) – HDB resale price data

---
### Team
SC2006-SCSB-T4 Group

Chong Qi En

Spencer

Yong khang

Atul

Shreya

Naveen
