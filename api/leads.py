import json
import mysql.connector
import requests
from fastapi import APIRouter
import hashlib
from environs import Env

env = Env()
env.read_env()

# Connect to the database
db = mysql.connector.connect(
    host=env("HOST"),
    user=env("USER_"),
    password=env("PASSWORD"),
    database=env("DBNAME")
)


# Function to fetch leads from SuiteCRM
def fetch_leads():
    url = "https://suitecrmdemo.dtbc.eu/service/v4/rest.php"
    username = "Demo"
    password = "Demo"  # Replace with the actual password

    # Authenticate with SuiteCRM and retrieve the session ID
    session_data = {
        "user_auth": {
            "user_name": username,
            "password": hashlib.md5(password.encode()).hexdigest(),
            "version": "1"
        },
        "application_name": "RestTest",
    }
    auth_data = {
        "method": "login",
        "input_type": "JSON",
        "response_type": "JSON",
        "rest_data": json.dumps(session_data),
    }
    auth_response = requests.post(url, data=auth_data)

    try:
        session_id = auth_response.json().get("id")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response.")
        return []

    # Use the obtained session ID to fetch leads
    if session_id:
        leads_data = {
            "session": session_id,
            "module_name": "Leads",
            "query": "",
            "order_by": "",
            "offset": "",
            "select_fields": ["phone_work", "first_name", "last_name"],
            "link_name_to_fields_array": "",
            "max_results": 100,
            "deleted": 0,
        }
        fetch_data = {
            "method": "get_entry_list",
            "input_type": "JSON",
            "response_type": "JSON",
            "rest_data": json.dumps(leads_data),
        }
        response = requests.post(url, data=fetch_data)

        try:
            leads = response.json().get("entry_list")
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON response.")
            return []

        return leads
    else:
        # Authentication failed
        return []


# Function to fetch the current Bitcoin price
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    bitcoin_price = response.json()["bitcoin"]["usd"]

    return bitcoin_price


# Function to store leads and Bitcoin price in the database
def store_data(leads, bitcoin_price):
    cursor = db.cursor()

    # Store leads in the database
    for lead in leads:
        phone = lead['name_value_list']['phone_work']['value']
        first_name = lead['name_value_list']['first_name']['value']
        last_name = lead['name_value_list']['last_name']['value']

        query = "INSERT INTO leads (phone, first_name, last_name) VALUES (%s, %s, %s)"
        values = (phone, first_name, last_name)
        cursor.execute(query, values)

    # Store Bitcoin price in the database
    query = "INSERT INTO bitcoin_prices (price) VALUES (%s)"
    values = (bitcoin_price,)
    cursor.execute(query, values)

    db.commit()
    cursor.close()


# Define the router for API endpoints
router = APIRouter(
    prefix='/leads',
    tags=['Leads'],
)


# Endpoint to fetch and store data
@router.get("/fetch-and-store-data")
def fetch_and_store_data():
    leads = fetch_leads()
    # print(leads)
    bitcoin_price = fetch_bitcoin_price()
    # print(bitcoin_price)
    store_data(leads, bitcoin_price)

    return {"message": "Data fetched and stored successfully."}
