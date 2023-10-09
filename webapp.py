import datetime
import json
import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_NAME = os.getenv("DB_NAME")
connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}"
engine = create_engine(connection_string)

try:
    orders_maand = pd.read_sql_query(
        """
        select
            extract(month
        from
            date) as maand,
            round(avg("Precipitation"))
        from
            customer_analytics.orders_filtered
        group by
            maand
        order by
            maand
        """,
        con=engine,
    )
except BaseException:
    print("Database error, data wordt lokaal ingeladen.")
    orders_maand = pd.read_csv("webapp/orders_maand.csv")


# %% Layout Basic

st.header(":blue[Deliverable koerier planning] :woman-biking:")
st.write(
    "In deze interactieve webapp kunt u het aantal orders voor Deliverable voorspellen. U kunt een datum in de toekomst opgeven en de verwachte neerslag voor die dag. Aan de hand van die twee gegevens zal daaruit een voorspelling volgen voor het aantal orders voor die dag."
)

col1, col2 = st.columns(2)

# %% Datum en Neerslag
with col1:
    vandaag = datetime.date.today()
    datum = st.date_input(
        "**Datum :date:**", vandaag, min_value=vandaag, max_value=datetime.date(2023, 12, 31)
    )

with col2:
    gem_neerslag = int(orders_maand[orders_maand.maand == datum.month].iloc[0, 1])
    neerslag = st.number_input(
        "**De totale neerslag (mm)** :rain_cloud:",
        min_value=0,
        step=1,
        value=gem_neerslag,
        help="Standaard is hier de gemiddelde neerslag van de maand ingevuld.",
    )

    if (neerslag >= 50) & (neerslag < 1000):
        st.write("*Dat is erg veel neerslag* :cry:")

    elif neerslag >= 1000:
        st.write("*Zoek een*  :sailboat:")

# %% Model inladen voor voorspelling

# df = pd.DataFrame(columns=["year", "month", "day"])
# df.loc[0] = [datum.year, datum.month, datum.day]

# # LOKAAL INLADEN

# model_name = "lin_model.pkl"
# with open(
#     os.path.join(os.getenv(key="AZUREML_MODEL_DIR", default="./mlops/"), model_name), "rb"
# ) as f:
#     model = pkl.load(f)
# prediction = model.predict(df)[0][0]


# INLADEN MODEL VAN API
scoring_uri = "http://dbadb1ee-15c3-48be-968e-d083c304f9d7.westeurope.azurecontainer.io/score"
headers = {"Content-Type": "application/json"}
# resp = find out how to trigger your api with the requests package and valid data
body = {"date": datum.strftime("%Y-%m-%d"), "precipitation": neerslag}
body = json.dumps(body)

resp = requests.post(scoring_uri, body, headers=headers)

# st.text(resp.text)


# Voorspelling
st.write("---------------------------------------------------")
st.markdown("**Voorspelling aantal orders :knife_fork_plate:**", unsafe_allow_html=True)
# st.header(int(round(prediction, 0)))
st.header(resp.text)
