# 🏨 Investigate Hotel Business using Data Visualization

Understanding Booking & Cancellation Behaviour — 2017–2019

## Project Overview

This project analyses ~119,000 real-world hotel bookings (City Hotel & Resort Hotel, 2017–2019) to answer three business questions for a hotel company:

1. Which hotel type do customers book most often, and how does that vary by season?
2. Does length of stay affect the booking cancellation rate?
3. Does lead time (days between booking and arrival) affect the cancellation rate?

The dataset is cleaned and analysed in a Jupyter Notebook, and the same analysis is rebuilt as an interactive Streamlit dashboard, deployed publicly.

## 🔗 Links

- **Live App:** [investigatehotelbusiness-ghfbyj8raaur2zxksivl7z.streamlit.app](https://investigatehotelbusiness-ghfbyj8raaur2zxksivl7z.streamlit.app/)
- **Repository:** github.com/abhi-1009/Investigate_Hotel_Business

## 📁 Repository Contents

| File | Description |
|---|---|
| `hotel_analysis.ipynb` | Full Jupyter Notebook — data cleaning, analysis, charts, and written answers to every project question |
| `hotel_booking_analysis.py` | Streamlit dashboard app (3 tabs: Problem Statement, Analysis Dashboard, Insights & Recommendations) |
| `hotel_bookings_data.csv` | Raw dataset (119,390 bookings × 29 columns) |
| `requirements.txt` | Python dependencies |
| `Hotel_Business_Analysis_Report.docx` | Full written project report |

## 📊 Dataset

- **Rows (raw):** 119,390
- **Columns:** 29
- **Period:** 2017–2019
- **Hotel types:** City Hotel, Resort Hotel

Key columns: `hotel`, `is_canceled`, `arrival_date_month`, `stays_in_weekend_nights` / `stays_in_weekdays_nights`, `lead_time`, `adr`.

## 🧹 Data Cleaning Summary

- **Missing values filled:** `company` (94% missing → 0), `agent` (14% missing → 0), `city` (→ 'Unknown'), `children` (→ 0)
- **Duplicates removed:** 33,261 fully duplicate rows
- **Inconsistent values fixed:** `meal` = 'Undefined' merged into 'No Meal'
- **Anomalies removed:** 1 row with negative `adr`, 180 rows with zero total guests
- **Final dataset:** 85,963 rows

## 📈 Key Insights

- **Hotel type:** City Hotel = 61% of bookings, Resort Hotel = 39%
- **Seasonality:** Both hotel types peak in **October** and trough in **March**
- **Cancellation by hotel type:** City Hotel ~30.2%, Resort Hotel ~23.5%
- **Stay duration:** Cancellation rises from ~25% (1–3 nights) to ~32% (7+ nights)
- **Lead time (strongest driver):** Cancellation rises from ~6–10% (0–7 day lead time) to over 50% for City Hotel bookings made 365+ days ahead

## 💡 Top Recommendation

Require a deposit or partial prepayment for bookings made more than ~90 days in advance — lead time is the strongest and most consistent driver of cancellations in the dataset, and City Hotel (61% of all bookings) shows the sharpest rise.

## 🛠️ Tech Stack

- **Analysis:** Python, Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn
- **Dashboard:** Streamlit
- **Deployment:** Streamlit Community Cloud

## ▶️ Running Locally

```bash
# Clone the repo
git clone https://github.com/abhi-1009/Investigate_Hotel_Business.git
cd Investigate_Hotel_Business

# Install dependencies
pip install -r requirements.txt

# Run the Jupyter Notebook
jupyter notebook hotel_analysis.ipynb

# OR run the Streamlit dashboard
streamlit run hotel_booking_analysis.py
```

The app will open at `http://localhost:8501`.

## 🚀 Deployment

Deployed on [Streamlit Community Cloud](https://share.streamlit.io):
1. Push this repository to GitHub (public).
2. Sign in to share.streamlit.io with GitHub.
3. Click **New app** → select this repo → branch `main` → main file `hotel_booking_analysis.py`.
4. Click **Deploy**.

## 👤 Author

ABHIJIT SINHA 