import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Calculadora de Áreas - Monte Carlo",
    layout="wide"
)

st.title("Calculadora de Áreas con el Método de Monte Carlo")
st.markdown("""
Esta aplicación permite estimar el área de una figura dentro de una imagen utilizando el método de Monte Carlo.
El algoritmo genera puntos aleatorios sobre la imagen completa y cuenta cuántos caen en la región no blanca
(la figura).
""")

# ---------------------------------------------------------
# SIDEBAR DE CONFIGURACIÓN
# ---------------------------------------------------------
st.sidebar.header("Configuración")

uploaded_file = st.sidebar.file_uploader(
    "Sube una imagen:",
    type=["png", "jpg", "jpeg"]
)

max_points = st.sidebar.number_input(
    "Número de puntos para generar:",
    min_value=1000,
    max_value=200000,
    value=20000,
    step=1000
)

seed = st.sidebar.number_input(
    "Semilla aleatoria (0 = aleatorio):",
    min_value=0,
    max_value=999999,
    value=0,
    step=1
)

# ---------------------------------------------------------
# PROCESAMIENTO DE LA IMAGEN
# ---------------------------------------------------------
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    st.subheader("Imagen cargada")
    st.image(image, use_column_width=True)

    height, width, _ = img_array.shape
    area_rect = width * height

    st.markdown(f"**Dimensiones de la imagen:** {width} × {height} px")
    st.markdown(f"**Área total del rectángulo:** {area_rect} unidades²")

    # -----------------------------------------------------
    # GENERACIÓN DE PUNTOS ALEATORIOS
    # -----------------------------------------------------
    if seed != 0:
        np.random.seed(seed)

    x_points = np.random.randint(0, width, max_points)
    y_points = np.random.randint(0, height, max_points)

    sampled_pixels = img_array[y_points, x_points]

    # Determinar si un píxel pertenece a la figura:
    # Definición: un píxel es parte de la figura si NO es casi blanco.
    mask_figure = ~( (sampled_pixels[:,0] > 240) &
                     (sampled_pixels[:,1] > 240) &
                     (sampled_pixels[:,2] > 240) )

    inside_count = np.sum(mask_figure)
    area_estimada = (inside_count / max_points) * area_rect

    st.subheader("Resultados")

    st.markdown(f"**Puntos totales generados:** {max_points}")
    st.markdown(f"**Puntos dentro de la figura:** {inside_count}")
    st.markdown(f"**Área estimada de la figura:** {area_estimada:.2f} unidades²")

    # -----------------------------------------------------
    # VISUALIZACIÓN
    # -----------------------------------------------------
    st.subheader("Visualización del muestreo")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(img_array)
    ax.scatter(x_points[mask_figure], y_points[mask_figure], s=1)
    ax.set_title("Puntos detectados dentro de la figura")
    ax.set_xticks([])
    ax.set_yticks([])
    st.pyplot(fig)

else:
    st.info("Sube una imagen desde el panel lateral para comenzar.")
