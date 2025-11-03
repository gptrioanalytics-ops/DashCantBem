import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import locale
import base64
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
import json

if "meta_exibida" not in st.session_state:
    st.session_state.meta_exibida = False
    st.session_state.categoria_meta = None


count = st_autorefresh(interval=20*1000, key="cotas_refresh")


base="light"
backgroundColor="#f9f9f9"


from pathlib import Path
img_path = Path(__file__).parent / "Aquarela.jpg"
def get_base64_of_image(image_file):
        with open(image_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

img_base64 = get_base64_of_image(img_path)



st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: right bottom;
            background-size: 400px ;
            height:90vh
            overflow: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True)

#locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
def format_brl(valor):
    return f" {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(page_title="Dashboard de Cotas Vendidas", layout="wide")

# --- Conexão com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive",
         "https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file"]
creds_dict = json.loads(st.secrets["creds_json"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

sheet = client.open("DashCantBem").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)


#meta_state = flag_meta_exibida()



df.columns = df.columns.str.strip().str.lower()
df["mostrar atingida"] = df["mostrar atingida"].str.strip().str.lower()

meta_atingida = df[df["mostrar atingida"] == "sim"]

if not meta_atingida.empty:
    categoria_meta = meta_atingida.iloc[0]["categoria"]

    # Guarda categoria na sessão
    if st.session_state.get("categoria_meta") != categoria_meta:
        st.session_state["categoria_meta"] = categoria_meta
        st.switch_page("pages/meta_atingida.py")



df.columns = df.columns.str.strip().str.lower()

for col in ["cotas totais", "valor unitario", "cotas vendidas", "meta"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --- Cores por categoria
cores_categorias = {
    "pintura" : "#c0dca1",
    "mobiliário" : "#a2c8d3",
    "alimentação" : "#e3ac9a",
    "kit higiene" : "#ccb0db",
    "mat. pedagógico" : "#c3f33d",
}


# --- Criando 5 colunas
col1, col2, col3, col4, col5 = st.columns(5)

# --- Função auxiliar para criar card
def criar_card(col, idx):
    categoria = df.iloc[idx]["categoria"]
    cotas_vendidas = df.iloc[idx]["cotas vendidas"]
    cotas_totais = df.iloc[idx]["cotas totais"]
    valor_unitario = df.iloc[idx]["valor unitario"]

    valor_total = cotas_vendidas * valor_unitario
    meta_total = cotas_totais * valor_unitario
    percentual = (valor_total / meta_total * 100) if meta_total > 0 else 0
    percentual = max(0, min(percentual, 100))
    cor_barra = cores_categorias.get(categoria.lower(), "#c0dca1")
    #valor_formatado = locale.format_string('%.2f', valor_total, grouping=True)
    valor_formatado = format_brl(valor_total)


    col.markdown(f"""
        
        <div style="
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
            text-align: left;
            margin-bottom: 20px;
            height: 580px;  
            display: flex; 
            flex-direction: column; 
            justify-content: space-between;
        ">
        <h2 style="color:{cor_barra}; font-size: 40px; text-align: center; text-transform: capitalize">{categoria}</h2>
        <p style="font-size:30px; text-align: center"><b>{cotas_vendidas} / {cotas_totais}</b></p>
        <p style="font-size:30px; text-align: center">Cotas Vendidas</p>
        <p style="font-size:40px; text-align: center"> Total: </p>
        <p style="font-size:30px; text-align:center"><b> R$ {valor_formatado}</b></p>

        <div style="
            background: #e0e0e0;
            border-radius: 20px;
            overflow: hidden;
            height: 35px;
            margin-top: 10px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        ">
            <div style="
                width: {percentual}%;
                height: 100%;
                text-align: center;
                background: linear-gradient(120deg, {cor_barra}, #FFFFFF);
                border-radius: 10px;
                transition: width 0.8s ease-in-out;
            "></div>
        </div>

        <h3 style="margin-top: 30px; color: {cor_barra}; font-weight: bold; text-align:center;">
            {percentual:.1f}% 
        </h3>
        </div>
    """, unsafe_allow_html=True)

# --- Criando cada card separadamente
criar_card(col1, 0)
criar_card(col2, 1)
criar_card(col3, 2)
criar_card(col4, 3)
criar_card(col5, 4)
