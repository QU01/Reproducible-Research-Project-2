# Finanzas: deuda, tipos de interés, flujos de capital y crisis

Objetivo: dotar al modelo (hoy sin módulo financiero) de (i) un panel país-año 1950–2024 con deuda
pública y externa, servicio de la deuda, ingresos/gastos fiscales, tipos, cuenta corriente, reservas,
crédito y crisis; (ii) series mundiales (tipo real de EE.UU., dólar, oleadas de crisis); y (iii) una
especificación concreta, con parámetros y objetivos de calibración, para un módulo de deuda y crisis
que alimente el `SFD` (*state fiscal distress*) del PSI, la dinámica centro-periferia y el conflicto.

Construcción: `src/sources/finanzas.py` → `build()`
(`.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import finanzas; finanzas.build()"`).
Salidas: `data/processed/sources/finanzas.csv`, `finanzas_world.csv`, `finanzas_dict.json`
(descripción y cobertura de cada variable). Ratios en **fracciones** (0,60 = 60 % del PIB).

---

## 1. Datos

### 1.1 Fuentes (todas vía `raw.githubusercontent.com` / `media.githubusercontent.com`)

| Fuente | Qué aporta | Ruta raw |
|---|---|---|
| **Global Macro Database** (Müller, Xu, Lehbib y Chen 2025), versión 2025_12, ficheros por variable del repo `KMueller-Lab/Global-Macro-Database-Stata` | Deuda pública combinada/gobierno general/central (empalma IMF HPDD, WEO, JST, Reinhart-Rogoff, Mitchell…), ingresos, gasto, impuestos, saldo fiscal, cuenta corriente, tipos (largo, corto, oficial), inflación, REER, tipo de cambio, PIB en USD; **dummies de inicio de crisis** bancaria, cambiaria y soberana (Laeven-Valencia con relleno de Reinhart-Rogoff) | `data/raw/finanzas/gmd/`, crisis en `large/` (12 MB c/u por notas repetidas; git-ignorado, se re-descarga) |
| **WDI** (Banco Mundial) vía paquete DDF de open-numbers (actualizado a 2024) | Deuda externa/INB, servicio de deuda/INB y /exportaciones, deuda a corto/reservas, reservas (meses de importación y USD), IED, crédito privado/PIB, intereses/ingresos, tipo real, cuenta corriente, crecimiento | `data/raw/finanzas/wdi/` |
| **IMF Historical Public Debt Database** (Abbas et al. 2010; Mauro et al. 2015) | Deuda bruta/PIB 1800–2015, 189 países (validación de GMD) | `hpdd_debt_gdp.csv` |
| **Laeven y Valencia (2018)** *Systemic Banking Crises Revisited* | 151 episodios bancarios 1970–2017 con pérdida de producto, coste fiscal, NPL máximos, aumento de deuda | `laeven_valencia_2018_episodes.csv` |
| **Laeven y Valencia (2026)** actualización 1970–2025 (Tabla A1 extraída) | Fechas de crisis bancarias sistémicas hasta 2025 | `laeven_valencia_2026_banking.csv` |
| **Jordà-Schularick-Taylor Macrohistory R6** | 18 economías avanzadas 1870–2020: crédito bancario/PIB, deuda, tipos, `crisisJST` | `JSTdatasetR6.xlsx` (hoja `JRT6 Data`; requiere `openpyxl`) |
| **FRED** DTWEXM (1973–2019) y DTWEXBGS (2006–) | Índice nominal del dólar (medias anuales) | `fred_usd_*_index.csv` |
| PWT 10.01 (`data/raw/pwt1001.csv`, ya en el repo) | Crecimiento real `g_real` 1951–2019 (el `rGDP` de GMD-Stata final crece como el PIB nominal y se descartó) | — |

Descartado o no accesible: el xlsx original de Laeven-Valencia con años de crisis cambiaria/soberana
(no está en GitHub; GMD ya lo integra), Harvard BFFS/Reinhart-Rogoff original con nombres de país (las
copias halladas no traen país o tienen crisis cambiarias vacías), el Excel de la HPDD en imf.org, FRED
directo, y el factor del ciclo financiero global de Miranda-Agrippino y Rey (no hay copia). El
repositorio de la GMD también publica en `data/final/` otras variables (M0–M4, HPI) si se necesitan.

### 1.2 Variables y cobertura (panel 1950–2024; 16 635 filas país-año)

| Variable | Descripción | Obs. | Países | Años |
|---|---|---|---|---|
| `debt_gdp` | Deuda pública bruta/PIB (GMD combinada) | 9 802 | 197 | 1950–2024 |
| `debt_gdp_gen`, `debt_gdp_cgov`, `debt_gdp_hpdd`, `debt_gdp_cgov_wdi`, `debt_gdp_jst` | Alternativas/validación | 1,3k–9,6k | 18–195 | |
| `gov_rev_gdp`, `gov_exp_gdp`, `gov_tax_gdp`, `gov_balance_gdp` | Ingresos, gasto, impuestos, saldo (−=déficit) | ~10k (tax 3,5k) | ~198 | 1950–2024 |
| `interest_rev` | Intereses/ingresos públicos (WDI) | 4 484 | 160 | 1972– |
| `implicit_rate` | Tipo implícito = intereses/PIB ÷ deuda₋₁ | 4 372 | 158 | 1972– |
| `ext_debt_gni`, `debt_service_gni`, `debt_service_exports`, `st_debt_reserves` | Deuda externa (solo países de ingreso bajo/medio, DRS) | ~5k | 113–121 | 1970– |
| `reserves_months`, `reserves_usd` | Reservas | 7–9k | ~180 | 1960– |
| `ca_gdp` (`ca_gdp_wdi`), `fdi_in_gdp` | Cuenta corriente, IED | 9,3k / 9,2k | 207 / 201 | |
| `credit_priv_gdp`, `credit_gdp_jst` | Crédito privado/PIB (WDI; JST 18 países) | 7,5k / 1,3k | 186 / 18 | |
| `ltrate`, `strate`, `cbrate`, `infl`, `real_rate_wdi` | Tipos nominales, inflación | 3k–12k | 83–216 | |
| `reer`, `usdfx`, `fx_depr`, `ngdp_usd` | Tipo de cambio real, nominal, depreciación, PIB USD | 10–15k | 180–235 | |
| `g_real`, `r_real_lt`, `r_minus_g`, `r_minus_g_eff` | Crecimiento, tipo real, r−g (bono largo; tipo implícito) | 14k / 3k / 3k / 3,6k | 227 / 83 / 83 / ~150 | |
| `crisis_bank`, `crisis_currency`, `crisis_sovdebt`, `crisis_any`, `crisis_twin` | **Inicio** de crisis (GMD) | ~9,1k | 160–163 | 1950–2019/20 |
| `lv_bank_onset`, `lv_bank_active` | Crisis bancaria sistémica LV-2026 (inicio / en curso) | 12,8k | 238 | 1970–2024 |
| `lv_output_loss`, `lv_fiscal_cost`, `lv_peak_npl`, `lv_debt_increase` | Costes por episodio (en el año de inicio) | 90–135 | 72–104 | 1976–2014 |
| `crisis_jst`, `ltrate_jst`, `stir_jst` | JST | ~1,3k | 18 | 1950–2020 |

Cobertura sobre las 180 economías del panel del modelo (PWT 1950–2019): `debt_gdp` 81 % de las
celdas país-año (174 países), `gov_rev_gdp` 82 %, crisis 78–80 %, `ca_gdp` 74 %, `ext_debt_gni` 45 %
(no existe para economías de ingreso alto), `r_minus_g_eff` 36 %, `ltrate` 26 %. Los huecos de deuda
se concentran en 1950–1969 para África y Asia (antes de la independencia o sin estadísticas).

**Series mundiales** (`finanzas_world.csv`, 1950–2024): `us_ltrate`, `us_strate`, `us_policy_rate`,
`us_infl`, `us_real_ltrate`, `us_real_strate` (proxy del tipo mundial libre de riesgo y del ciclo
financiero global), `us_reer`, `us_debt_gdp`, `usd_index_major`/`usd_index_broad`, proporción de
países en inicio de crisis (simple y ponderada por PIB), `share_bank_active_lv`, deuda mundial
ponderada y mediana, mediana de r−g.

### 1.3 Hechos estilizados en los datos (1950–2019)

* **Frecuencia anual de inicio** (por país-año): bancaria 2,0 % (188 episodios), cambiaria 3,6 %
  (331), soberana 1,6 % (145), alguna 6,6 %, gemela 0,44 %. JST (18 avanzadas): 2,0 %.
* **Régimen de Bretton Woods / represión financiera**: casi cero crisis bancarias en 1950–1972
  (0,0 %–0,4 % por década) frente a 3,1 % (1980s) y 5,6 % (1990s); soberanas 0,4 % (1970s) → 2,9–3,0 %
  (1980s–90s) → 0,9 % (2000s–2010s). Coincide con Bordo et al. (2001) y Reinhart y Rogoff (2009).
* **Deuda mundial** (ponderada por PIB): 74 % (1950, herencia bélica) → 36 % (1970) → 51 % (1990) →
  62 % (2007) → 84 % (2019). La licuación 1950–1975 ocurre con r−g ≈ −3 % (mediana por país:
  −3,0 % 1950s, −3,8 % 1970s) y se invierte a r−g > 0 en los 80–90 (+0,8 % / +1,5 %), para volver a ser
  negativo desde 2000 — el patrón de Mauro et al. (2015) y Blanchard (2019).
* **Tipo real de EE.UU.** (corto, ex post): media 0,7 %, σ = 2,0 pp; mínimo −5,8 % (1970s), máximo
  +5,3 % (principios de los 80, *shock* Volcker que precede a la crisis de deuda de 1982).
* **Deuda en el año previo a un impago soberano**: mediana 52 % del PIB (p25 30 %, p75 86 %);
  deuda externa mediana 66 % del INB (p25 41 %). Frente a medianas incondicionales de 39 % y 43 %:
  los impagos periféricos ocurren con niveles modestos (*debt intolerance*).
* **Laeven-Valencia 2018** (episodios bancarios): pérdida de producto acumulada mediana 23 % del PIB
  tendencial (34 % en países ricos, 13 % en el resto), coste fiscal mediano 8,7 % del PIB (7 % ricos,
  11 % resto), aumento de deuda pública mediano 12,8 pp (20 pp ricos, 10 pp resto).

---

## 2. Literatura y parámetros

### 2.1 Dinámica de la deuda y r−g
* Identidad: `d_{t+1} = d_t (1+r_t)/(1+g_t) − pb_t + sfa_t` (d deuda/PIB, pb saldo primario/PIB, sfa
  ajustes stock-flujo: rescates bancarios, valoración cambiaria, quitas). Con r<g la deuda se licua
  sin superávit (Blanchard 2019; Mauro y Zhou 2021 muestran que r−g<0 no impide impagos en emergentes
  porque r−g se dispara precisamente en las crisis).
* **Represión financiera**: Reinhart y Sbrancia (2015) estiman una "licuación" de 3–4 % del PIB anual
  en avanzadas en 1945–1980 mediante tipos reales negativos — consistente con nuestras medianas.
* **Función de reacción fiscal** (Bohn 1998): `pb_t = α + β d_{t-1} + γ g_t`; β≈0,02–0,05 en
  avanzadas (Bohn 0,054 EE.UU.; Mendoza y Ostry 2008 ≈0,04 avanzadas, ≈0,02–0,04 emergentes).
  **Fatiga fiscal** (Ghosh, Kim, Mendoza, Ostry y Qureshi 2013): la respuesta es cúbica en d, cae y se
  vuelve negativa para deudas altas (≈90–150 %), lo que define un límite de deuda y un "espacio
  fiscal". Nuestra estimación de efectos fijos (1972–2019, 3 807 obs., saldo primario construido con
  `gov_balance_gdp + interest_rev·gov_rev_gdp`): β = 0,0136 (e.e. 0,0064), γ = 0,18 (0,03), α = −0,026.

### 2.2 Umbrales de deuda
* Reinhart y Rogoff (2010): crecimiento mediano cae ~1 pp y la media se vuelve negativa por encima de
  90 % del PIB. **Herndon, Ash y Pollin (2014)** corrigen errores de hoja de cálculo y ponderación: la
  media sobre 90 % es +2,2 %, no −0,1 %; no hay precipicio. Pescatori, Sandri y Simon (2014) y
  Eberhardt y Presbitero (2015): no hay umbral universal; la trayectoria de la deuda importa más.
  Nuestros datos (crecimiento en t según deuda en t−1, mediana): <30 % → 4,5 %; 30–60 % → 3,9 %;
  60–90 % → 3,5 %; >90 % → 2,9 %. Gradiente suave (≈ −0,5 pp por cada 30 pp), sin salto; y la
  causalidad inversa es probable. **Recomendación: no imponer un umbral de crecimiento; usar un efecto
  lineal pequeño (≈ −0,015 en g por unidad de d, a lo sumo) o ninguno.**
* **Intolerancia a la deuda** (Reinhart, Rogoff y Savastano 2003): países con historial de impago
  entran en crisis con deuda externa de 30–40 % del PNB (más de la mitad de los impagos ocurre con
  <60 %). Umbrales operativos del marco FMI-BM para países de bajo ingreso (DSF 2017): VP deuda externa
  / PIB 30/40/55 %, servicio / exportaciones 10/15/21 %, deuda pública VP / PIB 35/55/70 % según
  capacidad institucional débil/media/fuerte. Manasse, Roubini y Schimmelpfennig (2003): deuda externa
  > ~50 % del PIB es la principal rama de su árbol de crisis.
* **Pecado original** (Eichengreen y Hausmann 1999; Eichengreen, Hausmann y Panizza 2005): la
  periferia no puede endeudarse externamente en su moneda; su deuda está dolarizada, de modo que una
  depreciación multiplica la carga. Ésta es la traducción financiera más directa del centro-periferia.

### 2.3 Modelos de impago soberano
* **Eaton y Gersovitz (1981)**: el soberano paga mientras el coste de la exclusión (autarquía
  financiera) supere el beneficio de no pagar; el endeudamiento está acotado por la reputación.
* **Arellano (2008)**, trimestral para Argentina: β = 0,953, aversión CRRA 2, r* = 1,7 %,
  probabilidad de reentrada θ = 0,282 por trimestre (exclusión media ≈ 1 año), coste de producto
  asimétrico `y_def = min(y, 0,969·E[y])`; genera impagos en recesiones, diferenciales contracíclicos y
  frecuencia de impago ≈ 3 % anual. Aguiar y Gopinath (2006): choques de tendencia. Mendoza y Yue
  (2012): el coste de producto sale endógeno de la pérdida de acceso a insumos importados.
* **Evidencia empírica**: Tomz y Wright (2007): solo ~62 % de los impagos ocurre con producto bajo
  tendencia (relación débil). Borensztein y Panizza (2009): caída de crecimiento ≈1–2,5 pp en el año
  del impago, efecto de corta duración. Cruces y Trebesch (2013): quita media ≈ 37 % (mayor quita →
  mayores diferenciales y exclusión más larga). Meyer, Reinhart y Trebesch (2022): quitas del orden
  de 40–45 % en 200 años de bonos; los acreedores obtienen aún así primas positivas.

### 2.4 Ciclo financiero global, paradas súbitas y privilegio exorbitante
* **Rey (2013)**, Miranda-Agrippino y Rey (2020): un factor global (VIX, política monetaria de EE.UU.)
  mueve flujos brutos, crédito y precios de activos en todo el mundo; el "trilema" se reduce a un
  "dilema" para la periferia. En nuestras regresiones el tipo real corto de EE.UU. es el predictor más
  robusto de las tres crisis (ver 2.6).
* **Paradas súbitas** (Calvo 1998; Calvo, Izquierdo y Mejía 2004): caídas bruscas de entradas de
  capital (>2 σ) que obligan a cerrar el déficit por cuenta corriente vía recesión y depreciación; su
  probabilidad aumenta con la dolarización de pasivos y una base de transables pequeña. Reinhart,
  Reinhart y Trebesch (2016): los ciclos de auge-caída de materias primas y de flujos de capital
  ("doble auge") preceden a oleadas de impagos (1820s, 1870s, 1930s, 1980s).
* **Privilegio exorbitante** (Gourinchas y Rey 2007): EE.UU. obtiene un diferencial de rentabilidad
  de ≈2 pp anuales (≈3 pp post-1973) entre sus activos y sus pasivos externos — el centro emite el
  activo seguro y cobra una renta financiera a la periferia. Para el modelo: el tipo de la potencia
  hegemónica = r*; la periferia paga r* + prima.
* **Sistema-mundo**: Arrighi (1994) — las "expansiones financieras" marcan la fase final (señal de
  crisis) de cada ciclo hegemónico; dependencia financiera y "integración financiera subordinada"
  (Kaltenbrunner y Painceira 2015) y jerarquía de monedas (Cohen 1998; Fritz, de Paula y Prates 2018).
  Estas ideas justifican primas de riesgo y participación de deuda en moneda extranjera crecientes con
  la periferialidad.

### 2.5 Crisis bancarias y ciclos de crédito
* **Schularick y Taylor (2012)**: logit de crisis sobre 5 retardos del crecimiento de Δlog(crédito
  real): suma de coeficientes ≈ 7 (1870–2008), AUC ≈ 0,7. Jordà, Schularick y Taylor (2013): las
  recesiones precedidas por auges de crédito son más profundas. Mian, Sufi y Verner (2017): un aumento
  de la deuda de los hogares/PIB predice menor crecimiento a 3–5 años.
* Replicación con nuestros datos (JST, 1950–2019, n = 1 150): `logit P(crisis) = −4,53 + 4,66·Σ_{k=1..5}
  Δlog(crédito/PIB)_{t−k}` (e.e. 1,19). Panel amplio (WDI, 1960–2019, n = 4 088):
  `b = 2,17` (0,48) por unidad de aumento de crédito privado/PIB en 5 años.

### 2.6 Costes de las crisis
* **Cerra y Saxena (2008)**: pérdidas grandes y **persistentes** (sin rebote): ≈ 4–5 % del PIB en
  crisis cambiarias, ≈ 7,5 % en bancarias y ≈ 10 % en gemelas tras 10 años; rebote parcial solo en
  guerras civiles. Reinhart y Rogoff (2009): tras crisis bancarias la deuda pública real aumenta
  ≈ 86 % en tres años, paro +7 pp, producto −9 % pico-valle. Laeven y Valencia (2018): ver 1.3.
  Furceri y Zdzienicka (2012): crisis de deuda → −10 % de producto a 8 años (estimación alta).
* **Proyecciones locales en nuestros datos** (log PIB real PWT, t+h − t−1, efectos fijos país y año,
  2 retardos de crecimiento, 1951–2019; e.e. por país):

| Inicio de crisis | h=0 | h=1 | h=2 | h=3 | h=5 | h=8 |
|---|---|---|---|---|---|---|
| Bancaria | −1,3 % (0,4) | −3,1 (0,7) | −3,6 (0,8) | −4,2 (0,9) | −4,1 (1,2) | **−4,6 (1,3)** |
| Cambiaria | −1,1 (0,5) | −1,5 (0,7) | −1,3 (0,8) | −1,2 (1,0) | −0,4 (1,1) | 0,0 (1,3) |
| Soberana | −1,8 (0,4) | −3,5 (0,8) | −4,2 (1,1) | −3,9 (1,2) | −5,0 (1,4) | **−5,2 (1,5)** |
| Gemela | −2,5 (1,4) | −4,8 (2,4) | −5,3 (2,5) | −5,1 (2,8) | −4,4 (3,3) | −4,6 (3,5) |

  Cambio de deuda/PIB tras el inicio (pp, mismo método): bancaria +8,8 (h0), +6,6 (h2), +6,7 (h4);
  cambiaria +11,9 (h0; efecto valoración de la deuda en divisas), +5,5 (h4); soberana ≈0 (la quita y la
  depreciación se compensan).

### 2.7 Crisis, fiscalidad e inestabilidad política
* **Goldstone (1991)**: la crisis fiscal del Estado (SFD) es una de las tres componentes del PSI
  (junto con la movilización de masas y de élites). **Turchin y Nefedov (2009)**, Turchin (2016): la
  fase de "estanflación" de los ciclos seculares termina en bancarrota estatal que precede a la crisis
  política; Turchin mide SFD en EE.UU. con deuda federal/PIB y desconfianza en las instituciones.
* **Funke, Schularick y Trebesch (2016)**: tras crisis financieras el voto de extrema derecha sube
  ≈30 % y aumentan fragmentación y protestas (no ocurre tras recesiones normales). **Ponticelli y
  Voth (2020)**: los recortes de gasto (austeridad) elevan disturbios, manifestaciones y huelgas
  (Europa 1919–2008), de forma no lineal con el tamaño del recorte.
* Nuestros datos: logit de inicio de conflicto armado (UCDP, panel del modelo) sobre "algún inicio de
  crisis en t, t−1 o t−2" con controles de log PIBpc₋₁ y log población: b = 0,30 (e.e. 0,13, p = 0,02)
  → odds ×1,35 sobre una base de 3,4 %/año. Por tipo: soberana 0,28 (0,22), bancaria 0,29 (0,21),
  cambiaria 0,28 (0,16) — magnitud similar, poco precisas por separado.

### 2.8 Probabilidad de crisis: estimaciones propias (logit, 1950–2019)

Covariables retardadas un año; `r*` = `us_real_strate` (en fracción, es decir 0,01 = 1 pp).

| Ecuación | Coeficientes (e.e.) | n | pseudo-R² |
|---|---|---|---|
| Soberana ~ deuda | const −2,65; `debt_gdp` **0,33** (0,14); r* **20,0** (4,5); `g_real` −5,5 (1,3); ln PIBpc −0,19 (0,08) | 7 039 | 0,043 |
| Soberana ~ deuda externa | `ext_debt_gni` 0,20 (0,11); `reserves_months` −0,10 (0,05); r* 17,7 (5,8); g −5,8 (2,0) | 2 931 | 0,053 |
| Soberana ~ servicio | const −4,20; `debt_service_exports` **2,70** (0,51); r* 14,0 (5,1); g −5,1 (1,7) | 3 559 | 0,057 |
| Bancaria ~ crédito | const −5,24; Δ5 `credit_priv_gdp` **2,17** (0,48); r* 20,0 (4,6); `ca_gdp` ≈0 | 4 088 | 0,046 |
| Cambiaria | const −2,51; `reserves_months` −0,19 (0,05); r* 15,3 (4,5); `infl` 0,39 (0,17) | 2 998 | 0,050 |

Lectura: +1 pp en el tipo real de EE.UU. multiplica las odds de crisis por ≈ e^{0,15–0,20} = 1,16–1,22;
+10 pp de servicio/exportaciones ×1,31; +30 pp de deuda/PIB solo ×1,10 (la deuda por sí sola predice
mal; lo que importa es su coste y su moneda). Advertencia: r* es una serie común a todos los países, por
lo que su coeficiente recoge también otras perturbaciones globales de esos años (p. ej. 1980–82).

---

## 3. Especificación recomendada para el módulo de deuda y crisis

Paso anual por país *i*; notación: `d` deuda pública/PIB, `x` deuda externa/PIB, `φ_i ∈ [0,1]`
periferialidad (1 = periferia; del módulo sistema-mundo), `r*` tipo real mundial (hegemón), `g`
crecimiento real, `H_i` historial de impago (decae).

### 3.1 Tipo mundial
Exógeno en la validación histórica: `r*_t = us_real_strate` (o `us_real_ltrate` para la deuda larga;
media 2,1 %, σ 2,2 pp). En simulación libre: `r*_t = r̄ + ρ (r*_{t−1} − r̄) + ε`, con r̄ = 0,01–0,02,
ρ ≈ 0,7, σ_ε ≈ 0,015; y régimen de represión financiera (1950–1972): r* − 0,02 y hazard bancario ×0,1.

### 3.2 Tipo efectivo y prima de riesgo
```
r_i = r* + s_i
s_i = s0 + s_φ·φ_i + s_d·max(0, d_i − D*_i) + s_H·H_i          (en fracciones)
```
s0 = 0,005; s_φ = 0,03–0,05 (diferencial típico EMBI de 300–500 pb para periferia); s_d = 0,03–0,05
por unidad de deuda por encima del umbral (≈3–5 pb por pp: Laubach 2009; Baldacci y Kumar 2010);
s_H = 0,02 tras un impago, decayendo a la mitad cada ~5 años (Cruces y Trebesch 2013). El tipo
implícito observado (`implicit_rate`, mediana ≈ 6,6 % en 1980) y `r_minus_g_eff` sirven para calibrar.

### 3.3 Acumulación de deuda
```
d_{t+1} = d_t·(1 + r_i)/(1 + g_i) − pb_i + sfa_i
pb_i    = α_i + β·d_t − κ·max(0, d_t − D_fat)² + γ·g_i          (fatiga fiscal, Ghosh et al. 2013)
sfa_i   = μ·ε_i·x_i                         (valoración: ε depreciación real, μ = cuota en divisas)
        + c_B·1[crisis bancaria]            (rescate)
        − h·d_t·1[impago]                   (quita)
```
β = 0,014 (propio; rango de literatura 0,02–0,05), γ = 0,18, α_i ≈ −0,026 (+efecto fijo por
país/régimen); D_fat ≈ 1,0 (centro) / 0,6 (periferia), κ ≈ 0,05; μ = 0,2 (centro) … 0,8 (periferia,
pecado original); c_B = 0,07–0,09 en el impacto (LP: +8,8 pp; LV: mediana 12,8 pp acumulada; coste
fiscal directo mediano 8,7 %); h = 0,37 (Cruces-Trebesch) aplicado a la deuda externa. Durante una
crisis cambiaria ε ≈ 0,3–0,5 (Frankel y Rose 1996 definen crisis con ≥25 % de depreciación).
Ingresos públicos: `gov_rev_gdp` observado (o del módulo fiscal) acota pb; el servicio de la deuda
`interest_rev = r_i·d_t / rev_i` entra en la presión fiscal (3.6).

### 3.4 Riesgos de crisis (hazards anuales de inicio)
```
logit P_sov  = a0 + a_d·(d_t − D*_i) + a_s·DS_i + a_r·r*_t + a_g·g_{t−1} + a_H·H_i
logit P_bank = b0 + b_c·Δ5(crédito/PIB) + b_r·r*_t + b_R·1[represión]
logit P_cur  = c0 − c_R·reservas_meses + c_r·r*_t + c_π·π_{t−1} + c_x·φ_i·x_i
```
Parámetros (de 2.8 salvo indicación): a_r = 15–20, a_g = −5,5, a_s = 2,7 por unidad de
servicio/exportaciones (o 0,33 por unidad de `d` si no se modela el servicio); **umbral de intolerancia**
`D*_i = 0,4 + 0,8·(1 − φ_i) − 0,15·H_i` (≈0,4–0,5 periferia con historial, ≈1,2 centro; Reinhart et al.
2003; DSF). Con un término no lineal adicional `a_d = 0,33` por debajo del umbral y ≈2 por encima
(recoge que el riesgo se concentra en la cola, cf. Manasse et al. 2003), a0 calibrado para que la
frecuencia media sea 1,6 %/año (≈ −4,2 con las demás covariables en sus medias). b_c = 2,2 (panel) o
4,7 por unidad de crecimiento log del crédito en 5 años (JST); b_r = 20; b0 tal que P ≈ 2 %/año
fuera de represión y ≈0,2 % en 1950–1972. c_R = 0,19; c_r = 15; c_π = 0,39; c0 → 3,6 %/año.
**Contagio**: añadir `+ λ·share_crisis_{t−1}` (proporción mundial en crisis del mismo tipo, en
`finanzas_world.csv`), λ ≈ 3–5, para generar las oleadas de 1982–83 y 1994–2002.
**Crisis gemelas**: si ocurre una, multiplicar las odds de las otras dos ×3 el mismo año (0,44 %
observado frente a ≈0,1 % bajo independencia).

### 3.5 Consecuencias
* **Producto** (choque de nivel persistente sobre la productividad/`rgdpna`): bancaria −1,5 % en t,
  −2 % adicional en t+1, sin rebote (−4,5 % total; Cerra-Saxena ≈−7,5 %); soberana −2 % en t, −2 % en
  t+1, −1 % en t+2 (−5 %); cambiaria −1,2 % transitorio que se recupera en ~5 años; gemela: el máximo
  de ambas +1 pp. Incertidumbre: ±1,5 pp (e.e. de las LP).
* **Acceso al mercado**: tras impago, exclusión con probabilidad de reentrada θ ≈ 0,3–0,5 anual
  (Arellano θ trimestral 0,28 ⇒ exclusión ~1 año; Cruces-Trebesch: 5–8 años con quitas altas);
  durante la exclusión `pb ≥ 0` forzoso (austeridad) y cuenta corriente ≥ 0.
* **Flujos centro-periferia**: el pago de intereses externos `r_i·x_i·PIB_i` es una transferencia de
  la periferia al centro (renta financiera, complementaria al intercambio desigual del módulo
  comercial); el impago la interrumpe. El privilegio exorbitante del hegemón: su pasivo externo paga
  r* mientras sus activos rinden r* + 0,02.

### 3.6 Enlace con PSI (SFD) y conflicto
```
SFD_i = σ( w1·(d_i/D*_i − 1) + w2·interest_rev_i + w3·(−pb_i) ) + ψ·1[crisis sov./banc. en t..t−2]
```
con σ logística, w1 ≈ 2, w2 ≈ 5 (20 % de los ingresos en intereses ≈ presión máxima), w3 ≈ 10, y ψ ≈
0,2 en escala [0,1]. Sustituye el proxy actual (baja cohesión). Validar que el efecto sobre el riesgo
de conflicto implícito en el modelo reproduzca odds ×1,35 (e.e. amplio: ×1,04–×1,75) tras una crisis,
y que la austeridad forzosa (pb sube >2 pp del PIB) eleve la movilización de masas (Ponticelli-Voth).
Canal político adicional: Funke et al. (2016) → aumento de la movilización de élites/polarización.

### 3.7 Objetivos de calibración (momentos a reproducir, 1950–2019)
1. Frecuencias de inicio por década (bancaria/cambiaria/soberana): 1950s 0/6,4/0,8 %; 1960s
   0,1/5,7/1,9 %; 1970s 0,4/1,6/0,4 %; 1980s 3,1/4,6/2,9 %; 1990s 5,6/5,6/3,0 %; 2000s 2,1/1,8/0,9 %;
   2010s 0,5/2,2/0,9 %.
2. Deuda mundial ponderada por PIB: 0,74 (1950), 0,36 (1970), 0,51 (1990), 0,62 (2007), 0,84 (2019);
   mediana por país 0,20 en 1950 y 0,39 en el conjunto 1950–2019.
3. Mediana de r−g: −3 % (1950–79), +1 % (1980–99), −1 % (2000–19).
4. Mediana de deuda en t−1 del impago: 0,52 (deuda pública), 0,66 (deuda externa/INB).
5. Pérdidas de producto (tabla 2.6) y aumento de deuda tras crisis bancarias (+7–9 pp).
6. Proporción máxima de países en crisis bancaria activa (LV): 12,8 % en 1995; en 2008–2009 ≈ 10 %
   de los países pero ≈ 50 % del PIB mundial (`share_bank_active_lv_gdpw`; 28 % ya en 2007 por EE.UU.).
7. Series de países concretos con varios impagos: ARG (8 inicios soberanos), TUR, URY, ECU, CHL, NIC,
   CIV (4).

---

## 4. Lagunas y advertencias
* Las dummies de crisis de GMD combinan Laeven-Valencia (1970–2017) con Reinhart-Rogoff (70 países,
  desde 1800); antes de 1970 la cobertura efectiva son esos 70 países, por lo que las frecuencias de
  1950–1969 para la periferia están infra-estimadas (crisis cambiarias mejor cubiertas que bancarias).
  Crisis terminan en 2019–2020; `lv_bank_*` llega a 2024 solo para crisis bancarias.
* No hay serie de deuda en moneda extranjera ni de composición acreedora (bonos vs. oficial, China),
  ni flujos brutos de capital; la deuda externa WDI existe solo para países de ingreso bajo/medio.
  `fdi_in_gdp`, `ca_gdp` y reservas son las mejores aproximaciones a flujos.
* El factor del ciclo financiero global (Miranda-Agrippino-Rey) y el VIX no están disponibles; se usa el
  tipo real de EE.UU. y el índice del dólar (este solo desde 1973).
* `ltrate` solo en 83 países; para r−g en emergentes usar `r_minus_g_eff` (tipo implícito, desde 1972).
* Tipos reales ex post con IPC; en hiperinflaciones `r_real_lt` y `r_minus_g_eff` toman valores
  extremos (recortar o winsorizar al usarlos).
* Las regresiones de §2.6–2.8 son asociaciones reducidas (sin identificación causal); sirven como
  órdenes de magnitud para calibrar, no como parámetros estructurales.
* El Excel de JST necesita `openpyxl` (instalado en `.venv`, no listado en `requirements.txt`); si falta,
  `build()` omite las columnas JST.

## Referencias principales
Abbas, Belhocine, El-Ganainy y Horton (2010) *IMF WP 10/245*; Aguiar y Gopinath (2006) *JIE*;
Arellano (2008) *AER*; Arrighi (1994) *The Long Twentieth Century*; Baldacci y Kumar (2010) *IMF WP
10/184*; Blanchard (2019) *AER*; Bohn (1998) *QJE*; Bordo, Eichengreen, Klingebiel y Martínez-Peria
(2001) *Economic Policy*; Borensztein y Panizza (2009) *IMF Staff Papers*; Calvo (1998) *J. Applied
Econ.*; Calvo, Izquierdo y Mejía (2004) *NBER WP 10520*; Cerra y Saxena (2008) *AER*; Cruces y Trebesch
(2013) *AEJ: Macro*; Eaton y Gersovitz (1981) *REStud*; Eichengreen y Hausmann (1999); Eichengreen,
Hausmann y Panizza (2005); Frankel y Rose (1996) *JIE*; Funke, Schularick y Trebesch (2016) *EER*;
Furceri y Zdzienicka (2012) *JIMF*; Ghosh, Kim, Mendoza, Ostry y Qureshi (2013) *EJ*; Goldstone (1991)
*Revolution and Rebellion*; Gourinchas y Rey (2007) en *G7 Current Account Imbalances* (NBER);
Herndon, Ash y Pollin (2014) *CJE*; Jordà, Schularick y Taylor (2013) *JMCB*, (2017) *NBER Macro
Annual*; Laeven y Valencia (2018) *IMF WP 18/206*, (2020) *IMF Econ. Rev.*; Laubach (2009) *JEEA*;
Manasse, Roubini y Schimmelpfennig (2003) *IMF WP 03/221*; Mauro, Romeu, Binder y Zaman (2015) *JME*;
Mauro y Zhou (2021) *IMF Econ. Rev.*; Mendoza y Ostry (2008) *JME*; Mendoza y Yue (2012) *QJE*; Meyer,
Reinhart y Trebesch (2022) *QJE*; Mian, Sufi y Verner (2017) *QJE*; Miranda-Agrippino y Rey (2020)
*REStud*; Müller, Xu, Lehbib y Chen (2025) *The Global Macro Database*; Ponticelli y Voth (2020) *JCE*;
Reinhart y Rogoff (2009) *This Time Is Different*, (2010) *AER P&P*; Reinhart, Rogoff y Savastano (2003)
*BPEA*; Reinhart, Reinhart y Trebesch (2016) *AER P&P*; Reinhart y Sbrancia (2015) *Economic Policy*;
Rey (2013) *Jackson Hole*; Schularick y Taylor (2012) *AER*; Tomz y Wright (2007) *JEEA*; Turchin y
Nefedov (2009) *Secular Cycles*; Turchin (2016) *Ages of Discord*.
