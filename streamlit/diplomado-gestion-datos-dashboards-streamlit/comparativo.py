import streamlit as st
import pandas as pd
import plotly.express as px

def show_comparativo_tab():
    st.header("📉 Comparativo de Indicadores Educativos")

    # Cargar datos principales
    if 'df_fact' not in st.session_state or 'dim_geo' not in st.session_state:
        st.warning("Primero debes construir la tabla de hechos en la pestaña 'Transformación y Métricas'.")
        return

    df = st.session_state['df_fact'].merge(st.session_state['dim_geo'], on='id_geo')

    st.subheader("🔄 Cargar Datos Externos")

    # Cargar archivo externo (por ejemplo proyecciones poblacionales)
    archivo_externo = st.file_uploader("Carga un archivo CSV externo", type="csv")
    if archivo_externo is not None:
        df_ext = pd.read_csv(archivo_externo)
        st.success(f"Archivo cargado: {archivo_externo.name}")
        st.write("Vista previa de los datos externos:")
        st.dataframe(df_ext.head())

        # Opcional: intentar unir con df por departamento
        if 'departamento' in df_ext.columns:
            df_ext['departamento'] = df_ext['departamento'].str.strip().str.title()
            df_merge = df.merge(df_ext, on='departamento', how='inner')
            st.success("✅ Se integró exitosamente con los datos principales.")

            # Mostrar tabla cruzada
            st.dataframe(df_merge.head(20))

            # Gráfico comparativo si hay alguna columna numérica
            columnas_numericas = df_ext.select_dtypes(include='number').columns.tolist()
            if columnas_numericas:
                col_eje_x = st.selectbox("Columna del archivo externo para eje X", columnas_numericas)
                fig = px.scatter(
                    df_merge,
                    x=col_eje_x,
                    y='tasa_matriculaci_n_5_16',
                    hover_name='departamento',
                    title=f"Relación entre {col_eje_x} y Tasa de Matrícula"
                )
                st.plotly_chart(fig, use_container_width=True)

## grafico 
st.subheader("🏫 Comparación: Aulas Mejoradas vs Cobertura Neta Promedio")

# Verifica si los datos externos están cargados
if 'df_externo' in st.session_state and 'df_fact' in st.session_state:
    df_ext = st.session_state['df_externo']
    df_fact = st.session_state['df_fact']
    dim_geo = st.session_state['dim_geo']

    # Asegurarse de que existan columnas necesarias
    if 'AULAS_MEJORADAS' in df_ext.columns and 'departamento' in df_ext.columns:
        df_ext['AULAS_MEJORADAS'] = pd.to_numeric(df_ext['AULAS_MEJORADAS'], errors='coerce')
        df_ext = df_ext.dropna(subset=['AULAS_MEJORADAS', 'departamento'])

        # Agrupar por departamento
        aulas_por_depto = df_ext.groupby('departamento')['AULAS_MEJORADAS'].sum().reset_index()

        # Promedio de cobertura por departamento
        df = df_fact.merge(dim_geo, on='id_geo')
        cobertura = df.groupby('departamento')['cobertura_neta'].mean().reset_index()

        # Combinar
        comparativo = aulas_por_depto.merge(cobertura, on='departamento', how='inner')

        # Graficar
        fig = px.scatter(
            comparativo,
            x='AULAS_MEJORADAS',
            y='cobertura_neta',
            color='departamento',
            size='cobertura_neta',
            hover_name='departamento',
            labels={
                'AULAS_MEJORADAS': 'Total de Aulas Mejoradas',
                'cobertura_neta': 'Cobertura Neta Promedio (%)'
            },
            title='Relación entre Infraestructura y Cobertura Neta por Departamento'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ El archivo externo no contiene las columnas esperadas ('AULAS_MEJORADAS' y 'departamento').")
else:
    st.info("🔹 Debes cargar los datos externos y construir la tabla de hechos para ver esta visualización.")
