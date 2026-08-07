import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Hotel Business Analysis",
    layout="wide",
)

sns.set_style("whitegrid")

# ----------------------------------------------------------------------
# Data loading + cleaning
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("hotel_bookings_data.csv")

    # Missing values
    df["company"] = df["company"].fillna(0)
    df["agent"] = df["agent"].fillna(0)
    df["city"] = df["city"].fillna("Unknown")
    df["children"] = df["children"].fillna(0)

    # Duplicates
    df = df.drop_duplicates()

    # Inconsistent values
    df["meal"] = df["meal"].replace("Undefined", "No Meal")

    # Anomalies
    df = df[df["adr"] >= 0]
    df = df[(df["adults"] + df["children"] + df["babies"]) > 0]

    # Derived columns
    df["total_stay"] = df["stays_in_weekend_nights"] + df["stays_in_weekdays_nights"]
    df["lead_time_bucket"] = pd.cut(
        df["lead_time"],
        bins=[-1, 7, 30, 90, 180, 365, df["lead_time"].max()],
        labels=["0-7", "8-30", "31-90", "91-180", "181-365", "365+"],
    )
    return df

df = load_data()

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# ----------------------------------------------------------------------
# Sidebar filters (apply to the Analysis Dashboard tab)
# ----------------------------------------------------------------------
st.sidebar.header("Filters")

ALL_HOTELS = sorted(df["hotel"].unique())
ALL_YEARS = sorted(df["arrival_date_year"].unique())

# Initialize session state defaults (only runs once per session)
if "hotel_filter" not in st.session_state:
    st.session_state["hotel_filter"] = ALL_HOTELS
if "year_filter" not in st.session_state:
    st.session_state["year_filter"] = ALL_YEARS
if "stay_slider" not in st.session_state:
    st.session_state["stay_slider"] = 15

def reset_filters():
    st.session_state["hotel_filter"] = ALL_HOTELS
    st.session_state["year_filter"] = ALL_YEARS
    st.session_state["stay_slider"] = 15

hotel_options = st.sidebar.multiselect(
    "Hotel type", options=ALL_HOTELS, key="hotel_filter"
)
year_options = st.sidebar.multiselect(
    "Arrival year", options=ALL_YEARS, key="year_filter"
)

st.sidebar.button("🔄 Reset Filters", on_click=reset_filters, use_container_width=True)

filtered = df[df["hotel"].isin(hotel_options) & df["arrival_date_year"].isin(year_options)]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered):,} of {len(df):,} bookings")
st.sidebar.caption("Filters apply to the Analysis Dashboard tab.")

# ----------------------------------------------------------------------
# Title
# ----------------------------------------------------------------------
st.title("🏨 Investigate Hotel Business using Data Visualization")
st.caption("Understanding Booking & Cancellation Behaviour — 2017–2019")

tab1, tab2, tab3 = st.tabs([
    "📋 Problem Statement & Objective",
    "📊 Analysis Dashboard",
    "💡 Insights & Recommendations",
])

# ========================================================================
# TAB 1 — Problem Statement & Business Objective
# ========================================================================
with tab1:
    st.header("Problem Statement")

    st.subheader("Why booking behaviour matters")
    st.write(
        """
        Understanding customer booking behaviour is central to running a hotel profitably.
        It helps management forecast demand and staff accordingly, price rooms dynamically
        across the year, reduce revenue lost to last-minute cancellations, and design
        retention or deposit policies aimed at the guests most likely to cancel. Without
        this insight, hotels either over-book to compensate for cancellations (risking
        guest dissatisfaction) or under-book (leaving rooms empty and revenue on the table).
        """
    )

    st.subheader("Business Questions")
    st.markdown(
        """
        1. **Which hotel type do customers book most often?**
        2. **Does the length of stay affect the booking cancellation rate?**
        3. **Does lead time (the gap between booking and arrival) affect the cancellation rate?**
        """
    )

    st.subheader("Project Objective")
    st.write(
        """
        To analyse ~119,000 hotel bookings from 2017–2019, clean and prepare the data,
        and produce a set of visualisations that answer the three business questions
        above — turning them into concrete, evidence-based recommendations that help
        hotel management grow bookings and reduce cancellation-related revenue loss.
        """
    )

    st.subheader("Dataset Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Bookings", f"{len(df):,}")
    c2.metric("Period Covered", "2017 – 2019")
    c3.metric("Columns", f"{df.shape[1]}")

    st.caption(
        "Key columns: `hotel`, `is_canceled`, `arrival_date_month`, "
        "`stays_in_weekend_nights` / `stays_in_weekdays_nights`, `lead_time`."
    )

# ========================================================================
# TAB 2 — Analysis Dashboard (interactive charts)
# ========================================================================
with tab2:
    if filtered.empty:
        st.warning("No data matches the selected filters. Please adjust the filters in the sidebar.")
        st.stop()

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bookings", f"{len(filtered):,}")
    col2.metric("Cancellation Rate", f"{filtered['is_canceled'].mean() * 100:.1f}%")
    col3.metric("Avg. Lead Time", f"{filtered['lead_time'].mean():.0f} days")
    col4.metric("Avg. Daily Rate (ADR)", f"{filtered['adr'].mean():.2f}")

    st.markdown("---")

    HOTEL_COLORS = {"City Hotel": "#4C72B0", "Resort Hotel": "#DD8452"}

    # Q1: Hotel type & seasonality
    st.header("1. Which hotel type is booked most often?")
    c1, c2 = st.columns([1, 2])

    with c1:
        hotel_share = filtered["hotel"].value_counts().reset_index()
        hotel_share.columns = ["hotel", "count"]
        fig = px.pie(
            hotel_share, names="hotel", values="count",
            color="hotel", color_discrete_map=HOTEL_COLORS,
            title="Share of Bookings by Hotel Type", hole=0.0,
        )
        fig.update_traces(textinfo="percent+label", hovertemplate="%{label}<br>%{value:,} bookings<br>%{percent}")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        monthly = (filtered.groupby(["arrival_date_month", "hotel"])
                   .size().reset_index(name="bookings"))
        fig = px.bar(
            monthly, x="arrival_date_month", y="bookings", color="hotel",
            barmode="group", category_orders={"arrival_date_month": MONTH_ORDER},
            color_discrete_map=HOTEL_COLORS,
            title="Bookings per Month by Hotel Type",
            labels={"arrival_date_month": "Month", "bookings": "Number of Bookings"},
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Q2: Stay duration vs cancellation
    st.header("2. Does length of stay affect cancellation rate?")
    c1, c2 = st.columns(2)

    with c1:
        cancel_by_hotel = (filtered.groupby("hotel")["is_canceled"].mean() * 100).reset_index()
        cancel_by_hotel.columns = ["hotel", "cancel_rate"]
        fig = px.bar(
            cancel_by_hotel, x="hotel", y="cancel_rate", color="hotel",
            color_discrete_map=HOTEL_COLORS,
            title="Overall Cancellation Rate by Hotel Type",
            labels={"cancel_rate": "Cancellation Rate (%)", "hotel": ""},
            text_auto=".1f",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        max_stay = st.slider("Max nights to display", 5, 30, key="stay_slider")
        stay_cancel = (filtered[filtered["total_stay"] <= max_stay]
                       .groupby(["total_stay", "hotel"])["is_canceled"]
                       .mean().reset_index())
        stay_cancel["is_canceled"] *= 100
        fig = px.line(
            stay_cancel, x="total_stay", y="is_canceled", color="hotel",
            markers=True, color_discrete_map=HOTEL_COLORS,
            title="Cancellation Rate by Length of Stay",
            labels={"total_stay": "Total Nights Stayed", "is_canceled": "Cancellation Rate (%)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Q3: Lead time vs cancellation
    st.header("3. Does lead time affect cancellation rate?")
    lead_cancel = (filtered.groupby(["lead_time_bucket", "hotel"], observed=True)["is_canceled"]
                   .mean().reset_index())
    lead_cancel["is_canceled"] *= 100
    fig = px.bar(
        lead_cancel, x="lead_time_bucket", y="is_canceled", color="hotel",
        barmode="group", color_discrete_map=HOTEL_COLORS,
        title="Cancellation Rate by Lead Time Bucket",
        labels={"lead_time_bucket": "Lead Time (days before arrival)", "is_canceled": "Cancellation Rate (%)"},
        text_auto=".1f",
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View underlying numbers"):
        st.dataframe(
            lead_cancel.pivot(index="lead_time_bucket", columns="hotel", values="is_canceled").round(1)
        )

# ========================================================================
# TAB 3 — Insights & Recommendations
# ========================================================================
with tab3:
    st.header("Key Findings")

    st.markdown(
        """
        - **Hotel type:** City Hotel accounts for roughly **61%** of all bookings versus
          **39%** for Resort Hotel — City Hotel is booked far more often overall.
        - **Seasonality:** Both hotel types peak around **October** and are quietest in
          **March**, suggesting a shared seasonal travel pattern rather than one hotel
          type driving the other.
        - **Cancellation by hotel type:** City Hotel has a notably higher cancellation
          rate (**~30%**) than Resort Hotel (**~24%**).
        - **Stay duration:** Cancellation rate rises slightly as length of stay increases
          for both hotel types, though the relationship is fairly weak on its own.
        - **Lead time:** This is the strongest pattern in the data — cancellation rate
          climbs steadily the further in advance a booking is made, from about **6–10%**
          for bookings made within a week of arrival to over **45–53%** for bookings made
          more than a year out (City Hotel shows this rise most sharply).
        """
    )

    st.markdown("---")
    st.header("Recommendations")

    st.subheader("1. Hotel type & seasonality")
    st.markdown(
        """
        - Run targeted off-season promotions for Resort Hotel (its smaller 39% share)
          to close the gap with City Hotel, especially outside the October peak.
        - Since both hotel types peak together in October, plan staffing and dynamic
          pricing increases jointly around that period rather than treating each hotel
          type's calendar independently.
        """
    )

    st.subheader("2. Stay duration & cancellations")
    st.markdown(
        """
        - Because the stay-duration effect is real but modest, pair it with lead-time
          policy rather than treating it as a standalone lever — e.g. a moderately
          stricter cancellation window for stays of 5+ nights.
        - Offer a small discount for guests who commit to a longer stay with a
          non-refundable or partially-refundable rate, to lock in revenue on higher-value bookings.
        """
    )

    st.subheader("3. Lead time")
    st.markdown(
        """
        - Since cancellation risk rises sharply with lead time, require a **deposit or
          partial prepayment** for bookings made more than ~90 days in advance, where
          cancellation rates exceed 30%.
        - Send a **confirmation/reminder email with a reschedule option** at a set point
          before arrival for long-lead-time bookings, to catch guests who'd otherwise cancel outright.
        """
    )

    st.subheader("Highest-impact recommendation")
    st.info(
        "**Lead time is the strongest and most actionable driver of cancellations in this "
        "dataset** — the cancellation rate rises from single digits for last-minute City "
        "Hotel bookings to over 50% for bookings made more than a year ahead. Introducing "
        "a deposit requirement for long-lead-time bookings directly targets the segment "
        "responsible for the largest share of lost revenue, and should have more impact "
        "than adjustments to stay-duration policy alone."
    )

    st.caption("Figures computed live from the cleaned dataset loaded in this app.")