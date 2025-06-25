from langchain_openai import ChatOpenAI


def extract_passport_fields(text):
   llm = ChatOpenAI(model="gpt-4-turbo")
    prompt = f"""
    Extrae del siguiente texto los campos:
    - numero_pasaporte
    - nombre
    - nacionalidad
    - fecha_nacimiento
    - fecha_emision
    - fecha_expiracion

    Devuelve en formato JSON.

    Texto:
    {text}
    """
    response = llm.invoke(prompt)
    return response
