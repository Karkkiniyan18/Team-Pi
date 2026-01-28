import streamlit as st
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="MediMate",
    page_icon="💊",
    layout="wide"
)

st.title("💊 MediMate – Sales & Stock Management App")
st.caption("Smart inventory, expiry tracking & sales analytics")

# ---------------- SESSION DATA ----------------
if "products" not in st.session_state:
    st.session_state.products = pd.DataFrame(
        columns=["Medicine", "Stock", "Price", "Expiry Date"]
    )

if "sales" not in st.session_state:
    st.session_state.sales = pd.DataFrame(
        columns=["Medicine", "Quantity", "Total Price", "Date"]
    )

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Product", "Add Sale", "Stock & Expiry"]
)

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.subheader("📊 Sales & Stock Dashboard")

    total_sales = st.session_state.sales["Total Price"].sum()
    total_items = st.session_state.sales["Quantity"].sum()
    total_products = len(st.session_state.products)

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Sales", f"₹ {total_sales}")
    col2.metric("📦 Items Sold", total_items)
    col3.metric("💊 Products", total_products)

    st.divider()

    # Sales Chart
    if not st.session_state.sales.empty:
        sales_by_date = st.session_state.sales.groupby("Date")["Total Price"].sum()

        fig, ax = plt.subplots()
        ax.plot(sales_by_date.index, sales_by_date.values)
        ax.set_title("Daily Sales Report")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales (₹)")
        st.pyplot(fig)
    else:
        st.info("No sales data available")

# ================= ADD PRODUCT =================
elif menu == "Add Product":
    st.subheader("➕ Add Medicine Product")

    with st.form("product_form"):
        medicine = st.text_input("Medicine Name")
        stock = st.number_input("Stock Quantity", min_value=1)
        price = st.number_input("Price per Unit (₹)", min_value=1.0)
        expiry = st.date_input("Expiry Date")

        submit = st.form_submit_button("Add Product")

        if submit:
            new_product = {
                "Medicine": medicine,
                "Stock": stock,
                "Price": price,
                "Expiry Date": expiry
            }
            st.session_state.products = pd.concat(
                [st.session_state.products, pd.DataFrame([new_product])],
                ignore_index=True
            )
            st.success("Product added successfully ✅")

# ================= ADD SALE =================
elif menu == "Add Sale":
    st.subheader("🧾 Add Sale Entry")

    if st.session_state.products.empty:
        st.warning("Add products first!")
    else:
        with st.form("sale_form"):
            medicine = st.selectbox(
                "Select Medicine",
                st.session_state.products["Medicine"]
            )
            quantity = st.number_input("Quantity Sold", min_value=1)
            sale_date = st.date_input("Sale Date", date.today())

            submit = st.form_submit_button("Add Sale")

            if submit:
                product = st.session_state.products[
                    st.session_state.products["Medicine"] == medicine
                ].iloc[0]

                if quantity > product["Stock"]:
                    st.error("Not enough stock ❌")
                else:
                    total_price = quantity * product["Price"]

                    # Update sales
                    new_sale = {
                        "Medicine": medicine,
                        "Quantity": quantity,
                        "Total Price": total_price,
                        "Date": sale_date
                    }

                    st.session_state.sales = pd.concat(
                        [st.session_state.sales, pd.DataFrame([new_sale])],
                        ignore_index=True
                    )

                    # Update stock
                    st.session_state.products.loc[
                        st.session_state.products["Medicine"] == medicine,
                        "Stock"
                    ] -= quantity

                    st.success("Sale recorded successfully ✅")

# ================= STOCK & EXPIRY =================
elif menu == "Stock & Expiry":
    st.subheader("📦 Stock & Expiry Monitoring")

    if st.session_state.products.empty:
        st.info("No products available")
    else:
        st.dataframe(st.session_state.products, use_container_width=True)

        st.divider()

        today = date.today()
        near_expiry = st.session_state.products[
            st.session_state.products["Expiry Date"] <= today + timedelta(days=30)
        ]

        low_stock = st.session_state.products[
            st.session_state.products["Stock"] <= 10
        ]

        col1, col2 = st.columns(2)

        with col1:
            st.warning("⏰ Near Expiry (30 days)")
            st.dataframe(near_expiry, use_container_width=True)

        with col2:
            st.error("⚠️ Low Stock Alert")
            st.dataframe(low_stock, use_container_width=True)
