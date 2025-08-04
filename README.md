# 🌾 ICRISAT Agricultural Data Dashboard

A comprehensive data analysis project on agricultural production in India using ICRISAT district-level data. This project includes an interactive **Streamlit dashboard**, **Power BI report**, and SQL-based exploratory data analysis.

---

## 📁 Project Structure

```
📦 agriproj/
├── dashboard.py              # Streamlit dashboard with SQL and CSV modes
├── eda.sql                   # SQL queries for key insights
├── eda.ipynb                 # Jupyter notebook for data exploration
├── EDA.pbix                  # Power BI file for advanced visualization
├── requirements.txt          # Python dependencies
├── data/
│   └── ICRISAT-District Level Data.csv  # Raw data file
└── README.md                 # Project overview
```

---

## 🔧 Features

### 🧪 Exploratory Data Analysis (Jupyter Notebook)
- Data cleaning and transformation
- Summary statistics and visualizations
- Correlation heatmaps and bar charts

### 🐍 Streamlit Dashboard (`dashboard.py`)
- Two interactive modes:
  - **📁 CSV Explorer** – For histograms, correlations, and visual exploration
  - **📊 SQL Explorer** – Connects to PostgreSQL and visualizes custom SQL queries

### 📊 Power BI Report (`EDA.pbix`)
- Clean and interactive data dashboards based on the same logic used in SQL queries

---

## 💽 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL
- Create a database `agriculture_data`
- Import the cleaned CSV data into a table named `agriculture_data`
- Update DB credentials in `dashboard.py` if needed

### 3. Run Streamlit App
```bash
streamlit run dashboard.py
```

---

## 📂 Data Source

- [ICRISAT District-Level Agricultural Data](https://www.icrisat.org/)

---

