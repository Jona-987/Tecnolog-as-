# streamlit_app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import io
import time
import csv

st.set_page_config(page_title="Calculadora de Áreas - Monte Carlo", layout="wide")

st.title("Calculadora de áreas - Método Monte Carlo")
st.markdown("Estimación de áreas de figuras irregulares mediante muestreo aleatorio")

# ----- Sidebar: configuración -----
st.sidebar.header("Configuración")

uploaded_file = st.sidebar.file_uploader("Sube una imagen (png/jpg/jpeg):", type=['png', 'jpg', 'jpeg'])

st.sidebar.markdown("Parámetros de detección")
area_ref = st.sidebar.number_input("Área de referencia (cm²):", min_value=0.01, value=100.0, step=0.1)

# Más puntos: rango amplio, slider con visualización inmediata
n_puntos = st.sidebar.slider("Número de puntos (muestras):", min_value=100, max_value=200000, value=5000, step=100)
st.sidebar.caption("Si eliges muchos puntos, la ejecución tarda más. Se muestran como máximo 5000 puntos en la visualización.")

# umbral y opción invertir (figura clara / figura oscura)
umbral = st.sidebar.slider("Umbral (0-255):", min_value=0, max_value=255, value=128)
invert = st.sidebar.checkbox("Invertir criterio (si la figura es clara sobre fondo oscuro)", value=False)

# opciones de recorte/autodetección
auto_bbox = st.sidebar.checkbox("Recortar a la caja mínima que contiene la figura (detección automática)", value=True)
pad_pixels = st.sidebar.number_input("Relleno de recorte (px):", min_value=0, max_value=50, value=5)

# opciones de visualización y descarga
display_limit = st.sidebar.number_input("Máx puntos para visualizar:", min_value=100, max_value=5000, value=2000, step=100)
seed = st.sidebar.number_input("Semilla aleatoria (0 = aleatorio):", min_value=0, value=0, step=1)

st.sidebar.markdown("---")
if st.sidebar.button("Calcular área"):
    if uploaded_file is None:
        st.sidebar.error("Sube primero una imagen.")
    else:
        # Leer imagen
        img = Image.open(uploaded_file).convert("L")  # escala de grises
        img_arr = np.array(img)
        h, w = img_arr.shape

        # Autodetección de bbox si se solicita
        if auto_bbox:
            # Considerar pixeles de figura según umbral/invert
            if not invert:
                mask = img_arr < umbral
            else:
                mask = img_arr > umbral

            ys, xs = np.where(mask)
            if len(xs) == 0:
                st.error("No se detectó figura con esos parámetros. Ajusta el umbral o desactiva recorte automático.")
                st.stop()
            x_min = max(xs.min() - pad_pixels, 0)
            x_max = min(xs.max() + pad_pixels, w - 1)
            y_min = max(ys.min() - pad_pixels, 0)
            y_max = min(ys.max() + pad_pixels, h - 1)

            img_crop = img.crop((x_min, y_min, x_max + 1, y_max + 1))
            img_arr = np.array(img_crop)
            crop_w = x_max - x_min + 1
            crop_h = y_max - y_min + 1
        else:
            img_crop = img
            crop_w, crop_h = w, h
            x_min = 0; y_min = 0

        # Preparar semilla
        if seed != 0:
            np.random.seed(int(seed))

        # Generación vectorizada en "chunks" para no agotar memoria y poder mostrar progreso
        total = int(n_puntos)
        chunk = 100000  # tamaño de chunk razonable para iterar
        puntos_dentro = 0
        puntos_x_display = []
        puntos_y_display = []
        dentro_bool_list = []

        progress_bar = st.progress(0)
        it_done = 0

        start_time = time.time()

        while it_done < total:
            this_chunk = min(chunk, total - it_done)
            # vectorized uniform random
            xs_rand = np.random.randint(0, crop_w, size=this_chunk)
            ys_rand = np.random.randint(0, crop_h, size=this_chunk)

            # sample pixel values
            vals = img_arr[ys_rand, xs_rand]
            if not invert:
                inside_chunk = vals < umbral
            else:
                inside_chunk = vals > umbral

            puntos_dentro += int(np.sum(inside_chunk))

            # store for visualization (only up to display_limit)
            needed = display_limit - len(puntos_x_display)
            if needed > 0:
                take = min(needed, this_chunk)
                # select indices for display uniformly in chunk
                idxs = np.linspace(0, this_chunk - 1, take).astype(int)
                puntos_x_display.extend(list(xs_rand[idxs] + x_min))
                puntos_y_display.extend(list(ys_rand[idxs] + y_min))
                dentro_bool_list.extend(list(inside_chunk[idxs]))

            it_done += this_chunk
            progress_bar.progress(it_done / total)

        elapsed = time.time() - start_time

        # cálculo de área estimada
        proporcion = puntos_dentro / total
        area_estimada = proporcion * float(area_ref)

        # Mostrar resultados (solo esenciales)
        st.subheader("Resultados")
        st.write(f"Área estimada: **{area_estimada:.2f} cm²**")
        st.write(f"Puntos dentro: **{puntos_dentro}** / **{total}**")
        st.write(f"Tiempo aproximado: {elapsed:.2f} s")

        # Visualizaciones en dos columnas
        col1, col2 = st.columns((1.1, 1))

        with col1:
            st.subheader("Distribución de puntos (vista)")
            fig1, ax1 = plt.subplots(figsize=(6, 5))
            ax1.imshow(img_crop, cmap='gray', alpha=0.9)
            # mostrar los puntos guardados
            for i in range(len(puntos_x_display)):
                if dentro_bool_list[i]:
                    ax1.plot(puntos_x_display[i] - x_min, puntos_y_display[i] - y_min, 'o', markersize=3, alpha=0.6)
                else:
                    ax1.plot(puntos_x_display[i] - x_min, puntos_y_display[i] - y_min, 'o', markersize=3, alpha=0.6, color='red')
            ax1.axis('off')
            st.pyplot(fig1)

        with col2:
            st.subheader("Evolución (muestras parciales)")
            # hacer cálculo de áreas parciales en puntos fijos
            pasos = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
            pasos = [p for p in pasos if p <= total]
            iteraciones = []
            areas_parciales = []
            # Para cada paso, tomar muestras aleatorias independientes (submuestreo)
            for p in pasos:
                xs_p = np.random.randint(0, crop_w, size=p)
                ys_p = np.random.randint(0, crop_h, size=p)
                vals_p = img_arr[ys_p, xs_p]
                if not invert:
                    inside_p = vals_p < umbral
                else:
                    inside_p = vals_p > umbral
                area_p = (inside_p.sum() / p) * float(area_ref)
                iteraciones.append(p)
                areas_parciales.append(area_p)

            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.plot(iteraciones, areas_parciales, '-o')
            ax2.axhline(y=area_estimada, color='red', linestyle='--', label=f'Área (final) {area_estimada:.2f}')
            ax2.set_xlabel("Número de puntos")
            ax2.set_ylabel("Área estimada (cm²)")
            ax2.legend()
            ax2.grid(alpha=0.3)
            st.pyplot(fig2)

        # botón para descargar resultados (CSV)
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(["area_estimada_cm2", "puntos_dentro", "total_puntos", "umbral", "invert", "auto_bbox"])
        csv_writer.writerow([f"{area_estimada:.5f}", puntos_dentro, total, umbral, invert, auto_bbox])
        csv_bytes = csv_buffer.getvalue().encode('utf-8')

        st.download_button("Descargar resultado (CSV)", data=csv_bytes, file_name="resultado_area.csv", mime="text/csv")

        # botón para descargar la imagen recortada con puntos superpuestos
        buf_img = io.BytesIO()
        fig1.savefig(buf_img, format='png', bbox_inches='tight')
        buf_img.seek(0)
        st.download_button("Descargar vista (PNG)", data=buf_img, file_name="vista_puntos.png", mime="image/png")

# Ayuda / instrucciones mínimas
st.markdown("---")
st.markdown("Instrucciones rápidas: sube la imagen, ajusta el umbral y parámetros, luego pulsa 'Calcular área'.")
