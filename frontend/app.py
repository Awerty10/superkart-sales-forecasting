
import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend (container name on the Docker network)
BACKEND_URL = "http://backend:7860"

# Page configuration and title
st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecasting")
st.write("Enter the product and store details below to predict the total sales of the product in that store.")

# ---------------- Single prediction ----------------
st.subheader("Single Prediction")

col1, col2 = st.columns(2)
with col1:
    Product_Weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Allocated_Area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0, value=0.027, format="%.3f")
    Product_MRP = st.number_input("Product MRP", min_value=0.0, value=117.08)
    Product_Id_char = st.selectbox("Product ID Prefix (FD = Food, DR = Drinks, NC = Non-Consumable)", ["FD", "DR", "NC"])
with col2:
    Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
    Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, value=16)

# Create the JSON payload expected by the backend
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
        if response.status_code == 200:
            predicted_sales = response.json()["Sales"]
            st.success(f"Predicted Product Store Sales Total: {predicted_sales:,.2f}")
        else:
            st.error(f"Prediction failed: {response.text}")
    except requests.exceptions.RequestException:
        st.error("Unable to connect to the prediction API. Make sure the backend container is running.")

# ---------------- Batch prediction ----------------
st.subheader("Batch Prediction")
st.write("Upload a CSV file with the same 10 feature columns to get predictions for many products at once.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    if st.button("Predict for Batch", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files={"file": uploaded_file.getvalue()}, timeout=60)
            if response.status_code == 200:
                predictions = response.json()
                # Show the uploaded rows together with their predicted sales
                result_df = pd.read_csv(uploaded_file)
                result_df["Predicted_Sales"] = [predictions[str(i)] for i in range(len(result_df))]
                st.success("Batch predictions completed.")
                st.dataframe(result_df)
                st.download_button("Download predictions as CSV", result_df.to_csv(index=False), "superkart_predictions.csv", "text/csv")
            else:
                st.error(f"Batch prediction failed: {response.text}")
        except requests.exceptions.RequestException:
            st.error("Unable to connect to the prediction API. Make sure the backend container is running.")
