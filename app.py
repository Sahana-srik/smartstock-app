import streamlit as st
import pandas as pd

# --- Hardcoded users (demo) ---
USERS = {"admin": "1234", "user1": "5678"}

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
    st.subheader("📂 Upload Inventory & Sales CSVs")

    inventory_file = st.file_uploader("Upload Inventory CSV", type="csv", key="inv")
    sales_file = st.file_uploader("Upload Sales CSV", type="csv", key="sales")

    if inventory_file:
        try:
            df = pd.read_csv(inventory_file)
            st.session_state["inventory_df"] = df
            st.success("✅ Inventory uploaded!")
        except Exception as e:
            st.error(f"Error reading inventory CSV: {e}")

    if sales_file:
        try:
            df = pd.read_csv(sales_file)
            st.session_state["sales_df"] = df
            st.success("✅ Sales uploaded!")
        except Exception as e:
            st.error(f"Error reading sales CSV: {e}")

    return st.session_state.get("inventory_df"), st.session_state.get("sales_df")

# --- Export CSV ---
def export_csv(df, filename):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(f"⬇️ Download {filename}", csv, file_name=filename, mime="text/csv")

# --- Inventory Page ---
def inventory_page(df):
    st.header("🏪 Inventory Dashboard")
    if df is not None:
        st.dataframe(df)
        df["ExpiryDate"] = pd.to_datetime(df["ExpiryDate"], errors="coerce")

        total_stock = df["Quantity"].sum()
        num_products = df["Product"].nunique()

        # Low-stock check only if 'ReorderLevel' exists
        if "ReorderLevel" in df.columns:
            low_stock = df[df["Quantity"] <= df["ReorderLevel"]]
            low_stock_count = len(low_stock)
        else:
            low_stock = pd.DataFrame()
            low_stock_count = 0

        # Products near expiry
        near_expiry = df[df["ExpiryDate"] <= pd.Timestamp.today() + pd.Timedelta(days=30)]

        # KPIs
        st.subheader("📊 KPIs")
        st.metric("Total Stock", total_stock)
        st.metric("Unique Products", num_products)
        st.metric("Low Stock Products", low_stock_count)
        st.metric("Products Near Expiry", len(near_expiry))

        # Show warnings if needed
        if not low_stock.empty:
            st.warning("⚠️ Low Stock Items")
            st.dataframe(low_stock)

        if not near_expiry.empty:
            st.warning("⚠️ Products Near Expiry")
            st.dataframe(near_expiry)

        # Stock chart
        st.subheader("📦 Stock by Product")
        chart_data = df.groupby("Product")["Quantity"].sum().nlargest(10).reset_index()
        st.bar_chart(chart_data.set_index("Product"))

        # Search
        search_inv = st.text_input("🔍 Search Inventory by Product", key="search_inv")
        if search_inv:
            filtered_inv = df[df["Product"].str.contains(search_inv, case=False)]
            st.write(f"### Search Results for '{search_inv}'")
            st.dataframe(filtered_inv)

        export_csv(df, "inventory.csv")
    else:
        st.info("Upload Inventory CSV to see data.")

# --- Sales Page ---
def sales_page(df):
    st.header("💰 Sales Dashboard")
    if df is not None:
        st.dataframe(df)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        total_sales = df["Quantity"].sum()
        st.subheader("📊 KPIs")

        if not df.empty:
            top_products = df.groupby("Product")["Quantity"].sum().sort_values(ascending=False).head(5)
            st.metric("Total Sales", total_sales)
            st.metric("Top Selling Product", f"{top_products.index[0]} ({top_products.iloc[0]} units)")

            st.subheader("Top 5 Products")
            st.bar_chart(top_products)

            # Sales trend
            sales_trend = df.groupby("Date")["Quantity"].sum().reset_index()
            st.subheader("📈 Sales Trend Over Time")
            st.line_chart(sales_trend.set_index("Date"))

        # Search
        search_sales = st.text_input("🔍 Search Sales by Product", key="search_sales")
        if search_sales:
            filtered_sales = df[df["Product"].str.contains(search_sales, case=False)]
            st.write(f"### Search Results for '{search_sales}'")
            st.dataframe(filtered_sales)

        export_csv(df, "sales.csv")
    else:
        st.info("Upload Sales CSV to see data.")

# --- Main App ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["inventory_df"] = None
        st.session_state["sales_df"] = None

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
        inventory_page(inventory_df)
    else:
        sales_page(sales_df)

if __name__ == "__main__":
    main()



