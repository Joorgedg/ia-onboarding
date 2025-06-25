import streamlit as st
import json
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data"
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "")

# Leer todos los JSONs
def load_passports():
    context = ""
    nombres = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as file:
                fields = json.load(file)
                nombre = fields.get("nombre", "").strip()

                if nombre:
                    nombre_display = nombre.upper()
                    nombres.append(nombre_display)
                else:
                    nombre_display = "(Pasaporte sin nombre — revisar OCR)"
                    nombres.append(nombre_display)

                numero = fields.get("numero_pasaporte", "desconocido")
                nacionalidad = fields.get("nacionalidad", "desconocida")
                nacimiento = fields.get("fecha_nacimiento", "desconocida")
                emision = fields.get("fecha_emision", "desconocida")
                expiracion = fields.get("fecha_expiracion", "desconocida")

                context += f"""
Pasaporte de {nombre_display}:
- Número: {numero}
- Nacionalidad: {nacionalidad}
- Fecha de nacimiento: {nacimiento}
- Fecha de emisión: {emision}
- Fecha de expiración: {expiracion}
                
"""
    return context, nombres

# Inicializar el modelo
llm = ChatOpenAI(model="gpt-4-turbo")

# Streamlit UI
st.title("IA Onboarding - Multi-Pasaportes")

# LOGIN SIMPLE — Contraseña
st.sidebar.header("Acceso")

password_input = st.sidebar.text_input("Introduce la contraseña:", type="password")

if password_input != ACCESS_PASSWORD or password_input == "":
    st.warning("Introduce la contraseña correcta para acceder al chat.")
    st.stop()

# Cargar todos los pasaportes
passport_context, nombres_pasaportes = load_passports()

# Mostrar en sidebar
with st.sidebar:
    st.header("Pasaportes procesados:")
    st.write("\n".join(nombres_pasaportes))
    st.text_area("Contexto", passport_context, height=400)

# Entrada del usuario
query = st.text_input("Haz tu pregunta sobre los pasaportes:")

if st.button("Enviar"):
    # Crear el prompt con contexto
    full_prompt = f"""
Estos son los datos de los pasaportes procesados:

{passport_context}

Responde a la siguiente pregunta de forma precisa:
{query}
    """

    # Invocar el modelo
    response = llm.invoke(full_prompt)

    # Mostrar respuesta
    st.write(response.content)
