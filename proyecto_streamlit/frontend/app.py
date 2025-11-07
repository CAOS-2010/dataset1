# frontend/app_new.py
import streamlit as st
import requests
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import StringIO
from pathlib import Path
st.set_page_config(page_title="Dashboard Escolar", layout="wide")

# ----- CARGAR ESTILOS PERSONALIZADOS -----
def load_local_css(file_name: str):
    """Carga un archivo CSS local dentro del HTML de Streamlit"""
    path = Path(__file__).parent / "static" / file_name
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ No se encontró el archivo de estilos: {path}")

# ✅ Llamar la función justo después de los imports
load_local_css("style.css")
# ----- CONFIG -----
try:
    API_BASE = st.secrets["API_BASE"]
except Exception:
    import os
    API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")


# --- ENCABEZADO PRINCIPAL ---
from PIL import Image

# Carga tu logo (ajusta la ruta a tu archivo, por ejemplo en /frontend/static/logo.png)
logo_path = "frontend/static/logo1.png"  # cambia la ruta si tu logo está en otra carpeta

try:
    logo = Image.open(logo_path)
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(logo, width=150)
    with col2:
        st.markdown(
            """
            <h1 style='font-size:60px; color:#6f9eea; margin-bottom:-15px;'>Portal Escolar</h1>
            <p style='color:#888; font-size:18px;'>Sistema de visualización académica</p>
            """,
            unsafe_allow_html=True
        )
except FileNotFoundError:
    st.markdown(
        """
        <h1 style='font-size:36px; color:#2ecc71; margin-bottom:-10px;'>Portal Escolar</h1>
        <p style='color:#888; font-size:18px;'>Sistema de visualización académica</p>
        """,
        unsafe_allow_html=True
    )

TAB_TITLES = [
    "Resumen Ejecutivo",
    "Rendimiento por Materia",
    "Tendencias",
    "Estudiantes en Riesgo",
    "Comparativa por Grupo",
    "Analisis de Grupo y Cursos"
]

tabs = st.tabs(TAB_TITLES)

# ----- HELPERS -----
def fetch(path, params=None):
    """Obtiene datos desde la API."""
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=12)
        r.raise_for_status()
        return r.json().get("data")
    except Exception as e:
        st.error(f"Error conectando API: {e}")
        return None

@st.cache_data(ttl=300)
def load_preview(limit=1001):
    data = fetch("/preview", params={"limit": limit})
    return pd.DataFrame(data) if data else pd.DataFrame()

# ----- Columnas -----
C_ID = "ID_Estudiante"
C_NAME = "Nombre"
C_GENERO = "Género"
C_ETNIA = "Etnia"
C_NSE = "Nivel_Socioeconómico"
C_GRUPO = "Grupo"
C_PROF = "Profesor"
C_MAT = "Calificación_Matemáticas"
C_LECT = "Calificación_Lectura"
C_CIEN = "Calificación_Ciencias"
C_HIST = "Calificación_Historia"
C_ARTE = "Calificación_Arte"
C_EDF = "Calificación_Educación Física"
C_PROM = "Promedio_General"
C_ASIS = "Asistencia_%"
C_RIESGO = "En_Riesgo"
C_PREP = "Nivel_Preparación"

num_cols = [C_MAT, C_LECT, C_CIEN, C_HIST, C_ARTE, C_EDF, C_PROM, C_ASIS, C_PREP]

def try_numeric_column(df, col):
    if col in df.columns:
        ser = df[col].astype(str).replace({"": None, "nan": None, "NaN": None}).str.strip()
        ser = ser.str.replace("%", "", regex=False).str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(ser, errors="coerce")
    return df

# ----- Cargar datos -----
df = load_preview(limit=1000)
if not df.empty:
    for c in num_cols:
        df = try_numeric_column(df, c)

# ----- VISTAS -----
with tabs[0]:
    st.title("📊 Resumen Ejecutivo")

    if df.empty:
        st.info("No se han cargado datos. Verifica que la API (/preview) esté disponible.")
    else:
        st.markdown("""
        Este panel muestra una visión general del desempeño académico y la asistencia de los estudiantes,
        junto con una distribución del nivel socioeconómico.
        """)

        # --- KPI principales ---
        n_estudiantes = len(df)
        tasa_asistencia = df["Asistencia_%"].mean() if "Asistencia_%" in df.columns else np.nan
        promedio_general = df["Promedio_General"].mean() if "Promedio_General" in df.columns else np.nan

        # --- KPI visuales ---
        k1, k2, k3 = st.columns(3)
        k1.metric(" Total de Estudiantes", n_estudiantes)
        k2.metric(" Tasa Promedio de Asistencia", f"{tasa_asistencia:.2f}%" if not np.isnan(tasa_asistencia) else "N/A")
        k3.metric(" Calificación Promedio General", f"{promedio_general:.2f}" if not np.isnan(promedio_general) else "N/A")

        # --- Distribución del nivel socioeconómico ---
# --- Distribución del nivel socioeconómico ---
    if "Nivel_Socioeconómico" in df.columns:
     st.subheader("Distribución por Nivel Socioeconómico")

    # Calcular proporciones correctamente
    socio_dist = (
        df["Nivel_Socioeconómico"]
        .value_counts(normalize=True)
        .mul(100)
        .reset_index()
        .rename(columns={"index": "Nivel_Socioeconómico", "Nivel_Socioeconómico": "Porcentaje"})
    )

    # Aseguramos nombres correctos
    socio_dist.columns = ["Nivel_Socioeconómico", "Porcentaje"]

    fig = px.pie(
        socio_dist,
        names="Nivel_Socioeconómico",
        values="Porcentaje",
        color="Nivel_Socioeconómico",
        title="Proporción de Estudiantes por Nivel Socioeconómico",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)


        # --- Gráfico complementario (distribución de promedio) ---
    if "Promedio_General" in df.columns:
            st.subheader("Distribución de Calificaciones Generales")
            fig_hist = px.histogram(
                df,
                x="Promedio_General",
                nbins=20,
                title="Distribución de Calificaciones Promedio",
                color_discrete_sequence=["#4C78A8"]
            )
            st.plotly_chart(fig_hist, use_container_width=True)


with tabs[1]:
    st.title("📚 Rendimiento por Materia")
    if df.empty:
        st.info("No hay datos.")
    else:
        materias = [C_MAT, C_LECT, C_CIEN, C_HIST, C_ARTE, C_EDF]
        materias = [c for c in materias if c in df.columns]

        if materias:
            st.markdown("### Promedio por Materia")
            prom = df[materias].mean().rename("Promedio").reset_index()
            prom.columns = ["Materia", "Promedio"]
            st.bar_chart(prom.set_index("Materia")["Promedio"])

            st.markdown("### Correlación entre Materias (Mapa de Calor)")
            corr = df[materias].corr().round(2)
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
            ax.set_title("Correlación entre Calificaciones por Materia")
            st.pyplot(fig)
        else:
            st.warning("No se detectaron columnas de materias.")

with tabs[2]:
    st.title("📈 Tendencias Académicas")

    if df.empty:
        st.info("No hay datos para mostrar.")
    else:
        st.markdown("### Tendencia de Asistencia Promedio a lo Largo del Año")
        # Generamos un eje temporal simulado si no hay fechas
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        # Simular fluctuaciones de asistencia
        np.random.seed(42)
        asistencia_prom = np.clip(np.random.normal(df[C_ASIS].mean(), 3, 12), 60, 100)
        trend_df = pd.DataFrame({"Mes": meses, "Asistencia Promedio (%)": asistencia_prom})
        st.line_chart(trend_df.set_index("Mes")["Asistencia Promedio (%)"])

        st.markdown("---")
        st.markdown("### 🎯 Relación entre Asistencia y Promedio General")
        if C_ASIS in df.columns and C_PROM in df.columns:
            fig2 = px.scatter(
                df, x=C_ASIS, y=C_PROM, color=C_GRUPO if C_GRUPO in df.columns else None,
                title="Correlación entre Asistencia y Promedio General",
                labels={C_ASIS: "Asistencia (%)", C_PROM: "Promedio General"},
                trendline="ols"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No se encontraron columnas de asistencia y promedio general para el gráfico de correlación.")

with tabs[3]:
    st.title("🎯 Estudiantes en Riesgo - Intervención Temprana")

    if df.empty:
        st.info("No hay datos para analizar.")
    else:
        st.markdown("""
        Esta vista permite identificar estudiantes con **bajo desempeño académico**
        y **baja asistencia**, para una intervención temprana.
        """)

        # --- Controles de filtro ---
        col1, col2 = st.columns(2)
        umbral_promedio = col1.slider("Umbral de calificación mínima", 0.0, 5.0, 3.0, 0.1)
        umbral_asistencia = col2.slider("Umbral mínimo de asistencia (%)", 0.0, 100.0, 75.0, 1.0)

        # --- Filtro de riesgo ---
        riesgo = df[
            (df["Promedio_General"] < umbral_promedio) &
            (df["Asistencia_%"] < umbral_asistencia)
        ].copy()

        st.subheader(f"🧾 Estudiantes en riesgo detectados: {len(riesgo)}")

        if riesgo.empty:
            st.success("No se detectaron estudiantes en riesgo según los criterios actuales.")
        else:
            # Ordenar por promedio y asistencia
            riesgo = riesgo.sort_values(by=["Promedio_General", "Asistencia_%"], ascending=[True, True])

            # Mostrar tabla dinámica
            st.dataframe(
                riesgo[
                    ["ID_Estudiante", "Nombre", "Género", "Grupo", "Promedio_General", "Asistencia_%", "En_Riesgo"]
                ],
                use_container_width=True,
            )

            # Gráfico de riesgo
            st.subheader("📊 Visualización de Riesgo (Asistencia vs Promedio)")
            fig = px.scatter(
                riesgo,
                x="Asistencia_%",
                y="Promedio_General",
                color="Grupo",
                hover_data=["Nombre"],
                title="Relación entre Asistencia y Promedio General",
                labels={"Asistencia_%": "Asistencia (%)", "Promedio_General": "Promedio General"},
                trendline="ols"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Botón de descarga
            csv = riesgo.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar lista de riesgo (CSV)", csv, "estudiantes_en_riesgo.csv")

with tabs[4]:
        st.title("🔎 Análisis Demográfico")

        if df.empty:
         st.info("No hay datos.")
        else:
         st.markdown("Analiza cómo varía el rendimiento por género, etnia y nivel de preparación.")

        # Materias disponibles en el dataset
        materias = [c for c in [C_MAT, C_LECT, C_CIEN, C_HIST, C_ARTE, C_EDF] if c in df.columns]
        if not materias:
            st.warning("No se detectaron columnas de materias para analizar.")
        else:
            # Controles
            col1, col2, col3 = st.columns([1,1,1])
            materia_sel = col1.selectbox("Selecciona materia", materias, index=0)
            demografia = col2.selectbox("Desglosar por", options=[C_GENERO, C_ETNIA, C_PREP])
            tipo_grafico = col3.selectbox("Tipo de gráfico", options=["Boxplot (distribución)", "Violin (distribución)", "Bar (promedios)"])

            st.markdown("---")

            # Filtrar datos limpios para la materia seleccionada
            df_plot = df[[materia_sel, demografia]].dropna(subset=[materia_sel, demografia]).copy()
            # Asegurar columna numérica
            df_plot[materia_sel] = pd.to_numeric(df_plot[materia_sel], errors="coerce")
            df_plot = df_plot.dropna(subset=[materia_sel])
            if df_plot.empty:
                st.warning("No hay datos válidos para la materia/segmento seleccionado.")
            else:
                # Mostrar resumen rápido (tabla agregada)
                agg = df_plot.groupby(demografia)[materia_sel].agg(["count", "mean", "median"]).reset_index().sort_values("mean", ascending=False)
                st.subheader("Resumen por segmento")
                st.dataframe(agg.rename(columns={"count":"Conteo","mean":"Media","median":"Mediana"}).round(2))

                # Gráficos interactivos con Plotly
                import plotly.express as px

                if tipo_grafico == "Boxplot (distribución)":
                    fig = px.box(
                        df_plot, x=demografia, y=materia_sel, points="outliers",
                        title=f"Boxplot de {materia_sel} por {demografia}",
                        labels={demografia: demografia, materia_sel: "Calificación"}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif tipo_grafico == "Violin (distribución)":
                    fig = px.violin(
                        df_plot, x=demografia, y=materia_sel, box=True, points="all",
                        title=f"Violin plot de {materia_sel} por {demografia}",
                        labels={demografia: demografia, materia_sel: "Calificación"}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                else:  # Bar (promedios)
                    mean_df = df_plot.groupby(demografia)[materia_sel].mean().reset_index().sort_values(materia_sel, ascending=False)
                    fig = px.bar(
                        mean_df, x=demografia, y=materia_sel, text=round(mean_df[materia_sel],2),
                        title=f"Promedio de {materia_sel} por {demografia}",
                        labels={demografia: demografia, materia_sel: "Promedio"}
                    )
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                # Opcional: scatter entre asistencia y materia coloreado por demografía
                if C_ASIS in df.columns:
                    st.subheader(f"Scatter: Asistencia vs {materia_sel} (coloreado por {demografia})")
                    df_sc = df[[C_ASIS, materia_sel, demografia]].dropna().copy()
                    df_sc[C_ASIS] = pd.to_numeric(df_sc[C_ASIS], errors="coerce")
                    df_sc[materia_sel] = pd.to_numeric(df_sc[materia_sel], errors="coerce")
                    df_sc = df_sc.dropna()
                    if not df_sc.empty:
                        fig2 = px.scatter(
                            df_sc, x=C_ASIS, y=materia_sel, color=demografia,
                            hover_data=[demografia, C_ASIS, materia_sel],
                            trendline="ols",
                            title=f"Asistencia vs {materia_sel} por {demografia}",
                            labels={C_ASIS: "Asistencia (%)", materia_sel: "Calificación"}
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.info("No hay datos suficientes para el scatter de asistencia.")

with tabs[5]:
    st.title("🔍 Detalle por Curso / Profesor")

    if df.empty:
        st.info("No hay datos.")
    else:
        st.markdown("Selecciona un **Profesor** o un **Curso / Grupo** para ver estadísticas y la lista de estudiantes asociados.")

        # controles: Profesor y Grupo (curso)
        colp, colg, cols = st.columns([1,1,1])
        profesor_list = sorted(df[C_PROF].dropna().unique().tolist()) if C_PROF in df.columns else []
        grupo_list = sorted(df[C_GRUPO].dropna().unique().tolist()) if C_GRUPO in df.columns else []

        profesor_sel = colp.selectbox("Filtrar por Profesor (opcional)", ["(Todos)"] + profesor_list, index=0)
        grupo_sel = colg.selectbox("Filtrar por Grupo/Curso (opcional)", ["(Todos)"] + grupo_list, index=0)

        # elegir materia para ver estadísticas
        materias = [c for c in [C_MAT, C_LECT, C_CIEN, C_HIST, C_ARTE, C_EDF] if c in df.columns]
        materia_sel = cols.selectbox("Selecciona materia para estadísticas", ["(Ninguna)"] + materias, index=0)

        # aplicar filtros
        df_filtered = df.copy()
        if profesor_sel and profesor_sel != "(Todos)":
            df_filtered = df_filtered[df_filtered[C_PROF] == profesor_sel]
        if grupo_sel and grupo_sel != "(Todos)":
            df_filtered = df_filtered[df_filtered[C_GRUPO] == grupo_sel]

        st.markdown(f"**Registros encontrados:** {len(df_filtered)}")

        if len(df_filtered) == 0:
            st.warning("No existen registros con los filtros seleccionados.")
        else:
            # Mostrar tabla dinámica (buscable): agregar search por nombre/ID
            st.subheader("Lista de Estudiantes")
            search_col1, search_col2 = st.columns([2,1])
            query_name = search_col1.text_input("Buscar por nombre (parcial)", "")
            query_id = search_col2.text_input("Buscar por ID (exacto)", "")

            table_df = df_filtered.copy()
            if query_name:
                table_df = table_df[table_df[C_NAME].astype(str).str.contains(query_name, case=False, na=False)]
            if query_id:
                table_df = table_df[table_df[C_ID].astype(str) == str(query_id)]

            # columnas a mostrar
            show_cols = [C_ID, C_NAME, C_GENERO, C_ETNIA, C_GRUPO, C_PROF, C_PROM, C_ASIS, C_RIESGO]
            show_cols = [c for c in show_cols if c in table_df.columns]
            st.dataframe(table_df[show_cols].reset_index(drop=True), use_container_width=True)

            # Estadísticas por materia seleccionada
            if materia_sel and materia_sel != "(Ninguna)":
                st.subheader(f"Estadísticas de {materia_sel} (filtro aplicado)")
                # asegurar tipo numérico
                table_df[materia_sel] = pd.to_numeric(table_df[materia_sel], errors="coerce")
                table_df[C_ASIS] = pd.to_numeric(table_df[C_ASIS], errors="coerce") if C_ASIS in table_df.columns else None

                n = int(table_df[materia_sel].count())
                mean = float(table_df[materia_sel].mean()) if n>0 else np.nan
                median = float(table_df[materia_sel].median()) if n>0 else np.nan
                std = float(table_df[materia_sel].std()) if n>1 else np.nan
                minv = float(table_df[materia_sel].min()) if n>0 else np.nan
                maxv = float(table_df[materia_sel].max()) if n>0 else np.nan

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Registros válidos", f"{n}")
                c2.metric("Media", f"{mean:.2f}" if not np.isnan(mean) else "N/A")
                c3.metric("Mediana", f"{median:.2f}" if not np.isnan(median) else "N/A")
                c4.metric("Desviación estándar", f"{std:.2f}" if not np.isnan(std) else "N/A")

                # Histograma de la materia
                st.markdown("**Distribución de calificaciones**")
                try:
                    fig_hist = px.histogram(table_df, x=materia_sel, nbins=20, title=f"Distribución de {materia_sel}")
                    st.plotly_chart(fig_hist, use_container_width=True)
                except Exception:
                    st.write(table_df[materia_sel].describe())

                # Scatter: Asistencia vs Nota (si hay Asistencia)
                if C_ASIS in table_df.columns and table_df[C_ASIS].notna().sum() > 0:
                    st.markdown("**Asistencia vs Calificación (scatter)**")
                    df_sc = table_df.dropna(subset=[materia_sel, C_ASIS]).copy()
                    if not df_sc.empty:
                        try:
                            fig_sc = px.scatter(
                                df_sc,
                                x=C_ASIS,
                                y=materia_sel,
                                color=C_GRUPO if C_GRUPO in df_sc.columns else None,
                                hover_data=[C_NAME, C_ID],
                                trendline="ols",
                                title=f"Asistencia (%) vs {materia_sel}"
                            )
                            st.plotly_chart(fig_sc, use_container_width=True)
                        except Exception:
                            st.write(df_sc[[C_ASIS, materia_sel]].head(50))
                # descargar filtrado
                csv = table_df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Descargar datos filtrados (CSV)", csv, "detalle_filtrado.csv")
            else:
                st.info("Selecciona una materia para ver estadísticas y gráficos específicos de ese grupo.")
