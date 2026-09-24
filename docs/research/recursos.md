# Recursos naturales desagregados: datos, literatura y especificación recomendada

*Módulo:* `src/sources/recursos.py` → `data/processed/sources/recursos.csv`, `recursos_world.csv`,
`recursos_hubbert.csv`, `recursos_dict.json`. Crudos en `data/raw/recursos/` (el WDI completo, de 208 MB,
va a `data/raw/recursos/large/`, que git ignora; lo que se versiona es un extracto de 2,2 MB,
`wdi_recursos_subset.csv`).

Reconstrucción:

```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import recursos; recursos.build()"
```

La reconstrucción tarda unos 10 s con los crudos ya descargados. Sin ellos descarga unos 230 MB, desde
raw.githubusercontent.com y media.githubusercontent.com.

---

## 1. Resumen ejecutivo

1. **La inicialización actual del modelo no cuadra con los datos físicos.** Hoy el modelo toma
   `x0 = 0,41` (fracción ya extraída en 1950) y `r_R = 0,014`. Los datos dan otra cosa:
   - Petróleo: la fracción extraída mundial en 1950 es ≈ **0,02**. El URR *proxy* se define como la
     producción acumulada entre 1900 y 2019 más las reservas probadas de 2019.
   - Gas: ≈ 0,01. Carbón: ≈ 0,065.
   - Agregado fósil ponderado por valor (`fosil_x_valor`): 0,028 mundial y 0,006 de mediana por país.

   El URR *proxy* es una cota inferior. Con los URR de la literatura (GEA 2012, USGS 2000), la fracción
   de 1950 sería todavía menor. Solo hay unos pocos países maduros en 1950: GBR (0,24), DEU (0,17),
   JPN, CZE (carbón), USA (0,10) y ROU (0,19 en petróleo).
2. **La pendiente logística empírica es 4–6 veces mayor que la calibrada.**
   - Linealización de Hubbert por país: mediana de r ≈ **0,09** en petróleo (RIC 0,07–0,11), **0,10**
     en gas y **0,06** en carbón.
   - r condicionado al URR *proxy*: 0,077, 0,090 y 0,041.
   - A nivel mundial, un ajuste logístico no lineal da r = 0,062 (petróleo), 0,061 (gas) y 0,030
     (carbón).
3. **Hay que modelar los descubrimientos.** En 1950 solo se había descubierto el 18 % del EUR de los
   campos gigantes conocidos hoy (el 27 % en el caso del petróleo), y en 1980 el 75 %. La curva
   acumulada de descubrimientos de gigantes es logística, con r ≈ 0,09 y punto medio en 1960–1967,
   unos 35–40 años antes del punto medio de la producción (≈ 2000).
4. **Las nacionalizaciones se concentran en 1960–1980.**
   - Guriev, Kolotilin y Sonin (2011) cuentan 73 nacionalizaciones petroleras en 1960–2002.
   - La tabla curada de este módulo registra por década 3, 9, **25**, 3, 0, 5 y 1 eventos petroleros
     (de los años 50 a los 2010).
   - Un logit ilustrativo sobre el panel da el signo esperado para los *shocks* de precio
     (Δ3 ln p > 0), el tamaño del productor, la falta de democracia y el régimen anterior a 1985.
     Propongo con él una tasa de riesgo endógena que traslade capital extranjero a doméstico.

---

## 2. Datos obtenidos

### 2.1 Panel país-año (`recursos.csv`: 221 ISO3, 1950–2019, 65 variables)

| Bloque | Variables | Fuente | Cobertura |
|---|---|---|---|
| Producción física | `oil/gas/coal_prod_twh`, `fosil_prod_twh`, `oil_prod_mbep` | OWID energy-data (Energy Institute Statistical Review 1965–; Shift Project/Etemad-Luciani 1900–1964; EIA 1980–2016 para productores menores) | 1950: 45 países con petróleo >0, 54 con carbón; 2000: 94/70; en total 216 ISO3 |
| Marcas de relleno | `*_prod_relleno` | propio | series que acaban en 2014–2016, arrastradas hasta 2019 (≈50 productores pequeños) |
| Producción acumulada | `oil/gas/coal/fosil_cum_twh`, `oil_cum_gbep` | propio, acumulado desde 1900 | La producción de URSS, Checoslovaquia y Yugoslavia se reparte entre los estados sucesores con la cuota de los primeros años observados |
| Reservas probadas | `oil_reservas_twh`, `gas_reservas_twh` | Energy Institute (vía Gapminder systema_globalis), en tep | 1980–2020; 49 países (los que el EI lista individualmente) |
| Reservas de carbón | `coal_reservas_2013_mt`, `coal_reservas_2013_twh` | BP Statistical Review 2014 (WEC 2013) | corte transversal de 2013; 32 países |
| URR y fracción agotada | `*_urr_proxy_twh`, `*_x_proxy`, `fosil_valor_urr_proxy_musd2019`, `fosil_x_valor` | propio (acumulada 2019 + reservas) | ≈ 72 países productores |
| R/P | `oil_rp_anios`, `gas_rp_anios` | propio | 1980–2019 |
| Descubrimientos gigantes | `gigantes_n`, `gigantes_eur_mbep`, `gigantes_eur_petroleo_mbep`, `gigantes_eur_twh`, `gigantes_npv_pct_pib`, `gigantes_eur_cum_mbep` | Horn (2014) ampliado por Cust, Mihalyi y Rivera-Ballesteros (1.060 campos, 79 países, 1868–2019) | VPN en % del PIB, 1960–2017 |
| Rentas por recurso | `renta_{petroleo,gas,carbon,minerales,forestal,total}_pct_pib`, `renta_*_share`, `renta_no_renovable_pct_pib` | WDI (NY.GDP.PETR/NGAS/COAL/MINR/FRST/TOTL.RT.ZS), edición 2022 | 1970–2019; 172–194 países |
| Agotamiento (ahorro ajustado) | `agotamiento_{energia,minerales,forestal}_pct_rnb` | WDI NY.ADJ.D*.GN.ZS | 1970–2019 |
| Exportaciones | `export_combustibles_pct_merc`, `export_minerales_metales_pct_merc` | WDI TX.VAL.FUEL/MMTL.ZS.UN | 1962–2019 (irregular) |
| Extracción de materiales | `de_fosiles_t`, `de_metales_t`, `de_no_metalicos_t`, `de_biomasa_t` | UN IRP Global Material Flows Database | 1970–2019, ≈205 países (mena bruta en toneladas) |
| Nacionalizaciones | `nac_petroleo_share_post`, `nac_mineria_share_post`, `nac_evento_petroleo`, `nac_evento_mineria`, `estado_share_petroleo_eventos` | tabla curada `nacionalizaciones_curado.csv` (62 eventos 1937–2012, con nivel de confianza y fuente) | ver §2.4 |
| PIB | `pib_usd_corr` | WDI | 1960–2019 |

La cobertura exacta de cada variable (n, primer y último año, número de países) está en
`recursos_dict.json`.

### 2.2 Series mundiales (`recursos_world.csv`, 1850–2025)

- **Precio del crudo**, 1861–2021:
  - Nominal (`petroleo_precio_nominal_usd_bbl`), de BP/EI: 1861–1944 media de EE. UU., 1945–1983
    Arabian Light, 1984– Brent.
  - Real en US$ de 2019 (`petroleo_precio_real_usd2019_bbl`). El deflactor es el IPC de EE. UU.
    implícito en BP 2014 hasta 2013 y el IPC del WDI después.
- **Jacks (2019)**, 1850–2025:
  - 42 precios reales (1900 = 100): energía, metales, minerales y agrícolas.
  - 3 índices agregados, ponderados por el valor de producción de 1975 o de 2019, o con pesos
    iguales.
  - 3 subíndices: bienes cultivados, del subsuelo y del subsuelo sin energía.
- **Grilli–Yang** (actualización de Pfaffenzeller, Newbold y Rayner 2007), 1900–2011: índice general
  y de metales, MUV-G5, y sus versiones reales (GYCPI/MUV).
- **Pink Sheet del Banco Mundial**, en US$ reales de 2010, 1960–2025: crudo, carbón australiano, gas
  (EE. UU. y Europa), cobre, hierro, aluminio, oro, estaño, níquel y zinc.
- **USGS DS140**, 1900–2022: producción mundial de cobre, hierro, bauxita, aluminio, oro, plata,
  estaño, zinc, plomo, níquel y fosfato.
- **Energía mundial**: producción y producción acumulada de petróleo, gas y carbón en TWh (OWID).
- **Descubrimientos gigantes mundiales**: número de campos, EUR (total y de petróleo) y EUR acumulado.
- **Constantes** en `recursos_dict.json`: reservas, recursos y producción histórica mundial de GEA
  2012 (Rogner et al., tabla 7.1), en EJ.

### 2.3 Ajustes de Hubbert (`recursos_hubbert.csv`)

Hay 186 filas país × recurso, solo de productores con una producción acumulada de al menos 500 TWh
(≈ 0,3 Gbep). Cada fila recoge:

- Q de 1950 y de 2019, reservas, URR *proxy* y x en 1950 y en 2019.
- Linealización de Hubbert P/Q = r(1 − Q/URR), estimada por MCO en los años con Q ≥ 20 % de Q₂₀₁₉:
  r, URR y R².
- r condicionado al URR *proxy*: mediana de P/[Q(1 − Q/URR)] en 1965–2019.
- Año y nivel del pico de producción.

### 2.4 Tabla curada de nacionalizaciones

`data/raw/recursos/nacionalizaciones_curado.csv` recoge 62 eventos:

- 47 petroleros, 13 mineros o de carbón, 1 de reversión (Irán 1954) y 1 de privatización (GBR
  1982, excluida de los indicadores).
- Columnas: país, año, sector, tipo, participación estatal posterior, empresas afectadas,
  descripción, confianza (alta/media/baja) y fuente sugerida.

La tabla se compiló a partir de Kobrin (1984), Guriev et al. (2011), Mahdavi (2020) y Yergin (1991).
**No es la base original de ninguno de ellos**, que no se pudo descargar: contiene aproximadamente
dos tercios de los 73 eventos de GKS y **debe verificarse** contra sus apéndices antes de estimar
parámetros finales.

La variable `estado_share_petroleo_eventos` toma la participación estatal del último evento
registrado. Vale 0 cuando no hay evento, lo que **no** equivale a propiedad extranjera (por ejemplo,
USA, CAN o NOR).

### 2.5 Fuentes buscadas y no conseguidas

- **Producción minera por país y metal** (USGS Minerals Yearbook, BGS World Mineral Statistics): no
  están en espejos accesibles. En su lugar se usan la extracción de minerales metálicos de UN IRP
  (en toneladas de mena) y las rentas minerales del WDI.
- **Ross y Mahdavi, "Oil and Gas Data 1932–2014"** (Harvard Dataverse): no hay ningún espejo
  completo en GitHub.
- **Datos originales de Kobrin (1980, 1984), Minor (1994) y Guriev et al. (2011).** Tampoco los
  índices de propiedad estatal de Jones Luong y Weinthal (2010), ni las fechas de creación de NOC
  de Mahdavi (2020).
- **Reservas de carbón como serie temporal**, reservas de minerales por país (USGS MCS) y series de
  EROI.
- **Producción anterior a 1900.** Para el petróleo es despreciable: menos de 2 Gb en EE. UU. y
  Rusia. Para el carbón no lo es: unas 40 Gt, sobre todo de GBR, DEU, USA, FRA y BEL. Por eso la
  x del carbón en 1950 está infraestimada en esos países; GBR tendría ≈ 0,7 en lugar de 0,61.

---

## 3. Hechos estilizados que salen de los datos

### 3.1 Agotamiento mundial (URR *proxy* = acumulada 1900–2019 + reservas 2019)

| | URR *proxy* (TWh) | Equivalente | x 1950 | x 2019 | P/Q 1950 | P/Q 2019 | r logístico (ajuste NL) | Punto medio |
|---|---|---|---|---|---|---|---|---|
| Petróleo | 5,09 M | ≈ 3.000 Gbep | 0,020 | 0,46 | 0,059 | 0,022 | 0,062 | 1999,6 |
| Gas | 3,22 M | ≈ 1.900 Gbep | 0,009 | 0,39 | 0,071 | 0,032 | 0,061 | 2011,5 |
| Carbón | 6,74 M | ≈ 580 Gtep | 0,065 | 0,32 | 0,026 | 0,021 | 0,030 | 2030,6 (mal identificado) |

- La linealización mundial del petróleo en 1985–2019 da r = 0,044 y un URR de 4,4 M TWh ≈ 2.600 Gb.
  Es coherente con los 2.000–3.000 Gb de crudo convencional más LGN de Sorrell et al. (2010) y con
  la media de USGS (2000), unos 3.000 Gb.
- Es conocido que la linealización **infraestima** el URR y lo va desplazando al alza con el tiempo
  (Brandt 2007; Kaufmann y Cleveland 2001).
- En el carbón, el ajuste logístico mundial no está identificado (R² = 0,2): la producción sigue
  lejos del pico.

### 3.2 Parámetros logísticos por país (`recursos_hubbert.csv`)

| Recurso | n | r linealización (mediana, RIC) | r condicionado al URR *proxy* (mediana, RIC) | Maduros (x₂₀₁₉ > 0,6): r_lin / r_cond | r_cond ponderado por Q |
|---|---|---|---|---|---|
| Petróleo | 74 | 0,091 (0,067–0,110) | 0,077 (0,055–0,099) | 0,081 / 0,081 (n = 31) | 0,057 |
| Gas | 65 | 0,104 (0,083–0,149) | 0,090 (0,072–0,112) | 0,085 / 0,096 (n = 23) | 0,071 |
| Carbón | 47 | 0,063 (0,050–0,093) | 0,041 (0,022–0,060) | 0,060 / 0,047 (n = 9) | 0,042 |

Ejemplos de petróleo (r_lin, URR_lin en Gbep, año del pico):

| País | r_lin | URR_lin (Gbep) | Pico |
|---|---|---|---|
| GBR | 0,136 | 27 | 1999 |
| NOR | 0,157 | 29 | 2001 |
| MEX | 0,094 | 55 | 2004 |
| IDN | 0,092 | 26 | 1977 |
| USA | 0,052 | 270 (convencional + esquisto) | — |
| ARG | 0,060 | — | 1998 |

Los países de la OPEP, con la producción restringida por cuotas, dan R² bajos (SAU 0,38; KWT 0,35;
IRQ 0,13) y URR linealizados muy por debajo de sus reservas declaradas.

**Coincidencia con la literatura.** Brandt (2007), con 139 regiones:

- Encuentra perfiles a menudo asimétricos, más rápidos al subir que al bajar, y la curva logística
  simétrica no domina.
- Las pendientes de subida son del 5–10 % anual en regiones grandes y mayores en regiones pequeñas.

Otras referencias:

- Hubbert (1956) y Deffeyes (2001) estiman para el petróleo de los 48 estados contiguos de EE. UU.
  un r ≈ 0,05–0,06.
- Los ajustes *multi-Hubbert* (Nashawi, Malallah y Al-Bisharah 2010; Maggio y Cacciola 2012)
  suponen varios ciclos por país y dan URR mundiales de 2.200–3.000 Gb.
- Para el carbón, Patzek y Croft (2010) y Mohr y Evans (2009) ajustan pendientes menores
  (≈ 0,03–0,06) y URR muy inciertos por la reclasificación de reservas; el URR mundial de carbón
  que manejan es de 700–1.200 Gt.
- Mohr et al. (2015) dan URR fósiles por país: son la mejor referencia para cotejar
  `*_urr_proxy_twh`.

### 3.3 Descubrimientos

Campos gigantes descubiertos por década:

| Década | Campos | EUR (Gbep) |
|---|---|---|
| 1920 | 26 | 96 |
| 1930 | 51 | 152 |
| 1940 | 38 | 212 |
| 1950 | 93 | 366 |
| 1960 | 217 | 641 |
| 1970 | 223 | 617 |
| 1980 | 101 | 159 |
| 1990 | 92 | 182 |
| 2000 | 119 | 177 |
| 2010 | 68 | 221 (sobre todo gas en aguas profundas) |

- Ajuste logístico del EUR acumulado de los gigantes: U_D ≈ 2.700 Gbep, r_D ≈ 0,087 y t_m ≈ 1967.
  Solo petróleo: 1.570 Gb, r_D ≈ 0,088 y t_m ≈ 1959.
- Es el "*creaming*" clásico: el tamaño medio del descubrimiento cae con el esfuerzo acumulado
  (Arps y Roberts 1958; Kaufmann y Cleveland 2001; Bentley 2002).
- Los gigantes suponen ≈ 60 % del URR convencional (Horn 2011; Höök et al. 2009).

### 3.4 Precios

Tendencia de ln(precio real), en % anual, y volatilidad (sd de Δln, 1900–2019):

| Serie | Tendencia 1900–2019 | Tendencia 1950–2019 | sd Δln |
|---|---|---|---|
| Petróleo (BP/EI, real) | +1,13 | +2,54 | 0,24 |
| Petróleo (Jacks) | +1,22 | +1,70 | 0,22 |
| Gas (Jacks) | +1,33 | +2,73 | 0,17 |
| Carbón (Jacks) | +0,64 | +0,47 | 0,16 |
| Cobre | −0,27 | −0,20 | 0,19 |
| Hierro | +0,30 | −0,31 | 0,16 |
| Estaño | −0,05 | −0,78 | 0,20 |
| Subsuelo (Jacks) | +0,90 | +1,23 | 0,17 |
| Subsuelo sin energía | +0,09 | −0,04 | 0,12 |
| Cultivados | −0,51 | −1,11 | 0,10 |
| Índice agregado (VP 1975) | +0,42 | +0,54 | 0,13 |

- Precio real del crudo (US$ de 2019/bbl): 36 en 1900, **18 en 1950**, 12 en 1970, 60 en 1974,
  114 en 1980, 34 en 1986, 20 en 1998, 116 en 2008 y 64 en 2019.
- El GYCPI real (materias primas frente a manufacturas) cae de 132 en 1900 a 63 en 1998: es la
  evidencia de Prebisch–Singer para bienes mayormente cultivados (Grilli y Yang 1988; Harvey et al.
  2010).
- Jacks (2019) destaca la subida de largo plazo de los precios reales de la energía, la ausencia de
  tendencia en los metales y los superciclos de 20–70 años (1890–1917, 1930–1951, 1960s–1970s,
  2000s). Coincide con Erten y Ocampo (2013).

### 3.5 Rentas (1970–2019, media ponderada por PIB, % del PIB mundial)

| Petróleo | Gas | Carbón | Minerales | Forestal | Total |
|---|---|---|---|---|---|
| 1,73 | 0,28 | 0,27 | 0,28 | 0,19 | 2,75 |

El petróleo supone ≈ 63 % de las rentas mundiales. El recurso genérico del modelo es, en esencia,
petróleo con algo de gas.

---

## 4. Literatura (síntesis)

### 4.1 Hubbert, URR y agotamiento

- **Hubbert (1956)** introduce la curva logística de la producción acumulada, Q(t) = URR/(1 + e^{−r(t−t_m)}),
  cuya producción P = rQ(1 − Q/URR) es simétrica.
- **Deffeyes (2001)** populariza la linealización P/Q = r − (r/URR)·Q.
- **Brandt (2007)**, *Testing Hubbert* (Energy Policy 35), muestra que:
  - la forma simétrica no es universal;
  - la subida suele ser más rápida que la bajada;
  - en unidades pequeñas la curva es más apuntada.
- **Sorrell, Speirs, Bentley, Brandt y Miller (2010)** (UKERC, Energy Policy 38) revisan las
  estimaciones de URR y de fechas de pico:
  - URR convencional de 2.000–4.000 Gb;
  - pico convencional antes de 2030 como riesgo significativo.
- **Rogner (1997)** y **Rogner et al. (2012, GEA cap. 7)** distinguen producción histórica,
  reservas, recursos y ocurrencias adicionales. A 2005, en EJ:

| Recurso | Producción histórica | Reservas | Recursos |
|---|---|---|---|
| Petróleo convencional | 6.069 | 4.900–7.610 | 4.170–6.150 |
| Gas convencional | 3.087 | 5.000–7.100 | 7.200–8.900 |
| Carbón | 6.712 | 17.300–21.000 | 291.000–435.000 |
| Petróleo no convencional | 513 | 3.750–5.600 | 11.280–14.800 |

  Implicaciones: el URR convencional de petróleo es de 15.000–20.000 EJ, es decir, ≈ 2.500–3.300 Gb,
  y x₂₀₀₅ ≈ 0,3–0,4.
- **McGlade y Ekins (2015)**, en *Nature*, publican reservas y recursos por región y la "carbono no
  quemable".
- **Mohr et al. (2015)**, en *Fuel*, proyectan los fósiles por país con URR estándar.
- **Crecimiento de reservas**: las reservas iniciales se revisan al alza un 30–70 % en décadas por
  la mejora del factor de recobro (Morehouse 1997; Klett y Schmoker 2003). Para pasar del URR
  *proxy* a un URR de largo plazo en el petróleo, el factor g ≈ 1,3–1,5 es razonable.

### 4.2 EROI y costes crecientes

- **Cleveland (2005)** y **Hall, Lambert y Balogh (2014)** (Energy Policy 64): el EROI del petróleo
  y el gas de EE. UU. pasa de ≈ 100:1 en los años 30 a ≈ 30:1 en los 70 y ≈ 11–18:1 en los 2000.
- **Gagnon, Hall y Brinker (2009)**: el EROI mundial del petróleo y el gas cae de ≈ 35:1 en 1999 a
  ≈ 18:1 en 2006.
- **Court y Fizaine (2017)** (Ecological Economics) estiman EROI mundiales de largo plazo con máximo
  a mediados del siglo XX y declive posterior.
- La degradación de las leyes minerales (cobre: ≈ 1,7 % en 1990 frente a ≈ 1,5 % en 2016, según
  Calvo et al. 2016 y Mudd 2010; ver `oregrades_bergsorensen.csv`) es el análogo para los metales.

**Implicación para el modelo:** el coste de capital por unidad de capacidad, c_R, debería crecer con
la fracción agotada.

### 4.3 Hotelling frente a los precios empíricos

- **Hotelling (1931)** predice un precio neto que crece al tipo de interés.
- La evidencia no lo apoya como descripción de los precios observados (Krautkraemer 1998, JEL;
  Livernois 2009, REEP):
  - Slade (1982) encuentra trayectorias en forma de U;
  - Pindyck (1999) documenta tendencias con reversión a la media y rupturas.
- Los descubrimientos, el progreso técnico y la estructura de mercado dominan: la OPEP desde 1973
  (Hamilton 2009; Kilian 2009, *shocks* de demanda).
- Los precios de largo plazo muestran superciclos más tendencias débiles:
  - positivas en energía, nulas o negativas en metales y cultivos;
  - Grilli y Yang (1988); Pfaffenzeller et al. (2007); Harvey, Kellard, Madsen y Wohar (2010,
    REStat); Jacks (2019).

**Recomendación:** el precio mundial del modelo es de equilibrio (clearing). No conviene imponer
Hotelling; sí validar contra los objetivos de §5.6.

### 4.4 Maldición de los recursos

- **Sachs y Warner (1995, 2001)**: las exportaciones de recursos en % del PIB tienen efecto negativo
  sobre el crecimiento.
- **Mehlum, Moene y Torvik (2006)**: el efecto depende de las instituciones.
- **Brunnschweiler y Bulte (2008)**: la dependencia es endógena; la abundancia en sí no daña.
- **Ross (2001, 2012, 2015)**: el petróleo refuerza el autoritarismo y los conflictos, sobre todo
  tras las nacionalizaciones de los años 70, cuando las rentas pasan al Estado.
- **Haber y Menaldo (2011)** discuten ese efecto sobre el autoritarismo.
- **van der Ploeg (2011, JEL)** hace la síntesis: enfermedad holandesa, volatilidad, búsqueda de
  rentas y "voracidad".
- **Evidencia cuasiexperimental con descubrimientos gigantes:**
  - Arezki, Ramey y Sheng (2017, QJE): el descubrimiento es un *shock* de noticias; la cuenta
    corriente cae, la inversión sube y el PIB crece a partir de ≈ 5 años.
  - Lei y Michaels (2014, JDE): un gigante eleva la incidencia de conflicto armado 5–8 puntos en
    4–8 años.
  - Tsui (2011, EJ): reducción de la democracia.
  - Cust y Mihalyi (2017): la "maldición previa" (*presource curse*), con decepción de crecimiento
    tras el descubrimiento en países con malas instituciones.
  - Smith (2015, JDE): efecto positivo sobre el PIB per cápita.

**Implicación para el modelo:** con `phi_R` (captura por las élites) y `nu_a` ya representados,
`gigantes_npv_pct_pib` sirve como variable de *shock* exógeno para validar las respuestas del
modelo a los descubrimientos.

### 4.5 Propiedad extranjera, nacionalizaciones y participación del gobierno anfitrión

**Por épocas** (Penrose 1968; Yergin 1991; Mahdavi 2020; Victor, Hults y Thurber 2012):

- **1950–1960: las "siete hermanas".** Exxon, Mobil, Socal, Texaco, Gulf, BP y Shell controlaban
  ≈ 85–90 % de la producción del mundo no comunista fuera de EE. UU.
  - El régimen fiscal era de concesiones a 50–75 años, regalía del 12,5 % y, desde Venezuela
    (1943/1948) y Arabia Saudí (1950), un reparto 50/50 de beneficios.
  - La participación del gobierno anfitrión (*government take*) rondaba el 50 %.
  - Hubo excepciones de propiedad estatal plena: México (1938) y la URSS. Irán (1951) quedó
    revertido de facto en 1954.
- **1960–1980: ola de nacionalizaciones.** Creación de la OPEP (1960), Resolución 1803 de la ONU
  (1962), Teherán-Trípoli (1971, reparto 55/45) y el Acuerdo General de Participación (1972): 25 %
  en 1973, 60 % en 1974 y 100 % hacia 1980.
  - Kobrin (1984) cuenta ≈ 560 actos de expropiación en 79 países en desarrollo entre 1960 y 1979,
    con máximo en 1974–1975.
  - Según Kobrin, "la nacionalización del petróleo, la minería y los servicios públicos estaba
    prácticamente completa hacia 1975".
  - Guriev et al. (2011) cuentan 73 nacionalizaciones petroleras entre 1960 y 2002.
- **1980–2000: ciclo inverso.**
  - Casi no hay expropiaciones (Minor 1994).
  - Hay privatizaciones: GBR 1979–1987, ARG 1993, PER y BOL en los 90.
  - Se imponen los contratos de reparto de producción (PSC) y de servicios.
  - La participación del gobierno anfitrión se sitúa en el 60–85 % para el petróleo y el 40–60 %
    para la minería (Johnston 1994/2003; Daniel, Keen y McPherson 2010, FMI).
- **2000–2012: "nacionalismo de recursos" con precios altos.** Rusia (Yukos 2004, Sajalín 2006),
  Venezuela (2007), Bolivia (2006), Ecuador (2006) y Argentina (YPF 2012).
  - Chang, Hevia y Loayza (2010) documentan ciclos de privatización y nacionalización ligados a los
    precios.
  - Hajzler (2012) cuenta las expropiaciones de 1993–2006.
- **Situación actual.** Las compañías petroleras nacionales (NOC) controlan ≈ 75–90 % de las
  reservas probadas y ≈ 55–60 % de la producción mundial.

**Determinantes:**

- Guriev et al. (2011) encuentran que la probabilidad de nacionalizar sube con el precio del
  petróleo y baja con las restricciones al ejecutivo y el capital humano. Su modelo lo explica por
  la falta de compromiso del gobierno frente a la empresa extranjera.
- Stroebel y van Benthem (2013) modelan contratos de extracción bajo amenaza de expropiación.
- Mahdavi (2014, 2020) atribuye las nacionalizaciones a líderes que buscan control político.
- Jones Luong y Weinthal (2010) sostienen que la maldición opera por la estructura de propiedad
  (estatal frente a privada, doméstica frente a extranjera), no por el petróleo en sí.

---

## 5. Especificación y parámetros recomendados

La notación es la del modelo: U (URR), X (extracción acumulada), x = X/U,
Cap = r_R·U·(x + ε)·(1 − x) y extracción = Cap·(1 − e^{−e}).

### 5.1 Recurso genérico = agregado fósil ponderado por valor (más minerales vía rentas)

Para cada país *i* y recurso *k* ∈ {petróleo, gas, carbón}, con precios de 2019 por TWh
p = (37,8; 17,1; 11,2) M US$/TWh:

$$U_i = \sum_k p_k \, g_k \, (Q_{ik,2019} + R_{ik,2019}), \qquad X_{i,1950} = \sum_k p_k\, Q_{ik,1950}$$

- **Crecimiento de reservas:** g = 1 da `fosil_valor_urr_proxy_musd2019` (cota inferior).
  Recomiendo g_petróleo ≈ 1,4 (rango 1,2–1,7), g_gas ≈ 1,3 y g_carbón = 1. Con esos valores, la suma
  mundial del petróleo alcanza ≈ 3.500–4.000 Gbep, en línea con GEA/USGS más algo de no convencional.
- **Minerales:** no hay URR por país. Se añade un componente mineral U_i^min, inferido como ahora de
  `renta_minerales_pct_pib` con x₀^min ≈ 0,2 (±0,1). Ese valor sale de los metales básicos:
  producción acumulada frente a producción acumulada más reservas del USGS MCS (cobre ≈ 0,3,
  hierro ≈ 0,2).
- **Escala:** las unidades de U deben seguir anclándose a las rentas observadas, como hace hoy
  `rescale`. Lo que aportan los datos físicos es x_i, la forma relativa entre países y la dinámica.

### 5.2 Fracción agotada inicial

$$x_{i,1950} = \frac{X_{i,1950}}{U_i}$$

- **Valor central:** `fosil_x_valor[1950]` dividido por g, lo que aproximadamente divide por ≈ 1,35
  la parte de petróleo y gas.
- **Distribución:** mediana 0,006, media ponderada por URR 0,028, máximo GBR 0,24 (0,3 corrigiendo
  el carbón anterior a 1900).
- **Países sin producción fósil significativa:** x₀ = 0,02 más el componente mineral.
- **Incertidumbre:** ±50 % relativo. Es una cota superior, porque URR mayores bajan x.
- **Implicación:** el `x0 = 0,41` común está fuera del intervalo de los datos para cualquier país
  salvo GBR (carbón) y quizá JPN. Si se mantiene para ajustar las rentas de 1970–2019, conviene
  reinterpretarlo como la fracción del URR *conocido* en 1950, no del URR final (ver §5.4).

### 5.3 Pendiente logística y ε

| Recurso | r_R central | Rango (≈ RIC por país) | Nota |
|---|---|---|---|
| Petróleo | 0,08 | 0,055–0,11 | los países maduros convergen a 0,08 |
| Gas | 0,09 | 0,07–0,12 | |
| Carbón | 0,045 | 0,02–0,065 | URR mal identificado |
| **Agregado por valor (petróleo 70 %, gas 20 %, carbón 10 %)** | **0,075** | 0,055–0,10 | |

- **Relación con el factor de esfuerzo.** Con (1 − e^{−e₀}) ≈ 0,70, el r efectivo del modelo es
  0,075 × 0,7 ≈ 0,053. Coincide con la pendiente mundial observada (0,044–0,062), que es menor que
  la mediana por país porque agrega curvas desfasadas y porque la OPEP restringe la producción.
- **ε (EPS_X = 0,05).** Con x₀ ≈ 0,02–0,03, ε = 0,05 triplica la capacidad inicial. Recomiendo
  **ε ≈ 0,005–0,01**, o sustituirlo por el proceso de descubrimientos de §5.4.
- **Comprobación con el mundo en 1950:**
  - Datos: P/URR ≈ 0,0012 al año.
  - Modelo con r = 0,075, x₀ = 0,025, ε = 0,01 y factor 0,7: 0,075·0,035·0,975·0,7 ≈ 0,0018 (del
    orden correcto).
  - Configuración actual (r = 0,014, x₀ = 0,41, ε = 0,05): ≈ 0,0027 y una dinámica casi plana.
- **Validación:** años de pico por país.

| País | Pico |
|---|---|
| USA (convencional) | 1970 |
| VEN | 1970 |
| LBY | 1970 |
| IRN | 1974 |
| IDN | 1977 |
| GBR | 1999 |
| NOR | 2001 |
| MEX | 2004 |
| DZA | 2007 |
| NGA | 2010 |

  Con r ≈ 0,08, la distancia entre x = 0,02 y el pico (x = 0,5) es ln(49)/0,08 ≈ 49 años.
  Encaja con los productores que empezaron en los años 50 y alcanzaron el pico hacia 2000.

**Costes crecientes (EROI).** Propongo c_R(x) = c_R0·(1 − x)^{−γ}, con γ ≈ 0,5–1. Así, el capital
por unidad de capacidad se duplica al pasar de x = 0 a x ≈ 0,6–0,75, en línea con la caída del EROI
de ≈ 30–40 a ≈ 15 (Hall et al. 2014).

### 5.4 Proceso de descubrimientos

Se separan el URR geológico final U_i y el conocido K_i(t) ≤ U_i. La capacidad se calcula sobre
K_i, con x = X/K.

**Opción determinista (mínima):**

$$\dot K_i = r_D \, s_i(t)\, K_i\left(1-\frac{K_i}{U_i}\right) \quad\text{o}\quad K_i(t) = \frac{U_i}{1+e^{-r_D (t-t_{m,i})}}$$

- r_D ≈ 0,09 (rango 0,07–0,11), a partir del ajuste logístico del EUR acumulado de los gigantes.
- t_m ≈ 1963 en el mundo. Por país, t_m,i se toma del año mediano ponderado por EUR de
  `gigantes_eur_mbep` (Oriente Medio ≈ 1950–1965; mar del Norte ≈ 1970; África occidental en aguas
  profundas ≈ 1995–2005).
- **Condición inicial:** K_i(1950)/U_i ≈ 0,2–0,3 en el mundo (0,177 del EUR de gigantes; 0,27 en
  petróleo).
- El término s_i(t) ≥ 0 permite que el esfuerzo exploratorio dependa del capital de extracción
  (doméstico más concesiones extranjeras): la exploración extranjera fue decisiva hasta 1970.

**Opción estocástica** (coherente con el carácter de agentes del modelo):

- Llegadas de descubrimientos gigantes según un proceso de Poisson con tasa
  λ_i(t) = λ₀·(explorac_i)·(1 − K_i/U_i).
- Tamaño lognormal con media decreciente en K_i/U_i (*creaming*). Mediana del EUR ≈ 1.000 Mbep y
  σ_ln ≈ 1,0 (ajustables con `giant_fields_2018.csv`).
- **Objetivos:** 1.060 gigantes en 79 países entre 1868 y 2019, perfil por décadas de §3.3,
  VPN/PIB del descubrimiento (Arezki et al. 2017) y respuesta del PIB y el conflicto.

### 5.5 Tasa de riesgo de nacionalización (propiedad extranjera → doméstica)

Especificación logit por país-año, solo mientras exista capital extranjero de extracción KR_f > 0:

$$h_{it} = \Lambda\left(\beta_0 + \beta_1 \Delta_3 \ln p_{t-1} + \beta_2 \ln p_{t-1} + \beta_3 \ln(1+\text{prod}_{it}) + \beta_4\, \text{dem}_{it} + \beta_5\, \mathbb{1}[t\ge 1985] + \beta_6\, \text{asabiya}_{it}\right)$$

Estimación ilustrativa con el panel y la tabla curada: productores con producción máxima > 50 TWh,
1955–2019, 3.354 observaciones y 33 eventos, excluidos los años posteriores a una nacionalización
total.

| Variable | Coef. | EE | p |
|---|---|---|---|
| Δ3 ln p_{t−1} | **+1,54** | 0,54 | 0,005 |
| ln p_{t−1} | −1,08 | 0,45 | 0,017 |
| ln(1 + prod TWh) | **+0,40** | 0,09 | <0,001 |
| polity2 | **−0,061** | 0,028 | 0,026 |
| post-1985 | **−1,55** | 0,73 | 0,034 |
| constante | −2,96 | 1,39 | 0,033 |

- **Tasas base:** 1,8 % anual antes de 1985 y 0,18 % después.
- **Lectura:** lo que dispara las nacionalizaciones son los **shocks** de precio (subidas
  recientes), no el nivel. El coeficiente negativo del nivel recoge que los precios altos de
  1980–2014 llegaron cuando la mayoría ya había nacionalizado. Coincide con Guriev et al. (2011) y
  con Chang et al. (2010).
- Con 33 eventos, los intervalos son amplios. **Hay que reestimar con la base completa de GKS
  antes de fijar parámetros.**

**En el modelo:**

1. Si ocurre el evento, se transfiere una fracción θ del capital extranjero al doméstico: θ ≈ 0,5
   en los casos de participación del 51–60 % y θ = 1 en los de nacionalización total. La tabla
   registra `participacion_estatal_post`.
2. Se paga una compensación κ ≈ 0,2–0,5 del valor contable. En el acuerdo YPF–Repsol fue ≈ 5.000 M
   US$ en bonos; los laudos del CIADI suelen quedarse en el 30–60 % de lo reclamado.
3. Se aplica una penalización a la entrada de concesiones nuevas durante 5–10 años. Es el
   mecanismo de Stroebel y van Benthem: sube el riesgo percibido y baja la regalía que el
   extranjero acepta pagar.

El `nu_a` actual (resistencia de la asabiya a las concesiones) puede entrar como β₆.

**Objetivos de calibración:**

- 73 ± 10 nacionalizaciones petroleras en 1960–2002 (GKS).
- Unos 25–35 eventos petroleros en 1970–1979 (≈ 50–60 % del total).
- Casi ninguno en 1985–1999.
- Repunte moderado (5–8) en 2004–2012.
- Hacia 1980, la participación de las NOC en la producción de la OPEP debe acercarse a 0,9, y la
  participación extranjera en la producción no comunista fuera de Norteamérica, a ≈ 0,3.

### 5.6 Participación del gobierno anfitrión (`roy`)

El `roy = 0,30` fijo infravalora lo que retiene el país anfitrión en todas las épocas. Recomiendo
que dependa de la época o que sea endógeno (negociación con el poder del anfitrión):

| Periodo | *Government take* típico (petróleo) | Minería |
|---|---|---|
| 1950–1959 | 0,50 (reparto 50/50) | 0,30–0,45 |
| 1960–1970 | 0,50–0,60 | 0,40 |
| 1971–1980 | 0,55 → 0,85+ (participación) | 0,50–0,60 |
| 1981–2000 | 0,60–0,80 (PSC) | 0,40–0,55 |
| 2001–2019 | 0,65–0,85 | 0,40–0,60 |

Fuentes: Johnston (2003); Daniel, Keen y McPherson (2010); Mahdavi (2020). Una especificación
parsimoniosa: roy_it = roy₀ + (roy₁ − roy₀)·(participación estatal acumulada del país), con
roy₀ ≈ 0,5 y roy₁ ≈ 0,85.

### 5.7 Objetivos de calibración y validación

| Objetivo | Valor | Fuente |
|---|---|---|
| x fósil mundial por valor, 1950 → 2019 | 0,028 → 0,415 (URR *proxy*; con g ≈ 1,35, ≈ 0,02 → 0,31) | `recursos.csv` |
| x petróleo mundial, 1950 → 2019 | 0,020 → 0,46 | ídem |
| P/Q mundial, petróleo, 1950 / 2019 | 0,059 / 0,022 | `recursos_world.csv` |
| Crecimiento de la producción mundial de petróleo, 1950–1973 | ≈ 7,7 % anual | ídem |
| Crecimiento de la producción mundial de petróleo, 1973–2019 | ≈ 1,0 % anual | ídem |
| Mediana de r por país (petróleo/gas/carbón) | 0,08 / 0,09 / 0,045 | `recursos_hubbert.csv` |
| Años de pico por país | ver §5.3 | ídem |
| EUR de gigantes descubierto en 1950 / 1980 | 18 % / 75 % | `recursos_world.csv` |
| Rentas petroleras/totales (% del PIB mundial, 1970–2019) | 1,73 / 2,75 | WDI |
| Precio real del crudo (US$ 2019): 1950 / 1974 / 1980 / 1998 / 2008 / 2019 | 18 / 60 / 114 / 20 / 116 / 64 | BP/EI |
| Volatilidad anual de Δln p del crudo | 0,22–0,24 | ídem |
| Tendencia del precio real de la energía (1900–2019) | +1,1 a +1,3 % anual | Jacks |
| Tendencia del precio real de los metales (1900–2019) | ≈ 0 | Jacks |
| Nacionalizaciones petroleras 1960–2002 | 73 | GKS 2011 |

---

## 6. Advertencias y trabajo pendiente

1. **El URR *proxy* es una cota inferior**, porque ignora el crecimiento de reservas y los
   descubrimientos futuros. Además, las reservas de la OPEP de 1985–1990 incluyen revisiones
   "políticas" al alza (Kuwait, Emiratos, Irán, Irak, Venezuela y Arabia Saudí suman ≈ +300 Gb sin
   descubrimientos). Conviene contrastarlas con el EUR de los gigantes y con Mohr et al. (2015).
2. **Venezuela y Canadá** incluyen crudo extrapesado y arenas bituminosas en las reservas, lo que da
   x bajas. Para el recurso "convencional" conviene restar ≈ 220 Gb (VEN, Orinoco) y ≈ 160 Gb (CAN).
3. **Estados sucesores de la URSS.** El reparto se hace con la cuota de 1985–1987, lo que
   infraestima el petróleo histórico de Azerbaiyán: Bakú era ≈ 40 % del petróleo soviético en 1950.
4. **Carbón:** solo hay reservas de 2013 y falta la producción anterior a 1900.
5. **Productores menores:** sus series de 2017–2019 están arrastradas desde 2016
   (`*_prod_relleno = 1`).
6. **Tabla de nacionalizaciones:** es parcial y curada a mano. Hay que ampliarla con GKS (73
   eventos), Kobrin/Minor (todos los sectores) y Hajzler (2012), y convendría añadir las fechas de
   creación de NOC (Mahdavi 2020).
7. **Falta una serie de participación extranjera en la extracción por país.** Solo se infiere de los
   eventos. Candidatos: Jones Luong y Weinthal (2010), con tipos de propiedad para 50 países
   productores entre 1900 y 2005, y la base NOC del NRGI.
8. **Minerales por país:** solo hay toneladas de mena (UN IRP, 1970–) y rentas. La producción por
   metal y país (BGS/USGS) sigue pendiente.

---

## Referencias

- Arezki, R., Ramey, V. A. y Sheng, L. (2017). News shocks in open economies: evidence from giant oil discoveries. *QJE* 132(1).
- Arps, J. J. y Roberts, T. G. (1958). Economics of drilling for Cretaceous oil on east flank of Denver-Julesburg basin. *AAPG Bulletin* 42.
- Bentley, R. W. (2002). Global oil & gas depletion: an overview. *Energy Policy* 30.
- Brandt, A. R. (2007). Testing Hubbert. *Energy Policy* 35(5).
- Brunnschweiler, C. y Bulte, E. (2008). The resource curse revisited and revised. *JEEM* 55(3).
- Calvo, G., Mudd, G., Valero, A. y Valero, A. (2016). Decreasing ore grades in global metallic mining. *Resources* 5(4).
- Chang, R., Hevia, C. y Loayza, N. (2010/2018). Privatization and nationalization cycles. NBER WP 16126; *Macroeconomic Dynamics* 22(2).
- Cleveland, C. J. (2005). Net energy from the extraction of oil and gas in the United States. *Energy* 30.
- Court, V. y Fizaine, F. (2017). Long-term estimates of the energy-return-on-investment (EROI) of coal, oil, and gas global productions. *Ecological Economics* 138.
- Cust, J. y Mihalyi, D. (2017). Evidence for a presource curse? World Bank PRWP 8140. Datos: Cust, Mihalyi y Rivera-Ballesteros, *Giant oil and gas field discoveries* (GitHub, 2019).
- Daniel, P., Keen, M. y McPherson, C. (eds.) (2010). *The Taxation of Petroleum and Minerals*. FMI/Routledge.
- Deffeyes, K. (2001). *Hubbert's Peak*. Princeton UP.
- Erten, B. y Ocampo, J. A. (2013). Super cycles of commodity prices since the mid-nineteenth century. *World Development* 44.
- Gagnon, N., Hall, C. A. S. y Brinker, L. (2009). A preliminary investigation of energy return on energy investment for global oil and gas production. *Energies* 2.
- Grilli, E. y Yang, M. C. (1988). Primary commodity prices, manufactured goods prices, and the terms of trade of developing countries. *WBER* 2(1).
- Guriev, S., Kolotilin, A. y Sonin, K. (2011). Determinants of nationalization in the oil sector: a theory and evidence from panel data. *JLEO* 27(2), 301–323.
- Haber, S. y Menaldo, V. (2011). Do natural resources fuel authoritarianism? *APSR* 105(1).
- Hajzler, C. (2012). Expropriation of foreign direct investments: sectoral patterns from 1993 to 2006. *Review of World Economics* 148.
- Hall, C. A. S., Lambert, J. G. y Balogh, S. B. (2014). EROI of different fuels and the implications for society. *Energy Policy* 64.
- Hamilton, J. D. (2009). Understanding crude oil prices. *Energy Journal* 30(2).
- Harvey, D. I., Kellard, N. M., Madsen, J. B. y Wohar, M. E. (2010). The Prebisch-Singer hypothesis: four centuries of evidence. *REStat* 92(2).
- Höök, M., Hirsch, R. y Aleklett, K. (2009). Giant oil field decline rates and their influence on world oil production. *Energy Policy* 37.
- Horn, M. K. (2011/2014). Giant oil and gas fields of the world. AAPG Datapages.
- Hotelling, H. (1931). The economics of exhaustible resources. *JPE* 39(2).
- Hubbert, M. K. (1956). Nuclear energy and the fossil fuels. API Drilling and Production Practice.
- Jacks, D. S. (2019). From boom to bust: a typology of real commodity prices in the long run. *Cliometrica* 13(2). Datos actualizados a 2025.
- Johnston, D. (1994/2003). *International Petroleum Fiscal Systems and Production Sharing Contracts*. PennWell.
- Jones Luong, P. y Weinthal, E. (2010). *Oil Is Not a Curse*. Cambridge UP.
- Kaufmann, R. K. y Cleveland, C. J. (2001). Oil production in the lower 48 states: economic, geological, and institutional determinants. *Energy Journal* 22(1).
- Kilian, L. (2009). Not all oil price shocks are alike. *AER* 99(3).
- Klett, T. R. y Schmoker, J. W. (2003). Reserve growth of the world's giant oil fields. AAPG Memoir 78.
- Kobrin, S. J. (1980). Foreign enterprise and forced divestment in LDCs. *International Organization* 34(1).
- Kobrin, S. J. (1984). Expropriation as an attempt to control foreign firms in LDCs: trends from 1960 to 1979. *ISQ* 28(3).
- Krautkraemer, J. (1998). Nonrenewable resource scarcity. *JEL* 36(4).
- Lei, Y.-H. y Michaels, G. (2014). Do giant oilfield discoveries fuel internal armed conflicts? *JDE* 110.
- Livernois, J. (2009). On the empirical significance of the Hotelling rule. *REEP* 3(1).
- Maggio, G. y Cacciola, G. (2012). When will oil, natural gas, and coal peak? *Fuel* 98.
- Mahdavi, P. (2014). Why do leaders nationalize the oil industry? *Energy Policy* 75; (2020). *Power Grab: Political Survival through Extractive Resource Nationalization*. Cambridge UP.
- McGlade, C. y Ekins, P. (2015). The geographical distribution of fossil fuels unused when limiting global warming to 2 °C. *Nature* 517.
- Mehlum, H., Moene, K. y Torvik, R. (2006). Institutions and the resource curse. *EJ* 116.
- Minor, M. (1994). The demise of expropriation as an instrument of LDC policy, 1980–1992. *JIBS* 25(1).
- Mohr, S. H. y Evans, G. M. (2009). Forecasting coal production until 2100. *Fuel* 88; Mohr, S. H., Wang, J., Ellem, G., Ward, J. y Giurco, D. (2015). Projection of world fossil fuels by country. *Fuel* 141.
- Morehouse, D. F. (1997). The intricate puzzle of oil and gas reserves growth. EIA Natural Gas Monthly.
- Mudd, G. (2010). The environmental sustainability of mining in Australia. *Resources Policy* 35.
- Nashawi, I. S., Malallah, A. y Al-Bisharah, M. (2010). Forecasting world crude oil production using multicyclic Hubbert model. *Energy & Fuels* 24.
- Patzek, T. W. y Croft, G. D. (2010). A global coal production forecast with multi-Hubbert cycle analysis. *Energy* 35.
- Penrose, E. (1968). *The Large International Firm in Developing Countries: The International Petroleum Industry*. Allen & Unwin.
- Pfaffenzeller, S., Newbold, P. y Rayner, A. (2007). A short note on updating the Grilli and Yang commodity price index. *WBER* 21(1).
- Pindyck, R. (1999). The long-run evolution of energy prices. *Energy Journal* 20(2).
- Rogner, H.-H. (1997). An assessment of world hydrocarbon resources. *Annual Review of Energy and the Environment* 22; Rogner, H.-H. et al. (2012). Energy resources and potentials. *Global Energy Assessment*, cap. 7.
- Ross, M. (2001). Does oil hinder democracy? *World Politics* 53; (2012). *The Oil Curse*. Princeton UP; (2015). What have we learned about the resource curse? *Annual Review of Political Science* 18.
- Sachs, J. y Warner, A. (1995). Natural resource abundance and economic growth. NBER WP 5398; (2001). The curse of natural resources. *EER* 45.
- Slade, M. (1982). Trends in natural-resource commodity prices: an analysis of the time domain. *JEEM* 9.
- Smith, B. (2015). The resource curse exorcised: evidence from a panel of countries. *JDE* 116.
- Sorrell, S., Speirs, J., Bentley, R., Brandt, A. y Miller, R. (2010). Global oil depletion: a review of the evidence. *Energy Policy* 38.
- Stroebel, J. y van Benthem, A. (2013). Resource extraction contracts under threat of expropriation: theory and evidence. *Review of Economics and Statistics* 95(5).
- Tsui, K. (2011). More oil, less democracy: evidence from worldwide crude oil discoveries. *EJ* 121.
- USGS World Energy Assessment Team (2000). U.S. Geological Survey World Petroleum Assessment 2000. DDS-60.
- van der Ploeg, F. (2011). Natural resources: curse or blessing? *JEL* 49(2).
- Victor, D., Hults, D. y Thurber, M. (eds.) (2012). *Oil and Governance: State-Owned Enterprises and the World Energy Supply*. Cambridge UP.
- Yergin, D. (1991). *The Prize*. Simon & Schuster.
