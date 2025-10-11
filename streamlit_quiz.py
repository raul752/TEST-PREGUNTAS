# -*- coding: utf-8 -*-
"""
Quiz IA Show - Versión Streamlit (Web App)
- Funciona en el navegador
- Sin necesidad de descargar ejecutable
- Compatible con móviles
- Audio con gTTS (Google Text-to-Speech)
"""

import streamlit as st
import os
import re
import base64
from io import BytesIO
import tempfile
import time

# ===================== CONFIGURACIÓN DE PÁGINA =====================
st.set_page_config(
    page_title="Test de Preguntas - El Fruti",
    page_icon="🍓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== CSS PERSONALIZADO =====================
st.markdown("""
<style>
    /* Fondo oscuro */
    .stApp {
        background-color: #072022;
    }
    
    /* Header personalizado */
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
    
    /* Pregunta */
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
    
    /* Botones de opciones */
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
    
    /* Resultado final */
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
    
    /* Errores */
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
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Progress bar */
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
    """Genera audio con gTTS y devuelve base64 para reproducción en el navegador"""
    if not GTTS_AVAILABLE:
        return None
    
    try:
        tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        
        # Guardar en memoria
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # Convertir a base64
        audio_base64 = base64.b64encode(fp.read()).decode()
        return audio_base64
    except Exception as e:
        st.error(f"Error generando audio: {e}")
        return None

def reproducir_audio(audio_base64):
    """Reproduce audio en el navegador usando HTML5"""
    if audio_base64:
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# ===================== CARGAR PREGUNTAS =====================
def cargar_preguntas(archivo="preguntas.txt"):
    """Lee el archivo de preguntas"""
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
                    
                    opciones = []
                    respuesta_correcta = None
                    
                    for letra_idx in range(4):
                        i += 1
                        if i < len(lineas):
                            linea_opcion = lineas[i].strip()
                            match_opcion = re.match(r'^([A-D])\.\s*(.+?)(\*?)$', linea_opcion)
                            
                            if match_opcion:
                                letra = match_opcion.group(1)
                                texto_opcion = match_opcion.group(2).strip()
                                tiene_asterisco = match_opcion.group(3) == '*'
                                
                                opciones.append(texto_opcion)
                                
                                if tiene_asterisco:
                                    respuesta_correcta = letra
                    
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
    st.session_state.preguntas = cargar_preguntas()

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
    """Reinicia el quiz"""
    st.session_state.indice_actual = 0
    st.session_state.respuestas_usuario = []
    st.session_state.quiz_finalizado = False
    st.rerun()

def responder_pregunta(opcion_idx):
    """Registra la respuesta del usuario"""
    q = st.session_state.preguntas[st.session_state.indice_actual]
    respuesta_usuario = chr(65 + opcion_idx)  # A, B, C, D
    es_correcta = respuesta_usuario == q["respuesta_correcta"]
    
    st.session_state.respuestas_usuario.append({
        "numero": q["numero"],
        "pregunta": q["pregunta"],
        "opciones": q["opciones"],
        "respuesta_usuario": respuesta_usuario,
        "respuesta_correcta": q["respuesta_correcta"],
        "es_correcta": es_correcta
    })
    
    # Avanzar a la siguiente pregunta
    st.session_state.indice_actual += 1
    
    # Si llegó al final, marcar como finalizado
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

# ===================== SIDEBAR (CONFIGURACIÓN) =====================
with st.sidebar:
    st.title("⚙️ Configuración")
    
    # Control de audio
    st.session_state.audio_enabled = st.checkbox("🔊 Habilitar Audio", value=st.session_state.audio_enabled)
    
    # Selector de archivo de preguntas
    st.subheader("📄 Archivo de Preguntas")
    archivo_uploaded = st.file_uploader("Subir archivo .txt", type=['txt'])
    
    if archivo_uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tmp_file:
            tmp_file.write(archivo_uploaded.getvalue().decode('utf-8'))
            tmp_path = tmp_file.name
        
        nuevas_preguntas = cargar_preguntas(tmp_path)
        
        if nuevas_preguntas:
            st.session_state.preguntas = nuevas_preguntas
            st.session_state.indice_actual = 0
            st.session_state.respuestas_usuario = []
            st.session_state.quiz_finalizado = False
            st.success(f"✅ Cargadas {len(nuevas_preguntas)} preguntas")
    
    # Botón reiniciar
    if st.button("🔄 Reiniciar Quiz", use_container_width=True):
        reiniciar_quiz()
    
    # Info
    st.markdown("---")
    st.info(f"📊 Total preguntas: {len(st.session_state.preguntas)}")

# ===================== CONTENIDO PRINCIPAL =====================
if not st.session_state.preguntas:
    st.error("❌ No hay preguntas cargadas. Por favor sube un archivo de preguntas.")
    st.stop()

# ----------------------- QUIZ EN PROGRESO -----------------------
if not st.session_state.quiz_finalizado:
    idx = st.session_state.indice_actual
    total = len(st.session_state.preguntas)
    
    # Barra de progreso
    progreso = (idx / total) * 100
    st.markdown(f'<p class="progress-text">Progreso: {idx}/{total} preguntas</p>', unsafe_allow_html=True)
    st.progress(progreso / 100)
    
    # Pregunta actual
    q = st.session_state.preguntas[idx]
    
    st.markdown(f"""
    <div class="pregunta-box">
        <p class="pregunta-text">❓ Pregunta {idx + 1} de {total}</p>
        <p class="pregunta-text">{q['pregunta']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio de la pregunta
    if st.session_state.audio_enabled and GTTS_AVAILABLE:
        texto_completo = f"{q['pregunta']}. "
        for i, opcion in enumerate(q['opciones']):
            letra = chr(65 + i)
            texto_completo += f"Opción {letra}. {opcion}. "
        
        audio_b64 = text_to_speech(texto_completo, 
                                   lang=st.session_state.voz_seleccionada['lang'],
                                   tld=st.session_state.voz_seleccionada['tld'])
        if audio_b64:
            reproducir_audio(audio_b64)
    
    # Opciones de respuesta
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

# ----------------------- RESULTADOS FINALES -----------------------
else:
    correctas = sum(1 for r in st.session_state.respuestas_usuario if r["es_correcta"])
    total = len(st.session_state.respuestas_usuario)
    porcentaje = int((correctas / total) * 100) if total > 0 else 0
    
    # Evaluación
    if porcentaje >= 90:
        eval_text = "¡PERFECTO! 🌟"
        eval_color = "#FFD700"
    elif porcentaje >= 70:
        eval_text = "¡Muy bien! 👍"
        eval_color = "#4CAF50"
    else:
        eval_text = "Sigue practicando 📚"
        eval_color = "#FFA500"
    
    # Mostrar resultado
    st.markdown(f"""
    <div class="resultado-box">
        <h1 style="color: #FFD700; font-size: 48px;">🏆 RESULTADO FINAL</h1>
        <p class="score-text">{correctas} / {total}</p>
        <p class="percentage-text">{porcentaje}% de aciertos</p>
        <h2 style="color: {eval_color}; margin-top: 20px;">{eval_text}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio del resultado
    if st.session_state.audio_enabled and GTTS_AVAILABLE:
        texto_resultado = f"Quiz finalizado. Obtuviste {correctas} respuestas correctas de {total}. {eval_text}"
        audio_b64 = text_to_speech(texto_resultado,
                                   lang=st.session_state.voz_seleccionada['lang'],
                                   tld=st.session_state.voz_seleccionada['tld'])
        if audio_b64:
            reproducir_audio(audio_b64)
    
    # Mostrar errores
    errores = [r for r in st.session_state.respuestas_usuario if not r["es_correcta"]]
    
    if errores:
        st.markdown("### ❌ Preguntas respondidas incorrectamente:")
        
        for err in errores:
            idx_usuario = ord(err['respuesta_usuario']) - 65
            idx_correcta = ord(err['respuesta_correcta']) - 65
            
            st.markdown(f"""
            <div class="error-box">
                <p class="error-text">
                    <strong>• Pregunta:</strong> {err['pregunta']}<br>
                    <strong style="color: #ff5555;">Tu respuesta:</strong> {err['respuesta_usuario']}. {err['opciones'][idx_usuario]}<br>
                    <strong style="color: #4CAF50;">Respuesta correcta:</strong> {err['respuesta_correcta']}. {err['opciones'][idx_correcta]}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Botón reiniciar
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Reiniciar Quiz", key="reiniciar_final", use_container_width=True):
            reiniciar_quiz()