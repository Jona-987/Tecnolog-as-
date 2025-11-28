import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Monte Carlo - Estimación de Áreas",
    layout="wide"
)

st.title("Estimación de Áreas mediante Muestreo Aleatorio (Método de Monte Carlo)")
st.markdown("""
Esta herramienta permite estimar el área de una figura dentro de un rectángulo mediante el método de Monte Carlo.
El usuario controla el área real del rectángulo, el número de puntos aleatorios generados y el umbral de detección.
""")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("Configuración")

uploaded_file = st.sidebar.file_uploader(
    "Sube una imagen:",
    type=["png", "jpg", "jpeg"]
)

rect_area = st.sidebar.number_input(
    "Área real del rectángulo (unidades²):",
    min_value=1.0, value=100.0, step=1.0,
    help="Este valor puede ser el área real del rectángulo físico en centímetros o metros."
)

n_points = st.sidebar.number_input(
    "Cantidad total de puntos:",
    min_value=1000,
    max_value=300000,
    value=20000,
    step=1000
)

threshold = st.sidebar.slider(
    "Umbral de detección (0 = muy estricto, 765 = muy permisivo):",
    min_value=0, max_value=765, value=600
)

seed = st.sidebar.number_input(
    "Semilla aleatoria (0 = aleatorio):",
    min_value=0, max_value=999999, value=0
)

# ---------------------------------------------------------
# PROCESAMIENTO
# ---------------------------------------------------------
if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)
    H, W, _ = img_array.shape

    st.subheader("Imagen cargada")
    st.image(image, use_column_width=True)

    st.markdown(f"**Dimensiones:** {W} × {H} px")

    # -----------------------------------------------------
    # GENERAR PUNTOS ALEATORIOS
    # -----------------------------------------------------
    if seed != 0:
        np.random.seed(seed)

    xs = np.random.randint(0, W, n_points)
    ys = np.random.randint(0, H, n_points)

    sample_pixels = img_array[ys, xs]
    brightness = sample_pixels.sum(axis=1)

    inside_mask = brightness < threshold
    inside_count = inside_mask.sum()

    # Estimación proporcional del área
    area_estimada = (inside_count / n_points) * rect_area

    st.subheader("Resultados")
    st.write(f"Puntos generados: **{n_points}**")
    st.write(f"Puntos dentro de la figura: **{inside_count}**")
    st.write(f"Área estimada: **{area_estimada:.3f} unidades²**")

    # -----------------------------------------------------
    # VISUALIZACIÓN DE PUNTOS
    # -----------------------------------------------------
    st.subheader("Visualización del muestreo")
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.imshow(img_array)
    ax.scatter(xs[inside_mask], ys[inside_mask], s=1, color="red")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Puntos detectados dentro de la figura")
    st.pyplot(fig)

    # -----------------------------------------------------
    # GRÁFICO DE CONVERGENCIA
    # -----------------------------------------------------
    st.subheader("Gráfico de convergencia del área estimada")

    partial_areas = []
    for k in range(1, n_points):
        inside_partial = inside_mask[:k].sum()
        partial_area = (inside_partial / k) * rect_area
        partial_areas.append(partial_area)

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.plot(partial_areas)
    ax2.set_title("Convergencia del área estimada")
    ax2.set_xlabel("Número de puntos")
    ax2.set_ylabel("Área estimada")
    st.pyplot(fig2)

else:
    st.info("Sube una imagen desde el panel lateral para comenzar.")
