# Acciones observadas: proxies empíricos de los seis canales de presupuesto

**Propósito.** Para resolver el problema inverso (clonación de comportamiento → política
empírica `a(s)`, y luego IRL tipo Bajari–Benkard–Levin para estimar la función de recompensa)
necesitamos observar, país-año, *qué hicieron* los gobiernos/economías con su presupuesto
discrecional. Este documento describe los datos reunidos en
`data/processed/sources/acciones.csv` (generado por `src/sources/acciones.py::build()`), su
cobertura, cómo se mapean a los canales `k, r, m, x, f, w` del modelo, sus sesgos conocidos, y
la literatura de economía política útil para especificar la forma funcional de `a(s)`.

Reproducir:

```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import acciones; acciones.build()"
```

Salida: `acciones.csv` (12 285 filas país-año, 226 códigos ISO3, 1950–2019, 50 variables;
todas las proporciones como fracción 0–1) y `acciones_dict.json` (descripción, fuente,
archivos, unidades y cobertura por década de cada variable).

---

## 1. Fuentes y restricciones de acceso

El entorno sólo alcanza `raw.githubusercontent.com` (más PyPI/npm). Por eso:

* **WDI (Banco Mundial).** Se usan los CSV "bulk" por indicador
  (`API_<código>_DS2_en_csv_v2_*.csv`) re-alojados en repositorios públicos. Para cada
  indicador se superponen dos capas: (1) una *vintage reciente* (lanzamientos 2020–2025) y
  (2) como relleno, el paquete completo `ronnywang/worldbank/WDI_bundle/parsed` (vintage ~2014,
  datos 1960–2013). Donde ambas existen manda la reciente (incorpora revisiones). Los
  archivos `WDIData.csv` completos encontrados en GitHub eran punteros git-lfs (inutilizables).
* **OWID (Our World in Data)**, exportaciones "grapher" re-alojadas: SIPRI (gasto militar),
  IMF *Public Finances in Modern History* (Mauro et al. 2015), ICTD/UNU-WIDER GRD (impuestos),
  OECD SOCX + Lindert (gasto social de largo plazo), Tanzi–Schuknecht (educación histórica).
* **SWIID 9.92** (Solt 2020): Gini de mercado y disponible → redistribución.
* **PWT 10.01** (`data/raw/pwt1001.csv`, de `src/fetch_data.py`): `csh_i, csh_g, csh_m, csh_x`
  como respaldo 1950–2019.

Todos los archivos crudos quedan en `data/raw/acciones/` (≈5.8 MB; ninguno >20 MB). El nombre
de cada archivo es `<dueño-del-repo>__<nombre-original>` y `acciones_dict.json` guarda la ruta
exacta de origen.

**No se pudo obtener** (hosts bloqueados o sin copia en GitHub): UNCTAD FDI *stocks*
(salientes), Lane & Milesi-Ferretti *External Wealth of Nations*, IMF GFS por función
(COFOG), inversión upstream en petróleo/minería por país (IEA/Rystad, propietarias), ILO
World Social Protection, V-Dem completo (variables de gasto clientelar vs. bienes públicos),
Juhász–Lane–Oehlsen–Pérez (medición textual de política industrial), OECD MSTI (GERD
histórico 1981–). WDI posterior a 2013 no está disponible para GFCF, manufacturas en
importaciones, exportaciones/PIB y transferencias (sólo la vintage 2014): esos huecos se
rellenan con PWT reescalado o arrastrando proporciones lentas (ver §3).

---

## 2. Variables y cobertura

Columnas: `iso3, year` + variables. Prefijo = canal del modelo. Cobertura = países con al menos
un dato en cada década (1950s/60s/70s/80s/90s/00s/10s). *Dentro del panel del modelo*
(180 países, 10 314 filas) la fracción de celdas no vacías aparece en la última columna.

| Variable | Fuente | Años | Países | Obs | Países por década | % panel |
|---|---|---|---|---|---|---|
| **k** `k_gfcf_wdi` | WDI NE.GDI.FTOT.ZS | 1960–2012 | 188 | 6867 | 0/74/110/150/178/184/167 | 61 |
| `k_gcf_wdi` | WDI NE.GDI.TOTL.ZS | 1960–2012 | 189 | 7317 | 0/94/120/154/179/185/171 | 64 |
| `k_csh_i_pwt` | PWT csh_i | 1950–2019 | 183 | 10399 | 75/114/157/158/181/183/183 | 100 |
| **r** `r_rd_gerd` | WDI GB.XPD.RSDV.GD.ZS (UNESCO UIS) | 1996–2019 | 157 | 2148 | 0/0/0/0/85/138/141 | 20 |
| `r_edu_pub` | WDI SE.XPD.TOTL.GD.ZS | 1970–2019 | 211 | 4720 | 0/0/106/112/169/180/191 | 42 |
| `r_edu_pub_hist` | Tanzi–Schuknecht (OWID) | 1960–1993 | 17 | 50 | — | 0 |
| `r_hitech_share_mexp` | WDI TX.VAL.TECH.MF.ZS (*resultado*, % export. manuf.) | 1988–2019 | 193 | 4243 | 0/0/0/44/158/184/178 | 38 |
| **m** `m_imports_wdi` | WDI NE.IMP.GNFS.ZS | 1960–2019 | 212 | 9449 | 0/110/131/157/193/208/208 | 81 |
| `m_manuf_share_imp` | WDI TM.VAL.MANF.ZS.UN (% import. mercancías) | 1962–2012 | 195 | 6113 | 0/104/143/138/172/184/156 | 54 |
| `m_csh_m_pwt` | PWT −csh_m | 1950–2019 | 183 | 10399 | 75/114/157/158/181/183/183 | 100 |
| `m_manuf_imports` | derivada: import/PIB × %manuf | 1962–2018 | 188 | 7286 | 0/89/120/130/170/181/174 | 65 |
| **x** `x_resource_rents` | WDI NY.GDP.TOTL.RT.ZS | 1960–2019 | 222 | 9195 | 0/2/146/176/206/218/215 | 75 |
| `x_fuel_share_exp` | WDI TX.VAL.FUEL.ZS.UN (% export. mercancías) | 1962–2019 | 203 | 7088 | 0/101/134/129/170/187/187 | 64 |
| `x_ores_share_exp` | WDI TX.VAL.MMTL.ZS.UN | 1962–2019 | 203 | 7330 | 0/104/143/136/174/189/185 | 65 |
| `x_exports_wdi` / `x_csh_x_pwt` | WDI NE.EXP.GNFS.ZS / PWT csh_x | 1960–2012 / 1950–2019 | 194 / 183 | | | 67 / 100 |
| `x_primary_exports` | derivada: export/PIB × (comb.+minerales) | 1962–2019 | 196 | 7137 | 0/95/134/130/169/182/179 | 66 |
| **f** `f_fdi_out` | WDI BM.KLT.DINV.WD.GD.ZS (salidas netas IED) | 1970–2019 | 202 | 6404 | 0/0/111/141/146/178/185 | 58 |
| `f_fdi_in` | WDI BX.KLT.DINV.WD.GD.ZS (entradas netas IED) | 1970–2019 | 208 | 8531 | 0/0/142/162/193/202/207 | 74 |
| **w** `w_gov_cons_wdi` | WDI NE.CON.GOVT.ZS | 1960–2019 | 207 | 9073 | 0/104/125/158/183/202/203 | 79 |
| `w_csh_g_pwt` | PWT csh_g | 1950–2019 | 183 | 10399 | 75/114/157/158/181/183/183 | 100 |
| `w_tax_wdi` | WDI GC.TAX.TOTL.GD.ZS (gob. central) | 1972–2019 | 176 | 4533 | 0/0/48/55/129/153/166 | 42 |
| `w_tax_ictd` | ICTD/UNU-WIDER GRD (OWID) | 1980–2019 | 191 | 5700 | 0/0/0/104/167/183/182 | 51 |
| `w_gov_exp_wdi` | WDI GC.XPN.TOTL.GD.ZS | 1972–2019 | 173 | 4186 | 0/0/42/51/119/152/158 | 39 |
| `w_gov_exp_hist` | IMF/Mauro et al. (OWID) | 1950–2011 | 164 | 5190 | 47/52/52/71/135/164/164 | 48 |
| `w_transfers_share_exp`, `w_transfers` | WDI GC.XPN.TRFT.ZS (% gasto) y ×gasto/PIB | 1990–2012 | 147 | 1841 | 0/0/0/0/92/136/112 | 17 |
| `w_social_exp` | OECD SOCX + Lindert (OWID) | 1960–2019 | 42 | 1660 | 0/16/17/25/36/39/42 | 16 |
| `w_redist_abs` | SWIID abs_red (sólo donde SWIID lo publica) | 1975–2019 | 72 | 2466 | 0/0/18/47/71/72/72 | 24 |
| `w_redist_abs_all`, `gini_mkt`, `gini_disp` | SWIID (todas las imputaciones) | 1960–2019 | 196 | 6131 | 0/35/59/108/150/190/182 | 56 |
| `w_civil_cons` | derivada: cons. gobierno − gasto militar | 1950–2019 | 214 | 11280 | 75/127/165/180/198/211/211 | 100 |
| **poder** `mil_exp_sipri` | SIPRI (OWID) | 1950–2019 | 164 | 7469 | 46/83/108/129/155/160/160 | 70 |
| `mil_exp_wdi` | WDI MS.MIL.XPND.GD.ZS (SIPRI) | 1960–2019 | 170 | 7286 | 0/83/107/133/159/166/166 | 67 |

Compuestos (§3): `acc_k` 100 %, `acc_r` 80 %, `acc_m` 100 %, `acc_x` 76 %, `acc_f` 58 %,
`acc_w` 100 % del panel; las seis a la vez (`a_*`, `budget_total`) 54 % (1970–2019,
183 países). Antes de 1970 no hay IED ni rentas → sólo se pueden clonar 4 canales (k, r, m, w).

---

## 3. Mapeo a los seis canales del modelo

El modelo reparte un presupuesto discrecional `B_t = β·Y_t` en `a_c` (fracciones del PIB).
Ningún dato mide directamente "decisiones"; medimos **flujos de gasto realizados** que son la
contraparte más cercana. El constructor produce dos niveles:

**(i) Acciones en % del PIB (`acc_c`):**

| Canal | Fórmula implementada | Justificación / alternativa |
|---|---|---|
| k | `acc_k = GFCF_WDI`, huecos ← `csh_i_PWT · ρ_i`, ρ_i = mediana país(GFCF/csh_i) | GFCF incluye inversión privada; si se quiere la *decisión pública* usar inversión pública (IMF Investment & Capital Stock Dataset, no accesible). `ρ_i` elimina el salto de nivel PPP vs. precios nacionales. |
| r | `acc_r = GERD (interp., falta→0) + educación pública (interp. ≤10 a, arrastre ±10 a)` | Canal de "tecnología/industria propia": I+D + capital humano. Imputar GERD=0 sesga poco (países sin dato tienen GERD típico 0.1–0.3 % PIB). Alternativa: sólo GERD (1996–) o `r_hitech_share_mexp` como *resultado* para validación. |
| m | `acc_m = import/PIB (WDI, huecos ← csh_m·ρ_i) × %manufacturas en importaciones (arrastrado, si no mediana país)` | Importaciones de bienes de alto valor del centro. Mezcla bienes y servicios (numerador) con mercancías (proporción) → aproximación. Se trunca en 1 (entrepôts: SGP, HKG). Mejor: importaciones de bienes de capital BEC (COMTRADE, no accesible). |
| x | `acc_x = θ · rentas_recursos`, θ = `X_THETA` = 0.3 | Supuesto: fracción de rentas reinvertida en capacidad extractiva (capex upstream global ≈0.4–0.5 billones USD/año frente a rentas WDI ≈1.5–3 billones → 0.2–0.35). **Es un supuesto, no una medición**; θ debe tratarse como parámetro a calibrar o estimar. Complementos: `x_primary_exports`, `x_fuel_share_exp`, producción fósil (fuente `recursos`). |
| f | `acc_f = max(IED neta saliente/PIB, 0)` | Flujo BoP; incluye reinversión de utilidades y *round-tripping* (paraísos fiscales: LUX, NLD, IRL, CYP, MUS…). Recomendado: excluir o recortar centros financieros y winsorizar. |
| w | `acc_w = gasto social (OECD/Lindert)`, si no `subsidios+transferencias gob. central`, si no `consumo gob. − gasto militar` | Jerarquía de mejor a peor proxy de "redistribución a las masas". `w_redist_abs` (SWIID) mide el *resultado* redistributivo (puntos Gini), útil como validación o como target alternativo. |
| (poder) | `mil_exp_sipri` (fallback `mil_exp_wdi`) | Acción adicional; se resta de `w`. |

**(ii) Participaciones de presupuesto (`a_c`)**: `a_c = acc_c / Σ_c acc_c` cuando las seis
existen (`budget_total` = Σ, mediana 0.70 del PIB). Para el modelo, si el presupuesto
discrecional es `β` del PIB, la acción observada es `a_c^{mod} = β · a_c` (o calibrar `β`
país-año como `budget_total` escalado).

Hechos estilizados (2000–2019, terciles de PIB per cápita, medias de `a_c`):

| | bajo | medio | alto |
|---|---|---|---|
| a_k | 0.351 | 0.335 | 0.282 |
| a_r | 0.063 | 0.064 | 0.074 |
| a_m | 0.366 | 0.392 | 0.369 |
| a_x | 0.044 | 0.022 | 0.021 |
| a_f | 0.011 | 0.011 | 0.046 |
| a_w | 0.164 | 0.175 | 0.209 |

Regresiones con efectos fijos país y año (errores agrupados por país; panel del modelo):

| y | log PIBpc | democracia (polyarchy) | rentas/PIB | conflicto |
|---|---|---|---|---|
| acc_k | **+0.037** (0.011) | −0.018 (0.019) | −0.065 (0.081) | −0.002 |
| acc_r | **+0.005** (0.002) | 0.000 | −0.015 (0.012) | −0.003 |
| acc_m | **+0.049** (0.014) | +0.030 (0.025) | −0.054 | −0.009 |
| acc_f | **+0.013** (0.006) | **−0.017** (0.008) | 0.000 | +0.002 |
| acc_w | −0.004 (0.008) | +0.016 (0.019) | **−0.127** (0.042) | −0.002 |
| gasto militar | **−0.011** (0.004) | −0.008 (0.005) | −0.039 | **+0.006** (0.002) |
| impuestos (ICTD) | **+0.016** (0.008) | +0.020 (0.013) | +0.023 | −0.002 |
| redistribución SWIID | — gini_mkt: **+0.18** (0.06) | −0.003 | | |

Persistencia (AR(1) anual *pooled*): ρ(acc_k)=0.90, ρ(acc_r)=0.97, ρ(acc_m)=0.96,
ρ(acc_w)=0.92, ρ(militar)=0.86, ρ(a_k)=0.94, ρ(a_w)=0.91; desviación típica del cambio anual
0.005 (r) a 0.05 (k, m). **Implicación clave: la política observada es fuertemente inercial**;
cualquier `a(s)` debe tener un término de ajuste parcial, y un estimador BBL que ignore la
inercia atribuirá a la recompensa lo que es costo de ajuste.

(`acc_x` es mecánicamente 0.3·rentas; su regresión sobre rentas no es informativa.)

---

## 4. Sesgos y problemas conocidos

1. **Acción vs. resultado.** GFCF, importaciones e IED son decisiones descentralizadas
   (privadas) moldeadas por políticas; no son decisiones del "agente-país". Rentas y
   export-shares son *resultados* del precio mundial (commodities) más que esfuerzo. La
   redistribución SWIID es resultado de reglas fiscales + estructura de mercado.
2. **Selección de datos (MNAR).** GERD, gasto social, transferencias y SWIID *abs_red* existen
   sobre todo para países ricos/democráticos. Pre-1970 sólo ~75–130 países; la URSS y Europa
   del Este casi ausentes antes de 1990 en WDI (PWT los cubre desde ~1990).
3. **Precios.** PWT `csh_*` están a PPP corrientes (bienes de inversión relativamente caros en
   países pobres → `csh_i` bajo; Hsieh–Klenow 2007). WDI a precios nacionales. El
   reescalado `ρ_i` mitiga el salto al empalmar, no el concepto.
4. **Vintages mezcladas.** Capa WDI 2014 (1960–2013) + capas 2020–2025; revisiones de cuentas
   nacionales (p.ej., rebasing de Nigeria 2014, Ghana 2010) crean discontinuidades en
   ratios/PIB. Revisar saltos >50 % entre años contiguos al estimar.
5. **Cobertura de gobierno.** WDI GC.* es gobierno central (subestima federaciones: USA, DEU,
   BRA, IND); ICTD e IMF/Mauro intentan gobierno general. SIPRI incluye paramilitares
   según país.
6. **IED.** Flujos netos pueden ser negativos (desinversión); centros financieros inflan
   salidas (>10 % PIB). `acc_f` recorta en [0,1].
7. **Imputaciones del compuesto.** GERD faltante=0; proporción de manufacturas arrastrada
   hasta 2019 desde 2012; educación arrastrada ±10 años. Hay que usar `n_acc_obs` y las
   variables crudas para análisis de sensibilidad.

---

## 5. Literatura: cómo deciden realmente los gobiernos (para especificar `a(s)`)

### 5.1 Incrementalismo y ajuste parcial (forma base)
* Davis, Dempster & Wildavsky (1966, *APSR*) "A Theory of the Budgetary Process":
  `B_t = α B_{t-1} + ε`, α≈1.0–1.2; el presupuesto es incremental.
* Jones & Baumgartner (2005) *The Politics of Attention*; Jones et al. (2009, *AJPS*)
  "A General Empirical Law of Public Budgets": cambios presupuestarios leptocúrticos
  (curtosis ≫3, colas de Pareto) en todos los países — equilibrio puntuado.
* **Forma propuesta**: ajuste parcial hacia un objetivo latente
  `a_{c,t} = ρ_c a_{c,t-1} + (1−ρ_c) a*_c(s_t) + ε_{c,t}`, con ε de colas pesadas (t de Student
  o mezcla) y ρ_c≈0.86–0.97 (nuestras estimaciones, §3).

### 5.2 Redistribución (canal w)
* Meltzer & Richard (1981, *JPE*): tasa impositiva lineal elegida por el votante mediano,
  `τ* ↑` con `ȳ/y_med` (inequidad de mercado). Empírica: Milanovic (2000, *EJPE*) —
  redistribución crece con la desigualdad de mercado; Kenworthy & Pontusson (2005).
  Nuestro dato: +0.18 puntos de redistribución por punto de Gini de mercado (FE).
* Acemoglu & Robinson (2000 *QJE*; 2006 *Economic Origins*): élites extienden el voto /
  redistribuyen ante amenaza revolucionaria; redistribución como función de la amenaza
  (en el modelo: PSI). Acemoglu, Naidu, Restrepo & Robinson (2015, *Handbook of Income
  Distribution*): la democracia eleva los impuestos/PIB ~16 % a largo plazo, sin efecto
  robusto sobre desigualdad.
* Lindert (2004) *Growing Public*: gasto social despega con el sufragio y el envejecimiento;
  Mulligan, Gil & Sala-i-Martin (2004, *JEP*): democracias y no-democracias gastan
  parecido condicional en demografía.
* Bueno de Mesquita et al. (2003) *The Logic of Political Survival*: la mezcla bienes
  públicos/privados depende de W/S (coalición ganadora/selectorado): con W pequeña →
  transferencias privadas a élites, no `w` a masas. Proxy de W: polyarchy.
* Forma: `a*_w = σ(β0 + β1 gini_mkt + β2 dem + β3 PSI + β4 rentas + β5 edad65)`, esperado
  β1>0, β2>0, β3>0 (cooptación ante estrés), β4<0 (Estado rentista: Ross 2001; nuestro
  −0.13).

### 5.3 Capacidad fiscal y regla fiscal (restricción presupuestaria)
* Besley & Persson (2011) *Pillars of Prosperity*: inversión en capacidad fiscal crece con
  "interés común" (guerras externas) y cohesión; cae con conflicto interno — enlaza con
  asabiya del modelo.
* Bohn (1998, *QJE*): superávit primario reacciona a la deuda con ≈0.054 (EE. UU.).
  Mendoza & Ostry (2008, *JME*): respuesta ≈0.02–0.06 en paneles; se debilita con deuda
  >~50 % PIB (emergentes). Ghosh et al. (2013, *EJ*) "fiscal fatigue": reacción cúbica.
* Prociclicidad: Kaminsky, Reinhart & Végh (2004); Frankel, Végh & Vuletin (2013, *JDE*):
  gasto procíclico en países en desarrollo y exportadores de commodities, contracíclico en
  OCDE → incluir brecha de producto y precio de commodities en `s`.
* Ley de Wagner: gasto público/PIB crece con el ingreso (elasticidad >1 en series largas;
  Peacock–Wiseman "efecto desplazamiento" tras guerras). Nuestro FE: impuestos +1.6 pp por
  log-punto de PIBpc.

### 5.4 Recursos naturales (canales x y f)
* Maldición de los recursos: Sachs & Warner (2001); Gylfason (2001, *EER*): capital natural
  desplaza educación e inversión; van der Ploeg (2011, *JEL*) revisión.
* Offset fiscal: Bornhorst, Gupta & Thornton (2009, *EJPE*): 1 pp de PIB de ingresos de
  hidrocarburos reduce ~0.2 pp los ingresos no petroleros (30 productores). Crivelli & Gupta
  (2014, IMF WP/14/5) resultados similares.
* Tornell & Lane (1999, *AER*) "efecto voracidad": ante shocks de rentas, grupos poderosos
  se apropian más que proporcionalmente → `a_w` y `a_k` pueden caer con rentas.
* Regla de Hartwick / ingreso permanente (Collier, van der Ploeg, Spence & Venables 2010):
  norma prescriptiva — invertir las rentas en capital reproducible; la desviación
  observada de esta norma es una medida de "impaciencia" (descuento) que el IRL puede
  identificar.
* Ross (2012) *The Oil Curse*; Ross & Mahdavi (2015) nacionalizaciones 1932–2014 (Dataverse,
  no accesible) — útil para modelar competencia extracción doméstica vs. extranjera.
* IED saliente y recursos: Dunning (1981) "Investment Development Path": posición neta de
  inversión saliente en forma de U/J con el PIBpc (Durán & Úbeda 2001: cuadrática);
  Kolstad & Wiig (2012, *JWB*): la IED china va a países ricos en recursos con instituciones
  débiles. Nuestro FE: `acc_f` +0.013 por log PIBpc y −0.017 con democracia.

### 5.5 Inversión, tecnología e importaciones de alto valor (k, r, m)
* Estado desarrollista: Johnson (1982), Amsden (1989), Wade (1990), Evans (1995):
  inversión dirigida y protección condicionada a exportar; Lane (2025, *QJE*) — el impulso
  HCI coreano (1973–79) elevó persistentemente la producción en industrias objetivo.
  Juhász, Lane & Rodrik (2024, *Annual Rev. Econ.*) "The New Economics of Industrial Policy".
* Acelerador y determinantes robustos de inversión: Levine & Renelt (1992) — la tasa de
  inversión es el correlato robusto del crecimiento; nuestro FE: +3.7 pp de GFCF por
  log-punto de PIBpc.
* I+D: intensidad crece con el ingreso (nuestro +0.5 pp); elasticidad de la I+D al costo de
  uso ≈ −1 a largo plazo (Bloom, Griffith & Van Reenen 2002, *JPubE*; Bloom, Van Reenen &
  Williams 2019, *JEP*).
* Capital importado: Lee (1995, *JDE*) importaciones de bienes de capital y crecimiento;
  Eaton & Kortum (2001, *EER*) comercio de equipos; Mutreja, Ravikumar & Sposi (2018, *EER*).
  Sustitución de importaciones vs. apertura: `a_m` decrece con estrategias ISI (América
  Latina 1950–80) y crece con liberalización — incluir dummies de régimen comercial
  (Sachs–Warner/Wacziarg–Welch) en `s` si están disponibles (fuente `comercio`).

### 5.6 Gasto militar ("poder")
* Dunne & Perlo-Freeman (2003, *Defence & Peace Econ.*); Nordhaus, Oneal & Russett (2012,
  *Int. Organization*, 165 países 1950–2000): la probabilidad de disputa militar fatal
  (amenaza) es un determinante fuerte del gasto; forma típica
  `log m_t = ρ log m_{t-1} + γ log amenaza + δ guerra + η log m_rivales + θ dem + …`,
  ρ≈0.8–0.9 (nuestro AR(1) 0.86; +0.6 pp en años de conflicto).
* Richardson (1960): carreras armamentistas `ṁ_i = k m_j − α m_i + g`.

### 5.7 Especificación recomendada para clonación de comportamiento
1. **Modelo de proporciones**: logit multinomial fraccional (Papke & Wooldridge 1996;
   Mullahy 2015) o regresión Dirichlet sobre `a_{c,t}` con log-ratios respecto a `k`:
   `log(a_c/a_k)_t = ρ log(a_c/a_k)_{t-1} + (1−ρ) [α_c + β_c' s_t] + u_{c,t}`.
2. **Estado `s_t`** mínimo: log PIBpc, gini_mkt, democracia, PSI/conflicto, rentas/PIB,
   reservas remanentes (Hubbert), posición centro-periferia, amenaza externa, deuda, brecha de
   producto, precio del petróleo. Todas disponibles en otras fuentes del repositorio.
3. **Efectos fijos** país (o tipos latentes con clases finitas, para BBL) — el grueso de la
   varianza de `a_c` es entre países.
4. **Costo de ajuste en la recompensa**: con ρ≈0.9, la recompensa BBL debería incluir
   `−κ Σ_c (a_{c,t} − a_{c,t−1})²`; sin él, el estimador confunde inercia con preferencias.
5. **Validación**: `r_hitech_share_mexp`, `w_redist_abs`, `x_primary_exports` como
   resultados fuera de muestra.

---

## Referencias (selección)
Acemoglu, D. & Robinson, J. (2000) *QJE* 115(4); (2006) *Economic Origins of Dictatorship and
Democracy*. · Acemoglu, Naidu, Restrepo & Robinson (2015) "Democracy, Redistribution and
Inequality", *Handbook of Income Distribution* 2B; (2019) *JPE* 127(1). · Amsden (1989) *Asia's
Next Giant*. · Bajari, Benkard & Levin (2007) *Econometrica* 75(5). · Besley & Persson (2011)
*Pillars of Prosperity*. · Bloom, Griffith & Van Reenen (2002) *J. Public Econ.* 85. · Bloom,
Van Reenen & Williams (2019) *JEP* 33(3). · Bohn (1998) *QJE* 113(3). · Bornhorst, Gupta &
Thornton (2009) *EJPE* 25(4). · Bueno de Mesquita et al. (2003). · Collier, van der Ploeg,
Spence & Venables (2010) *IMF Staff Papers* 57. · Crivelli & Gupta (2014) IMF WP/14/5. ·
Davis, Dempster & Wildavsky (1966) *APSR* 60(3). · Dunning (1981) *Weltwirtschaftliches
Archiv* 117. · Dunne & Perlo-Freeman (2003) *Defence Peace Econ.* 14(6). · Eaton & Kortum (2001)
*EER* 45. · Evans (1995) *Embedded Autonomy*. · Feenstra, Inklaar & Timmer (2015) *AER*
105(10). · Frankel, Végh & Vuletin (2013) *JDE* 100. · Ghosh et al. (2013) *EJ* 123. · Gylfason
(2001) *EER* 45. · Jones et al. (2009) *AJPS* 53(4). · Juhász, Lane & Rodrik (2024) *ARE* 16. ·
Kaminsky, Reinhart & Végh (2004) *NBER Macro Annual*. · Kolstad & Wiig (2012) *J. World
Business* 47. · Lane (2025) *QJE*. · Lee (1995) *JDE* 48. · Levine & Renelt (1992) *AER* 82. ·
Lindert (2004) *Growing Public*. · Mauro et al. (2015) *Economic Policy* 30(82). · Meltzer &
Richard (1981) *JPE* 89(5). · Mendoza & Ostry (2008) *JME* 55(6). · Milanovic (2000) *EJPE*
16. · Mulligan, Gil & Sala-i-Martin (2004) *JEP* 18(1). · Nordhaus, Oneal & Russett (2012) *IO*
66(3). · Papke & Wooldridge (1996) *J. Appl. Econometrics* 11. · Ross (2001) *World Politics*
53; (2012) *The Oil Curse*. · Sachs & Warner (2001) *EER* 45. · Solt (2020) *SSQ* 101(3) (SWIID).
· Tornell & Lane (1999) *AER* 89(1). · van der Ploeg (2011) *JEL* 49(2). · Wade (1990)
*Governing the Market*.
