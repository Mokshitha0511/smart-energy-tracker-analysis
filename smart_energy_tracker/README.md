# ⚡ Smart Energy Tracker – Capstone Project
A Flask-based smart energy analytics system that allows users to upload time-series data, automatically preprocesses it, detects anomalies, visualizes energy usage, and stores anomaly outputs in SQLite.  
The dashboard and chatbot-style UI make the system highly interactive and user-friendly.

---

## 🚀 Features

### **1. Chatbot-Style Upload Flow**
- Upload CSV/TXT datasets via a modern chat-style interface  
- Shows file confirmation and bot “thinking…” animation  
- Smooth transition to results page  

### **2. Automated Cleaning & Preprocessing**
The system:
- Cleans invalid or missing power readings  
- Converts data types (e.g., numeric power values)  
- Constructs a unified `DateTime` column  
- Renames required columns for anomaly detection  
- Ensures consistent structure for downstream steps  

### **3. Anomaly Detection**
Uses IQR-based statistical analysis to detect unusual power usage:
- Identifies high or low outlier readings  
- Highlights anomalies in the visualization  
- Links anomalies back to original data (preprocessing-safe)  

### **4. Visualization Dashboard**
- Full-sized time-series plot  
- Power usage shown as a continuous line  
- Anomalies marked in red  
- Clean dashboard layout with responsive design  
- One-click anomaly CSV download  

### **5. SQLite Database Storage**
Each upload generates:
- A unique anomaly CSV  
- Stored as text inside SQLite  
- Timestamped record for tracking  
- Accessible via download endpoint  

---

## 🧠 Architecture Overview

### **Frontend**
- Chatbot-style UI (`upload.html`, `upload_result.html`)  
- Dashboard (`plot.html`)  

### **Backend**
- Flask as API & web server  
- Routes for upload, plot generation, anomaly download  

### **Processing Layer**
- Pandas for cleaning & transformations  
- IQR-based anomaly detection  
- Matplotlib for graph generation  

### **Database**
- SQLite  
- Table: `AnomalyDetector`  
- Fields: `FileName`, `SavedAt`, `FileBlob`  

---


---

## 💻 Running the Application

### **1. Install dependencies**

pip install -r requirements.txt

### **2. Start the Flask server**

python app.py

### **3. Access the app**
Open in your browser:
http://127.0.0.1:5000/upload

---

## 📦 requirements.txt (Version-Neutral)

Flask
pandas
matplotlib


---

## 🧪 Supported File Formats
- `.csv` (semicolon/comma separated)  
- `.txt` (auto-parsed by pandas engine)

---

## 🔧 Future Enhancements
- Implement a **generalized data loader** to handle multiple time-series schemas  
- Replace SQLite with **MySQL or MongoDB** for production scalability  
- Add forecasting using **LSTM/Transformer** models  
- Implement monthly/weekly analytic views  
- Deploy to cloud with authentication and user history tracking  

---

## 📄 License
Academic submission for AI Cohort 2 Batch 5 Capstone Project.

---

## 🙌 Acknowledgements
- Instructors & mentors  
- GitHub Copilot and ChatGPT for coding support and debugging assistance  
