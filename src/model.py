"""Hybrid agent-based model: World-Systems + Structural-Demographic + Metaethnic Frontier.

Every country is an agent. Each year it produces output with a Cobb-Douglas technology
    Y = A * K^alpha * (hc * L)^(1-alpha)
plus a natural-resource input R (share psi_t), bought on a world market, and splits a
discretionary budget (share of GDP) across six channels:

    k  domestic capital accumulation
    r  technology / industrial upgrading (R&D, industrial policy) -> stochastic tech jumps
    m  buy high-value goods from the core (quality consumption + embodied tech, but pays
       a monopoly rent to core exporters; the part produced by one's own industry stays home)
    x  extraction capital for the country's own natural resources
    f  invest abroad in other countries' natural resources (concessions; profits repatriate)
    w  redistribution to the masses (lowers elite capture and mass mobilisation potential)

Natural resources
    * Each country has ultimate recoverable resources U. Its gross extraction capacity follows a
      logistic (Hubbert) curve in cumulative extraction X:  Cap = r_R * U * (x + eps) * (1 - x),
      x = X / U: it rises while the deposit is being opened up and falls as it is depleted.
    * Actual extraction = Cap * (1 - exp(-e)), e = extraction capital / (c_R * Cap). Domestic
      and foreign extraction capital compete for the same capacity: foreign concessions take
      their share of the output, speed up depletion (x rises faster) and so shrink the host's
      own gross capacity. The host keeps a royalty; the rest of the rent is repatriated.
    * Resources enter production (Y = A K^alpha R^psi (hL)^(1-alpha-psi)); a world price clears
      the market. psi_t is the observed world rent share (Cobb-Douglas pins it), so the model
      explains the cross-country distribution of rents, not the global oil cycles. Countries that must import resources pay a markup zeta on the imported
      share, so running out of one's own resources slows growth unless one secures supply
      abroad (investing in foreign extraction counts as owned supply).
    * Elites capture a larger share phi_R of resource income (resource curse).

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
CHANNELS = ["k", "r", "m", "x", "f", "w"]
CHANNEL_NAMES = {"k": "Capital doméstico", "r": "Tecnología/industria propia",
                 "m": "Importar bienes del centro", "x": "Extracción propia de recursos",
                 "f": "Invertir fuera en recursos", "w": "Redistribución"}
EPS_X = 0.05


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
    # natural resources
    r_R: float = 0.04          # Hubbert steepness of the logistic extraction capacity
    x0: float = 0.08           # share of ultimate resources already extracted at entry
    e0: float = 1.2            # initial extraction effort (capital / capacity)
    c_R: float = 3.0           # extraction capital per unit of capacity
    d_R: float = 0.06          # depreciation of extraction capital
    zeta: float = 0.15         # markup paid on imported resources
    roy: float = 0.30          # royalty the host keeps on foreign extraction
    phi_R: float = 0.70        # elite capture of resource income (resource curse)
    nu_a: float = 0.80         # asabiya resists foreign concessions (resource nationalism)
    # historical policy mapping (only used when actions come from data)
    x_hist: float = 0.30       # share of resource rents reinvested in extraction
    r_hist: float = 0.015      # implied upgrading effort (share of GDP), scaled by investment
    f_hist: float = 0.02       # implied outward resource FDI of core countries (share of GDP)
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
    rr: np.ndarray          # natural-resource rents / GDP (filled)
    rr_obs: np.ndarray      # same, NaN where WDI has no observation
    psi_t: np.ndarray       # world resource rents / world GDP by year (T,)
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
    rr = np.clip(grid("res_rents"), 0.001, 0.6)
    Yg = grid("rgdpna", fill=None)
    psi_t = np.nansum(np.where(observed, rr * Yg, 0), 0) / np.nansum(np.where(observed, Yg, 0), 0)
    meta = p.groupby("iso3").agg(country=("country", "first"), isonum=("isonum", "first"))
    w = World(
        iso3=iso, names=[meta.loc[c, "country"] for c in iso],
        isonum=[int(meta.loc[c, "isonum"]) if pd.notna(meta.loc[c, "isonum"]) else -1 for c in iso],
        years=years,
        pop=grid("pop"), hc=grid("hc"),
        open_=np.clip((grid("csh_x") + grid("csh_m")) / 2, 0.02, 1.2),
        delta=grid("delta"), csh_i=grid("csh_i"), csh_m=grid("csh_m"), labsh=grid("labsh"),
        rr=rr, rr_obs=grid("res_rents_obs", fill=None), psi_t=psi_t,
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
           "jump", "cons_pc", "res_share", "reserves", "fshare", "ims", "res_out"] + CHANNELS

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
        self.asab, self.conf = z(self.p.s0), z(0.0)
        self.mass_ma = z(1.0)          # moving average of mass income per capita
        self.v0 = z(1.0)               # reference elite/mass income ratio at entry
        # natural resources: ultimate stock, cumulative extraction, extraction capital
        self.U, self.X = z(1e-6), z(0.0)
        self.KRd, self.KRf, self.claims = z(0.0), z(0.0), z(0.0)
        self.mR = z(1.0)               # markup multiplier on resources (lagged import dependence)
        self.price = np.ones((R, 1))
        self.last = {}
        new = w.observed[:, t0] & (w.entry <= t0)
        self.psi_freeze = None
        self._init_country(new, t0, price=1.0)
        self.price = self._clearing_price_from_gdp(new, w.Y[:, t0])
        self._anchor(new, t0, w.Y[new, t0])
        self.lnA_F = self._q_lnA()

    def _init_country(self, mask, t, price):
        """Initialise countries in mask (N,) from data at year index t (TFP anchored separately)."""
        w, p = self.w, self.p
        if not mask.any():
            return
        L = w.pop[mask, t]
        G = w.Y[mask, t]
        self.K[:, mask] = w.K[mask, t]
        self.E[:, mask] = np.clip(1 - w.labsh[mask, t], 0.15, 0.85)
        self.ne[:, mask] = 1.0
        self.asab[:, mask] = p.s0
        self.conf[:, mask] = w.conflict[mask, t]
        self.mass_ma[:, mask] = (1 - self.E[:, mask]) * (G / L)
        self.v0[:, mask] = self.E[:, mask] / (1 - self.E[:, mask])
        # resources: observed rent share pins down current extraction; x0 and e0 the rest
        E0 = w.rr[mask, t] * G / np.maximum(price, 1e-6)
        cap_per_U = p.r_R * (p.x0 + EPS_X) * (1 - p.x0)
        cap0 = E0 / (1 - np.exp(-p.e0))
        self.U[:, mask] = cap0 / cap_per_U
        self.X[:, mask] = p.x0 * cap0 / cap_per_U
        self.KRd[:, mask] = p.e0 * p.c_R * cap0
        self.KRf[:, mask] = 0.0
        self.claims[:, mask] = 0.0
        self.mR[:, mask] = 1.0
        self.active[:, mask] = True

    # ---------------------------------------------------------------- resource helpers
    def _extraction(self):
        """Capacity (logistic in cumulative extraction), extraction and domestic share (R, N)."""
        p = self.p
        x = np.clip(self.X / np.maximum(self.U, 1e-12), 0.0, 1.0)
        cap = p.r_R * self.U * (x + EPS_X) * (1 - x)
        KR = self.KRd + self.KRf
        e = KR / np.maximum(p.c_R * cap, 1e-12)
        ext = np.where(self.active, cap * (1 - np.exp(-e)), 0.0)
        sd = np.where(KR > 0, self.KRd / np.maximum(KR, 1e-12), 1.0)
        return cap, e, ext, sd, x

    def _psi(self, t):
        """Resource share in production = observed world rent share (Cobb-Douglas pins it);
        frozen at the pre-forecast average when forecasting."""
        w = self.w
        if self.psi_freeze is not None and t > self.psi_freeze:
            return float(np.mean(w.psi_t[max(0, self.psi_freeze - 9):self.psi_freeze + 1]))
        return float(w.psi_t[min(t, w.T - 1)])

    def _clearing_price_from_gdp(self, mask, G):
        """World resource price consistent with observed GDP G (N,) of countries in mask."""
        psi = self._psi(self.t)
        _, _, ext, _, _ = self._extraction()
        a = psi / (1 - psi)
        m = self.mR
        Gm = np.where(self.active, np.broadcast_to(G, m.shape), 0.0)
        num = a * np.nansum(Gm / m, 1, keepdims=True)
        den = ext.sum(1, keepdims=True) + a * np.sum(ext / m, 1, keepdims=True)
        return num / np.maximum(den, 1e-12)

    def _anchor(self, mask, t, G):
        """Set TFP so the model reproduces observed GDP G of countries in mask at the current price."""
        w, p = self.w, self.p
        if not np.any(mask):
            return
        _, _, ext, _, _ = self._extraction()
        pr = self.price
        psi = self._psi(t)
        Yt = np.maximum((G[None] - pr * ext[:, mask]) / (1 - psi), 0.3 * G[None])
        pj = pr * self.mR[:, mask]
        B = Yt ** (1 - psi) / (psi / pj) ** psi
        L, hc = w.pop[mask, t], w.hc[mask, t]
        self.lnA[:, mask] = (np.log(B) - ALPHA * np.log(self.K[:, mask])
                             - (1 - ALPHA - psi) * np.log(hc * L))

    def _activate(self, t):
        new = (self.w.entry == t) & ~self.active[0]
        if new.any():
            self._init_country(new, t, price=self.price)
            self._anchor(new, t, self.w.Y[new, t])

    def _q_lnA(self, q=0.9):
        """Technology frontier: upper quantile of TFP among active countries (R, 1)."""
        return np.nanquantile(np.where(self.active, self.lnA, np.nan), q, axis=1, keepdims=True)

    def assimilate(self, t):
        """Re-anchor observable state to data at year t (forecast origin): capital, GDP (via TFP),
        elite share, conflict and the level of resource rents. Latent states are kept."""
        w = self.w
        m = w.observed[:, t]
        self.K[:, m] = w.K[m, t]
        self.E[:, m] = np.clip(1 - w.labsh[m, t], 0.15, 0.85)
        self.conf[:, m] = w.conflict[m, t]
        # rescale the resource base so extraction matches the observed rent share
        _, _, ext, _, _ = self._extraction()
        target = w.rr[m, t] * w.Y[m, t] / np.maximum(self.price, 1e-6)
        sc = np.clip(target / np.maximum(ext[:, m], 1e-12), 0.05, 20)
        for arr in (self.U, self.X, self.KRd, self.KRf):
            arr[:, m] *= sc
        self._anchor(m, t, w.Y[m, t])
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
            rr = np.nanmean(w.rr[:, lo:freeze_from + 1], axis=1)
        else:
            ci, cm, rr = w.csh_i[:, t], w.csh_m[:, t], w.rr[:, t]
        c = self.last.get("core", np.zeros((self.R, w.N)))
        k = np.broadcast_to(ci, (self.R, w.N))
        r = p.r_hist * k / 0.22
        m = np.broadcast_to(p.m_hist * np.clip(cm, 0, 0.8), (self.R, w.N))
        x = np.broadcast_to(p.x_hist * rr, (self.R, w.N))
        f = p.f_hist * c
        wv = np.full((self.R, w.N), p.w_hist)
        return dict(k=k, r=r, m=m, x=x, f=f, w=wv)

    # ------------------------------------------------------------------ dynamics
    def step(self, actions):
        """Advance one year. actions: dict channel -> (R, N) shares of GDP."""
        w, p, R, t = self.w, self.p, self.R, self.t
        act = self.active
        L, hc = w.pop[:, t], w.hc[:, t]
        o = w.open_[:, t]
        dlt = np.nan_to_num(w.delta[:, t], nan=0.045)
        rng = self.rng
        psi = self._psi(t)

        # -- natural resources: logistic capacity, extraction, world market clearing
        cap, eff_e, ext, sd, xdep = self._extraction()
        Kp = np.maximum(self.K, 1e-6)
        B = np.exp(self.lnA) * Kp ** ALPHA * (hc * L) ** (1 - ALPHA - psi) * (1 - p.gam_c * self.conf)
        B = np.where(act, B, 0.0)
        S = ext.sum(1, keepdims=True)
        inv = 1.0 / (1 - psi)
        denom = np.sum(np.where(act, self.mR ** (-inv) * B ** inv, 0.0), 1, keepdims=True)
        q = (np.maximum(S, 1e-12) / np.maximum(denom, 1e-12)) ** (1 - psi)   # = psi / price
        price = psi / q
        pj = price * self.mR
        Y = np.where(act, (B * (psi / pj) ** psi) ** inv, 0.0)             # gross output
        Rres = np.where(act, psi * Y / pj, 0.0)                            # resources used
        rev = price * ext                                                  # value of extraction
        G = np.where(act, (1 - psi) * Y + rev, 0.0)                        # GDP (value added)
        Gs = np.maximum(G, 1e-9)
        ly = np.where(act, np.log(Gs / L), np.nan)

        # ownership of extraction: domestic, foreign concessions, and claims abroad
        foreign_ext = (1 - sd) * ext
        cl_n = self.claims / np.maximum(self.claims.sum(1, keepdims=True), 1e-12)
        owned = sd * ext + cl_n * foreign_ext.sum(1, keepdims=True)
        ims = np.where(act, np.clip(1 - owned / np.maximum(Rres, 1e-12), 0.0, 1.0), 0.0)
        res_out = (1 - p.roy) * price * foreign_ext                        # repatriated rents
        res_in = cl_n * res_out.sum(1, keepdims=True)
        res_inc = price * sd * ext + p.roy * price * foreign_ext           # stays in the host

        # coreness relative to the world distribution of productivity
        ref = np.nanquantile(ly, p.core_q, axis=1, keepdims=True)
        core = np.where(act, _sigmoid((ly - ref) / p.core_s), 0.0)
        gap = np.where(act, np.clip(self.lnA_F - self.lnA, 0.0, 4.0), 0.0)

        a = {c: np.where(act, actions[c], 0.0) for c in CHANNELS}

        # exporters of high-value goods: technological weight
        wexp = core ** 2 * G
        wexp_n = wexp / np.maximum(wexp.sum(1, keepdims=True), 1e-9)
        # (1) unequal exchange
        drain = p.tau * o * G * (1 - core)
        drain_in = drain.sum(1, keepdims=True) * wexp_n
        # (2) monopoly rents on high-value imports (own industry supplies a share = coreness)
        mspend = a["m"] * G
        foreign_m = mspend * (1 - core)
        rent_m_in = p.mu * foreign_m.sum(1, keepdims=True) * wexp_n
        # (3) resource concessions abroad: capital goes where untapped capacity is cheapest to
        #     reach, and competes with the host's own extraction capital
        fout = a["f"] * G
        host_w = np.where(act, cap * np.exp(-eff_e) * o * (1 - self.conf)
                          * np.clip(1 - p.nu_a * self.asab, 0.02, 1), 0.0)
        host_w = host_w / np.maximum(host_w.sum(1, keepdims=True), 1e-12)
        fin = fout.sum(1, keepdims=True) * host_w
        self.claims = self.claims * (1 - p.d_R) + fout
        self.KRf = self.KRf * (1 - p.d_R) + fin
        eff = 0.75 + 0.5 * self.asab                     # state capacity (asabiya)
        self.KRd = np.where(act, self.KRd * (1 - p.d_R) + eff * a["x"] * G, self.KRd)
        self.X = np.where(act, self.X + ext, self.X)

        rent_in = drain_in + rent_m_in + res_in
        rent_out = drain + p.mu * foreign_m + res_out
        gni = np.maximum(G + rent_in - rent_out, 1e-6 * Gs)

        # -- capital
        self.K = np.where(act, (1 - dlt) * self.K + eff * a["k"] * G, self.K)

        # -- technology: diffusion + stochastic jumps
        embodied = np.minimum(foreign_m / Gs, 0.3)
        dln = (p.g0 + gap * (p.kappa + p.kappa_m * embodied)
               + p.sig_a * rng.standard_normal((R, w.N)) - p.gam_a * self.conf)
        lam = p.lam0 * np.sqrt(np.maximum(a["r"], 0)) * (0.5 + self.asab)
        njump = rng.poisson(np.clip(np.nan_to_num(np.where(act, lam, 0.0)), 0, 5))
        jsize = np.where(njump > 0, rng.exponential(1.0, (R, w.N)) * p.j0 * (1 + gap) * njump, 0.0)
        self.lnA = np.where(act, self.lnA + np.clip(dln + jsize, -0.3, 0.3), self.lnA)
        self.lnA_F = np.maximum(self.lnA_F + p.g0, self._q_lnA())

        # -- structural-demographic dynamics (resource income is captured more by elites)
        base = G - res_inc
        elite_inc = self.E * base + p.phi_R * res_inc + p.phi * rent_in
        mass_inc = ((1 - self.E) * base + (1 - p.phi_R) * res_inc + (1 - p.phi) * rent_in
                    - rent_out + a["w"] * G)
        mass_inc = np.maximum(mass_inc, 0.05 * Gs)
        mass_pc = mass_inc / L
        v = elite_inc / mass_inc                                     # elite / mass income ratio
        grow = np.clip(p.beta_e * (v / self.v0 - self.ne) - 0.15 * self.conf, -0.5, 0.5)
        self.ne = np.where(act, np.clip(self.ne * np.exp(grow), 0.1, 10.0), self.ne)
        mmp = (self.mass_ma / np.maximum(mass_pc, 1e-9)) ** 2
        emp = self.ne / np.maximum(v / self.v0, 1e-3)
        sfd = 1.5 - self.asab
        psi_idx = np.where(act, mmp * emp * sfd, np.nan)
        self.mass_ma = 0.9 * self.mass_ma + 0.1 * mass_pc
        rent_share = (p.phi * rent_in + (p.phi_R - self.E) * res_inc) / Gs
        self.E = np.clip(self.E + p.eps_r * rent_share * 0.1 - p.eps_w * a["w"] * 0.1
                         + p.eps_0 * (0.5 - self.E) * 0.1 - 0.02 * self.conf, 0.05, 0.95)

        # -- instability
        lp = np.log(np.maximum(psi_idx, 1e-6))
        p_on = _sigmoid(p.b0 + p.b1 * lp + p.b2 * (np.nan_to_num(ly) - 9.0) + p.b3 * (self.asab - 0.5))
        p_stay = _sigmoid(p.bp + p.b1 * lp * 0.5)
        hazard = np.where(self.conf > 0, p_stay, p_on)
        newconf = (rng.random((R, w.N)) < hazard).astype(float)
        self.hazard_onset = np.where(act, p_on, np.nan)
        self.hazard = np.where(act, hazard, np.nan)

        # -- asabiya: grows at the metaethnic frontier (a core that drains the country, including
        #    foreign resource concessions), decays in the core
        frontier = o * (1 - core) + 4.0 * (drain + p.mu * foreign_m + res_out) / Gs
        self.asab = np.clip(self.asab + p.r_a * self.asab * (1 - self.asab) * frontier
                            - p.d_a * self.asab * core * np.maximum(self.ne, 0.5)
                            - 0.03 * self.conf * self.asab, 0.02, 0.98)
        self.asab = np.where(act, self.asab, p.s0)

        # -- import dependence for next year's resource markup
        self.mR = np.where(act, 1 + p.zeta * ims, 1.0)
        self.price = price

        cons = (1 - sum(a[c] for c in CHANNELS)) * gni + mspend * 0.5 + a["w"] * G * 0.5
        nz = lambda v: np.where(act, v, np.nan)
        rec = dict(ly=ly, core=core, E=self.E.copy(), ne=self.ne.copy(), psi=psi_idx, asab=self.asab.copy(),
                   conflict=self.conf.copy(), gni_pc=nz(gni / L),
                   rent_in=nz((rent_in - rent_out) / Gs), drain=nz(drain / Gs), jump=nz(jsize),
                   cons_pc=nz(np.maximum(cons, 1e-6) / L),
                   res_share=nz(rev / Gs), reserves=nz(1 - np.clip(self.X / np.maximum(self.U, 1e-12), 0, 1)),
                   fshare=nz(1 - sd), ims=nz(ims), res_out=nz((res_in - res_out) / Gs),
                   **{c: nz(a[c]) for c in CHANNELS})
        self.last = rec
        self.last_price = price[:, 0].copy()
        self.conf = np.where(act, newconf, 0.0)
        self.t += 1
        if self.t < w.T:
            self._activate(self.t)
        return rec

    def run(self, t0=0, t1=None, policy="hist", freeze_from=None, assimilate_at=None, record=True):
        """Run from year index t0 to t1 (exclusive). Returns dict of (R, N, T) arrays
        plus 'price' (R, T)."""
        w = self.w
        t1 = w.T if t1 is None else t1
        self.reset(t0)
        self.psi_freeze = freeze_from
        out = {k: np.full((self.R, w.N, t1 - t0), np.nan) for k in self.REC}
        out["hazard"] = np.full((self.R, w.N, t1 - t0), np.nan)
        out["price"] = np.full((self.R, t1 - t0), np.nan)
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
                out["price"][:, t - t0] = self.last_price
        return out
