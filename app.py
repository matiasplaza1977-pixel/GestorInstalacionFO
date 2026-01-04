import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io  # Necesario para la exportación en memoria


# --- 1. FUNCIÓN DE FORMATO DE NÚMEROS ---
def formato_moneda(valor):
    return "{:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")


# --- 2. FUNCIÓN PARA EXPORTAR A EXCEL (Para mantener formato de tabla) ---
def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    # Exportamos solo las columnas visibles que interesan
    df_export = df[
        ["ID", "Nombre", "Fecha Inicio", "Metros Totales", "Metros Instalados", "Progreso %", "Estado", "Ganancia"]]
    df_export.to_excel(writer, index=False, sheet_name='Proyectos')
    # Formatear columnas en Excel automáticamente (opcional, pero ayuda)
    workbook = writer.book
    worksheet = writer.sheets['Proyectos']
    # Ajustar ancho de columnas
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:H', 18)

    writer.close()
    processed_data = output.getvalue()
    return processed_data


# --- 3. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Gestor de Proyectos FO",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 4. CSS "NOCHE ETERNA" + TÍTULOS UNIFICADOS VERDES ---
st.markdown("""
<style>
    /* Fondo General */
    .stApp { background-color: #0B1121; color: #E2E8F0; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #050911; border-right: 1px solid #1F2937; }

    /* Ocultar elementos nativos */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}

    /* --- ESTILO SCI-FI PARA NÚMEROS (Verde Neón) --- */
    div[data-testid="stMetricValue"] {
        color: #00FF41; text-shadow: 0 0 10px #00FF41; 
        font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748B; font-size: 14px; font-family: 'Segoe UI', sans-serif; text-transform: uppercase; letter-spacing: 1px;
    }
    div[data-testid="stMetricDelta"] {
        color: #4ADE80; font-family: 'Courier New', monospace;
    }

    /* --- TÍTULOS UNIFICADOS (H1, H2, H3) --- */
    h1, h2, h3 {
        color: #00FF41 !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        border-bottom: 2px solid #00FF41 !important;
        padding-bottom: 10px !important;
        margin-top: 20px !important;
        text-shadow: 0 0 10px #00FF41 !important;
        font-family: 'Courier New', monospace !important;
        background-color: transparent;
    }

    /* --- TABLAS OSCURAS --- */
    .stDataEditor td, .stDataEditor th {
        background-color: #111827 !important;
        color: #E2E8F0 !important;
        border-color: #1F2937 !important;
        font-family: 'Courier New', monospace; 
    }
    .stDataEditor th {
        color: #00FF41 !important; font-weight: bold; text-transform: uppercase;
    }
    .stDataEditor td:nth-child(4), .stDataEditor td:nth-child(5),
    .stDataEditor td:nth-child(6), .stDataEditor td:nth-child(7) {
        color: #00FF41 !important;
    }

    /* --- CONTENEDORES --- */
    .css-1d391kg { border: 1px solid #374151; background-color: #111827; border-radius: 8px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 5. INICIALIZACIÓN DE DATOS ---
if 'df_trabajos' not in st.session_state:
    data = {
        "ID": ["PROY-001", "PROY-002"],
        "Nombre": ["Instalación Centro A", "Reparación Nodo B"],
        "Fecha Inicio": [datetime(2023, 10, 25), datetime(2023, 10, 26)],
        "Metros Totales": [3000, 1200],
        "Metros Instalados": [3000, 600]
    }
    st.session_state.df_trabajos = pd.DataFrame(data)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("⚡ FO MANAGER")
    st.markdown("---")

    # CONFIGURACIÓN PRECIO
    st.subheader("💰 Configuración")
    precio_por_metro = st.number_input("Precio por Metro (FO):", value=750.0, min_value=0.0, step=1.0, format="%f")

    st.markdown("---")

    # FORMULARIO AGREGAR
    st.subheader("➕ Nuevo Trabajo")
    with st.form("form_agregar", clear_on_submit=True):
        nombre = st.text_input("Nombre del Proyecto")
        fecha_inicio = st.date_input("Fecha Inicio", datetime.now())
        metros_totales = st.number_input("Metros Totales", min_value=1, step=50)
        metros_actuales = st.number_input("Metros Instalados (Inicial)", min_value=0, step=50)

        submitted = st.form_submit_button("Agregar Trabajo")
        if submitted:
            if metros_actuales > metros_totales:
                st.error("Los instalados no pueden superar el total.")
            else:
                nuevo_id = f"PROY-{len(st.session_state.df_trabajos) + 1:03d}"
                nuevo_registro = pd.DataFrame([{
                    "ID": nuevo_id,
                    "Nombre": nombre,
                    "Fecha Inicio": pd.to_datetime(fecha_inicio),
                    "Metros Totales": metros_totales,
                    "Metros Instalados": metros_actuales
                }])
                st.session_state.df_trabajos = pd.concat([st.session_state.df_trabajos, nuevo_registro],
                                                         ignore_index=True)
                st.rerun()

    st.markdown("---")

    # ZONA DE BORRADO
    st.subheader("🗑️ Eliminar Registro")
    if not st.session_state.df_trabajos.empty:
        ids_list = st.session_state.df_trabajos['ID'].tolist()
        id_borrar = st.selectbox("Selecciona ID:", ids_list)
        if st.button("Eliminar"):
            st.session_state.df_trabajos = st.session_state.df_trabajos[st.session_state.df_trabajos['ID'] != id_borrar]
            st.rerun()

# --- 7. LÓGICA DE CÁLCULO ---
df = st.session_state.df_trabajos.copy()

if not df.empty:
    df['Ganancia'] = df['Metros Instalados'] * precio_por_metro
    df['Progreso %'] = (df['Metros Instalados'] / df['Metros Totales']) * 100
    df['Estado'] = df['Progreso %'].apply(lambda x: "Completado" if x >= 100 else "En Progreso")

    hoy = datetime.now().date()
    df['Solo Fecha'] = pd.to_datetime(df['Fecha Inicio']).dt.date

    ganancia_total = df['Ganancia'].sum()
    ganancia_hoy = df[df['Solo Fecha'] == hoy]['Ganancia'].sum()

    mes_actual = hoy.month
    año_actual = hoy.year
    ganancia_mes = df[(df['Fecha Inicio'].dt.month == mes_actual) & (df['Fecha Inicio'].dt.year == año_actual)][
        'Ganancia'].sum()
    estimacion_anual = ganancia_mes * 12
else:
    ganancia_total = 0
    ganancia_hoy = 0
    ganancia_mes = 0
    estimacion_anual = 0

# --- 8. DASHBOARD PRINCIPAL ---
st.markdown("<h1>DASHBOARD DE INSTALACIÓN FO</h1>", unsafe_allow_html=True)

# MÉTRICAS
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Instalado", f"{int(df['Metros Instalados'].sum())} m")
with c2:
    st.metric("Ganancia Total", formato_moneda(ganancia_total))
with c3:
    st.metric("Ganancia Mes", formato_moneda(ganancia_mes))
with c4:
    st.metric("Proyección Anual", formato_moneda(estimacion_anual), delta="(Est)")

st.markdown("<br>", unsafe_allow_html=True)

# EDITOR DE DATOS + BOTÓN DE EXPORTACIÓN
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown("### Editor de Proyectos")
    st.caption("Edita celdas directamente.")

with col_right:
    st.markdown("<br>", unsafe_allow_html=True)
    # Botón de Descarga Excel
    df_xlsx = to_excel(df)
    st.download_button(
        label='📥 Exportar Excel',
        data=df_xlsx,
        file_name=f'Proyectos_FO_{datetime.now().strftime("%Y%m%d")}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

columnas_mostrar = ["ID", "Nombre", "Fecha Inicio", "Metros Totales", "Metros Instalados", "Estado"]

column_config = {
    "ID": st.column_config.TextColumn("ID", disabled=True, width="small"),
    "Nombre": st.column_config.TextColumn("Proyecto", width="medium"),
    "Fecha Inicio": st.column_config.DateColumn("Inicio", width="small"),
    "Metros Totales": st.column_config.NumberColumn("Total (m)", width="small"),
    "Metros Instalados": st.column_config.NumberColumn("Hecho (m)", width="small", min_value=0),
    "Estado": st.column_config.SelectboxColumn("Estado", options=["En Progreso", "Completado", "Detenido"],
                                               width="small")
}

edited_df = st.data_editor(
    df,
    column_config=column_config,
    use_container_width=True,
    num_rows="dynamic",
    key="editor",
    hide_index=True
)

st.session_state.df_trabajos = edited_df

# --- 9. GRÁFICOS ---
col_g1, col_g2 = st.columns([1, 1])

if not df.empty:
    with col_g1:
        st.markdown("### Avance (%)")
        fig_bar = px.bar(
            df, x='Progreso %', y='Nombre', orientation='h',
            color='Estado',
            color_discrete_map={'Completado': '#00FF41', 'En Progreso': '#00CCFF', 'Detenido': '#FF0033'},
            text='Progreso %',
            template="plotly_dark"
        )
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        st.markdown("### Distribución Ganancias")
        fig_pie = px.pie(
            df, values='Ganancia', names='Nombre', hole=0.4,
            template="plotly_dark"
        )
        fig_pie.update_traces(marker=dict(colors=['#00FF41', '#00CCFF', '#FFFF00', '#FF0033']))
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)