import streamlit as st
import pandas as pd
import plotly.express as px

def show_comparacion_tab():
    st.header("🏫 Comparación: Infraestructura vs Cobertura Educativa")

    if 'df_fact' not in st.session_state or 'df_infraestructura' not in st.session_state:
        st.warning("Primero debes cargar tanto los datos educativos como los datos de infraestructura.")
        return

    df_fact = st.session_state['df_fact']
    dim_geo = st.session_state['dim_geo']
    df_infra = st.session_state['df_infraestructura'].copy()

    # =============== Preprocesamiento ===============
    df_geo = dim_geo[['id_geo', 'departamento']].drop_duplicates()

    # Obtener cobertura neta promedio por departamento
    df_cobertura = df_fact.merge(df_geo, on='id_geo')
    df_cobertura = df_cobertura.groupby('departamento')['cobertura_neta'].mean().reset_index()

    # Procesar datos de infraestructura
    df_infra['aulas_mejoradas'] = pd.to_numeric(df_infra.get('aulas_mejoradas', 0), errors='coerce').fillna(0)
    df_infra['nombre_depto'] = df_infra['nombre_depto'].str.strip().str.title()
    df_infra_agg = df_infra.groupby('nombre_depto')['aulas_mejoradas'].sum().reset_index()

    # Unión por nombre de departamento
    df_comparado = df_cobertura.merge(df_infra_agg, left_on='departamento', right_on='nombre_depto', how='inner')

    # =================== GRÁFICO ===================
    st.subheader("📊 Relación entre Aulas Mejoradas y Cobertura Neta Promedio")

    fig = px.scatter(
        df_comparado,
        x='aulas_mejoradas',
        y='cobertura_neta',
        text='departamento',
        size='aulas_mejoradas',
        color='cobertura_neta',
        labels={
            'aulas_mejoradas': 'Total Aulas Mejoradas',
            'cobertura_neta': 'Cobertura Neta Promedio (%)'
        },
        title='Comparación de Aulas Mejoradas vs Cobertura Neta Promedio por Departamento'
    )

    fig.update_traces(textposition='top center')
    fig.update_layout(height=600)

    st.plotly_chart(fig, use_container_width=True)
