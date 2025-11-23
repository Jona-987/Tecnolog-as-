import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2

def procesar_imagen_mejorado(imagen, n_puntos, area_rectangulo_real):
    """Versión mejorada para fotos reales"""
    
    # Convertir a array y procesar
    img_array = np.array(imagen)
    
    # Convertir a escala de grises
    if len(img_array.shape) == 3:
        img_gris = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        img_gris = img_array
    
    # MEJORA: Usar threshold adaptativo (mejor para fotos con iluminación irregular)
    img_bin = cv2.adaptiveThreshold(
        img_gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # MEJORA: Operaciones morfológicas para limpiar ruido
    kernel = np.ones((3,3), np.uint8)
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel)
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_CLOSE, kernel)
    
    # Dimensiones
    h, w = img_bin.shape
    
    # Generar puntos aleatorios
    puntos_x = np.random.randint(0, w, n_puntos)
    puntos_y = np.random.randint(0, h, n_puntos)
    
    # Contar puntos dentro
    puntos_dentro = np.sum(img_bin[puntos_y, puntos_x] == 255)
    
    # Calcular área
    proporcion = puntos_dentro / n_puntos
    area_aprox = proporcion * area_rectangulo_real
    
    return area_aprox, puntos_dentro, img_bin, puntos_x, puntos_y

# INTERFAZ MEJORADA SIN PLANTA
st.set_page_config(
    page_title="Calculadora de Áreas - Método Monte Carlo", 
    layout="wide",
    page_icon="📐"  # Icono de regla en lugar de planta
)

st.title("📐 Calculadora de Áreas - Método Monte Carlo")
st.markdown("### ¡Calcula áreas de figuras irregulares con probabilidad!")

# Sidebar
st.sidebar.header("⚙️ Configuración")

uploaded_file = st.sidebar.file_uploader(
    "Sube tu imagen:", 
    type=['png', 'jpg', 'jpeg'],
    help="💡 Consejo: Usa fondos contrastantes y buena iluminación"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Imagen Original")
        st.image(image, use_column_width=True)
    
    # Parámetros mejorados
    st.sidebar.subheader("📊 Parámetros de Cálculo")
    area_ref = st.sidebar.number_input(
        "Área de referencia (cm²):", 
        min_value=0.1, 
        value=100.0,
        help="Área total del rectángulo que contiene tu figura en la realidad"
    )
    
    n_puntos = st.sidebar.select_slider(
        "Número de puntos:", 
        options=[500, 1000, 2000, 5000, 10000],
        value=5000
    )
    
    if st.sidebar.button("🎯 Calcular Área", type="primary"):
        with st.spinner("Procesando imagen y lanzando puntos aleatorios..."):
            area_calculada, puntos_dentro, img_procesada, px, py = procesar_imagen_mejorado(
                image, n_puntos, area_ref
            )
        
        with col2:
            st.subheader("📈 Resultados")
            
            # Mostrar imagen procesada
            st.image(img_procesada, caption="Imagen procesada para detección", use_column_width=True)
            
            # Resultados
            st.success(f"**📏 Área calculada: {area_calculada:.2f} cm²**")
            st.info(f"🎯 Puntos dentro de la figura: {puntos_dentro} de {n_puntos} ({(puntos_dentro/n_puntos)*100:.1f}%)")
            
            # Gráfico de convergencia
            st.subheader("📊 Evolución de la Estimación")
            iteraciones = np.linspace(100, n_puntos, 20, dtype=int)
            areas_parciales = []
            
            for n in iteraciones:
                puntos_parcial = np.sum(img_procesada[py[:n], px[:n]] == 255)
                area_parcial = (puntos_parcial / n) * area_ref
                areas_parciales.append(area_parcial)
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(iteraciones, areas_parciales, 'b-o', linewidth=2, markersize=4)
            ax.axhline(y=area_calculada, color='r', linestyle='--', label=f'Área final: {area_calculada:.2f} cm²')
            ax.set_xlabel('Número de Puntos')
            ax.set_ylabel('Área Estimada (cm²)')
            ax.set_title('Convergencia del Método de Monte Carlo')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)

else:
    st.markdown("""
    ### 📋 Instrucciones de Uso:
    
    **📸 Para mejores resultados:**
    1. **Fondo contrastante**: Figura oscura sobre fondo blanco, o viceversa
    2. **Buena iluminación**: Evita sombras y reflejos
    3. **Foto desde arriba**: Toma la foto perpendicular a la figura
    4. **Figura completa**: Asegúrate que toda la figura esté visible
    
    **⚙️ Configuración recomendada:**
    - **Área de referencia**: Mide el área total del rectángulo visible
    - **Número de puntos**: Usa 5000-10000 para mejor precisión
    
    **🎯 Ejemplo práctico para estudiantes:**
    - Coloca una hoja sobre papel milimetrado
    - Calcula: Área referencia = ancho × alto del papel visible
    - Toma foto y sube a la aplicación
    - ¡Observa cómo converge el resultado!
    
    **🔢 Fórmula del método:**
    ```
    Área ≈ (Puntos dentro / Total puntos) × Área referencia
    ```
    """)

# Información educativa
st.sidebar.markdown("---")
st.sidebar.info("""
**🎓 Uso Educativo:**
- Método de Monte Carlo para cálculo de áreas
- Apropiado para matemáticas y estadística
- Visualización interactiva del método
""")
