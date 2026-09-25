"""Figures for the PDF report (reads results/ and dashboard/osint/)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "fig"
FIG.mkdir(parents=True, exist_ok=True)
D = json.load(open(ROOT / "results" / "dashboard_data.json"))
REC = json.load(open(ROOT / "results" / "recomendaciones.json"))
YEARS = np.array(D["meta"]["years"])
ISO = D["meta"]["iso3"]

INK, MUTED, GRID = "#18222c", "#6b7682", "#e3e7eb"
C = dict(data="#18222c", model="#2a78d6", fc="#e8662f", proj="#c2408a", rl="#1baf7a", amber="#d99400", violet="#6a55c9")
CHC = dict(k="#2a78d6", r="#e8662f", m="#1baf7a", x="#d99400", f="#c2408a", w="#2f7d32")
CHN = dict(k="Capital", r="Tecnología", m="Importar del centro", x="Extracción propia", f="Recursos fuera", w="Redistribuir")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
                     "figure.dpi": 200, "savefig.bbox": "tight"})


def arr(scn, var):
    a = D["scenarios"].get(scn, {}).get(var)
    return None if a is None else np.array([[np.nan if v is None else v for v in row] for row in a], float)


def save(fig, name):
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)


def diagram():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis("off"); ax.grid(False)
    def box(x, y, w, h, t, s, col):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc=col, ec=INK, lw=0.8, alpha=0.95))
        ax.text(x + w / 2, y + h * 0.62, t, ha="center", va="center", fontsize=9, weight="bold", color=INK)
        ax.text(x + w / 2, y + h * 0.28, s, ha="center", va="center", fontsize=7, color=INK)
    def arrow(a, b, col, txt="", off=(0, 0), rad=0.0):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, color=col, lw=1.3, connectionstyle=f"arc3,rad={rad}"))
        if txt:
            ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], txt, fontsize=6.8, color=col, ha="center")
    box(2, 34, 26, 12, "Periferia", "asabiya ↑ en la frontera", "#fde6da")
    box(72, 34, 26, 12, "Centro", "élites capturan rentas", "#dbe9fb")
    box(37, 48, 26, 11, "Frontera tecnológica", "difusión + saltos (Poisson)", "#eef2f5")
    box(2, 4, 26, 12, "Recursos (Hubbert)", "capacidad logística", "#fcf0d2")
    box(37, 4, 26, 12, "Deuda y crisis", "ahorro, crédito externo", "#e7e4f8")
    box(72, 4, 26, 12, "Estrés político (PSI)", "MMP × EMP × SFD → conflicto", "#f3d9d9")
    box(37, 21, 26, 12, "Decisión de cada país", "k · r · m · x · f · w + gasto", "#d8f3e8")
    arrow((28, 42), (72, 42), C["fc"], "intercambio desigual, rentas de monopolio, intereses", (0, 4.2), rad=-0.15)
    arrow((72, 37), (28, 37), C["model"], "bienes de alto valor, capital, concesiones", (0, -1.2), rad=0.12)
    arrow((50, 33.5), (50, 48), C["rl"], "invertir r", (6, -2))
    arrow((44, 21), (18, 16), C["amber"], "extraer x / fuera f", (-6, 0))
    arrow((50, 21), (50, 16), C["violet"], "financiar", (5, 0))
    arrow((85, 34), (85, 16), "#b03a3a", "élites y masas", (8, 0))
    arrow((72, 10), (63, 10), MUTED)
    ax.text(50, 60.5, "Arquitectura del modelo: un agente por país, 1950–2030", ha="center", fontsize=9.5, weight="bold", color=INK)
    save(fig, "f01_arquitectura")


def gdp_paths():
    show = ["USA", "CHN", "KOR", "BRA", "IND", "NGA", "MEX", "RUS"]
    ly_d, ly_m, ly_f = arr("datos", "ly"), arr("modelo_hist", "ly"), arr("pronostico", "ly")
    p10, p90 = arr("pronostico", "ly_p10"), arr("pronostico", "ly_p90")
    ly_p, q10, q90 = arr("proyeccion", "ly"), arr("proyeccion", "ly_p10"), arr("proyeccion", "ly_p90")
    fig, axs = plt.subplots(2, 4, figsize=(7.6, 4.1), sharex=True)
    for ax, c in zip(axs.flat, show):
        i = ISO.index(c)
        ax.fill_between(YEARS, np.exp(p10[i]), np.exp(p90[i]), color=C["fc"], alpha=0.15, lw=0)
        ax.fill_between(YEARS, np.exp(q10[i]), np.exp(q90[i]), color=C["proj"], alpha=0.15, lw=0)
        ax.plot(YEARS, np.exp(ly_d[i]), color=C["data"], lw=1.6, label="Datos (PWT)")
        ax.plot(YEARS, np.exp(ly_m[i]), color=C["model"], lw=1.1, label="Modelo con acciones observadas")
        ax.plot(YEARS, np.exp(ly_f[i]), color=C["fc"], lw=1.1, label="Pronóstico desde 1990")
        ax.plot(YEARS, np.exp(ly_p[i]), color=C["proj"], lw=1.1, label="Proyección 2020–2030")
        ax.set_yscale("log"); ax.set_title(D["meta"]["names"][i], fontsize=8.5, color=INK)
        ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(1, 2, 5)))
        ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v/1000:g}k" if v >= 1000 else f"{v:g}"))
        ax.axvline(1990, color=MUTED, lw=0.6, ls=":")
        ax.tick_params(labelsize=6.5)
    axs[0, 0].legend(loc="upper left", fontsize=5.8, bbox_to_anchor=(0, -1.55), ncol=4)
    fig.suptitle("PIB per cápita (USD PPA 2017, escala log): datos, modelo y pronósticos", fontsize=9.5, color=INK)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97))
    save(fig, "f02_trayectorias")


def validation():
    v = D["validacion"]["gdp"]
    hs = ["1", "5", "10"]
    methods = [("completo", "Modelo", C["model"]), ("ar1_crecimiento", "AR(1) crecimiento", MUTED), ("panel_directo", "Regresión panel", "#9aa3ab"),
               ("persistencia", "Persistencia", "#c9ced3"), ("politica_congelada", "Modelo, política congelada", C["rl"])]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6))
    w = 0.16
    for k, (m, n, col) in enumerate(methods):
        axs[0].bar(np.arange(3) + (k - 2) * w, [v[h][m]["crps"] for h in hs], w, color=col, label=n)
    axs[0].set_xticks(range(3), ["1 año", "5 años", "10 años"]); axs[0].set_title("CRPS del log PIB pc (menor es mejor)", fontsize=8.5)
    axs[0].legend(fontsize=6.3, loc="upper left")
    cov = [v[h]["completo"]["cobertura_80"] for h in hs]
    axs[1].bar(range(3), cov, 0.5, color=C["model"]); axs[1].axhline(0.8, color=C["fc"], ls="--", lw=1)
    axs[1].text(2.3, 0.81, "nominal 80 %", color=C["fc"], fontsize=7, ha="right")
    axs[1].set_xticks(range(3), ["1 año", "5 años", "10 años"]); axs[1].set_ylim(0, 1); axs[1].set_title("Cobertura de la banda p10–p90", fontsize=8.5)
    for i, c in enumerate(cov): axs[1].text(i, c + 0.02, f"{c:.0%}", ha="center", fontsize=7)
    fig.tight_layout(); save(fig, "f03_validacion")


def ablations():
    v = D["validacion"]
    base = v["gdp"]["10"]["completo"]["crps"]
    auc0 = v["conf"]["10"]["completo"]["auc"]
    names = {"sin_sistema_mundo": "Sistema-mundo", "sin_demografia_estructural": "Demografía estructural", "sin_frontera_metaetnica": "Frontera metaétnica",
             "sin_politica_de_recursos": "Política de recursos", "sin_deuda_crisis": "Deuda y crisis", "sin_instituciones": "Instituciones",
             "sin_clima_ecologia": "Clima y ecología", "politica_congelada": "Regla de decisión (vs. congelada)"}
    ks = list(names)
    d_crps = [(v["gdp"]["10"][k]["crps"] - base) * 1000 for k in ks]
    d_auc = [(auc0 - v["conf"]["10"][k]["auc"]) * 100 for k in ks]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    y = np.arange(len(ks))
    axs[0].barh(y, d_crps, color=[C["model"] if x > 0 else "#c9ced3" for x in d_crps])
    axs[0].set_yticks(y, [names[k] for k in ks], fontsize=7); axs[0].axvline(0, color=INK, lw=0.6)
    axs[0].set_title("Aporte al PIB a 10 años\n(aumento del CRPS × 1000 al quitarlo)", fontsize=8)
    axs[1].barh(y, d_auc, color=[C["fc"] if x > 0 else "#c9ced3" for x in d_auc]); axs[1].axvline(0, color=INK, lw=0.6)
    axs[1].set_title("Aporte al conflicto a 10 años\n(caída del AUC × 100 al quitarlo)", fontsize=8)
    fig.tight_layout(); save(fig, "f04_ablaciones")


def irl():
    e = D["irl"]
    f = ["bienestar", "poder", "elite", "paz", "autonomia", "inercia"]
    lab = ["Bienestar", "Poder", "Ingreso élite", "Paz", "Autonomía", "Inercia"]
    th = [e["theta_std"][k] for k in f]
    ci = np.array([e["theta_std_ic90"][k] for k in f])
    fig, axs = plt.subplots(1, 2, figsize=(7.3, 2.8), gridspec_kw={"width_ratios": [1, 1.25]})
    y = np.arange(len(f))[::-1]
    axs[0].barh(y, th, color=[C["model"] if t >= 0 else C["fc"] for t in th], height=0.6)
    axs[0].errorbar(th, y, xerr=[np.array(th) - ci[:, 0], ci[:, 1] - np.array(th)], fmt="none", ecolor=INK, lw=0.8, capsize=2)
    axs[0].set_yticks(y, lab); axs[0].axvline(0, color=INK, lw=0.6); axs[0].set_xlim(-1, 1)
    axs[0].set_title(f"Recompensa revelada (norma 1, IC 90 %)\nracionalidad {e['racionalidad']:.0%}", fontsize=8)
    groups = [("Periferia", e["por_zona"]["periferia"]), ("Semiperiferia", e["por_zona"]["semiperiferia"]), ("Centro", e["por_zona"]["centro"]),
              ("Democracias", e["por_regimen"]["democracias"]), ("Autocracias", e["por_regimen"]["autocracias"])]
    M = np.array([[g[1]["theta_std"][k] for k in f] for g in groups])
    im = axs[1].imshow(M, cmap="RdBu", vmin=-1, vmax=1, aspect="auto")
    axs[1].set_xticks(range(len(f)), lab, rotation=35, ha="right", fontsize=7); axs[1].set_yticks(range(len(groups)), [g[0] for g in groups], fontsize=7.5)
    axs[1].grid(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            axs[1].text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color="white" if abs(M[i, j]) > 0.5 else INK)
    axs[1].set_title("Pesos por grupo", fontsize=8)
    fig.tight_layout(); save(fig, "f05_irl")


def allocation():
    S = json.load(open(ROOT / "results" / "summary.json"))["resumen"]
    rows = [("Datos observados", S["datos_asignacion_por_zona"]), ("Modelo, acciones observadas", S["modelo_hist"]["asignacion_por_zona"])]
    rows += [(f"RL · {n}", S["rl"][m]["asignacion_por_zona"]) for m, n in (("bienestar", "Bienestar"), ("poder", "Poder"), ("elite", "Élite"), ("irl", "Recompensa revelada"))]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    labels, y = [], 0
    for name, az in rows:
        for zn in ("centro", "periferia"):
            a = az[zn]; tot = sum(a.values()); left = 0
            for c in "krmxfw":
                ax.barh(y, a[c] / tot, left=left, color=CHC[c], height=0.8, label=CHN[c] if y == 0 else None)
                left += a[c] / tot
            labels.append(f"{name} · {zn}"); y += 1
        y += 0.4
    ax.set_yticks([i + (i // 2) * 0.4 for i in range(len(labels))], labels, fontsize=6.8); ax.invert_yaxis()
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1)); ax.grid(False)
    ax.legend(ncol=6, fontsize=6.3, loc="upper center", bbox_to_anchor=(0.45, 1.13))
    fig.tight_layout(); save(fig, "f06_asignacion")


def recommendations():
    P = REC["bienestar"]["paises"]
    ly = arr("datos", "ly")[:, 69]
    q80, q50 = np.nanquantile(ly, 0.8), np.nanquantile(ly, 0.5)
    zone = {iso: (2 if ly[i] >= q80 else 1 if ly[i] >= q50 else 0) for i, iso in enumerate(ISO) if np.isfinite(ly[i])}
    fig, axs = plt.subplots(1, 2, figsize=(7.3, 2.7))
    w = 0.26
    for zi, (zn, col) in enumerate(((0, "#e8662f"), (1, "#1baf7a"), (2, "#2a78d6"))):
        mem = [p for k, p in P.items() if zone.get(k) == zn]
        vals = [np.mean([p["cambio_pp"][c] for p in mem]) for c in "krmxfw"]
        axs[0].bar(np.arange(6) + (zi - 1) * w, vals, w, color=col, label=["Periferia", "Semiperiferia", "Centro"][zi])
    axs[0].set_xticks(range(6), [CHN[c] for c in "krmxfw"], rotation=30, ha="right", fontsize=7); axs[0].axhline(0, color=INK, lw=0.6)
    axs[0].set_title("Cambio recomendado 2020–2024\n(puntos del PIB frente a la regla, bienestar)", fontsize=8); axs[0].legend(fontsize=6.5)
    lp = REC["bienestar"]["largo_plazo"]
    yrs = lp["anios"]
    axs[1].plot(yrs, np.array(lp["lc"]) * 100, color=C["rl"], lw=1.8, label="Consumo per cápita")
    axs[1].plot(yrs, np.array(lp["ly"]) * 100, color=C["fc"], lw=1.8, label="PIB per cápita")
    axs[1].axhline(0, color=INK, lw=0.6); axs[1].set_ylabel("% frente a la regla (log × 100)", fontsize=7)
    axs[1].set_title("Largo plazo: misma política desde 2000", fontsize=8); axs[1].legend(fontsize=6.8)
    fig.tight_layout(); save(fig, "f07_recomendaciones")


def climate():
    m = D["mundo"]
    t = np.arange(1950, 1950 + len(m["tg_obs"]))
    g = lambda k: np.array([np.nan if x is None else x for x in m[k]], float)
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6))
    axs[0].plot(t, g("tg_obs"), color=C["data"], lw=1.3, label="Observada (HadCRUT/GISTEMP)")
    axs[0].plot(t, g("tg_pronostico_1990"), color=C["fc"], lw=1.6, label="Pronóstico desde 1990")
    axs[0].plot(t, g("tg_proyeccion"), color=C["proj"], lw=1.6, label="Proyección 2020–2030")
    axs[0].set_title("Temperatura global (°C sobre el preindustrial)", fontsize=8); axs[0].legend(fontsize=6.3)
    axs[1].plot(t, g("co2_obs") / 1000, color=C["data"], lw=1.3, label="Observadas (GCP)")
    axs[1].plot(t, g("co2_pronostico_1990") / 1000, color=C["fc"], lw=1.6, label="Pronóstico desde 1990")
    axs[1].set_title("Emisiones de CO₂ fósil (Gt/año)", fontsize=8); axs[1].legend(fontsize=6.3)
    fig.tight_layout(); save(fig, "f08_clima")


def conflicts():
    ged = json.load(open(ROOT / "dashboard" / "osint" / "conflictos_ged.json"))
    mod = json.load(open(ROOT / "dashboard" / "osint" / "modelo.json"))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.4))
    ys = sorted(int(y) for y in ged["muertes_por_anio"])
    axs[0].bar(ys, [ged["muertes_por_anio"][str(y)] / 1000 for y in ys], color="#d04a3a")
    axs[0].set_title("Muertes en eventos de violencia organizada (miles, UCDP GED)", fontsize=8)
    yc = sorted(int(y) for y in mod["conflictos_por_anio"])
    axs[1].plot(yc, [len(mod["conflictos_por_anio"][str(y)]) for y in yc], color="#d04a3a", lw=1.6)
    haz = arr("modelo_hist", "conflict")
    axs[1].plot(YEARS[:70], np.nansum(haz[:, :70], 0), color=C["model"], lw=1.2, label="Modelo: conflictos esperados")
    axs[1].set_title("Países con conflicto armado activo (UCDP/PRIO)", fontsize=8); axs[1].legend(fontsize=6.5)
    fig.tight_layout(); save(fig, "f09_conflictos")


if __name__ == "__main__":
    for f in (diagram, gdp_paths, validation, ablations, irl, allocation, recommendations, climate, conflicts):
        f(); print("ok", f.__name__)
