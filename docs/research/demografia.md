# Demografía y asabiya: datos, literatura y especificación recomendada

Este documento acompaña a `src/sources/demografia.py`, que genera `data/processed/sources/demografia.csv` y su diccionario `demografia_dict.json`.

Regenerar con:

```
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from sources import demografia; demografia.build()"
```

La primera ejecución descarga unos 86 MB y tarda unos 2 minutos.

## 1. Datos construidos

El panel es país-año: 236 códigos ISO3 × 1950–2030, es decir 19 116 filas. Los 180 países de `panel.csv` están todos cubiertos.

- 1950–2023 son estimaciones.
- 2024–2030 son proyecciones UN WPP 2024 en la variante media, marcadas con `wpp_projection = 1`.
- Todas las proporciones están expresadas como fracciones.

### 1.1 Demografía (UN World Population Prospects 2024)

Fuente: paquete R `PPgp/wpp2024`, con edades simples de 0 a 100+ y datos anuales. La cobertura es completa (236 países, 1950–2030).

| variable | definición |
|---|---|
| `pop_wpp` | población total en millones. Correlación 0,9998 con `pop` de PWT; la mediana del cociente WPP/PWT es 1,01 |
| `share_0_14`, `share_15_24`, `share_15_29`, `share_15_64`, `share_65p` | estructura por edad |
| `youth_bulge_15_24_adult` | **medida de Urdal (2006)**: 15–24 / población de 15 años o más |
| `youth_bulge_15_29_adult` | 15–29 / población de 15 años o más |
| `male_share_15_29` | varones de 15–29 / población total |
| `dependency_ratio` | (0–14 + 65+) / 15–64 |
| `median_age` | edad mediana, interpolada dentro de cada año de edad |
| `tfr`, `life_expectancy` | fecundidad total; esperanza de vida al nacer (ambos sexos) |
| `net_migration` (millones), `net_migration_rate` (por persona), `crude_birth_rate`, `crude_death_rate`, `pop_growth` | flujos |
| `pop_wpp_lo80`, `pop_wpp_hi80`, `pop_wpp_low_var`, `pop_wpp_high_var` | intervalo probabilístico del 80 % y variantes baja y alta (±0,5 hijos). Solo para 2024–2030 |

**Uso recomendado en el modelo.** En los pronósticos hay que sustituir la población realizada por `pop_wpp` a partir de 2020 (o de 2024). Hasta 2023 la serie WPP es una estimación ex post, así que en un backtest honesto con origen T habría que usar la revisión WPP disponible en T. Esa revisión no está disponible aquí: WPP 2024 incorpora información posterior, sobre todo la mortalidad por COVID.

### 1.2 Urbanización

`urban_share` procede del WDI SP.URB.TOTL.IN.ZS (release de julio de 2026), que se basa en UN WUP 2018 y cubre 1960–2023.

- **1950–1959** se retropola con una tendencia logit-lineal ajustada a 1960–1979.
- **2024–2030** se extrapola con la tendencia logit de 2014–2023.
- Estos años llevan `urban_share_imputed = 1`.

Comprobación del agregado mundial ponderado por población:

| año | construido | UN WUP 2018 |
|---|---|---|
| 1950 | 31,4 % | 29,6 % |
| 2019 | 56,1 % | 55,7 % |

La retropolación sobreestima la urbanización de China en 1950 (18,5 % frente a 11,8 %). Para 1950–59 debe tratarse con cautela. `urban_pop_growth` es la diferencia de log(urbana × población), que corresponde a la "velocidad de urbanización" de Goldstone. La cobertura es de 216 países.

### 1.3 Cohesión / asabiya

Las variables anuales se arrastran hacia adelante (ffill) después de su último año observado.

| bloque | variables | fuente y cobertura |
|---|---|---|
| Fraccionalización y polarización anual | `creg_ethfrac`, `creg_ethpol`, `creg_relfrac`, `creg_relpol` | CREG (Nardulli et al. 2012) vía `cran/peacesciencer`; 1945–2013; 156–159 países |
| Fraccionalización étnica histórica | `hief_efindex` | HIEF (Dražanová 2020), 1945–2013; 155 países |
| Exclusión étnica del poder | `epr_excluded_share` (powerless + discriminated + self-exclusion), `epr_discriminated_share`, `epr_monopoly_dominant`, `epr_n_groups`, `epr_largest_group` | EPR 2021 (Vogt et al. 2015), 1946–2021; 174 países |
| Fraccionalización constante | `al_ethnic`, `al_language`, `al_religion` | Alesina et al. (2003); 210 países |
| Confianza generalizada | `trust_wvs` (observada por ola, 1984–2022; 115 países y 419 observaciones), `trust_wvs_interp` (interpolación lineal y constante fuera del rango observado), `trust_wvs_mean` | WVS/EVS vía Our World in Data |
| Capacidad estatal | `v2stfisccap` (capacidad fiscal), `v2svstterr` (fracción del territorio controlado), `v2clrspct` (administración imparcial), `v2stcritrecadm` (meritocracia), `v2x_rule` | V-Dem v14 (`vdeminstitute/vdemdata`); 176 países |
| Polarización y estructura social | `v2cacamps` (polarización política), `v2pepwrsoc` (poder repartido entre grupos sociales), `v2xpe_exlsocgr` (exclusión por grupo social), `v2exl_legit_nationalist` (legitimación nacionalista del régimen) | V-Dem v14 |
| Frontera histórica | `rivalries_active`, `rivalries_spatial` (rivalidades estratégicas y territoriales de Thompson-Dreyer; las vigentes en 2010 se suponen en curso), `rivalry_years_cum` (años-rivalidad acumulados desde 1816) | `peacesciencer::td_rivalries` |
| Origen colonial | `colonial_ruler` (ISO3 de la metrópoli o "none"), `indep_year`, `indep_violent`, `former_colony`, `years_since_indep` | ICOW Colonial History 1.1 (Hensel); 194 países |
| Antigüedad del estado moderno | `state_age`: años en el sistema Gleditsch-Ward, contados desde 1816 | `andybega/ds-external-data`; 195 países |
| Geografía | `rugged` (Nunn-Puga), `log_mountainous` (Fearon-Laitin) | peacesciencer; 190 países |
| Índices compuestos | `state_capacity_index`, `cohesion_index`, `asabiya_proxy` | construidos; ver §3.4 |

**Advertencias sobre estas fuentes:**
- ICOW fecha algunas "independencias" en época premoderna (por ejemplo, CHN 1368 y DEU 1618).
- En `state_age`, Alemania se reinicia en 1949 (código GW 260). Conviene usar `state_age` y `years_since_indep` en logaritmo y truncados.

### 1.4 Carencias (no encontradas en espejos accesibles)

- **Hanson & Sigman (2021)**, índice de capacidad estatal 1960–2015. Solo está en Harvard Dataverse, que está bloqueado. Sustituto: `state_capacity_index` (V-Dem). La correlación publicada entre Hanson-Sigman y la capacidad fiscal de V-Dem es alta (≈0,8).
- **Índice de antigüedad del estado de Bockstette-Chanda-Putterman** (`statehist`). No se encontró. Sustitutos parciales: `state_age`, `indep_year` y `rivalry_years_cum`.
- **Fearon (2003)**, fraccionalización y diversidad cultural. HIEF y CREG son alternativas con la misma metodología básica.
- **UN WUP 2018 anual 1950–59**. En GitHub solo aparece como puntero git-lfs; de ahí la retropolación.
- **Fortin (2012)** y la capacidad tributaria (ICTD/UNU-WIDER GRD) no se incluyen aquí; pueden estar en el módulo de finanzas.

## 2. Literatura

### 2.1 Bulto juvenil y conflicto

- **Urdal (2006, *ISQ* 50:607–630).** El bulto juvenil (15–24 / 15+) aumenta el riesgo de conflicto armado interno, terrorismo y disturbios. Cada punto porcentual adicional eleva el riesgo de conflicto en más de un 4 % (odds). Un país con un bulto del 35 % tiene un riesgo aproximadamente un 150 % mayor que uno con el 17 % (el valor típico de los países desarrollados). El efecto se amplifica con baja escolarización y bajo crecimiento económico, y es mayor en regímenes autocráticos y en fases de transición.
- **Goldstone (1991, 2002).** En el enfoque estructural-demográfico, el potencial de movilización masiva (MMP) depende de salarios reales estancados, de la presión juvenil y de la urbanización rápida. Goldstone et al. (2010, *AJPS*; PITF) predicen la inestabilidad con cuatro variables: tipo de régimen (la democracia parcial faccionalizada es la más peligrosa, con odds ratio ≈ 30), mortalidad infantil relativa (odds ratio ≈ 4–7 en el cuartil superior), conflicto en países vecinos y discriminación estatal. Alcanzan un 80 % de acierto a dos años.
- **Cincotta (2008–2017), teoría estructural de la edad.** Con edad mediana por debajo de ~25 años, la probabilidad de conflicto intraestatal es alta. La democracia liberal estable se vuelve probable por encima de ~29–30 años.
- **Collier & Hoeffler (2004).** La escolarización secundaria masculina reduce el riesgo, y la población tiene una elasticidad positiva.
- **Fearon & Laitin (2003).** Coeficientes logit de inicio de guerra civil: log de la población ≈ +0,27; log del porcentaje de terreno montañoso ≈ +0,22; PIB per cápita ≈ −0,34 por cada 1 000 $. La fraccionalización étnica (+0,16) y la religiosa (+0,33) no son significativas. Estado nuevo ≈ +1,7; inestabilidad política ≈ +0,6.
- **Estimación propia con este panel**, como objetivo de calibración. Logit de `onset` (UCDP) en años sin conflicto previo, 1950–2019, n = 8 983:

  | regresor | coeficiente (EE) |
  |---|---|
  | `youth_bulge` (pp) | **+0,035** (0,014) |
  | log PIBpc | −0,34 (0,08) |
  | log población | +0,40 (0,04) |

  Con controles (urbanización, EPR, polarización, montaña) el efecto del bulto es +0,038 (0,015). La incidencia de conflicto crece con el bulto:

  | bulto juvenil | incidencia |
  |---|---|
  | < 20 % | 3,5 % |
  | 20–25 % | 8 % |
  | 25–30 % | 13 % |
  | > 35 % | 17 % |

  Si se usa la edad mediana en lugar del bulto, su coeficiente es −0,055 por año (0,014).

### 2.2 Urbanización y protesta

- La evidencia sobre la urbanización como causa de conflicto armado es débil. Urdal & Hoelscher (2012) y Buhaug & Urdal (2013) no encuentran que el crecimiento urbano aumente los disturbios urbanos en Asia y África.
- Wallace (2014, *Cities and Stability*) muestra que la concentración en la capital eleva el riesgo para los regímenes (protesta urbana y golpes).
- Goldstone sostiene que la urbanización rápida sin empleo alimenta el MMP.
- En este panel, `urban_pop_growth` tiene coeficiente **negativo** en el logit de inicio (−4,9, EE 1,9). Probablemente capta crecimiento económico. El nivel de urbanización no es significativo (−0,29, EE 0,48).
- **Recomendación:** que la urbanización entre en el MMP solo en interacción con el estancamiento salarial (urbanización × caída del ingreso), con un peso pequeño y una prior centrada en 0.

### 2.3 Transición demográfica y crecimiento (dividendo demográfico)

- **Bloom & Williamson (1998, *WBER*).** En regresiones de crecimiento per cápita, el crecimiento de la población en edad de trabajar tiene coeficiente ≈ +1,4 a +1,6, y el de la población total ≈ −1,0 a −1,1. La transición explica entre un cuarto y un tercio del "milagro" de Asia oriental entre 1965 y 1990.
- **Bloom, Canning & Sevilla (2003)** y **Kelley & Schmidt (2005)** obtienen resultados similares. El dividendo depende de las instituciones y del capital humano.
- **Implicación para el modelo:** si la producción es por trabajador, hay que añadir un término que traduzca el cambio en `share_15_64` en crecimiento. El ingreso per cápita crece mecánicamente con Δln(share_15_64), con elasticidad ≈ 1 como identidad contable, más un posible efecto conductual sobre el ahorro y la inversión.

### 2.4 Turchin: frontera metaétnica y asabiya

- **Turchin (2003, *Historical Dynamics*, caps. 3–4).** La asabiya S ∈ [0,1] crece logísticamente en las regiones de frontera metaétnica y decae linealmente en el interior. La versión espacial es dS/dt = r₀ S(1−S) en la frontera y −δS fuera de ella. La réplica de referencia usa r₀ = 0,2, δ = 0,1, atenuación del poder con la distancia h = 2, umbral de colapso S_crit = 0,003 y S₀ = 0,25.

  Esos valores son **por paso del modelo**, que Turchin interpreta aproximadamente como una generación. En su modelo "geopolítico-asabiya" no espacial, el crecimiento de S disminuye con el tamaño del imperio A: dS/dt = r₀(1 − A/b) S(1 − S). El resultado son ciclos de auge y caída de 2 a 4 siglos, que coinciden con los ~3–4 generaciones de Ibn Jaldún.
- **Turchin (2006, *War and Peace and War*)** presenta la versión narrativa. **Turchin (2009, *Cliodynamics*)** contrasta con datos la teoría de la frontera en Europa: las megaestados surgen en fronteras metaétnicas.
- **Turchin, Currie, Turner & Gavrilets (2013, *PNAS* 110:16384).** El modelo de evolución cultural con difusión de la tecnología militar desde la estepa explica ≈ 65 % de la varianza espacio-temporal de los grandes imperios entre 1500 a. C. y 1500 d. C.
- **Besley & Persson (2009, 2010, 2011).** La inversión en capacidad fiscal y legal es mayor cuando hay amenaza de guerra externa ("common interest") e instituciones cohesivas. Esta idea tipo Tilly es la misma que la frontera de Turchin. Dincecco & Prado (2012) y Gennaioli & Voth (2015) encuentran que la exposición histórica a la guerra eleva la capacidad fiscal.
- **Cohesión y crecimiento.** Easterly & Levine (1997): pasar de ELF = 0 a ELF = 1 reduce el crecimiento ≈ 2 pp al año. Alesina et al. (2003) confirman el efecto negativo de la fraccionalización étnica y lingüística, más débil una vez se controlan las instituciones. Knack & Keefer (1997) y Zak & Knack (2001): +15 pp de confianza se asocian a +1 pp de crecimiento anual.
- **Cohesión y conflicto.** Montalvo & Reynal-Querol (2005, *AER*): la **polarización** étnica, no la fraccionalización, predice la incidencia de guerra civil. Cederman, Wimmer & Min (2010) y Wimmer, Cederman & Min (2009): la exclusión étnica del poder (EPR) eleva el riesgo de conflicto étnico. En este panel, `epr_excluded_share` tiene coeficiente +0,62 (EE 0,30), mientras que la polarización CREG resulta nula.
- **Antigüedad del estado.** Bockstette, Chanda & Putterman (2002) encuentran que la historia estatal larga se asocia a más crecimiento en 1960–95. Borcan, Olsson & Putterman (2018) hallan una relación en U invertida.

## 3. Especificación recomendada

### 3.1 MMP con estructura de edad y urbanización

$$
\text{MMP}_{it} = \Big(\frac{w_{it}}{w^*_{it}}\Big)^{-1} \cdot \underbrace{\exp\{\beta_Y (Y_{it}-\bar Y)\}}_{\text{bulto juvenil}} \cdot \underbrace{\exp\{\beta_U\, \max(0,\Delta\ln U_{it}) \cdot \mathbb 1[\Delta\ln w_{it}<0]\}}_{\text{urbanización sin empleo}}
$$

- Y es `youth_bulge_15_24_adult` en puntos porcentuales y Ȳ ≈ 28 (la media mundial de 1950–2019 está entre 25 y 30 %).
- **β_Y = 0,035–0,045 por pp.** La estimación propia es 0,035 (EE 0,014), Urdal da > 0,04 y el intervalo razonable es [0,015; 0,06]. Si el PSI entra en un logit de conflicto, esto equivale a sumar β_Y·(Y − Ȳ) al índice lineal.
- **β_U: prior N(0; 1)**, que se deja estimar. La evidencia es débil.
- Como alternativa robusta a Y se puede usar la edad mediana, con β = −0,055 por año (EE 0,014).

### 3.2 Asabiya anual

$$
S_{i,t+1} = S_{it} + r\,F_{it}\,S_{it}(1-S_{it}) - \delta\,(1-F_{it})\,g(y_{it})\,S_{it}
$$

**Frontera F_it ∈ [0,1].** Es una combinación de exposición a un núcleo extractor o rival:
- rivalidades espaciales activas: min(1, `rivalries_spatial` / 2);
- conflicto interestatal y extracción externa, a tomar de los módulos de comercio y geopolítica;
- años post-independencia violenta, con decaimiento exponencial.

**Decaimiento g(y) en núcleos ricos.** g(y) = 1/(1 + exp(−(ln y − ln y₀))), con y₀ ≈ 20 000 $ PPA. Así la erosión es máxima en los núcleos ricos, como en Ibn Jaldún: la opulencia erosiona la solidaridad.

**Conversión a tasas anuales.** Los parámetros de Turchin son por generación (~25 años): r₀ = 0,2 → 0,008/año y δ = 0,1 → 0,004/año. La calibración histórica también da cifras de este orden:
- que S pase de 0,1 a 0,9 en 1–2 siglos implica r = 2 ln 9 / T ≈ 0,02–0,045 al año;
- una vida media de la asabiya en el núcleo de ~100 años (tres generaciones de Ibn Jaldún) implica δ = ln 2 / 100 ≈ 0,007 al año.

| parámetro | recomendado | intervalo plausible |
|---|---|---|
| r (anual) | **0,02** | [0,008; 0,05] |
| δ (anual) | **0,007** | [0,003; 0,015] |

**Implicación.** Con estas tasas, S cambia poco en 70 años (ΔS ≤ ~0,2). El **valor inicial S₀** domina, y conviene estimarlo a partir de proxies (§3.4) en lugar de fijarlo en 0,5 para todos.

### 3.3 Efectos de la asabiya

- **Capacidad estatal.** Eficiencia de la inversión φ = φ₀ (1 + κ (S − 0,5)), con κ ≈ 0,5–1,0. La referencia es el efecto de la confianza de Zak-Knack, ~1 pp de crecimiento por cada 15 pp de confianza.
- **Resistencia a la inestabilidad.** Se resta un término de S al índice lineal del logit de conflicto. En este panel el `asabiya_proxy` tiene coeficiente **−3,2 (EE 0,53)**: pasar de 0,3 a 0,7 multiplica las odds de inicio por ≈ 0,28. Hay que tomarlo como una **cota superior**, porque el control territorial es parcialmente endógeno al conflicto. Una prior razonable es entre −1 y −3 por unidad de S.
- `state_capacity_index` por sí solo da −1,1 (EE 0,12) por DE. `cohesion_index` no es significativo una vez se controla la capacidad.

### 3.4 Mapeo de proxies a S₀

`asabiya_proxy` ya está en el CSV:

$$
S = 0{,}2 + 0{,}6\,\Phi\!\left(\frac{\bar z}{\text{sd}(\bar z)}\right),\quad \bar z = \tfrac12\big[\underbrace{\text{media } z(1-\text{frac}_{\text{étnica}},\,1-\text{excl}_{\text{EPR}},\,\text{trust})}_{\text{cohesión}} + \underbrace{\text{media } z(\text{v2stfisccap},\,\text{v2svstterr},\,\text{v2clrspct})}_{\text{capacidad}}\big]
$$

- Los z se calculan sobre 1950–2019 y se exigen al menos 3 componentes. Cobertura: 176 países.
- Rango de salida [0,2; 0,8], media 0,50 y DE 0,17. Correlaciona 0,61 con el log del PIB per cápita.
- Para S₀ se recomienda usar el valor de 1950, o el primer año disponible.
- Otra opción es usar S₀ = 0,5 + 0,15·z y estimar ese 0,15 en la calibración.
- **Advertencia teórica.** Turchin predice asabiya *alta en la frontera y baja en núcleos ricos*, mientras que los proxies de capacidad son altos en los núcleos ricos. Por eso el proxy mide más "capacidad cohesiva" que asabiya en sentido estricto. Se recomienda calibrar dos versiones:
  - (a) S₀ igual al proxy;
  - (b) S₀ igual al proxy de cohesión solo (`cohesion_index`), con el decaimiento g(y) haciendo el resto.

## 4. Objetivos de calibración

1. **Frecuencia de inicio de conflicto** 1950–2019 ≈ 3,4 % de los país-año, e incidencia ≈ 11,3 % (panel).
2. **Gradiente de incidencia por bulto juvenil:** 3,5 % (< 20 %), 8 % (20–25 %), 13 % (25–35 %), 17 % (> 35 %).
3. **Semielasticidad logit del bulto** ≈ 0,035–0,04 por pp, **manteniendo** log PIBpc ≈ −0,3 y log población ≈ +0,4.
4. **Pronóstico de población:** error de `pop` simulada frente a `pop_wpp` en 2020–2030 inferior al intervalo del 80 % de WPP.
5. **Asabiya:** rango de S entre países ≈ 0,2–0,8, correlación S–capacidad ≈ 0,8, y logit de inicio con coeficiente de S negativo (−1 a −3).
6. **Dividendo demográfico:** el crecimiento per cápita del modelo en Asia oriental en 1965–1990 debería atribuir ≈ 1/4–1/3 a Δ`share_15_64`.

## Referencias principales

Alesina, A., Devleeschauwer, A., Easterly, W., Kurlat, S., Wacziarg, R. (2003). Fractionalization. *J. Economic Growth* 8:155–194. · Besley, T., Persson, T. (2011). *Pillars of Prosperity*. Princeton. · Bloom, D., Williamson, J. (1998). Demographic transitions and economic miracles in emerging Asia. *World Bank Econ. Rev.* 12:419–455. · Bockstette, V., Chanda, A., Putterman, L. (2002). States and markets: the advantage of an early start. *J. Econ. Growth* 7:347–369. · Buhaug, H., Urdal, H. (2013). An urbanization bomb? *Global Env. Change* 23:1–10. · Cederman, L.-E., Wimmer, A., Min, B. (2010). Why do ethnic groups rebel? *World Politics* 62:87–119. · Cincotta, R. (2008). How democracies grow up. *Foreign Policy*. · Collier, P., Hoeffler, A. (2004). Greed and grievance in civil war. *Oxford Econ. Papers* 56:563–595. · Dražanová, L. (2020). Introducing the Historical Index of Ethnic Fractionalization (HIEF). *J. Open Humanities Data* 6. · Easterly, W., Levine, R. (1997). Africa's growth tragedy. *QJE* 112:1203–1250. · Fearon, J., Laitin, D. (2003). Ethnicity, insurgency, and civil war. *APSR* 97:75–90. · Goldstone, J. (1991). *Revolution and Rebellion in the Early Modern World*. · Goldstone, J. et al. (2010). A global model for forecasting political instability. *AJPS* 54:190–208. · Hanson, J., Sigman, R. (2021). Leviathan's latent dimensions. *J. Politics* 83:1495–1510. · Knack, S., Keefer, P. (1997). Does social capital have an economic payoff? *QJE* 112:1251–1288. · Montalvo, J., Reynal-Querol, M. (2005). Ethnic polarization, potential conflict, and civil wars. *AER* 95:796–816. · Nardulli, P. et al. (2012). Composition of Religious and Ethnic Groups (CREG). · Turchin, P. (2003). *Historical Dynamics*. Princeton. · Turchin, P. (2006). *War and Peace and War*. · Turchin, P., Currie, T., Turner, E., Gavrilets, S. (2013). War, space, and the evolution of Old World complex societies. *PNAS* 110:16384–16389. · UN DESA (2024). *World Population Prospects 2024*. · Urdal, H. (2006). A clash of generations? *ISQ* 50:607–630. · Urdal, H., Hoelscher, K. (2012). Explaining urban social disorder and violence. *Int. Interactions* 38:512–528. · Vogt, M. et al. (2015). Integrating data on ethnicity, geography, and conflict: EPR-ETH. *JCR* 59:1327–1342. · Wallace, J. (2014). *Cities and Stability*. OUP. · Zak, P., Knack, S. (2001). Trust and growth. *Economic Journal* 111:295–321.

**Nota de incertidumbre.** Algunos coeficientes citados de memoria (Fearon-Laitin, Bloom-Williamson, Goldstone et al.) son aproximados y deben verificarse contra las tablas originales antes de publicar. Los valores de Turchin (r₀ = 0,2, δ = 0,1, h = 2, S_crit = 0,003) proceden de réplicas del modelo de 2003 (p. ej. `dmely/cliodynamics`, CoMSES "Replica of Turchin's (2003) Metaethnic Frontier model"). Su equivalencia en años (≈ una generación por paso) es una interpretación.
