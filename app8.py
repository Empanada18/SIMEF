import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análisis de Mecanismos de Falla", layout="wide")

import base64

# Función para obtener el base64 de la imagen
def get_base64(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Cargar logo
img_logo = get_base64("evo.png")
# ==========================================================================================
# BASE COMPLETA DE PARÁMETROS CON OBSERVACIONES
# ==========================================================================================

PARAMETROS = {
    "agua_libre": {"mecanismo": "M1", "tipo": "num", "critico": lambda v: v >= 2, "critico_severo": None,
                   "obs": "Agua en contacto con acero activa corrosión general."},
    "ph": {"mecanismo": "M1", "tipo": "num", "critico": lambda v: v <= 6, "critico_severo": None,
           "obs": "Acidez favorece corrosión."},
    "pco2": {"mecanismo": "M1", "tipo": "num", "critico": lambda v: v >= 0.3, "critico_severo": lambda v: v >= 1,
             "obs": "Corrosión dulce."},
    "oxigeno_disuelto": {"mecanismo": "M1", "tipo": "num", "critico": lambda v: v > 50, "critico_severo": None,
                         "obs": "Muy corrosivo en sistemas 'deaerated'."},
    "temperatura_m1": {"mecanismo": "M1", "tipo": "num", "critico": lambda v: v >= 40, "critico_severo": None,
                       "obs": "Aumenta la tasa de corrosión."},
    "corrosion_rate": {"mecanismo": "M1", "tipo": "num", "critico": lambda v: v >= 0.10,
                       "critico_severo": lambda v: v >= 0.30, "obs": "Usa cupones/UT."},

    "deadlegs": {"mecanismo": "M2", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                 "obs": "Zonas sin barrido hidráulico."},
    "interfaz_liquido_gas": {"mecanismo": "M2", "tipo": "bool", "critico": lambda v: v is True,
                             "critico_severo": None, "obs": "Potencia pitting interno."},
    "cloruros": {"mecanismo": "M2", "tipo": "num", "critico": lambda v: v >= 50, "critico_severo": None,
                 "obs": "Pitting en inox o CS recubierto."},
    "velocidad_baja": {"mecanismo": "M2", "tipo": "num", "critico": lambda v: v <= 0.3, "critico_severo": None,
                       "obs": "Permite acumulación."},
    "severidad_pit": {"mecanismo": "M2", "tipo": "num", "critico": lambda v: v <= 80, "critico_severo": None,
                      "obs": "Identifica pitting significativo."},

    "velocidad_liq_sol_m3": {"mecanismo": "M3", "tipo": "num", "critico": lambda v: v >= 3, "critico_severo": None,
                             "obs": "Líquidos con sólidos ≥3 m/s; gas ≥15 m/s."},
    "velocidad_m3_gas": {"mecanismo": "M3", "tipo": "num", "critico": lambda v: v >= 15, "critico_severo": None,
                         "obs": "Líquidos con sólidos ≥3 m/s; gas ≥15 m/s."},
    "solidos": {"mecanismo": "M3", "tipo": "num", "critico": lambda v: v >= 0.5, "critico_severo": None,
                "obs": "O concentración ≥ 50–100 mg/L."},
    "geometria_agresiva": {"mecanismo": "M3", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                           "obs": "Codo/tee/restricción."},
    "patron_visual": {"mecanismo": "M3", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                      "obs": "Perfil erosivo confirmado."},

    "aislamiento": {"mecanismo": "M4", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                    "obs": "Requisito de CUI."},
    "rango_temp_cui": {"mecanismo": "M4", "tipo": "num", "critico": lambda v: v >= 40, "critico_severo": None,
                       "obs": "Según API 583."},
    "dano_jacket": {"mecanismo": "M4", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                    "obs": "Ingreso de agua."},
    "ambiente_humedo": {"mecanismo": "M4", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                        "obs": "Lluvia, lavado, ambientes húmedos."},
    "soportes_humedad": {"mecanismo": "M4", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                         "obs": "Evidencia visual."},

    "depositos_internos": {"mecanismo": "M5", "tipo": "num", "critico": lambda v: v >= 1, "critico_severo": None,
                           "obs": "Incrustación visible."},
    "velocidad_baja_m5": {"mecanismo": "M5", "tipo": "num", "critico": lambda v: v <= 0.3, "critico_severo": None,
                          "obs": "Bajo barrido hidráulico."},
    "microbiologia": {"mecanismo": "M5", "tipo": "num", "critico": lambda v: v >= 1000, "critico_severo": None,
                      "obs": "SRB u otros microorganismos."},
    "fluidos_nutrientes": {"mecanismo": "M5", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                           "obs": "Agua sucia o hidrocarburos pesados."},
    "pitting_bajo_depositos": {"mecanismo": "M5", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                               "obs": "Confirmación visual."},

    "t_externa": {"mecanismo": "M12", "tipo": "num", "critico": lambda v: v < 0, "critico_severo": None,
                  "obs": "Temperatura externa bajo freezing."},
    "operacion_detenida": {"mecanismo": "M12", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                           "obs": "Línea sin flujo."},
    "sin_purgas": {"mecanismo": "M12", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                   "obs": "Agua atrapada."},
    "sin_tracing": {"mecanismo": "M12", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                    "obs": "Riesgo de congelamiento."},
    "patron_rotura": {"mecanismo": "M12", "tipo": "bool", "critico": lambda v: v is True, "critico_severo": None,
                      "obs": "Grieta circunferencial típica."},
}

# ==========================================================================================
# SIDEBAR
# ==========================================================================================

# Barra lateral
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center">
            <img src="data:image/png;base64,{img_logo}" width="180">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("⚙️ Panel") 
    vista = st.radio("Selecciona vista", ["Calculadora", "Tabla / Visual"])
    


# ==========================================================================================
# VISTA: CALCULADORA
# ==========================================================================================
if vista == "Calculadora":
    st.title("📊  Plataforma Inteligente de Análisis de Causa Raíz - Falla en sistemas de Tuberías")
    st.write("Selecciona los parámetros que deseas ingresar.")

    parametros_seleccionados = st.multiselect(
        "Selecciona parámetros a evaluar",
        list(PARAMETROS.keys())
    )

    valores = {}

    for p in parametros_seleccionados:
        info = PARAMETROS[p]
        st.subheader(f"🔸 {p} — ({info['mecanismo']})")
        st.caption(f"**Observación:** {info['obs']}")

        if info["tipo"] == "num":
            valores[p] = st.number_input(f"Ingrese valor numérico para {p}", value=0.0)
        elif info["tipo"] == "bool":
            valores[p] = st.radio(f"Seleccione valor para {p}", [False, True])

    if st.button("Calcular"):
        st.header("📌 Resultados")

        activados = {m: 0 for m in ["M1", "M2", "M3", "M4", "M5", "M12"]}
        severidad = {m: 0 for m in activados}
        drivers_activados = {m: [] for m in activados}

        # Evaluación
        for p, v in valores.items():
            info = PARAMETROS[p]
            mec = info["mecanismo"]

            if info["critico"](v):
                activados[mec] += 1
                severidad[mec] = max(severidad[mec], 1)
                drivers_activados[mec].append(p)

            if info["critico_severo"] and info["critico_severo"](v):
                activados[mec] += 1
                severidad[mec] = max(severidad[mec], 2)
                if p not in drivers_activados[mec]:
                    drivers_activados[mec].append(p)

        # Tabla y gráficos
        st.subheader("📉 Visualización Gráfica")
        df = pd.DataFrame({
            "Mecanismo": activados.keys(),
            "Parámetros Activados": activados.values(),
            "Severidad": severidad.values()
        })

        fig1, ax1 = plt.subplots()
        ax1.bar(df["Mecanismo"], df["Parámetros Activados"])
        ax1.set_title("Cantidad de Parámetros Activados por Mecanismo")
        ax1.set_ylabel("Cantidad")
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        ax2.bar(df["Mecanismo"], df["Severidad"])
        ax2.set_title("Severidad por Mecanismo (0=Normal, 1=Activado, 2=Severo)")
        ax2.set_ylabel("Nivel de Severidad")
        st.pyplot(fig2)

        # Mecanismo predominante
        mecanismo_predominante = df.sort_values("Parámetros Activados", ascending=False).iloc[0]["Mecanismo"]
        st.success(f"🔺 Mecanismo predominante: **{mecanismo_predominante}**")

        # Recomendaciones
        st.subheader("📘 Recomendaciones Automáticas")
        for m, sev in severidad.items():
            drivers = ", ".join(drivers_activados[m])
            if sev == 0:
                st.info(f"✅ **{m}: Normal** — No requiere intervención.")
            elif sev == 1:
                st.warning(f"⚠️ **{m}: Activado** — Se recomienda evaluación detallada y monitoreo. "
                           f"Drivers activados: {drivers}")
            elif sev == 2:
                st.error(f"🔥 **{m}: Severo** — Atención inmediata requerida. Revisar integridad rápidamente. "
                         f"Drivers activados: {drivers}")

# ==========================================================================================
# VISTA: TABLA / VISUAL
# ==========================================================================================
elif vista == "Tabla / Visual":
    st.title("📚 Tabla de Mecanismos y Parámetros")
    
    # Datos por mecanismo (ejemplo, puedes agregar todos)
    datos_mecanismos = {
        "M1": [
            {"Driver":"M1-D1","Parámetro":"% Agua libre (φ_water)","Tipo":"numérico (%)","Criterio":"φ_water ≥ 2%","Observaciones":"Agua en contacto con acero activa corrosión general."},
            {"Driver":"M1-D2","Parámetro":"pH","Tipo":"numérico","Criterio":"pH ≤ 6","Observaciones":"Acidez favorece corrosión."},
            {"Driver":"M1-D3","Parámetro":"pCO₂","Tipo":"numérico (bar)","Criterio":"≥ 0.3 bar → activo; ≥ 1 bar → severo","Observaciones":"Corrosión dulce."},
            {"Driver":"M1-D4","Parámetro":"Oxígeno disuelto","Tipo":"numérico (ppb)","Criterio":"> 50 ppb en sistemas deaerated","Observaciones":"Muy corrosivo."},
            {"Driver":"M1-D5","Parámetro":"Temperatura","Tipo":"numérico (°C)","Criterio":"T ≥ 40°C","Observaciones":"Aumenta la tasa de corrosión."},
            {"Driver":"M1-D6","Parámetro":"Corrosion rate histórica","Tipo":"numérico (mm/año)","Criterio":"≥ 0.10 mm/año → activo; ≥ 0.30 → severo","Observaciones":"Usa cupones/UT."},
        ],
        "M2": [
            {"Driver":"M2-D1","Parámetro":"Deadlegs / estancamiento","Tipo":"boolean","Criterio":"= TRUE","Observaciones":"Zonas sin barrido hidráulico."},
            {"Driver":"M2-D2","Parámetro":"Interfaz líquido-gas","Tipo":"boolean","Criterio":"= TRUE","Observaciones":"Potencia pitting interno."},
            {"Driver":"M2-D3","Parámetro":"Cloruros","Tipo":"numérico (ppm)","Criterio":"≥ 50–100 ppm","Observaciones":"Pitting en inox o CS recubierto."},
            {"Driver":"M2-D4","Parámetro":"Velocidad baja","Tipo":"numérico (m/s)","Criterio":"≤ 0.3–0.5 m/s","Observaciones":"Permite acumulación."},
            {"Driver":"M2-D5","Parámetro":"Severidad del pit","Tipo":"geométrico","Criterio":"t_min ≤ 80% del espesor promedio local","Observaciones":"Identifica pitting significativo."},
        ],
        "M3": [
            {"Driver":"M3-D1","Parámetro":"Velocidad","Tipo":"numérico (m/s)","Criterio":"líquidos con sólidos ≥3; gas ≥15","Observaciones":"Ajustable por proceso"},
            {"Driver":"M3-D2","Parámetro":"Sólidos en flujo","Tipo":"numérico (%)","Criterio":"≥ 0.5–1%","Observaciones":"O concentración 50–100 mg/L"},
            {"Driver":"M3-D3","Parámetro":"Geometría agresiva","Tipo":"boolean","Criterio":"TRUE si codo/tee/restricción → activa","Observaciones":"Zonas turbulentas"},
            {"Driver":"M3-D4","Parámetro":"Patrón visual/UT","Tipo":"boolean","Criterio":"TRUE si perfil erosivo","Observaciones":"Evidencia confirmatoria"},
        ],

        "M4": [
            {"Driver":"M4-D1","Parámetro":"Aislamiento","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Requisito de CUI"},
            {"Driver":"M4-D2","Parámetro":"Rango temperatura CUI","Tipo":"numérico (°C)","Criterio":"Según API 583 – susceptible","Observaciones":"Referencia API 583"},
            {"Driver":"M4-D3","Parámetro":"Daño en jacket","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Ingreso de agua"},
            {"Driver":"M4-D4","Parámetro":"Ambiente húmedo","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Lluvia, lavado, procesos húmedos"},
            {"Driver":"M4-D5","Parámetro":"Soportes atrapahumedad","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Evidencia visual"},
        ],

        "M5": [
            {"Driver":"M5-D1","Parámetro":"Depósitos internos","Tipo":"geométrico","Criterio":"≥ 1–2 mm","Observaciones":"Incrustación visible"},
            {"Driver":"M5-D2","Parámetro":"Velocidad baja","Tipo":"numérico (m/s)","Criterio":"≤ 0.3–0.5 m/s","Observaciones":"Bajo barrido"},
            {"Driver":"M5-D3","Parámetro":"Microbiología","Tipo":"numérico (CFU/mL)","Criterio":"≥ 10³ CFU/mL","Observaciones":"SRB u otros"},
            {"Driver":"M5-D4","Parámetro":"Fluido con nutrientes","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Agua sucia, hidrocarburos pesados"},
            {"Driver":"M5-D5","Parámetro":"Pitting bajo depósitos","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Confirmación"},
        ],

        "M12": [
            {"Driver":"M12-D1","Parámetro":"T externa","Tipo":"numérico (°C)","Criterio":"T_amb < T_freezing fluido","Observaciones":"Se activa riesgo"},
            {"Driver":"M12-D2","Parámetro":"Operación detenida","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Línea sin flujo"},
            {"Driver":"M12-D3","Parámetro":"Sin purgas","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Agua atrapada"},
            {"Driver":"M12-D4","Parámetro":"Sin tracing/aislamiento","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Congelamiento"},
            {"Driver":"M12-D5","Parámetro":"Patrón de rotura","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Grieta circunferencial típica"},
        ],

    }
    
    for m, datos in datos_mecanismos.items():
        with st.expander(f"{m} - Parámetros"):
            st.table(pd.DataFrame(datos))


