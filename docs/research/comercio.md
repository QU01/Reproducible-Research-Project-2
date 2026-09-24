# Comercio, IED, intercambio desigual y tecnología

Fuente del proyecto: `src/sources/comercio.py` (`build()`). Salidas:

| Fichero | Contenido |
|---|---|
| `data/processed/sources/comercio.csv` | panel país-año (iso3, year), 1950-2019, 13 625 filas, 251 códigos ISO3 (cubre los 183 del panel PWT) |
| `data/processed/sources/comercio_dyadic.csv.gz` | 790 673 flujos bilaterales dirigidos anuales, 1950-2014 (4,1 MB) |
| `data/processed/sources/comercio_dict.json` | diccionario (descripción, unidad, fuente y cobertura de cada variable) y **estimaciones auxiliares** (gravedad, efecto Penn, ECI→crecimiento, difusión, drenaje por década) |
| `data/raw/comercio/` | ficheros brutos; `large/` (COW diádico, 81 MB) está excluido de git con su propio `.gitignore` |

Reconstrucción: `.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import comercio; comercio.build()"` (unos 20 s; descarga lo que falte).

---

## 1. Datos

### 1.1 Fuentes obtenidas

Todas se descargan desde `raw.githubusercontent.com` (espejos en GitHub de los ficheros oficiales; las URL están en `SOURCES`).

| Fuente | Cobertura | Uso |
|---|---|---|
| **COW Dyadic Trade v4.0** (Barbieri y Keshk 2016; Barbieri, Keshk y Pollins 2009) | 1870-2014, díadas, millones de USD corrientes | red comercial, cuotas con el centro, concentración, drenaje |
| **CEPII GeoDist** (Mayer y Zignago 2011), paquete CRAN `cepiigeodist` | distancias, contigüidad, lengua, vínculo colonial | gravedad |
| **countrycode** (CRAN) | tabla COW→ISO3 | armonización |
| **Atlas of Economic Complexity** (Harvard Growth Lab), ECI SITC 1962-2016 y HS 1995-2016, vía Gapminder/open-numbers DDF | 250 países | complejidad |
| **Growth Lab ECI rankings** (SITC, HS92) | 1995-2023 (se usa hasta 2019) | complejidad reciente |
| **WDI** (Banco Mundial), ediciones 2024-2025 | ver tabla 1.2 | apertura, IED, tecnología, términos de intercambio |
| **PWT 10.01** (`data/raw/pwt1001.csv`, ya en el repo) | 1950-2019 | niveles de precios `pl_gdpo`, `pl_x`, `pl_m`; PIB nominal = `cgdpo·pl_gdpo` |

Armonización COW→ISO3: se usa el sucesor que emplea PWT. RFA (260) pasa a DEU, Checoslovaquia (315) a CZE, Yugoslavia (345) a SRB y Yemen del Norte (678) a YEM. La RDA, Yemen del Sur y Vietnam del Sur se descartan. Los valores `-9` de COW (dato ausente) y los flujos nulos no se escriben en el fichero diádico, de modo que una díada ausente significa "0 o desconocido".

### 1.2 Variables país-año (`comercio.csv`)

Las cuotas se expresan como fracciones. El "centro" (`is_core`) está formado por los países del 20 % superior del PIB per cápita PWT (`rgdpna/pop`) en cada año. Es el mismo criterio que usa el modelo (`core_q = 0.80`).

| Variable | Definición | Cobertura (años; n obs.; países) |
|---|---|---|
| `exports_cow`, `imports_cow` | suma de flujos diádicos, M USD corrientes | 1950-2014; 9 450; 188 |
| `openness_cow` | (X+M)/PIB nominal, solo bienes | 1950-2014; 8 431; 171 |
| `openness_pwt` | `csh_x − csh_m` (PPA) | 1950-2019; 10 378; 183 |
| `trade_gdp_wdi` | NE.TRD.GNFS.ZS (bienes y servicios) | 1960-2019; 7 890; 190 |
| `share_trade_core`, `share_x_to_core`, `share_m_from_core` | peso del centro en el comercio | 1950-2014; ~9 440; 188 |
| `hhi_export_partners`, `hhi_import_partners`, `n_export_partners` | concentración por socio (Herfindahl) | 1950-2014; ~9 420; 188 |
| `drain_erdi_usd`, `_gdp`, `_x` | drenaje por intercambio desigual, método ERDI (§3.1), solo periferia | 1950-2014; 6 704; 155 |
| `drain_px_usd`, `_gdp`, `_x` | variante conservadora con precios de exportación `pl_x` | 1950-2014; 6 702; 155 |
| `drain_erdi_in_*`, `drain_px_in_*` | drenaje recibido por cada país del centro | 1950-2014; 1 697; 41 |
| `price_level` | `pl_gdpo` (EE. UU. = 1); ERDI = 1/price_level | 1950-2019; 183 |
| `tot_pwt` | términos de intercambio `pl_x/pl_m` | 1950-2019; 183 |
| `tot_wdi` | TT.PRI.MRCH.XD.WD (2000=100) | 1980-2011; 195 |
| `fdi_in_gdp`, `fdi_out_gdp` | IED neta entrante y saliente / PIB | 1970-2019; 200 / 196 |
| `fdi_in_stock_proxy` | Σ entradas/PIB con depreciación del 5 %, contada desde la primera observación | 1970-2019; 200 |
| `eci` | ECI empalmado: Growth Lab SITC (1995+) y Atlas SITC reescalado antes de 1995 (r = 0,96 en el solape; pendiente 0,975) | 1962-2019; 11 788; 250 |
| `eci_sitc_atlas`, `eci_hs_atlas`, `eci_sitc_gl`, `eci_hs92_gl` | series originales | ver diccionario |
| `hightech_x_share` | TX.VAL.TECH.MF.ZS (este fichero WDI solo trae 2007+) | 2007-2019; 184 |
| `manuf_x_share` | TX.VAL.MANF.ZS.UN | 1962-2019; 198 |
| `patents_resident`, `patents_res_per_mn` | IP.PAT.RESD (total y por millón de habitantes) | 1980-2019; 156 |
| `researchers_per_mn` | SP.POP.SCIE.RD.P6 | 1996-2019; 136 |
| `rd_gdp` | GB.XPD.RSDV.GD.ZS | 1996-2019; 150 |

### 1.3 Hechos estilizados (periferia = países fuera del centro, medianas)

| Década | cuota del comercio con el centro | HHI socios exp. | apertura PWT | `tot_pwt` | ECI |
|---|---|---|---|---|---|
| 1950 | 0,73 | 0,21 | 0,22 | 1,09 | — |
| 1960 | 0,75 | 0,24 | 0,20 | 1,01 | −0,41 |
| 1970 | 0,67 | 0,18 | 0,26 | 0,96 | −0,16 |
| 1980 | 0,69 | 0,17 | 0,26 | 0,99 | −0,21 |
| 1990 | 0,68 | 0,15 | 0,26 | 1,02 | −0,26 |
| 2000 | 0,56 | 0,13 | 0,40 | 1,05 | −0,28 |
| 2010 | 0,49 | 0,11 | 0,44 | 1,10 | −0,35 |

Estructura del comercio mundial por tipo de díada (fracción del valor total; C = centro, P = periferia; la primera letra es el exportador):

| Década | P→P | P→C | C→P | C→C |
|---|---|---|---|---|
| 1950 | 0,08 | 0,22 | 0,26 | 0,44 |
| 1970 | 0,10 | 0,20 | 0,20 | 0,50 |
| 1990 | 0,07 | 0,18 | 0,18 | 0,56 |
| 2010 | 0,16 | 0,23 | 0,23 | 0,38 |

El comercio Sur-Sur se duplica después de 2000, sobre todo por China. Por eso el supuesto actual del modelo (toda la periferia comercia con el centro y le transfiere valor) exagera las transferencias después de 2000.

---

## 2. Literatura y magnitudes

### 2.1 Gravedad

- **Head y Mayer (2014, *Handbook of International Economics* vol. 4)**, metaanálisis de 2 500 estimaciones. La elasticidad a la distancia tiene mediana −0,89 en todas las estimaciones y −1,14 en las estructurales (con efectos fijos exportador/importador). Las elasticidades al PIB están cerca de 1. Las medianas de los regresores ficticios son: contigüidad ≈ 0,5-0,7, lengua común ≈ 0,5 y vínculo colonial ≈ 0,9.
- **Santos Silva y Tenreyro (2006)**: la estimación PPML reduce la elasticidad a la distancia a ≈ −0,75 e incorpora los ceros.
- **Estimación propia** (`estimates.gravity`: MCO log-lineal con EF de año, COW 1950-2014, 643 837 obs., R² within 0,63): ln Y_o 0,99; ln Y_d 0,84; ln dist −1,04; contig 0,55; lengua 0,57; colonia 1,04. Las cifras coinciden con la literatura. Los errores estándar son ingenuos (≤ 0,015), así que la incertidumbre real se toma de la literatura (±0,2 en distancia).

### 2.2 Intercambio desigual y drenaje

- **Emmanuel (1972, *Unequal Exchange*)**: la transferencia de valor nace de diferencias salariales mayores que las de productividad, con capital móvil y trabajo inmóvil. **Amin (1974, 1976)** estimó unos 22 000 M USD anuales hacia finales de los sesenta. **Köhler (1998)** aplicó el "exchange-rate deviation" (ERD) y obtuvo ≈ 1,75 billones USD en 1995.
- **Hickel, Sullivan y Zoomkawala (2021, *New Political Economy* 26(6))**, "Plunder in the post-colonial era". Método ERDI: las exportaciones del Sur se revalúan a precios del Norte con la razón entre los índices de desviación del tipo de cambio. El drenaje total 1960-2018 fue de **62 billones USD de 2011** (152 billones si se cuenta el crecimiento perdido), y en 2015 **≈ 2,2 billones USD/año**. La intensidad aumenta con fuerza durante el ajuste estructural de los años 80-90. Con salarios en vez de ERDI el orden de magnitud es similar.
- **Hickel, Dorninger, Wieland y Suwandi (2022, *Global Environmental Change* 73)**, "Imperialist appropriation in the world economy: drain from the global South through unequal exchange, 1990-2015" (el coautor es Wieland, no Wiedmann). Con MRIO (Eora) calculan la apropiación neta del Norte en 2015: 12 Gt de materias primas equivalentes, 822 Mha de tierra, 21 EJ de energía y 188 millones de años-persona de trabajo. Todo ello vale **≈ 10,8 billones USD a precios del Norte** y suma 242 billones en 1990-2015. Hay que exportar unas 13 unidades de trabajo incorporado para importar una.
- **Hickel, Hanbury Lemos y Barbour (2024, *Nature Communications*)** extienden el análisis al trabajo incorporado en 2021: el Sur aporta ≈ 90 % del trabajo de las cadenas globales y recibe ≈ 21 % del ingreso.
- **Crítica metodológica.** El ERDI mezcla intercambio desigual con el efecto Balassa-Samuelson (precios de no transables). Por eso es una **cota superior** de la transferencia de *ingreso*, que es lo que el modelo resta al PNB.

### 2.3 Términos de intercambio (Prebisch-Singer)

- **Grilli y Yang (1988)**: los precios de materias primas no energéticas caen frente a las manufacturas ≈ 0,5-0,6 %/año entre 1900 y 1986.
- **Ocampo y Parra (2010)**: la caída es escalonada, con rupturas en 1920 y 1979.
- **Harvey, Kellard, Madsen y Wohar (2010, *REStat*)**, con series desde 1650: tendencia negativa significativa en unas 11 de 25 materias primas.
- **Arezki, Hadri, Loungani y Rao (2014, *JIMF*)**: resultados similares con rupturas estructurales.
- **Datos propios**: `tot_pwt` de la periferia no muestra tendencia en 1950-2019. Cae de 1,09 a 0,96 en los años 70 y sube a 1,10 en los 2010 con el superciclo de materias primas. Prebisch-Singer se puede modelar como una deriva de −0,5 %/año en el precio relativo de las exportaciones primarias, con ciclos largos (±30 %).

### 2.4 Difusión tecnológica por comercio e IED

- **Coe y Helpman (1995, *EER*)**, 22 países OCDE. La elasticidad de la PTF al stock doméstico de I+D es 0,234 en el G7 y 0,078 en el resto. El stock extranjero ponderado por importaciones tiene coeficiente ≈ 0,29 (interactuado con la cuota importadora).
- **Coe, Helpman y Hoffmaister (1997, *EJ*)**, 77 países en desarrollo, 1971-1990. La elasticidad de la PTF al stock de I+D del Norte ponderado por importaciones de maquinaria es **0,058** y la elasticidad a la cuota importadora **0,279**. **CHH (2009)** confirman la cointegración y encuentran más spillovers con mejores instituciones.
- **Keller (2002, *AER*; 2004, *JEL*)**: los spillovers se reducen a la mitad a ≈ 1 200 km. Las fuentes extranjeras explican ≈ 90 % del crecimiento de la productividad en países pequeños de la OCDE. El comercio explica una parte y la IED otra (evidencia micro más robusta).
- **Borensztein, De Gregorio y Lee (1998, *JIE*)**: la IED eleva el crecimiento solo por encima de un umbral de capital humano. **Javorcik (2004, *AER*)**: spillovers verticales hacia proveedores locales. **Alfaro et al. (2004)**: hace falta desarrollo financiero.
- **Estimación propia** (`estimates.diffusion`, 1 099 obs., 1970-2005 en pasos de 5 años). Especificación: crecimiento anual del PIB pc a 10 años = 0,0013·gap − 0,0007·gap·m_core + **0,064·gap·IED/PIB** + EF de año. Errores estándar: 0,0008, 0,0039 y **0,013**. La brecha (gap) es ln(y_USA/y_i). La IED ayuda a converger. Las importaciones desde el centro no añaden convergencia en forma reducida. La convergencia incondicional es casi nula (≈ 0,1 %/año por unidad de gap). La literatura clásica (Barro-Sala-i-Martin) encuentra ≈ 2 %/año solo *condicional*.

### 2.5 Complejidad económica y crecimiento

- **Hidalgo y Hausmann (2009, *PNAS*)**, **Hausmann, Hidalgo et al. (2011/2014, *Atlas*)**: el ECI predice el crecimiento a 10 años mejor que la gobernanza, la educación o los índices de competitividad. Cuando el ingreso está por debajo del que "corresponde" a la complejidad, el crecimiento posterior es más rápido. **Hausmann, Hwang y Rodrik (2007)** llegan a un resultado análogo con EXPY. **Stojkoski et al. (2016)** y **Albeaik et al. (2017, ECI+)** confirman el poder predictivo con otras métricas.
- **Estimación propia** (`estimates.eci_growth`, 1 389 obs., t = 1965…2005). Crecimiento anual a 10 años = **0,0086·ECI** (EE 0,0009) − 0,0050·ln y (EE 0,0007) + EF de año, R² = 0,12. Una desviación típica de ECI (0,93) equivale a **≈ +0,8 pp/año** de crecimiento a igualdad de ingreso. El coeficiente implícito de convergencia condicional es del 0,5 %/año.

### 2.6 Rentas de monopolio

El parámetro `mu` (0,25) se ancla en **De Loecker y Eeckhout (2018)** y **De Loecker, Eeckhout y Unger (2020, *QJE*)**. El markup medio pasa de ≈ 1,1-1,2 (1980) a ≈ 1,6 (2016). La parte de renta en el precio (1 − 1/markup) va de 0,1 a 0,37, así que mu ∈ [0,15; 0,35] con valor central 0,25 es coherente.

---

## 3. Especificación recomendada para el modelo

### 3.1 Sustituir los pesos sintéticos `core²·G` por pesos de red

Hoy el drenaje se calcula como `drain = tau·o·G·(1−core)`, y el centro lo recibe en proporción a `wexp_n = core²G/Σcore²G`. Propuesta:

**(a) Matriz de cuotas de exportación S_ij(t)**, donde S_ij es la fracción de las exportaciones de i que van a j.

- *Modo histórico* (1950-2014): cuotas observadas de `comercio_dyadic.csv.gz` (media móvil de 3 años). Para 2015-2019 se mantiene la cuota de 2014.
- *Modo contrafactual*: gravedad con los parámetros de §2.1:

  S_ij ∝ G_j^0,84 · dist_ij^(−1,04) · exp(0,55·contig_ij + 0,57·lengua_ij + 1,04·colonia_ij), con Σ_j S_ij = 1.

  Las distancias están en `data/raw/comercio/cepii_dist.rda`. El exponente de G_i (0,99 ≈ 1) desaparece en las cuotas y se usa para el volumen total X_i = o_i·G_i. Rango para la calibración: exponente de distancia ∈ [−1,3; −0,75].

**(b) Drenaje bilateral con escala en la brecha de productividad** (efecto Penn):

  drain_ij = θ · X_i · S_ij · c_j(1−c_i) · max(0, (y_j / y_i)^β − 1)

  El término c_j(1−c_i) limita la transferencia a la relación centro-periferia; si se quiere el ERDI puro, se sustituye por 1[y_j > y_i]. Otros componentes:

  - **β = 0,20** (EE 0,004): elasticidad del nivel de precios del PIB al ingreso relativo, PWT 10.01 con EF de año (`estimates.penn_effect`). La literatura de sección cruzada da 0,25-0,35.
  - **θ** escala entre la cota superior ERDI (θ = 1, precios del PIB) y la cota inferior con precios de exportación (`drain_px`). Con `pl_x` no hay efecto Penn (β_x ≈ 0), así que el drenaje "puro de precios de transables" es pequeño. La razón px/ERDI de los datos es ≈ 0,45 en los años 50-60 y ≈ 0,08-0,11 desde 1990. **Recomendación: θ ∈ [0,1; 0,3], valor central 0,15**, que da un drenaje ≈ 2-4 % del PIB periférico en 1990-2010.
  - Lo recibido por j es Σ_i drain_ij. Esto sustituye a `drain_in = drain.sum·wexp_n`: el receptor pasa a ser el socio comercial real, y no el centro en proporción a core²G.

**(c) Rentas de monopolio sobre importaciones de alto valor**: `rent_m_in_j = mu · Σ_i foreign_m_i · M_ij`, donde M_ij es la cuota de importaciones de i procedentes de j (el traspuesto de la matriz diádica) ponderada por c_j. Así desaparece el reparto sintético `wexp_n`. mu = 0,25 ∈ [0,15; 0,35].

### 3.2 Objetivos de calibración del drenaje (periferia agregada, `estimates.drain_*_by_decade`)

| Década | ERDI: drenaje/PIB periferia (agregado; mediana) | ERDI: drenaje/exportaciones | px: drenaje/PIB (agregado; mediana) | px: drenaje/exportaciones | ERDI, miles de M USD/año |
|---|---|---|---|---|---|
| 1950 | 1,7 %; 1,6 % | 0,24 | 0,7 %; 0,03 % | 0,10 | 5 |
| 1960 | 3,0 %; 3,9 % | 0,40 | 1,4 %; 0,2 % | 0,19 | 13 |
| 1970 | 4,6 %; 5,2 % | 0,39 | 1,9 %; 0,8 % | 0,16 | 75 |
| 1980 | 10,6 %; 6,5 % | 0,76 | 1,6 %; 1,1 % | 0,11 | 335 |
| 1990 | 23,3 %; 16,8 % | 1,25 | 2,7 %; 1,7 % | 0,14 | 1 425 |
| 2000 | 24,6 %; 15,9 % | 0,85 | 1,9 %; 0,9 % | 0,07 | 3 131 |
| 2010 | 14,0 %; 11,0 % | 0,56 | 1,1 %; 0,4 % | 0,04 | 3 820 |

Nuestro ERDI de los años 2010 (≈ 3,8 billones USD corrientes al año) tiene el mismo orden de magnitud que Hickel et al. (2021), ≈ 2,2 billones USD de 2011 en 2015. Es algo mayor porque aquí toda exportación periferia→centro se revalúa, incluida la de China. Para el centro, el drenaje recibido tiene mediana ≈ 5-8 % del PIB con ERDI en 1990-2010 y ≈ 0,3-0,4 % con px.

**Objetivo recomendado para el modelo**: drenaje neto/PIB de la periferia ≈ 1,5-3 % (1960-1980), 2,5-5 % (1990-2000) y 1,5-3 % (2010), con la cota ERDI como techo. El valor actual τ = 0,03 sobre el output comerciado implica ≈ 1 % del PIB periférico (con o ≈ 0,3). Queda en el extremo bajo pero dentro del rango px, así que no es disparatado. La forma (b) añade la dependencia de la brecha y el pico de los años 80-90.

### 3.3 Difusión tecnológica

Especificación actual: `dln = g0 + gap·(kappa + kappa_m·embodied) + ruido + saltos`. Propuesta:

  dlnA_i = g0 + gap_i · (κ + κ_m · m_core,i + κ_f · FDI_i/G_i) + ε + saltos,
  con m_core,i = Σ_j M_ij c_j · imports_i / G_i.

- **κ** (difusión autónoma): la literatura de convergencia condicional pide 0,01-0,03 por unidad de gap en ln PTF. Los datos dan convergencia incondicional casi nula. Se recomienda κ ≈ 0,015 ∈ [0,005; 0,03] y dejar que los frenos de conflicto y de drenaje produzcan la falta de convergencia incondicional.
- **κ_m** (importaciones incorporadas): CHH (1997) da una elasticidad de la PTF de 0,058 al stock de I+D del Norte ponderado por maquinaria y de 0,279 a la cuota importadora. Traducido a nuestra forma, con m_core ≈ 0,17 y gap ≈ 1,5, κ_m ≈ 0,05-0,15. En forma reducida, nuestros datos no detectan efecto (−0,0007 ± 0,004 sobre el PIB). **Recomendación: bajar κ_m de 0,40 a ≈ 0,10 ∈ [0; 0,25]**. El valor actual, con `embodied` hasta 0,3, llega a +0,12 por unidad de gap, algo que ningún estudio respalda.
- **κ_f** (IED): estimación propia **0,064 (EE 0,013)** sobre el crecimiento del PIB pc. La literatura (Borensztein et al. 1998) condiciona el efecto al capital humano: se recomienda κ_f·min(1, hc/hc*) con hc* ≈ 2 (índice PWT). Con la IED media del 2,3 % del PIB, esto suma ≈ 0,0015/año por unidad de gap.
- **Localización geográfica** (opcional): m_core con peso exp(−dist/1 700 km) (semivida ≈ 1 200 km, Keller 2002).

**Saltos tecnológicos y ECI.** La tasa λ = lam0·√r·(0,5+asab) puede calibrarse con dos objetivos:

1. **Pendiente ECI→crecimiento**: la regresión simulada del crecimiento a 10 años sobre un "ECI simulado" (por ejemplo, el esfuerzo r acumulado estandarizado o la complejidad implícita ln A − ln A_F) y ln y debería dar ≈ 0,009 por DE de ECI (IC 95 % ≈ 0,007-0,010).
2. **Gradiente de patentes y de I+D**: las patentes de residentes por millón de habitantes tienen mediana ≈ 4 (1980), 13 (2000) y 10 (2010) en la periferia, frente a cientos en el centro (EE. UU. 783 en 2010, Corea más de 3 000). El gasto en I+D/PIB tiene mediana 0,56 %, EE. UU. 2,7 %. Esto sirve para fijar r_hist y la elasticidad de λ a r: el paso de r = 0,5 % a r = 2,5 % multiplica λ por ≈ √5 ≈ 2,2 con la forma √r actual.

### 3.4 Otros objetivos de calibración disponibles

- Cuota del comercio periférico con el centro: 0,73 (1950) → 0,49 (2010). El modelo debe reproducir la caída a medida que la periferia comercia más entre sí.
- Concentración de socios (HHI exportaciones, mediana periférica): 0,24 (1960) → 0,11 (2010).
- Apertura PWT mediana de la periferia: 0,20-0,26 (1950-1990) → 0,44 (2010). Puede sustituir a `o` como dato exógeno en el modo histórico.
- Términos de intercambio: deriva media ≈ 0 en 1950-2019 con ciclos de ±10-15 % en las medianas y ±30 % para exportadores primarios. Prebisch-Singer (−0,5 %/año) solo se ve en series largas de materias primas.

---

## 4. Lagunas y advertencias

1. **BACI/CEPII, Comtrade y Atlas diádico por producto** no son accesibles (dominios bloqueados). COW termina en 2014 y solo cubre bienes. Para 2015-2019 hay que extrapolar las cuotas de 2014.
2. **Concentración por producto** (HHI o Theil de UNCTAD/FMI): no hay datos. `hhi_*_partners` mide la concentración por socio, no por producto; el ECI es un sustituto parcial.
3. **Stocks bilaterales de IED (UNCTAD, CDIS)**: no se obtuvieron. Solo hay flujos WDI de país (1970+) y un proxy de stock por inventario perpetuo.
4. **`hightech_x_share`** solo cubre 2007+ en el fichero WDI disponible, y **`tot_wdi`** solo 1980-2011. Como sustituto se usa `tot_pwt`, que abarca 1950-2019.
5. Las series de **Hickel et al.** no están disponibles en bruto. `drain_erdi_*` es una reconstrucción propia con su método (usa el nivel de precios bilateral en vez del ERDI medio del Norte). `drain_px_*` es la alternativa conservadora. Conviene tratar ambas como cotas.
6. Los niveles de precios PWT tienen outliers (valores negativos o mayores que 10). Se ponen a NaN, igual que las cuotas `csh_x/csh_m` imposibles.
7. Las estimaciones propias (gravedad, ECI, difusión) son MCO simples sin agrupar los errores estándar. Sirven como objetivos de orden de magnitud, no para inferencia.

## Referencias

- Albeaik, S., Kaltenberg, M., Alsaleh, M., Hidalgo, C. (2017). Improving the Economic Complexity Index. arXiv:1707.05826.
- Alfaro, L., Chanda, A., Kalemli-Ozcan, S., Sayek, S. (2004). FDI and economic growth: the role of local financial markets. *JIE* 64.
- Amin, S. (1974). *Accumulation on a World Scale*. Monthly Review; (1976) *Unequal Development*.
- Arezki, R., Hadri, K., Loungani, P., Rao, Y. (2014). Testing the Prebisch-Singer hypothesis since 1650. *JIMF* 42.
- Barbieri, K., Keshk, O. (2016). Correlates of War Project Trade Data Set Codebook, v4.0.
- Borensztein, E., De Gregorio, J., Lee, J.-W. (1998). How does FDI affect economic growth? *JIE* 45.
- Coe, D., Helpman, E. (1995). International R&D spillovers. *EER* 39.
- Coe, D., Helpman, E., Hoffmaister, A. (1997). North-South R&D spillovers. *Economic Journal* 107; (2009) International R&D spillovers and institutions. *EER* 53.
- De Loecker, J., Eeckhout, J., Unger, G. (2020). The rise of market power. *QJE* 135.
- Emmanuel, A. (1972). *Unequal Exchange*. Monthly Review.
- Grilli, E., Yang, M. C. (1988). Primary commodity prices, manufactured goods prices and the terms of trade. *WBER* 2.
- Harvey, D., Kellard, N., Madsen, J., Wohar, M. (2010). The Prebisch-Singer hypothesis: four centuries of evidence. *REStat* 92.
- Hausmann, R., Hidalgo, C. et al. (2014). *The Atlas of Economic Complexity*. MIT Press.
- Hausmann, R., Hwang, J., Rodrik, D. (2007). What you export matters. *JEG* 12.
- Head, K., Mayer, T. (2014). Gravity equations: workhorse, toolkit, and cookbook. *Handbook of Int. Econ.* 4.
- Hickel, J., Sullivan, D., Zoomkawala, H. (2021). Plunder in the post-colonial era. *New Political Economy* 26(6).
- Hickel, J., Dorninger, C., Wieland, H., Suwandi, I. (2022). Imperialist appropriation in the world economy. *Global Environmental Change* 73.
- Hickel, J., Hanbury Lemos, M., Barbour, F. (2024). Unequal exchange of labour in the world economy. *Nature Communications* 15.
- Hidalgo, C., Hausmann, R. (2009). The building blocks of economic complexity. *PNAS* 106.
- Javorcik, B. (2004). Does FDI increase the productivity of domestic firms? *AER* 94.
- Keller, W. (2002). Geographic localization of international technology diffusion. *AER* 92; (2004) International technology diffusion. *JEL* 42.
- Köhler, G. (1998). The structure of global money and world tables of unequal exchange. *JWSR* 4(2).
- Mayer, T., Zignago, S. (2011). Notes on CEPII's distances measures: the GeoDist database. CEPII WP 2011-25.
- Ocampo, J. A., Parra-Lancourt, M. (2010). The terms of trade for commodities since the mid-19th century. *Revista de Historia Económica* 28.
- Santos Silva, J., Tenreyro, S. (2006). The log of gravity. *REStat* 88.
