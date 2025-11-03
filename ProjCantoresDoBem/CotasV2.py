import streamlit as st
import pandas as pd
import locale
from datetime import datetime
from pathlib import Path
import base64
from calendar import monthrange
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 
import hashlib

st.set_page_config(page_title="Dashboard de Cotas Vendidas", layout="wide")

# --- Função para carregar dados do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive",
         "https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file"]
creds = ServiceAccountCredentials.from_json_keyfile_name("coral-sanctuary-476617-m6-70561c48c9f5.json", scope)
client = gspread.authorize(creds)

sheet = client.open("DashCantBem").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

df.columns = df.columns.str.strip().str.lower()

for col in ["cotas totais", "valor unitario", "cotas vendidas", "meta"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

cores_categorias = {
    "pintura" : "#c0dca1",
    "mobiliário" : "#a2c8d3",
    "alimentação" : "#e3ac9a",
    "kit higiene" : "#ccb0db",
    "material pedagógico" : "#ede592",
}


# --- Título principal
#st.markdown("<h1 style='text-align: center; color: #white;'> Cotas Vendidas</h1>", unsafe_allow_html=True)
#st.markdown("---")

# --- Layout com 5 colunas
cols = st.columns(5)

for i, row in df.iterrows():
    categoria = row.get("categoria", "N/A")
    cotas_vendidas = row.get("cotas vendidas", 0)
    cotas_totais = row.get("cotas totais", 0)
    valor_unitario = row.get("valor unitario",0)

    valor_total = cotas_vendidas * valor_unitario
    meta_total = cotas_totais * valor_unitario
    
    
    if meta_total > 0:
        percentual = (valor_total / meta_total) * 100
    else:
        percentual = 0

    percentual = max(0, min(percentual, 100))  # entre 0 e 100

    cor_barra = cores_categorias.get(categoria.lower(), "#2ECC40")
   

    # --- Escolher cor da barra de progresso
    if percentual < 50:
        cor = "#FF4136"
    elif percentual < 80:
        cor = "#FF851B"
    else:
        cor = "#2ECC40"

    with cols[i]:
        st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                text-align: center;
                margin-bottom: 15px;
            ">
            <h3 style="color:{cor_barra}; text-transform: capitalize">{categoria}</h3>
            <p style="font-size:18px;"><b>{cotas_vendidas} / {cotas_totais}</b> cotas vendidas</p>
            <p style="font-size:16px;"><b>Total: R$ {valor_total:,.2f}</b></p>

            <div style="
                background-color: #e0e0e0;
                border-radius: 20px;
                overflow: hidden;
                height: 25px;
                margin-top: 10px;
            ">
                <div style="
                    width: {percentual}%;
                    height: 100%;
                    background-color: {cor_barra};
                    border-radius: 10px;
                "></div>
            </div>

            <p style="margin-top: 8px; color: {cor_barra}; font-weight: bold;">
                {percentual:.1f}% da meta atingida
            </p>

        </div>
        """, unsafe_allow_html=True)

        #st.progress(int(percentual))
        #st.markdown(f"<p style='text-align:center; color:green; font-weight:bold;'>{percentual:.1f}% da meta atingida</p>", unsafe_allow_html=True)
#st.markdown("---")