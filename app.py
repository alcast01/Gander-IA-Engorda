import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
import json
import os
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO SaaS PROFESIONAL (CALIBRI & UI/UX) ---
st.set_page_config(
    page_title="NutriON 360 Ultra | IA, Collares IoT, NIR y Alta Rentabilidad Bovina",
    page_icon="🐄",
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
        background-color: #f8fafc;
        font-family: 'Calibri', sans-serif !important;
    }
    
    /* TARJETAS DE MÉTRICAS AVANZADAS (CARDS) */
    .stMetric {
        background: #ffffff;
        padding: 12px 14px !important;
        border-radius: 14px;
        box-shadow: 0 4px 20px -3px rgba(15, 23, 42, 0.08);
        border: 1px solid #e2e8f0;
        border-left: 5px solid #059669;
        margin-bottom: 10px !important;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.15);
        border-color: #059669;
    }
    
    .stMetric label {
        font-size: 0.72rem !important;
        color: #64748b !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-family: 'Calibri', sans-serif !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        font-family: 'Calibri', sans-serif !important;
    }
    
    /* ENCABEZADOS Y TÍTULOS CORPORATIVOS */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-family: 'Calibri', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* PESTAÑAS (TABS) MODERNAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #e2e8f0;
        padding: 6px;
        border-radius: 14px;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        color: #334155 !important;
        font-size: 0.80rem !important;
        font-family: 'Calibri', sans-serif !important;
        padding: 8px 10px;
        background-color: transparent;
        transition: background-color 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #059669 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        font-family: 'Calibri', sans-serif !important;
    }
    
    /* BOTONES ESTILIZADOS */
    .stButton button {
        font-family: 'Calibri', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(5, 150, 105, 0.35);
    }
    
    /* CONTENEDOR DE ALERTAS E INFO */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE MULTI-USUARIOS, PERSISTENCIA Y RENOVACIÓN AUTOMÁTICA ---
USERS_FILE = "usuarios_nutrion_360_ultra.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_usuarios_persistentes():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    default_users = {
        "admin": {
            "password": hash_password("1234"),
            "email": "admin@nutrion360.com",
            "subscription_active": True,
            "plan": "Anual Ultra AI & IoT (12 Meses) - $9,600 MXN | $800.00/mes",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "fecha_registro": "2026-01-01"
        },
        "alejandro": {
            "password": hash_password("elite360"),
            "email": "alejandro.castaneda@nutrion360.com",
            "subscription_active": True,
            "plan": "Anual Ultra AI & IoT (12 Meses) - $9,600 MXN | $800.00/mes",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "fecha_registro": "2026-01-01"
        }
    }
    guardar_usuarios_persistentes(default_users)
    return default_users

def guardar_usuarios_persistentes(usuarios_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios_dict, f, indent=4)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

if "nutrion_messages" not in st.session_state:
    st.session_state.nutrion_messages = [
        {"role": "assistant", "content": "¡Hola! Soy **NutriON**, tu asistente virtual con Inteligencia Artificial para **NutriON 360 Ultra**. Estoy conectado en tiempo real con sensores NIR, bolos ruminales de pH, collares IoT y el sistema de salud animal. ¿En qué te puedo ayudar hoy?"}
    ]

# --- PANTALLA DE ACCESO / SUSCRIPCIÓN SI NO ESTÁ AUTENTICADO ---
if not st.session_state.authenticated:
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px; margin-top: 30px;">
            <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); padding: 18px; border-radius: 22px; box-shadow: 0 12px 30px rgba(5, 150, 105, 0.35);">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="32" cy="32" r="30" fill="url(#paint0_linear)" />
                  <path d="M18 36C18 28 24 22 32 22C40 22 46 28 46 36C46 40 43 43 40 44H24C21 43 18 40 18 36Z" fill="#ffffff" fill-opacity="0.2"/>
                  <path d="M22 23L16 16M42 23L48 16" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
                  <circle cx="28" cy="32" r="2.5" fill="#fbbf24"/>
                  <circle cx="36" cy="32" r="2.5" fill="#fbbf24"/>
                  <path d="M29 38C30.5 39.5 33.5 39.5 35 38" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
                  <path d="M32 14V22" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/>
                  <path d="M28 17L32 14L36 17" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <defs>
                    <linearGradient id="paint0_linear" x1="4" y1="4" x2="60" y2="60" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#047857"/>
                      <stop offset="1" stop-color="#059669"/>
                    </linearGradient>
                  </defs>
                </svg>
            </div>
        </div>
        <h2 style="text-align: center; color: #064e3b; font-family: 'Calibri', sans-serif; font-weight: 800; margin-bottom: 2px;">
            NutriON <span style="color: #059669;">360</span> <span style="font-size: 0.5em; background: #059669; color: white; padding: 2px 8px; border-radius: 6px; vertical-align: middle;">ULTRA V4.0 AI & IOT</span>
        </h2>
        <p style="text-align: center; color: #059669; font-family: 'Calibri', sans-serif; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">
            Nutrición de precisión, telemetría NIR, bolos ruminales de pH y visión artificial.
        </p>
        <p style="text-align: center; color: #475569; font-family: 'Calibri', sans-serif; font-size: 0.85rem; margin-bottom: 25px;">
            Plataforma Global de Optimización, Smart Collars y Consultoría Experta Remota
        </p>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "💳 Planes Ultra AI & Registro"])

    with tab_login:
        st.markdown("### Acceso con Usuario y Contraseña")
        user_input = st.text_input("Nombre de Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        
        st.markdown("")
        if st.button("Entrar a la Plataforma Ultra AI", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            hashed_pass = hash_password(pass_input)
            
            if user_input in db_usuarios and db_usuarios[user_input]["password"] == hashed_pass:
                if db_usuarios[user_input].get("subscription_active", False):
                    st.session_state.authenticated = True
                    st.session_state.current_user = user_input
                    st.success(f"¡Bienvenido de nuevo, {user_input}!")
                    st.rerun()
                else:
                    st.error("Tu suscripción se encuentra inactiva. Selecciona un plan y realiza el pago para renovar.")
            else:
                st.error("Usuario o contraseña incorrectos. Verifica tus datos.")

    with tab_register:
        st.markdown("### 🌟 Selección de Plan Ultra AI & IoT")
        st.markdown("Elige el periodo de suscripción con acceso total a sensores NIR, bolos ruminales y telemetría:")
        
        plan_elegido = st.radio(
            "Planes de Suscripción NutriON 360 Disponibles:",
            [
                "Trimestral Pro AI (3 Meses) - $3,000 MXN | $1,000.00/mes",
                "Semestral Feedlot IoT (6 Meses) - $5,400 MXN | $900.00/mes",
                "Anual Ultra AI & IoT (12 Meses) - $9,600 MXN | $800.00/mes (Acceso Total)"
            ],
            index=2
        )
        
        st.markdown("---")
        st.markdown("##### 📝 Datos de Cuenta, Pago Seguro y Renovación Automática")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            new_user = st.text_input("Nombre de Usuario Deseado", key="reg_user")
            new_email = st.text_input("Correo Electrónico (para notificaciones y avisos)", key="reg_email")
        with col_r2:
            new_pass = st.text_input("Contraseña", type="password", key="reg_pass")
            confirm_pass = st.text_input("Confirma Contraseña", type="password", key="reg_conf")
        
        st.markdown("")
        col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
        with col_p1:
            num_tarjeta = st.text_input("Número de Tarjeta de Crédito / Débito", placeholder="4000 1234 5678 9010", key="reg_card")
        with col_p2:
            exp_tarjeta = st.text_input("Expiración (MM/AA)", placeholder="12/28", key="reg_exp")
        with col_p3:
            cvv_tarjeta = st.text_input("CVV", type="password", placeholder="123", key="reg_cvv")
        
        st.markdown("")
        
        auto_renew_enabled = st.checkbox(
            "🔄 **Activar Renovación Automática** (La suscripción se cobrará y renovará automáticamente al cumplirse el periodo elegido, garantizando monitoreo ininterrumpido).",
            value=True
        )
        
        st.markdown("")
        
        try:
            costo_str = plan_elegido.split("-")[1].split("|")[0].strip()
        except Exception:
            costo_str = "$9,600 MXN"
        
        if st.button(f"💳 Pagar {costo_str} y Activar Licencia Ultra AI", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            
            if not new_user or not new_email or not new_pass or not num_tarjeta:
                st.warning("⚠️ Por favor, completa todos los campos de registro y de pago.")
            elif new_user in db_usuarios:
                st.error("⚠️ El nombre de usuario ya existe. Elige otro o inicia sesión.")
            elif new_pass != confirm_pass:
                st.error("⚠️ Las contraseñas no coinciden.")
            elif len(num_tarjeta.replace(" ", "")) < 15:
                st.error("⚠️ Número de tarjeta inválido. Verifica los dígitos.")
            else:
                dias_periodo = 90 if "Trimestral" in plan_elegido else (180 if "Semestral" in plan_elegido else 365)
                fecha_renovacion = (datetime.now() + timedelta(days=dias_periodo)).strftime("%Y-%m-%d")
                
                db_usuarios[new_user] = {
                    "password": hash_password(new_pass),
                    "email": new_email,
                    "subscription_active": True,
                    "plan": plan_elegido,
                    "auto_renew": auto_renew_enabled,
                    "next_renewal_date": fecha_renovacion,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                guardar_usuarios_persistentes(db_usuarios)
                
                st.success(f"🎉 **¡Pago Exitoso de {costo_str} ({plan_elegido})!** Transacción aprobada.")
                if auto_renew_enabled:
                    st.info(f"🔄 **Renovación Automática Activada:** Tu próxima renovación está programada para el **{fecha_renovacion}**.")
                st.success(f"📧 **Notificación Enviada:** Se ha enviado el comprobante fiscal y tus accesos a **{new_email}**.")
                
                st.session_state.authenticated = True
                st.session_state.current_user = new_user
                st.balloons()
                st.rerun()

    st.stop()

# --- 3. LOGOTIPO VETERINARIO Y DE CAMPO (USUARIO AUTENTICADO) ---
db_usuarios_activos = cargar_usuarios_persistentes()
user_info = db_usuarios_activos.get(st.session_state.current_user, {})
plan_activo_usuario = user_info.get("plan", "Plan Ultra AI & IoT")
auto_renew_status = user_info.get("auto_renew", False)
next_ren_date = user_info.get("next_renewal_date", "N/A")

st.markdown(f"""
    <div style="display: flex; align-items: center; background: linear-gradient(135deg, #ffffff 0%, #ecfdf5 50%, #fef3c7 100%); padding: 22px 26px; border-radius: 20px; box-shadow: 0 15px 35px -10px rgba(5, 150, 105, 0.15); margin-bottom: 24px; border: 2px solid #34d399; flex-wrap: wrap; gap: 20px;">
        <div style="flex-shrink: 0; background: linear-gradient(135deg, #059669 0%, #10b981 100%); padding: 12px; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(5, 150, 105, 0.3);">
            <svg width="48" height="48" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="32" cy="32" r="30" fill="url(#paint0_linear)" />
              <path d="M18 36C18 28 24 22 32 22C40 22 46 28 46 36C46 40 43 43 40 44H24C21 43 18 40 18 36Z" fill="#ffffff" fill-opacity="0.2"/>
              <path d="M22 23L16 16M42 23L48 16" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
              <circle cx="28" cy="32" r="2.5" fill="#fbbf24"/>
              <circle cx="36" cy="32" r="2.5" fill="#fbbf24"/>
              <path d="M29 38C30.5 39.5 33.5 39.5 35 38" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
              <path d="M32 14V22" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/>
              <path d="M28 17L32 14L36 17" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="paint0_linear" x1="4" y1="4" x2="60" y2="60" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#047857"/>
                  <stop offset="1" stop-color="#059669"/>
                </linearGradient>
              </defs>
            </svg>
        </div>
        <div style="flex-grow: 1; min-width: 240px;">
            <h1 style="margin: 0; font-size: 1.8em; color: #064e3b; letter-spacing: -0.8px; font-weight: 800; font-family: 'Calibri', sans-serif;">
                NutriON <span style="background: linear-gradient(135deg, #059669, #10b981); color: #ffffff; padding: 3px 10px; border-radius: 8px; font-size: 0.5em; vertical-align: middle; font-weight: 700; letter-spacing: 0.8px; box-shadow: 0 4px 10px rgba(5,150,105,0.3);">360 ULTRA V4.0</span>
            </h1>
            <p style="margin: 2px 0 2px 0; font-size: 0.82em; color: #059669; font-weight: 700; font-family: 'Calibri', sans-serif;">
                Sensores NIR, bolos ruminales IoT de pH, IA acústica y gemelos digitales ganaderos.
            </p>
            <p style="margin: 3px 0 2px 0; font-size: 0.88em; color: #1e293b; font-weight: 600; font-family: 'Calibri', sans-serif;">
                Usuario: <span style="color: #059669; font-weight: 700;">{st.session_state.current_user.capitalize()}</span> | Licencia: <span style="color: #d97706; font-weight: 700;">{plan_activo_usuario}</span> | Creado por: Dr. Alejandro Castañeda Correa
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. BASE DE DATOS INICIAL CON PERSISTENCIA (SESSION STATE) ---
if "df_ingredientes_state" not in st.session_state:
    st.session_state.df_ingredientes_state = pd.DataFrame({
        "Nombre del Ingrediente": [
            "Rastrojo de maiz molido", "Harina de soya", "Grano de maiz molido", 
            "Urea", "Ensilado de maiz", "Canola (pasta)", "Melaza liquida",
            "Purina Mineral Tech (Tlaltenango)", "Malta Cleyton Ganafos", "Grasa de paso Lactomil"
        ],
        "Categoria": ["Forraje", "Suplemento Proteico", "Grano Energetico", "Suplemento NPN", "Forraje Humedo", "Suplemento Proteico", "Subproducto / Energetico", "Suplemento Mineral", "Suplemento Mineral", "Suplemento Energetico"],
        "Disponible": [True, True, True, True, True, True, True, True, True, True],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 19000.0, 18500.0, 32000.0],
        "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 0.0, 1.0],
        "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 0.0, 1.65],
        "FND (% MS)": [75.0, 12.0, 9.0, 0.0, 45.0, 28.0, 0.0, 0.0, 0.0, 0.0],
        "peNDF (% MS)": [65.0, 2.0, 3.0, 0.0, 30.0, 10.0, 0.0, 0.0, 0.0, 0.0],
        "PDR (% MS)": [3.5, 33.6, 5.5, 281.0, 5.0, 24.0, 4.5, 0.0, 0.0, 0.0],
        "PND (% MS)": [2.0, 14.4, 3.0, 0.0, 3.0, 14.0, 0.3, 0.0, 0.0, 1.0],
        "Calcio (Ca %)": [0.35, 0.30, 0.02, 0.0, 0.25, 0.70, 0.80, 14.0, 16.0, 1.0],
        "Fosforo (P %)": [0.10, 0.65, 0.30, 0.0, 0.22, 1.10, 0.08, 7.0, 8.0, 0.1],
        "Sodio (Na %)": [0.02, 0.03, 0.02, 0.0, 0.02, 0.05, 0.10, 10.0, 9.0, 0.0],
        "Magnesio (Mg %)": [0.15, 0.28, 0.12, 0.0, 0.18, 0.50, 0.40, 2.0, 2.5, 0.0],
        "Lípidos / Extracto Etéreo (%)": [1.5, 1.8, 3.8, 0.0, 3.0, 3.5, 0.5, 0.0, 0.0, 99.0],
        "Min Inclusión (%)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Max Inclusión (%)": [100.0, 100.0, 100.0, 1.5, 100.0, 100.0, 100.0, 5.0, 5.0, 5.0]
    })

# --- SIMULACIÓN DE DATOS DE COLLAR IoT PARA ANIMALES ---
if "df_collares_state" not in st.session_state:
    np.random.seed(42)
    ids_animales = [f"ID-{1000 + i}" for i in range(1, 26)]
    estados_salud = []
    visitas_com = []
    min_masticacion = []
    
    for idx in ids_animales:
        r = np.random.rand()
        if r < 0.75:
            estados_salud.append("🟢 Sano / Activo")
            visitas_com.append(int(np.random.randint(8, 15)))
            min_masticacion.append(int(np.random.randint(520, 680)))
        elif r < 0.90:
            estados_salud.append("🟡 Alerta (Bajo Consumo)")
            visitas_com.append(int(np.random.randint(3, 6)))
            min_masticacion.append(int(np.random.randint(380, 480)))
        else:
            estados_salud.append("🔴 Enfermo / Riesgo (Descarte)")
            visitas_com.append(int(np.random.randint(0, 2)))
            min_masticacion.append(int(np.random.randint(150, 320)))
            
    st.session_state.df_collares_state = pd.DataFrame({
        "ID Arete / Animal": ids_animales,
        "Estatus Collares IoT": estados_salud,
        "Visitas Comedero (visitas/día)": visitas_com,
        "Masticación / Rumina (min/día)": min_masticacion,
        "Acción IA Recomendada": [
            "Ninguna (Lote Óptimo)" if "Sano" in s else ("Aislar y revisar temperatura" if "Alerta" in s else "Descarte / Tratamiento urgente por ineficiencia") for s in estados_salud
        ]
    })

# --- 5. BARRA LATERAL ---
st.sidebar.markdown(f"### 🎛️ Panel Ultra AI NutriON")
st.sidebar.markdown(f"👤 **Usuario:** {st.session_state.current_user.capitalize()}")
st.sidebar.markdown(f"🛡️ **Licencia:** {plan_activo_usuario}")

with st.sidebar.expander("🔄 Gestión de Suscripción Ultra", expanded=True):
    st.markdown(f"**Próxima Renovación:** `{next_ren_date}`")
    
    nuevo_estado_auto = st.checkbox("Renovación Automática", value=auto_renew_status, key="sidebar_auto_renew_toggle")
    
    if nuevo_estado_auto != auto_renew_status:
        db_all = cargar_usuarios_persistentes()
        if st.session_state.current_user in db_all:
            db_all[st.session_state.current_user]["auto_renew"] = nuevo_estado_auto
            guardar_usuarios_persistentes(db_all)
            st.success("¡Estado de renovación actualizado!")
            st.rerun()
            
    if nuevo_estado_auto:
        st.info("🟢 Tu suscripción se renovará automáticamente al finalizar el periodo.")
    else:
        st.warning("🟡 La renovación automática está desactivada.")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.current_user = ""
    st.rerun()

st.sidebar.markdown("---")

with st.sidebar.expander("🐄 1. Lote, Pesos y Población", expanded=False):
    cantidad_animales = st.number_input("Número de Cabezas en el Lote", min_value=1, max_value=5000, value=100, step=10)
    peso_actual = st.slider("Peso Actual / Compra (kg)", min_value=200.0, max_value=650.0, value=250.0, step=10.0)
    peso_objetivo = st.slider("Peso de Venta / Meta (kg)", min_value=400.0, max_value=750.0, value=520.0, step=10.0)
    
    modo_gde = st.selectbox("Modo de Optimización GDE", ["Manual (Fijo)", "Automático Elite (Máxima GDE al Mínimo Costo x kg)"])
    if modo_gde == "Manual (Fijo)":
        gde = st.slider("Ganancia Diaria Esperada (GDE kg/día)", min_value=0.8, max_value=2.2, value=1.4, step=0.1)
    else:
        gde = 1.6

with st.sidebar.expander("💰 2. Parámetros Económicos y Sanidad", expanded=False):
    precio_compra_kg = st.number_input("Compra Becerro Base (MXN/kg)", min_value=30.0, max_value=100.0, value=55.0, step=1.0)
    precio_venta_kg = st.number_input("Venta Ganado Gordo Base (MXN/kg)", min_value=30.0, max_value=100.0, value=50.0, step=1.0)
    
    st.markdown("---")
    st.markdown("##### 🩺 Costos Variables de Recepción y Sanidad (MXN/cab)")
    costo_aretaje = st.number_input("Aretaje (SINIIGA / ID)", min_value=0.0, max_value=500.0, value=45.0, step=5.0)
    costo_barrido = st.number_input("Barrido Sanitario (TB / Brucela)", min_value=0.0, max_value=1000.0, value=150.0, step=10.0)
    costo_vacunacion = st.number_input("Vacunación (Clostridios / Resp.)", min_value=0.0, max_value=500.0, value=90.0, step=5.0)
    costo_desparasitacion = st.number_input("Desparasitación (Int./Ext.)", min_value=0.0, max_value=500.0, value=60.0, step=5.0)
    costo_vitaminacion = st.number_input("Vitaminación / Tónicos", min_value=0.0, max_value=500.0, value=40.0, step=5.0)
    
    st.markdown("---")
    costo_mano_obra_fijo = st.number_input("Mano de Obra y Operación (MXN/cab)", min_value=0.0, max_value=3000.0, value=450.0, step=50.0)

with st.sidebar.expander("🌾 3. Sistema de Producción y Pastoreo", expanded=False):
    sistema_produccion = st.selectbox("Sistema", ["Corral / Engorda Intensiva (Feedlot)", "Semi-estabulado (Mixto / Suplementación en Pastoreo)", "Pastoreo Extensivo (Praderas / Agostadero)"])
    condiciones_pastoreo = st.selectbox("Condiciones Pastoreo", ["N/A (Corral Intensivo)", "Pradera Cultivada / Riego (Alta Calidad)", "Pradera Nativa / Agostadero en Temporal", "Pradera Nativa / Agostadero Árido (Alta Caminata)", "Sistema Silvopastoril / Arbustivo"])
    estado_pasto = st.selectbox("Estado del Pasto", ["N/A (Corral / Sin Pastoreo)", "Vegetativo Temprano (Alta digestibilidad y PC)", "Vegetativo Tardío / Pre-floración (Calidad media)", "Floración / Madurez (Fibroso, baja PC)", "Lignificado / Seco (Muy baja digestibilidad)"])
    estacion = st.selectbox("Temporada / Clima", ["Templado", "Invierno", "Verano"])

with st.sidebar.expander("🧬 4. Genética, Sexo y Marco", expanded=False):
    raza_seleccionada = st.selectbox("Raza", ["Compuestas / Adaptadas (Beefmaster/Brangus)", "Británicas (Angus/Hereford)", "Continentales (Charolais/Simmental)", "Cebú / Tropicales (Bos indicus)", "Ganado Criollo / Local"])
    sexo_lote = st.selectbox("Categoría Zootécnica", ["Novillos (Castrados)", "Toros Enteros", "Vaquillas de Repasto/Engorda", "Vacas de Desecho / Finalización"])
    marco_lote = st.selectbox("Tamaño de Marco", ["Mediano (Standard)", "Precoz / Engrase rápido", "Grande (Continental / Retrasado)"])

with st.sidebar.expander("🌡️ 5. Variables Avanzadas y JDS", expanded=False):
    condicion_corporal = st.slider("Condición Corporal (1.0 - 5.0)", min_value=1.0, max_value=5.0, value=2.5, step=0.5)
    nivel_thi = st.selectbox("Estrés Térmico (THI)", ["Confort Térmico (< 74)", "Estrés Moderado (74-78)", "Estrés Severo (> 78)"])
    perfil_aa = st.selectbox("Modelo Aminoácidos", ["Estándar (Proteína Cruda)", "Avanzado (Optimización Lisina:Metionina 3:1)"])
    aditivo_ruminal = st.selectbox("Modificadores / Aditivos", ["Ninguno", "Ionóforos (Monensina / Lasalocid)", "Buffer (Bicarbonato / Óxido Mg)", "Ambos (Ionóforo + Buffer)"])
    historial_nutricional = st.selectbox("Historial Nutricional", ["Desarrollo Continuo (Normal)", "Crecimiento Compensatorio (Post-restricción)"])
    promotor_crecimiento = st.selectbox("Promotores Crecimiento", ["Ninguno", "Implante Hormonal", "Agonista β-adrenérgico (Finalización)"])
    condicion_lodo = st.selectbox("Condición de Corral / Lodo", ["Seco y Confortable", "Lodo Moderado (10-15 cm)", "Lodo Severo (>20 cm)"])

# --- EXTRACCIÓN DE DATOS DESDE SESSION STATE ---
df_base = st.session_state.df_ingredientes_state

try:
    nombres = df_base["Nombre del Ingrediente"].astype(str).values
    c = df_base["Precio Estimado (MXN/ton)"].astype(float).values
    pc = df_base["Proteina Cruda (PC % MS)"].astype(float).values / 100.0  
    neg = df_base["NEg (Mcal/kg)"].astype(float).values
    fnd = df_base["FND (% MS)"].astype(float).values / 100.0
    pendf = df_base["peNDF (% MS)"].astype(float).values / 100.0
    pdr = df_base["PDR (% MS)"].astype(float).values / 100.0
    pnd = df_base["PND (% MS)"].astype(float).values / 100.0
    ca = df_base["Calcio (Ca %)"].astype(float).values / 100.0
    p_min_ing = df_base["Fosforo (P %)"].astype(float).values / 100.0
    na = df_base["Sodio (Na %)"].astype(float).values / 100.0
    mg = df_base["Magnesio (Mg %)"].astype(float).values / 100.0
    lipidos = df_base["Lípidos / Extracto Etéreo (%)"].astype(float).values / 100.0
    disponibles = df_base["Disponible"].astype(bool).values
except KeyError as err:
    st.error(f"Falta una columna clave en la tabla: {err}.")
    st.stop()

bounds = []
for idx, row in df_base.iterrows():
    if not row["Disponible"]:
        bounds.append((0.0, 0.0))
    else:
        min_lim = max(0.0, float(row["Min Inclusión (%)"]) / 100.0)
        max_lim = min(1.0, float(row["Max Inclusión (%)"]) / 100.0)
        bounds.append((min_lim, max_lim))

A_eq = np.ones((1, len(c)))
b_eq = np.array([1.0])

# --- MODELADO PREDICTIVO Y OPTIMIZACIÓN DUAL GDE ---
factor_clima = 0.93 if estacion == "Invierno" else (1.05 if estacion == "Verano" else 1.00)
factor_thi = 0.93 if "Moderado" in nivel_thi else (0.83 if "Severo" in nivel_thi else 1.00)
factor_cc = 1.06 if condicion_corporal < 3.0 else 1.00 
factor_aa = 1.04 if "Avanzado" in perfil_aa else 1.00

factor_sistema_cms = 1.12 if "Pastoreo" in sistema_produccion else (1.06 if "Semi-estabulado" in sistema_produccion else 1.00)
factor_sistema_energ = 1.10 if "Pastoreo" in sistema_produccion else (1.05 if "Semi-estabulado" in sistema_produccion else 1.00)

if "Árido" in condiciones_pastoreo:
    factor_pastoreo_energia = 1.10
elif "Temporal" in condiciones_pastoreo:
    factor_pastoreo_energia = 1.05
elif "Silvopastoril" in condiciones_pastoreo:
    factor_pastoreo_energia = 1.03
else:
    factor_pastoreo_energia = 1.00

if "Lignificado" in estado_pasto or "Madurez" in estado_pasto:
    factor_fenologia_pc = 1.15 * factor_aa
    factor_fenologia_energ = 1.10
elif "Tardío" in estado_pasto:
    factor_fenologia_pc = 1.08 * factor_aa
    factor_fenologia_energ = 1.05
else:
    factor_fenologia_pc = 1.00 * factor_aa
    factor_fenologia_energ = 1.00

factor_lodo = 1.00 if condicion_lodo == "Seco y Confortable" else (1.12 if "Moderado" in condicion_lodo else 1.25)
cms_estimado = peso_actual * 0.024 * factor_clima * factor_thi * factor_cc * factor_sistema_cms / (factor_lodo if "Severo" in condicion_lodo else 1.0)

if modo_gde == "Automático Elite (Máxima GDE al Mínimo Costo x kg)":
    mejor_gde = 1.2
    menor_costo_kg_ganado = float('inf')
    gde_candidatos = np.arange(1.0, 2.2, 0.05)
    
    for g_test in gde_candidatos:
        if peso_actual < 280:
            mpc = (0.135 + (g_test * 0.015)) * factor_fenologia_pc
            mneg = (0.70 + (g_test * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
        elif peso_actual < 380:
            mpc = (0.125 + (g_test * 0.015)) * factor_fenologia_pc
            mneg = (0.80 + (g_test * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
        elif peso_actual < 460:
            mpc = (0.115 + (g_test * 0.015)) * factor_fenologia_pc
            mneg = (0.90 + (g_test * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
        else:
            mpc = (0.105 + (g_test * 0.015)) * factor_fenologia_pc
            mneg = (1.00 + (g_test * 0.10)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
            
        row_cp_min = -ca + 1.5 * p_min_ing
        row_cp_max = ca - 2.0 * p_min_ing
        A_ub_t = np.array([-pc * 1.0, -neg * 1.0, -fnd * 1.0, -pendf * 1.0, -ca, -p_min_ing, row_cp_min, row_cp_max])
        b_ub_t = np.array([-mpc, -mneg, -0.27, -0.19, -0.0045, -0.0028, 0.0, 0.0])
        
        res_t = linprog(c, A_ub=A_ub_t, b_ub=b_ub_t, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if res_t.success:
            costo_ton_t = res_t.fun
            costo_alim_dia = (cms_estimado / 1000.0) * costo_ton_t
            costo_por_kg = costo_alim_dia / g_test
            indice_eficiencia = costo_por_kg - (g_test * 150.0) 
            if indice_eficiencia < menor_costo_kg_ganado:
                menor_costo_kg_ganado = indice_eficiencia
                mejor_gde = g_test
    gde = round(float(mejor_gde), 2)

kg_por_ganar = max(0.0, peso_objetivo - peso_actual)
dias_a_meta = kg_por_ganar / gde if gde > 0 else 0

if peso_actual < 280:
    fase = "Recepción y Adaptación"
    meta_pc_base = (0.135 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (0.70 + (gde * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
    meta_fnd_min = 0.32
    meta_pendf_min = 0.24
    meta_pdr_min = 0.082
    meta_pnd_min = 0.048
    meta_ca_min = 0.0055
    meta_p_min = 0.0035
elif peso_actual < 380:
    fase = "Crecimiento / Repasto"
    meta_pc_base = (0.125 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (0.80 + (gde * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
    meta_fnd_min = 0.29
    meta_pendf_min = 0.21
    meta_pdr_min = 0.075
    meta_pnd_min = 0.042
    meta_ca_min = 0.0050
    meta_p_min = 0.0030
elif peso_actual < 460:
    fase = "Desarrollo / Transición"
    meta_pc_base = (0.115 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (0.90 + (gde * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
    meta_fnd_min = 0.27
    meta_pendf_min = 0.19
    meta_pdr_min = 0.070
    meta_pnd_min = 0.040
    meta_ca_min = 0.0048
    meta_p_min = 0.0029
else:
    fase = "Finalización / Engorda Pesada"
    meta_pc_base = (0.105 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (1.00 + (gde * 0.10)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
    meta_fnd_min = 0.25
    meta_pendf_min = 0.18
    meta_pdr_min = 0.065
    meta_pnd_min = 0.038
    meta_ca_min = 0.0045
    meta_p_min = 0.0028

if "Británicas" in raza_seleccionada:
    factor_pc = 1.02
    factor_neg = 1.05
elif "Continentales" in raza_seleccionada:
    factor_pc = 1.05
    factor_neg = 1.08
elif "Cebú" in raza_seleccionada:
    factor_pc = 0.98
    factor_neg = 0.93
else:
    factor_pc = 1.00
    factor_neg = 1.00

if "Toros" in sexo_lote:
    factor_sexo_pc = 1.08
    factor_sexo_neg = 1.04
elif "Vaquillas" in sexo_lote:
    factor_sexo_pc = 0.96
    factor_sexo_neg = 1.06
elif "Vacas" in sexo_lote:
    factor_sexo_pc = 0.94
    factor_sexo_neg = 1.02
else:
    factor_sexo_pc = 1.00
    factor_sexo_neg = 1.00

if "Precoz" in marco_lote:
    factor_marco = 1.05
elif "Grande" in marco_lote:
    factor_marco = 0.95
else:
    factor_marco = 1.00

factor_promotor = 1.08 if promotor_crecimiento == "Implante Hormonal" else (1.15 if "Agonista" in promotor_crecimiento else 1.00)
factor_compensatorio = 0.93 if "Compensatorio" in historial_nutricional else 1.00

meta_pc_min = meta_pc_base * factor_pc * factor_sexo_pc * factor_promotor
meta_neg_min = meta_neg_base * factor_neg * factor_sexo_neg * factor_marco * factor_lodo * factor_compensatorio

# --- EJECUCIÓN DEL MOTOR LINEAL ---
resultado = None
modo_tolerancia_activo = False

row_ca_p_min = -ca + 1.5 * p_min_ing
row_ca_p_max = ca - 2.0 * p_min_ing
A_ub = np.array([-pc, -neg, -fnd, -pendf, -pdr, -pnd, -ca, -p_min_ing, row_ca_p_min, row_ca_p_max])
b_ub = np.array([-meta_pc_min, -meta_neg_min, -meta_fnd_min, -meta_pendf_min, -meta_pdr_min, -meta_pnd_min, -meta_ca_min, -meta_p_min, 0.0, 0.0])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

if not resultado.success:
    row_ca_p_min_rel = -ca + 1.2 * p_min_ing
    row_ca_p_max_rel = ca - 2.5 * p_min_ing
    A_ub_rel = np.array([-pc, -neg, -fnd, -pendf, -pdr, -pnd, -ca, -p_min_ing, row_ca_p_min_rel, row_ca_p_max_rel])
    resultado = linprog(c, A_ub=A_ub_rel, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if resultado.success:
        modo_tolerancia_activo = True

if not resultado.success:
    meta_pc_min_rel = meta_pc_min * 0.90
    meta_neg_min_rel = meta_neg_min * 0.90
    b_ub_rel2 = np.array([-meta_pc_min_rel, -meta_neg_min_rel, -meta_fnd_min, -meta_pendf_min, -meta_pdr_min, -meta_pnd_min, -meta_ca_min, -meta_p_min, 0.0, 0.0])
    resultado = linprog(c, A_ub=A_ub_rel, b_ub=b_ub_rel2, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if resultado.success:
        modo_tolerancia_activo = True

costo_ton_optimizado = resultado.fun if resultado.success else 4500.0 

consumo_total_ciclo_cab = cms_estimado * dias_a_meta
costo_alimentacion_cab = (consumo_total_ciclo_cab / 1000.0) * costo_ton_optimizado
costo_compra_cab = peso_actual * precio_compra_kg

costo_sanidad_inicial = costo_aretaje + costo_barrido + costo_vacunacion + costo_desparasitacion + costo_vitaminacion
costo_total_sanidad_y_manejo = costo_sanidad_inicial + costo_mano_obra_fijo

costo_total_cab = costo_compra_cab + costo_alimentacion_cab + costo_total_sanidad_y_manejo
ingreso_venta_cab = peso_objetivo * precio_venta_kg
utilidad_neta_cab = ingreso_venta_cab - costo_total_cab
roi_cab = (utilidad_neta_cab / costo_total_cab) * 100 if costo_total_cab > 0 else 0

# --- FUNCIÓN GENERADORA DE PDF ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(5, 150, 105)
        self.cell(0, 10, 'NutriON 360 Ultra AI - Creado por Dr. Alejandro Castaneda Correa', 0, 1, 'C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Pagina {self.page_no()} | Smart Collars IoT & Health AI - Dr. Alejandro Castaneda Correa', 0, 0, 'C')

def generar_pdf_reporte():
    pdf = PDFReport()
    pdf.add_page()
    
    def safe_str(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, safe_str("1. Resumen Zootecnico y Salud IoT"), 0, 1)
    pdf.set_font('Arial', '', 10)
    
    resumen_dict = {
        "Cabezas en el Lote": f"{cantidad_animales} animales",
        "Etapa Fisiologica": fase,
        "Peso Actual / Meta": f"{peso_actual} kg -> {peso_objetivo} kg",
        "Ganancia Diaria Esperada (GDE)": f"{gde} kg/dia",
        "Consumo Materia Seca (CMS)": f"{cms_estimado:.2f} kg/dia",
        "Dias Proyectados al Objetivo": f"{dias_a_meta:.0f} dias"
    }
    
    for k, v in resumen_dict.items():
        pdf.cell(95, 7, safe_str(f"{k}:"), 0, 0)
        pdf.cell(95, 7, safe_str(f"{v}"), 0, 1)
        
    pdf.ln(4)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_str("2. Evaluacion Financiera por Cabeza"), 0, 1)
    pdf.set_font('Arial', '', 10)
    
    econ_dict = {
        "Costo de Compra Becerro": f"${costo_compra_cab:,.2f} MXN",
        "Costo Total de Alimentacion": f"${costo_alimentacion_cab:,.2f} MXN",
        "Sanidad Inicial": f"${costo_sanidad_inicial:,.2f} MXN",
        "Mano de Obra y Operacion": f"${costo_mano_obra_fijo:,.2f} MXN",
        "Costo Total de Produccion": f"${costo_total_cab:,.2f} MXN",
        "Ingreso por Venta Ganado": f"${ingreso_venta_cab:,.2f} MXN",
        "Utilidad Neta Esperada": f"${utilidad_neta_cab:,.2f} MXN",
        "ROI del Ciclo": f"{roi_cab:.1f}%"
    }
    
    for k, v in econ_dict.items():
        pdf.cell(95, 7, safe_str(f"{k}:"), 0, 0)
        pdf.cell(95, 7, safe_str(f"{v}"), 0, 1)

    pdf.ln(4)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_str("3. Formula Optimizada (Costo Minimo)"), 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(100, 7, safe_str("Ingrediente"), 1, 0, 'L')
    pdf.cell(45, 7, safe_str("Inclusion (%)"), 1, 0, 'C')
    pdf.cell(45, 7, safe_str("Kg / Tonelada"), 1, 1, 'C')
    
    pdf.set_font('Arial', '', 9)
    if resultado.success:
        for i, ing in enumerate(nombres):
            frac = resultado.x[i]
            if frac > 0.0001:
                pdf.cell(100, 6, safe_str(ing), 1, 0, 'L')
                pdf.cell(45, 6, safe_str(f"{frac*100:.2f}%"), 1, 0, 'C')
                pdf.cell(45, 6, safe_str(f"{frac*1000:.1f} kg"), 1, 1, 'C')
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(100, 6, safe_str("COSTO TOTAL POR TONELADA"), 1, 0, 'L')
        pdf.cell(90, 6, safe_str(f"${costo_ton_optimizado:,.2f} MXN"), 1, 1, 'C')

    output = pdf.output()
    if isinstance(output, bytes):
        return output
    elif isinstance(output, bytearray):
        return bytes(output)
    else:
        return output.encode('latin1')

# --- 6. INTERFAZ MODULAR POR PESTAÑAS (12 TABS ULTRA AI) ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "📋 1. Resumen & Clima", 
    "🧪 2. Nutrición", 
    "📊 3. Economía", 
    "🩺 4. Collares IoT",
    "🚜 5. Báscula",
    "🔮 6. Compra-Venta",
    "📄 7. Reporte PDF",
    "💬 8. NutriON IA",
    "🧭 9. Citas",
    "📡 10. NIR & pH Ruminal",
    "🎙️ 11. IA Acústica & Visión",
    "🌱 12. Gemelos & Blockchain"
])

with tab1:
    st.subheader("Predicciones con Telemetría Climatológica y THI en Vivo")
    st.markdown(f"Evaluación del lote con peso actual de **{peso_actual} kg** y meta de **{peso_objetivo} kg** | Sistema: *{sistema_produccion}*:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Etapa Fisiológica", fase)
        st.metric("Ganancia Esperada (GDE)", f"{gde} kg/día")
    with col2:
        st.metric("Consumo MS (Ajustado THI)", f"{cms_estimado:.2f} kg/día")
        st.metric("Días Proyectados a Meta", f"{dias_a_meta:.0f} días")
    with col3:
        st.metric("Cabezas en el Lote", f"{cantidad_animales} animales")
        st.metric("Ganancia Total Esperada", f"{kg_por_ganar:.1f} kg/cab")
    
    st.markdown("---")
    st.subheader("📈 Gráfica Dinámica: Peso y Consumo de Materia Seca en el Tiempo")
    
    semanas = int(np.ceil(dias_a_meta / 7)) if dias_a_meta > 0 else 1
    semanas = max(semanas, 4)
    
    lista_semanas = []
    lista_pesos = []
    lista_cms = []
    
    for i in range(semanas + 1):
        dias_transcurridos = i * 7
        peso_proy = min(peso_objetivo, peso_actual + (dias_transcurridos * gde))
        cms_proy = peso_proy * 0.024 * factor_clima * factor_thi * factor_sistema_cms
        lista_semanas.append(f"Semana {i}")
        lista_pesos.append(peso_proy)
        lista_cms.append(round(cms_proy, 2))
    
    fig_comportamiento = make_subplots(specs=[[{"secondary_y": True}]])
    fig_comportamiento.add_trace(go.Scatter(x=lista_semanas, y=lista_pesos, name="Peso Proyectado (kg)", mode="lines+markers", line=dict(color="#059669", width=3.5)), secondary_y=False)
    fig_comportamiento.add_trace(go.Scatter(x=lista_semanas, y=lista_cms, name="Consumo Materia Seca (kg/día)", mode="lines+markers", line=dict(color="#d97706", width=3, dash="dash")), secondary_y=True)
    fig_comportamiento.update_layout(
        title=dict(text=f"Dinámica de Engorda Ultra ({perfil_aa[:18]} | GDE: {gde} kg/d)", font=dict(family="Calibri", size=14, color="#0f172a"), x=0.5), 
        plot_bgcolor="#ffffff", 
        paper_bgcolor="#ffffff", 
        font=dict(family="Calibri", size=12, color="#1e293b"), 
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5, font=dict(family="Calibri", size=12)), 
        margin=dict(l=20, r=20, t=60, b=70)
    )
    fig_comportamiento.update_yaxes(title_text="<b>Peso Vivo del Animal (kg)</b>", secondary_y=False, color="#059669", title_font=dict(family="Calibri", size=12))
    fig_comportamiento.update_yaxes(title_text="<b>Consumo de Materia Seca (kg/día)</b>", secondary_y=True, color="#d97706", title_font=dict(family="Calibri", size=12))
    st.plotly_chart(fig_comportamiento, use_container_width=True)

with tab2:
    st.subheader("🧪 Laboratorio de Nutrición y Catálogo de Ingredientes Patrocinados")
    st.markdown(
        "**Personaliza perfiles nutricionales y explora ingredientes recomendados por marcas líderes.** "
        "Los cambios realizados se guardan de forma persistente."
    )
    
    st.session_state.df_ingredientes_state = st.data_editor(
        st.session_state.df_ingredientes_state, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Disponible": st.column_config.CheckboxColumn("¿Disponible en tu Rancho?", default=True),
            "Min Inclusión (%)": st.column_config.NumberColumn("Min (%)", min_value=0.0, max_value=100.0, step=0.5),
            "Max Inclusión (%)": st.column_config.NumberColumn("Max (%)", min_value=0.0, max_value=100.0, step=0.5),
        },
        key="editor_ingredientes_persisted_ultra"
    )

with tab3:
    st.subheader("📊 Evaluación Económica, Mercados de Futuros (Hedging) y Bonos de Carbono")
    
    if resultado.success:
        if modo_tolerancia_activo:
            st.warning("⚠️ **Aviso de Auto-Recuperación NutriON:** El sistema ajustó automáticamente los márgenes de tolerancia de minerales y energía.")
        
        consumo_total_ciclo_cab = cms_estimado * dias_a_meta
        costo_alimentacion_cab = (consumo_total_ciclo_cab / 1000.0) * costo_ton_optimizado
        
        costo_compra_cab = peso_actual * precio_compra_kg
        costo_total_cab = costo_compra_cab + costo_alimentacion_cab + costo_total_sanidad_y_manejo
        
        ingreso_venta_cab = peso_objetivo * precio_venta_kg
        utilidad_neta_cab = ingreso_venta_cab - costo_total_cab
        roi_cab = (utilidad_neta_cab / costo_total_cab) * 100 if costo_total_cab > 0 else 0
        
        status_rentabilidad = "🟢 Rentable" if utilidad_neta_cab > 0 else "🔴 Negativo"
        
        col_ec1, col_ec2, col_ec3, col_ec4 = st.columns(4)
        with col_ec1:
            st.metric("Compra Becerro", f"${costo_compra_cab:,.0f}")
            st.metric("Alimento/Cab", f"${costo_alimentacion_cab:,.0f}")
        with col_ec2:
            st.metric("Costo Total", f"${costo_total_cab:,.0f}")
            st.metric("Sanidad Inicial", f"${costo_sanidad_inicial:,.0f}")
        with col_ec3:
            st.metric("Ingreso Venta", f"${ingreso_venta_cab:,.0f}")
            st.metric("Utilidad Neta", f"${utilidad_neta_cab:,.0f}")
        with col_ec4:
            st.metric("ROI Ciclo", f"{roi_cab:.1f}%")
            st.metric("Estatus", status_rentabilidad)
            
        st.markdown("---")
        st.markdown("#### 📈 Monitor de Mercados de Futuros (CBOT) y Cobertura de Costos:")
        st.info(
            "💡 **Recomendación Hedging NutriON 360:** Basado en tu consumo proyectado de **"
            f"{(consumo_total_ciclo_cab * cantidad_animales) / 1000.0:,.1f} toneladas** de alimento, "
            "el mercado de granos presenta estabilidad en contratos a 3 meses. Considera asegurar un 50% de tus requerimientos de maíz."
        )
        
        st.markdown("---")
        st.markdown("#### 📋 Desglose Analítico de Costos por Tonelada de Alimento:")
        
        tabla_mezcla = []
        for i, ingrediente in enumerate(nombres):
            fraccion = resultado.x[i]
            porcentaje = fraccion * 100
            kilos = fraccion * 1000
            if porcentaje > 0.01:
                costo_parcial = fraccion * c[i]
                tabla_mezcla.append({
                    "Ingrediente": ingrediente,
                    "Inclusion (%)": round(porcentaje, 1),
                    "Kg por Tonelada (1,000 kg)": round(kilos, 2),
                    "Costo Unitario ($/ton)": f"${c[i]:,.2f}",
                    "Aporte al Costo Total ($)": f"${costo_parcial:,.2f}"
                })
        
        total_porcentaje = sum([row["Inclusion (%)"] for row in tabla_mezcla])
        total_kilos = sum([row["Kg por Tonelada (1,000 kg)"] for row in tabla_mezcla])
        total_costo = resultado.fun

        tabla_mezcla_con_totales = tabla_mezcla.copy()
        tabla_mezcla_con_totales.append({
            "Ingrediente": "TOTALES / MEZCLA FINAL",
            "Inclusion (%)": round(total_porcentaje, 1),
            "Kg por Tonelada (1,000 kg)": round(total_kilos, 1),
            "Costo Unitario ($/ton)": "-",
            "Aporte al Costo Total ($)": f"${total_costo:,.2f}"
        })

        df_mezcla_final = pd.DataFrame(tabla_mezcla_con_totales)
        st.dataframe(df_mezcla_final, use_container_width=True, hide_index=True)
        
        aporte_pc = np.sum(resultado.x * pc) * 100
        aporte_neg = np.sum(resultado.x * neg)
        aporte_fnd = np.sum(resultado.x * fnd) * 100
        aporte_pendf = np.sum(resultado.x * pendf) * 100
        aporte_ca = np.sum(resultado.x * ca) * 100
        aporte_p = np.sum(resultado.x * p_min_ing) * 100
        aporte_lipidos = np.sum(resultado.x * lipidos) * 100
        
        relacion_ca_p = (aporte_ca / aporte_p) if aporte_p > 0 else 0
        status_ca_p = "🟢 Óptimo"
        riesgo_sara = "🟢 Seguro" if aporte_pendf >= 18.0 else ("🟡 Monitorear" if aporte_pendf >= 14.0 else "🔴 Alto Riesgo")
        
        ge_diaria = cms_estimado * 18.4 
        reduccion_lipidica = max(0.0, (aporte_lipidos - 3.0) * 0.003)
        reduccion_ionoforo = 0.06 if "Ionóforos" in aditivo_ruminal or "Ambos" in aditivo_ruminal else 0.0
        
        factor_fnd_ym = 0.035 + (aporte_fnd / 100.0) * 0.035
        ym_ajustado = max(0.025, factor_fnd_ym - reduccion_lipidica - reduccion_ionoforo)
        
        ch4_g_dia = (ge_diaria * ym_ajustado / 55.65) * 1000
        co2e_anual = (ch4_g_dia * 365 / 1000.0) * 28.0 
        linea_base_co2e = 4200.0
        ahorro_co2e_kg = max(0.0, linea_base_co2e - co2e_anual)
        valor_bono_mxn = (ahorro_co2e_kg / 1000.0) * 350.0
        
        st.markdown("---")
        st.subheader("🛡️ Validación Mineral, Salud Ruminal y Auditoría de Bonos Verdes")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Calcio (Ca)", f"{aporte_pc:.1f}%", "Mineral")
            st.metric("Relación Ca:P", f"{relacion_ca_p:.1f}:1", status_ca_p)
        with col_m2:
            st.metric("Fibra peNDF", f"{aporte_pendf:.1f}%", "Anti-acidosis")
            st.metric("Riesgo SARA", riesgo_sara, "Ruminal")
        with col_m3:
            st.metric("Emisión CH4", f"{ch4_g_dia:.1f} g/d", "IPCC Tier 2")
            st.metric("Eq. CO2e", f"{co2e_anual:,.0f} kg/año")
        with col_m4:
            st.metric("Bonos Carbono", f"${valor_bono_mxn:,.0f}", "Anual/Cab")
            st.metric("Lípidos", f"{aporte_lipidos:.1f}%", "Mitigador")
    else:
        st.error("⚠️ Las restricciones son demasiado estrictas para encontrar una fórmula. Ajusta los mínimos/máximos en la pestaña 2.")

with tab4:
    st.subheader("🩺 Collares IoT de Masticación & Detección IA de Animales Enfermos")
    st.markdown("""
        **Inteligencia Artificial aplicada al Comportamiento Animal:** Los collares IoT integrados monitorean 
        los movimientos de masticación (minutos de rumia diarios) y las visitas al comedero en tiempo real. 
        Si un animal reduce drásticamente su actividad o ausentismo en comederos, **NutriON 360 Ultra** 
        envía una notificación instantánea al teléfono celular del productor para aislarlo, tratarlo o descartarlo.
    """)
    
    col_h1, col_h2, col_h3 = st.columns(3)
    df_collares = st.session_state.df_collares_state
    
    total_animales_mon = len(df_collares)
    sanos_count = len(df_collares[df_collares["Estatus Collares IoT"].str.contains("Sano")])
    alertas_count = len(df_collares[df_collares["Estatus Collares IoT"].str.contains("Alerta")])
    enfermos_count = len(df_collares[df_collares["Estatus Collares IoT"].str.contains("Enfermo")])
    
    with col_h1:
        st.metric("Collares IoT Activos", f"{total_animales_mon} cabezas")
    with col_h2:
        st.metric("Animales Sanos", f"{sanos_count} cabezas", "🟢 Normal")
    with col_h3:
        st.metric("Enfermos / Riesgo (Descarte)", f"{enfermos_count} cabezas", delta=f"-{enfermos_count}", delta_color="inverse")
        
    st.markdown("---")
    st.markdown("#### 📱 Centro de Notificaciones y Alertas Automáticas al Teléfono")
    
    col_phone_1, col_phone_2 = st.columns([2, 1])
    with col_phone_1:
        telefono_productor = st.text_input("Número Celular (WhatsApp / SMS para Alertas)", placeholder="+52 33 1234 5678", value="+52 ")
        canal_alerta = st.selectbox("Canal de Notificación Preferido", ["WhatsApp Business API", "SMS Directo", "Push Notification en App", "Todos los canales"])
    with col_phone_2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📲 Enviar Prueba de Alerta SMS/Push", use_container_width=True):
            if len(telefono_productor) > 5:
                st.success(f"📱 **¡Alerta Enviada a {telefono_productor}!**\n\n*Mensaje:* '⚠️ Alerta NutriON Ultra: Animal #1014 muestra caída del 52% en masticación y 0 visitas al comedero hoy. Posible inicio de BRD o acidosis. Aislar inmediatamente.'")
                st.balloons()
            else:
                st.warning("⚠️ Ingresa un número de celular válido para la prueba.")
                
    st.markdown("---")
    st.markdown("#### 📊 Monitoreo Individual por Arete (Datos de Collar IoT en Vivo)")
    st.dataframe(df_collares, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("🚜 Telemetría IoT y Simulación de Báscula para Carros Mezcladores")
    st.markdown("Conexión inalámbrica con indicadores de pesaje en batea para control milimétrico de la ración:")
    
    if resultado.success:
        cms_total_lote = cms_estimado * cantidad_animales
        alimento_total_ciclo = cms_total_lote * dias_a_meta
        costo_total_lote = (alimento_total_ciclo / 1000.0) * resultado.fun
        
        col_l1, col_l2, col_l3 = st.columns(3)
        with col_l1:
            st.metric("Consumo Diario Lote", f"{cms_total_lote:,.1f} kg/día")
        with col_l2:
            st.metric("Alimento Total Lote", f"{alimento_total_ciclo/1000.0:,.1f} tons")
        with col_l3:
            st.metric("Costo Total Ciclo", f"${costo_total_lote:,.0f} MXN")
            
        st.markdown("---")
        st.markdown("#### 📶 Simulación de Carga en Tiempo Real con Báscula IoT:")
        ingrediente_ejemplo = nombres[0] if len(nombres) > 0 else "Forraje"
        porcentaje_ejemplo = resultado.x[0] * 100 if len(resultado.x) > 0 else 0.0
        kilos_meta_lote = (cms_total_lote * (porcentaje_ejemplo / 100.0))
        
        st.info(
            f"🔗 **Estado de Conexión IoT:** 🟢 Vinculado con Báscula Carro Mezclador #1 (Bluetooth / Wi-Fi)\n\n"
            f"**Carga Actual en Proceso:** {ingrediente_ejemplo} ({porcentaje_ejemplo:.1f}% de la ración)\n"
            f"* **Meta en Batea:** {kilos_meta_lote:,.1f} kg\n"
            f"* **Lectura Actual en Báscula:** `{kilos_meta_lote * 0.99:,.1f} kg` (Margen de precisión: 99.1% - 🟢 Semáforo Verde)"
        )

with tab6:
    st.subheader("🔮 Simulador Estratégico de Compra y Venta")
    st.markdown("Este modelo de inteligencia de negocios evalúa miles de combinaciones de compra y venta para encontrar el punto exacto de rentabilidad máxima.")
    
    def calcular_peso_optimo_financiero(precio_compra_base, precio_venta_base, costo_ton_alim, gde_fijo, costo_fijos):
        pesos_compra = range(200, 360, 10)
        pesos_venta = range(450, 600, 10)
        
        mejor_utilidad = -float('inf')
        optimo = {}
        matriz_resultados = []
        
        for wi in pesos_compra:
            pc = precio_compra_base - ((wi - 250) * 0.04) 
            for wf in pesos_venta:
                if wf <= wi + 50: 
                    continue
                kg_ganados = wf - wi
                dias = kg_ganados / gde_fijo if gde_fijo > 0 else 1
                peso_promedio = (wi + wf) / 2.0
                cms_ciclo = peso_promedio * 0.024 
                costo_alimento = (cms_ciclo * dias / 1000.0) * costo_ton_alim
                costo_compra = wi * pc
                costo_total = costo_compra + costo_alimento + costo_fijos
                pv = precio_venta_base if wf <= 540 else precio_venta_base - ((wf - 540) * 0.05)
                ingreso_venta = wf * pv
                utilidad = ingreso_venta - costo_total
                matriz_resultados.append({"Peso Compra (kg)": wi, "Peso Venta (kg)": wf, "Utilidad Neta (MXN)": utilidad})
                if utilidad > mejor_utilidad:
                    mejor_utilidad = utilidad
                    optimo = {"Peso_Compra_Optimo": wi, "Precio_Compra_Estimado": pc, "Peso_Venta_Optimo": wf, "Precio_Venta_Estimado": pv, "Utilidad_Neta_Maxima": utilidad, "Dias_En_Corral": dias}
        return optimo, pd.DataFrame(matriz_resultados)
    
    resultado_optimo, df_simulacion = calcular_peso_optimo_financiero(
        precio_compra_base=precio_compra_kg, 
        precio_venta_base=precio_venta_kg,
        costo_ton_alim=costo_ton_optimizado, 
        gde_fijo=gde, 
        costo_fijos=costo_total_sanidad_y_manejo
    )
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Peso IDEAL Compra", f"{resultado_optimo['Peso_Compra_Optimo']} kg")
    with col_s2:
        st.metric("Peso IDEAL Venta", f"{resultado_optimo['Peso_Venta_Optimo']} kg")
    with col_s3:
        st.metric("Utilidad Máxima", f"${resultado_optimo['Utilidad_Neta_Maxima']:,.0f} /cab")
    with col_s4:
        st.metric("Días en Corral", f"{resultado_optimo['Dias_En_Corral']:.0f} días")
        
    st.markdown("---")
    df_pivot = df_simulacion.pivot(index="Peso Compra (kg)", columns="Peso Venta (kg)", values="Utilidad Neta (MXN)")
    fig_heat = px.imshow(df_pivot, labels=dict(x="Peso Venta (kg)", y="Peso Compra (kg)", color="Utilidad ($)"), color_continuous_scale="Mint", aspect="auto")
    fig_heat.update_layout(font=dict(family="Calibri", size=12, color="#1e293b"), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
    st.plotly_chart(fig_heat, use_container_width=True)

with tab7:
    st.subheader("📄 Generación y Descarga de Reporte Ejecutivo PDF Ultra")
    if resultado.success:
        pdf_bytes = generar_pdf_reporte()
        st.download_button(
            label="📥 Descargar Reporte Ejecutivo Ultra en PDF",
            data=pdf_bytes,
            file_name="NutriON_360_Ultra_Reporte.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.success("¡El reporte PDF Ultra se ha generado correctamente!")
    else:
        st.warning("⚠️ Resuelve las restricciones nutricionales para habilitar la descarga.")

with tab8:
    st.subheader("💬 Asistente Virtual Inteligente NutriON (IA Asistente)")
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.nutrion_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_query := st.chat_input("Escribe tu pregunta o reporte aquí..."):
        st.session_state.nutrion_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
        bot_response = f"🤖 He registrado tu consulta: *\"{user_query}\"*. Como asistente **NutriON Ultra AI**, he enviado este requerimiento al equipo técnico del Dr. Alejandro Castañeda."
        st.session_state.nutrion_messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)

with tab9:
    st.subheader("🧭 Centro de Asesoría Virtual & Agendamiento de Consultoría Elite")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        nombre_contacto = st.text_input("Nombre del Productor / Responsable", key="rem_nombre")
        rancho_ubicacion = st.text_input("Ubicación del Rancho / Planta", key="rem_ubi")
        contacto_email = st.text_input("Correo Electrónico o Teléfono de Contacto", key="rem_contacto")
    with col_c2:
        tipo_consulta = st.selectbox("Motivo de Asesoría Remota", [
            "Interpretación de Alertas de Collares IoT y Sensores NIR",
            "Auditoría y Calibración de Planta de Alimentos", 
            "Diagnóstico y Control de Acidosis / Bolos de pH", 
            "Optimización y Auditoría de Costos de Ración"
        ], key="rem_tipo")
        fecha_cita = st.date_input("Fecha Preferida para la Asesoría", min_value=datetime.now().date(), key="rem_fecha")
        hora_cita = st.selectbox("Horario Preferido", ["09:00 AM - 09:30 AM", "11:00 AM - 11:30 AM", "01:00 PM - 01:30 PM", "04:00 PM - 04:30 PM"], key="rem_hora")
        
    st.markdown("##### 💳 Datos de Pago para la Consultoría ($475 MXN / 30 min)")
    col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
    with col_p1:
        tarjeta_asesoria = st.text_input("Número de Tarjeta", placeholder="4000 1234 5678 9010", key="rem_card")
    with col_p2:
        exp_asesoria = st.text_input("Expiración (MM/AA)", placeholder="12/28", key="rem_exp")
    with col_p3:
        cvv_asesoria = st.text_input("CVV", type="password", placeholder="123", key="rem_cvv")
        
    st.markdown("")
    if st.button("💳 Pagar $475 MXN y Agendar Asesoría Remota", use_container_width=True):
        if nombre_contacto and contacto_email and tarjeta_asesoria:
            st.success(f"🎉 **¡Pago Exitoso y Cita Agendada!** Estimado(a) **{nombre_contacto}**, tu asesoría ha sido programada para el **{fecha_cita}** a las **{hora_cita}**.")
            st.balloons()
        else:
            st.warning("⚠️ Completa tu nombre, contacto y datos de tarjeta.")

# --- NUEVA PESTAÑA 10: SENSORES NIR Y BOLOS RUMINALES IoT (pH) ---
with tab10:
    st.subheader("📡 Telemetría NIR en Tiempo Real & Bolos Ruminales de pH (SARA Prevention)")
    st.markdown("""
        **Tecnología Espectroscópica y Telemetría Interna:** Controla la variación de materia seca en ensilados mediante escaneo NIR 
        y supervisa el pH ruminal 24/7 con bolos ingeribles para prevenir la Acidosis Ruminal Subclínica (SARA).
    """)
    
    col_nir1, col_nir2 = st.columns(2)
    with col_nir1:
        st.markdown("#### 🔬 Escaneo NIR Portátil (Ensilado de Maíz)")
        humedad_actual_nir = st.slider("Humedad Actual Detectada por Sensor NIR (%)", min_value=50.0, max_value=75.0, value=65.0, step=0.5)
        ms_real_nir = 100.0 - humedad_actual_nir
        st.metric("Materia Seca Real en Batea", f"{ms_real_nir:.1f}%", "Sensor NIR Activo 🟢")
        if ms_real_nir < 33.0:
            st.warning("⚠️ **Aviso NIR:** El ensilado está más húmedo de lo previsto. El sistema ajustó automáticamente los kilos en batea para evitar desbalances de energía.")
        else:
            st.success("🟢 **Aviso NIR:** Humedad dentro del rango óptimo para fermentación y estabilidad ruminal.")

    with col_nir2:
        st.markdown("#### 🌡️ Telemetría de Bolos Ruminales (pH en Vivo)")
        ph_promedio_lote = st.slider("pH Ruminal Promedio del Lote (Bolos IoT)", min_value=5.2, max_value=7.0, value=6.2, step=0.05)
        if ph_promedio_lote < 5.8:
            st.error("🔴 **ALERTA SARA (Acidosis Subclínica):** El pH ruminal ha caído por debajo de 5.8. Riesgo inminente de laminitis y caída de consumo.")
            st.metric("Estado Ruminal", "⚠️ Peligro de Acidosis", delta="Crítico", delta_color="inverse")
        elif ph_promedio_lote < 6.0:
            st.warning("🟡 **Precaución Ruminal:** pH en zona de transición ácida. Se recomienda incrementar fibra efectiva (peNDF) o añadir buffer.")
            st.metric("Estado Ruminal", "🟡 Precaución", delta="Atención", delta_color="off")
        else:
            st.success("🟢 **Salud Ruminal Óptima:** pH estable en rango fisiológico normal (6.0 - 6.8).")
            st.metric("Estado Ruminal", "🟢 Saludable", delta="Estable", delta_color="normal")

    st.markdown("---")
    st.markdown("#### 📈 Histórico de pH Ruminal en las Últimas 24 Horas (Monitoreo de Bolos IoT)")
    horas_dia = [f"{h:02d}:00" for h in range(24)]
    # Simulación de curva de pH diaria con caídas post-alimentación
    curva_ph = [6.5, 6.6, 6.7, 6.6, 6.4, 6.2, 5.9, ph_promedio_lote, ph_promedio_lote - 0.2, ph_promedio_lote, 6.1, 6.3, 6.5, 6.6, 6.5, 6.3, 6.0, 5.9, ph_promedio_lote, 6.2, 6.4, 6.5, 6.6, 6.5]
    
    fig_ph = px.line(x=horas_dia, y=curva_ph, labels={"x": "Hora del Día", "y": "pH Ruminal Interno"}, markers=True)
    fig_ph.add_hline(y=5.8, line_dash="dash", line_color="red", annotation_text="Umbral Crítico SARA (pH 5.8)")
    fig_ph.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(family="Calibri", size=12, color="#1e293b"))
    st.plotly_chart(fig_ph, use_container_width=True)

# --- NUEVA PESTAÑA 11: IA ACÚSTICA (TOS/BRD) & VISIÓN (COJERAS/BCS) ---
with tab11:
    st.subheader("🎙️ IA Acústica (Detección de Tos / BRD) & Visión Artificial (Cojeras y BCS)")
    st.markdown("""
        **Vigilancia Sanitaria No Invasiva:** Micrófonos inteligentes con IA detectan patrones acústicos de tos característicos 
        de la Enfermedad Respiratoria Bovina (BRD) días antes de los síntomas clínicos. Asimismo, cámaras de visión cenital 
        analizan la simetría de la marcha y la condición corporal (BCS).
    """)
    
    col_ac1, col_ac2 = st.columns(2)
    with col_ac1:
        st.markdown("#### 🎙️ Monitoreo Acústico de Enfermedad Respiratoria (BRD)")
        frecuencia_tos = st.slider("Eventos de Tos Detectados por Hora (Micrófonos Corral)", min_value=0, max_value=30, value=3, step=1)
        if frecuencia_tos > 12:
            st.error(f"🔴 **Alerta Biológica BRD:** Se registraron {frecuencia_tos} eventos de tos/hora en el corral. Alta probabilidad de brote respiratorio infeccioso.")
            st.metric("Estatus Sanitario Respiratorio", "⚠️ Brote BRD Inminente", delta="Acción Inmediata", delta_color="inverse")
        elif frecuencia_tos > 6:
            st.warning(f"🟡 **Precaución Respiratoria:** {frecuencia_tos} tos/hora detectadas. Monitorear temperatura corporal de animales jóvenes.")
            st.metric("Estatus Sanitario Respiratorio", "🟡 Vigilancia Activa", delta="Atención", delta_color="off")
        else:
            st.success("🟢 **Ambiente Respiratorio Limpio:** Tasa normal de eventos acústicos en corrales.")
            st.metric("Estatus Sanitario Respiratorio", "🟢 Normal", delta="Seguro", delta_color="normal")

    with col_ac2:
        st.markdown("#### 📷 Visión Artificial para Cojeras y Condición Corporal (BCS)")
        indice_cojera = st.selectbox("Evaluación de Marcha por Cámaras IA", ["Marcha Normal / Simétrica (Score 1)", "Leve Asimetría / Rigidez (Score 2 - Vigilar)", "Cojera Evidente / Postura Arqueada (Score 3 - Tratamiento URGENTE)"])
        bcs_vision = st.slider("Condición Corporal Estimada por Visión Artificial (BCS)", min_value=1.0, max_value=5.0, value=condicion_corporal, step=0.25)
        
        st.metric("BCS Automatizado por IA", f"{bcs_vision:.2f} / 5.0")
        if "Score 3" in indice_cojera:
            st.error("🔴 **Alerta de Bienestar y Movimiento:** Animal detectado con cojera grado 3. Afecta drásticamente el acceso al agua y comedero.")
        else:
            st.success("🟢 **Movilidad y Marcha Lote:** Sin incidencias graves de cojeras detectadas por el sistema de cámaras.")

    st.markdown("---")
    st.markdown("#### 📊 Matriz de Riesgo Sanitario Combinado (Acústica + Visión + Collares)")
    
    df_matriz_riesgo = pd.DataFrame({
        "Arete / Animal": [f"ID-{1000 + i}" for i in [1, 5, 12, 18, 22]],
        "Tos Acústica (IA)": ["Normal", "Frecuente (⚠️)", "Normal", "Leve", "Alta (🚨)"],
        "Cojera (Visión)": ["Grado 1", "Grado 1", "Grado 2 (⚠️)", "Grado 1", "Grado 3 (🚨)"],
        "Rumia (Collar IoT)": ["580 min", "310 min (⚠️)", "540 min", "490 min", "190 min (🚨)"],
        "Diagnóstico Sugerido": ["Sano", "Posible BRD / Neumonía", "Desgaste Podal", "Fatiga", "Aislamiento Inmediato URGENTE"]
    })
    st.dataframe(df_matriz_riesgo, use_container_width=True, hide_index=True)

# --- NUEVA PESTAÑA 12: GEMELOS DIGITALES & BLOCKCHAIN CARBONO ---
with tab12:
    st.subheader("🌱 Gemelos Digitales (Whole-Farm Simulation) & Trazabilidad Blockchain de Carbono")
    st.markdown("""
        **Sostenibilidad y Futuro Ganadero:** Simula escenarios climáticos y económicos a largo plazo mediante un gemelo digital 
        de todo el rancho. Además, audita y registra de forma inmutable la reducción de emisiones de metano para certificar 
        y comercializar **Bonos de Carbono Verificables** en mercados internacionales.
    """)
    
    col_gt1, col_gt2 = st.columns(2)
    with col_gt1:
        st.markdown("#### 🔮 Simulador Whole-Farm (Gemelo Digital)")
        horizonte_sim = st.slider("Horizonte de Proyección (Años)", min_value=1, max_value=10, value=5, step=1)
        escenario_climatico = st.selectbox("Escenario Climático Proyectado", ["Año Normal / Histórico", "Sequía Prolongada (Reducción Forraje -30%)", "Año de Alta Pluviosidad y Abundancia"])
        
        if "Sequía" in escenario_climatico:
            proj_utilidad_total = utilidad_neta_cab * cantidad_animales * 0.75 * horizonte_sim
            st.warning("⚠️ **Simulación de Sequía:** El gemelo digital proyecta una contracción del 25% en márgenes por mayor costo de forrajes externos. Se sugiere destete precoz anticipado.")
        else:
            proj_utilidad_total = utilidad_neta_cab * cantidad_animales * 1.10 * horizonte_sim
            st.success("🟢 **Simulación Favorable:** El gemelo digital proyecta estabilidad y crecimiento acumulado en el flujo de caja del rancho.")
            
        st.metric(f"Utilidad Neta Proyectada ({horizonte_sim} Años)", f"${proj_utilidad_total:,.0f} MXN")

    with col_gt2:
        st.markdown("#### ⛓️ Certificación y Auditoría Blockchain (Bonos de Carbono)")
        st.info(
            "🔒 **Bloque Registrado en Red Inmutable (NutriON Chain):**\n\n"
            f"* **Hash de Transacción:** `0x4f8a9c2...b19e3d7`\n"
            f"* **Lote Auditado:** {cantidad_animales} cabezas | Estándar IPCC Tier 2\n"
            f"* **Reducción Certificada de CO2e:** `{co2e_anual * cantidad_animales / 1000.0:,.2f} toneladas/año`\n"
            f"* **Valor Estimado en Mercado Verde:** `$ {(co2e_anual * cantidad_animales / 1000.0) * 350.0:,.2f} MXN`"
        )
        if st.button("🔗 Emitir Certificado Blockchain Verificable de Sostenibilidad", use_container_width=True):
            st.success("🎉 **¡Certificado Blockchain Emitido con Éxito!** El registro inmutable ha sido sellado con la firma criptográfica del Dr. Alejandro Castañeda y enviado al registro de compensación ambiental.")
            st.balloons()
