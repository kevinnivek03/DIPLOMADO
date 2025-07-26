import streamlit as st
import pandas as pd
import requests

# API Socrata de Infraestructura MEN
INFRAESTRUCTURA_URL = "https://www.datos.gov.co/resource/3ncw-3qwq.json"

def load_infraestructura_from_api(limit: int = 50000) -> pd.DataFrame:
    """
    Carga datos de infraestructura educativa desde la API Socrata del MEN.

    Args:
        limit (int): Límite de registros a consultar.

    Returns:
        pd.DataFrame: Datos en DataFrame o vacío si hay error.
    """
    url = f"{INFRAESTRUCTURA_URL}?$limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")
    return pd.DataFrame()

def show_infraestructura_tab():
    st.header("🏫 Carga de Datos de Infraestructura Educativa")

    st.markdown("""
    Este conjunto de datos proviene de [datos.gov.co](https://www.datos.gov.co/Educaci-n/MEN_INDICADORES_INFRAESTRUCTURA/3ncw-3qwq).
    
    Presiona el botón para cargar directamente los datos de infraestructura educativa.
    """)

    if st.button("📡 Cargar Infraestructura"):
        with st.spinner("Cargando datos desde la API..."):
            df_infra = load_infraestructura_from_api()

        if not df_infra.empty:
            st.session_state['df_infraestructura'] = df_infra
            st.success(f"¡Datos cargados exitosamente! ({len(df_infra)} filas)")
            st.dataframe(df_infra.head(20))
        else:
            st.warning("No se pudieron cargar los datos.")
    else:
        st.info("Presiona el botón para iniciar la carga.")
