import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random

st.set_page_config(page_title="Calculadora de Áreas", layout="wide")

st.title("🌿 Calculadora de Áreas - Método Monte Carlo")
st.markdown("### ¡Sube una imagen y calcula su área!")

# Sidebar
st.sidebar.header("📐 Configuración")

uploaded_file = st.sidebar.file_uploader("Sube tu imagen:", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Tu imagen", use_column_width=True)
    
    # Parámetros
    area_ref = st.sidebar.number_input("Área de referencia (cm²):", value=100.0)
    n_puntos = st.sidebar.slider("Número de puntos:", 100, 5000, 1000)
    
    if st.sidebar.button("🎯 Calcular Área"):
        # Convertir a array
        img_array = np.array(image.convert('L'))
        
        # Dimensiones
        h, w = img_array.shape
        
        # Generar puntos aleatorios
        puntos_dentro = 0
        puntos_x = []
        puntos_y = []
        colores = []
        
        for i in range(n_puntos):
            x = random.randint(0, w-1)
            y = random.randint(0, h-1)
            
            # Si el pixel es oscuro (figura)
            if img_array[y, x] < 128:  # Umbral simple
                puntos_dentro += 1
                colores.append('blue')
            else:
                colores.append('red')
            
            puntos_x.append(x)
            puntos_y.append(y)
        
        # Calcular área
        proporcion = puntos_dentro / n_puntos
        area_calculada = proporcion * area_ref
        
        # Mostrar resultados
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"**Área calculada: {area_calculada:.2f} cm²**")
            st.info(f"Puntos dentro: {puntos_dentro} de {n_puntos}")
            
            # Gráfico simple
            fig, ax = plt.subplots(figsize=(6, 4))
            iteraciones = list(range(100, n_puntos, n_puntos//10))
            if iteraciones:
                areas_parciales = [(puntos_dentro * area_ref) / n for n in iteraciones]
                ax.plot(iteraciones, areas_parciales, 'b-o')
                ax.set_xlabel('Número de puntos')
                ax.set_ylabel('Área (cm²)')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            # Visualización
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.imshow(img_array, cmap='gray', alpha=0.5)
            ax2.scatter(puntos_x[:500], puntos_y[:500], c=colores[:500], s=1, alpha=0.6)
            ax2.set_title("Puntos: Azul=dentro, Rojo=fuera")
            ax2.axis('off')
            st.pyplot(fig2)

else:
    st.markdown("""
    ### 📋 Instrucciones:
    1. **Sube una imagen** usando el panel izquierdo
    2. **Configura el área de referencia** (el área total que contiene tu figura)
    3. **Elige cuántos puntos** quieres lanzar
    4. **Haz clic en 'Calcular Área'**
    
    ### 💡 Ejemplo:
    - Si tu imagen muestra una hoja en un rectángulo de 10x10 cm, el área de referencia es 100 cm²
    - La aplicación lanzará puntos aleatorios y contará cuántos caen sobre la hoja
    - ¡Entre más puntos, más precisa será la estimación!
    """)
