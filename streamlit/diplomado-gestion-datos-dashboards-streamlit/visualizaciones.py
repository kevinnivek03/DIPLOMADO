import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def show_visualization_tab():
    st.header("📈 Visualizaciones por Departamento")

    if 'df_fact' not in st.session_state:
        st.warning("Primero debes construir la tabla de hechos en la pestaña 'Transformación y Métricas'.")
        return

    df_fact = st.session_state['df_fact']
    dim_geo = st.session_state['dim_geo']
    dim_tiempo = st.session_state['dim_tiempo']

    df = df_fact.merge(dim_geo, on='id_geo').merge(dim_tiempo, on='id_tiempo')

    # ================================
    # PRIMER GRÁFICO
    # ================================
    st.subheader("📊 Serie de tiempo: Tasa de Matriculación vs Cobertura Neta")

    deptos = sorted(df['departamento'].unique())
    selected_depto_1 = st.selectbox("Selecciona un departamento (Gráfico 1)", deptos)

    df_1 = df[df['departamento'] == selected_depto_1]
    df_1 = df_1.groupby('a_o')[['tasa_matriculaci_n_5_16', 'cobertura_neta']].mean().reset_index()

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=df_1['a_o'],
        y=df_1['tasa_matriculaci_n_5_16'],
        name='Tasa de matriculación (5-16)',
        mode='lines+markers',
        yaxis='y1',
        line=dict(color='blue')
    ))

    fig1.add_trace(go.Scatter(
        x=df_1['a_o'],
        y=df_1['cobertura_neta'],
        name='Cobertura neta',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='orange')
    ))

    fig1.update_layout(
        title=f"Serie de tiempo - {selected_depto_1}",
        xaxis=dict(title='Año'),
        yaxis=dict(
            title=dict(text='Tasa de Matriculación (%)', font=dict(color='blue')),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=dict(text='Cobertura Neta (%)', font=dict(color='orange')),
            tickfont=dict(color='orange'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ================================
    # SEGUNDO GRÁFICO
    # ================================
    st.subheader("📊 Serie de tiempo: Cobertura Bruta vs Otra Métrica")

    selected_depto_2 = st.selectbox("Selecciona un departamento (Gráfico 2)", deptos, index=deptos.index(selected_depto_1))

    df_2 = df[df['departamento'] == selected_depto_2]
    df_2 = df_2.groupby('a_o')[['cobertura_bruta']].mean().reset_index()

    # Simulamos métrica adicional
    if 'repitencia_secundaria' in df.columns:
        df_2['otra_metrica'] = df[df['departamento'] == selected_depto_2].groupby('a_o')['repitencia_secundaria'].mean().values
        nombre_metrica = 'Repitencia secundaria'
    else:
        df_2['otra_metrica'] = df[df['departamento'] == selected_depto_2].groupby('a_o')['tasa_matriculaci_n_5_16'].mean().values
        nombre_metrica = 'Tasa de Matriculación (5-16)'

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=df_2['a_o'],
        y=df_2['cobertura_bruta'],
        name='Cobertura Bruta',
        mode='lines+markers',
        yaxis='y1',
        line=dict(color='green')
    ))

    fig2.add_trace(go.Scatter(
        x=df_2['a_o'],
        y=df_2['otra_metrica'],
        name=nombre_metrica,
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='purple')
    ))

    fig2.update_layout(
        title=f"Cobertura Bruta vs {nombre_metrica} - {selected_depto_2}",
        xaxis=dict(title='Año'),
        yaxis=dict(
            title=dict(text='Cobertura Bruta (%)', font=dict(color='green')),
            tickfont=dict(color='green')
        ),
        yaxis2=dict(
            title=dict(text=nombre_metrica, font=dict(color='purple')),
            tickfont=dict(color='purple'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig2, use_container_width=True)
        # ================================
    # TERCER GRÁFICO - BURBUJAS
    # ================================
    st.subheader("🟢 Comparativo de Departamentos: Matrícula vs Cobertura (Gráfico de Burbujas)")

    # Preparación del dataframe base
    df_bubble = df[['departamento', 'a_o', 'tasa_matriculaci_n_5_16', 'cobertura_neta', 'poblaci_n_5_16']].copy()
    df_bubble = df_bubble.dropna()

    # Selección del año
    years = sorted(df_bubble['a_o'].unique())
    selected_year = st.selectbox("Selecciona un año (Gráfico 3)", years, index=len(years)-1)

    # Filtrar y agregar datos por departamento
    df_filtered = df_bubble[df_bubble['a_o'] == selected_year]
    df_grouped = df_filtered.groupby('departamento', as_index=False).agg({
        'tasa_matriculaci_n_5_16': 'mean',
        'cobertura_neta': 'mean',
        'poblaci_n_5_16': 'mean'
    })

    fig3 = px.scatter(
        df_grouped,
        x='cobertura_neta',
        y='tasa_matriculaci_n_5_16',
        size='poblaci_n_5_16',
        color='departamento',
        hover_name='departamento',
        size_max=60,
        labels={
            'cobertura_neta': 'Cobertura Neta (%)',
            'tasa_matriculaci_n_5_16': 'Tasa de Matrícula (%)',
            'poblaci_n_5_16': 'Población 5-16 años'
        },
        title=f"Tasa de Matrícula vs Cobertura Neta - Año {selected_year}"
    )

    fig3.update_layout(
        height=600,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig3, use_container_width=True)

    # mapa de calor
    st.subheader("🔥 Mapa de Calor Interactivo: Cobertura Neta por Departamento y Año")

    df_heatmap = df.dropna(subset=['cobertura_neta'])

    df_pivot = df_heatmap.pivot_table(
        index='departamento',
        columns='a_o',
        values='cobertura_neta',
        aggfunc='mean'
    ).round(1).reset_index()

    # Convertimos a formato largo
    df_melted = df_pivot.melt(id_vars='departamento', var_name='a_o', value_name='cobertura_neta')

    fig_heatmap = px.density_heatmap(
        df_melted,
        x='a_o',
        y='departamento',
        z='cobertura_neta',
        color_continuous_scale='YlGnBu',
        text_auto=True,
        title="Mapa de Calor: Cobertura Neta Promedio por Departamento y Año"
    )

    fig_heatmap.update_layout(
        height=700,
        xaxis_title="Año",
        yaxis_title="Departamento",
        coloraxis_colorbar=dict(title="Cobertura (%)"),
        margin=dict(l=0, r=0, t=60, b=0)
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)


# boxplot
    # ================================
    # GRÁFICO 3: Boxplot de cobertura neta por departamento con filtro individual
    # ================================
    st.subheader("📊 Distribución de Cobertura Neta por Departamento")

    selected_depto_3 = st.selectbox("Selecciona un departamento (Gráfico 3)", deptos)

    df_3 = df[df['departamento'] == selected_depto_3]

    fig3 = px.box(df_3, x='departamento', y='cobertura_neta', points='all', color='departamento')
    fig3.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Cobertura Neta (%)",
        height=500
    )
    st.plotly_chart(fig3, use_container_width=True)

         # ================================
    # CUARTO GRÁFICO - GRÁFICO 3D INTERACTIVO CORREGIDO
    # ================================
    st.subheader("🧊 Gráfico 3D: Matrícula, Cobertura y Población (Animado)")

    df_3d = df[['departamento', 'a_o', 'tasa_matriculaci_n_5_16', 'cobertura_neta', 'poblaci_n_5_16']].dropna()

    # Filtrar población válida (mayores a 500)
    df_3d = df_3d[df_3d['poblaci_n_5_16'] > 500]

    df_3d_grouped = df_3d.groupby(['departamento', 'a_o'], as_index=False).agg({
        'tasa_matriculaci_n_5_16': 'mean',
        'cobertura_neta': 'mean',
        'poblaci_n_5_16': 'mean'
    })

    # Escala logarítmica para mejorar visibilidad si hay mucha disparidad
    fig3d = px.scatter_3d(
        df_3d_grouped,
        x='tasa_matriculaci_n_5_16',
        y='cobertura_neta',
        z='poblaci_n_5_16',
        color='departamento',
        animation_frame='a_o',
        size='poblaci_n_5_16',
        size_max=100,  # Tamaño máximo de burbuja
        log_z=True,   # Escala log para mejor visualización
        labels={
            'tasa_matriculaci_n_5_16': 'Tasa de Matrícula (%)',
            'cobertura_neta': 'Cobertura Neta (%)',
            'poblaci_n_5_16': 'Población 5-16 años',
            'a_o': 'Año'
        },
        title="📊 Gráfico 3D: Relación entre Matrícula, Cobertura y Población"
    )

    fig3d.update_layout(
        scene=dict(
            xaxis_title='Tasa de Matrícula (%)',
            yaxis_title='Cobertura Neta (%)',
            zaxis_title='Población 5-16 años'
        ),
        height=700,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig3d, use_container_width=True)
