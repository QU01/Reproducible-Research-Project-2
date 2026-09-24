# Instituciones y geopolítica: datos, literatura y especificación para el modelo

Este documento acompaña a `src/sources/geopolitica.py`, que construye:

| Archivo | Contenido |
|---|---|
| `data/processed/sources/geopolitica.csv` | Panel país-año (ISO3, 1946–2019; 202 países, 13 088 filas, 88 columnas) |
| `data/processed/sources/geopolitica_world.csv` | Series mundiales anuales 1946–2019 (hegemonía, polaridad, olas democráticas, golpes, sanciones) |
| `data/processed/sources/geopolitica_dict.json` | Diccionario de variables, fuentes, cobertura por variable y **momentos de calibración** estimados con estos datos |

Reconstrucción: `.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import geopolitica; geopolitica.build()"` (≈90 s; descarga lo que falte en `data/raw/geopolitica/`; V-Dem, de 34 MB, va a `data/raw/geopolitica/large/`, que git ignora mediante su propio `.gitignore`).

Hoy el modelo solo tiene un evento político: el riesgo de conflicto civil que genera el PSI. Lo que sigue propone cómo añadir **(i)** instituciones (tipo de régimen, transiciones, golpes, salidas irregulares de líderes) y **(ii)** geopolítica (hegemonía, bloques, ayuda, sanciones, guerra interestatal, transición de poder), usando formas funcionales anuales con parámetros tomados de la literatura o estimados aquí.

---

## 1. Datos

### 1.1 Fuentes y cobertura

Todas se descargan de `raw.githubusercontent.com`. Los espejos CRAN salen del paquete `peacesciencer` de Miller (2022); el resto viene de repositorios de replicación públicos.

| Bloque | Fuente | Variables principales | Años | Países |
|---|---|---|---|---|
| Golpes | Powell & Thyne (2011), v2023-09-08 | `coup_attempts`, `coup_success`, `coup_failed`, `coup_any`, `years_since_coup`, `coups_past10` | 1950–2019 | 202 |
| Régimen | V-Dem v15 (paquete `vdemdata`) | `vdem_polyarchy`, `vdem_libdem`, `regime_row` (Regimes of the World 0–3), `regime_change`, `dem_transition`, `dem_breakdown`, `polyarchy_change`, `vdem_ex_military`, `vdem_neopat`, `vdem_corr`, `vdem_rule`, `vdem_jucon`, `vdem_fisccap` (capacidad fiscal), `vdem_intl_autonomy`, `vdem_civlib` | 1946–2019 | 176 |
| Régimen (alternativas) | Boix-Miller-Rosato y Cheibub-Gandhi-Vreeland, vía V-Dem; Polity5 y UDS, vía peacesciencer | `bmr_democracy`, `bmr_transition` (±1), `bmr_breakdowns`, `cheibub_democracy` (≤2008), `polity2` (≤2017), `uds_democracy` (≤2017) | 1946– | 167–195 |
| Líderes | Archigos 4.1 (Goemans, Gleditsch & Chiozza 2009) | `leader_entries`, `leader_irregular_exit`, `leader_foreign_removal`, `leader_removed_military`, `leader_removed_protest`, `leader_tenure`, `leader_irregular_entry` | 1946–2015 | 202 |
| Capacidades | COW NMC 6.0 | `cinc`, `log_cinc`, `milex`, `milper`, `cinc_rank` | 1946–2016 | 195 |
| Estatus | Grandes potencias COW; potencias de Maoz | `major_power`, `global_power_maoz`, `regional_power_maoz` | 1946–2019 | – |
| Alianzas | ATOP 5.1 (diadas) | `n_defense_allies`, `n_allies_any`, `ally_us_defense`, `ally_rus_defense`, `ally_chn_defense`, `bloc` (+1 bloque EE.UU. / −1 bloque URSS / 0) | 1946–2018 | 202 |
| Afinidad | Puntos ideales en la AGNU (Bailey, Strezhnev & Voeten 2017) | `unga_ideal_point`, `unga_dist_us`, `unga_dist_rus`, `unga_dist_chn` (desde 1971) | 1946–2019 | 194 |
| Disputas | GML MID 2.2.1 | `mid_ongoing`, `mid_onset`, `mid_n`, `mid_n_onsets`, `mid_fatal`, `mid_initiated`, `mid_hostlev_max`, `mid_use_force` | 1946–2010 | 201 |
| Guerra interestatal | COW Inter-State War 4.0 | `cow_war_ongoing`, `cow_war_onset`, `cow_war_batdeaths`, `cow_war_won`, `cow_war_lost` | 1946–2003 | 201 |
| Conflicto interestatal e intervención | UCDP/PRIO ACD (`data/raw/ucdp_acd.csv`) | `ucdp_interstate`, `ucdp_interstate_war`, `intervention_abroad_n` (actor secundario en guerras civiles ajenas), `civil_war_foreign_intervened` | 1946–2019 | 202 |
| Rivalidades | Thompson & Dreyer (2012) | `n_rivalries`, `rival_parity_max` (min/max del CINC frente al rival), `rival_power_share_min` | 1946–2010 | 96 con rival |
| Vecindad | COW Direct Contiguity 3.2 | `n_contig_neighbors` (tierra o agua ≤150 millas), `n_land_neighbors`, `neighbor_parity_max` (máxima paridad CINC con un vecino, ≤2016), `neighbor_dem_share` (difusión) | 1946–2019 | 202 |
| Ayuda | WDI DT.ODA.ODAT.GN.ZS (AOD neta, % del INB) | `oda_gni` | 1960–2019 | 161 |
| Sanciones | Global Sanctions Data Base v4 (Felbermayr et al. 2020) | `sanctions_n`, `sanctions_onset`, `sanctions_us`, `sanctions_eu`, `sanctions_un`, `sanctions_trade`, `sanctions_financial` | 1949–2019 | 202 |

Series mundiales (`geopolitica_world.csv`):

- **Poder material:** `cinc_share_usa`, `cinc_share_rus`, `cinc_share_chn`, `cinc_top1_iso`, `cinc_top1_share`, `cinc_top2_share`, `cinc_lead_ratio`, `cinc_hhi`, `cinc_con` (concentración de Singer-Bremer-Stuckey), `chn_usa_cinc_ratio`, `n_poles_10pct`.
- **PIB:** `gdp_share_usa`, `gdp_share_chn`, `gdp_share_rus`, `chn_usa_gdp_ratio` (PIB en PPA de 2011 según Anders, Fariss & Markowitz 2020; hasta 2015).
- **Orden internacional:** `cold_war` y `bipolar` (1947–1991), `n_states`, `share_democracies_row`, `mean_polyarchy`.
- **Conteos de eventos:** `coups_world`, `coups_success_world`, `dem_transitions_world`, `dem_breakdowns_world`, `mid_onsets_world`, `states_in_interstate_conflict`, `states_sanctioned`, `n_major_powers`, `mean_oda_gni`.

### 1.2 Decisiones de construcción

- **Códigos de país.** Se usa `country_converter` (clasificación `GWcode`) más un mapa manual, porque el conversor falla con varios casos: 816 y 817 los asigna mal, y no reconoce 255, 678, 679 ni 345. Criterio de continuidad: COW 255/260 y GW 260 → DEU, 345/340 → SRB, 365 → RUS, 678/679 → YEM, 315/316 → CZE, 816 → VNM. Los microestados del Pacífico difieren entre COW y GW (COW 970 = Nauru, GW 970 = Kiribati) y se tratan por separado. Los estados extintos (RDA, Yemen del Sur, Vietnam del Sur) se usan internamente y se eliminan del panel final. Solo quedan ISO3 válidos más Kosovo (XKX). No se cubren los territorios británicos del panel PWT (AIA, BMU, CYM, MSR, TCA, VGB). Cobertura sobre las filas de `panel.csv`: CINC 86 %, polyarchy 91 %, golpes 96 %.
- **Eventos.** Se rellenan con 0 solo dentro de la ventana de cobertura de su fuente y quedan NaN fuera de ella (p. ej., MID después de 2010 o guerra COW después de 2003). Para 2004–2019 conviene usar `ucdp_interstate`.
- **Transiciones.** `dem_transition` vale 1 cuando `regime_row` pasa de ≤1 (autocracia cerrada o electoral) a ≥2 (democracia electoral o liberal); `dem_breakdown` es el cambio inverso.
- **Bloque.** `bloc` = pacto de defensa ATOP con EE.UU. menos pacto con URSS/Rusia; EE.UU. vale +1 y la URSS −1 hasta 1991. `cold_war` = 1947–1991.
- **Sanciones.** Los emisores y blancos colectivos del GSDB (p. ej., "Comecon" o "Terrorist organizations") se descartan salvo que se puedan descomponer en países.
- **Advertencia sobre el CINC.** Pesa mucho la población, el acero y la energía. Por eso la URSS supera a EE.UU. entre 1971 y 1987, y China lo supera desde 1995. Para la hegemonía económica conviene usar también `gdp_share_*`.

### 1.3 Hechos estilizados (de los datos construidos)

| | 1950 | 1970 | 1990 | 2000 | 2010 | 2015/16 |
|---|---|---|---|---|---|---|
| Cuota de EE.UU. en el CINC | 0.28 | 0.18 | 0.14 | 0.14 | 0.15 | 0.13 |
| Cuota URSS/Rusia en el CINC | 0.18 | 0.17 | 0.13 | 0.05 | 0.04 | 0.04 |
| Cuota de China en el CINC | 0.12 | 0.11 | 0.11 | 0.16 | 0.21 | 0.23 |
| Cuota de EE.UU. en el PIB mundial | 0.27 | 0.23 | 0.22 | 0.23 | 0.18 | 0.16 |
| PIB China / PIB EE.UU. | 0.19 | 0.19 | 0.29 | 0.43 | 0.89 | 1.18 |
| Concentración del CINC (CON) | 0.35 | 0.28 | 0.24 | 0.24 | 0.27 | 0.28 |
| Proporción de democracias (RoW ≥2) | 0.16 | 0.22 | 0.32 | 0.43 | 0.47 | 0.48 |
| Estados bajo sanciones | 8 | 30 | 47 | 45 | 51 | 68 |

Tasa anual de intentos de golpe (país-año, muestra PWT) por década:

| Década | 1950s | 1960s | 1970s | 1980s | 1990s | 2000s | 2010s |
|---|---|---|---|---|---|---|---|
| Tasa | 5.6 % | 7.0 % | 5.8 % | 4.6 % | 2.8 % | 1.6 % | 1.2 % |

---

## 2. Literatura

### 2.1 Golpes de Estado

- **Trampa del golpe.** Londregan & Poole (1990, *World Politics* 42:151) estiman conjuntamente golpes e ingreso. Un golpe reciente multiplica el riesgo de otro; el ingreso bajo y el crecimiento bajo lo aumentan. El efecto del ingreso sobre los golpes es grande; el de los golpes sobre el crecimiento es pequeño y ambiguo. Belkin & Schofer (2003) distinguen entre riesgo estructural (legitimidad, sociedad civil, golpes pasados) y detonantes. Gassebner, Gutmann & Voigt (2016, *Public Choice*) hacen un análisis de *extreme bounds* sobre unos 66 predictores. Los robustos son: golpes pasados, ingreso bajo, crecimiento bajo, régimen militar u otra autocracia no consolidada, y la Guerra Fría.
- **Tasa de éxito.** Powell & Thyne (2011) registran alrededor de 490 intentos entre 1950 y 2023; la mitad aproximadamente tuvo éxito (48.6 % en nuestra muestra).
- **Coup-proofing.** Quinlivan (1999), Powell (2012, *JCR*) y De Bruin (2018, 2020, *How to Prevent Coups d'État*). Contrapesar al ejército con guardias paralelas y fuerzas de seguridad fragmentadas reduce el **éxito** de los golpes, no necesariamente los **intentos**. Su coste es menor eficacia militar en guerras interestatales (Talmadge 2015) y mayor riesgo de guerra civil (Roessler 2011, 2016: *coup-civil war trap*, un dilema entre excluir étnicamente a rivales y exponerse a una rebelión).
- **Guerra Fría y después.** Marinov & Goemans (2014, *BJPS*): tras 1991, la condicionalidad de la ayuda occidental hizo que la mayoría de los golpes terminaran en elecciones en unos 5 años. Derpanopoulos et al. (2016) lo discuten: los golpes posteriores a la Guerra Fría siguen conduciendo a autocracia en la mayoría de los casos. O'Rourke (2018, *Covert Regime Change*) documenta 64 intentos encubiertos de EE.UU. entre 1947 y 1989.
- **Consecuencias.** Meyersson (2016): los golpes contra democracias reducen el PIB per cápita de forma persistente (del orden de 1 pp de crecimiento al año durante 5–10 años). En nuestros datos, el crecimiento acumulado a 5 años tras un golpe exitoso es 6.3 %, frente a 9.9 % sin golpe, es decir, unos −0.7 pp al año (correlación, no causalidad).

### 2.2 Democracia, ingreso y crecimiento

- **Modernización.** Lipset (1959). Przeworski, Alvarez, Cheibub & Limongi (2000, *Democracy and Development*): el ingreso **no predice** las transiciones a la democracia (democratización "exógena") pero **sí la supervivencia** democrática. Esperanza de vida de una democracia según ingreso (US$ PPA de 1985):

  | Ingreso | Vida esperada | Hazard anual aprox. |
  |---|---|---|
  | < $1 000 | ≈ 8 años | 0.12 |
  | $1 000–2 000 | ≈ 16 años | 0.06 |
  | $2 000–4 000 | ≈ 33 años | 0.03 |
  | $4 000–6 055 | ≈ 100 años | 0.01 |
  | > $6 055 (Argentina, 1976) | nunca cayó ninguna | 0 |

  En dólares de 2017, multiplicar por ≈2.2.
- **Democratización endógena.** Boix & Stokes (2003) la defienden con datos desde el siglo XIX. Acemoglu, Johnson, Robinson & Yared (2008, *AER*) responden que con efectos fijos por país el efecto del ingreso sobre la democracia desaparece: ingreso y democracia comparten causas históricas (instituciones de las coyunturas críticas). Treisman (2015) encuentra que el ingreso sí aumenta la probabilidad de democratización a mediano plazo, sobre todo tras un cambio de líder.
- **Nuestros datos (logit sin efectos fijos).** El ingreso predice fuertemente los **quiebres** (coeficiente −0.73 por log de PIB per cápita, EE 0.10) y débilmente las **transiciones** (+0.25, EE 0.09). Las autocracias electorales transitan unas 8 veces más que las cerradas (coeficiente 2.08). El patrón coincide con Przeworski et al.
- **La democracia causa crecimiento.** Acemoglu, Naidu, Restrepo & Robinson (2019, *JPE* 127:47–100) usan un indicador dicotómico de democracia, efectos fijos por país y cuatro rezagos del PIB: ln y_it = Σ_{k=1..4} γ_k ln y_i,t−k + β D_it + α_i + δ_t + ε.
  - Estimación base: β ≈ 0.79 (×100, EE ≈ 0.23) y Σγ ≈ 0.963. El efecto de largo plazo es β/(1−Σγ) ≈ **21 %**; la respuesta al impulso muestra ≈ **20 % más de PIB per cápita 25 años después** de democratizar.
  - Con otros estimadores (GMM, HT, IV con olas regionales de democratización) el efecto de largo plazo va de ≈16 % a ≈35 %.
  - Canales: inversión, escolarización, salud, reformas económicas y menos malestar social.
  - Papaioannou & Siourounis (2008): +≈1 pp de crecimiento anual tras una democratización permanente.
  - En nuestros datos, el crecimiento medio es 2.4 %/año en democracias frente a 1.6 % en autocracias (bruto).
- **Difusión.** Gleditsch & Ward (2006): la proporción de democracias en el vecindario aumenta la probabilidad de transición, y las olas de Huntington (1991) tienen un componente internacional. Goldstone et al. (2010, *AJPS*, PITF) muestran que las democracias parciales con faccionalismo tienen odds de inestabilidad unas 30 veces mayores que las autocracias plenas.

### 2.3 Hegemonía y ciclos hegemónicos

- **Estabilidad hegemónica.** Kindleberger (1973), Krasner (1976), Gilpin (1981, *War and Change in World Politics*): un hegemón provee bienes públicos (apertura comercial, moneda de reserva, seguridad). El orden se erosiona porque el crecimiento se difunde a los retadores (convergencia) y porque el coste de proteger el orden crece más rápido que los recursos (*imperial overstretch*, Kennedy 1987). La evidencia de que la hegemonía causa apertura es mixta (Lake 1993; Mansfield 1994: la concentración del poder se relaciona en forma de U con el comercio).
- **Ciclos largos de Modelski** (Modelski 1987; Modelski & Thompson 1996). Ciclos de liderazgo global de ≈100–120 años: Portugal (1494–1580), Provincias Unidas (1580–1688), Gran Bretaña I (1688–1792), Gran Bretaña II (1792–1914), EE.UU. (1914–). Cada ciclo tiene cuatro fases de ≈25 años: guerra global, potencia mundial, deslegitimación y desconcentración. Operativamente, la potencia mundial controla ≥50 % del poder naval global tras la guerra global.
- **Ciclos sistémicos de acumulación de Arrighi** (1994, *The Long Twentieth Century*). Genovés (≈220 años), holandés (≈180), británico (≈130) y estadounidense (≈100), cada vez más cortos. Cada uno tiene una fase de expansión material seguida de una expansión financiera (*signal crisis*: para EE.UU., ≈1970). La financiarización es un indicador adelantado del declive hegemónico.
- **Wallerstein** (1984): las hegemonías son breves (≈25–50 años) y se basan en la superioridad simultánea en producción, comercio y finanzas. Casos: Provincias Unidas 1625–1672, Gran Bretaña 1815–1873, EE.UU. 1945–1967.
- **Datos.** La cuota de EE.UU. en el PIB mundial cae de 0.27 (1950) a 0.16 (2015), unos −0.8 %/año relativo. En el CINC cae de 0.28 a 0.13 (−1.1 %/año), con una meseta de 0.13–0.15 entre 1980 y 2016. La concentración del sistema (CON) baja hasta 1990 y vuelve a subir después, por el ascenso de China.

### 2.4 Transición de poder y guerra interestatal

- **Teoría de la transición de poder.** Organski (1958); Organski & Kugler (1980, *The War Ledger*). El riesgo de guerra entre el dominante y un retador **insatisfecho** es máximo cerca de la paridad (retador entre 80 % y 120 % del dominante) y cuando el retador crece rápido. Evidencia en Houweling & Siccama (1988), Kugler & Lemke (1996) y Lemke (2002, jerarquías regionales). Allison (2017, *Destined for War*): 12 de 16 transiciones hegemónicas en 500 años terminaron en guerra, un 75 %. Si una transición dura ≈25 años, eso implica un hazard anual de 1−0.25^(1/25) ≈ 5 %; es una cota superior sesgada por la selección de casos.
- **Diadas peligrosas.** Bremer (1992, *JCR*): la contigüidad es el predictor más fuerte, de un orden de magnitud. Le siguen la paridad de poder, la ausencia de alianza, la democracia conjunta (reduce), el desarrollo y el estatus de gran potencia. Russett & Oneal (2001): la democracia conjunta reduce la probabilidad de una MID fatal en un 35–50 %; la interdependencia comercial y las organizaciones internacionales (OIG) también la reducen. Paz nuclear: no ha habido guerra entre grandes potencias desde 1945. Con 0 eventos en 74 años, la regla del 3 da un hazard sistémico < 3/74 ≈ **4 %/año** (cota superior del 95 %).
- **Nuestros datos (monádicos).** Tasa de inicio de guerra COW de 1.65 % por país-año; conflicto interestatal UCDP en 2.0 % de los países-año; inicio de MID en 23 % de los países-año (muestra PWT). El inicio de MID aumenta con el número de rivalidades (logit +0.75 por rivalidad) y con la paridad frente al rival más fuerte (tasa de 34 % con paridad <0.2 frente a 48 % con paridad >0.8). La relación con la paridad se debilita al controlar por rivalidades, porque el nivel monádico no la identifica: hace falta un modelo diádico.
- **Guerra y crecimiento.** Chupilkin & Kóczán (2022, EBRD WP 271; unas 400 guerras, controles sintéticos): las guerras en territorio propio reducen el PIB per cápita en ≈7 pp frente al control sintético el año posterior al fin del conflicto. Las guerras fuera del territorio no lo reducen y a veces lo aumentan. Las guerras civiles dejan efectos más persistentes que las interestatales. Organski & Kugler (1977) describen el "efecto fénix": los perdedores recuperan su trayectoria en 15–20 años. Glick & Taylor (2010): las guerras destruyen comercio bilateral y con neutrales durante años. Collier (1999): la guerra civil resta ≈2.2 pp de crecimiento anual.
- **La guerra hace al Estado.** Tilly (1975, 1990, *Coercion, Capital and European States*): la competencia militar europea forzó la extracción fiscal y la burocratización. Besley & Persson (2009, 2011, *Pillars of Prosperity*): el riesgo de guerra externa (un bien común) aumenta la inversión en capacidad fiscal; la guerra civil la reduce. Dincecco & Prado (2012): las bajas en guerras premodernas predicen la capacidad fiscal actual. Thies (2005): la rivalidad interestatal aumentó la extracción en América Latina. Centeno (2002, *Blood and Debt*): las guerras limitadas latinoamericanas no construyeron Estados, porque se financiaron con deuda externa y no con impuestos (Queralt 2019). Efecto trinquete de Peacock & Wiseman (1961): el gasto no vuelve a su nivel previo tras la guerra. En nuestros datos, la capacidad fiscal V-Dem aumenta +0.22 en los 10 años posteriores al inicio de una guerra COW, frente a +0.15 sin guerra (n = 138, evidencia débil a favor de Tilly).

### 2.5 Ayuda externa

- **Efectividad.** Burnside & Dollar (2000, *AER*): la ayuda aumenta el crecimiento solo con buenas políticas. Easterly, Levine & Roodman (2004, *AER*) no lo replican con más datos. Rajan & Subramanian (2008): no hay efecto robusto. Clemens, Radelet, Bhavnani & Bazzi (2012, *EJ*): la ayuda de impacto temprano tiene un efecto positivo modesto con rendimientos decrecientes. Galiani, Knack, Xu & Zou (2017, *J. Econ. Growth*) usan como instrumento el umbral de ingreso para ser elegible a la ayuda de la AIF/IDA (la ayuda cae ≈59 % al cruzarlo): **+1 pp de AOD/INB → +0.35 pp de crecimiento per cápita anual**, vía inversión. Easterly (2006, *The White Man's Burden*) critica el enfoque de los "planificadores".
- **Asignación política.** Alesina & Dollar (2000): el pasado colonial y la afinidad en votaciones de la ONU pesan más que la pobreza o las políticas. Kuziemko & Werker (2006): ser miembro rotativo del Consejo de Seguridad aumenta la ayuda de EE.UU. un ≈59 %. Durante la Guerra Fría la ayuda compraba alineamiento; después se condicionó a la democracia (Dunning 2004; Bermeo 2016). Nuestros datos: AOD/INB mediana de 2.7 % entre receptores. Los aliados formales de EE.UU. reciben menos en proporción al INB (1 % frente a 4.4 % de los no alineados en la Guerra Fría), un efecto de composición porque los aliados son más ricos.
- **Efectos no deseados.** Nunn & Qian (2014, *AER*): un 10 % más de ayuda alimentaria de EE.UU. aumenta la incidencia de conflicto civil en ≈0.7 pp. Djankov, Montalvo & Reynal-Querol (2008): la ayuda funciona como una renta ("maldición de la ayuda") y reduce la democracia.

### 2.6 Sanciones

- **Eficacia política.** Hufbauer, Schott & Elliott (2007) cifran el éxito en ≈34 % de los casos; Pape (1997) lo reduce a <5 %. El GSDB clasifica los resultados de ≈1 500 casos.
- **Efectos económicos.** Neuenkirch & Neumeier (2015, *EJPE*): las sanciones de la ONU reducen el crecimiento per cápita en 2.3–3.5 pp durante ≈10 años (−25 % de PIB acumulado; más de 5 pp si el embargo es integral). Las de EE.UU. lo reducen en 0.75–1 pp durante ≈7 años (−13 % acumulado).
- **Efectos políticos.** Marinov (2005, *AJPS*): las sanciones desestabilizan a los líderes y aumentan la probabilidad de que pierdan el poder. Escribà-Folch & Wright (2010): el efecto se concentra en regímenes personalistas. Peksen & Drury (2010): las sanciones reducen la democracia del país sancionado.

### 2.7 Alineamiento en la Guerra Fría

- **Bipolaridad** (Waltz 1979: más estable entre grandes potencias). Las superpotencias compitieron en la periferia con guerras subsidiarias, intervenciones encubiertas y ayuda.
- **Nuestros datos.** La Guerra Fría multiplica el riesgo de golpe por e^0.80 ≈ 2.2, controlando por ingreso, crecimiento, régimen y trampa del golpe.
- **Intereses económicos.** Berger, Easterly, Nunn & Satyanath (2013, *AER*): las intervenciones de la CIA aumentaron las importaciones del país intervenido desde EE.UU.
- **Imposición externa de régimen.** Downes & Monten (2013): el cambio de régimen impuesto desde fuera rara vez democratiza.
- **Distancia en la AGNU.** Es un proxy continuo de alineamiento (Bailey et al. 2017) y predice ayuda, sanciones y disputas.

---

## 3. Especificación recomendada para el modelo anual

Notación:

| Símbolo | Significado |
|---|---|
| y | PIB per cápita (PWT, US$ de 2017) |
| ℓ | ln(y_{t−1}/10 000) |
| g | crecimiento de ln y en t−1 |
| D ∈ {0,1} | democracia (RoW ≥ 2) |
| EA | autocracia electoral (RoW = 1) |
| T | 1 si hubo intento de golpe en los 10 años previos |
| CW | Guerra Fría (1947–1991) o su equivalente endógeno (bipolaridad simulada) |
| W_D | proporción mundial de democracias |
| PSI | índice de estrés político del bloque estructural-demográfico, estandarizado |

Todas las probabilidades son anuales (logit Λ). Los coeficientes marcados con "est." son estimaciones propias en 1951–2019 (≈9 500 países-año; logit sin efectos fijos, errores no agrupados). Están guardados en `geopolitica_dict.json → calibration_targets`. Hay que tomarlos como **priors de calibración**, no como estimaciones causales.

### 3.1 Golpes de Estado (trampa del golpe)

```
P(intento) = Λ( −4.35 − 0.28·ℓ − 2.7·g + 1.37·T − 0.71·D + 0.80·CW + a_PSI·PSI )
             (EE:  0.47   0.06   0.7    0.12    0.19    0.13 ;  est.)
P(éxito | intento) = 0.50  (rango 0.45–0.55; menor si hubo coup-proofing)
```

- Con una variable de régimen militar (`vdem_ex_military`, coeficiente +2.05) y autocracia electoral (+0.82), el término de trampa baja a 0.83 y el de democracia se vuelve nulo. Los regímenes militares explican buena parte de la trampa.
- **a_PSI.** Prior de 0.3–0.6 por desviación estándar, a calibrar para que el modelo reproduzca la tasa de golpes por década. Una parte de la trampa del golpe es inestabilidad de élites (Turchin: sobreproducción de élites).
- **Efectos de un golpe exitoso.**
  - El régimen pasa a autocracia cerrada o electoral y el líder cambia.
  - Crecimiento −0.7 a −1 pp/año durante 5 años (Meyersson 2016; nuestros datos dan −0.7).
  - Hazard de golpe elevado vía T durante 10 años.
  - Tras la Guerra Fría, 50 % de probabilidad de volver a elecciones en 5 años (Marinov & Goemans 2014).
- **Coup-proofing como elección del incumbente.** Reduce P(éxito) en un 30–50 %, a cambio de −10 a −20 % de eficacia militar en guerra interestatal y de un aumento del hazard de conflicto civil (Roessler).
- **Blancos de calibración:**
  - Tasa media 3.7 %/año (1950–2019).
  - Por décadas: 5.6 / 7.0 / 5.8 / 4.6 / 2.8 / 1.6 / 1.2 %.
  - Por cuartiles de ingreso: q1–q2 ≈ 6.2 %, q3 1.7 %, q4 0.5 %. Cortes en $2 725, $7 108 y $16 860.
  - Con golpe en los 10 años previos: 10.7 %; sin él: 1.8 %.
  - Proporción de éxitos: 48.6 %.

### 3.2 Cambio de régimen

La recomendación es una cadena de Markov sobre las cuatro categorías RoW, o una versión binaria D ∈ {0,1}.

```
P(A→D) = Λ( −5.32 + 0.25·ℓ − 1.5·g + 2.08·EA + 0.7·W_D − 0.2·CW )        (est.; EE ℓ 0.09, EA 0.31)
P(D→A) = Λ( −3.34 − 0.73·ℓ − 5.2·g − 1.1·W_D − 0.8·CW )                  (est.; EE ℓ 0.10, g 2.0)
```

- **Interpretación.** Las transiciones apenas dependen del ingreso: son "exógenas" (Przeworski et al.) y sensibles a shocks. Los quiebres sí dependen del ingreso: el hazard cae de ≈5 % en el cuartil pobre a 0.3 % en el rico. El crecimiento negativo desencadena ambos tipos de cambio.
- **Coherencia con Przeworski.** Hazard de quiebre de ≈0.08 con y ≈ $2 000 y ≈0.01 con y ≈ $30 000 (con W_D ≈ 0.3); por encima de ≈$15 000 los quiebres son casi inexistentes en los datos (0.3 % en q4).
- **Acoplamientos sugeridos.**
  - Golpe exitoso ⇒ D→A inmediato.
  - Guerra civil (PSI alto) ⇒ multiplicador ×1.5–2 sobre ambos hazards; las democracias parciales son las más inestables (Goldstone et al. 2010).
  - Presión de la potencia hegemónica: si el hegemón es democrático y la ayuda se condiciona a la democracia (post-1991), sumar +0.5 a +1 al logit de P(A→D) de los receptores de ayuda (Dunning 2004).
  - Difusión regional: la proporción de vecinos contiguos democráticos (`neighbor_dem_share`) entra con **+1.32** (EE 0.31; est., `dem_transition_logit_neighbors`). Es mucho más precisa que la proporción mundial W_D y concuerda con Gleditsch & Ward (2006). Se recomienda usar la difusión vecinal en lugar de W_D.
- **Blancos de calibración:**
  - Tasa de transición de autocracias: 2.1 %/año. Por cuartiles de ingreso: 1.5 / 1.8 / 4.2 / 1.6 %.
  - Tasa de quiebre de democracias: 1.7 %/año. Por cuartiles: 5.2 / 4.5 / 1.8 / 0.3 %.
  - Proporción de democracias: 0.16 (1950) → 0.22 (1970) → 0.32 (1990) → 0.47 (2010) → 0.47 (2019).

### 3.3 Efecto de la democracia sobre el crecimiento

Siguiendo Acemoglu et al. (2019), la democracia se implementa como un impulso a la PTF con dinámica propia:

```
ln A_it = ln A_it^base + B_it
B_it = ρ_B·B_i,t−1 + β_D·D_it        con β_D = 0.0079, ρ_B = 0.963
⇒ efecto de largo plazo β_D/(1−ρ_B) ≈ 0.21 ; tras 25 años ≈ 0.13–0.20 según los rezagos
```

- La forma más simple que reproduce "+20 % en 25 años" es un crecimiento adicional de **+0.8 pp/año durante 25 años**, con tope de 0.20 en ln A, mientras D = 1. Si hay quiebre, B decae con ρ_B.
- Rango de incertidumbre del efecto de largo plazo: 0.10–0.35.
- Al democratizar se puede añadir una caída transitoria de −1 a −2 pp el primer año (ANRR encuentran una caída previa a la transición).

### 3.4 Guerra interestatal y transición de poder

**Nivel diádico** (recomendado; la matriz de pares se limita a vecinos más grandes potencias):

```
h_ij = Λ( c0 + 2.3·Contig_ij + β_p·P_ij + 0.8·Rival_ij − 0.7·D_i·D_j − 0.5·Ally_ij + 0.3·Dissat_ij )
P_ij = max(0, 1 − |ln(C_i/C_j)| / ln 3)     (1 con paridad exacta, 0 si la ratio de CINC es ≥3:1)
β_p ≈ 0.7–1.1  (paridad ⇒ riesgo ×2–3; Bremer 1992, Kugler & Lemke 1996)
```

- c0 se calibra para que la tasa monádica de inicio de guerra sea ≈1.6 %/año (COW, 1946–2003) y la de MID fatal ≈12 %/año.
- `Dissat` se aproxima con la distancia en la AGNU al hegemón (`unga_dist_us`) o con el bloque opuesto.

**Nivel monádico**, si no se modelan diadas:

```
P(war onset) = Λ( −5.2 + 0.46·P_rival + 0.52·N_rival + 0.26·CW )     (est.; EE 0.41, 0.08, 0.23)
```

**Guerra hegemónica (sistémica).** Sea r = C_retador/C_hegemón.

```
h_H = 0.002 + 0.04·1[0.8 ≤ r ≤ 1.2]·Dissat·(1 − 0.7·Nuclear)
```

- La tasa dentro de la zona de transición (≈4 %/año) es compatible con Allison (75 % en ≈25 años) y con la cota empírica post-1945 (<4 %/año, cero guerras).
- En las simulaciones, con disuasión nuclear, la tasa efectiva es ≈1 %/año.

**Efectos de la guerra.**

- **PIB.** En territorio propio: −3 a −10 % durante la guerra (≈−7 pp frente al control sintético; Chupilkin & Kóczán 2022) más destrucción de capital. La recuperación es acelerada (efecto fénix: la brecha se cierra en 15–20 años, tasa ≈0.1/año). Fuera del territorio: efecto nulo o ligeramente positivo.
- **Capacidad estatal S (efecto de Tilly).** dS = +θ_w durante la guerra, con θ_w ≈ 0.02–0.05 de la escala V-Dem al año, o +1–3 pp de ingresos fiscales/PIB por guerra mayor con efecto trinquete. Cuando la guerra se financia con deuda externa (caso latinoamericano), θ_w ≈ 0. Una rivalidad activa suma una contribución pequeña (≈+0.01/año).
- **Derrota.** Aumenta el riesgo de salida irregular del líder y de cambio de régimen (Bueno de Mesquita et al. 1992): multiplicador de ×2–3 en P(cambio de régimen) el año del fin de la guerra.

### 3.5 Dinámica hegemónica

Sea H_t la cuota del hegemón en el PIB o el CINC mundial.

```
g_hegemón = g_mundo − δ_H + ε ,   δ_H ≈ 0.008–0.011 (erosión relativa observada 1950–2015)
δ_H = δ_0 + κ·(gasto_militar_hegemón/PIB − m*)   (overstretch; Kennedy 1987, Gilpin 1981)
```

- La convergencia de los retadores ya la genera el bloque de crecimiento; δ_0 captura los costes de liderazgo.
- **Bienes públicos.** La apertura comercial del sistema (aranceles, costes de comercio del bloque World-Systems) mejora con H mientras H > H* ≈ 0.25. Por debajo aumentan el proteccionismo, la fragmentación en bloques y la volatilidad financiera.
- **Fase financiera (Arrighi).** Cuando la rentabilidad del hegemón cae, la cuota financiera de su economía sube. Es un indicador adelantado de declive, a calibrar con el bloque financiero si existe.
- **Ciclo.** Un cambio de liderazgo requiere r > 1 y (con alta probabilidad) una guerra hegemónica. La duración del ciclo emerge del modelo y debe quedar en el rango de 80–130 años (Modelski ≈100–120; Arrighi con ciclos cada vez más cortos).
- **Blancos de calibración:**
  - Cuota de EE.UU. en el CINC: 0.28 → 0.14 → 0.13 (1950/1990/2016).
  - Cuota de EE.UU. en el PIB: 0.27 → 0.22 → 0.16 (1950/1990/2015).
  - PIB China/EE.UU.: 0.19 (1950), 0.29 (1990), 0.89 (2010), 1.18 (2015).
  - Concentración CON: 0.35 (1950) → 0.24 (1990) → 0.28 (2016).
  - Cuota de la URSS en el CINC: ≈0.17 de forma estable hasta 1985, y un colapso a 0.04 después de 1991.

### 3.6 Bloques, ayuda y sanciones

- **Alineamiento.** Una variable continua a_i ∈ [−1, 1] (bloque), inicializada con `bloc` y con `unga_dist_us` normalizada. Durante la bipolaridad, cada superpotencia:
  - asigna ayuda a sus aliados ∝ afinidad × importancia estratégica (Alesina & Dollar 2000);
  - interviene de forma encubierta en países alineados con el rival: multiplicador ×2 sobre el hazard de golpe (CW = 0.80 en el logit);
  - arma a los gobiernos aliados (menor P(éxito rebelde)).
- **Ayuda.** AOD/INB_i = f(ℓ, afinidad, estatus de ex-colonia). Mediana de 2.7 % entre receptores; decae con el ingreso y es casi nula por encima del umbral de elegibilidad para la ayuda de la AIF/IDA.
  - Efecto sobre el crecimiento: **+0.35 pp por cada 1 pp de AOD/INB** (Galiani et al. 2017), con rendimientos decrecientes (p. ej., 0.35·a·(1 − a/0.3) para a = AOD/INB ≤ 0.3). Rango de incertidumbre: 0–0.35 (Rajan & Subramanian 2008).
  - Efecto secundario: la ayuda es fungible y financia élites, así que eleva el hazard de conflicto civil (Nunn & Qian 2014: +0.7 pp por un 10 % más de ayuda alimentaria).
- **Sanciones.** Hazard de ser sancionado = Λ(c + b1·dist_AGNU_hegemón + b2·golpe_t + b3·quiebre_t + b4·guerra_iniciada), calibrado para reproducir un 22.6 % de países-año bajo alguna sanción y el aumento de 8 (1950) a 80 (2019) estados sancionados.
  - Efectos: −2.3 a −3.5 pp de crecimiento/año durante ≈10 años si las sanciones son multilaterales (ONU); −0.75 a −1 pp/año durante ≈7 años si son unilaterales del hegemón.
  - Aumento del hazard de salida irregular del líder: ×1.3–1.5 (Marinov 2005), mayor en regímenes personalistas.
  - Probabilidad de "éxito" (el blanco cambia de política): ≈0.3.

---

## 4. Blancos de calibración (resumen)

| Momento | Valor | Fuente / periodo |
|---|---|---|
| Intentos de golpe, tasa anual | 3.7 % (5.6→1.2 % por década) | Powell & Thyne, 1950–2019 |
| Proporción de golpes exitosos | 48.6 % | ídem |
| Tasa de golpe con / sin golpe previo (10 años) | 10.7 % / 1.8 % | ídem |
| Salidas irregulares de líderes | 2.8 % de los países-año | Archigos, 1950–2015 |
| Transiciones A→D | 2.1 %/año | V-Dem RoW |
| Quiebres D→A | 1.7 %/año (5.2 % en q1, 0.3 % en q4) | V-Dem RoW |
| Proporción de democracias | 0.16 / 0.32 / 0.47 (1950/1990/2019) | V-Dem RoW |
| Efecto de la democracia sobre el PIB per cápita | +20 % a 25 años (rango 10–35 %) | Acemoglu et al. 2019 |
| Inicio de guerra interestatal | 1.65 % de los países-año | COW, 1946–2003 |
| Conflicto interestatal UCDP (≥25 muertes) | 2.0 % de los países-año | UCDP, 1946–2019 |
| Inicio de MID / MID fatal | 23 % / 12 % | GML, 1946–2010 (muestra PWT) |
| Guerras entre grandes potencias | 0 en 74 años (hazard < 4 %/año) | 1946–2019 |
| Cuota de EE.UU. en el CINC / PIB | 0.28→0.13 / 0.27→0.16 | NMC / Anders et al. |
| Paridad China-EE.UU. | CINC en 1995; PIB (PPA) ≈2014 | ídem |
| AOD/INB, mediana entre receptores | 2.7 % | WDI 1960–2019 |
| Países-año bajo sanciones | 22.6 % (8 estados en 1950 → 80 en 2019) | GSDB v4 |

---

## 5. Limitaciones y trabajo pendiente

1. **Cortes de cobertura.** Las MID terminan en 2010, la guerra COW en 2003 (en esta versión de peacesciencer), Archigos en 2015, el CINC en 2016, ATOP en 2018 y las rivalidades en 2010. Para 2004–2019 hay que usar UCDP (`ucdp_interstate`) y la AGNU.
2. **Datos diádicos.** No se generó un panel diádico de salida. Los insumos crudos diádicos ya están en `data/raw/geopolitica/`: contigüidad (`cow_contdir.rda`), alianzas ATOP y COW, MID GML y COW (dirigidas y no dirigidas) y guerra COW. En el panel monádico solo se resumen (paridad máxima con vecinos o rivales, aliados con EE.UU., URSS o China). Para estimar el hazard diádico de la sección 3.4 habría que construir un panel diádico de vecinos más grandes potencias.
3. **Fuentes no encontradas.** La ayuda bilateral por donante (Greenbook de EE.UU. o AidData) no apareció en GitHub; solo hay AOD total. El poder naval de Modelski y Thompson (necesario para los ciclos largos) tampoco está disponible; se aproxima con el CINC y el gasto militar.
4. **Estimaciones propias sin efectos fijos.** Capturan diferencias entre países y no tienen interpretación causal. Los errores estándar no están agrupados por país, así que la incertidumbre real es mayor.
5. **Artefacto del CINC.** Sobrevalora a los países populosos (China, India, la URSS). Para la hegemonía conviene combinar el CINC con el PIB (p. ej., la media geométrica).
6. **Transiciones según RoW.** Las transiciones son más frecuentes que en BMR porque RoW tiene cuatro categorías. BMR (`bmr_transition`) sirve como alternativa conservadora.

## Referencias principales

Acemoglu, D., Johnson, S., Robinson, J. & Yared, P. (2008). Income and democracy. *AER* 98(3). · Acemoglu, D., Naidu, S., Restrepo, P. & Robinson, J. (2019). Democracy does cause growth. *JPE* 127(1):47–100. · Alesina, A. & Dollar, D. (2000). Who gives foreign aid to whom and why? *J. Econ. Growth* 5. · Allison, G. (2017). *Destined for War*. · Arrighi, G. (1994). *The Long Twentieth Century*. · Bailey, M., Strezhnev, A. & Voeten, E. (2017). *JCR* 61(2). · Belkin, A. & Schofer, E. (2003). *JCR* 47(5). · Berger, D., Easterly, W., Nunn, N. & Satyanath, S. (2013). *AER* 103(2). · Besley, T. & Persson, T. (2009). *AER* 99(4); (2011) *Pillars of Prosperity*. · Boix, C. & Stokes, S. (2003). *World Politics* 55. · Bremer, S. (1992). Dangerous dyads. *JCR* 36(2). · Burnside, C. & Dollar, D. (2000). *AER* 90(4). · Centeno, M. (2002). *Blood and Debt*. · Chupilkin, M. & Kóczán, Z. (2022). EBRD WP 271. · Clemens, M. et al. (2012). *EJ* 122. · De Bruin, E. (2020). *How to Prevent Coups d'État*. · Derpanopoulos, G. et al. (2016). *Research & Politics*. · Dincecco, M. & Prado, M. (2012). *J. Econ. Growth* 17. · Downes, A. & Monten, J. (2013). *Int. Security* 37(4). · Dunning, T. (2004). *IO* 58(2). · Easterly, W., Levine, R. & Roodman, D. (2004). *AER* 94(3). · Escribà-Folch, A. & Wright, J. (2010). *ISQ* 54. · Felbermayr, G. et al. (2020). The Global Sanctions Data Base. *EER* 129. · Galiani, S., Knack, S., Xu, L. C. & Zou, B. (2017). *J. Econ. Growth* 22. · Gassebner, M., Gutmann, J. & Voigt, S. (2016). *Public Choice* 169. · Gilpin, R. (1981). *War and Change in World Politics*. · Gleditsch, K. & Ward, M. (2006). *IO* 60(4). · Goemans, H., Gleditsch, K. & Chiozza, G. (2009). Archigos. *JPR* 46(2). · Goldstone, J. et al. (2010). *AJPS* 54(1). · Hufbauer, G., Schott, J., Elliott, K. & Oegg, B. (2007). *Economic Sanctions Reconsidered*. · Kennedy, P. (1987). *The Rise and Fall of the Great Powers*. · Kindleberger, C. (1973). *The World in Depression*. · Krasner, S. (1976). *World Politics* 28(3). · Kugler, J. & Lemke, D. (eds.) (1996). *Parity and War*. · Kuziemko, I. & Werker, E. (2006). *JPE* 114(5). · Leeds, B. et al. (2002). ATOP. *Int. Interactions* 28. · Londregan, J. & Poole, K. (1990). Poverty, the coup trap, and the seizure of executive power. *World Politics* 42(2). · Marinov, N. (2005). *AJPS* 49(3). · Marinov, N. & Goemans, H. (2014). *BJPS* 44(4). · Meyersson, E. (2016). Political man on horseback. Working paper. · Miller, S. (2022). peacesciencer. *CMPS* 39(6). · Modelski, G. (1987). *Long Cycles in World Politics*. · Neuenkirch, M. & Neumeier, F. (2015). *EJPE* 40:110–125. · Nunn, N. & Qian, N. (2014). US food aid and civil conflict. *AER* 104(6). · O'Rourke, L. (2018). *Covert Regime Change*. · Organski, A. F. K. & Kugler, J. (1980). *The War Ledger*. · Papaioannou, E. & Siourounis, G. (2008). *EJ* 118. · Pape, R. (1997). *Int. Security* 22(2). · Powell, J. (2012). *JCR* 56(6). · Powell, J. & Thyne, C. (2011). *JPR* 48(2). · Przeworski, A., Alvarez, M., Cheibub, J. & Limongi, F. (2000). *Democracy and Development*. · Rajan, R. & Subramanian, A. (2008). *REStat* 90(4). · Roessler, P. (2011). *World Politics* 63(2). · Russett, B. & Oneal, J. (2001). *Triangulating Peace*. · Singer, J. D., Bremer, S. & Stuckey, J. (1972). Capability distribution, uncertainty, and major power war. · Talmadge, C. (2015). *The Dictator's Army*. · Thies, C. (2005). *AJPS* 49(3). · Thompson, W. & Dreyer, D. (2012). *Handbook of International Rivalries*. · Tilly, C. (1990). *Coercion, Capital, and European States*. · Treisman, D. (2015). *BJPS* 45(4). · Wallerstein, I. (1984). *The Politics of the World-Economy*.
