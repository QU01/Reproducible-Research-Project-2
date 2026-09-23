"""Evaluate calibrated model + trained RL policies and export everything the dashboard needs.

Output: results/dashboard_data.json and results/summary.json
"""
import json
from pathlib import Path

import numpy as np

from calibrate import CONF, LY, T_SPLIT, W, backtest
from model import CHANNEL_NAMES, CHANNELS, Params, Simulator
from rl import N_OBS, mlp, observe, rollout, to_shares

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
MODES = ["bienestar", "poder", "elite"]
NK = 5  # number of policy archetypes
VARS = ["ly", "core", "E", "ne", "psi", "asab", "conflict", "rent_in",
        "res_share", "reserves", "fshare", "ims"] + CHANNELS


def rnd(a, d=3):
    a = np.asarray(a, float)
    out = np.round(a, d).astype(object)
    out[~np.isfinite(a)] = None
    return out.tolist()


def gini_w(x, w):
    ok = np.isfinite(x) & np.isfinite(w)
    x, w = x[ok], w[ok]
    o = np.argsort(x)
    x, w = x[o], w[o]
    cw = np.cumsum(w) / w.sum()
    cx = np.cumsum(x * w) / (x * w).sum()
    return float(1 - np.sum((cx[1:] + cx[:-1]) * np.diff(cw)) - cx[0] * cw[0])


def zone_of(ly):
    """(R?, N, T) -> zone codes by year: 2 core (top 20%), 1 semi (next 30%), 0 periphery."""
    q80 = np.nanquantile(ly, 0.8, axis=-2, keepdims=True)
    q50 = np.nanquantile(ly, 0.5, axis=-2, keepdims=True)
    z = np.where(ly >= q80, 2, np.where(ly >= q50, 1, 0)).astype(float)
    z[~np.isfinite(ly)] = np.nan
    return z


def resource_outcomes(o, price):
    """Natural-resource indicators from per-run arrays (R, N, T) and price (R, T)."""
    t19 = W.T - 1
    zr = zone_of(o["ly"])
    fs = o["fshare"][:, :, t19]
    return dict(
        precio_recursos_2019=float(np.nanmean(price[:, t19] / price[:, 20])),  # index 1970 = 1
        reservas_restantes_2019=float(np.nanmedian(o["reserves"][:, :, t19])),
        extraccion_extranjera_periferia_2019=float(np.nanmean(fs[zr[:, :, t19] == 0])),
        extraccion_extranjera_centro_2019=float(np.nanmean(fs[zr[:, :, t19] == 2])),
        dependencia_importacion_centro_2019=float(np.nanmean(o["ims"][:, :, t19][zr[:, :, t19] == 2])),
        rentas_recursos_periferia_2019=float(np.nanmean(o["res_share"][:, :, t19][zr[:, :, t19] == 0])),
    )


def outcomes(ly, conflict, E, psi=None, label=""):
    """World-level outcome indicators from mean trajectories (N, T)."""
    pop = W.pop
    t19, t70 = W.T - 1, 20
    z = zone_of(ly)
    ok = np.isfinite(z[:, t70]) & np.isfinite(z[:, t19])
    up = float(np.mean(z[ok, t19] > z[ok, t70]))
    down = float(np.mean(z[ok, t19] < z[ok, t70]))
    y19 = np.exp(ly[:, t19])
    res = dict(
        gini_2019=gini_w(y19, pop[:, t19]),
        gini_1970=gini_w(np.exp(ly[:, t70]), pop[:, t70]),
        pib_pc_mediano_2019=float(np.nanmedian(y19)),
        pib_pc_mundial_2019=float(np.nansum(y19 * pop[:, t19]) / np.nansum(pop[:, t19] * np.isfinite(y19))),
        conflicto_1990_2019=float(np.nanmean(conflict[:, 40:])),
        movilidad_ascendente=up, movilidad_descendente=down,
        elite_share_2019=float(np.nanmean(E[:, t19])) if E is not None else None,
    )
    if psi is not None:
        zc = z[:, t19] == 2
        res["psi_centro_2019"] = float(np.nanmedian(psi[zc, t19]))
        res["psi_periferia_2019"] = float(np.nanmedian(psi[z[:, t19] == 0, t19]))
    return res


def kmeans(X, k=4, seed=0, iters=100):
    rng = np.random.default_rng(seed)
    best = None
    for rep in range(10):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(iters):
            lab = np.argmin(((X[:, None] - C[None]) ** 2).sum(-1), 1)
            C2 = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(C2, C):
                break
            C = C2
        inertia = ((X - C[lab]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, lab, C)
    return best[1], best[2]


def main():
    cal = json.load(open(RES / "calibration.json"))
    params = Params().with_vector(list(cal["params"]), list(cal["params"].values()))
    years = W.years.tolist()
    data = {"meta": {
        "years": years, "iso3": W.iso3, "names": W.names, "isonum": W.isonum,
        "channels": CHANNELS, "channel_names": CHANNEL_NAMES, "t_split": 1950 + T_SPLIT,
        "pop": rnd(W.pop, 3)},
        "calibration": cal, "scenarios": {}}

    # ---- observed data
    E_obs = np.where(W.observed, 1 - W.labsh, np.nan)
    RR = np.where(W.observed, W.rr_obs, np.nan)
    data["scenarios"]["datos"] = {"ly": rnd(LY), "conflict": rnd(CONF, 0), "E": rnd(E_obs),
                                  "core": rnd(zone_of(LY) / 2, 1), "res_share": rnd(RR)}
    summary = {"datos": outcomes(LY, CONF, E_obs)}

    # ---- model with historical (data-implied) policies, no re-anchoring: 1950-2019
    sim = Simulator(W, params, R=48, seed=21)
    o = sim.run(0, W.T)
    mean = {k: np.nanmean(o[k], 0) for k in VARS}
    mean["conflict"] = np.nanmean(o["hazard"], 0)
    data["scenarios"]["modelo_hist"] = {k: rnd(mean[k]) for k in VARS}
    summary["modelo_hist"] = outcomes(mean["ly"], mean["conflict"], mean["E"], mean["psi"])
    summary["modelo_hist"].update(resource_outcomes(o, o["price"]))
    data["precio"] = {"modelo_hist": rnd(np.nanmean(o["price"], 0))}
    zh = zone_of(o["ly"])
    tot_h = sum(o[c] for c in CHANNELS)
    summary["modelo_hist"]["asignacion_por_zona"] = {
        zn: {c: float(np.nanmean((o[c] / tot_h)[zh == zi])) for c in CHANNELS}
        for zi, zn in enumerate(["periferia", "semiperiferia", "centro"])}

    # ---- backtest (forecast from 1990)
    bt, ob = backtest(params)
    lyb = np.nanmean(ob["ly"], 0)
    lyb[:, :T_SPLIT] = np.nan
    data["scenarios"]["pronostico"] = {
        "ly": rnd(lyb), "ly_p10": rnd(np.where(np.isfinite(lyb), np.nanpercentile(ob["ly"], 10, 0), np.nan)),
        "ly_p90": rnd(np.where(np.isfinite(lyb), np.nanpercentile(ob["ly"], 90, 0), np.nan)),
        "conflict": rnd(np.where(np.isfinite(lyb), np.nanmean(ob["hazard"], 0), np.nan)),
        "res_share": rnd(np.where(np.isfinite(lyb), np.nanmean(ob["res_share"], 0), np.nan))}

    # fit series for a few showcase countries (data vs model)
    show = ["USA", "CHN", "KOR", "BRA", "IND", "NGA", "DEU", "MEX", "ARG", "ZAF", "RUS", "EGY"]
    data["showcase"] = [c for c in show if c in W.iso3]

    # ---- RL policies
    rl_summary, archetype_rows, resp = {}, [], {}
    for mode in MODES:
        f = RES / f"policy_{mode}.npy"
        if not f.exists():
            continue
        th = np.load(f, allow_pickle=True).item()
        rng = np.random.default_rng(5)
        simr = Simulator(W, params, R=32, seed=33)
        _, rec = rollout(simr, th["pol"], th["logstd"], rng, mode, deterministic=True, record=True)
        m = {k: np.nanmean(rec[k], 0) for k in VARS}
        m["conflict"] = np.nanmean(rec["conflict"], 0)
        # budget shares (actions are SIGMA * share)
        tot = sum(m[c] for c in CHANNELS)
        for c in CHANNELS:
            m[c] = m[c] / tot
        data["scenarios"][f"rl_{mode}"] = {k: rnd(m[k]) for k in VARS}
        out = outcomes(m["ly"], m["conflict"], m["E"], m["psi"])
        out.update(resource_outcomes(rec, rec["price"]))
        # how resource decisions react to depletion along the simulated paths (pooled OLS on
        # country-years; budget shares on remaining own reserves, import dependence, log PSI, coreness)
        tot_b = sum(rec[c] for c in CHANNELS)
        Z = [rec["reserves"], rec["ims"], np.log(rec["psi"]), rec["core"]]
        okz = np.all([np.isfinite(z) for z in Z + [tot_b]], 0)
        Xr = np.column_stack([np.ones(okz.sum())] + [z[okz] for z in Z])
        out["sensibilidad"] = {
            ch: dict(zip(["const", "reservas", "dependencia", "log_psi", "centralidad"],
                         np.linalg.lstsq(Xr, (rec[ch] / tot_b)[okz], rcond=None)[0].round(4).tolist()))
            for ch in ("x", "f")}
        data["precio"][f"rl_{mode}"] = rnd(np.nanmean(rec["price"], 0))
        # allocation by zone (zone defined each year inside each run)
        z = zone_of(rec["ly"])
        tot_r = sum(rec[c] for c in CHANNELS)
        byzone = {}
        for zi, zn in enumerate(["periferia", "semiperiferia", "centro"]):
            sel = z == zi
            byzone[zn] = {c: float(np.nanmean((rec[c] / tot_r)[sel])) for c in CHANNELS}
        out["asignacion_por_zona"] = byzone
        # allocation over decades
        dec = {}
        for d0 in range(1950, 2020, 10):
            sl = slice(d0 - 1950, min(d0 - 1950 + 10, W.T))
            dec[str(d0)] = {c: float(np.nanmean(m[c][:, sl])) for c in CHANNELS}
        out["asignacion_por_decada"] = dec
        out["curva_entrenamiento"] = [float(x) for x in th["curve"]]
        rl_summary[mode] = out

        # country average allocation -> archetypes (pooled across modes)
        avg = np.stack([np.nanmean(m[c], 1) for c in CHANNELS], 1)
        for i in range(W.N):
            if np.all(np.isfinite(avg[i])):
                archetype_rows.append((mode, i, avg[i]))

        # response curves: vary one feature, others at the median observed state in 1990
        simr.reset(0)
        _, rec2 = None, None
        obs_all = []
        simr2 = Simulator(W, params, R=4, seed=3)
        simr2.reset(0)
        # collect realistic observations from a deterministic rollout snapshot
        rollout(simr2, th["pol"], th["logstd"], rng, mode, deterministic=True)
        ob = observe(simr2, W.T - 1)[simr2.active]
        med = np.median(ob, 0)
        feats = {"ly_rel": (0, np.linspace(-2.5, 2.5, 21)), "asabiya": (5, np.linspace(0.05, 0.95, 21)),
                 "reservas": (10, np.linspace(0.02, 1.0, 21)), "extranjera": (11, np.linspace(0.0, 0.9, 21)),
                 "log_psi": (4, np.linspace(-2, 3, 21)), "elite_E": (2, np.linspace(0.2, 0.8, 21))}
        resp[mode] = {}
        for fname, (j, grid) in feats.items():
            X = np.repeat(med[None], len(grid), 0)
            X[:, j] = grid
            if fname == "ly_rel":  # coreness moves with relative income
                X[:, 1] = 1 / (1 + np.exp(-(grid - 1.2) / 0.35))
            sh = to_shares(mlp(th["pol"], X))
            resp[mode][fname] = {"grid": grid.round(3).tolist(),
                                 **{c: sh[:, k].round(4).tolist() for k, c in enumerate(CHANNELS)}}

    # archetypes
    if archetype_rows:
        X = np.array([r[2] for r in archetype_rows])
        Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
        lab, C = kmeans(Xs, k=NK)
        cent = np.array([X[lab == j].mean(0) for j in range(NK)])
        names = {"k": "Acumulador", "r": "Desarrollista tecnológico", "m": "Importador que aprende",
                 "x": "Extractivista", "f": "Buscador de recursos fuera", "w": "Redistributivo"}
        # name each cluster by the channel it over-weights most vs. the average country-regime,
        # assigned greedily so every cluster gets a distinct name
        ratio = cent / X.mean(0)
        ratio[:, X.mean(0) < 0.02] = -np.inf  # marginal channels (e.g. f ~1%) do not name a cluster
        top, used = {}, set()
        for j, ci in sorted(np.ndindex(ratio.shape), key=lambda jc: -ratio[jc]):
            if j not in top and ci not in used and np.isfinite(ratio[j, ci]):
                top[j] = CHANNELS[ci]
                used.add(ci)
        arche = []
        for j in range(NK):
            members = [(archetype_rows[i][0], W.iso3[archetype_rows[i][1]]) for i in np.where(lab == j)[0]]
            arche.append({"id": j, "nombre": names[top[j]], "canal_dominante": top[j],
                          "centroide": {c: float(v) for c, v in zip(CHANNELS, cent[j])},
                          "n": int((lab == j).sum()),
                          "por_modo": {md: int(sum(1 for a, _ in members if a == md)) for md in MODES},
                          "ejemplos": members[:400]})
        country_arch = {}
        for (md, i, _), l in zip(archetype_rows, lab):
            country_arch.setdefault(md, {})[W.iso3[i]] = int(l)
        data["arquetipos"] = arche
        data["arquetipo_pais"] = country_arch
    data["respuesta"] = resp
    summary["rl"] = rl_summary
    data["resumen"] = summary
    json.dump(data, open(RES / "dashboard_data.json", "w"), separators=(",", ":"))
    json.dump({"resumen": summary, "arquetipos": data.get("arquetipos"), "respuesta": resp,
               "backtest": bt}, open(RES / "summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "rl"}, indent=1))
    for md, s in rl_summary.items():
        print(md, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()
                   if k not in ("asignacion_por_decada", "curva_entrenamiento")})
    for a in data.get("arquetipos", []):
        print(a["nombre"], a["n"], a["por_modo"], {c: round(v, 3) for c, v in a["centroide"].items()})


if __name__ == "__main__":
    main()
