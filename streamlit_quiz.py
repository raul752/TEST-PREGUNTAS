# -*- coding: utf-8 -*-
"""
Quiz IA Show - Versión Streamlit (Web App)
- Carga automática de listas desde GitHub (/LISTAS)
- Arranca automáticamente con "CLUB ATLETICO HURACAN.txt"
- Compatible con móviles
- Audio con gTTS (Google Text-to-Speech)
"""

import streamlit as st
import os
import re
import base64
from io import BytesIO
import tempfile
import requests

# ===================== TOKEN SEGURO (desde Streamlit Secrets) =====================
import openai

# Carga el token de los secrets de Streamlit (Settings → Secrets)
try:
    TOKEN = st.secrets["TOKEN"]
    openai.api_key = TOKEN
    st.success("🔐 Token cargado desde Streamlit Secrets.")
except Exception:
    TOKEN = None
    st.warning("⚠️ No se encontró TOKEN en los secrets. Algunas funciones pueden no estar disponibles.")

# ===================== CONFIGURACIÓN DE PÁGINA =====================
st.set_page_config(
    page_title="Test de Preguntas - El Fruti",
    page_icon="🍓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== CSS PERSONALIZADO =====================
st.markdown("""
    page_title="Test de Preguntas - El Fruti",
    page_icon="🍓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== CSS PERSONALIZADO =====================
st.markdown("""
<style>
    .stApp { background-color: #072022; }
    .header-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .header-title {
        font-size: 32px;
        font-weight: bold;
        color: #000000;
        margin: 0;
    }
    .header-subtitle {
        font-size: 18px;
        font-weight: bold;
        color: #ff0000;
        text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
        margin: 5px 0 0 0;
    }
    .pregunta-box {
        background-color: #0a3d62;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .pregunta-text {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
        line-height: 1.4;
    }
    .stButton > button {
        width: 100%;
        height: 100px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        margin: 10px 0;
        background-color: #0a5170;
        color: white;
        border: 3px solid #126a83;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #0d6b8b;
        transform: scale(1.02);
    }
    .resultado-box {
        background-color: #0a3d62;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin: 30px 0;
    }
    .score-text {
        font-size: 60px;
        font-weight: bold;
        color: #4CAF50;
    }
    .percentage-text {
        font-size: 32px;
        color: #ffffff;
        margin-top: 10px;
    }
    .error-box {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff5555;
    }
    .error-text {
        color: #ffffff;
        font-size: 18px;
        line-height: 1.6;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .progress-text {
        color: #ffffff;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ===================== FUNCIONES DE AUDIO =====================
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except:
    GTTS_AVAILABLE = False
    st.warning("⚠️ gTTS no disponible. El audio estará deshabilitado.")

def text_to_speech(text, lang="es", tld="com.ar"):
    if not GTTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except Exception as e:
        st.error(f"Error generando audio: {e}")
        return None

def reproducir_audio(audio_base64):
    if audio_base64:
        st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)

# ===================== CARGAR PREGUNTAS =====================
def cargar_preguntas(archivo="preguntas.txt"):
    try:
        if not os.path.exists(archivo):
            st.error(f"❌ No se encuentra el archivo: {archivo}")
            return []
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        preguntas = []
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            if re.match(r'^\d+\.', linea):
                match = re.match(r'^(\d+)\.\s*(.+)', linea)
                if match:
                    numero = int(match.group(1))
                    pregunta = match.group(2).strip()
                    opciones, respuesta_correcta = [], None
                    for letra_idx in range(4):
                        i += 1
                        if i < len(lineas):
                            linea_opcion = lineas[i].strip()
                            match_opcion = re.match(r'^([A-D])\.\s*(.+?)(\*?)$', linea_opcion)
                            if match_opcion:
                                letra = match_opcion.group(1)
                                texto_opcion = match_opcion.group(2).strip()
                                if match_opcion.group(3) == '*':
                                    respuesta_correcta = letra
                                opciones.append(texto_opcion)
                    if len(opciones) == 4:
                        if not respuesta_correcta:
                            respuesta_correcta = "A"
                        preguntas.append({
                            "numero": numero,
                            "pregunta": pregunta,
                            "opciones": opciones,
                            "respuesta_correcta": respuesta_correcta
                        })
            i += 1
        return preguntas
    except Exception as e:
        st.error(f"Error cargando preguntas: {e}")
        return []

# ===================== INICIALIZAR SESSION STATE =====================
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
    try:
        # 🔰 Cargar lista por defecto al iniciar
        default_url = "https://raw.githubusercontent.com/raul752/TEST-PREGUNTAS/main/LISTAS/CLUB%20ATLETICO%20HURACAN.txt"
        response = requests.get(default_url)
        if response.status_code == 200:
            contenido = response.text
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp_file:
                tmp_file.write(contenido)
                tmp_path = tmp_file.name
            preguntas_default = cargar_preguntas(tmp_path)
            if preguntas_default:
                st.session_state.preguntas = preguntas_default
                st.session_state.indice_actual = 0
                st.session_state.respuestas_usuario = []
                st.session_state.quiz_finalizado = False
                st.info("📘 Lista predeterminada cargada: CLUB ATLETICO HURACAN.txt")
        else:
            st.warning("⚠️ No se pudo cargar la lista predeterminada desde GitHub.")
    except Exception as e:
        st.error(f"Error cargando lista predeterminada: {e}")

if 'indice_actual' not in st.session_state:
    st.session_state.indice_actual = 0
if 'respuestas_usuario' not in st.session_state:
    st.session_state.respuestas_usuario = []
if 'quiz_finalizado' not in st.session_state:
    st.session_state.quiz_finalizado = False
if 'audio_enabled' not in st.session_state:
    st.session_state.audio_enabled = True
if 'voz_seleccionada' not in st.session_state:
    st.session_state.voz_seleccionada = {"nombre": "🇦🇷 Argentina", "lang": "es", "tld": "com.ar"}

# ===================== FUNCIONES PRINCIPALES =====================
def reiniciar_quiz():
    st.session_state.indice_actual = 0
    st.session_state.respuestas_usuario = []
    st.session_state.quiz_finalizado = False
    st.rerun()

def responder_pregunta(opcion_idx):
    q = st.session_state.preguntas[st.session_state.indice_actual]
    respuesta_usuario = chr(65 + opcion_idx)
    es_correcta = respuesta_usuario == q["respuesta_correcta"]
    st.session_state.respuestas_usuario.append({
        "numero": q["numero"],
        "pregunta": q["pregunta"],
        "opciones": q["opciones"],
        "respuesta_usuario": respuesta_usuario,
        "respuesta_correcta": q["respuesta_correcta"],
        "es_correcta": es_correcta
    })
    st.session_state.indice_actual += 1
    if st.session_state.indice_actual >= len(st.session_state.preguntas):
        st.session_state.quiz_finalizado = True
    st.rerun()

# ===================== HEADER =====================
st.markdown("""
<div class="header-container">
    <h1 class="header-title">« « « TEST DE PREGUNTAS » » »</h1>
    <p class="header-subtitle">PROGRAMADO BY DARDO 🍓</p>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.title("⚙️ Configuración")
    st.session_state.audio_enabled = st.checkbox("🔊 Habilitar Audio", value=st.session_state.audio_enabled)

    # === Cargar dinámicamente archivos desde la carpeta LISTAS de GitHub ===
    GITHUB_USER = "raul752"
    GITHUB_REPO = "TEST-PREGUNTAS"
    GITHUB_PATH = "LISTAS"

    st.subheader("🌐 Cargar desde GitHub /LISTAS")

    try:
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_PATH}"
        response = requests.get(api_url)
        response.raise_for_status()
        files_data = response.json()
        archivos_txt = [f["name"] for f in files_data if f["name"].endswith(".txt")]
    except Exception as e:
        archivos_txt = []
        st.error(f"❌ No se pudo listar archivos: {e}")

    if archivos_txt:
        archivo_seleccionado = st.selectbox("Elegí una lista de preguntas:", archivos_txt)
        if st.button("⬇️ Cargar archivo desde GitHub", use_container_width=True):
            try:
                raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{GITHUB_PATH}/{archivo_seleccionado}"
                response = requests.get(raw_url)
                response.raise_for_status()
                contenido = response.text
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp_file:
                    tmp_file.write(contenido)
                    tmp_path = tmp_file.name
                nuevas_preguntas = cargar_preguntas(tmp_path)
                if nuevas_preguntas:
                    st.session_state.preguntas = nuevas_preguntas
                    st.session_state.indice_actual = 0
                    st.session_state.respuestas_usuario = []
                    st.session_state.quiz_finalizado = False
                    st.success(f"✅ Cargadas {len(nuevas_preguntas)} preguntas desde {archivo_seleccionado}")
            except Exception as e:
                st.error(f"❌ Error cargando archivo desde GitHub: {e}")
    else:
        st.warning("⚠️ No se encontraron archivos .txt en la carpeta LISTAS")

    st.markdown("---")
    if st.button("🔄 Reiniciar Quiz", use_container_width=True):
        reiniciar_quiz()
    st.markdown("---")
    st.info(f"📊 Total preguntas: {len(st.session_state.preguntas)}")

# ===================== CONTENIDO PRINCIPAL =====================
if not st.session_state.preguntas:
    st.error("❌ No hay preguntas cargadas. Usa el panel lateral para elegir una lista de GitHub.")
    st.stop()

if not st.session_state.quiz_finalizado:
    idx = st.session_state.indice_actual
    total = len(st.session_state.preguntas)
    progreso = (idx / total) * 100
    st.markdown(f'<p class="progress-text">Progreso: {idx}/{total} preguntas</p>', unsafe_allow_html=True)
    st.progress(progreso / 100)
    q = st.session_state.preguntas[idx]
    st.markdown(f"""
    <div class="pregunta-box">
        <p class="pregunta-text">❓ Pregunta {idx + 1} de {total}</p>
        <p class="pregunta-text">{q['pregunta']}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.audio_enabled and GTTS_AVAILABLE:
        texto = f"{q['pregunta']}. " + " ".join([f"Opción {chr(65+i)}. {op}." for i, op in enumerate(q['opciones'])])
        audio_b64 = text_to_speech(texto, lang=st.session_state.voz_seleccionada['lang'], tld=st.session_state.voz_seleccionada['tld'])
        if audio_b64: reproducir_audio(audio_b64)

    st.markdown("### Selecciona tu respuesta:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"**A.** {q['opciones'][0]}", key="opt_A", use_container_width=True):
            responder_pregunta(0)
        if st.button(f"**C.** {q['opciones'][2]}", key="opt_C", use_container_width=True):
            responder_pregunta(2)
    with col2:
        if st.button(f"**B.** {q['opciones'][1]}", key="opt_B", use_container_width=True):
            responder_pregunta(1)
        if st.button(f"**D.** {q['opciones'][3]}", key="opt_D", use_container_width=True):
            responder_pregunta(3)
else:
    correctas = sum(1 for r in st.session_state.respuestas_usuario if r["es_correcta"])
    total = len(st.session_state.respuestas_usuario)
    porcentaje = int((correctas / total) * 100) if total > 0 else 0
    if porcentaje >= 90:
        eval_text, eval_color = "¡PERFECTO! 🌟", "#FFD700"
    elif porcentaje >= 70:
        eval_text, eval_color = "¡Muy bien! 👍", "#4CAF50"
    else:
        eval_text, eval_color = "Sigue practicando 📚", "#FFA500"
    st.markdown(f"""
    <div class="resultado-box">
        <h1 style="color: #FFD700; font-size: 48px;">🏆 RESULTADO FINAL</h1>
        <p class="score-text">{correctas} / {total}</p>
        <p class="percentage-text">{porcentaje}% de aciertos</p>
        <h2 style="color: {eval_color}; margin-top: 20px;">{eval_text}</h2>
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.audio_enabled and GTTS_AVAILABLE:
        texto_resultado = f"Quiz finalizado. Obtuviste {correctas} de {total}. {eval_text}"
        audio_b64 = text_to_speech(texto_resultado)
        if audio_b64: reproducir_audio(audio_b64)
    errores = [r for r in st.session_state.respuestas_usuario if not r["es_correcta"]]
    if errores:
        st.markdown("### ❌ Preguntas incorrectas:")
        for err in errores:
            iu, ic = ord(err['respuesta_usuario']) - 65, ord(err['respuesta_correcta']) - 65
            st.markdown(f"""
            <div class="error-box">
                <p class="error-text">
                    <strong>• Pregunta:</strong> {err['pregunta']}<br>
                    <strong style="color: #ff5555;">Tu respuesta:</strong> {err['respuesta_usuario']}. {err['opciones'][iu]}<br>
                    <strong style="color: #4CAF50;">Correcta:</strong> {err['respuesta_correcta']}. {err['opciones'][ic]}
                </p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🔄 Reiniciar Quiz", key="reiniciar_final", use_container_width=True):
            reiniciar_quiz()
