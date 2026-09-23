"""Calibrate the model on 1950-1990 and evaluate out-of-sample forecasts for 1991-2019.

Estimation: simulated method of moments + trajectory fit, using only 1950-1990 data.
    loss = RMSE(log GDP pc, mean of simulations vs data, all country-years <= 1990)
         + RMSE of natural-resource rents / GDP vs World Bank WDI (1970-1990)
         + |sd of simulated 10y growth - sd observed| (identifies the stochastic tech jumps)
         + cross-entropy of simulated conflict hazard vs observed UCDP conflict incidence
Backtest: state is re-anchored to observed data in 1990, policies are frozen at each
country's 1981-1990 average (no future information), then the model runs to 2019.
Demography (population, human capital) is taken as exogenous.
"""
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution
from scipy.stats import spearmanr

from model import Params, Simulator, build_world

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
T_SPLIT = 40  # 1990

FREE = {  # name: (low, high)
    "g0": (0.0, 0.02), "kappa": (0.0, 0.03), "kappa_m": (0.0, 1.0),
    "lam0": (0.0, 1.5), "j0": (0.0, 0.15), "sig_a": (0.005, 0.08), "tau": (0.0, 0.08),
    "b0": (-6.0, 0.0), "b1": (0.0, 3.0), "b2": (-1.5, 0.5), "bp": (0.0, 4.0), "b3": (-3.0, 0.0),
    "r_R": (0.01, 0.12), "x0": (0.01, 0.5), "x_hist": (0.05, 1.5),
}
NAMES = list(FREE)

W = build_world()
LY = np.log(W.Y / W.pop)
LY[~W.observed] = np.nan
CONF = np.where(W.observed, W.conflict, np.nan)
RR = np.where(W.observed, W.rr_obs, np.nan)


def growth_sd(ly, t_end):
    """Cross-country sd of 10-year growth of log GDP pc, pooled over windows up to t_end."""
    g = []
    for t in range(10, t_end + 1, 5):
        d = ly[..., t] - ly[..., t - 10]
        g.append(d)
    g = np.stack(g, -1)
    return np.nanstd(g)


SD_OBS = growth_sd(LY, T_SPLIT)


def loss(v, R=12, seed=1, detail=False):
    try:
        return _loss(v, R, seed, detail)
    except Exception:
        return 1e3


def _loss(v, R=12, seed=1, detail=False):
    p = Params().with_vector(NAMES, v)
    sim = Simulator(W, p, R=R, seed=seed)
    o = sim.run(0, T_SPLIT + 1)
    m = np.nanmean(o["ly"], 0)
    d = LY[:, :T_SPLIT + 1]
    ok = ~np.isnan(d) & ~np.isnan(m)
    rmse = np.sqrt(np.mean((m[ok] - d[ok]) ** 2))
    sd_sim = np.mean([growth_sd(o["ly"][r], T_SPLIT) for r in range(R)])
    h = np.clip(np.nanmean(o["hazard"], 0), 1e-4, 1 - 1e-4)
    c = CONF[:, :T_SPLIT + 1]
    okc = ~np.isnan(c) & ~np.isnan(h)
    ce = -np.mean(c[okc] * np.log(h[okc]) + (1 - c[okc]) * np.log(1 - h[okc]))
    # aggregate conflict incidence by decade (keeps conflicts from piling up over time)
    inc = sum(abs(np.nanmean(np.where(okc, h, np.nan)[:, a:a + 10]) - np.nanmean(c[:, a:a + 10]))
              for a in range(0, T_SPLIT, 10)) / 4
    # natural-resource rents / GDP (WDI starts in 1970)
    rs = np.nanmean(o["res_share"], 0)
    d_rr = RR[:, :T_SPLIT + 1]
    okr = ~np.isnan(d_rr) & ~np.isnan(rs)
    rr_rmse = np.sqrt(np.mean((rs[okr] - d_rr[okr]) ** 2))
    # calibration of the stochastic part: share of observed country-years (from 1955) inside the
    # simulated 10-90% band (target 0.8)
    lo, hi = np.nanpercentile(o["ly"], 10, 0), np.nanpercentile(o["ly"], 90, 0)
    okb = ok & (np.arange(T_SPLIT + 1)[None] >= 5)
    cov = np.mean((d[okb] >= lo[okb]) & (d[okb] <= hi[okb]))
    total = (rmse + 2.0 * abs(sd_sim - SD_OBS) + 1.0 * ce + 3.0 * inc + 3.0 * rr_rmse
             + 1.0 * abs(cov - 0.8))
    if detail:
        return dict(total=total, rmse=rmse, sd_sim=sd_sim, sd_obs=SD_OBS, ce=ce, inc_gap=inc,
                    rr_rmse=rr_rmse, cobertura_80=cov)
    return total if np.isfinite(total) else 1e3


def auc(y, s):
    y, s = np.asarray(y), np.asarray(s)
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    order = np.argsort(np.concatenate([pos, neg]))
    ranks = np.empty(len(order))
    ranks[order] = np.arange(1, len(order) + 1)
    return (ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def zones(ly_col):
    """Core / semi-periphery / periphery by world quantiles (top 20%, next 30%, rest)."""
    q80, q50 = np.nanquantile(ly_col, 0.8), np.nanquantile(ly_col, 0.5)
    return np.where(ly_col >= q80, 2, np.where(ly_col >= q50, 1, 0))


def backtest(p, R=64, seed=7):
    sim = Simulator(W, p, R=R, seed=seed)
    o = sim.run(0, W.T, freeze_from=T_SPLIT, assimilate_at=T_SPLIT)
    m = np.nanmean(o["ly"], 0)
    lo, hi = np.nanpercentile(o["ly"], 10, 0), np.nanpercentile(o["ly"], 90, 0)
    t0 = T_SPLIT
    base = ~np.isnan(LY[:, t0])
    # baselines (all use information up to 1990 only)
    g_own = np.array([np.nanmean(np.diff(LY[i, max(0, t0 - 20):t0 + 1])) for i in range(W.N)])
    g_world = np.nanmean(np.diff(LY[:, :t0 + 1], axis=1))
    X, Yg = [], []
    for t in range(0, t0 - 9):
        ok = ~np.isnan(LY[:, t]) & ~np.isnan(LY[:, t + 10])
        X += list(LY[ok, t]); Yg += list((LY[ok, t + 10] - LY[ok, t]) / 10)
    bcoef = np.polyfit(X, Yg, 1)
    res = {"horizons": {}, "baselines_def": {
        "persistencia": "log PIBpc constante desde 1990",
        "deriva_propia": "crecimiento medio del país 1970-1990",
        "deriva_global": "crecimiento medio mundial 1950-1990",
        "convergencia_beta": f"g = {bcoef[1]:.4f} + {bcoef[0]:.4f}·log y (MCO 1950-1990)"}}
    cover = []
    for yr in [2000, 2010, 2019]:
        t = yr - 1950
        h = t - t0
        ok = base & ~np.isnan(LY[:, t]) & ~np.isnan(m[:, t])
        truth = LY[ok, t]
        preds = {
            "modelo": m[ok, t],
            "persistencia": LY[ok, t0],
            "deriva_propia": LY[ok, t0] + h * np.nan_to_num(g_own[ok], nan=g_world),
            "deriva_global": LY[ok, t0] + h * g_world,
        }
        yb = LY[ok, t0].copy()
        for _ in range(h):
            yb = yb + np.polyval(bcoef, yb)
        preds["convergencia_beta"] = yb
        row = {}
        for k, pr in preds.items():
            e = pr - truth
            gtrue, gpred = truth - LY[ok, t0], pr - LY[ok, t0]
            row[k] = dict(rmse=float(np.sqrt(np.mean(e ** 2))), mae=float(np.mean(np.abs(e))),
                          spearman_level=float(spearmanr(pr, truth)[0]),
                          corr_growth=float(np.corrcoef(gpred, gtrue)[0, 1]) if np.std(gpred) > 0 else None,
                          zone_acc=float(np.mean(zones(pr) == zones(truth))))
        cover.append(float(np.mean((truth >= lo[ok, t]) & (truth <= hi[ok, t]))))
        row["n"] = int(ok.sum())
        row["cobertura_80"] = cover[-1]
        res["horizons"][str(yr)] = row

    # natural-resource rents / GDP: model vs persistence of the 1990 share
    rs = np.nanmean(o["res_share"], 0)
    res["recursos"] = {}
    for yr in [2000, 2010, 2019]:
        t = yr - 1950
        ok = ~np.isnan(RR[:, t]) & ~np.isnan(rs[:, t]) & ~np.isnan(RR[:, t0])
        truth = RR[ok, t]
        row = {}
        for k, pr in {"modelo": rs[ok, t], "persistencia": RR[ok, t0]}.items():
            row[k] = dict(rmse=float(np.sqrt(np.mean((pr - truth) ** 2))),
                          spearman=float(spearmanr(pr, truth)[0]))
        row["n"] = int(ok.sum())
        res["recursos"][str(yr)] = row

    # conflict: per country-year hazard vs observed 1991-2019
    hz = np.nanmean(o["hazard"], 0)[:, t0 + 1:]
    c = CONF[:, t0 + 1:]
    ok = ~np.isnan(c) & ~np.isnan(hz)
    freq_past = np.nanmean(CONF[:, t0 - 20:t0 + 1], axis=1)
    fp = np.broadcast_to(np.nan_to_num(freq_past, nan=np.nanmean(freq_past))[:, None], c.shape)
    res["conflicto"] = {
        "modelo": dict(auc=float(auc(c[ok], hz[ok])), brier=float(np.mean((hz[ok] - c[ok]) ** 2)),
                       tasa_pred=float(hz[ok].mean())),
        "frecuencia_pasada": dict(auc=float(auc(c[ok], fp[ok])), brier=float(np.mean((fp[ok] - c[ok]) ** 2)),
                                  tasa_pred=float(fp[ok].mean())),
        "tasa_obs": float(c[ok].mean()),
    }
    return res, o


def main():
    OUT.mkdir(exist_ok=True)
    x0 = Params().vector(NAMES)
    prev = OUT / "calibration.json"
    if prev.exists():  # warm start from the previous calibration where names overlap
        old = json.load(open(prev))["params"]
        x0 = np.array([np.clip(old.get(n, v), *FREE[n]) for n, v in zip(NAMES, x0)])
    print("initial", loss(x0, detail=True))
    t = time.time()
    r = differential_evolution(loss, [FREE[n] for n in NAMES], seed=3, maxiter=90, popsize=12,
                               tol=1e-4, polish=False, workers=4, updating="deferred", x0=x0)
    print("DE done", round(time.time() - t), "s", r.fun)
    p = Params().with_vector(NAMES, r.x)
    fit = loss(r.x, R=32, seed=11, detail=True)  # fresh seeds for reporting
    print("fit", fit)
    bt, o = backtest(p)
    print(json.dumps(bt, indent=1))
    json.dump({"params": {n: float(v) for n, v in zip(NAMES, r.x)}, "fit_1950_1990": fit,
               "backtest": bt}, open(OUT / "calibration.json", "w"), indent=1)


if __name__ == "__main__":
    main()
