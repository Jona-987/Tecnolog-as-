import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random

st.set_page_config(
    page_title="Calculadora de Áreas - Método Monte Carlo", 
    layout="wide"
)

st.title("Calculadora de Áreas - Método Monte Carlo")
st.markdown("### ¡Calcula áreas de figuras irregulares con probabilidad!")

# Sidebar
st.sidebar.header("Configuración")

uploaded_file = st.sidebar.file_uploader(
    "Sube tu imagen:", 
    type=['png', 'jpg', 'jpeg']
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Mostrar imagen en sidebar
    st.sidebar.image(image, caption="Tu imagen", use_column_width=True)
    
    # PARÁMETROS
    st.sidebar.subheader("Parámetros de Cálculo")
    
    area_ref = st.sidebar.number_input(
        "Área de referencia (cm²):", 
        min_value=0.1, 
        value=100.0,
        help="Área total del rectángulo que contiene tu figura en la realidad"
    )
    
    n_puntos = st.sidebar.select_slider(
        "Número de puntos:", 
        options=[500, 1000, 2000, 5000, 10000],
        value=2000
    )
    
    umbral = st.sidebar.slider(
        "Umbral de detección:",
        min_value=1,
        max_value=255,
        value=128,
        help="Ajusta si la figura no se detecta bien (valores bajos para figuras oscuras)"
    )
    
    # ⚠️⚠️⚠️ ¡ESTE ES EL BOTÓN QUE DEBE APARECER! ⚠️⚠️⚠️
    calcular_button = st.sidebar.button("🎯 CALCULAR ÁREA", type="primary", use_container_width=True)
    
    if calcular_button:
        with st.spinner("Lanzando puntos aleatorios..."):
            # Convertir a escala de grises
            img_gris = image.convert('L')
            img_array = np.array(img_gris)
            h, w = img_array.shape
            
            # Generar puntos aleatorios
            puntos_dentro = 0
            puntos_x = []
            puntos_y = []
            dentro_lista = []
            
            for i in range(n_puntos):
                x = random.randint(0, w-1)
                y = random.randint(0, h-1)
                
                # Si el pixel es oscuro (figura)
                if img_array[y, x] < umbral:
                    puntos_dentro += 1
                    dentro_lista.append(True)
                else:
                    dentro_lista.append(False)
                
                puntos_x.append(x)
                puntos_y.append(y)
            
            # Calcular área
            proporcion = puntos_dentro / n_puntos
            area_calculada = proporcion * area_ref
            
            # MOSTRAR RESULTADOS
            st.success(f"** Área calculada: {area_calculada:.2f} cm²**")
            st.info(f"🎯 Puntos dentro de la figura: {puntos_dentro} de {n_puntos} ({(puntos_dentro/n_puntos)*100:.1f}%)")
            
            # Visualización
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Simulación de Puntos")
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                ax1.imshow(img_gris, cmap='gray', alpha=0.7)
                
                # Mostrar solo los primeros 1000 puntos para no saturar
                muestra = min(1000, n_puntos)
                for i in range(muestra):
                    if dentro_lista[i]:
                        ax1.plot(puntos_x[i], puntos_y[i], 'bo', markersize=2, alpha=0.6)
                    else:
                        ax1.plot(puntos_x[i], puntos_y[i], 'ro', markersize=2, alpha=0.6)
                
                ax1.set_title(f"Puntos: Azul=dentro, Rojo=fuera\n(Mostrando {muestra} puntos)")
                ax1.axis('off')
                st.pyplot(fig1)
            
            with col2:
                st.subheader("Convergencia del Método")
                
                # Calcular evolución
                iteraciones = []
                areas_parciales = []
                
                for paso in [100, 500, 1000, 2000, 5000]:
                    if paso <= n_puntos:
                        puntos_parcial = sum(dentro_lista[:paso])
                        area_parcial = (puntos_parcial / paso) * area_ref
                        iteraciones.append(paso)
                        areas_parciales.append(area_parcial)
                
                fig2, ax2 = plt.subplots(figsize=(8, 4))
                ax2.plot(iteraciones, areas_parciales, 'go-', linewidth=2, markersize=6)
                ax2.axhline(y=area_calculada, color='red', linestyle='--', label=f'Área final: {area_calculada:.2f} cm²')
                ax2.set_xlabel('Número de Puntos')
                ax2.set_ylabel('Área Estimada (cm²)')
                ax2.set_title('Evolución de la Estimación')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                st.pyplot(fig2)
                
            # Explicación del método
            st.markdown("---")
            st.subheader("🔢 Explicación del Método")
            st.latex(rf"Área_{{figura}} = \frac{{{puntos\_dentro}}}{{{n\_puntos}}} \times {area\_ref} = {area\_calculada:.2f}  cm²")
            st.markdown("""
            **¿Cómo funciona?**
            1. Se lanzan puntos aleatorios sobre toda el área
            2. Se cuentan los puntos que caen dentro de la figura
            3. La proporción de puntos dentro vs total es igual a la proporción de áreas
            """)

else:
    # Pantalla inicial sin imagen
    st.markdown("""
    ### 📋 Instrucciones de Uso:
    
    1. **📸 Sube una imagen** usando el panel izquierdo
    2. **📐 Configura el área de referencia** (el área total del rectángulo que contiene tu figura)
    3. **🎯 Elige cuántos puntos** quieres lanzar (más puntos = más precisión)
    4. **🚀 Haz clic en 'CALCULAR ÁREA'** (aparecerá en el panel izquierdo después de subir la imagen)
    
    ### Consejos para mejores resultados:
    - **Usa fondos contrastantes**: Figura oscura sobre fondo blanco, o viceversa
    - **Buena iluminación**: Evita sombras
    - **Ajusta el umbral**: Si la figura no se detecta bien, cambia el deslizador "Umbral de detección"
    
    ### 🎯 Ejemplo para estudiantes:
    - Coloca una hoja sobre papel milimetrado
    - Calcula: Área referencia = ancho × alto del papel visible
    - Toma foto desde arriba y ¡calcula el área de la hoja!
    """)

# Información adicional
st.sidebar.markdown("---")
st.sidebar.info("""
**🎓 Para educadores:**
- Método de Monte Carlo aplicado
- Visualización interactiva
- Apropiado para matemáticas y estadística
""")
