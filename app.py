import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# 1. Configuración de la página web
st.set_page_config(
    page_title="Optimizador Inmobiliario", page_icon="🏡", layout="wide"
)

st.title("🏡 Optimizador Inmobiliario")
st.markdown("### Sistema Experto de Búsqueda de Primera Vivienda")
st.markdown(
    "Definí tus criterios en el menú lateral y nuestro motor de inferencia"
    " filtrará las mejores opciones del mercado."
)


# 2. Carga de datos
@st.cache_data
def cargar_datos():
  file_id = "1eNFGYL2YttBPRyZjjkJJEBm8y-N3Fg7U"
  url = f"https://drive.google.com/uc?id={file_id}"

  inmuebles = pd.read_csv(url, sep=";")
  inmuebles = inmuebles.drop_duplicates()

  columnas_utiles = [
      "property_type",
      "place_with_parent_names",
      "price",
      "price_aprox_usd",
      "surface_total_in_m2",
      "rooms",
  ]
  df_limpio = inmuebles[columnas_utiles].copy()
  df_limpio = df_limpio.dropna(subset=["price"])
  df_limpio["rooms"] = df_limpio["rooms"].fillna(2)

  return df_limpio


df_limpio = cargar_datos()

# 3. Interfaz del Menú Lateral
st.sidebar.header("🔍 Filtros del Sistema Experto")

opcion_tipo = st.sidebar.selectbox(
    "1. ¿Qué tipo de propiedad buscas?",
    ["Todos / Indiferente", "Departamento (apartment)", "Casa (house)", "PH"],
)

presupuesto = st.sidebar.number_input(
    "2. Presupuesto máximo (USD) - 0 para sin límite:",
    min_value=0,
    value=150000,
    step=10000,
)

ambientes = st.sidebar.number_input(
    "3. Cantidad mínima de ambientes:", min_value=1, value=2, step=1
)

barrio = st.sidebar.text_input("4. ¿Algún barrio o zona específica? (Opcional)")

excluir = st.sidebar.text_input("5. ¿Querés excluir alguna zona? (Opcional)")

# 4. Botón de Búsqueda y Lógica
```python
# 4. Botón de Búsqueda y Lógica
if st.sidebar.button("Buscar Propiedades 🚀"):
    url_n8n = "https://nancyriquelme.app.n8n.cloud/webhook-test/buscar-propiedades"

    parametros = {
        "Tipo": opcion_tipo,
        "presupuesto": presupuesto,
        "Ambientes": ambientes,
        "barrio": barrio,
        "excluir": excluir,
    }

    try:
        with st.spinner("Buscando propiedades con n8n..."):
            respuesta = requests.post(
                url_n8n,
                json=parametros,
                timeout=120,
            )
            respuesta.raise_for_status()
            datos = respuesta.json()

        if isinstance(datos, dict):
            datos = datos.get("data", datos.get("items", []))

        df_filtrado = pd.DataFrame(datos)

        st.subheader(
            f"✅ Propiedades que cumplen con las reglas: {len(df_filtrado)}"
        )

        if not df_filtrado.empty:
            columnas = [
                "property_type",
                "price_aprox_usd",
                "surface_total_in_m2",
                "rooms",
                "place_with_parent_names",
            ]

            columnas_disponibles = [
                columna
                for columna in columnas
                if columna in df_filtrado.columns
            ]

            columnas_orden = [
                columna
                for columna in [
                    "surface_total_in_m2",
                    "price_aprox_usd",
                ]
                if columna in df_filtrado.columns
            ]

            if columnas_orden:
                df_filtrado = df_filtrado.sort_values(
                    by=columnas_orden,
                    ascending=False,
                )

            st.markdown("#### 🏆 Top 5 de opciones recomendadas:")

            vista_top5 = df_filtrado[columnas_disponibles].head(5).copy()

            if "price_aprox_usd" in vista_top5.columns:
                vista_top5["price_aprox_usd"] = vista_top5[
                    "price_aprox_usd"
                ].apply(
                    lambda x: f"USD {float(x):,.0f}"
                    if pd.notna(x)
                    else "Sin precio"
                )

            st.dataframe(vista_top5, use_container_width=True)

            if {
                "surface_total_in_m2",
                "price_aprox_usd",
                "property_type",
            }.issubset(df_filtrado.columns):
                st.markdown(
                    "#### 📊 Relación Superficie vs. Precio (Top 200)"
                )

                sns.set_theme(style="whitegrid")
                fig, ax = plt.subplots(figsize=(10, 5))

                sns.scatterplot(
                    data=df_filtrado.head(200),
                    x="surface_total_in_m2",
                    y="price_aprox_usd",
                    hue="property_type",
                    alpha=0.8,
                    s=70,
                    palette="viridis",
                    ax=ax,
                )

                ax.set_xlabel("Superficie Total (m²)")
                ax.set_ylabel("Precio (USD)")
                ax.yaxis.set_major_formatter(
                    ticker.FuncFormatter(lambda x, p: f"${x:,.0f}")
                )

                ax.legend(
                    title="Tipo de Propiedad",
                    bbox_to_anchor=(1.05, 1),
                    loc="upper left",
                )

                st.pyplot(fig)

        else:
            st.warning(
                "
```
