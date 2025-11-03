import streamlit as st
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Meta Atingida!", layout="centered")

categoria = st.session_state.get("categoria_meta", "Cota Desconhecida")

st.title("🎉 META ATINGIDA! 🎉")
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
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "coral-sanctuary-476617-m6-70561c48c9f5.json", scope
)
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

