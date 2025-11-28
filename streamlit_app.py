import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Calculadora de Áreas - Monte Carlo",
    layout="wide"
)

# Título principal
st.title("Calculadora de Áreas con el Método de Monte Carlo")
st.markdown("### Estimación de áreas mediante muestreo aleatorio")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("Configuración")

uploaded_file = st.sidebar.file_uploader(
    "Sube una imagen:",
    type=["png", "jpg", "jpeg"]
)

# Área real del rectángulo
rect_area = st.sidebar.number_input(
    "Área real del rectángulo (unidades²):",
    min_value=1.0,
    value=100.0,
    step=1.0
)

# Número total de puntos
num_points = st.sidebar.number_input(
    "Número total de puntos a generar:",
    min_value=1000,
    max_value=300000,
    value=20000,
    step=1000
)

# Umbral de detección
threshold = st.sidebar.slider(
    "Umbral de detección (0 = muy estricto, 765 = muy permisivo):",
    min_value=0,
    max_value=765,
    value=600
)

# Semilla
seed = st.sidebar.number_input(
    "Semilla aleatoria (0 = aleatorio):",
    min_value=0,
    max_value=999999,
    value=0
)

# ---------------------------------------------------------
# PROCESAMIENTO PRINCIPAL: SIN RECORTES
# ---------------------------------------------------------
if uploaded_file is not None:
    # Imagen ORIGINAL completa (sin recorte)
    image = Image.open(uploaded_file).convert("RGB")
    image_array = np.array(image)
    H, W, _ = image_array.shape

    st.subheader("Imagen cargada")
    st.image(image, use_column_width=True)

    st.markdown(f"**Dimensiones de la imagen:** {W} × {H} px")

    # Generar puntos aleatorios
    if seed != 0:
        np.random.seed(seed)

    xs = np.random.randint(0, W, num_points)
    ys = np.random.randint(0, H, num_points)

    sampled_pixels = image_array[ys, xs]

    # Brillo → R + G + B
    brightness = sampled_pixels.sum(axis=1)

    # Detectamos si el punto pertenece a la figura
    inside_mask = brightness < threshold
    inside_count = inside_mask.sum()

    # Cálculo del área estimada
    area_est = (inside_count / num_points) * rect_area

    # -----------------------------------------------------
    # RESULTADOS
    # -----------------------------------------------------
    st.subheader("Resultados")
    col1, col2 = st.columns(2)

    col1.metric("Puntos generados", f"{num_points:,}")
    col1.metric("Puntos dentro de la figura", f"{inside_count:,}")
    col2.metric("Área estimada", f"{area_est:.4f} unidades²")

    # -----------------------------------------------------
    # GRÁFICO DE PUNTOS
    # -----------------------------------------------------
    st.subheader("Visualización del muestreo")
    fig1, ax1 = plt.subplots(figsize=(7, 6))
    ax1.imshow(image_array)
    ax1.scatter(xs[inside_mask], ys[inside_mask], s=1, color="red")
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_title("Puntos detectados dentro de la figura")
    st.pyplot(fig1)

    # -----------------------------------------------------
    # GRÁFICO DE CONVERGENCIA
    # -----------------------------------------------------
    st.subheader("Gráfico de convergencia del área estimada")

    partial_areas = []
    inside_so_far = 0

    for k in range(1, num_points + 1):
        if inside_mask[k-1]:
            inside_so_far += 1
        partial_areas.append((inside_so_far / k) * rect_area)

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.plot(partial_areas)
    ax2.set_title("Convergencia del área estimada")
    ax2.set_xlabel("Número de puntos")
    ax2.set_ylabel("Área estimada")
    st.pyplot(fig2)

else:
    st.info("Sube una imagen desde el panel lateral para comenzar.")
