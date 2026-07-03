
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from io import BytesIO

st.set_page_config(page_title="Gráfico Simple de Cojinete", page_icon="📊", layout="wide")

st.title("📊 Medición de Cojinetes Big End Bearing")
st.caption("Ingrese valores 5x3 y genere una representación visual sencilla y práctica.")

st.sidebar.header("Datos generales")
equipo = st.sidebar.text_input("Equipo / Unidad", "GENSET 11")
cilindro = st.sidebar.text_input("Cilindro", "A1")
posicion = st.sidebar.selectbox("Posición", ["UPPER", "LOWER"])
titulo = f"{cilindro} {posicion}"

st.subheader("Ingrese mediciones en mm")

valores = []
headers = ["A - Interior", "B - Centro", "C - Exterior"]
cols = st.columns(3)

for j, col in enumerate(cols):
    with col:
        st.markdown(f"**{headers[j]}**")
        columna = []
        for i in range(5):
            v = st.number_input(
                f"{headers[j]} / Posición {i+1}",
                value=1.00,
                step=0.01,
                format="%.2f",
                key=f"{j}_{i}"
            )
            columna.append(v)
        valores.append(columna)

arr = np.array(valores).T

def interp_surface(arr, nx=220, ny=150):
    x = np.arange(1, 6)
    y = np.arange(1, 4)
    xi = np.linspace(1, 5, nx)
    temp = np.array([np.interp(xi, x, arr[:, j]) for j in range(3)])
    yi = np.linspace(1, 3, ny)
    zi = np.array([np.interp(yi, y, temp[:, i]) for i in range(nx)]).T
    X, Y = np.meshgrid(xi, yi)
    return X, Y, zi

def wear_centroid(arr):
    wear = arr.max() - arr
    total = wear.sum()
    Xp, Yp = np.meshgrid(np.arange(1, 6), np.arange(1, 4), indexing="ij")
    if total <= 0:
        return 3, 2
    return (Xp * wear).sum() / total, (Yp * wear).sum() / total

def condition(arr):
    minimo = arr.min()
    rango = arr.max() - arr.min()
    if minimo < 0.85 or rango > 0.50:
        return "REVISAR", "#d7191c"
    elif minimo < 1.05 or rango > 0.28:
        return "MONITOREAR", "#f5b400"
    return "NORMAL", "#228b22"

def crear_grafico(arr, equipo, titulo):
    cmap = LinearSegmentedColormap.from_list(
        "wear_scale",
        ["#b30000", "#e34a33", "#fdbb84", "#fee08b", "#d9ef8b", "#66bd63", "#1a9850"]
    )

    vmin = np.floor((arr.min() - 0.02) * 100) / 100
    vmax = np.ceil((arr.max() + 0.02) * 100) / 100
    norm = Normalize(vmin=vmin, vmax=vmax)

    fig = plt.figure(figsize=(13, 8), dpi=180)
    fig.patch.set_facecolor("white")

    fig.text(0.04, 0.94, "MEDICIÓN DE COJINETES BIG END BEARING",
             fontsize=18, fontweight="bold", color="#0b2545")
    fig.text(0.04, 0.905, f"Equipo: {equipo}   |   {titulo}   |   Rojo = menor espesor / mayor desgaste",
             fontsize=10, color="#0b55b8")

    ax = fig.add_axes([0.07, 0.22, 0.55, 0.58])
    X, Y, Z = interp_surface(arr)

    ax.imshow(
        Z.T,
        origin="lower",
        extent=[1, 5, 1, 3],
        cmap=cmap,
        norm=norm,
        interpolation="bicubic",
        aspect="auto"
    )

    levels = np.linspace(vmin, vmax, 5)
    cs = ax.contour(X, Y, Z, levels=levels, colors="#0b2545", linewidths=0.45, alpha=0.35)
    ax.clabel(cs, fontsize=7, inline=True, fmt="%.2f")

    for i in range(5):
        for j in range(3):
            ax.scatter(i+1, j+1, s=45, facecolor="white", edgecolor="black", linewidth=0.9, zorder=4)
            ax.text(i+1, j+1, f"{arr[i,j]:.2f}",
                    ha="center", va="center", fontsize=7, color="#0b2545", zorder=5)

    min_idx = np.unravel_index(np.argmin(arr), arr.shape)
    ax.scatter(min_idx[0]+1, min_idx[1]+1, s=120, marker="s",
               facecolor="none", edgecolor="black", linewidth=1.6, zorder=6)

    cx, cy = wear_centroid(arr)
    ax.scatter(cx, cy, s=110, facecolor="white", edgecolor="black", linewidth=2.0, zorder=7)
    ax.scatter(cx, cy, s=25, facecolor="#0b2545", edgecolor="white", linewidth=0.6, zorder=8)
    ax.text(cx + 0.12, cy + 0.08, "Centroide", fontsize=8, fontweight="bold", color="#0b2545")

    ax.set_xlim(1, 5)
    ax.set_ylim(1, 3)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["A\nInterior", "B\nCentro", "C\nExterior"], fontsize=9)
    ax.set_xlabel("Posición circunferencial 1 → 5", fontsize=10)
    for sp in ax.spines.values():
        sp.set_visible(False)

    ax_tbl = fig.add_axes([0.68, 0.48, 0.25, 0.28])
    ax_tbl.axis("off")
    table_data = [["P", "A", "B", "C"]]
    for i in range(5):
        table_data.append([str(i+1)] + [f"{arr[i,j]:.2f}" for j in range(3)])

    tbl = ax_tbl.table(cellText=table_data, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.1, 1.3)

    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#c5d0df")
        cell.set_linewidth(0.5)
        if r == 0:
            cell.set_facecolor("#0b2545")
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")

    ax_tbl.set_title("LECTURA VISUAL (mm)", fontsize=10, color="#0b2545", fontweight="bold")

    promedio = arr.mean()
    minimo = arr.min()
    maximo = arr.max()
    rango = maximo - minimo
    estado, color_estado = condition(arr)

    ax_kpi = fig.add_axes([0.68, 0.23, 0.25, 0.18])
    ax_kpi.axis("off")

    kpis = [
        ("PROMEDIO", promedio, "#0b2545"),
        ("MÍNIMO", minimo, "red"),
        ("MÁXIMO", maximo, "#168323"),
        ("RANGO", rango, "#0b2545")
    ]

    for idx, (label, value, color) in enumerate(kpis):
        x = (idx % 2) * 0.50
        y = 0.63 if idx < 2 else 0.18
        ax_kpi.text(x + 0.23, y + 0.16, label, ha="center", fontsize=8, color=color, fontweight="bold")
        ax_kpi.text(x + 0.23, y, f"{value:.2f} mm", ha="center", fontsize=13, color=color, fontweight="bold")

    fig.text(0.72, 0.14, f"CONDICIÓN: {estado}",
             fontsize=16, color=color_estado, fontweight="bold")

    ax_scale = fig.add_axes([0.08, 0.08, 0.35, 0.04])
    grad = np.linspace(vmin, vmax, 256).reshape(1, -1)
    ax_scale.imshow(grad, cmap=cmap, norm=norm, aspect="auto", extent=[vmin, vmax, 0, 1])
    ax_scale.set_yticks([])
    ax_scale.set_xticks(np.linspace(vmin, vmax, 5))
    ax_scale.tick_params(axis="x", labelsize=8)
    for sp in ax_scale.spines.values():
        sp.set_visible(False)

    fig.text(0.08, 0.13, "MENOR ESPESOR / MAYOR DESGASTE", fontsize=8, color="red", fontweight="bold")
    fig.text(0.32, 0.13, "MAYOR ESPESOR", fontsize=8, color="#168323", fontweight="bold")

    return fig

if st.button("Generar gráfico", type="primary"):
    fig = crear_grafico(arr, equipo, titulo)

    png = BytesIO()
    pdf = BytesIO()

    fig.savefig(png, format="png", bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, format="pdf", bbox_inches="tight", facecolor="white")

    png.seek(0)
    pdf.seek(0)

    plt.close(fig)

    st.success("Gráfico generado correctamente.")
    st.image(png, use_container_width=True)

    st.download_button("Descargar PNG", data=png.getvalue(), file_name="grafico_cojinete.png", mime="image/png")
    st.download_button("Descargar PDF", data=pdf.getvalue(), file_name="grafico_cojinete.pdf", mime="application/pdf")
else:
    st.info("Ingrese los valores y presione 'Generar gráfico'.")
