import streamlit as st 
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random

st.set_page_config(
    page_title="Calculadora de Áreas - Monte Carlo", 
    layout="wide"
)

st.title("Calculadora de Áreas con el Método de Monte Carlo")
st.markdown("### Estimación de áreas mediante muestreo aleatorio")

# Sidebar
st.sidebar.header("Configuración")

uploaded_file = st.sidebar.file_uploader(
    "Sube una imagen:", 
    type=['png', 'jpg', 'jpeg']
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Mostrar imagen en sidebar
    st.sidebar.image(image, caption="Imagen cargada", use_column_width=True)
    
    st.sidebar.subheader("Parámetros de cálculo")
    
    area_ref = st.sidebar.number_input(
        "Área de referencia (cm²):", 
        min_value=0.1, 
        value=100.0
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
        value=128
    )
    
    calcular_button = st.sidebar.button("Calcular área", type="primary", use_container_width=True)
    
    if calcular_button:
        with st.spinner("Procesando..."):
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
                x = random.randint(0, w - 1)
                y = random.randint(0, h - 1)
                
                if img_array[y, x] < umbral:
                    puntos_dentro += 1
                    dentro_lista.append(True)
                else:
                    dentro_lista.append(False)
                
                puntos_x.append(x)
                puntos_y.append(y)
            
            # Calcular área estimada
            proporcion = puntos_dentro / n_puntos
            area_calculada = proporcion * area_ref
            
            # Mostrar resultados
            st.subheader("Resultados")
            st.write(f"Área estimada: **{area_calculada:.2f} cm²**")
            st.write(f"Puntos dentro: **{puntos_dentro}** de **{n_puntos}**")
            
            # Visualización
            col1, col2 = st.columns(2)
            
            # Gráfico 1: puntos sobre la imagen
            with col1:
                st.subheader("Distribución de puntos")
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                ax1.imshow(img_gris, cmap='gray', alpha=0.7)
                
                muestra = min(1000, n_puntos)
                for i in range(muestra):
                    if dentro_lista[i]:
                        ax1.plot(puntos_x[i], puntos_y[i], 'bo', markersize=2, alpha=0.6)
                    else:
                        ax1.plot(puntos_x[i], puntos_y[i], 'ro', markersize=2, alpha=0.6)
                
                ax1.set_title(f"Puntos: azul=dentro, rojo=fuera (mostrando {muestra})")
                ax1.axis('off')
                st.pyplot(fig1)
            
            # Gráfico 2: convergencia
            with col2:
                st.subheader("Convergencia del método")
                
                iteraciones = []
                areas_parciales = []
                
                for paso in [100, 500, 1000, 2000, 5000]:
                    if paso <= n_puntos:
                        puntos_parcial = sum(dentro_lista[:paso])
                        area_parcial = (puntos_parcial / paso) * area_ref
                        iteraciones.append(paso)
                        areas_parciales.append(area_parcial)
                
                fig2, ax2 = plt.subplots(figsize=(8, 4))
                ax2.plot(iteraciones, areas_parciales, 'o-', linewidth=2, markersize=6)
                ax2.axhline(
                    y=area_calculada, 
                    color='red', 
                    linestyle='--', 
                    label=f'Área final: {area_calculada:.2f} cm²'
                )
                ax2.set_xlabel('Número de Puntos')
                ax2.set_ylabel('Área Estimada (cm²)')
                ax2.set_title('Evolución de la estimación')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                st.pyplot(fig2)

else:
    st.markdown("""
    ### Instrucciones de uso:
    
    1. Sube una imagen desde el panel izquierdo.  
    2. Especifica el área real del rectángulo que contiene la figura.  
    3. Selecciona la cantidad de puntos a utilizar.  
    4. Ajusta el umbral si la figura no se detecta correctamente.  
    5. Haz clic en **Calcular área**.  
    """)

st.sidebar.markdown("---")
st.sidebar.info("""
Aplicación educativa para estimación de áreas mediante el método de Monte Carlo.
""")
