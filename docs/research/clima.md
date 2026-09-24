# Clima y ecología: datos, literatura y módulo propuesto

> Documento de investigación para el modelo macrohistórico basado en agentes (`src/model.py`).
> Código de datos: `src/sources/clima.py` → `data/processed/sources/clima.csv`,
> `clima_world.csv` y `clima_dict.json`. Hoy el modelo **no** tiene clima ni ecología: el recurso
> genérico `R` (combustibles fósiles, minerales y bosques agregados) se extrae con una capacidad
> Hubbert-logística y un precio que vacía el mercado mundial, sin costes externos. Aquí proponemos
> cerrar ese circuito: extracción → emisiones → concentración → temperatura global → temperatura
> local → daños (productividad, capital, conflicto), junto con un stock de degradación ecológica y
> un flujo de intercambio ecológico desigual entre centro y periferia.

---

## 0. Resumen ejecutivo

| Bloque | Ecuación recomendada | Parámetro central (rango) | Fuente |
|---|---|---|---|
| Emisiones fósiles | $E^{fos}_t=\varepsilon_t\,\phi\,R_t$ | ε con caída −0,25 %/año (−0,1 a −1 %) | OWID/GCP; derivado en datos |
| Emisiones de uso del suelo | $E^{luc}_{i,t}=e_L\cdot\text{deforestación}_{i,t}$ | ≈ 4,7–6,6 GtCO₂/año, 95 % en periferia | GCP 2024 vía OWID |
| Temperatura global (opción A) | $T_t=T_{1950}+\lambda\,(C_t-C_{1950})$ | λ = 0,45 °C/1000 GtCO₂ (0,27–0,63) | IPCC AR6 TCRE; 0,46 en nuestros datos |
| Temperatura global (opción B) | DICE-2023/FaIR 4 cajas + 2 cajas térmicas | ECS = 3,0 °C; ver §5.3 | Barrage & Nordhaus 2024 |
| Temperatura local | $T_{i,t}=\bar T_i+\beta_i\,\Delta T_t+\sigma_i\,\epsilon_{i,t}$ | β mediana 1,33 (IQR 1,14–1,65); σ ≈ 0,30 °C | estimado en datos (FAO vs GISTEMP) |
| Daño a productividad | $\ln A^{ef}_{i,t}=\ln A_{i,t}+D_{i,t}$, $D_{i,t}=\rho_D D_{i,t-1}+h(T_{i,t})-h(\bar T_i)$ | $h(T)=0{,}0127T-0{,}000487T^2$; óptimo 13,1 °C; ρ_D = 0,8 (0–1) | BHM 2015 (replicado exacto) |
| Desastres → capital | $K\leftarrow K(1-s_{i,t})$, $s\sim$ Bernoulli($p_i e^{\kappa\Delta T}$)×LogNormal | p ≈ 0,24–0,34; E[s·Y/K] ≈ 0,5 %; κ = 0,1/°C (0–0,3) | EM-DAT 1990–2019; Hsiang & Jina 2014 |
| Conflicto | $\text{logit}\,h_{i,t}=\ldots+\gamma_c z^{T}_{i,t}$ | γ_c = 0,05 por DE (0–0,11) | Burke-Hsiang-Miguel 2015b; Mach et al. 2019; nuestra réplica ≈ 0 |
| Degradación ecológica | $N_{i,t+1}=N_{i,t}+g N_{i,t}(1-N_{i,t})-\eta\,x^{ren}_{i,t}-\zeta\,\Delta T^+$ ; TFP ∝ $N^{\xi}$, capacidad Hubbert ∝ N | ξ = 0,05–0,10; g = 0,02–0,05 | Dasgupta 2021; Johnson et al. 2021 |
| Intercambio ecológico desigual | $U_{c\leftarrow p,t}=\omega\,\tilde m_{c,t}$ (recursos incorporados por $ de importación) | 2015: 12 Gt materiales, 822 Mha, 21 EJ, 188 M años-persona | Hickel et al. 2022; Dorninger et al. 2021 |

Objetivos de calibración clave (todos en `clima*.csv`): CO₂ atmosférico 312,8 ppm (1950) → 411,7 ppm
(2019); anomalía global preindustrial suavizada 0,27 °C (1950) → 1,07 °C (2014, media móvil de 11 años);
emisiones fósiles 5,9 → 37,1 GtCO₂/año; emisiones acumuladas 662 → 2542 GtCO₂; fracción aerotransportada
≈ 0,42; coeficientes BHM (0,0127; −0,000487) re-estimados en nuestro panel PWT (0,0065; −0,00026;
óptimo 12,5 °C); huella/biocapacidad mundial 0,72 (1961) → 1,74 (2019); Living Planet Index −69 %
(1970–2018).

---

## 1. Datos recopilados

### 1.1 Accesibilidad y procedencia

El entorno sólo alcanza `raw.githubusercontent.com` (más PyPI y npm). Por ello cada fuente se toma de un
repositorio oficial (Our World in Data, `datasets/`, `open-numbers` = World Bank WDI / Gapminder) o de un
espejo de replicación verificado. Las URL exactas están en `SOURCES`, `EMDAT`, `WDI`, `GAP` y `GFN_FILES`
de `src/sources/clima.py`; `build()` descarga sólo lo que falte y rechaza punteros git-lfs.

| Archivo crudo (`data/raw/clima/`) | Contenido | Origen (espejo) | Cobertura |
|---|---|---|---|
| `owid-co2-data.csv` (14 MB) | CO₂ territorial, de consumo, acumulado, por combustible, uso del suelo, CH₄, N₂O, GEI, contribución al calentamiento (Jones et al. 2023) | `owid/co2-data` (oficial) | 1750–2023, 215 países con ISO3 |
| `owid-energy-data.csv` (9 MB) | Producción de carbón/petróleo/gas (TWh), consumo fósil, energía primaria | `owid/energy-data` (oficial) | 1900–2024 |
| `bhm_GrowthClimateDataset.dta` (7 MB) | Datos de réplica de Burke, Hsiang & Miguel (2015): temperatura y precipitación ponderadas por población (U. Delaware), crecimiento WDI | réplica UW (Stanford Digital Repository) | 1960–2010, 167 países |
| `fao_temperature_change.csv` (8 MB) | FAOSTAT *Temperature change on land* (basado en NASA GISTEMP), anomalía vs 1951–1980, mensual/estacional/anual, y DE climatológica | espejo en GitHub del bulk FAOSTAT | 1961–2021, 239 áreas |
| `fao_country_codes.csv` | Tabla FAO ↔ M49 ↔ ISO3 | FAOSTAT | — |
| `era5_decadal_temperature.csv` | Temperatura media decadal por país (ERA5, ponderada por área; OWID/Copernicus) | espejo OWID | décadas 1940–2020 |
| `global_temp_annual.csv` | Anomalía media global GISTEMP (base 1951–1980) y HadCRUT5 (base s. XX) | `datasets/global-temp` (oficial) | 1850/1880–2026 |
| `co2_mlo_annmean.csv`, `co2_longterm_owid.csv` | CO₂ Mauna Loa (NOAA/Scripps) y serie larga de núcleos de hielo | `datasets/co2-ppm`; espejo OWID | 1959–2025; −800 ka–2018 |
| `nfa_2018.csv` (12 MB) | National Footprint Accounts 2018 (GFN): huella de consumo, producción, importaciones, exportaciones, biocapacidad, por tipo de tierra | espejo del dataset público de GFN | 1961–2014, 196 países |
| `gfn_nfa2025_percap.csv` | NFA edición 2025: huella de consumo y biocapacidad per cápita (174 archivos por país combinados) | espejo `eldho-se/overshoot-app` | 1961–2024, 160 países + Mundo |
| `large/emdat_natural_1900_2025.csv` (7,5 MB, *git-ignored*) | EM-DAT (CRED/UCLouvain) extracto público: 17 318 desastres naturales con muertes, afectados y daños ajustados por IPC | espejo; licencia EM-DAT prohíbe redistribución → `large/` | 1900–2025 |
| `wdi/*.csv` (22 indicadores) | Bosque, tierra agrícola, rendimientos, fertilizantes, estrés hídrico, población bajo 5 m, agotamiento de recursos y daños por CO₂/PM (ahorro neto ajustado), áreas protegidas, PM2.5, pesca, especies amenazadas | `open-numbers/ddf--open_numbers--world_development_indicators` | 1960–2023 según indicador |
| `gapminder/*.csv` | Huella material (UNEP-IRP) total y per cápita; Sustainable Development Index (Hickel 2020) | `open-numbers/ddf--gapminder--fasttrack` | 1970–2024; 1990–2019 |
| `ndgain_*.csv` | ND-GAIN: índice, vulnerabilidad, preparación, vulnerabilidad alimentaria e hídrica | espejo OECD States of Fragility 2022 | 1995–2019 |
| `lpi_owid.csv` | Living Planet Index (WWF/ZSL 2022) mundial y regional con IC 95 % | espejo OWID | 1970–2018 |

**No conseguido** (bloqueado o inexistente en GitHub sin LFS): CRU TS por país (`crucy`), Berkeley Earth
por país (sólo punteros LFS; además termina en 2013), ERA5 anual por país ponderado por población, SPEI
(sequía), datos de Dorninger et al. 2021 / Hickel et al. 2022 (MRIO EXIOBASE/Eora), UNEP-IRP DMC,
datos de ciclones de Hsiang & Jina, datos de Kalkuhl & Wenz (Zenodo). Ver §9 (lagunas).

### 1.2 Panel país-año `clima.csv` (17 364 filas × 107 columnas; 1950–2019)

Claves `iso3`, `year`. El panel incluye cualquier ISO3 presente en alguna fuente (251 códigos); el
modelo debe fusionar por `iso3,year` con `panel.csv` (≈180 países). Resumen de variables (el
diccionario completo con unidades, fuente, cobertura, nº de observaciones y países está en
`clima_dict.json`):

**Temperatura y precipitación**

| Variable | Descripción | Cobertura (obs / países) |
|---|---|---|
| `tmp_pw_udel`, `pre_pw_udel` | T (°C) y P (mm/año) ponderadas por población, UDel v3.01 (BHM 2015) | 1960–2010 (7 351 / 167) |
| `tmp_anom_fao`, `tmp_anom_fao_sd` | Anomalía terrestre vs 1951–1980 (área, GISTEMP) y su DE climatológica | 1961–2019 (12 495 / 239) |
| `tmp_era5_decadal` | Media decadal ERA5 (área) | 1950–2019 (193) |
| **`tmp_level`** | Temperatura anual en nivel, empalmada (ver abajo) | 1950–2019 (12 125 / 193) |
| `tmp_level_src` | 1 = UDel; 2 = climatología UDel 1981–2010 + anomalía FAO; 3 = UDel 1961–70 + diferencia ERA5 1950s–1960s (constante 1950–60); 4 = ERA5 área + anomalía FAO (países sin UDel) | — |
| `tmp_level_sq`, `tmp_anom_level` | cuadrado; desviación respecto a la media propia 1951–1980 | — |
| `tmp_pattern_beta` | Coeficiente de escalamiento de patrón (OLS país: anomalía local sobre GISTEMP global, 1961–2019) | 199 países |
| `pre_clim_wdi` | Precipitación media de largo plazo (WDI, constante en el tiempo) | 181 |

*Construcción de `tmp_level`.* El nivel importa porque la función de daño BHM es no lineal en el nivel de
temperatura. Se usa UDel ponderada por población (la medida de BHM) donde existe; para 2011–2019 se añade a
la climatología UDel 1981–2010 del país la anomalía FAO desviada de su media 1981–2010. Validación: en
2001–2010 (fuera de la ventana de ajuste 1981–2000) la anomalía sintética correlaciona 0,77 con la UDel,
con sesgo medio de +0,04 °C y RMSE de 0,33 °C. En un panel balanceado de 180 países no hay salto en
2010→2011 (media 19,01 → 18,78 °C, igual que la anomalía FAO 1,08 → 0,80, año La Niña). Faltan después de
2010: BDI, CRI, RWA, SDN, YEM (sin anomalía FAO), así como 1950–1960 con variación interanual real (src 3
y 4 son constantes decadales). **Advertencia:** src 4 es ponderada por área, no por población.

**Emisiones y energía** (OWID, MtCO₂ salvo indicación): `co2_mt`, `co2_pc`, `co2_per_gdp`,
`co2_incl_luc_mt`, `co2_luc_mt`, `co2_{coal,oil,gas,cement,flaring}_mt`, `co2_cons_mt`, `co2_cons_pc`,
`co2_trade_mt` (importaciones netas incorporadas = consumo − territorial; desde 1990), `co2_trade_share`,
`co2_cum_mt`, `co2_cum_incl_luc_mt`, `co2_cum_luc_mt`, `co2_share_world`, `co2_cum_share_world`,
`ch4_mtco2e`, `n2o_mtco2e`, `ghg_mtco2e`, `ghg_excl_lucf_mtco2e`, `ghg_pc`, `dT_from_ghg`, `dT_from_co2`,
`dT_share_world` (calentamiento global atribuible a cada país, Jones et al. 2023), `primary_energy_twh`,
`coal_prod_twh`, `oil_prod_twh`, `gas_prod_twh`, `fossil_prod_twh` (útil para enlazar **extracción** con
emisiones: responsabilidad del lado de la oferta), `fossil_cons_twh`, `fossil_share_energy`.

**Desastres (EM-DAT, por año de inicio)**: `dis_n_total`, `dis_n_climate` (subgrupos hidrológico +
meteorológico + climatológico), `dis_n_flood`, `dis_n_storm`, `dis_n_drought`, `dis_n_extreme_temp`,
`dis_n_wildfire`, `dis_n_geo` (sismos/volcanes: *placebo* no climático), `dis_deaths`,
`dis_deaths_climate`, `dis_affected`, `dis_damage_kusd`, `dis_damage_climate_kusd` (miles de USD
ajustados por IPC). Ausencia de registro = 0. **Fuerte subregistro antes de ~1990** (los eventos
climáticos mundiales pasan de 230 en los 1950 a 3 431 en los 2000; gran parte es mejora de reporte) → usar
efectos fijos de año o limitar a ≥1990 para calibración.

**Huella ecológica y biocapacidad (GFN)**: `ef_cons_pc_2018ed`, `ef_prod_pc`, `biocap_pc_2018ed`,
`ef_imports_pc`, `ef_exports_pc`, `ef_cons_gha`, `biocap_gha`, `ef_imports_gha`, `ef_exports_gha`,
`ef_carbon_pc`, `ef_net_imports_gha`, `ef_net_imports_pc` (1961–2014); `ef_cons_pc_2025ed`,
`biocap_pc_2025ed` (1961–2019 en el panel); combinadas `ef_cons_pc`, `biocap_pc`, `eco_deficit_pc`.

**Tierra, agua, bosques, recursos (WDI)**: `forest_pct`, `forest_km2`, `forest_loss_pct` (1990–),
`agri_land_pct`, `arable_land_pct`, `cereal_yield`, `fertilizer_kg_ha`, `water_stress_pct`,
`fw_withdrawal_pct`, `pop_below5m_pct`, `drought_flood_pop_pct` (sólo media 1990–2009),
`forest_rents_pct`, `depl_{forest,natres,energy,mineral}_pct_gni`, `dmg_co2_pct_gni`, `dmg_pm_pct_gni`,
`protected_land_pct`, `pm25`, `fish_capture_t`, `threatened_mammals` (2018).

**Materiales y sostenibilidad**: `material_footprint_t`, `material_footprint_pc` (1970–2019, 158
países), `sdi` (1990–2019).

**Vulnerabilidad**: `ndgain_index`, `ndgain_vulnerability`, `ndgain_readiness`, `ndgain_food`,
`ndgain_water` (1995–2019).

### 1.3 Series mundiales `clima_world.csv` (1850–2025)

`gmst_gistemp`, `gmst_hadcrut5`, `gmst_preind` (HadCRUT5 rebasada a 1850–1900), `co2_ppm` (Mauna Loa desde
1959; núcleos de hielo interpolados antes), `co2_ppm_mlo`, `co2_ppm_icecore`, todas las variables OWID de
emisiones a nivel Mundo (incl. `co2_gtc`, `co2_cum_incl_luc_gtco2`, `dT_from_ghg`), producción fósil
mundial, conteos/daños EM-DAT mundiales (`world_dis_*`), huella/biocapacidad mundial NFA 2025 y
`overshoot_ratio`, `lpi` (+IC), `material_footprint_t_sum`.

Valores de referencia:

| Año | GISTEMP | T preind. | CO₂ ppm | CO₂ fósil (Gt) | CO₂ uso suelo (Gt) | Acumulado incl. LUC (Gt) | ΔT por GEI (Jones) | Huella/biocap. | LPI |
|---|---|---|---|---|---|---|---|---|---|
| 1950 | −0,18 | 0,12 | 312,8 | 5,9 | 6,7 | 662 | 0,41 | — | — |
| 1980 | 0,25 | 0,55 | 338,8 | 19,4 | 6,0 | 1241 | 0,82 | 1,12 | 81,5 |
| 2000 | 0,39 | 0,68 | 369,7 | 25,5 | 6,1 | 1810 | 1,15 | 1,41 | 47,2 |
| 2019 | 0,98 | 1,24 | 411,7 | 37,1 | 4,9 | 2542 | 1,56 | 1,74 | (30,9 en 2018) |

Hechos derivados de nuestros datos (útiles como objetivos):

* **Intensidad de CO₂ de la producción fósil**: 0,296 tCO₂/MWh (1950) → 0,259 (1965) → 0,251 (2019):
  descarbonización del *mix* fósil ≈ −0,24 %/año.
* **Fracción aerotransportada** $\Delta M/E$ (con 2,124 GtC/ppm): media 0,42 (1960–2019), por década
  0,37; 0,40; 0,48; 0,40; 0,42; 0,45.
* **TCRE efectiva** (incluye forzamiento no-CO₂ neto): 1,07 °C / 2334 GtCO₂ = **0,46 °C por 1000 GtCO₂**
  (2014, media de 11 años) — coincide con el valor central AR6 (0,45).
* **Escalamiento de patrón**: β medio 1,37 (DE 0,45), mediana 1,33; por tercil de temperatura: fríos 1,58,
  templados 1,27, cálidos 1,36. La tierra se calienta ~1,3–1,6 veces más que la media global (océano
  incluido), como en la literatura (Sutton et al. 2007; Lynch et al. 2017).
* **Ruido interanual local**: DE climatológica mediana 0,31 °C; residuos (sin tendencia de 11 años) con
  DE mediana 0,30 °C y autocorrelación ≈ 0 → ruido blanco.
* **Responsabilidad histórica**: en 2019, el quintil más rico por PIB per cápita (14 % de la población)
  suma 54 % del CO₂ fósil acumulado; la periferia (86 %) 43 %.
* **Emisiones incorporadas en comercio**: el quintil rico importa en neto 1,07 GtCO₂ (1995), 1,87
  (2005), 1,62 (2019); consumo per cápita mediano 12–13,5 tCO₂ frente a 1,5–2,5 en la periferia.
* **Uso del suelo**: 53 % de las emisiones de CO₂ mundiales en 1950, 12 % en 2019; en 2019, el 95 %
  (5,2 de 5,5 Gt) proviene de la periferia; pérdida forestal mediana +0,05 %/año en periferia frente a
  −0,05 %/año (reforestación) en el núcleo (1991–2019).
* **Huella**: huella de consumo mediana 5,8 gha/persona en el núcleo vs 2,1 en la periferia (2019) con
  biocapacidad casi igual (1,44 vs 1,37); huella material 29,8 vs 7,7 t/persona.
* **Desastres (1990–2019)**: probabilidad de un año con daños climáticos registrados 0,24 (periferia) y
  0,34 (núcleo); daño condicional medio ≈ 1,8 % del PIB (mediana 0,07 %; cola pesada, ln-daño con DE ≈
  2,3–2,7); daño medio incondicional 0,43 % (periferia) y 0,58 % (núcleo) del PIB; mortalidad climática
  0,51 frente a 0,29 por 100 000 hab./año.

---

## 2. Clima → economía

### 2.1 Efectos de la temperatura sobre el producto

**Dell, Jones & Olken (2012, AEJ: Macro).** Panel de países 1950–2003 con efectos fijos: en países pobres,
+1 °C en un año reduce el crecimiento del PIB en ≈ 1,4 pp (efectos sobre agricultura, industria y
estabilidad política); en ricos no hay efecto significativo. Los efectos rezagados no revierten
completamente, lo que sugiere efectos sobre la **tasa de crecimiento** y no sólo el nivel. Introdujo el
método "weather-as-shock" (variación interanual dentro de país).

**Burke, Hsiang & Miguel (2015, Nature; "BHM").** Especificación:

$$ g_{it} = \beta_1 T_{it} + \beta_2 T_{it}^2 + \lambda_1 P_{it} + \lambda_2 P_{it}^2 + \mu_i + \nu_t + \theta_{i1} t + \theta_{i2} t^2 + \varepsilon_{it}, $$

con $g$ = crecimiento del PIB per cápita (WDI), $T$ y $P$ ponderadas por población (UDel), efectos fijos de
país y año y tendencias cuadráticas por país; 166 países, 1960–2010. **Hemos replicado exactamente** el
resultado con sus datos (`clima_dict.json → _estimates`):

| Muestra | β₁ (EE) | β₂ (EE) | T óptima | N |
|---|---|---|---|---|
| BHM original, UDel, 1961–2010 | **0,01272** (0,00379) | **−0,000487** (0,000118) | **13,06 °C** | 6 584 |
| Nuestro panel PWT 10.01, `tmp_level`, 1951–2019 | 0,00648 (0,00315) | −0,000259 (0,000109) | 12,51 °C | 8 837 |

La pendiente marginal $\partial g/\partial T = \beta_1+2\beta_2T$ es +0,78 pp/°C a 5 °C, 0 a 13 °C,
−0,68 pp a 20 °C, −1,17 pp a 25 °C y −1,46 pp a 28 °C. BHM no encuentra diferencias significativas entre
países ricos y pobres una vez que se controla por temperatura (la aparente heterogeneidad se debe a que los
pobres son cálidos) y la relación es estable en 1960–1989 vs 1990–2010 (poca adaptación). Proyección
RCP8.5 sin mitigación: −23 % del PIB mundial per cápita en 2100 respecto a sin cambio climático, con
ganancias en países fríos y pérdidas de hasta −75 % para el 40 % más pobre. En nuestro panel PWT el efecto
es ≈ la mitad (atenuación por PWT vs WDI, más años, precipitación imputada después de 2010 y temperatura
no ponderada en src 4); la curvatura y el óptimo se mantienen.

**Kalkuhl & Wenz (2020, JEEM).** Nuevo panel de >1 500 regiones subnacionales en 77 países. Evidencia robusta
de que la temperatura afecta **niveles** de productividad considerablemente sin impactos permanentes
sobre la tasa de crecimiento; +3,5 °C de calentamiento global hacia 2100 reduciría el producto mundial en
7–14 % (más en regiones tropicales y pobres). La variabilidad interanual de la temperatura también daña.

**Kotz, Levermann & Wenz (2024, Nature, "The economic commitment of climate change") — RETRACTADO.** Con
datos subnacionales (~1 600 regiones) y efectos distribuidos de 10 rezagos de temperatura media,
variabilidad diaria y precipitación, estimaba un "compromiso" de pérdida de ingreso del 19 % (11–29 %) para
2049 con independencia de la trayectoria de emisiones. Tuvo una *Author Correction* (julio 2024) y fue
**retractado el 3 de diciembre de 2025** (Nature, Retraction Note s41586-025-09726-0) tras comentarios de
*Matters Arising* (agosto 2025; p. ej. "Data anomalies and the economic commitment of climate change"): los
resultados eran sensibles a quitar un país (Uzbekistán, datos erróneos 1995–1999) y al tratamiento de la
autocorrelación espacial; con las correcciones el rango pasaba a 6–31 % y la probabilidad de divergencia
entre escenarios en 2050 de 99 % a 90 %. Existe una versión actualizada sin revisión por pares. **No usar
sus números como calibración**; mencionarlo como cota superior no validada.

**Newell, Prest & Sexton (2021, JEEM).** Validación cruzada de 800 especificaciones: muchas son
estadísticamente indistinguibles fuera de muestra, incluidas algunas sin efecto de temperatura. Los
modelos de **nivel** producen pérdidas en 2100 centradas en 1–3 % del PIB; los de **crecimiento**
acumulativo tienen un IC 95 % de −84 % a +359 %. Encuentran efectos significativos en PIB de países pobres y
en producción agrícola, pero no en PIB rico, no agrícola, ni en la tasa de crecimiento.

**Otros resultados relevantes para el rango de parámetros.**
* *Nath, Ramey & Klenow (2024, NBER w32761)*: los choques de temperatura tienen efectos **persistentes pero
  no permanentes** sobre el nivel (≈ entre el modelo de nivel y el de crecimiento), con daños globales en
  2100 de varios puntos de PIB, mayores en países cálidos.
* *Kahn et al. (2021, Energy Economics)*: desviaciones persistentes respecto de las normas climáticas
  históricas; +0,04 °C/año sin adaptación → −7,2 % del PIB per cápita mundial en 2100.
* *Bilal & Känzig (2024, NBER w32450)*: usando la temperatura **global** (correlacionada con extremos) en
  lugar de la local, +1 °C global reduce el PIB mundial ≈ 12 % (pico a los ~6 años) — seis veces más que las
  estimaciones locales; implica un coste social del carbono de ≈ 1 367 USD/tCO₂. Útil como **cota
  superior**.
* *DICE-2023 (Barrage & Nordhaus 2024, PNAS)*: daño agregado $\Omega = 0{,}003467\,T^2$ del producto
  (3,1 % a 3 °C, 5,5 % a 4 °C); representa la **cota inferior/convencional**.
* *Burke, Davis & Diffenbaugh (2018, Nature)*; *Diffenbaugh & Burke (2019, PNAS)*: el calentamiento
  1961–2010 ya habría aumentado la desigualdad entre países ~25 % (pobres más cálidos perdieron, ricos fríos
  ganaron) — mecanismo directamente relevante para centro/periferia.

**Nivel vs. crecimiento.** Formalmente, con $\ln Y_{it}=\ln A_{it}+\ldots$ y un daño $D_{it}$,
* efecto nivel: $D_{it}=h(T_{it})-h(\bar T_i)$ (el daño desaparece si el clima vuelve a la norma);
* efecto crecimiento: $D_{it}=D_{i,t-1}+h(T_{it})-h(\bar T_i)$ (se acumula);
* intermedio: $D_{it}=\rho_D D_{i,t-1}+h(T_{it})-h(\bar T_i)$, con $0<\rho_D<1$ (vida media
  $\ln 0{,}5/\ln\rho_D$).

La literatura reciente (Kalkuhl & Wenz; Newell et al.; Nath et al.) apunta a efectos persistentes pero no
permanentes: recomendamos **ρ_D = 0,8** (vida media ≈ 3 años; el impacto acumulado de un choque
permanente es $h/(1-\rho_D)=5h$, i. e. un efecto nivel de largo plazo 5 veces el anual), con sensibilidad
ρ_D ∈ {0; 0,5; 0,9; 1}. Nota: la regresión BHM en crecimientos es consistente con ρ_D = 1 sólo si los
rezagos no revierten; BHM reportan que los rezagos a 5 años no revierten significativamente, pero con gran
incertidumbre.

**Adaptación.** BHM no encuentran aplanamiento temporal ni por riqueza; Dell et al. (2012) tampoco;
Kalkuhl & Wenz encuentran algo de adaptación en regiones ricas; la literatura agrícola (Burke & Emerick
2016, AEJ: Policy) muestra que la adaptación de largo plazo en EE. UU. compensa < 50 % de los impactos de
corto plazo. En el modelo, la adaptación puede ser una opción presupuestaria: parte de `r` (tecnología) o
de `w` reduce $|\beta_2|$ del país, p. ej. $\beta_{2,i}^{ef}=\beta_2(1-a_i)$, $a_i\le 0{,}5$.

### 2.2 Agricultura y rendimientos

Schlenker & Roberts (2009, PNAS): rendimientos de maíz, soja y algodón en EE. UU. crecen hasta 29–32 °C y
caen bruscamente por encima (grados-día extremos). Lobell, Schlenker & Costa-Roberts (2011, Science):
el calentamiento 1980–2008 redujo la producción mundial de maíz ≈ 3,8 % y de trigo ≈ 5,5 % respecto a un
contrafactual sin tendencia climática. Ortiz-Bobea et al. (2021, Nature Climate Change): el cambio
climático antropogénico redujo la productividad total de los factores agrícola mundial en ≈ 21 % desde
1961 (26–34 % en África y América Latina). Zhao et al. (2017, PNAS): cada +1 °C global reduce rendimientos
medios de maíz 7,4 %, trigo 6,0 %, arroz 3,2 %, soja 3,1 %. Para el modelo: el canal agrícola está
implícito en BHM, pero es la vía principal de daño en la periferia (mayor peso agrícola). Variable de
validación: `cereal_yield`.

### 2.3 Desastres y capital

**Hsiang & Jina (2014, NBER w20352)**: reconstrucción de la exposición de cada país a 6 700 ciclones
(1950–2008). El ingreso nacional cae respecto a su tendencia previa y **no se recupera en 20 años**; un
evento del percentil 90 reduce el ingreso per cápita 7,4 % dos décadas después; ricos y pobres responden
de forma similar, con pérdidas mayores donde hay menos experiencia histórica de ciclones. Otros: Noy (2009)
(los desastres reducen el crecimiento de corto plazo en países en desarrollo); Cavallo et al. (2013) (sólo
los desastres muy grandes con revolución política posterior tienen efectos de largo plazo); Felbermayr &
Gröschl (2014) (desastres del percentil superior reducen el PIB per cápita ≈ 0,5 pp de crecimiento);
Coronese et al. (2019, PNAS) (tendencia creciente de los daños extremos, sobre todo en la cola alta);
Botzen, Deschênes & Sanders (2019, REEP) (revisión). IPCC AR6 WG1 cap. 11: la precipitación extrema diaria
se intensifica ≈ 7 % por °C (Clausius-Clapeyron); aumenta la fracción de ciclones de categoría 4–5 y la
frecuencia de olas de calor y sequías agrícolas.

### 2.4 Clima → conflicto

* **Hsiang, Burke & Miguel (2013, Science)**; actualización **Burke, Hsiang & Miguel (2015, Annual Review
  of Economics)**: meta-análisis de 55 estudios; cada +1 DE de temperatura aumenta la violencia
  interpersonal ≈ 2,4 % y el **conflicto intergrupal ≈ 11,3 %** (en la versión de 2013: 4 % y 14 %).
* **Mach et al. (2019, Nature)**: elicitación de 11 expertos (incluido Buhaug, crítico): 3–20 % del
  riesgo de conflicto armado del último siglo habría sido influido por el clima; el clima es menos
  influyente que el bajo desarrollo socioeconómico y la baja capacidad estatal; con +2 °C la probabilidad
  de un aumento sustancial del riesgo es ≈ 13 % y con +4 °C ≈ 26 %.
* **Críticas**: Buhaug (2010, PNAS) y Buhaug et al. (2014, Climatic Change) — resultados frágiles a la
  definición de conflicto, sesgo de selección de casos y de publicación; Theisen, Gleditsch & Buhaug (2013)
  — sin efecto robusto de sequías en África; von Uexkull et al. (2016, PNAS) — la sequía prolonga conflictos
  en grupos dependientes de la agricultura y políticamente excluidos (efecto condicional).
* **Nuestra verificación** en el panel (UCDP, 1950–2019; LPM con efectos fijos país y año, EE por país):
  incidencia de conflicto +0,012 por °C (EE 0,009; +1 DE = 0,58 °C → +5,5 % sobre la media, no
  significativo); inicio −0,003 (EE 0,0045); inicio sobre log(1+desastres climáticos) −0,009 (EE 0,007).
  Es decir, a escala país-año el efecto directo es **pequeño e impreciso**, en línea con Buhaug y Mach et
  al.; el canal principal en el modelo debería ser **indirecto** (clima → ingreso/recursos → PSI y
  legitimidad).

### 2.5 Clima → migración

Cattaneo & Peri (2016, JDE): más temperatura aumenta la emigración (y la urbanización) en países de
ingreso medio y la **reduce** en los pobres (restricción de liquidez: "población atrapada"). Missirian &
Schlenker (2017, Science): las solicitudes de asilo en la UE aumentan de forma no lineal con desviaciones
de 20 °C en zonas agrícolas de origen: +28 % (RCP4.5) a +188 % (RCP8.5) hacia 2100. Beine & Parsons (2015):
efectos principalmente indirectos vía ingreso. Para el modelo: canal opcional, emigración neta periferia →
centro $\propto$ brecha de ingreso × función de daño climático, con reducción en países pobres.

---

## 3. Física del clima

### 3.1 TCRE y presupuestos de carbono

IPCC AR6 WG1 (SPM D.1.1): cada 1000 GtCO₂ acumuladas causan **0,45 °C** de calentamiento (rango
*probable* 0,27–0,63 °C; 1,65 °C por 1000 PgC). Entre 1850–1900 y 2010–2019 se emitieron ≈ 2390 GtCO₂ y el
calentamiento observado fue 1,07 °C (0,8–1,3), incluyendo el efecto neto de otros forzantes. Nuestros datos
dan 0,46 °C/1000 GtCO₂ efectivos (§1.3). La TCRE es casi constante hasta ~2000–3000 GtC porque la
saturación logarítmica del forzamiento se compensa con la menor eficacia de los sumideros. Para un bucle
anual la relación $T_t\approx T_0+\lambda C_t$ basta hasta ~2,5 °C, pero no reproduce la inercia ni el
enfriamiento tras cero emisiones (en realidad casi nulo: "ZEC" ≈ 0 ± 0,3 °C).

### 3.2 Forzamiento y otros gases

$F_{CO_2}=F_{2\times}\log_2(M/M_{pre})$, con $F_{2\times}$ = 3,93 W/m² (AR6: 3,93 ± 0,47). AR6 (2019): ERF
total 2,72 W/m²; CO₂ 2,16; CH₄ 0,54; N₂O 0,21; halocarbonos 0,41; aerosoles −1,1. El forzamiento no-CO₂ neto
es ≈ +0,56 W/m², i. e. ≈ 25 % del CO₂. Parsimonioso: $F^{otros}_t=0{,}25\,F_{CO_2,t}$ (o usar la serie
exógena `F_Misc` de DICE-2023).

### 3.3 Modelos simples de ciclo de carbono y temperatura (anuales)

**DICE-2023 / FaIR simplificado (Barrage & Nordhaus 2024)** — parámetros exactos del código GAMS
(`FAIR-beta-3-17.gms`):

Ciclo de carbono (4 reservorios, $E_t$ en GtCO₂, $\Delta t$ = 1 año):

$$ R_{j,t+1} = R_{j,t}\,e^{-\Delta t/(\tau_j\alpha_t)} + a_j\,\tau_j\alpha_t\,\frac{E_t}{3{,}667}\bigl(1-e^{-\Delta t/(\tau_j\alpha_t)}\bigr),\qquad M_t = M_{eq}+\sum_j R_{j,t}$$

| j | $a_j$ | $\tau_j$ (años) |
|---|---|---|
| 0 | 0,2173 | 1 000 000 |
| 1 | 0,2240 | 394,4 |
| 2 | 0,2824 | 36,53 |
| 3 | 0,2763 | 4,304 |

$M_{eq}$ = 588 GtC (≈ 277 ppm). El factor $\alpha_t$ resuelve cada año
$\sum_j \alpha a_j\tau_j(1-e^{-100/(\alpha\tau_j)}) = \text{iIRF}_{100} = 32{,}4 + 0{,}019\,C^{acc}_t + 4{,}165\,T_t$,
con $C^{acc}$ = carbono acumulado en sumideros (GtC) = emisiones acumuladas − ($M-M_{eq}$). Es monótona en α:
una bisección de 20 iteraciones basta.

Forzamiento: $F_t = 3{,}93\,\log_2(M_t/588) + F^{otros}_t$.

Temperatura (2 cajas):

$$T^{(1)}_{t+1}=T^{(1)}_t e^{-1/d_1}+q_1F_{t+1}(1-e^{-1/d_1}),\quad T^{(2)}_{t+1}=T^{(2)}_t e^{-1/d_2}+q_2F_{t+1}(1-e^{-1/d_2}),\quad T_t=T^{(1)}_t+T^{(2)}_t $$

$d_1$ = 236 años (océano profundo), $d_2$ = 4,07 años (capa superior), $q_1$ = 0,324, $q_2$ = 0,44 K·m²/W →
**ECS = 3,93 × 0,764 = 3,0 °C** (AR6: 3 °C, probable 2,5–4). Condiciones iniciales DICE en 2020: $M$ =
886,5 GtC; $R$ = (150,1; 102,7; 39,5; 6,19) GtC; $T^{(1)}$ = 0,148; $T^{(2)}$ = 1,099; $T$ = 1,247 °C.

**Inicialización para 1950**: arrancar en 1850 con $R_j=0$, $T=0$ y las emisiones mundiales observadas
`co2_incl_luc_mt` de OWID (World) para 1850–1949 (spin-up); comprobar que en 1950 se obtiene $M\approx$
664 GtC (312,8 ppm × 2,124) y $T\approx 0{,}27$ °C (media 11 años de `gmst_preind`). Alternativamente
fijar α constante ≈ 0,3–0,5 y calibrar para reproducir la serie de CO₂ 1950–2019.

**FaIR v2 (Leach et al. 2021, GMD)** tiene la misma estructura (3 cajas térmicas), con parámetros
calibrados a CMIP6 y distribuciones de incertidumbre; Hector (Hartin et al. 2015) es una alternativa. Para
nuestro modelo, DICE-2023 es suficiente y está documentado.

### 3.4 Escalamiento de patrón (global → país)

Supuesto estándar (Santer et al. 1990; Mitchell 2003; Tebaldi & Arblaster 2014): el cambio local es
lineal en el global, $\Delta T_{i,t}=\beta_i\Delta T_t$. Nuestras estimaciones (`tmp_pattern_beta`, 199
países, 1961–2019) tienen media 1,37, mediana 1,33 e IQR 1,14–1,65 (mayor en latitudes altas: amplificación
ártica; mínima en pequeñas islas tropicales). Usar $\beta_i$ estimado por país, reemplazando valores
extremos (< 0,5 o > 3, típicamente islas con pocos datos) por la mediana regional. Para agentes sin dato,
β = 1,33.

---

## 4. Límites ecológicos

* **Límites planetarios**: Rockström et al. (2009, Nature); Steffen et al. (2015, Science); Richardson et
  al. (2023, Science Advances): 6 de 9 límites transgredidos; **Planetary Health Check 2025** (PIK,
  septiembre 2025): 7 de 9 (se añade acidificación oceánica; pH superficial −0,1 desde la era
  preindustrial, +30–40 % de acidez). Sólo la carga de aerosoles y el ozono estratosférico siguen en el
  espacio seguro. Límite climático: 350 ppm CO₂ / +1 W/m² (hoy 420 ppm, +2,7 W/m²).
* **Huella ecológica** (GFN): la humanidad usa ≈ 1,74 planetas (2019; 0,72 en 1961; cruzó 1 hacia 1970).
  Cuestionada (Blomqvist et al. 2013, PLoS Biology) porque el "déficit" es casi todo carbono convertido en
  bosque hipotético, pero útil como índice de presión y de apropiación.
* **Biodiversidad**: Living Planet Index −69 % 1970–2018 (edición 2022; −73 % 1970–2020 en la de 2024;
  América Latina −94 %). Dasgupta Review (2021): entre 1992 y 2014 el capital producido per cápita se
  duplicó, el humano creció ≈ 13 % y el **capital natural per cápita cayó ≈ 40 %** (Managi & Kumar, Inclusive
  Wealth Report 2018).
* **Servicios ecosistémicos → PIB**: Johnson et al. (2021, Banco Mundial, *The Economic Case for Nature*):
  el colapso parcial de polinización, pesca marina y madera de bosques nativos reduciría el PIB mundial en
  2,3 % (2,7 billones USD) en 2030, con −10 % en países de ingreso bajo y medio-bajo.
* **Suelos**: ≈ 1/3 de los suelos moderada o altamente degradados (FAO/ITPS 2015); el coste de la
  degradación de tierras ≈ 0,3–0,4 % del PIB mundial por año (Nkonya et al. 2016, ≈ 300 000 millones USD);
  erosión: pérdidas de rendimiento de 0,3 %/año en promedio mundial (FAO 2015), mucho mayores en suelos
  tropicales degradados.
* **Pesca**: FAO SOFIA 2022: 35,4 % de los stocks sobreexplotados (2019; 10 % en 1974); la captura marina
  está estancada en ~80–90 Mt desde los 1990. Worm et al. (2006, Science): 29 % de las especies pescadas
  colapsadas hacia 2003. Ejemplo de colapso con histéresis: bacalao de Terranova (1992). Variable:
  `fish_capture_t`.
* **Bosques**: FAO FRA 2020: pérdida neta 4,7 Mha/año (2010–2020), deforestación bruta 10 Mha/año
  (2015–2020), 178 Mha perdidas desde 1990, concentradas en trópicos. Variables `forest_km2`,
  `forest_loss_pct`, `co2_luc_mt`.
* **EROI** (retorno energético): petróleo y gas de EE. UU. ≈ 100:1 (1930) → 30:1 (1970) → ~11:1
  (2000s) (Hall, Lambert & Balogh 2014, Energy Policy); mundial ≈ 35:1 (1999) → 18:1 (2006) (Gagnon et al.
  2009); a nivel de energía final ≈ 6:1 y en descenso (Brockway et al. 2019, Nature Energy). Umbral social
  mínimo propuesto 5–15:1. En el modelo: el coste de extracción de $R$ debería aumentar con el
  agotamiento acumulado (ya implícito en Hubbert); se puede añadir $c_x \propto 1/\text{EROI}(Q/URR)$.

---

## 5. Intercambio ecológico desigual y deuda climática

* **Dorninger et al. (2021, Ecological Economics 179:106824)**: MRIO (EXIOBASE/Eora) 1990–2015. Los países de
  ingreso alto son **importadores netos** de materiales, energía, tierra y trabajo incorporados y a la vez
  obtienen **superávit monetario**. El valor agregado por tonelada de materia prima incorporada en
  exportaciones es 11 veces mayor en países ricos que en los más pobres, y 28 veces mayor por unidad de
  trabajo incorporado. Salvo la tierra en China e India, todas las regiones son exportadoras netas de todos
  los recursos hacia los países ricos.
* **Hickel, Dorninger, Wieland & Suwandi (2022, Global Environmental Change)**: en 2015 el Norte se apropió
  en neto del Sur de **12 000 millones de t de materias primas equivalentes, 822 Mha de tierra, 21 EJ de
  energía y 188 millones de años-persona de trabajo**, por un valor de 10,8 billones USD a precios del
  Norte.
* **Hickel, Hanbury Lemos & Barbour (2024, Nature Communications)**: en 2021 el Norte se apropió en neto de
  826 000 millones de horas de trabajo incorporado; salarios del Sur 87–95 % menores por trabajo de igual
  cualificación; el Sur aporta 90 % del trabajo y recibe 21 % del ingreso mundial.
* **Hickel, Sullivan & Zoomkawala (2021, New Political Economy)**: drenaje por intercambio desigual
  1960–2018 ≈ 62 billones USD (de 2011), ≈ 2,2 billones USD/año en los años recientes.
* **Deuda climática / responsabilidad histórica**: Hickel (2020, Lancet Planetary Health): el Norte global
  es responsable del 92 % de las emisiones que exceden el presupuesto "justo" de 350 ppm; Matthews (2016,
  Nature Climate Change): deudas de carbono per cápita; Fanning & Hickel (2023, Nature Sustainability):
  compensación de ≈ 192 billones USD a 2050. Nuestros datos: el quintil rico (14 % de la población) acumula
  el 54 % del CO₂ fósil histórico; la periferia sufre mayores daños por °C (BHM) y más mortalidad por
  desastres.
* **Proxies físicos en nuestro panel**: `co2_trade_mt` (CO₂ incorporado neto, 1990–), `ef_net_imports_gha`
  (hectáreas globales netas importadas, 1961–2014), `material_footprint_pc` vs extracción doméstica (no
  disponible; DMC faltante), `co2_luc_mt` (deforestación en periferia vinculada a exportaciones; Pendrill
  et al. 2019: 29–39 % de las emisiones por deforestación tropical están incorporadas en comercio
  internacional).

---

## 6. Módulo propuesto para el modelo anual

Notación: $i$ país, $t$ año; $R_{i,t}$ extracción del recurso genérico (el modelo ya distingue extracción
propia `x` y extranjera `f`); $Y,K,A$ como en `src/model.py`; centro $c$ / periferia $p$.

### 6.1 Emisiones

$$E^{fos}_{t}=\sum_i \varepsilon_t\,\phi\,R_{i,t},\qquad \varepsilon_t=\varepsilon_{1950}\,(1+g_\varepsilon)^{t-1950}$$

* $\phi$ = fracción fósil del recurso agregado (≈ 0,6–0,75 según la participación de rentas energéticas en
  las rentas totales; calibrar con `recursos`). $\varepsilon_{1950}$ se calibra para que $E^{fos}_{1950}$ =
  5,9 GtCO₂ y $E^{fos}_{2019}$ = 37,1 GtCO₂ dado el $R$ simulado; $g_\varepsilon$ = −0,25 %/año (intensidad
  física del *mix* fósil), rango −0,1 a −1 % (con políticas de descarbonización, ver escenario).
* **Asignación de emisiones**: por extracción (quién extrae — `fossil_prod_twh`), por producción territorial
  (`co2_mt`) o por consumo (`co2_cons_mt`). Para la dinámica física da igual (la suma mundial); para la
  responsabilidad y el intercambio desigual se sugiere registrar las tres.
* **Uso del suelo**: $E^{luc}_{i,t}=e_L\,x^{bosque}_{i,t}$ con $e_L$ calibrado para 6,7 Gt (1950) →
  4,9 Gt (2019), 95 % periférico; o exógeno por región con `co2_luc_mt`.
* $E_t = E^{fos}_t+\sum_i E^{luc}_{i,t}$.

### 6.2 Concentración y temperatura global

*Opción A (mínima)*: $C_t=C_{t-1}+E_t/1000$ (miles de GtCO₂), $T_t = 0{,}27 + 0{,}46\,(C_t-0{,}662)$ °C
(desde 1950). Una sola línea; reproduce la tendencia 1950–2019 pero no la inercia.

*Opción B (recomendada)*: ecuaciones DICE-2023 de §3.3 con $F^{otros}_t=0{,}25\,F_{CO_2,t}$ (o +0,1 a
+0,6 W/m²); coste computacional despreciable (4 + 2 estados + bisección de α). Salidas: `co2_ppm` = $M/2{,}124$
y $T_t$.

Objetivos: `co2_ppm` (1950 312,8; 1980 338,8; 2000 369,7; 2019 411,7) y `gmst_preind` suavizada (0,27 →
1,07 °C). Incertidumbre: ECS 2,5–4 °C (escalar $q_1,q_2$); TCRE 0,27–0,63.

### 6.3 Temperatura local

$$T_{i,t}=\bar T_i+\beta_i\,(T_t-\bar T^{glob})+\sigma_i\,\epsilon_{i,t},\qquad \epsilon_{i,t}\sim N(0,1)\ \text{i.i.d.}$$

$\bar T_i$ = media de `tmp_level` 1951–1980; $\bar T^{glob}$ = media de $T_t$ 1951–1980 (≈ 0,30 °C sobre
preindustrial); $\beta_i$ = `tmp_pattern_beta` (winsorizado); $\sigma_i$ = `tmp_anom_fao_sd` (mediana
0,31 °C). En la fase histórica (1950–2019) se puede alimentar directamente `tmp_level` observado (modo
"clima observado") y usar la ecuación sólo para proyecciones o contrafactuales.

### 6.4 Daño a la productividad (BHM con persistencia)

$$h(T)=\beta_1T+\beta_2T^2,\qquad D_{i,t}=\rho_D D_{i,t-1}+\bigl[h(T_{i,t})-h(\bar T_i)\bigr](1-a_{i,t}),\qquad A^{ef}_{i,t}=A_{i,t}\,e^{D_{i,t}}$$

* $\beta_1$ = 0,0127 (EE 0,0038), $\beta_2$ = −0,000487 (EE 0,000118) (BHM; replicado). Alternativa
  "nuestro panel": 0,0065 / −0,00026. Rango para análisis de sensibilidad: escalar $h$ por $s_h\in[0{,}5;\,1{,}5]$.
* $\rho_D$ = 0,8 (0 = efecto nivel à la Newell/Kalkuhl-Wenz; 1 = BHM crecimiento).
* $a_{i,t}\in[0;0{,}5]$: adaptación financiada con parte del gasto en tecnología o redistribución (p. ej.
  $a=0{,}5\,(1-e^{-k\cdot gasto})$).
* Recorte por seguridad numérica: $D_{i,t}\ge -1{,}5$.
* Como el crecimiento histórico de $A$ ya está calibrado con datos que incluyen el clima observado, activar
  el daño relativo a la climatología 1951–1980 (efecto histórico pequeño: ≈ −0,1 a −0,5 pp acumulado en
  países cálidos) y sobre todo en proyecciones.
* *Cota superior alternativa*: Bilal-Känzig, $\ln Y_{i,t}$ −12 % por °C global en 6 años (aplicar a todos).
  *Cota inferior*: DICE, $Y^{net}=Y/(1+0{,}003467\,T_t^2)$.

**Calibración recomendada**: replicar la regresión BHM sobre el panel simulado y sobre el observado
(`panel.csv` + `tmp_level` + `pre_pw_udel`), comparar $(\hat\beta_1,\hat\beta_2)$ y el óptimo (~12,5–13 °C).
`clima.build()` ya produce ambas estimaciones en `clima_dict.json["_estimates"]`.

### 6.5 Desastres → capital

$$K_{i,t}^{+}=K_{i,t}\,(1-s_{i,t}),\qquad s_{i,t}=B_{i,t}\,\frac{Y_{i,t}}{K_{i,t}}\,\ell_{i,t},\quad B_{i,t}\sim\text{Bernoulli}\!\bigl(p_i\,e^{\kappa\,(T_t-T_{1990})}\bigr),\quad \ln\ell_{i,t}\sim N(\mu_\ell,\sigma_\ell^2)$$

* Calibración EM-DAT 1990–2019 (daño climático / PIB): $p$ = 0,24 (periferia), 0,34 (núcleo) — o
  específico por país; $\mu_\ell$ ≈ −7,5, $\sigma_\ell$ ≈ 2,3–2,7 (media condicional ≈ 1,8 % del PIB,
  mediana 0,07 %). Con K/Y ≈ 3,4 (periferia) – 4,3 (núcleo) la pérdida media de capital es ≈ 0,1–0,15 %/año.
  EM-DAT subregistra daños en la periferia (67 % de sus eventos climáticos 1990–2019 carecen de estimación de daño, frente a 42 % en el núcleo), así que
  $p$ periférico debería subirse ×1,5–2 o usar mortalidad (`dis_deaths_climate`) como proxy.
* **Persistencia (Hsiang & Jina)**: además del golpe a $K$, un evento grande (percentil 90) implica −7,4 %
  de ingreso a 20 años; implementarlo como choque a $D_{i,t}$ con persistencia $\rho_D$ (p. ej. −0,01 a
  −0,02 por evento extremo).
* **Intensificación con el calentamiento**: κ = 0,1 por °C (0–0,3): IPCC AR6 (+7 %/°C en precipitación
  extrema, mayor proporción de ciclones intensos), Coronese et al. 2019. No usar la tendencia bruta de
  conteos EM-DAT (sesgada por reporte).
* Vulnerabilidad: multiplicar $\ell$ por $(\text{vuln}_i/\overline{\text{vuln}})$ con `ndgain_vulnerability`.

### 6.6 Conflicto

En el hazard logístico de conflicto civil (PSI/SDT): $\text{logit}\,h_{i,t}=\ldots+\gamma_c\,z_{i,t}$,
$z_{i,t}=(T_{i,t}-\bar T_i)/\sigma_i$. $\gamma_c$ = 0,05 por DE (rango 0 – 0,107; este último es ln 1,113,
BHM 2015b). Hacerlo condicional a dependencia agrícola/baja capacidad estatal: $\gamma_c\cdot
\mathbb 1[\text{gdppc}<\text{mediana}]$ (von Uexkull et al. 2016; Mach et al. 2019). El canal principal
es indirecto: $D_{i,t}$ reduce el ingreso y los recursos estatales → mayor PSI y menor asabiya. Nuestra
réplica directa en el panel es ≈ 0 (no significativa); usar esto como objetivo de validación (el modelo no
debería generar un efecto directo muy superior al 5–10 % por DE).

### 6.7 Degradación ecológica (capital natural)

Stock de capital natural por país $N_{i,t}\in(0,1]$ (1 = estado de 1950):

$$N_{i,t+1}=N_{i,t}+g_N N_{i,t}(1-N_{i,t})-\eta\,\frac{x^{ren}_{i,t}+\chi\,\text{EF}^{exceso}_{i,t}}{\text{biocap}_{i,1961}}-\zeta\max(0,\,T_{i,t}-\bar T_i)$$

* $g_N$ = 0,02–0,05 (regeneración lenta de suelos y bosques; bosques secundarios 20–50 años).
* $x^{ren}$ = componente renovable (bosque/pesca/suelo) de la extracción; $\text{EF}^{exceso}$ = huella de
  consumo por encima de la biocapacidad (`eco_deficit_pc`). Calibrar η para que el agregado mundial caiga
  ≈ 40 % 1992–2014 per cápita (Dasgupta) o siga el LPI (−69 % 1970–2018; usar como índice ordinal).
* Efectos: (i) TFP: $A^{ef}\leftarrow A^{ef}\,N^{\xi}$ con ξ = 0,05–0,10 (implica −2 a −4 % de producto con
  N = 0,6, coherente con Johnson et al. 2021, −2,3 % mundial y −10 % en ingreso bajo, donde la ponderación
  agrícola es mayor: usar $\xi_i=\xi\cdot(1+\text{peso agrícola})$); (ii) capacidad de extracción Hubbert
  del componente renovable $\propto N_{i,t}$ (colapso de pesquerías/bosques con histéresis si $N<N^*$ ≈ 0,3).
* Objetivos: `forest_loss_pct`, `fish_capture_t`, `cereal_yield`, `eco_deficit_pc`, `overshoot_ratio`
  mundial (0,72 → 1,74).

### 6.8 Intercambio ecológico desigual

Con el comercio centro-periferia existente (importaciones de núcleo `m` y extracción extranjera `f`):

$$U^{mat}_{c\leftarrow p,t}=\omega^{mat}_t\,M_{c\leftarrow p,t},\qquad U^{land}_{c\leftarrow p,t}=\omega^{land}_t\,M_{c\leftarrow p,t},\qquad \Delta N_p \mathrel{-}= \eta\,U^{land}/\text{biocap}_p$$

donde $M_{c\leftarrow p}$ es el valor de las importaciones del centro desde la periferia (o la extracción
extranjera `f`). Calibración a Hickel et al. (2022) para 2015: 12 Gt materiales, 822 Mha, 21 EJ, 188 M
años-persona, 10,8 billones USD a precios del Norte; en nuestros datos, CO₂ neto importado por el núcleo
≈ 1,6–1,9 Gt (≈ 5 % de las emisiones mundiales) y huella neta importada ≈ 300 Mgha (2014). El ingrediente
clave de Dorninger et al.: el valor agregado por unidad física es 11× mayor en el centro → en el modelo, el
precio relativo periferia/centro de la unidad de recurso incorporada ≈ 1/11 (el intercambio desigual
monetario ya modelado debe ser coherente con esa brecha). Registrar además la **deuda climática**
acumulada $\text{DC}_i=\sum_t(E_{i,t}-\bar e_t\,\text{pob}_{i,t})$ (exceso sobre la cuota per cápita mundial),
útil como variable política (reclamaciones de reparación, legitimidad) y de redistribución `w`.

### 6.9 Integración en el bucle anual (orden sugerido)

1. Decisiones de los agentes (presupuestos k, r, m, x, f, w; opcional: adaptación `a` y mitigación).
2. Extracción $R_{i,t}$ → emisiones $E^{fos}$, $E^{luc}$.
3. Ciclo de carbono y temperatura global (opción A/B).
4. Temperatura local por patrón + ruido (o observada en modo histórico).
5. Daño $D_{i,t}$ → $A^{ef}$; desastres → $K$ y $D$; degradación $N$ → $A^{ef}$ y capacidad de $R$.
6. Producción $Y=A^{ef}K^\alpha R^\psi(hL)^{1-\alpha-\psi}$, precio mundial de $R$, comercio e intercambio
   (monetario y ecológico).
7. Demografía/élites/PSI con $\gamma_c z_{i,t}$ y el efecto de ingreso; conflicto.

Parámetros resumidos (valor central; rango):

| Parámetro | Central | Rango | Referencia |
|---|---|---|---|
| $\varepsilon$ tendencia | −0,25 %/año | −0,1 a −1 % | OWID (derivado) |
| TCRE λ | 0,46 °C/1000 GtCO₂ | 0,27–0,63 | IPCC AR6; nuestros datos |
| $F_{2\times}$ | 3,93 W/m² | 3,46–4,40 | AR6 / DICE-2023 |
| ECS | 3,0 °C | 2,5–4,0 | AR6 / DICE-2023 |
| $a_j,\tau_j,d_1,d_2,q_1,q_2$ | ver §3.3 | — | DICE-2023 |
| $F^{otros}/F_{CO_2}$ | 0,25 | 0,1–0,4 | AR6 ERF 2019 |
| $\beta_i$ | mediana 1,33 | 1,14–1,65 (IQR) | nuestros datos |
| $\sigma_i$ | 0,31 °C | 0,15–0,6 | FAOSTAT |
| $\beta_1,\beta_2$ | 0,0127; −0,000487 | ×0,5–1,5 | BHM 2015 |
| $\rho_D$ | 0,8 | 0–1 | Kalkuhl-Wenz; Newell; Nath et al.; BHM |
| adaptación máx. | 0,5 | 0–0,5 | Burke & Emerick 2016 |
| $p$ desastres | 0,24 (p) / 0,34 (c) | ×1–2 (subregistro) | EM-DAT |
| $\mu_\ell,\sigma_\ell$ | −7,5; 2,5 | — | EM-DAT |
| κ | 0,1 /°C | 0–0,3 | AR6 WG1 cap. 11; Coronese 2019 |
| $\gamma_c$ | 0,05 por DE | 0–0,107 | BHM 2015b; Mach 2019; réplica propia |
| $g_N$ | 0,03 | 0,02–0,05 | supuesto (regeneración) |
| ξ | 0,07 | 0,05–0,10 | Johnson et al. 2021; Dasgupta 2021 |
| $\omega$ (intercambio) | calibrar a 12 Gt, 822 Mha (2015) | ±30 % | Hickel et al. 2022 |

---

## 7. Objetivos de calibración y validación

1. **Físicos (mundo)**: `co2_ppm`, `gmst_preind` (suavizada), `co2_mt`, `co2_incl_luc_mt`,
   `co2_cum_incl_luc_gtco2`, fracción aerotransportada ≈ 0,42.
2. **Distribución de emisiones**: `co2_share_world` por grupos centro/periferia; `co2_cum_share_world`;
   `co2_trade_mt` de centro ≈ +1,6 Gt (2019).
3. **Daño**: re-estimar BHM en el panel simulado (β₁ ≈ 0,006–0,013; β₂ ≈ −0,0003 a −0,0005; óptimo
   12–13 °C) y en el observado (hecho: ver `_estimates`).
4. **Desastres**: proporción de años con daño, media condicional y cola (p99 ≈ 3 % del PIB).
5. **Conflicto**: el efecto directo temperatura→conflicto no debe exceder ~10 % por DE.
6. **Ecología**: `overshoot_ratio` (0,72 → 1,74), `forest_loss_pct` periferia ≈ +0,05 %/año vs núcleo
   ≈ −0,05, LPI (índice), `eco_deficit_pc` por grupos.

## 8. Uso del código

```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import clima; clima.build()"
```

`build(force_download=False)` descarga lo que falte (≈ 1 min; 174 archivos GFN pequeños), construye los
tres productos y estima BHM (≈ 30 s). Para leer:

```python
import pandas as pd, json
c = pd.read_csv("data/processed/sources/clima.csv")
w = pd.read_csv("data/processed/sources/clima_world.csv")
meta = json.load(open("data/processed/sources/clima_dict.json"))
```

## 9. Lagunas y advertencias

* Temperatura: sin serie anual ponderada por población después de 2010 (empalme con anomalía de área);
  1950–1960 sólo decadal (sin variación interanual); 5 países sin datos tras 2010. Mejor opción futura:
  ERA5 país-año ponderado por población (p. ej. ClimateRepo/CoMoS) o CRU CY si se habilita la red.
* Precipitación anual sólo 1960–2010 (UDel); después, sólo climatología (`pre_clim_wdi`). No hay SPEI ni
  índices de extremos (grados-día > 30 °C) por país.
* EM-DAT: subregistro fuerte antes de 1990 y en la periferia; daños ausentes en la mayoría de eventos
  periféricos; licencia restrictiva (archivo en `large/`, no versionado).
* Huella ecológica: NFA 2018 completa (1961–2014) y NFA 2025 sólo per cápita (consumo y biocapacidad);
  faltan ≈ 30 países pequeños en la edición 2025.
* No hay extracción doméstica de materiales (DMC) ni flujos MRIO de tierra/materiales/trabajo incorporados
  por país: el intercambio ecológico desigual se calibra con magnitudes agregadas de la literatura y proxies
  (CO₂ en comercio, huella neta importada).
* No hay datos de ciclones (Hsiang & Jina) ni de rendimientos por cultivo; `cereal_yield` y
  `drought_flood_pop_pct` son aproximaciones.
* Kotz et al. (2024) está retractado: no usar.

---

## Referencias

* Barrage, L. & Nordhaus, W. (2024). Policies, projections, and the social cost of carbon: Results from the DICE-2023 model. *PNAS* 121(13): e2312030121.
* Beine, M. & Parsons, C. (2015). Climatic factors as determinants of international migration. *Scandinavian Journal of Economics* 117(2): 723–767.
* Bilal, A. & Känzig, D. R. (2024). The macroeconomic impact of climate change: Global vs. local temperature. NBER WP 32450.
* Blomqvist, L. et al. (2013). Does the shoe fit? Real versus imagined ecological footprints. *PLoS Biology* 11(11): e1001700.
* Botzen, W. J. W., Deschênes, O. & Sanders, M. (2019). The economic impacts of natural disasters: A review of models and empirical studies. *Review of Environmental Economics and Policy* 13(2): 167–188.
* Brockway, P. E. et al. (2019). Estimation of global final-stage energy-return-on-investment for fossil fuels with comparison to renewable energy sources. *Nature Energy* 4: 612–621.
* Buhaug, H. (2010). Climate not to blame for African civil wars. *PNAS* 107(38): 16477–16482.
* Buhaug, H. et al. (2014). One effect to rule them all? A comment on climate and conflict. *Climatic Change* 127: 391–397.
* Burke, M. & Emerick, K. (2016). Adaptation to climate change: Evidence from US agriculture. *AEJ: Economic Policy* 8(3): 106–140.
* Burke, M., Hsiang, S. M. & Miguel, E. (2015a). Global non-linear effect of temperature on economic production. *Nature* 527: 235–239.
* Burke, M., Hsiang, S. M. & Miguel, E. (2015b). Climate and conflict. *Annual Review of Economics* 7: 577–617.
* Burke, M., Davis, W. M. & Diffenbaugh, N. S. (2018). Large potential reduction in economic damages under UN mitigation targets. *Nature* 557: 549–553.
* Cattaneo, C. & Peri, G. (2016). The migration response to increasing temperatures. *Journal of Development Economics* 122: 127–146.
* Cavallo, E., Galiani, S., Noy, I. & Pantano, J. (2013). Catastrophic natural disasters and economic growth. *Review of Economics and Statistics* 95(5): 1549–1561.
* Coronese, M. et al. (2019). Evidence for sharp increase in the economic damages of extreme natural disasters. *PNAS* 116(43): 21450–21455.
* Dasgupta, P. (2021). *The Economics of Biodiversity: The Dasgupta Review*. HM Treasury, Londres.
* Dell, M., Jones, B. F. & Olken, B. A. (2012). Temperature shocks and economic growth: Evidence from the last half century. *AEJ: Macroeconomics* 4(3): 66–95.
* Diffenbaugh, N. S. & Burke, M. (2019). Global warming has increased global economic inequality. *PNAS* 116(20): 9808–9813.
* Dorninger, C. et al. (2021). Global patterns of ecologically unequal exchange: Implications for sustainability in the 21st century. *Ecological Economics* 179: 106824.
* EM-DAT, CRED / UCLouvain. The International Disaster Database. www.emdat.be.
* Fanning, A. L. & Hickel, J. (2023). Compensation for atmospheric appropriation. *Nature Sustainability* 6: 1077–1086.
* FAO (2020). *Global Forest Resources Assessment 2020*. FAO (2022). *The State of World Fisheries and Aquaculture 2022*. FAO & ITPS (2015). *Status of the World's Soil Resources*.
* Felbermayr, G. & Gröschl, J. (2014). Naturally negative: The growth effects of natural disasters. *Journal of Development Economics* 111: 92–106.
* Gagnon, N., Hall, C. A. S. & Brinker, L. (2009). A preliminary investigation of energy return on energy investment for global oil and gas production. *Energies* 2(3): 490–503.
* Global Footprint Network. National Footprint and Biocapacity Accounts, ediciones 2018 y 2025.
* Hall, C. A. S., Lambert, J. G. & Balogh, S. B. (2014). EROI of different fuels and the implications for society. *Energy Policy* 64: 141–152.
* Hartin, C. A. et al. (2015). A simple object-oriented and open-source model for scientific and policy analyses of the global climate system – Hector v1.0. *Geoscientific Model Development* 8: 939–955.
* Hickel, J. (2020). Quantifying national responsibility for climate breakdown: an equality-based attribution approach for carbon dioxide emissions in excess of the planetary boundary. *Lancet Planetary Health* 4(9): e399–e404.
* Hickel, J. (2020). The sustainable development index: Measuring the ecological efficiency of human development in the Anthropocene. *Ecological Economics* 167: 106331.
* Hickel, J., Sullivan, D. & Zoomkawala, H. (2021). Plunder in the post-colonial era: Quantifying drain from the global South through unequal exchange, 1960–2018. *New Political Economy* 26(6): 1030–1047.
* Hickel, J., Dorninger, C., Wieland, H. & Suwandi, I. (2022). Imperialist appropriation in the world economy: Drain from the global South through unequal exchange, 1990–2015. *Global Environmental Change* 73: 102467.
* Hickel, J., Hanbury Lemos, M. & Barbour, F. (2024). Unequal exchange of labour in the world economy. *Nature Communications* 15: 6298.
* Hsiang, S. M., Burke, M. & Miguel, E. (2013). Quantifying the influence of climate on human conflict. *Science* 341: 1235367.
* Hsiang, S. M. & Jina, A. S. (2014). The causal effect of environmental catastrophe on long-run economic growth: Evidence from 6,700 cyclones. NBER WP 20352.
* IPCC (2021). *Climate Change 2021: The Physical Science Basis*. Contribución del GT I al AR6 (SPM; cap. 5 ciclo del carbono y TCRE; cap. 7 forzamiento y ECS; cap. 11 extremos).
* Johnson, J. A. et al. (2021). *The Economic Case for Nature*. Banco Mundial.
* Jones, M. W. et al. (2023). National contributions to climate change due to historical emissions of carbon dioxide, methane, and nitrous oxide since 1850. *Scientific Data* 10: 155.
* Kahn, M. E. et al. (2021). Long-term macroeconomic effects of climate change: A cross-country analysis. *Energy Economics* 104: 105624.
* Kalkuhl, M. & Wenz, L. (2020). The impact of climate conditions on economic production. Evidence from a global panel of regions. *JEEM* 103: 102360.
* Kotz, M., Levermann, A. & Wenz, L. (2024). The economic commitment of climate change. *Nature* 628: 551–557. **Retractado** (Retraction Note, *Nature*, 3 dic. 2025, doi:10.1038/s41586-025-09726-0).
* Leach, N. J. et al. (2021). FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration. *Geoscientific Model Development* 14: 3007–3036.
* Lobell, D. B., Schlenker, W. & Costa-Roberts, J. (2011). Climate trends and global crop production since 1980. *Science* 333: 616–620.
* Lynch, C. et al. (2017). An efficient and accurate method for computing the global mean temperature and pattern scaling. *Earth System Dynamics*.
* Mach, K. J. et al. (2019). Climate as a risk factor for armed conflict. *Nature* 571: 193–197.
* Managi, S. & Kumar, P. (eds.) (2018). *Inclusive Wealth Report 2018*. Routledge/UNEP.
* Matthews, H. D. (2016). Quantifying historical carbon and climate debts among nations. *Nature Climate Change* 6: 60–64.
* Missirian, A. & Schlenker, W. (2017). Asylum applications respond to temperature fluctuations. *Science* 358: 1610–1614.
* Nath, I. B., Ramey, V. A. & Klenow, P. J. (2024). How much will global warming cool global growth? NBER WP 32761.
* Newell, R. G., Prest, B. C. & Sexton, S. E. (2021). The GDP-temperature relationship: Implications for climate change damages. *JEEM* 108: 102445.
* Nkonya, E., Mirzabaev, A. & von Braun, J. (eds.) (2016). *Economics of Land Degradation and Improvement – A Global Assessment for Sustainable Development*. Springer.
* Noy, I. (2009). The macroeconomic consequences of disasters. *Journal of Development Economics* 88(2): 221–231.
* Ortiz-Bobea, A. et al. (2021). Anthropogenic climate change has slowed global agricultural productivity growth. *Nature Climate Change* 11: 306–312.
* Pendrill, F. et al. (2019). Agricultural and forestry trade drives large share of tropical deforestation emissions. *Global Environmental Change* 56: 1–10.
* PIK / Planetary Boundaries Science (2025). *Planetary Health Check 2025*. Potsdam.
* Richardson, K. et al. (2023). Earth beyond six of nine planetary boundaries. *Science Advances* 9: eadh2458.
* Rockström, J. et al. (2009). A safe operating space for humanity. *Nature* 461: 472–475.
* Schlenker, W. & Roberts, M. J. (2009). Nonlinear temperature effects indicate severe damages to U.S. crop yields under climate change. *PNAS* 106(37): 15594–15598.
* Steffen, W. et al. (2015). Planetary boundaries: Guiding human development on a changing planet. *Science* 347: 1259855.
* Tebaldi, C. & Arblaster, J. M. (2014). Pattern scaling: Its strengths and limitations, and an update on the latest model simulations. *Climatic Change* 122: 459–471.
* Theisen, O. M., Gleditsch, N. P. & Buhaug, H. (2013). Is climate change a driver of armed conflict? *Climatic Change* 117: 613–625.
* von Uexkull, N. et al. (2016). Civil conflict sensitivity to growing-season drought. *PNAS* 113(44): 12391–12396.
* Worm, B. et al. (2006). Impacts of biodiversity loss on ocean ecosystem services. *Science* 314: 787–790.
* WWF (2022, 2024). *Living Planet Report*. WWF/ZSL.
* Zhao, C. et al. (2017). Temperature increase reduces global yields of major crops in four independent estimates. *PNAS* 114(35): 9326–9331.

Fuentes web consultadas para el estado de Kotz et al.: [Retraction Watch, 3 dic. 2025](https://retractionwatch.com/2025/12/03/authors-retract-nature-paper-projecting-high-costs-of-climate-change/); [Retraction Note, Nature](https://www.nature.com/articles/s41586-025-09726-0); [Author Correction](https://www.nature.com/articles/s41586-024-07732-2). Planetary Health Check 2025: [PIK](https://www.pik-potsdam.de/en/news/latest-news/seven-of-nine-planetary-boundaries-now-breached-2013-ocean-acidification-joins-the-danger-zone).
