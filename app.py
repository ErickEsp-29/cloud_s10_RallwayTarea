import os
import streamlit as st
import psycopg2
import pandas as pd

# ==========================================
# CONEXIÓN A LA BASE DE DATOS DE RAILWAY
# ==========================================
# Railway inyecta automáticamente la variable DATABASE_URL de forma segura
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    # Nos conectamos usando la URL directa, sin exponer credenciales
    return psycopg2.connect(DB_URL)

# ==========================================
# CREACIÓN DE LA TABLA INICIAL
# ==========================================
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registro_reciclaje (
            id SERIAL PRIMARY KEY,
            material VARCHAR(50),
            cantidad_kg NUMERIC(5,2)
        )
    """)
    conn.commit()
    conn.close()
except Exception as e:
    st.error(f"Error inicializando la base de datos: {e}")

# ==========================================
# INTERFAZ (UI) - MVP TALENTLOOP
# ==========================================
st.set_page_config(page_title="TalentLoop MVP", page_icon="♻️")
st.title("♻️ TalentLoop: Registro de Reciclaje")

with st.form("registro_form"):
    material = st.selectbox("Tipo de Material", ["Plástico", "Cartón", "Vidrio", "Metal"])
    cantidad = st.number_input("Cantidad (Kg)", min_value=0.1, step=0.1)
    
    submit = st.form_submit_button("Registrar Reciclaje")
    
    if submit:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO registro_reciclaje (material, cantidad_kg) VALUES (%s, %s)",
                (material, cantidad)
            )
            conn.commit()
            conn.close()
            st.success(f"¡Excelente! Se han registrado {cantidad} Kg de {material}.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")

st.divider()

st.header("📋 Historial de Reciclaje")

try:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM registro_reciclaje ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay registros en la base de datos.")
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")