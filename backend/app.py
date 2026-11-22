
# Import necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask app with a name
superkart_api = Flask("SuperKart")

# Load the trained model pipeline (preprocessing + model)
model = joblib.load("superkart_model.joblib")

# Feature columns expected by the model, in the order used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Home route - confirms the API is running
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Forecasting API"


# Endpoint to predict sales for a single product-store combination
@superkart_api.post("/v1/predict")
def predict_sales():
    # Get the JSON data from the request
    data = request.get_json()

    # Check that all required features are present
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Convert the input into a one-row DataFrame with the expected columns
    input_data = pd.DataFrame([{f: data[f] for f in FEATURES}])

    # Make a prediction using the trained model
    prediction = model.predict(input_data).tolist()[0]

    # Return the prediction as a JSON response
    return jsonify({"Sales": round(prediction, 2)})


# Endpoint to predict sales for a batch of products uploaded as a CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files["file"]

    # Read the file into a DataFrame
    input_data = pd.read_csv(file)

    # Check that all required features are present
    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Make predictions for the batch data
    predictions = model.predict(input_data[FEATURES]).tolist()

    # Map each row index to its predicted sales
    output_dict = {str(i): round(pred, 2) for i, pred in enumerate(predictions)}
    return jsonify(output_dict)


# Run the Flask app in debug mode (for local testing only; Gunicorn is used in Docker)
if __name__ == "__main__":
    superkart_api.run(debug=True)
