import streamlit as st
import pandas as pd

# --- Hardcoded users (demo) ---
USERS = {"admin": "1234", "user1": "5678"}

# --- Sample Data ---
SAMPLE_INVENTORY = pd.DataFrame({
    "Product": ["Apples", "Bananas", "Oranges"],
    "BatchID": ["A1", "B1", "O1"],
    "Quantity": [100, 150, 120],
    "ExpiryDate": ["2025-09-10", "2025-09-15", "2025-09-12"],
    "ReorderLevel": [20, 30, 25]
})

SAMPLE_SALES = pd.DataFrame({
    "Product": ["Apples", "Bananas", "Oranges"],
    "Quantity": [50, 60, 30],
    "Date": ["2025-08-01", "2025-08-02", "2025-08-03"]
})

# --- Login Function ---
def login():
    st.title("🔐 SmartStock Login")
    user_id = st.text_input("User ID")
    pin = st.text_input("PIN", type="password")
    if st.button("Login"):
        if user_id in USERS and USERS[user_id] == pin:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
        else:
            st.error("❌ Invalid User ID or PIN")

# --- Upload CSVs ---
def upload_csvs():
    st.subheader("📂 Upload Inventory & Sales CSVs (optional)")
    inventory_file = st.file_uploader("Upload Inventory CSV", type="csv", key="inv")
    sales_file = st.file_uploader("Upload Sales CSV", type="csv", key="sales")

    # Load uploaded files if available, else use sample
    if inventory_file:
        try:
            df = pd.read_csv(inventory_file)
            st.session_state["inventory_df"] = df
            st.success("✅ Inventory uploaded!")
        except Exception as e:
            st.error(f"Error reading inventory CSV: {e}")
    elif "inventory_df" not in st.session_state:
        st.session_state["inventory_df"] = SAMPLE_INVENTORY.copy()

    if sales_file:
        try:
            df = pd.read_csv(sales_file)
            st.session_state["sales_df"] = df
            st.success("✅ Sales uploaded!")
        except Exception as e:
            st.error(f"Error reading sales CSV: {e}")
    elif "sales_df" not in st.session_state:
        st.session_state["sales_df"] = SAMPLE_SALES.copy()

    return st.session_state["inventory_df"], st.session_state["sales_df"]

# --- Main App ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None

    if not st.session_state["logged_in"]:
        login()
        return

    st.sidebar.title("Navigation")
    st.sidebar.write(f"Logged in as: **{st.session_state['user_id']}**")
    page = st.sidebar.radio("Go to", ["Inventory", "Sales"])

    if st.sidebar.button("🔒 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.success("You have been logged out!")
        return

    inventory_df, sales_df = upload_csvs()

    if page == "Inventory":
        st.header("🏪 Inventory Dashboard")
        st.dataframe(inventory_df)
    else:
        st.header("💰 Sales Dashboard")
        st.dataframe(sales_df)

if __name__ == "__main__":
    main()
