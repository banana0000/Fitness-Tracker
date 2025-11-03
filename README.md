# Fitness-Tracker

# 🏋️♀️ Fitness Tracker

A simple fitness tracking web app built with Python and Flask.  
It allows users to upload workout data, clean and analyze it, and visualize progress over time.

---

## 🚀 Features
- Upload CSV files containing fitness/workout data  
- Data cleaning and transformation  
- Generate summary statistics  
- Interactive charts using Plotly/Dash  
- Simple web interface for data exploration

---

## 🧰 Tech Stack
- **Python 3.12+**
- **Flask**
- **Pandas**
- **Plotly Dash**
- **Docker**

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/banana0000/Fitness-Tracker.git
cd Fitness-Tracker
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

The web application will start on:  
👉 `http://127.0.0.1:5000/`

---

## 🐳 Docker Setup

Build and run with Docker:

```bash
docker build -t fitness-tracker .
docker run -p 5000:5000 fitness-tracker
```

---

## 📊 Example CSV Format

Use a CSV file like this for uploads:

| date       | activity | duration_minutes | calories |
|-------------|-----------|------------------|-----------|
| 2025-10-31  | Running   | 45               | 420       |
| 2025-11-01  | Cycling   | 60               | 530       |

---

## 📜 License
This project is licensed under the MIT License.

---

## 💡 Future Improvements
- User login and authentication  
- Weekly and monthly progress reports  
- Integration with fitness APIs (e.g., Strava, Garmin)

---

## 👤 Author
Created by **banana0000**  
GitHub: [https://github.com/banana0000](https://github.com/banana0000)