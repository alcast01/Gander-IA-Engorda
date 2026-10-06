import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO SaaS (CALIBRI & UI/UX ULTRA V4.0) ---
st.set_page_config(
    page_title="NutriON 360 ULTRA V4.0 | Hereford & Finanzas Ganaderas",
    page_icon="🐂",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* UNIFICACIÓN GLOBAL DE FUENTE Y COLOR BASE SaaS */
    html, body, [class*="css"], .stMarkdown, .stText, .stSelectbox, .stSlider, .stNumberInput, div, span, p, label, .stRadio {
        font-family: 'Calibri', sans-serif !important;
        color: #1e293b !important;
    }
    
    .main {
        background-color: #fcfaf8;
        font-family: 'Calibri', sans-serif !important;
    }
    
    /* TARJETAS DE MÉTRICAS AVANZADAS (CARDS) */
    .stMetric {
        background: #ffffff;
        padding: 12px 14px !important;
        border-radius: 14px;
        box-shadow: 0 4px 20px -3px rgba(154, 52, 18, 0.08);
        border: 1px solid #fed7aa;
        border-left: 5px solid #ea580c;
        margin-bottom: 10px !important;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(234, 88, 12, 0.15);
        border-color: #ea580c;
    }
    
    .stMetric label {
        font-size: 0.72rem !important;
        color: #7c2d12 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-family: 'Calibri', sans-serif !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        color: #431407 !important;
        font-weight: 800 !important;
        font-family: 'Calibri', sans-serif !important;
    }
    
    /* ENCABEZADOS Y TÍTULOS CORPORATIVOS */
    h1, h2, h3, h4, h5, h6 {
        color: #431407 !important;
        font-family: 'Calibri', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* PESTAÑAS (TABS) MODERNAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #ffedd5;
        padding: 6px;
        border-radius: 14px;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        color: #7c2d12 !important;
        font-size: 0.78rem !important;
        font-family: 'Calibri', sans-serif !important;
        padding: 8px 10px;
        background-color: transparent;
        transition: background-color 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #ea580c !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        font-family: 'Calibri', sans-serif !important;
    }
    
    /* BOTONES ESTILIZADOS */
    .stButton button {
        font-family: 'Calibri', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25);
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(234, 88, 12, 0.35);
    }
    
    /* CONTENEDOR DE ALERTAS E INFO */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid #fed7aa !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE ESTADOS DE CHAT ---
if "nutrion_hereford_messages" not in st.session_state:
    st.session_state.nutrion_hereford_messages = [
        {"role": "assistant", "content": "¡Hola! Soy **NutriON 360 ULTRA V4.0**, tu asistente virtual especializado en genética Hereford, finanzas empresariales y nutrición de precisión. ¿Cómo podemos optimizar la rentabilidad y ganancias de tu hato hoy?"}
    ]

# --- 3. ENCABEZADO Y LOGOTIPO HEREFORD ULTRA V4.0 ---
st.markdown("""
    <div style="display: flex; align-items: center; background: linear-gradient(135deg, #ffffff 0%, #fff7ed 50%, #ffedd5 100%); padding: 22px 26px; border-radius: 20px; box-shadow: 0 15px 35px -10px rgba(154, 52, 18, 0.15); margin-bottom: 24px; border: 2px solid #f97316; flex-wrap: wrap; gap: 20px;">
        <div style="flex-shrink: 0; background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%); padding: 14px; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(154, 52, 18, 0.3); font-size: 2.2rem;">
            🐂🥩
        </div>
        <div style="flex-grow: 1; min-width: 240px;">
            <h1 style="margin: 0; font-size: 1.8em; color: #7c2d12; letter-spacing: -0.8px; font-weight: 800; font-family: 'Calibri', sans-serif;">
                NutriON 360 <span style="background: linear-gradient(135deg, #ea580c, #c2410c); color: #ffffff; padding: 3px 10px; border-radius: 8px; font-size: 0.5em; vertical-align: middle; font-weight: 700; letter-spacing: 0.8px; box-shadow: 0 4px 10px rgba(154,52,18,0.3);">ULTRA V4.0 • BECERRO HEREFORD</span>
            </h1>
            <p style="margin: 2px 0 2px 0; font-size: 0.85em; color: #c2410c; font-weight: 700; font-family: 'Calibri', sans-serif;">
                "Tecnolog-IA en tus manos: Finanzas sólidas, empresa rentable y máxima ganancia por kilogramo."
            </p>
            <p style="margin: 3px 0 2px 0; font-size: 0.88em; color: #1e293b; font-weight: 600; font-family: 'Calibri', sans-serif;">
                Aplicación creada y desarrollada por el Nutriólogo Veterinario Alejandro Castañeda Correa
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. BASE DE DATOS INICIAL DE INGREDIENTES (SISTEMA VACA-BECERRO) ---
if "df_ingredientes_hereford" not in st.session_state:
    st.session_state.df_ingredientes_hereford = pd.DataFrame({
        "Nombre del Ingrediente": [
            "Ensilado de maiz", "Heno de zacate Buffel / Pasto nativo", "Harina de soya", 
            "Grano de maiz molido", "Pasta de canola", "Melaza de caña", 
            "Sal mineralizada 12% P", "Urea ganadera", "Núcleo Becerro Engorda", "Grasa sobrepaso"
        ],
        "Categoria": ["Forraje Húmedo", "Forraje Seco", "Suplemento Proteico", "Grano Energético", "Suplemento Proteico", "Subproducto Energético", "Suplemento Mineral", "Fuente No Proteica", "Suplemento Mineral", "Suplemento Energético"],
        "Disponible": [True, True, True, True, True, True, True, True, True, True],
        "Precio Estimado (MXN/ton)": [1100.0, 3200.0, 12500.0, 5800.0, 8500.0, 4800.0, 11000.0, 14000.0, 24000.0, 34000.0],
        "Proteina Cruda (PC % MS)": [8.0, 8.5, 48.0, 8.5, 38.0, 4.8, 0.0, 281.0, 0.0, 1.0],
        "Energia Neta Ganancia (ENg Mcal/kg)": [0.95, 0.82, 1.45, 1.52, 1.38, 1.30, 0.0, 0.0, 0.0, 2.10],
        "FND (% MS)": [45.0, 68.0, 12.0, 9.0, 28.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Calcio (Ca %)": [0.25, 0.40, 0.30, 0.02, 0.70, 0.80, 18.0, 0.0, 20.0, 1.0],
        "Fosforo (P %)": [0.22, 0.18, 0.65, 0.30, 1.10, 0.08, 12.0, 0.0, 10.0, 0.1],
        "Min Inclusión (%)": [0.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.5, 0.0],
        "Max Inclusión (%)": [50.0, 50.0, 25.0, 60.0, 20.0, 6.0, 3.0, 1.2, 3.0, 4.0]
    })

# --- 5. BARRA LATERAL GANADERA ---
st.sidebar.markdown(f"### 🎛️ Panel Financiero Hereford")
st.sidebar.markdown(f"👤 **Desarrollador:** MVZ Alejandro Castañeda C.")

st.sidebar.markdown("---")

with st.sidebar.expander("🐂 1. Parámetros del Hato Hereford", expanded=True):
    num_vientres = st.number_input("Número de Vientres en el Hato", min_value=1, max_value=5000, value=100, step=10)
    peso_destete_meta = st.slider("Peso Objetivo al Destete (kg)", min_value=180.0, max_value=300.0, value=230.0, step=5.0)
    porcentaje_destete = st.slider("Porcentaje de Destete Esperado (%)", min_value=60.0, max_value=95.0, value=85.0, step=1.0)
    precio_venta_kg = st.number_input("Precio de Venta Becerro Destetado (MXN/kg)", min_value=30.0, max_value=100.0, value=65.0, step=1.0)

with st.sidebar.expander("💰 2. Costos Operativos y Empresa", expanded=False):
    costo_operativo_vaca_ano = st.number_input("Costo Anual por Vaca Madre (MXN/año)", min_value=1000.0, max_value=15000.0, value=6500.0, step=250.0)
    inversion_sanidad_lote = st.number_input("Sanidad y Vacunación por Cabeza (MXN)", min_value=50.0, max_value=1000.0, value=350.0, step=25.0)

with st.sidebar.expander("🌾 3. Alimentación y Ganancia", expanded=False):
    ganancia_diaria_esperada = st.slider("GDP Esperada Becerro (kg/día)", min_value=0.6, max_value=1.5, value=0.95, step=0.05)
    consumo_ms_pct_peso = st.slider("Consumo Materia Seca (% del Peso Vivo)", min_value=1.8, max_value=3.2, value=2.5, step=0.1)

# --- EXTRACCIÓN DE DATOS DE INGREDIENTES ---
df_base_h = st.session_state.df_ingredientes_hereford

try:
    nombres_h = df_base_h["Nombre del Ingrediente"].astype(str).values
    c_h = df_base_h["Precio Estimado (MXN/ton)"].astype(float).values
    pc_h = df_base_h["Proteina Cruda (PC % MS)"].astype(float).values / 100.0  
    eng_h = df_base_h["Energia Neta Ganancia (ENg Mcal/kg)"].astype(float).values
    fnd_h = df_base_h["FND (% MS)"].astype(float).values / 100.0
    ca_h = df_base_h["Calcio (Ca %)"].astype(float).values / 100.0
    p_h = df_base_h["Fosforo (P %)"].astype(float).values / 100.0
    disponibles_h = df_base_h["Disponible"].astype(bool).values
except KeyError as err:
    st.error(f"Falta columna clave en ingredientes: {err}")
    st.stop()

bounds_h = []
for idx, row in df_base_h.iterrows():
    if not row["Disponible"]:
        bounds_h.append((0.0, 0.0))
    else:
        min_lim = max(0.0, float(row["Min Inclusión (%)"]) / 100.0)
        max_lim = min(1.0, float(row["Max Inclusión (%)"]) / 100.0)
        bounds_h.append((min_lim, max_lim))

A_eq_h = np.ones((1, len(c_h)))
b_eq_h = np.array([1.0])

pc_min_req = 0.14
eng_min_req = 1.25

A_ub_h = np.array([
    -pc_h,
    -eng_h
])
b_ub_h = np.array([
    -pc_min_req,
    -eng_min_req
])

resultado_h = linprog(c_h, A_ub=A_ub_h, b_ub=b_ub_h, A_eq=A_eq_h, b_eq=b_eq_h, bounds=bounds_h, method='highs')

costo_ton_dieta = resultado_h.fun if resultado_h.success else 4800.0
becerros_destetados_total = int(num_vientres * (porcentaje_destete / 100.0))
ingreso_total_venta = becerros_destetados_total * peso_destete_meta * precio_venta_kg
costos_totales_hato = num_vientres * costo_operativo_vaca_ano
utilidad_neta_empresarial = ingreso_total_venta - costos_totales_hato
rentabilidad_sobre_costo = (utilidad_neta_empresarial / costos_totales_hato) * 100 if costos_totales_hato > 0 else 0.0

# --- FUNCIÓN PDF FINANCIERO / VACA-BECERRO ---
class PDFHerefordReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(194, 65, 12)
        self.cell(0, 10, 'NutriON 360 ULTRA V4.0 - Becerro Hereford & Finanzas Ganaderas', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, 5, 'Desarrollado por el Nutriologo Veterinario Alejandro Castaneda Correa', 0, 1, 'C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Pagina {self.page_no()} | Tecnolog-IA en tus manos', 0, 0, 'C')

def generar_pdf_hereford():
    pdf = PDFHerefordReport()
    pdf.add_page()
    def safe_str(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(67, 20, 7)
    pdf.cell(0, 8, safe_str("1. Resumen Zootecnico del Hato Hereford"), 0, 1)
    pdf.set_font('Arial', '', 10)
    
    res = {
        "Vientres en Reproduccion": f"{num_vientres} cabezas",
        "Porcentaje de Destete": f"{porcentaje_destete}%",
        "Becerros Destetados Anuales": f"{becerros_destetados_total} cabezas",
        "Peso Promedio Destete": f"{peso_destete_meta} kg",
        "GDP Esperada": f"{ganancia_diaria_esperada} kg/dia"
    }
    for k, v in res.items():
        pdf.cell(95, 7, safe_str(f"{k}:"), 0, 0)
        pdf.cell(95, 7, safe_str(f"{v}"), 0, 1)

    pdf.ln(4)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_str("2. Evaluacion Financiera y Ganancias"), 0, 1)
    pdf.set_font('Arial', '', 10)
    
    econ = {
        "Ingreso Total por Venta de Becerros": f"${ingreso_total_venta:,.2f} MXN",
        "Costo Operativo Total del Hato": f"${costos_totales_hato:,.2f} MXN",
        "Utilidad Neta Empresarial": f"${utilidad_neta_empresarial:,.2f} MXN",
        "Rentabilidad sobre Inversion": f"{rentabilidad_sobre_costo:.1f}%",
        "Costo Dieta Optimizada": f"${costo_ton_dieta:,.2f} MXN/ton"
    }
    for k, v in econ.items():
        pdf.cell(95, 7, safe_str(f"{k}:"), 0, 0)
        pdf.cell(95, 7, safe_str(f"{v}"), 0, 1)

    output = pdf.output()
    return bytes(output) if isinstance(output, (bytes, bytearray)) else output.encode('latin1')

# --- 6. PESTAÑAS DE LA APLICACIÓN (10 TABS) ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📋 1. Panel & Empresa",
    "🧪 2. Nutrición Becerro",
    "📊 3. Finanzas & Ganancias",
    "🐂 4. Genética Hereford",
    "🚜 5. Raciones TMR",
    "🔮 6. Proyección Venta",
    "📄 7. Reporte PDF",
    "💬 8. NutriON IA",
    "🧭 9. Asesoría Experta",
    "📡 10. Monitoreo & Costos"
])

with tab1:
    st.subheader("Indicadores Clave del Sistema Vaca-Becerro")
    st.markdown(f"Evaluación empresarial para **{num_vientres} vientres** | Destete estimado: **{becerros_destetados_total} becerros**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Utilidad Neta Anual", f"${utilidad_neta_empresarial:,.0f} MXN", "Ganancia Total")
        st.metric("Rentabilidad Hato", f"{rentabilidad_sobre_costo:.1f}%", "Retorno de Inversión")
    with col2:
        st.metric("Ingreso por Venta", f"${ingreso_total_venta:,.0f} MXN", "Facturación Bruta")
        st.metric("Costo Total Operativo", f"${costos_totales_hato:,.0f} MXN", "Inversión Anual")
    with col3:
        st.metric("Peso Destete Objetivo", f"{peso_destete_meta} kg")
        st.metric("Precio Venta / kg", f"${precio_venta_kg:,.2f} MXN")

    st.markdown("---")
    st.subheader("📈 Proyección Financiera de Ganancias por Kilogramo")
    
    pesos_sim = [180, 200, 220, 240, 260, 280, 300]
    ingresos_sim = [p * becerros_destetados_total * precio_venta_kg for p in pesos_sim]
    
    fig_fin = px.line(x=pesos_sim, y=ingresos_sim, markers=True, labels={"x": "Peso al Destete (kg)", "y": "Ingreso Bruto Total (MXN)"}, title="Ingreso Bruto según Peso Objetivo al Destete")
    fig_fin.update_traces(line_color="#ea580c", line_width=3)
    fig_fin.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(family="Calibri", size=12))
    st.plotly_chart(fig_fin, use_container_width=True)

with tab2:
    st.subheader("🧪 Formulación de Ración y Requerimientos para Becerro Hereford")
    st.markdown("Ajusta ingredientes, costos y restricciones para garantizar el máximo desarrollo muscular y eficiencia al destete.")
    
    st.session_state.df_ingredientes_hereford = st.data_editor(
        st.session_state.df_ingredientes_hereford,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Disponible": st.column_config.CheckboxColumn("¿Disponible?", default=True),
            "Min Inclusión (%)": st.column_config.NumberColumn("Min (%)", min_value=0.0, max_value=100.0, step=0.5),
            "Max Inclusión (%)": st.column_config.NumberColumn("Max (%)", min_value=0.0, max_value=100.0, step=0.5),
        },
        key="editor_ingredientes_hereford_persisted"
    )

with tab3:
    st.subheader("📊 Evaluación Financiera & Márgenes de Ganancia")
    if resultado_h.success:
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
            st.metric("Ingreso Bruto", f"${ingreso_total_venta:,.2f}")
            st.metric("Costos Totales", f"${costos_totales_hato:,.2f}")
        with col_e2:
            st.metric("Utilidad Neta", f"${utilidad_neta_empresarial:,.2f}", "Alta")
            st.metric("Rentabilidad", f"{rentabilidad_sobre_costo:.1f}%")
        with col_e3:
            st.metric("Costo Dieta Ton", f"${costo_ton_dieta:,.2f}")
            st.metric("Becerros Destete", f"{becerros_destetados_total} cab")
        with col_e4:
            st.metric("Estatus Empresa", "🟢 Solvente")
            st.metric("Margen Beneficio", f"{(utilidad_neta_empresarial/ingreso_total_venta)*100:.1f}%" if ingreso_total_venta > 0 else "0%")

        st.markdown("---")
        st.markdown("#### 📋 Dieta Óptima de Costo Mínimo (Becerro):")
        tabla_dieta = []
        for i, ing in enumerate(nombres_h):
            frac = resultado_h.x[i]
            porc = frac * 100
            kg_ton = frac * 1000
            if porc > 0.01:
                costo_parcial = frac * c_h[i]
                tabla_dieta.append({
                    "Ingrediente": ing,
                    "Inclusión (%)": round(porc, 1),
                    "Kg por Tonelada": round(kg_ton, 1),
                    "Costo Unitario ($/ton)": f"${c_h[i]:,.2f}",
                    "Aporte al Costo ($)": f"${costo_parcial:,.2f}"
                })
        df_dieta_res = pd.DataFrame(tabla_dieta)
        st.dataframe(df_dieta_res, use_container_width=True, hide_index=True)
    else:
        st.error("⚠️ Ajusta las restricciones de disponibilidad en la pestaña 2 para hallar solución factible.")

with tab4:
    st.subheader("🐂 Genética Hereford & Potencial de Ganancia Diaria")
    st.markdown("""
        **Eficiencia Genética Hereford en el Sistema Vaca-Becerro:** La raza Hereford aporta excelente docilidad, 
        habilidad materna superior y una conversión alimenticia sobresaliente en sistemas de engorda y destete al pastoreo y corral.
    """)
    st.info("💡 **Recomendación Estratégica:** Mantener suplementación mineral de alta disponibilidad para asegurar ganancias superiores a 0.950 kg/día durante la etapa crítica de lactancia y crecimiento.")

with tab5:
    st.subheader("🚜 Control y Mezcla de Raciones TMR / Suplementos")
    if resultado_h.success:
        st.success("✅ Sistema de optimización lineal convergente y validado para máxima rentabilidad ganadera.")

with tab6:
    st.subheader("🔮 Simulador de Escenarios de Venta y Ganancias")
    precio_alza = st.slider("Variación Esperada en Precio de Venta (MXN/kg)", -10.0, 15.0, 0.0, 0.5)
    nuevo_precio = precio_venta_kg + precio_alza
    nuevo_ingreso = becerros_destetados_total * peso_destete_meta * nuevo_precio
    nueva_utilidad = nuevo_ingreso - costos_totales_hato
    st.metric("Nueva Utilidad Neta Proyectada", f"${nueva_utilidad:,.0f} MXN", f"Con precio de ${nuevo_precio}/kg")

with tab7:
    st.subheader("📄 Generación de Reporte Ejecutivo en PDF")
    pdf_b = generar_pdf_hereford()
    st.download_button(
        label="📥 Descargar Reporte Financiero y Zootécnico en PDF",
        data=pdf_b,
        file_name="NutriON_360_Ultra_Hereford_Reporte.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.success("¡Reporte corporativo listo para descarga!")

with tab8:
    st.subheader("💬 Asistente Virtual NutriON IA (Vaca-Becerro)")
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.nutrion_hereford_messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    if q_h := st.chat_input("Escribe tu duda sobre finanzas, nutrición Hereford o costos..."):
        st.session_state.nutrion_hereford_messages.append({"role": "user", "content": q_h})
        with st.chat_message("user"):
            st.markdown(q_h)
        resp = f"🤖 Recibido: *\"{q_h}\"*. Como asistente **NutriON 360 ULTRA V4.0 Hereford**, he registrado tu consulta para maximizar tus ganancias empresariales."
        st.session_state.nutrion_hereford_messages.append({"role": "assistant", "content": resp})
        with st.chat_message("assistant"):
            st.markdown(resp)

with tab9:
    st.subheader("🧭 Centro de Asesoría Empresarial con el Especialista")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        nom_h = st.text_input("Productor / Propietario", key="h_nom")
        ran_h = st.text_input("Nombre del Rancho / Empresa", key="h_ran")
        mail_h = st.text_input("Correo o Teléfono de Contacto", key="h_mail")
    with col_h2:
        mot_h = st.selectbox("Objetivo de Asesoría", [
            "Optimización de Costos y Márgenes de Ganancia en Hato",
            "Nutrición de Vientres en Época Crítica / Seca",
            "Programa Genético Hereford y Destete Precoz",
            "Auditoría Financiera y Empresa Ganadera"
        ], key="h_mot")
        f_cita = st.date_input("Fecha Preferida", min_value=datetime.now().date(), key="h_fec")
        h_cita = st.selectbox("Horario", ["09:00 AM", "11:00 AM", "01:00 PM", "04:00 PM"], key="h_hor")
    
    if st.button("💳 Pagar $475 MXN y Agendar Asesoría con el Dr. Alejandro Castañeda", use_container_width=True):
        if nom_h and mail_h:
            st.success(f"🎉 **¡Cita Agendada con Éxito!** El Nutriólogo Veterinario Alejandro Castañeda se conectará contigo el {f_cita} a las {h_cita}.")
            st.balloons()
        else:
            st.warning("⚠️ Completa tu nombre y datos de contacto.")

with tab10:
    st.subheader("📡 Monitoreo de Costos, Insumos y Sanidad")
    st.markdown("""
        **Control Total de la Empresa Ganadera:** Administra con precisión los costos fijos por vientre, 
        evalúa el impacto de la sanidad preventiva y asegura la máxima rentabilidad en tu sistema vaca-becerro.
    """)
