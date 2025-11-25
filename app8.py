import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import graphviz  

st.set_page_config(page_title="Análisis de Mecanismos de Falla", layout="wide")

# ==========================================================================================
# FUNCIONES UTILITARIAS
# ==========================================================================================

def get_base64(img_path):
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return "" # Retorna vacío si no encuentra la imagen para que no falle

# Cargar logo (Asegúrate de tener la imagen o el código no mostrará el logo)
img_logo = get_base64("evo.png")

# ==========================================================================================
# BASE COMPLETA DE PARÁMETROS
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

with st.sidebar:
    if img_logo:
        st.markdown(
            f"""
            <div style="text-align:center">
                <img src="data:image/png;base64,{img_logo}" width="180">
            </div>
            """,
            unsafe_allow_html=True
        )
    st.title("⚙️ Panel") 
    vista = st.radio("Selecciona vista", ["Calculadora", "Tabla / Visual", "Mapa Conceptual", "Árbol de Fallas (Master)"])


# ==========================================================================================
# VISTA: CALCULADORA
# ==========================================================================================
if vista == "Calculadora":
    st.title("📊 Plataforma Inteligente de Análisis de Causa Raíz - Falla en sistemas de Tuberías")
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
            valores[p] = st.number_input(f"Ingrese valor para {p}", value=0.0)
        elif info["tipo"] == "bool":
            valores[p] = st.radio(f"Seleccione valor para {p}", [False, True])

    if st.button("Calcular"):
        # ---------------------------------------------------------
        # GUARDAR EN SESSION_STATE (Corrección clave)
        # ---------------------------------------------------------
        st.session_state["valores"] = valores
        
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

        # Gráficos
        st.subheader("📉 Visualización Gráfica")
        df = pd.DataFrame({
            "Mecanismo": activados.keys(),
            "Parámetros Activados": activados.values(),
            "Severidad": severidad.values()
        })

        col1, col2 = st.columns(2)
        with col1:
            fig1, ax1 = plt.subplots()
            ax1.bar(df["Mecanismo"], df["Parámetros Activados"], color='skyblue')
            ax1.set_title("Parámetros Activados")
            st.pyplot(fig1)

        with col2:
            fig2, ax2 = plt.subplots()
            colores_sev = ['green' if s == 0 else 'orange' if s == 1 else 'red' for s in df["Severidad"]]
            ax2.bar(df["Mecanismo"], df["Severidad"], color=colores_sev)
            ax2.set_title("Nivel de Severidad")
            st.pyplot(fig2)

        # Recomendaciones
        st.subheader("📘 Estado General")
        for m, sev in severidad.items():
            drivers = ", ".join(drivers_activados[m])
            if sev == 0:
                st.info(f"✅ **{m}: Normal**")
            elif sev == 1:
                st.warning(f"⚠️ **{m}: Alerta** — Drivers: {drivers}")
            elif sev == 2:
                st.error(f"🔥 **{m}: Severo** — Drivers: {drivers}")

# ==========================================================================================
# VISTA: TABLA / VISUAL
# ==========================================================================================
elif vista == "Tabla / Visual":
    st.title("📚 Tabla de Mecanismos y Parámetros")
    
    # Datos resumidos para el ejemplo
    datos_mecanismos = {
        "M1": [ {"Driver":"M1-D1","Parámetro":"% Agua libre (φ_water)","Tipo":"numérico (%)","Criterio":"φ_water ≥ 2%","Observaciones":"Agua en contacto con acero activa corrosión general."}, {"Driver":"M1-D2","Parámetro":"pH","Tipo":"numérico","Criterio":"pH ≤ 6","Observaciones":"Acidez favorece corrosión."}, {"Driver":"M1-D3","Parámetro":"pCO₂","Tipo":"numérico (bar)","Criterio":"≥ 0.3 bar → activo; ≥ 1 bar → severo","Observaciones":"Corrosión dulce."}, {"Driver":"M1-D4","Parámetro":"Oxígeno disuelto","Tipo":"numérico (ppb)","Criterio":"> 50 ppb en sistemas deaerated","Observaciones":"Muy corrosivo."}, {"Driver":"M1-D5","Parámetro":"Temperatura","Tipo":"numérico (°C)","Criterio":"T ≥ 40°C","Observaciones":"Aumenta la tasa de corrosión."}, {"Driver":"M1-D6","Parámetro":"Corrosion rate histórica","Tipo":"numérico (mm/año)","Criterio":"≥ 0.10 mm/año → activo; ≥ 0.30 → severo","Observaciones":"Usa cupones/UT."}, ],
        "M2": [ {"Driver":"M2-D1","Parámetro":"Deadlegs / estancamiento","Tipo":"boolean","Criterio":"= TRUE","Observaciones":"Zonas sin barrido hidráulico."}, {"Driver":"M2-D2","Parámetro":"Interfaz líquido-gas","Tipo":"boolean","Criterio":"= TRUE","Observaciones":"Potencia pitting interno."}, {"Driver":"M2-D3","Parámetro":"Cloruros","Tipo":"numérico (ppm)","Criterio":"≥ 50–100 ppm","Observaciones":"Pitting en inox o CS recubierto."}, {"Driver":"M2-D4","Parámetro":"Velocidad baja","Tipo":"numérico (m/s)","Criterio":"≤ 0.3-0.5 m/s","Observaciones":"Permite acumulación."}, {"Driver":"M2-D5","Parámetro":"Severidad del pit","Tipo":"geométrico","Criterio":"t_min ≤ 80% del espesor promedio local","Observaciones":"Identifica pitting significativo."}, ],
        "M3": [ {"Driver":"M3-D1","Parámetro":"Velocidad","Tipo":"numérico (m/s)","Criterio":"líquidos con sólidos ≥3; gas ≥15","Observaciones":"Ajustable por proceso"}, {"Driver":"M3-D2","Parámetro":"Sólidos en flujo","Tipo":"numérico (%)","Criterio":"≥ 0.5-1%","Observaciones":"O concentración 50-100 mg/L"}, {"Driver":"M3-D3","Parámetro":"Geometría agresiva","Tipo":"boolean","Criterio":"TRUE si codo/tee/restricción → activa","Observaciones":"Zonas turbulentas"}, {"Driver":"M3-D4","Parámetro":"Patrón visual/UT","Tipo":"boolean","Criterio":"TRUE si perfil erosivo","Observaciones":"Evidencia confirmatoria"}, ],
        "M4": [ {"Driver":"M4-D1","Parámetro":"Aislamiento","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Requisito de CUI"}, {"Driver":"M4-D2","Parámetro":"Rango temperatura CUI","Tipo":"numérico (°C)","Criterio":"Según API 583 – susceptible","Observaciones":"Referencia API 583"}, {"Driver":"M4-D3","Parámetro":"Daño en jacket","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Ingreso de agua"}, {"Driver":"M4-D4","Parámetro":"Ambiente húmedo","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Lluvia, lavado, procesos húmedos"}, {"Driver":"M4-D5","Parámetro":"Soportes atrapahumedad","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Evidencia visual"}, ],
        "M5": [ {"Driver":"M5-D1","Parámetro":"Depósitos internos","Tipo":"geométrico","Criterio":"≥ 1-2 mm","Observaciones":"Incrustación visible"}, {"Driver":"M5-D2","Parámetro":"Velocidad baja","Tipo":"numérico (m/s)","Criterio":"≤ 0.3-0.5 m/s","Observaciones":"Bajo barrido"}, {"Driver":"M5-D3","Parámetro":"Microbiología","Tipo":"numérico (CFU/mL)","Criterio":"≥ 10³ CFU/mL","Observaciones":"SRB u otros"}, {"Driver":"M5-D4","Parámetro":"Fluido con nutrientes","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Agua sucia, hidrocarburos pesados"}, {"Driver":"M5-D5","Parámetro":"Pitting bajo depósitos","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Confirmación"}, ],
        "M12": [ {"Driver":"M12-D1","Parámetro":"T externa","Tipo":"numérico (°C)","Criterio":"T_amb < T_freezing fluido","Observaciones":"Se activa riesgo"}, {"Driver":"M12-D2","Parámetro":"Operación detenida","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Línea sin flujo"}, {"Driver":"M12-D3","Parámetro":"Sin purgas","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Agua atrapada"}, {"Driver":"M12-D4","Parámetro":"Sin tracing/aislamiento","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Congelamiento"}, {"Driver":"M12-D5","Parámetro":"Patrón de rotura","Tipo":"boolean","Criterio":"TRUE","Observaciones":"Grieta circunferencial típica"}, ],
    }
    
    for m, datos in datos_mecanismos.items():
        with st.expander(f"{m}"):
            st.table(pd.DataFrame(datos))

# ==========================================================================================
# VISTA: MAPA CONCEPTUAL (CORREGIDA)
# ==========================================================================================
elif vista == "Mapa Conceptual":
    st.title("📌 Mapa Conceptual de la Falla F1")

    # 1. Validación de Session State
    if "valores" not in st.session_state or len(st.session_state["valores"]) == 0:
        st.warning("⚠️ Primero ingresa valores en la vista *Calculadora* y presiona 'Calcular' para generar el mapa.")
        st.stop()

    st.subheader("Árbol de Influencia de Parámetros")
    
    # 2. Crear Grafo
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB') 
    
    # Nodo Central
    graph.node('F1', 'FALLA POTENCIAL', shape='doubleoctagon', style='filled', fillcolor='#e0e0e0', fontsize='20')

    # 3. Lógica integrada para colorear nodos
    valores_guardados = st.session_state["valores"]
    
    for parametro, valor in valores_guardados.items():
        # Recuperar reglas del diccionario global PARAMETROS
        reglas = PARAMETROS.get(parametro)
        
        # Determinar estado y color
        estado_texto = "Normal"
        color_fondo = "#ccffcc" # Verde claro (Safe)

        if reglas:
            # Chequear Crítico Severo
            if reglas["critico_severo"] and reglas["critico_severo"](valor):
                estado_texto = "CRÍTICO"
                color_fondo = "#ffcccc" # Rojo claro
            # Chequear Crítico Normal (Alerta)
            elif reglas["critico"](valor):
                estado_texto = "ALERTA"
                color_fondo = "#fff4cc" # Amarillo claro
        
        # Etiqueta del nodo
        label_nodo = f"{parametro}\nVal: {valor}\n[{estado_texto}]"
        
        # Crear nodo y arista
        graph.node(parametro, label_nodo, shape='box', style='filled', fillcolor=color_fondo)
        
        # Conectar al mecanismo correspondiente o directo a la Falla
        mecanismo = reglas["mecanismo"] if reglas else "General"
        
        # Opcional: Crear nodos intermedios por mecanismo para agrupar
        # graph.node(mecanismo, mecanismo, shape='ellipse')
        # graph.edge(mecanismo, 'F1')
        # graph.edge(parametro, mecanismo)
        
        # Conexión directa simple
        graph.edge('F1', parametro, label=mecanismo)

    st.graphviz_chart(graph, use_container_width=True)
    
# ==========================================================================================
# VISTA: ÁRBOL DE FALLAS (MASTER) - ESTRUCTURA COMPLETA
# ==========================================================================================
elif vista == "Árbol de Fallas (Master)":
    st.title("🌳 Árbol Estructural Completo de Falla F1")
    st.markdown("Visualización de **todos** los mecanismos y parámetros configurados en el sistema.")

    import graphviz

    # Configuración del Grafo
    master_graph = graphviz.Digraph()
    # 'LR' (Left to Right) se ve mejor para árboles grandes que 'TB' (Top to Bottom)
    master_graph.attr(rankdir='LR') 
    master_graph.attr('node', shape='box', style='filled', fontname="Helvetica")

    # 1. Nodo Raíz (La Falla Principal)
    master_graph.node('ROOT', 'FALLA F1\n(Integridad)', shape='doubleoctagon', fillcolor='#2c3e50', fontcolor='white', fontsize='16')

    # 2. Definir los Mecanismos (Nivel 1)
    # Creamos un diccionario auxiliar para dar nombres bonitos a los mecanismos
    nombres_mecanismos = {
        "M1": "Corrosión General\n(Química)",
        "M2": "Corrosión Localizada\n(Pitting/Estancamiento)",
        "M3": "Erosión / Mecánica\n(Velocidad)",
        "M4": "CUI / Externo\n(Aislamiento)",
        "M5": "MIC / Depósitos\n(Biológico)",
        "M12": "Falla Física\n(Frío/Rotura)"
    }

    # 3. Construir la estructura iterando sobre PARAMETROS
    
    # Primero creamos los nodos de Mecanismos para asegurar el orden
    for codigo_mec, nombre_desc in nombres_mecanismos.items():
        # Nodo de Mecanismo (Color Azulado)
        master_graph.node(codigo_mec, f"🛡️ {codigo_mec}\n{nombre_desc}", shape='ellipse', fillcolor='#d6eaf8', fontsize='12')
        # Conectar Raíz -> Mecanismo
        master_graph.edge('ROOT', codigo_mec, penwidth='2')

    # Ahora buscamos los parámetros (Hijos) en tu base de datos
    for param_key, data in PARAMETROS.items():
        mec_padre = data['mecanismo']
        
        # Formatear el nombre del parámetro para que se lea bien (quitar guiones bajos)
        nombre_visible = param_key.replace('_', ' ').capitalize()
        
        # Añadir info extra en el nodo (opcional)
        info_extra = ""
        if data['tipo'] == 'bool':
            info_extra = "\n(Si/No)"
        elif data['tipo'] == 'num':
            info_extra = "\n(Numérico)"

        label_nodo = f"{nombre_visible}{info_extra}"
        
        # Nodo Parámetro (Color Blanco/Gris claro)
        master_graph.node(param_key, label_nodo, fillcolor='white', fontsize='10', color='#aaaaaa')
        
        # Conectar Mecanismo -> Parámetro
        if mec_padre in nombres_mecanismos:
            master_graph.edge(mec_padre, param_key, color='#aaaaaa')
        else:
            # Por si tienes un mecanismo en PARAMETROS que no definimos en nombres_mecanismos
            master_graph.node(mec_padre, mec_padre, shape='ellipse', fillcolor='#d6eaf8')
            master_graph.edge('ROOT', mec_padre)
            master_graph.edge(mec_padre, param_key)

    # Mostrar el gráfico ocupando todo el ancho
    st.graphviz_chart(master_graph, width="stretch")



