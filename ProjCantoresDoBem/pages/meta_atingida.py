import streamlit as st
import time
import gspread
import base64
from pathlib import Path
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(
    page_title="Meta Atingida",
    layout="wide"
)

st.set_page_config(page_title="Meta Atingida!", layout="centered")
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


categoria = st.session_state.get("categoria_meta", "Cota Desconhecida")

st.markdown(f"""
            <div style="text-align: center; font-size:120px; color: green; font-weight:;">
            🎉 META ATINGIDA! 🎉
            </div>
            """,unsafe_allow_html=True)
st.markdown(f"""
            <div style="text-align: center; font-size:24px; color: black;"> 
            Parabéns! A categoria {categoria.upper()} atingiu a meta! 🎯
            </div>
            """, unsafe_allow_html=True)

# --- Mostra os balões
with st.container():
    st.balloons()
    st.markdown("### Verificando status da meta...")

# --- Pausa um pouco (pra dar tempo de mostrar)
time.sleep(3)

# --- Conecta ao Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]
creds_dict = json.loads(st.secrets["creds_json"])
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

sheet = client.open("DashCantBem").sheet1
data = sheet.get_all_records()

# --- Normaliza colunas e linhas
colunas = [c.strip().lower() for c in data[0].keys()] if data else []
mostrar_col = "mostrar atingida"

# --- Atualiza "mostrar atingida" para "não" (se ainda estiver sim)
if mostrar_col in colunas:
    for i, linha in enumerate(data, start=2):
        if linha["categoria"].strip().lower() == categoria.strip().lower():
            idx_col = colunas.index(mostrar_col) + 1

            # Atualiza para "não" se ainda estiver "sim"
            if linha[mostrar_col].strip().lower() == "sim":
                sheet.update_cell(i, idx_col, "não")
                st.info("🔁 Atualizando status...")
                time.sleep(60) # Espera um minuto para garantir a atualização)

            # Releitura pra garantir consistência
            atual = sheet.cell(i, idx_col).value.strip().lower()

            # Se já estiver "não", volta automaticamente
            if atual == "não":
                st.session_state["categoria_meta"] = None
                st.switch_page("Cotas.py")
            break

