import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="AI Ride Pricing Engine", layout="wide")

# --------------------------------------------------
# 🔐 LOGIN SYSTEM (FIXED VERSION)
# --------------------------------------------------

def login():

    st.title("🔐 Login - AI Ride Pricing Dashboard")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid Username or Password")


# Initialize login state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()
    
# --------------------------------------------------
# DASHBOARD STARTS AFTER LOGIN
# --------------------------------------------------

st.title("🚕 AI Dynamic Ride Pricing & Revenue Optimization System")
st.markdown("---")

# Logout Button
if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------
if "data" not in st.session_state:
    st.session_state["data"] = pd.read_csv("dynamic_pricing.csv")

df = st.session_state["data"]

df["Ride_ID"] = range(1, len(df) + 1)

# --------------------------------------------------
# Sidebar Controls
# --------------------------------------------------
st.sidebar.header("⚙️ Real-Time Controls")

selected_ride = st.sidebar.selectbox(
    "Select Ride ID",
    df["Ride_ID"]
)

current_drivers = int(df.loc[df["Ride_ID"] == selected_ride, "Number_of_Drivers"])

new_drivers = st.sidebar.slider(
    "Update Available Drivers",
    1,
    100,
    current_drivers
)

df.loc[df["Ride_ID"] == selected_ride, "Number_of_Drivers"] = new_drivers

# --------------------------------------------------
# Price Optimization Logic
# --------------------------------------------------
def optimize_price(row):
    base_price = row["Historical_Cost_of_Ride"]
    riders = row["Number_of_Riders"]
    drivers = row["Number_of_Drivers"]
    rating = row["Average_Ratings"]

    ratio = riders / drivers

    if ratio > 2:
        base_price *= 1.30
    elif ratio > 1.5:
        base_price *= 1.15
    elif drivers > riders:
        base_price *= 0.90

    if rating > 4.5:
        base_price *= 1.05

    return round(base_price, 2)

df["Optimized_Ride_Price"] = df.apply(optimize_price, axis=1)

# --------------------------------------------------
# Revenue Calculation
# --------------------------------------------------
df["Estimated_Revenue"] = df["Optimized_Ride_Price"] * df["Number_of_Riders"]
total_revenue = df["Estimated_Revenue"].sum()

# --------------------------------------------------
# KPI Section
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"₹ {round(total_revenue,2)}")
col2.metric("🚗 Total Drivers", int(df["Number_of_Drivers"].sum()))
col3.metric("⭐ Avg Rating", round(df["Average_Ratings"].mean(),2))

st.markdown("---")

# --------------------------------------------------
# 📊 Charts Section (1 Pie + 1 Bar)
# --------------------------------------------------
st.subheader("📊 Analytics Overview")

colA, colB = st.columns(2)

top5 = df.sort_values("Estimated_Revenue", ascending=False).head(5)

# -------- PIE CHART (Revenue Share) --------
with colA:
    fig1, ax1 = plt.subplots(figsize=(4,4))

    ax1.pie(
        top5["Estimated_Revenue"],
        labels=top5["Ride_ID"],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'color': 'white'}
    )

    fig1.patch.set_alpha(0.0)
    ax1.set_facecolor("none")
    ax1.set_title("Top 5 Revenue Share", color="white")

    st.pyplot(fig1)
    plt.close(fig1)

# -------- BAR CHART (Average Ratings) --------
with colB:
    fig2, ax2 = plt.subplots(figsize=(4,4))

    top5_rating = df.sort_values("Average_Ratings", ascending=False).head(5)

    ax2.bar(top5_rating["Ride_ID"], top5_rating["Average_Ratings"])
    ax2.set_xlabel("Ride ID", color="white")
    ax2.set_ylabel("Average Rating", color="white")
    ax2.set_title("Top 5 Average Ratings", color="white")

    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')

    fig2.patch.set_alpha(0.0)
    ax2.set_facecolor("none")

    st.pyplot(fig2)
    plt.close(fig2)

st.markdown("---")

# --------------------------------------------------
# Data Table
# --------------------------------------------------
st.subheader("📋 Optimized Ride Pricing Table")
st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# Download Button
# --------------------------------------------------
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Optimized Ride Pricing Data",
    data=csv,
    file_name="optimized_ride_pricing.csv",
    mime="text/csv"
)