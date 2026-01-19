import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- Page setup ----------------
st.set_page_config(
    page_title="Vehicles Dashboard",
    layout="wide"
)

st.title("Dashboard: Anuncios de venta de coches (USA)")
st.caption(
    "By: Monica Magdub Lopez
)

# ---------------- Load data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("vehicles_us.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# ---------------- Sidebar: filters ----------------
st.sidebar.header("Filtros")
df_f = df.copy()

# Año del modelo
if "model_year" in df_f.columns and df_f["model_year"].notna().any():
    min_year = int(df_f["model_year"].dropna().min())
    max_year = int(df_f["model_year"].dropna().max())
    year_range = st.sidebar.slider(
        "Año del modelo",
        min_year,
        max_year,
        (min_year, max_year)
    )
    df_f = df_f[df_f["model_year"].between(year_range[0], year_range[1])]

# Tipo de vehículo
if "type" in df_f.columns:
    types = sorted(df_f["type"].dropna().unique())
    sel_type = st.sidebar.multiselect(
        "Tipo de vehículo",
        types,
        default=types
    )
    if sel_type:
        df_f = df_f[df_f["type"].isin(sel_type)]

# Condición
if "condition" in df_f.columns:
    conditions = sorted(df_f["condition"].dropna().unique())
    sel_cond = st.sidebar.multiselect(
        "Condición",
        conditions,
        default=conditions
    )
    if sel_cond:
        df_f = df_f[df_f["condition"].isin(sel_cond)]

# Precio
if "price" in df_f.columns and df_f["price"].notna().any():
    p_min = int(df_f["price"].dropna().min())
    p_max = int(df_f["price"].dropna().max())
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

# ================= TAB 1 =================
with tab1:
    st.subheader("Exploración del dataset")

    all_cols = df_f.columns.tolist()
    default_cols = all_cols[:8] if len(all_cols) > 8 else all_cols
    cols_to_show = st.multiselect(
        "Columnas a mostrar",
        all_cols,
        default=default_cols
    )

    st.dataframe(df_f[cols_to_show].head(100), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Filas", f"{len(df_f):,}")
    c2.metric("Columnas", f"{df_f.shape[1]}")
    if "price" in df_f.columns:
        c3.metric("Precio medio", f"{df_f['price'].mean():,.0f}")

    st.download_button(
        "Descargar datos filtrados (CSV)",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="vehicles_filtered.csv",
        mime="text/csv"
    )

# ================= TAB 2 =================
with tab2:
    st.subheader("Visualizaciones")

    show_hist = st.checkbox("Mostrar histograma (odometer)", value=True)
    show_scatter = st.checkbox("Mostrar dispersión (odometer vs price)", value=True)
    show_stacked = st.checkbox("Mostrar tipos de vehículo por modelo", value=True)

    st.divider()

    # ---- Histogram ----
    if show_hist and "odometer" in df_f.columns:
        st.markdown("### Histograma del kilometraje (odometer)")
        fig = px.histogram(df_f, x="odometer", nbins=50)
        st.plotly_chart(fig, width="stretch")

    # ---- Scatter ----
    if show_scatter and {"odometer", "price"}.issubset(df_f.columns):
        st.markdown("### Dispersión: odometer vs price")
        color_col = "condition" if "condition" in df_f.columns else None
        fig = px.scatter(
            df_f,
            x="odometer",
            y="price",
            color=color_col,
            opacity=0.4
        )
        st.plotly_chart(fig, width="stretch")

    # ---- Stacked bar (FINAL FIX) ----
    if show_stacked and {"model", "type"}.issubset(df_f.columns):
        st.markdown("### Vehicle types by model")

        top_models = df_f["model"].value_counts().head(15).index
        df_top = df_f[df_f["model"].isin(top_models)]

        fig = px.histogram(
            df_top,
            x="model",
            color="type",
            barmode="stack"
        )
        fig.update_layout(xaxis_title="model", yaxis_title="count")
        st.plotly_chart(fig, width="stretch")

