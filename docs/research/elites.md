# Élites, desigualdad e indicadores estructural-demográficos

Módulo de datos: `src/sources/elites.py` → `data/processed/sources/elites.csv` (+ `elites_dict.json`).
Crudos en `data/raw/elites/` (el directorio `large/` está ignorado por git y ahora está vacío:
el volcado WID se filtra al descargarlo y ocupa unos 6 MB).

```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import elites; elites.build()"
```

Salida: 15 071 filas país-año, 227 códigos ISO3, 34 variables, 1950-2019. Todas las
participaciones van en fracciones 0-1.

---

## 1. Datos recopilados

### 1.1 Fuentes y cobertura

| Variable(s) | Fuente | Países | Años | Notas |
|---|---|---|---|---|
| `top1_share_ptinc`, `top10_share_ptinc`, `mid40_share_ptinc`, `bot50_share_ptinc`, `gini_ptinc_wid` | WID (sptinc992j, gptinc992j), volcado masivo por país | 215 | 1950-2019 (anual desde 1980; 1950/1960/1970 para 48 países y serie anual para unos 7 antes de 1980) | Renta nacional antes de impuestos, adultos, reparto igualitario (*equal split*). |
| `top1_share_wealth`, `top10_share_wealth`, `bot50_share_wealth`, `gini_wealth_wid` | WID (shweal992j, ghweal992j) | 214 | Casi solo 1995-2019 | Antes de 1995 hay datos solo para unos 5-7 países ricos. |
| `avg_inc_top1`, `avg_inc_top10`, `avg_inc_all`, `avg_inc_bot50`, `nni_per_adult` | WID (aptinc992j, anninc992i) | 214 | Igual que las participaciones (`nni_per_adult`: 151 países ya en 1960) | USD PPA constantes del año de referencia WID. La media del 50 % inferior se recalcula como `2·bot50_share·avg_inc_all`: en el volcado, `aptinc p0p50` vale exactamente la mitad (es share×media). |
| `top1_bot50_income_ratio`, `bot50_rel_income` | Derivadas de WID | 214 | | Renta relativa élite/masas y «salario relativo» WID (= 2·bot50_share). |
| `wid_flat_flag` | Derivada | 215 | | 1 si la participación top1 no cambia respecto del año contiguo. WID mantiene constante la distribución cuando faltan encuestas o datos fiscales. Afecta a un 30 % de las observaciones desde 1980 (más del 85 % en SAU, MAR, ZWE, MMR y SDN). |
| `gini_disp`, `gini_mkt` (+`_se`), `redist_rel` | SWIID 9.6 (Solt 2020), fichero resumen | 198 | 1960-2019 (4 países en 1960, 110 en 1990, 146 en 2015) | Media de 100 imputaciones, con su error estándar. |
| `tert_share_2564`, `tert_compl_share_2564`, `tert_share_2534`, `yr_sch_2564`, `youth_share_1524_of_1564` | Barro-Lee v3 (2021) | 146 | 1950-2015 (quinquenal, interpolada a anual) | La población 25-34 con estudios terciarios es el proxy de **aspirantes a élite**. La cohorte 15-24 sobre 15-64 es el proxy de *youth bulge*. |
| `tert_enrol_gross` | WDI SE.TER.ENRR (vintage 2026-04) | 201 | 1970-2019 | Tasa bruta; puede superar 1. |
| `hh_cons_pc_2015usd` | WDI NE.CON.PRVT.PC.KD (2025-07) | 181 | 1960-2019 | Proxy de renta de masas. |
| `youth_unemp` | WDI SL.UEM.1524.ZS, estimación modelada de la OIT (2023-10) | 186 | 1991-2019 | |
| `urban_share` | WDI SP.URB.TOTL.IN.ZS (2026-07) | 216 | 1960-2019 | Término N_urb/N del MMP. |
| `rel_wage_pwt`, `wage_per_worker_pwt`, `emp_pop_ratio` | PWT 10.01 (`data/raw/pwt1001.csv`) | 138 | 1950-2019 | Salario relativo de Turchin: w = (labsh·Y/emp)/(Y/pop) = labsh·pop/emp. |

Medianas mundiales (para fijar referencias):

| | 1960 | 1980 | 1990 | 2000 | 2015 | 2019 |
|---|---|---|---|---|---|---|
| top10 (renta) | 0,45 | 0,46 | 0,46 | 0,47 | 0,47 | 0,47 |
| top1 (renta) | 0,18 | 0,15 | 0,15 | 0,16 | 0,16 | 0,16 |
| bot50 (renta) | 0,17 | 0,15 | 0,15 | 0,15 | 0,16 | 0,16 |
| Gini disponible (SWIID) | – | 0,37 | 0,36 | 0,40 | 0,38 | 0,36 |
| Población 25-34 con estudios terciarios | 0,018 | 0,061 | 0,089 | 0,122 | 0,212 | – |
| Matrícula terciaria bruta | – | 0,03 | 0,07 | 0,15 | 0,45 | 0,50 |
| Proporción urbana | 0,34 | 0,47 | 0,52 | 0,56 | 0,62 | 0,63 |
| Población 15-24 / 15-64 | 0,32 | 0,36 | 0,33 | 0,31 | 0,25 | – |

Ejemplos: la participación top1 de EE. UU. pasa de 0,104 (1980) a 0,190 (2019) y la
bottom50 de 0,201 a 0,136. En China, top1 pasa de 0,066 a 0,146. En Francia, de 0,075 a 0,114.

### 1.2 Advertencias

* **WID antes de 1980** solo cubre 48 países y en años decenales. Muchas series de
  1980-2019 de países sin datos fiscales son interpolaciones o extrapolaciones planas: use
  `wid_flat_flag==0` para calibrar o pondere por calidad.
* WID **no incluye la riqueza oculta en paraísos fiscales**. En Rusia, los países del Golfo y
  Venezuela esa riqueza equivale a entre el 50 % y el 60 % del PIB (Alstadsæter, Johannesen
  y Zucman 2018), así que infravalora la captura de élite en petroestados.
* SWIID tiene poca cobertura antes de 1975 y su incertidumbre es grande en países pobres
  (use `*_se`).
* Barro-Lee termina en 2015. Para 2016-2019, extrapole con `tert_enrol_gross`.
* **No se consiguió** (hosts bloqueados o sin copia en GitHub):
  * desempleo de titulados (SL.UEM.ADVN.ZS);
  * número de abogados o doctores;
  * salarios reales OIT/ILOSTAT;
  * el índice de desigualdad horizontal (GREG/G-Econ) de Cederman et al.;
  * la serie PSI de EE. UU. de Turchin (tampoco está publicada en formato tabular abierto);
  * los datos PITF de inestabilidad.
  * La deuda pública (término SFD) corresponde al módulo fiscal/estatal.

---

## 2. Revisión de la literatura

### 2.1 Goldstone (1991): el Political Stress Indicator original

En *Revolution and Rebellion in the Early Modern World*, Goldstone define

Ψ = MMP × EMP × SFD

* **MMP** (potencial de movilización de masas) = w⁻¹ · (N_urb/N) · A₁₅₋₂₉, donde w es el salario real,
  N_urb/N la urbanización y A₁₅₋₂₉ la proporción de jóvenes.
* **EMP** (potencial de movilización de élites) = competencia intraelite: movilidad de élite
  y aspirantes (matrícula universitaria, litigios, cargos). En Turchin se expresa como renta por
  élite y número de élites.
* **SFD** (crisis fiscal del Estado) = (deuda/ingresos) · (1 − confianza en el Estado).

El carácter multiplicativo implica que la crisis requiere presión simultánea en los tres frentes.

### 2.2 Turchin (2013; *Ages of Discord* 2016; *End Times* 2023)

Turchin (2013, «Modeling Social Pressures Toward Political Instability», *Cliodynamics*
4(2)) adapta el PSI a EE. UU. (1780-2010). Las definiciones siguientes coinciden con la
literatura secundaria, pero **la forma exacta de ε no se pudo verificar** con el PDF original
(host bloqueado):

* **Salario relativo** w = W / (G/N): salario típico entre PIB per cápita. Es el motor del modelo.
* **Número relativo de élites** e = E/N. Su dinámica viene de la movilidad ascendente
  impulsada por la «bomba de riqueza»:

  e_t = e_{t−1} + μ₀ · (w₀ − w_t)/w_t,  con **μ₀ = 0,1 y w₀ = 1** (w normalizado).

  Cuando el salario relativo cae por debajo de w₀, crece el número de élites (sobreproducción).
* **Renta relativa por élite** ε = (1 − wλ)/e (λ = población activa/total): el ingreso no
  salarial repartido entre las élites.
* **MMP = w⁻¹ · (N_urb/N) · A₂₀₋₂₉**
* **EMP = ε⁻¹ · (e/e₀)**
* **SFD = (Y/G) · (1 − T)**: deuda pública / PIB × desconfianza institucional.
* **PSI = MMP · EMP · SFD**.

Turchin también añade retardos: la movilización de masas responde a la caída salarial con
un desfase de unos 10 a 20 años vía la estructura de edades.

En *End Times* (2023) los proxies de élite son:

* hogares con patrimonio superior a 10 M$;
* titulados en derecho y doctores frente a las plazas disponibles;
* el coste de las campañas electorales.

Sostiene que la «bomba de riqueza» (salario relativo decreciente y renta del capital
creciente) generó sobreproducción de élites desde 1980.

Evaluaciones empíricas:

* **Turchin & Korotayev (2020, PLOS ONE)** valoran positivamente el pronóstico de 2010 de un
  pico de inestabilidad en EE. UU. hacia 2020.
* **Georgescu (2023, PLOS ONE)** contrasta la teoría en países industrializados y rechaza
  sus predicciones:
  * la caída del salario relativo se explica por automatización y globalización, no por
    exceso de oferta laboral;
  * la renta de élite crece de forma monótona al caer w (no en forma de joroba);
  * la sobreproducción de élites no predice la inestabilidad reciente;
  * el aumento del PSI se debe sobre todo a la desigualdad.
* **PSI de Polonia (arXiv 2405.01163, 2024)**:
  * la versión simulada reproduce la caída del comunismo;
  * el índice es muy sensible a los parámetros: rangos relativos de 0,51 (MMP), 0,60 (EMP)
    y 0,41 (SFD);
  * las ecuaciones originales no describen bien la fracción de élite a largo plazo.

### 2.3 Modelos predictivos de inestabilidad

* **Goldstone et al. (2010, AJPS; PITF)** predicen el inicio de inestabilidad (1955-2003) con
  más del 80 % de acierto y dos años de antelación, usando solo cuatro variables:
  * **tipo de régimen**: las democracias parciales con faccionalismo tienen una odds unas
    30 veces mayor que las autocracias plenas;
  * **mortalidad infantil** relativa a la mediana mundial: el percentil 75 frente al 25
    multiplica el riesgo aproximadamente por 7;
  * **mal vecindario**: cuatro o más vecinos en conflicto;
  * **discriminación estatal**.

  Lección: las instituciones dominan sobre las variables económicas y demográficas.
* **Fearon & Laitin (2003)** y **Collier & Hoeffler (2004)**:
  * la renta per cápita y la población son los predictores robustos;
  * la desigualdad vertical (Gini) no es significativa;
  * la dependencia de materias primas tiene un efecto en U invertida, con máximo del riesgo
    cuando las exportaciones primarias rondan el 33 % del PIB.
* **Urdal (2006, ISQ)**: cada punto porcentual adicional de *youth bulge* eleva el riesgo de
  conflicto un 4 % aproximadamente. Es decir, d ln p/dA ≈ 4 por unidad de proporción, una
  elasticidad cercana a 1,2 con A ≈ 0,3.
* **Korotayev et al. (2011, 2014)** vinculan la Primavera Árabe al *youth bulge* combinado
  con una expansión rápida de la educación terciaria. Es un mecanismo de sobreproducción de
  élites vía titulados desempleados.

### 2.4 Desigualdad vertical frente a horizontal

* **Østby (2008, JPR)**: la desigualdad horizontal social entre grupos étnicos y la
  polarización social aumentan el inicio de conflicto. La desigualdad interpersonal (Gini)
  y la polarización étnica pura no son significativas.
* **Cederman, Weidmann & Gleditsch (2011, APSR)**: los grupos étnicos políticamente
  relevantes con PIB per cápita muy inferior o superior a la media nacional (datos G-Econ
  geocodificados) tienen un riesgo de guerra etnonacionalista claramente mayor. Del orden
  de 2-3 veces en los extremos de la distribución (valor aproximado; no verificado en la
  tabla original).
* **Bartusevičius (2014, JPR)** encuentra algo de efecto de la desigualdad vertical de renta
  y educación sobre las rebeliones populares, no sobre las guerras civiles en general.

**Estimación exploratoria propia** (logit de `onset` UCDP con renta, población, democracia
parcial y rentas; errores agrupados por país; retardo de un año; unos 7000 país-años y 250 onsets):

| Regresor | coef. | e.e. | Implicación |
|---|---|---|---|
| ln PIB pc | −0,43 | 0,09 | Robusto (≈ Fearon-Laitin) |
| ln población | 0,46 | 0,08 | Robusto |
| Rentas de recursos / PIB | 2,4-3,2 | 0,6-1,0 | +10 pp → OR ≈ 1,3 |
| Top1 renta (WID) | 2,4 | 1,8 | +10 pp → OR ≈ 1,27 (n.s.) |
| Top1, solo obs. no planas | 1,6 | 2,2 | n.s. |
| Gini disponible (SWIID) | 0,26 | 1,5 | n.s. |
| Crecimiento renta bot50 (5 años) | −1,0 | 1,8 | n.s. |
| Terciaria 25-34 / youth bulge | −0,6 / 1,4 | 1,3 / 2,5 | n.s. |
| ln PSI proxy (w⁻¹·U·A × e/ε) | −0,02 | 0,07 | n.s. |

La tasa base de onset es 0,034 por país-año. Conclusión: la desigualdad vertical tiene un
efecto débil y positivo, pero muy incierto, en línea con la literatura. El PSI ingenuo
construido con datos nacionales **no** predice el onset de guerra civil. En el modelo, el PSI
debe contribuir con una elasticidad moderada y no puede sustituir a la renta y a las rentas.

### 2.5 Captura de rentas por las élites

* **Rentas de recursos**: Andersen, Johannesen, Lassen & Paltseva (2017, JEEA) estiman que en
  petroestados **autocráticos** aproximadamente el **15 %** de las ganancias extraordinarias
  del petróleo acaba en cuentas bancarias secretas en paraísos fiscales. En países con
  controles institucionales no hay efecto. Es un límite inferior de la captura de élite,
  porque solo mide la parte oculta en el extranjero.
* **Rentas externas y ayuda**: Andersen, Johannesen & Rijkers (2022, JPE) estiman una fuga
  del **7,5 %** de la ayuda hacia paraísos fiscales en la media muestral, creciente con el
  cociente ayuda/PIB.
* **Riqueza offshore**: Alstadsæter, Johannesen & Zucman (2018) la cifran en un 10 % del PIB
  mundial, con entre el 50 % y el 60 % del PIB en Rusia, los países del Golfo y Venezuela.
* **Estimación propia con efectos fijos**: se regresó la participación top10 de WID (solo
  observaciones no planas, 1980-2019) sobre rentas/PIB con efectos fijos de país y año:
  * pendiente −0,016 (e.e. 0,027);
  * autocracias (v2x_polyarchy < 0,4): +0,020 (e.e. 0,006) en el nivel;
  * sin interacción significativa con las rentas.

  Dentro de un mismo país, las fluctuaciones de rentas **no** alteran la distribución
  medida antes de impuestos. Es decir, φ_R − E ≈ 0 ± 0,05 en lo observable por WID, y la
  captura adicional sería oculta (offshore) o se manifiesta en el nivel (autocracias),
  no en la varianza temporal.
* **Ross (2012)** y **Arezki & Brückner (2011)**: los aumentos de renta petrolera elevan la
  corrupción y reducen los derechos políticos. Este es el canal institucional.

---

## 3. Especificación recomendada para `src/model.py`

Notación del modelo:

* G: PIB;
* `res_inc`: renta de recursos retenida;
* `rent_in` y `rent_out`: rentas entrantes y salientes;
* L: población;
* S: asabiya;
* D: democracia (v2x_polyarchy);
* E: participación de élite en la producción base;
* n_e: número de élites normalizado a 1 en el año de entrada;
* v = renta de élite / renta de masas.

**(1) Definición e inicialización de E.** Tomar la élite como el **10 % superior**.

* E_i0 = `top10_share_ptinc` del primer año disponible con `wid_flat_flag==0`, o la mediana
  del país en 1980-1990 si falta.
* Si tampoco hay dato WID: E_i0 ≈ 0,44 + 0,5·(labsh_mundial − labsh_i). La correlación entre
  1−labsh y top10 es de solo 0,39 y las medias son parecidas (0,46 frente a 0,44), por lo que
  1−labsh es un proxy pobre.

Así, la renta per cápita relativa de élite es (E/0,1)/((1−E)/0,9).

**(2) Captura de rentas** (sustituye φ_R = 0,7 y φ = 0,6 fijos):

  φ_R,i = E_i + 0,15·(1 − D_i)    (rango 0,05-0,25; Andersen et al. 2017)
  φ_i   = E_i + 0,075·(1 − D_i)   (rango 0-0,15; Andersen et al. 2022)

Con E ≈ 0,45, esto da φ_R ≈ 0,45-0,60, bastante menos que 0,7. Una opción es añadir una
constante autocrática ΔE = +0,02·𝟙(D < 0,4) en el nivel de E.

**(3) Salario relativo / renta de masas.** Definir

  w_t = (mass_inc/L) / (G/L) = mass_inc / G

y normalizarlo por su valor de entrada (w₀ = 1). Objetivos de calibración:

* `bot50_rel_income` (WID) y `rel_wage_pwt / media del país` (PWT) para w;
* `avg_inc_bot50` y `hh_cons_pc_2015usd` para la renta de masas absoluta.

**(4) Número de élites (sobreproducción).** Mantener la forma actual, que es una versión
con reversión a la media de Turchin:

  Δln n_e = β_e · (v/v₀ − n_e) − 0,15·conflict

con **β_e ≈ 0,05** (rango 0,03-0,10).

* La cota superior μ₀ = 0,1 es la de Turchin (2013).
* La mediana del crecimiento anual de `tert_share_2534` es 0,034 en los años ochenta y
  0,025-0,029 en 1990-2019, con 0,044-0,057 en los sesenta y setenta. Con v/v₀ − n_e ≈ 0,5
  en expansión, eso implica β_e ≈ 0,05-0,07.

Alternativa más fiel a Turchin: Δn_e = μ₀·(1 − w)/w con μ₀ = 0,1. Objetivo de calibración:
n_e,t / n_e,0 frente a `tert_share_2534,t / tert_share_2534,0` (Barro-Lee) y `tert_enrol_gross`.
Dos alternativas más:

* usar la matrícula terciaria observada como forzamiento exógeno de la oferta de aspirantes;
* modelar n_e = aspirantes × tasa de absorción.

**(5) EMP según Turchin.** La renta por élite es ε = v/n_e, así que

  EMP = ε⁻¹ · (e/e₀) = n_e² · v₀ / v.

El código actual (`emp = ne / (v/v0)`) omite el factor e/e₀. **Se recomienda elevar n_e al
cuadrado**, o al menos a una potencia de 1,5 a 2.

**(6) MMP según Goldstone y Turchin, más la brecha de expectativas del código actual:**

  MMP = (1/w) · (U/U_ref) · (A/A_ref) · (m̄/m)^κ

* U es `urban_share` (U_ref = 0,52, la mediana de 1990).
* A es `youth_share_1524_of_1564` (A_ref = 0,33, mediana de 1990). A proyectar con el módulo
  demográfico después de 2015.
* m̄/m es la media móvil de la renta de masas frente a la actual (curva J de Davies).
  κ = 1: el exponente 2 actual amplifica en exceso.

**(7) SFD.** Mientras no haya deuda pública:

  SFD = 1,5 − S

Con datos fiscales: SFD = (1 + deuda/PIB)·(1,5 − S), o (deuda/PIB)·(1 − T) como en Turchin.

**(8) Riesgo de inicio de conflicto:**

  logit p_on = b₀ + b₁·ln(PSI/PSI_ref) + b₂·(ln y − 9) + b₃·(S − 0,5) + b₄·(rentas/PIB) + b₅·dem_parcial

| Parámetro | Recomendado | Rango | Justificación |
|---|---|---|---|
| b₀ | −3,35 | calibrar | logit(0,034) = tasa base de onset UCDP; con PSI normalizado a la mediana |
| b₁ | **0,6** | 0,3-1,2 | Elasticidades implícitas: youth bulge ≈ 1,2 (Urdal); top1 ≈ 0,36; PSI proxy ≈ 0. El valor actual 1,2 es la cota superior. |
| b₂ | −0,43 | −0,3 a −0,55 | Estimación propia (e.e. 0,09); Fearon-Laitin |
| b₄ | 2,5 | 1,5-3,2 | Estimación propia; Collier-Hoeffler |
| b₅ | 1,0 | 0,5-3,4 | PITF: odds ≈ 30 para democracia parcial con faccionalismo; ≈ 2-5 sin faccionalismo |
| persistencia `bp` | 2,0 | | Sin cambios |

Un OR de 1,5 por duplicación del PSI (b₁ = 0,6) es coherente con los efectos, grandes pero
imprecisos, de la desigualdad horizontal (×2-3 en los extremos) y con los débiles de la
vertical.

### 3.1 Objetivos de calibración

1. **E_t**: trayectoria de `top10_share_ptinc` (peso 1 si `wid_flat_flag==0`, 0,2 si no).
   Momentos secundarios:
   * `top1_share_ptinc`;
   * `gini_mkt` y `gini_disp` (SWIID, ponderados por 1/se²).
2. **w_t**: `bot50_rel_income` y `rel_wage_pwt` normalizado.
   Estilizado: en EE. UU. el salario relativo cae de 1,39 a 1,24 (PWT) y la participación
   bot50 de 0,20 a 0,14 entre 1980 y 2019.
3. **n_e**: crecimiento de `tert_share_2534` y `tert_enrol_gross`.
   Estilizado: la mediana mundial de población 25-34 con estudios terciarios pasa de 0,018
   a 0,21 entre 1960 y 2015, unas 12 veces.
4. **Rentas → E**: con efectos fijos, la pendiente de top10 frente a rentas/PIB debe ser
   ≈ 0 (±0,05). El nivel en autocracias es +0,02.
5. **Hazard**: tasa de onset 0,034; prevalencia de conflicto 0,113; y el gradiente por renta
   (b₂) y por rentas (b₄) de la tabla 2.4.
6. **Validación fuera de muestra**: `youth_unemp` (1991-2019) y la interacción entre terciaria
   y youth bulge en MENA hacia 2010 (Korotayev), como prueba cualitativa del EMP.

### 3.2 Incertidumbre principal

* La teoría estructural-demográfica tiene apoyo cuantitativo cross-nacional débil en
  sociedades industriales (Georgescu 2023) y el PSI es muy sensible a los parámetros
  (Polonia 2024).
* Por eso se recomienda tratar β_e, b₁ y el exponente de n_e en el EMP como parámetros
  libres en la calibración bayesiana o ABC, con los rangos indicados como *priors* uniformes.

---

## Referencias

* Alstadsæter, A., Johannesen, N., Zucman, G. (2018). Who owns the wealth in tax havens? *J. Public Econ.* 162.
* Andersen, J.J., Johannesen, N., Lassen, D.D., Paltseva, E. (2017). Petro rents, political institutions, and hidden wealth. *JEEA* 15(4): 818-860.
* Andersen, J.J., Johannesen, N., Rijkers, B. (2022). Elite capture of foreign aid. *JPE* 130(2): 388-425.
* Arezki, R., Brückner, M. (2011). Oil rents, corruption, and state stability. *Eur. Econ. Rev.* 55(7).
* Barro, R., Lee, J.-W. (2013). A new data set of educational attainment in the world, 1950-2010. *JDE* 104. Actualización v3 (2021).
* Bartusevičius, H. (2014). The inequality-conflict nexus re-examined. *JPR* 51(1).
* Cederman, L.-E., Weidmann, N.B., Gleditsch, K.S. (2011). Horizontal inequalities and ethnonationalist civil war. *APSR* 105(3): 478-495.
* Collier, P., Hoeffler, A. (2004). Greed and grievance in civil war. *Oxford Econ. Papers* 56.
* Fearon, J., Laitin, D. (2003). Ethnicity, insurgency, and civil war. *APSR* 97(1).
* Georgescu, O.-M. (2023). The structural-demographic theory revisited: An empirical test for industrialized societies. *PLOS ONE* 18(11): e0287912.
* Goldstone, J.A. (1991). *Revolution and Rebellion in the Early Modern World*. Univ. of California Press.
* Goldstone, J.A. et al. (2010). A global model for forecasting political instability. *AJPS* 54(1): 190-208.
* Korotayev, A. et al. (2011). A trap at the escape from the trap? *Cliodynamics* 2(2); Korotayev, A., Issaev, L., Malkov, S., Shishkina, A. (2014). The Arab Spring: a quantitative analysis. *Arab Studies Quarterly* 36(2).
* Østby, G. (2008). Polarization, horizontal inequalities and violent civil conflict. *JPR* 45(2): 143-162.
* Political Stress Index of Poland (2024). arXiv:2405.01163.
* Ross, M. (2012). *The Oil Curse*. Princeton UP.
* Solt, F. (2020). Measuring income inequality across countries and over time: The SWIID. *Social Science Quarterly* 101(3). SWIID v9.6.
* Turchin, P. (2013). Modeling social pressures toward political instability. *Cliodynamics* 4(2): 241-280.
* Turchin, P. (2016). *Ages of Discord*. Beresta Books.
* Turchin, P. (2023). *End Times: Elites, Counter-Elites, and the Path of Political Disintegration*. Penguin.
* Turchin, P., Korotayev, A. (2020). The 2010 structural-demographic forecast for the 2010-2020 decade: A retrospective assessment. *PLOS ONE* 15(8): e0237458.
* Turchin, P., Nefedov, S. (2009). *Secular Cycles*. Princeton UP.
* Urdal, H. (2006). A clash of generations? Youth bulges and political violence. *ISQ* 50(3): 607-629.
* World Inequality Lab. WID - World Inequality Database (wid.world), volcado masivo por país (copia en github.com/sandravizz/Global-Inequality-Data).
