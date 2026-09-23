"""Hybrid agent-based model: World-Systems + Structural-Demographic + Metaethnic Frontier.

Every country is an agent. Each year it produces output with a Cobb-Douglas technology
    Y = A * K^alpha * (hc * L)^(1-alpha)
and splits a discretionary budget (share of GDP) across five channels:

    k  domestic capital accumulation
    r  technology / industrial upgrading (R&D, industrial policy) -> stochastic tech jumps
    m  buy high-value goods from the core (quality consumption + embodied tech, but pays
       a monopoly rent to core exporters; the part produced by one's own industry stays home)
    f  invest abroad (capital goes to hosts with high marginal product; profits repatriate)
    w  redistribution to the masses (lowers elite capture and mass mobilisation potential)

World-systems layer (Wallerstein / Emmanuel / Amin)
    * "coreness" c_i in (0,1) is a smooth function of relative productivity.
    * Unequal exchange: the periphery loses a share tau of its traded output, which accrues
      to core exporters in proportion to their technological weight c_j^2 * Y_j.
    * Monopoly rents mu on high-value goods bought from the core.
    * FDI goes to hosts with high marginal product of capital, and repatriated profits
      flow back to the owners.
Structural-demographic layer (Goldstone / Turchin)
    * Elites capture a share E of output plus a share phi of all rents flowing into the country.
    * Elite numbers n_e grow when income per elite is high relative to the masses (elite
      overproduction). Stagnating mass income raises mass mobilisation potential (MMP).
    * PSI = MMP * EMP * SFD drives the hazard of internal instability (civil conflict).
      Conflict destroys output and prunes the elite.
Metaethnic-frontier layer (Turchin)
    * Collective solidarity (asabiya) S grows logistically where there is an external
      frontier: exposure to a core that drains the country (open periphery, rents extracted).
      It decays in rich cores, and faster under elite overproduction.
    * Asabiya raises state capacity: investment efficiency, tech-jump success and
      resistance to instability.
Technology
    * Deterministic diffusion toward the frontier through trade and FDI (Gerschenkron).
    * Stochastic jumps: Poisson hazard rising with upgrading effort and asabiya;
      jump size rises with the distance to the frontier.
"""
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ALPHA = 0.35
CHANNELS = ["k", "r", "m", "f", "w"]
CHANNEL_NAMES = {"k": "Capital doméstico", "r": "Tecnología/industria propia",
                 "m": "Importar bienes del centro", "f": "Invertir en el exterior",
                 "w": "Redistribución"}


@dataclass
class Params:
    # technology
    g0: float = 0.008          # frontier drift of log TFP per year
    kappa: float = 0.030       # diffusion speed toward frontier (per unit gap)
    kappa_m: float = 0.40      # extra diffusion from embodied tech in core imports / FDI
    lam0: float = 0.60         # tech-jump hazard scale
    j0: float = 0.04           # mean jump size (log TFP), scaled by (1+gap)
    sig_a: float = 0.020       # idiosyncratic TFP noise
    # world-system flows
    tau: float = 0.030         # unequal-exchange drain on the periphery's traded output
    mu: float = 0.25           # monopoly rent share on high-value core goods
    rho_f: float = 0.35        # share of MPK repatriated as profits on foreign capital
    phi: float = 0.60          # share of incoming rents captured by elites
    core_q: float = 0.80       # coreness threshold quantile of world productivity
    core_s: float = 0.35       # smoothness of coreness (log points)
    # structural-demographic
    beta_e: float = 0.04       # elite-overproduction speed
    eps_r: float = 0.50        # rents -> elite share
    eps_w: float = 0.60        # redistribution -> lower elite share
    eps_0: float = 0.05        # reversion of elite share
    b0: float = -3.2           # conflict onset intercept
    b1: float = 1.2            # onset sensitivity to log PSI
    b2: float = -0.45          # onset sensitivity to log income (rich -> fewer onsets)
    b3: float = -1.0           # asabiya protects against instability
    bp: float = 2.0            # persistence logit of an ongoing conflict
    gam_c: float = 0.04        # output loss from conflict
    gam_a: float = 0.010       # TFP loss per conflict year
    # metaethnic frontier / asabiya
    r_a: float = 0.12          # asabiya growth at the frontier
    d_a: float = 0.06          # asabiya decay in the core
    s0: float = 0.50           # initial asabiya
    # historical policy mapping (only used when actions come from data)
    r_hist: float = 0.015      # implied upgrading effort (share of GDP), scaled by investment
    f_hist: float = 0.02       # implied outward FDI of core countries (share of GDP)
    w_hist: float = 0.03       # implied redistribution
    m_hist: float = 0.35       # fraction of imports that are high-value core goods

    def vector(self, names):
        return np.array([getattr(self, n) for n in names])

    def with_vector(self, names, v):
        d = asdict(self)
        d.update({n: float(x) for n, x in zip(names, v)})
        return Params(**d)


def load_panel():
    p = pd.read_csv(ROOT / "data" / "processed" / "panel.csv")
    p = p[p.year.between(1950, 2019)]
    return p


@dataclass
class World:
    """Exogenous inputs aligned to arrays of shape (N, T)."""
    iso3: list
    names: list
    isonum: list
    years: np.ndarray
    pop: np.ndarray
    hc: np.ndarray
    open_: np.ndarray
    delta: np.ndarray
    csh_i: np.ndarray
    csh_m: np.ndarray
    labsh: np.ndarray
    K: np.ndarray
    Y: np.ndarray
    conflict: np.ndarray
    onset: np.ndarray
    entry: np.ndarray       # index of first observed year
    observed: np.ndarray    # bool (N, T): data available

    @property
    def N(self):
        return len(self.iso3)

    @property
    def T(self):
        return len(self.years)


def build_world(panel=None):
    p = load_panel() if panel is None else panel
    years = np.arange(1950, 2020)
    iso = sorted(p.iso3.unique())
    idx = {c: i for i, c in enumerate(iso)}
    N, T = len(iso), len(years)

    def grid(col, fill="ffill"):
        g = np.full((N, T), np.nan)
        for r in p[["iso3", "year", col]].itertuples(index=False):
            g[idx[r[0]], r[1] - 1950] = r[2]
        df = pd.DataFrame(g.T)
        df = df.ffill().bfill() if fill == "ffill" else df
        return df.values.T

    observed = ~np.isnan(grid("rgdpna", fill=None))
    entry = observed.argmax(axis=1)
    meta = p.groupby("iso3").agg(country=("country", "first"), isonum=("isonum", "first"))
    w = World(
        iso3=iso, names=[meta.loc[c, "country"] for c in iso],
        isonum=[int(meta.loc[c, "isonum"]) if pd.notna(meta.loc[c, "isonum"]) else -1 for c in iso],
        years=years,
        pop=grid("pop"), hc=grid("hc"),
        open_=np.clip((grid("csh_x") + grid("csh_m")) / 2, 0.02, 1.2),
        delta=grid("delta"), csh_i=grid("csh_i"), csh_m=grid("csh_m"), labsh=grid("labsh"),
        K=grid("rnna", fill=None), Y=grid("rgdpna", fill=None),
        conflict=np.nan_to_num(grid("conflict", fill=None)),
        onset=np.nan_to_num(grid("onset", fill=None)),
        entry=entry, observed=observed,
    )
    return w


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


class Simulator:
    """Vectorised over R Monte-Carlo worlds x N countries."""

    REC = ["ly", "core", "E", "ne", "psi", "asab", "conflict", "gni_pc", "rent_in", "drain",
           "jump", "k", "r", "m", "f", "w", "cons_pc"]

    def __init__(self, world: World, params: Params, R=8, seed=0):
        self.w, self.p, self.R = world, params, R
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------ state
    def reset(self, t0=0):
        w, R, N = self.w, self.R, self.w.N
        self.t = t0
        self.active = np.zeros((R, N), bool)
        z = lambda v=0.0: np.full((R, N), v)
        self.K, self.lnA, self.E, self.ne = z(1.0), z(), z(0.5), z(1.0)
        self.asab, self.Kf, self.claims = z(self.p.s0), z(), z()
        self.conf = z(0.0)
        self.mass_ma = z(1.0)          # moving average of mass income per capita
        self.v0 = z(1.0)               # reference elite/mass income ratio at entry
        self.last = {}
        self._activate(t0, force_all_observed=True)
        self.lnA_F = self._q_lnA()

    def _init_country(self, mask, t):
        """Initialise countries in mask (N,) from data at year index t."""
        w, p = self.w, self.p
        if not mask.any():
            return
        K = w.K[mask, t]
        L, hc = w.pop[mask, t], w.hc[mask, t]
        lnA = np.log(w.Y[mask, t]) - ALPHA * np.log(K) - (1 - ALPHA) * np.log(hc * L)
        self.K[:, mask] = K
        self.lnA[:, mask] = lnA
        self.E[:, mask] = np.clip(1 - w.labsh[mask, t], 0.15, 0.85)
        self.ne[:, mask] = 1.0
        self.asab[:, mask] = p.s0
        self.Kf[:, mask] = 0.0
        self.claims[:, mask] = 0.0
        self.conf[:, mask] = w.conflict[mask, t]
        self.mass_ma[:, mask] = (1 - self.E[:, mask]) * (w.Y[mask, t] / L)
        self.v0[:, mask] = self.E[:, mask] / (1 - self.E[:, mask])
        self.active[:, mask] = True

    def _activate(self, t, force_all_observed=False):
        w = self.w
        if force_all_observed:
            new = w.observed[:, t] & (w.entry <= t)
        else:
            new = (w.entry == t)
        new = new & ~self.active[0]
        self._init_country(new, t)

    def _q_lnA(self, q=0.9):
        """Technology frontier: upper quantile of TFP among active countries (R, 1)."""
        return np.nanquantile(np.where(self.active, self.lnA, np.nan), q, axis=1, keepdims=True)

    def assimilate(self, t):
        """Reset observable state (K, TFP, elite share) to data at year t (forecast origin)."""
        w = self.w
        m = w.observed[:, t]
        K = w.K[m, t]
        L, hc = w.pop[m, t], w.hc[m, t]
        self.K[:, m] = K
        self.lnA[:, m] = np.log(w.Y[m, t]) - ALPHA * np.log(K) - (1 - ALPHA) * np.log(hc * L)
        self.E[:, m] = np.clip(1 - w.labsh[m, t], 0.15, 0.85)
        self.conf[:, m] = w.conflict[m, t]
        self.Kf[:, m] = 0.0
        self.claims[:, m] = 0.0
        self.active[:, m] = True
        self.lnA_F = np.maximum(self.lnA_F, self._q_lnA())

    # ------------------------------------------------------------------ policy helpers
    def hist_actions(self, t, freeze_from=None):
        """Allocation implied by observed data (shares of GDP).
        If freeze_from is given, use the country's 10-year average up to that year
        (out-of-sample forecast: no future data)."""
        w, p = self.w, self.p
        if freeze_from is not None and t > freeze_from:
            lo = max(0, freeze_from - 9)
            ci = np.nanmean(w.csh_i[:, lo:freeze_from + 1], axis=1)
            cm = np.nanmean(w.csh_m[:, lo:freeze_from + 1], axis=1)
        else:
            ci, cm = w.csh_i[:, t], w.csh_m[:, t]
        c = self.last.get("core", np.zeros((self.R, w.N)))
        k = np.broadcast_to(ci, (self.R, w.N))
        r = p.r_hist * k / 0.22
        m = np.broadcast_to(p.m_hist * np.clip(cm, 0, 0.8), (self.R, w.N))
        f = p.f_hist * c
        wv = np.full((self.R, w.N), p.w_hist)
        return dict(k=k, r=r, m=m, f=f, w=wv)

    # ------------------------------------------------------------------ dynamics
    def step(self, actions):
        """Advance one year. actions: dict channel -> (R, N) shares of GDP."""
        w, p, R, t = self.w, self.p, self.R, self.t
        act = self.active
        L, hc = w.pop[:, t], w.hc[:, t]
        o = w.open_[:, t] if t < w.T else w.open_[:, -1]
        dlt = np.nan_to_num(w.delta[:, t], nan=0.045)
        rng = self.rng

        Kp = np.maximum(self.K, 1e-6)
        Y = np.exp(self.lnA) * Kp ** ALPHA * (hc * L) ** (1 - ALPHA)
        Y = Y * (1 - p.gam_c * self.conf)
        Y = np.where(act, Y, 0.0)
        ly = np.where(act, np.log(np.maximum(Y, 1e-9) / L), np.nan)

        # coreness relative to the world distribution of productivity
        ref = np.nanquantile(ly, p.core_q, axis=1, keepdims=True)
        core = np.where(act, _sigmoid((ly - ref) / p.core_s), 0.0)
        # technology gap to a frontier that drifts exogenously (g0) and is pushed by innovators
        gap = np.where(act, np.clip(self.lnA_F - self.lnA, 0.0, 4.0), 0.0)

        a = {c: np.where(act, actions[c], 0.0) for c in CHANNELS}

        # exporters of high-value goods: technological weight
        wexp = core ** 2 * Y
        wexp_n = wexp / np.maximum(wexp.sum(1, keepdims=True), 1e-9)
        # (1) unequal exchange
        drain = p.tau * o * Y * (1 - core)
        drain_in = drain.sum(1, keepdims=True) * wexp_n
        # (2) monopoly rents on high-value imports (own industry supplies a share = coreness)
        mspend = a["m"] * Y
        foreign_m = mspend * (1 - core)
        rent_m_in = p.mu * foreign_m.sum(1, keepdims=True) * wexp_n
        # (3) FDI: capital to high-MPK hosts, profits back to owners
        mpk = ALPHA * Y / Kp
        fout = a["f"] * Y
        host_w = np.where(act, Y * np.minimum(mpk, 0.3) * (1 - self.conf) * o * (1 - core * 0.5), 0.0)
        host_w = host_w / np.maximum(host_w.sum(1, keepdims=True), 1e-9)
        fin = fout.sum(1, keepdims=True) * host_w
        self.claims = self.claims * (1 - dlt) + fout
        self.Kf = self.Kf * (1 - dlt) + fin
        profits_out = p.rho_f * mpk * self.Kf
        cl_n = self.claims / np.maximum(self.claims.sum(1, keepdims=True), 1e-9)
        profits_in = profits_out.sum(1, keepdims=True) * cl_n

        rent_in = drain_in + rent_m_in + profits_in
        rent_out = drain + p.mu * foreign_m + profits_out
        gni = np.maximum(Y + rent_in - rent_out, 1e-6 * np.maximum(Y, 1e-6))

        # -- capital: efficiency of investment rises with state capacity (asabiya)
        eff = 0.75 + 0.5 * self.asab
        self.K = np.where(act, (1 - dlt) * self.K + eff * a["k"] * Y + fin, self.K)

        # -- technology: diffusion + stochastic jumps
        embodied = np.minimum((foreign_m + fin) / np.maximum(Y, 1e-9), 0.3)
        dln = (p.g0 + gap * (p.kappa + p.kappa_m * embodied)
               + p.sig_a * rng.standard_normal((R, w.N)) - p.gam_a * self.conf)
        lam = p.lam0 * np.sqrt(np.maximum(a["r"], 0)) * (0.5 + self.asab)
        njump = rng.poisson(np.clip(np.nan_to_num(np.where(act, lam, 0.0)), 0, 5))
        jsize = np.where(njump > 0, rng.exponential(1.0, (R, w.N)) * p.j0 * (1 + gap) * njump, 0.0)
        self.lnA = np.where(act, self.lnA + np.clip(dln + jsize, -0.3, 0.3), self.lnA)
        self.lnA_F = np.maximum(self.lnA_F + p.g0, self._q_lnA())

        # -- structural-demographic dynamics
        Ypc = Y / L
        elite_inc = self.E * Y + p.phi * rent_in
        mass_inc = (1 - self.E) * Y + (1 - p.phi) * rent_in - rent_out + a["w"] * Y
        mass_inc = np.maximum(mass_inc, 0.05 * Y)
        mass_pc = np.maximum(mass_inc, 1e-9) / L
        v = elite_inc / np.maximum(mass_inc, 1e-9)            # elite / mass income ratio
        grow = np.clip(p.beta_e * (v / self.v0 - self.ne) - 0.15 * self.conf, -0.5, 0.5)
        self.ne = np.where(act, np.clip(self.ne * np.exp(grow), 0.1, 10.0), self.ne)
        mmp = (self.mass_ma / np.maximum(mass_pc, 1e-9)) ** 2
        emp = self.ne / np.maximum(v / self.v0, 1e-3)
        sfd = 1.5 - self.asab
        psi = np.where(act, mmp * emp * sfd, np.nan)
        self.mass_ma = 0.9 * self.mass_ma + 0.1 * mass_pc
        rent_share = p.phi * rent_in / np.maximum(Y, 1e-9)
        self.E = np.clip(self.E + p.eps_r * rent_share * 0.1 - p.eps_w * a["w"] * 0.1
                         + p.eps_0 * (0.5 - self.E) * 0.1 - 0.02 * self.conf, 0.05, 0.95)

        # -- instability
        lp = np.log(np.maximum(psi, 1e-6))
        p_on = _sigmoid(p.b0 + p.b1 * lp + p.b2 * (np.nan_to_num(ly) - 9.0) + p.b3 * (self.asab - 0.5))
        p_stay = _sigmoid(p.bp + p.b1 * lp * 0.5)
        hazard = np.where(self.conf > 0, p_stay, p_on)
        newconf = (rng.random((R, w.N)) < hazard).astype(float)
        self.hazard_onset = np.where(act, p_on, np.nan)
        self.hazard = np.where(act, hazard, np.nan)

        # -- asabiya: grows at the metaethnic frontier (exposure to a draining core), decays in the core
        frontier = o * (1 - core) + 4.0 * (drain + p.mu * foreign_m + profits_out) / np.maximum(Y, 1e-9)
        self.asab = np.clip(self.asab + p.r_a * self.asab * (1 - self.asab) * frontier
                            - p.d_a * self.asab * core * np.maximum(self.ne, 0.5)
                            - 0.03 * self.conf * self.asab, 0.02, 0.98)
        self.asab = np.where(act, self.asab, p.s0)

        cons = (1 - sum(a[c] for c in CHANNELS)) * gni + mspend * 0.5 + a["w"] * Y * 0.5
        rec = dict(ly=ly, core=core, E=self.E.copy(), ne=self.ne.copy(), psi=psi, asab=self.asab.copy(),
                   conflict=self.conf.copy(), gni_pc=np.where(act, gni / L, np.nan),
                   rent_in=np.where(act, (rent_in - rent_out) / np.maximum(Y, 1e-9), np.nan),
                   drain=np.where(act, drain / np.maximum(Y, 1e-9), np.nan),
                   jump=np.where(act, jsize, np.nan),
                   cons_pc=np.where(act, np.maximum(cons, 1e-6) / L, np.nan),
                   **{c: np.where(act, a[c], np.nan) for c in CHANNELS})
        self.last = rec
        self.conf = np.where(act, newconf, 0.0)
        self.t += 1
        if self.t < w.T:
            self._activate(self.t)
        return rec

    def run(self, t0=0, t1=None, policy="hist", freeze_from=None, assimilate_at=None, record=True):
        """Run from year index t0 to t1 (exclusive). Returns dict of (R, N, T) arrays."""
        w = self.w
        t1 = w.T if t1 is None else t1
        self.reset(t0)
        out = {k: np.full((self.R, w.N, t1 - t0), np.nan) for k in self.REC}
        out["hazard"] = np.full((self.R, w.N, t1 - t0), np.nan)
        for t in range(t0, t1):
            if assimilate_at is not None and t == assimilate_at:
                self.assimilate(t)
            if policy == "hist":
                acts = self.hist_actions(t, freeze_from)
            else:
                acts = policy(self, t)
            rec = self.step(acts)
            if record:
                for k in self.REC:
                    out[k][:, :, t - t0] = rec[k]
                out["hazard"][:, :, t - t0] = self.hazard
        return out
