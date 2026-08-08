import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio

# ---------------- Page setup ----------------
st.set_page_config(page_title="Investigate Hotel Business", page_icon="🏨", layout="wide")

NAVY, GOLD, CREAM = "#142850", "#D4AF37", "#FAF7F2"
HOTEL_COLORS = {"City Hotel": NAVY, "Resort Hotel": GOLD}

pio.templates["hotel_theme"] = pio.templates["plotly_white"]
pio.templates["hotel_theme"].layout.update(
    font=dict(family="Inter, sans-serif", color=NAVY),
    title=dict(font=dict(family="Playfair Display, serif", size=18, color=NAVY)),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=[NAVY, GOLD],
)
pio.templates.default = "hotel_theme"

# ---------------- Theme CSS ----------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background-color: {CREAM}; }}
section[data-testid="stSidebar"] {{ background: {NAVY}; }}
section[data-testid="stSidebar"] * {{ color: #F1EEE4 !important; }}
section[data-testid="stSidebar"] .stButton>button {{ background: {GOLD}; color: {NAVY} !important; font-weight: 600; border: none; border-radius: 8px; }}
.hero {{ background: linear-gradient(135deg, {NAVY}, #4B3869); border-radius: 16px; padding: 30px 36px; margin-bottom: 22px; }}
.hero h1 {{ font-family: 'Playfair Display', serif; color: #F7EFD9; font-size: 32px; margin: 0 0 4px 0; }}
.hero p {{ color: #CBD5E1; margin: 0; }}
.kpi-card {{ background: #fff; border-radius: 12px; padding: 14px 18px; border-left: 4px solid {GOLD}; box-shadow: 0 3px 10px rgba(20,40,80,0.08); }}
.kpi-label {{ color: #6b7280; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
.kpi-value {{ color: {NAVY}; font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; }}
.stTabs [aria-selected="true"] {{ color: {NAVY} !important; border-bottom: 3px solid {GOLD} !important; }}
h1, h2, h3 {{ font-family: 'Playfair Display', serif; color: {NAVY}; }}
</style>
""", unsafe_allow_html=True)

def kpi_card(label, value):
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

# ---------------- Data loading & cleaning ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("hotel_bookings_data.csv")
    df["company"] = df["company"].fillna(0)
    df["agent"] = df["agent"].fillna(0)
    df["city"] = df["city"].fillna("Unknown")
    df["children"] = df["children"].fillna(0)
    df = df.drop_duplicates()
    df["meal"] = df["meal"].replace("Undefined", "No Meal")
    df = df[df["adr"] >= 0]
    df = df[(df["adults"] + df["children"] + df["babies"]) > 0]
    df["total_stay"] = df["stays_in_weekend_nights"] + df["stays_in_weekdays_nights"]
    df["lead_time_bucket"] = pd.cut(
        df["lead_time"], bins=[-1, 7, 30, 90, 180, 365, df["lead_time"].max()],
        labels=["0-7", "8-30", "31-90", "91-180", "181-365", "365+"],
    )
    return df

df = load_data()
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# ---------------- Sidebar filters ----------------
st.sidebar.header("🔎 Filters")
ALL_HOTELS = sorted(df["hotel"].unique())
ALL_YEARS = sorted(df["arrival_date_year"].unique())

st.session_state.setdefault("hotel_filter", ALL_HOTELS)
st.session_state.setdefault("year_filter", ALL_YEARS)
st.session_state.setdefault("stay_slider", 15)

def reset_filters():
    st.session_state["hotel_filter"] = ALL_HOTELS
    st.session_state["year_filter"] = ALL_YEARS
    st.session_state["stay_slider"] = 15

hotels = st.sidebar.multiselect("Hotel type", ALL_HOTELS, key="hotel_filter")
years = st.sidebar.multiselect("Arrival year", ALL_YEARS, key="year_filter")
st.sidebar.button("🔄 Reset Filters", on_click=reset_filters, use_container_width=True)

filtered = df[df["hotel"].isin(hotels) & df["arrival_date_year"].isin(years)]
st.sidebar.caption(f"Showing {len(filtered):,} of {len(df):,} bookings")

# ---------------- Hero banner ----------------
st.markdown("""
<div class="hero">
    <h1>🏨 Investigate Hotel Business</h1>
    <p>Explore Booking Trends &amp; Cancellation Patterns in Real Time</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Problem Statement & Objective", "📊 Analysis Dashboard", "💡 Insights & Recommendations"])

# ======================== TAB 1 ========================
with tab1:
    st.header("Problem Statement")
    st.subheader("Why booking behaviour matters")
    st.write(
        "Understanding customer booking behaviour is central to running a hotel profitably. "
        "It helps management forecast demand, price rooms dynamically, reduce revenue lost to "
        "cancellations, and design retention policies for guests most likely to cancel."
    )
    st.subheader("Business Questions")
    st.markdown(
        "1. **Which hotel type do customers book most often?**\n"
        "2. **Does length of stay affect the cancellation rate?**\n"
        "3. **Does lead time affect the cancellation rate?**"
    )
    st.subheader("Project Objective")
    st.write(
        "To analyse ~119,000 hotel bookings from 2017–2019, clean the data, and turn "
        "visualisations of the three questions above into concrete recommendations for "
        "hotel management."
    )
    st.subheader("Dataset Overview")
    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("🗂️ Total Bookings", f"{len(df):,}")
    with c2: kpi_card("📅 Period Covered", "2017 – 2019")
    with c3: kpi_card("📊 Columns", f"{df.shape[1]}")

# ======================== TAB 2 ========================
with tab2:
    if filtered.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🛎️ Total Bookings", f"{len(filtered):,}")
    with c2: kpi_card("📉 Cancellation Rate", f"{filtered['is_canceled'].mean()*100:.1f}%")
    with c3: kpi_card("⏳ Avg. Lead Time", f"{filtered['lead_time'].mean():.0f} days")
    with c4: kpi_card("💰 Avg. Daily Rate", f"${filtered['adr'].mean():.2f}")
    st.markdown("---")

    st.header("1. Which hotel type is booked most often?")
    c1, c2 = st.columns([1, 2])
    with c1:
        share = filtered["hotel"].value_counts().reset_index()
        share.columns = ["hotel", "count"]
        fig = px.pie(share, names="hotel", values="count", color="hotel",
                     color_discrete_map=HOTEL_COLORS, title="Share of Bookings by Hotel Type")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        monthly = filtered.groupby(["arrival_date_month", "hotel"]).size().reset_index(name="bookings")
        fig = px.bar(monthly, x="arrival_date_month", y="bookings", color="hotel", barmode="group",
                     category_orders={"arrival_date_month": MONTHS}, color_discrete_map=HOTEL_COLORS,
                     title="Bookings per Month by Hotel Type",
                     labels={"arrival_date_month": "Month", "bookings": "Bookings"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("2. Does length of stay affect cancellation rate?")
    c1, c2 = st.columns(2)
    with c1:
        cbh = (filtered.groupby("hotel")["is_canceled"].mean() * 100).reset_index()
        cbh.columns = ["hotel", "rate"]
        fig = px.bar(cbh, x="hotel", y="rate", color="hotel", color_discrete_map=HOTEL_COLORS,
                     title="Overall Cancellation Rate by Hotel Type", text_auto=".1f",
                     labels={"rate": "Cancellation Rate (%)", "hotel": ""})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        max_stay = st.slider("Max nights to display", 5, 30, key="stay_slider")
        sc = filtered[filtered["total_stay"] <= max_stay].groupby(["total_stay", "hotel"])["is_canceled"].mean().reset_index()
        sc["is_canceled"] *= 100
        fig = px.line(sc, x="total_stay", y="is_canceled", color="hotel", markers=True,
                      color_discrete_map=HOTEL_COLORS, title="Cancellation Rate by Length of Stay",
                      labels={"total_stay": "Total Nights", "is_canceled": "Cancellation Rate (%)"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("3. Does lead time affect cancellation rate?")
    lc = filtered.groupby(["lead_time_bucket", "hotel"], observed=True)["is_canceled"].mean().reset_index()
    lc["is_canceled"] *= 100
    fig = px.bar(lc, x="lead_time_bucket", y="is_canceled", color="hotel", barmode="group",
                 color_discrete_map=HOTEL_COLORS, title="Cancellation Rate by Lead Time Bucket",
                 labels={"lead_time_bucket": "Lead Time (days)", "is_canceled": "Cancellation Rate (%)"},
                 text_auto=".1f")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("View underlying numbers"):
        st.dataframe(lc.pivot(index="lead_time_bucket", columns="hotel", values="is_canceled").round(1))

# ======================== TAB 3 ========================
with tab3:
    st.header("Key Findings")
    st.markdown(
        "- **Hotel type:** City Hotel = 61% of bookings, Resort Hotel = 39%.\n"
        "- **Seasonality:** Both hotel types peak in **October**, trough in **March**.\n"
        "- **Cancellation:** City Hotel ~30%, Resort Hotel ~24%.\n"
        "- **Stay duration:** Cancellation rises from ~25% (1–3 nights) to ~32% (7+ nights).\n"
        "- **Lead time:** Strongest driver — rises from ~6–10% (0–7 days) to over 50% "
        "for City Hotel bookings made 365+ days ahead."
    )
    st.header("Recommendations")
    st.subheader("Hotel type & seasonality")
    st.markdown(
        """
        - Run targeted off-season promotions for Resort Hotel (its smaller 39% share)
          to close the gap with City Hotel, especially outside the October peak.
        - Since both hotel types peak together in October, plan staffing and dynamic
          pricing increases jointly around that period rather than treating each hotel
          type's calendar independently.
        """
    )
    st.subheader("Stay duration & cancellations")
    st.markdown(
        """
        - Because the stay-duration effect is real but modest, pair it with lead-time
          policy rather than treating it as a standalone lever — e.g. a moderately
          stricter cancellation window for stays of 5+ nights.
        - Offer a small discount for guests who commit to a longer stay with a
          non-refundable or partially-refundable rate, to lock in revenue on higher-value bookings.
        """
    )
    st.subheader("Lead time")
    st.markdown(
        """
        - Since cancellation risk rises sharply with lead time, require a **deposit or
          partial prepayment** for bookings made more than ~90 days in advance, where
          cancellation rates exceed 30%.
        - Send a **confirmation/reminder email with a reschedule option** at a set point
          before arrival for long-lead-time bookings, to catch guests who'd otherwise cancel outright.    
        """          
    )
    st.info(
        "**Lead time is the strongest and most actionable driver of cancellations in this "
        "dataset** — the cancellation rate rises from single digits for last-minute City "
        "Hotel bookings to over 50% for bookings made more than a year ahead. Introducing "
        "a deposit requirement for long-lead-time bookings directly targets the segment "
        "responsible for the largest share of lost revenue, and should have more impact "
        "than adjustments to stay-duration policy alone."
    )
    st.caption("Figures computed live from the cleaned dataset loaded in this app.")