# 2006-SCSB-T4
Project Codes are currently using the HomeProperty Refactored Branch 

#  HomeProperty Platform – 2006-SCSB-T4

A Flask-based web application for property listing and bidding. Built for SC2006 Software Engineering with features for sellers to list properties and agents to bid for them.


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

### Features:
Property listing by sellers

Sellers can view bidder's profile and past reviews.

Agents can view, bid and counterbid on properties

Real-time price suggestions using Data.gov resale API

OTP-secured registration using Twilio SMS, note that due to Twilio free-account limitations, only 1 phone number works (Use 93898718, Spencer's phone number) for account
registration

Integrated dashboards for both agents and sellers

### Technologies Used

Python + Flask

SQLite

HTML/CSS/JavaScript

Twilio API (for OTP)

Data.gov.sg API

### Team
SC2006-SCSB-T4 Group

Chong Qi En

Spencer

Yong khang

Atul

Shreya

Naveen
