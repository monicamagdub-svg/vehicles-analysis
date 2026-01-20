import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- Page setup ----------------
st.set_page_config(page_title="Sprint7 - Vehicles Dashboard", layout="wide")

st.title("Dashboard: Anuncios de venta de coches (USA)")
st.caption("Sprint 7 by Monica Magdub")

# ---------------- Load data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("vehicles_us.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# ---------------- Helpers ----------------
def safe_minmax(series, default_min=0, default_max=1):
    s = series.dropna()
    if s.empty:
        return default_min, default_max
    return float(s.min()), float(s.max())

# ---------------- Sidebar: filters ----------------
st.sidebar.header("Filtros")

df_f = df.copy()

# Año del modelo
if "model_year" in df_f.columns and df_f["model_year"].notna().any():
    y_min, y_max = safe_minmax(df_f["model_year"])
    y_min, y_max = int(y_min), int(y_max)
    year_range = st.sidebar.slider(
        "Año del modelo",
        y_min,
        y_max,
        (y_min, y_max)
    )
    df_f = df_f[df_f["model_year"].between(year_range[0], year_range[1])]

# Tipo de vehículo
if "type" in df_f.columns:
    types = sorted(df_f["type"].dropna().unique().tolist())
    sel_type = st.sidebar.multiselect("Tipo de vehículo", types, default=types)
    if sel_type:
        df_f = df_f[df_f["type"].isin(sel_type)]

# Condición
if "condition" in df_f.columns:
    conditions = sorted(df_f["condition"].dropna().unique().tolist())
    sel_cond = st.sidebar.multiselect("Condición", conditions, default=conditions)
    if sel_cond:
        df_f = df_f[df_f["condition"].isin(sel_cond)]

# Precio
if "price" in df_f.columns and df_f["price"].notna().any():
    p_min, p_max = safe_minmax(df_f["price"])
    p_min, p_max = int(p_min), int(p_max)
    price_range = st.sidebar.slider(
        "Rango de precio",
        p_min,
        p_max,
        (p_min, p_max)
    )
    df_f = df_f[df_f["price"].between(price_range[0], price_range[1])]

st.sidebar.write(f"Filas tras filtros: **{len(df_f):,}**")

# ---------------- Tabs ----------------
tab1, tab2 = st.tabs(["Explorar datos", "Gráficos"])

# ================= TAB 1: Explore =================
with tab1:
    st.subheader("Exploración del dataset")

    # Column selector
    cols = df_f.columns.tolist()
    default_cols = cols[:8] if len(cols) > 8 else cols
    cols_to_show = st.multiselect("Columnas a mostrar", cols, default=default_cols)

    st.dataframe(df_f[cols_to_show].head(100), use_container_width=True)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Filas", f"{len(df_f):,}")
    c2.metric("Columnas", f"{df_f.shape[1]}")
    if "price" in df_f.columns and df_f["price"].notna().any():
        c3.metric("Precio medio", f"{df_f['price'].mean():,.0f}")

    # Download filtered dataset
    st.download_button(
        "Descargar datos filtrados (CSV)",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="vehicles_filtered.csv",
        mime="text/csv",
    )

    st.divider()

    # ---- Data viewer like the example ----
    st.markdown("### Data viewer")

    if "model" in df_f.columns and df_f["model"].notna().any():
        min_ads = st.slider(
            "Mínimo de anuncios por modelo",
            min_value=1,
            max_value=5000,
            value=1000,
            step=50
        )
        include_small = st.checkbox(
            "Incluir modelos con menos anuncios que el mínimo",
            value=True
        )

        model_counts = df_f["model"].value_counts()

        if include_small:
            df_view = df_f.copy()
        else:
            keep_models = model_counts[model_counts >= min_ads].index
            df_view = df_f[df_f["model"].isin(keep_models)]

        st.dataframe(df_view.head(200), use_container_width=True)
        st.caption(f"Mostrando **{len(df_view):,}** filas en el Data viewer.")
    else:
        st.info("No se encontró la columna 'model' para construir el Data viewer.")

# ================= TAB 2: Charts =================
with tab2:
    st.subheader("Visualizaciones")

    show_hist = st.checkbox("Mostrar histograma (odometer)", value=True)
    show_scatter = st.checkbox("Mostrar dispersión (odometer vs price)", value=True)
    show_cond_year = st.checkbox("Mostrar histograma (condition vs model_year)", value=True)
    show_compare = st.checkbox("Comparar distribución de precio (2 modelos)", value=True)
    show_stacked = st.checkbox("Mostrar tipos de vehículo por modelo", value=True)

    st.divider()

    # ---- Histogram odometer ----
    if show_hist:
        st.markdown("### Histograma del kilometraje (odometer)")
        if "odometer" in df_f.columns and df_f["odometer"].notna().any():
            fig = px.histogram(df_f.dropna(subset=["odometer"]), x="odometer", nbins=50)
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning("No hay datos suficientes en 'odometer' para graficar.")

    # ---- Scatter odometer vs price ----
    if show_scatter:
        st.markdown("### Dispersión: odometer vs price")
        if {"odometer", "price"}.issubset(df_f.columns):
            data_sc = df_f.dropna(subset=["odometer", "price"])
            if not data_sc.empty:
                color_col = "condition" if "condition" in data_sc.columns else None
                fig = px.scatter(
                    data_sc,
                    x="odometer",
                    y="price",
                    color=color_col,
                    opacity=0.4,
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.warning("No hay filas con odometer y price para graficar.")
        else:
            st.warning("Faltan columnas 'odometer' y/o 'price'.")

    # ---- Histogram condition vs model_year ----
    if show_cond_year:
        st.markdown("### Histogram of condition vs model_year")
        if {"model_year", "condition"}.issubset(df_f.columns):
            data_h = df_f.dropna(subset=["model_year", "condition"])
            if not data_h.empty:
                fig = px.histogram(
                    data_h,
                    x="model_year",
                    color="condition",
                    nbins=40
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.warning("No hay datos suficientes para 'model_year' y 'condition'.")
        else:
            st.warning("Faltan columnas 'model_year' y/o 'condition'.")

    # ---- Compare price distribution between 2 models ----
    if show_compare:
        st.markdown("### Compare price distribution between models")

        if {"model", "price"}.issubset(df_f.columns):
            # Top modelos para que el selector sea útil y rápido
            top_models = df_f["model"].value_counts().head(30).index.tolist()

            if len(top_models) >= 2:
                m1 = st.selectbox("Select model 1", top_models, index=0)
                m2 = st.selectbox("Select model 2", top_models, index=1)

                normalize = st.checkbox("Normalize histogram", value=True)

                data_cmp = df_f[df_f["model"].isin([m1, m2])].dropna(subset=["price"])
                histnorm = "percent" if normalize else None

                if not data_cmp.empty:
                    fig = px.histogram(
                        data_cmp,
                        x="price",
                        color="model",
                        nbins=40,
                        histnorm=histnorm,
                        barmode="overlay",
                        opacity=0.6
                    )
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.warning("No hay datos de price para los modelos seleccionados.")
            else:
                st.warning("No hay suficientes modelos para comparar (se necesitan al menos 2).")
        else:
            st.warning("Faltan columnas 'model' y/o 'price'.")

    # ---- Stacked: vehicle types by model ----
    if show_stacked:
        st.markdown("### Vehicle types by model")
        if {"model", "type"}.issubset(df_f.columns):
            top_models = df_f["model"].value_counts().head(15).index
            data_stack = df_f[df_f["model"].isin(top_models)]

            if not data_stack.empty:
                fig = px.histogram(
                    data_stack,
                    x="model",
                    color="type",
                    barmode="stack"
                )
                fig.update_layout(xaxis_title="model", yaxis_title="count")
                st.plotly_chart(fig, width="stretch")
            else:
                st.warning("No hay datos suficientes para construir el gráfico apilado.")
        else:
            st.warning("Faltan columnas 'model' y/o 'type'.")
