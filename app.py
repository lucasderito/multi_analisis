import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from openai import OpenAI

# Configuración de la página
st.set_page_config(page_title="Análisis de sentimientos en texto", layout="wide")

#configuracion de openai

# Función para restablecer la variable de sesión
def reset_session():
    session_state.api_key = None #esta es un funcion que reseta la variable de session ( clave ) cuando se llama.

# Crear o recuperar la variable de sesión
session_state = st.session_state
if not hasattr(session_state, 'api_key'):
    reset_session()  # Restablecer la variable de sesión si no existe

# Título de la app
st.write("<h1 style='color: #66b3ff; font-size: 36px;'>Esta aplicación funciona con API Key de OpenAI</h1>",
         unsafe_allow_html=True)

# Mostrar el cuadro de entrada de la API key si la sesión no está establecida
if session_state.api_key is None:
    user_input = st.text_input("Ingresa tu API key de OpenAI:", type="password")
else:
    user_input = ""  # Cuadro de entrada en blanco si la sesión está establecida

# Botón de validación
if st.button("Validar API Key"):
    session_state.api_key = user_input  # Almacena la API key en la sesión

# Intentar establecer conexión con la API de OpenAI
try:
    if session_state.api_key:
        client = OpenAI(api_key=session_state.api_key)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": "Hello!"}]
        )

        st.success("API key válida. Puedes utilizar la aplicación.")

except Exception as e:
    st.error(f"Error al validar la API key: {e}")

def limpiar_texto(texto):
    # Elimina saltos de línea y espacios en blanco adicionales.
    texto_limpio = " ".join(texto.split())
    return texto_limpio


def analizar_sentimientos(texto, max_respuesta_length=200):
    texto_limpio = limpiar_texto(texto)
    prompt = (
        f"Por favor analiza el sentimiento predominante en el siguiente texto: '{texto_limpio}' "
        f"y da una explicación detallada como si fueses un profesional. "
        f"No más de {max_respuesta_length} tokens."
    )

    client = OpenAI(api_key=session_state.api_key)
    try:
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Menciona los sentimientos relacionados al texto ingresado."},
                {"role": "user", "content": prompt}
            ]
        )

        # Obtener el contenido de la respuesta
        respuesta_formateada = respuesta.choices[0].message.content.strip()
        # En este caso, puedes dividir el análisis detallado y el sentimiento, si aplica
        emociones = "Detección de emociones no implementada"
        return respuesta_formateada, emociones

    except Exception as e:
        st.error(f"Error al analizar el texto: {e}")
        return None, None



def analizar_sentimientos_json(respuesta_formateada, emociones):
    texto_limpio = limpiar_texto(respuesta_formateada)
    prompt = (
        f"Por favor analiza el sentimiento predominante en el siguiente texto: '{texto_limpio}'. "
        "Devuélveme un JSON que contenga las emociones específicas: gusto, amor, interesante, enfado, tristeza, "
        "felicidad, sorpresa, miedo, desprecio, divertido, orgullo, culpa, emocion, confusion, aburrimiento, "
        "tranquilidad, indiferencia, esperanza, inquietud. "
        "Detecta todas las emociones presentes y devuelve sus valores en un rango de hasta +10 por emocion, mostrando valores positivos solamente "
        "Ejemplo de formato: {'emociones': {'felicidad': 0.8, 'tristeza': 0.5}}."
    )

    client = OpenAI(api_key=session_state.api_key)

    try:
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Proporciona un análisis de sentimientos con emociones en formato JSON."},
                      {"role": "user", "content": prompt}]
        )

        respuesta_formateada = respuesta.choices[0].message.content.strip()

        # Intenta cargar la respuesta como JSON
        emociones = json.loads(respuesta_formateada)

        # corrobora de que la estructura es correcta
        if 'emociones' in emociones:
            return emociones['emociones']
        else:
            return {"Error": "Formato de respuesta inesperado"}

    except Exception as e:
        return f"Error al analizar el texto: {str(e)}"

# Agregar una línea horizontal
st.write('<hr>', unsafe_allow_html=True)
st.write("<h1 style='color: #66b3ff;font-size: 28px;'>Análisis Textual:</h1>", unsafe_allow_html=True)




# Barra lateral para seleccionar secciones
section = st.sidebar.selectbox(
    'Selecciona una sección:',
    ['Análisis textual', 'Análisis con valores']
)


#contenido basico de cada seccion

if section == 'Análisis textual':
    st.title("Análisis de sentimientos en texto")
    with st.container():
        try:
            texto_a_analizar = st.text_area("Ingrese el texto que quiere analizar:")
            if st.button("Analizar Texto"):
                # Agregar una línea horizontal
                st.write('<hr>', unsafe_allow_html=True)
                if texto_a_analizar:
                    st.subheader("Resultado del Análisis:")
                    resultado_analisis, emociones = analizar_sentimientos(texto_a_analizar)
                    # Mostrar la respuesta en negrita
                    st.markdown(f"**{resultado_analisis}**")
                    # Agregar una línea horizontal
                    st.write('<hr>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Acceso Denegado: {e}")

        st.divider()



    # En la sección 'Análisis con valores':
elif section == 'Análisis con valores':
    st.title("Análisis con valores de emociones")
    with st.container():
        try:
            texto_a_analizar = st.text_area("Ingrese el texto que quiere analizar:")
            if st.button("Analizar Texto"):
                # Agregar una línea horizontal
                st.write('<hr>', unsafe_allow_html=True)
                if texto_a_analizar:
                    # Obtener el análisis de sentimientos y las emociones
                    resultado_analisis, emociones = analizar_sentimientos(texto_a_analizar)

                    # Agregar una línea horizontal
                    st.write('<hr>', unsafe_allow_html=True)

                    # Mostrar el gráfico de barras con emociones
                    st.subheader("Emociones Detectadas:")

                    # Obtener las emociones en formato JSON
                    resultado_analisis_json = analizar_sentimientos_json(resultado_analisis, emociones)

                    # Mostrar gráfico si la respuesta es válida
                    if isinstance(resultado_analisis_json, dict) and 'Error' not in resultado_analisis_json:
                        # Convierte el diccionario de emociones a un DataFrame
                        emociones_df = pd.DataFrame.from_dict(resultado_analisis_json, orient='index',
                                                              columns=['Valor'])
                        emociones_df.reset_index(inplace=True)
                        emociones_df.columns = ['Emoción', 'Valor']  # Renombrar columnas para claridad

                        # Ordenar las emociones de mayor a menor valor
                        emociones_df = emociones_df.sort_values(by='Valor', ascending=False)

                        # Seleccionar las 4 emociones con mayor valor
                        top_emociones = emociones_df.head(4)

                        # Crear el gráfico de barras
                        plt.figure(figsize=(10, 6))
                        barras = plt.bar(emociones_df['Emoción'], emociones_df['Valor'], color='skyblue')

                        # Resaltar en negrita las emociones con mayor valor
                        for i, barra in enumerate(barras):
                            if emociones_df.iloc[i]['Emoción'] in top_emociones['Emoción'].values:
                                barra.set_color('orange')  # Cambiar el color de las barras más destacadas
                                plt.text(barra.get_x() + barra.get_width() / 2, barra.get_height(),
                                         f'{emociones_df.iloc[i]["Valor"]:.2f}', ha='center', va='bottom',
                                         fontweight='bold')

                        plt.xlabel('Emociones')
                        plt.ylabel('Valor')
                        plt.title('Gráfico de Emociones Detectadas')

                        # Rotar las etiquetas del eje X para evitar superposición
                        plt.xticks(rotation=45, ha='right')

                        # Mostrar el gráfico en Streamlit
                        st.pyplot(plt)

                    else:
                        st.error("Error al obtener las emociones para graficar.")

        except Exception as e:
            st.error(f"Acceso Denegado: {e}")




# Verificar si la API key está en la sesión
if session_state.api_key:
    st.write(f"Sesión establecida")
else:
    st.write("API key no presente en la sesión")

# Botón para cerrar la sesión
if st.button("Cerrar Sesión"):
    reset_session()