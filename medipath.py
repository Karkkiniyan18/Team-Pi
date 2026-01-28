import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="Medimate",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Medimate – Medical Sales & Stock Management")

# -----------------------------
# Initialize Session State Data
# -----------------------------
if "products" not in st.session_state:
    st.session_state.products = pd.DataFrame(
        columns=["Product Name", "Stock", "Price", "Expiry Date", "Total Sales"]
    )

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Add / Update Products", "Sales Entry", "Expiry Alerts"]
)

# =========================================================
# 1️⃣ DASHBOARD PAGE
# =========================================================
if page == "Dashboard":
    st.header("📊 Sales & Stock Dashboard")

    if st.session_state.products.empty:
        st.info("No product data available. Please add products first.")
    else:
        col1, col2 = st.columns(2)

        # -------- Pie Chart: Highest Sales --------
        with col1:
            st.subheader("🔹 Highest Sales by Product")
            sales_data = st.session_state.products.set_index("Product Name")["Total Sales"]

            fig1, ax1 = plt.subplots()
            ax1.pie(sales_data, labels=sales_data.index, autopct="%1.1f%%")
            ax1.axis("equal")
            st.pyplot(fig1)

        # -------- Pie Chart: Highest Stock --------
        with col2:
            st.subheader("🔹 Highest Stock by Product")
            stock_data = st.session_state.products.set_index("Product Name")["Stock"]

            fig2, ax2 = plt.subplots()
            ax2.pie(stock_data, labels=stock_data.index, autopct="%1.1f%%")
            ax2.axis("equal")
            st.pyplot(fig2)

        st.subheader("📋 Current Product Data")
        st.dataframe(st.session_state.products, use_container_width=True)

# =========================================================
# 2️⃣ ADD / UPDATE PRODUCTS PAGE
# =========================================================
elif page == "Add / Update Products":
    st.header("📦 Add or Update Products")

    with st.form("product_form"):
        product_name = st.text_input("Product Name")
        stock = st.number_input("Stock Quantity", min_value=0)
        price = st.number_input("Price per Unit", min_value=0.0)
        expiry_date = st.date_input("Expiry Date")

        submitted = st.form_submit_button("Save Product")

        if submitted:
            new_product = {
                "Product Name": product_name,
                "Stock": stock,
                "Price": price,
                "Expiry Date": expiry_date,
                "Total Sales": 0
            }

            st.session_state.products = pd.concat(
                [st.session_state.products, pd.DataFrame([new_product])],
                ignore_index=True
            )

            st.success(f"✅ Product '{product_name}' added successfully!")

    st.subheader("📋 Product List")
    st.dataframe(st.session_state.products, use_container_width=True)

# =========================================================
# 3️⃣ SALES ENTRY PAGE
# =========================================================
elif page == "Sales Entry":
    st.header("💰 Record Sales")

    if st.session_state.products.empty:
        st.warning("No products available. Please add products first.")
    else:
        product = st.selectbox(
            "Select Product",
            st.session_state.products["Product Name"]
        )
        quantity_sold = st.number_input("Quantity Sold", min_value=1)

        if st.button("Record Sale"):
            idx = st.session_state.products[
                st.session_state.products["Product Name"] == product
            ].index[0]

            if st.session_state.products.at[idx, "Stock"] >= quantity_sold:
                st.session_state.products.at[idx, "Stock"] -= quantity_sold
                st.session_state.products.at[idx, "Total Sales"] += quantity_sold
                st.success(f"✅ Sale recorded for {product}")
            else:
                st.error("❌ Not enough stock available!")

# =========================================================
# 4️⃣ EXPIRY ALERTS PAGE
# =========================================================
elif page == "Expiry Alerts":
    st.header("⏰ Expiry Date Alerts")

    if st.session_state.products.empty:
        st.info("No products available.")
    else:
        today = datetime.today().date()
        alert_date = today + timedelta(days=30)

        expiring_products = st.session_state.products[
            st.session_state.products["Expiry Date"] <= alert_date
        ]

        if expiring_products.empty:
            st.success("🎉 No products expiring within 30 days!")
        else:
            st.warning("⚠️ Products Expiring Within 30 Days")
            st.dataframe(expiring_products, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("© 2026 Medimate | Medical Sales & Stock Tracking System")
