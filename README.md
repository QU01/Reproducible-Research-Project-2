# Atlas del Sistema-Mundo

Modelo agéntico de 180 países (1950–2019, proyección a 2030) que combina:

| Bloque | Qué aporta | Datos que lo anclan |
|---|---|---|
| **Sistema-mundo** (Wallerstein, Emmanuel, Amin) | Centro/semiperiferia/periferia por productividad relativa. Intercambio desigual sobre la red real de comercio bilateral, rentas de monopolio sobre bienes de alto valor, intereses de la deuda periférica hacia el centro. | COW Dyadic Trade 1950–2014, PWT price levels, ECI, WDI FDI |
| **Demografía estructural** (Goldstone, Turchin) | Captura de élites (anclada en el top 10 % del WID), sobreproducción de élites, movilización de masas con protuberancia juvenil y PSI = MMP × EMP × SFD, donde SFD incluye la deuda. PSI y factores de riesgo determinan el conflicto civil. | WID, SWIID, Barro-Lee, UN WPP 2024, UCDP/PRIO |
| **Frontera metaétnica** (Turchin) | Asabiya inicial a partir de proxies de cohesión y capacidad estatal. Crece en la frontera (drenaje, extracción extranjera) y decae en centros ricos. | V-Dem, CREG, EPR, WVS, rivalidades |
| **Recursos** (Hubbert) | Capacidad bruta de extracción logística en lo ya extraído, con fracciones iniciales físicas por país. La extracción extranjera compite con la nacional, hay nacionalizaciones y regalías por época, y el precio mundial es de equilibrio. | OWID energy, reservas, yacimientos gigantes, rentas del Banco Mundial, nacionalizaciones |
| **Deuda y crisis** | Regla de reacción Δd = a + b·d + c·g + e·crisis + (r* − r̄)·d estimada con datos (reversión −0,027, crecimiento −0,30). Crisis por logit (deuda, tasa de EE. UU., crecimiento, contagio) con pérdida permanente. | Global Macro Database, IMF HPDD, Laeven-Valencia, JST |
| **Instituciones y geopolítica** | Golpes (trampa del golpe, Guerra Fría), transiciones y quiebres democráticos, impulso de la democracia a la productividad, ayuda oficial. | Powell-Thyne, V-Dem RoW, Archigos, ATOP, WDI ODA |
| **Clima y ecología** | Emisiones de la extracción fósil, temperatura global por TCRE y escalamiento por país. Daño Burke-Hsiang-Miguel con persistencia, desastres que destruyen capital, capital natural degradado por la huella ecológica. | OWID CO₂, HadCRUT/GISTEMP, UDel/FAO, EM-DAT, Global Footprint Network |

Cada país reparte cada año un presupuesto entre seis canales: **k** capital, **r** tecnología (I+D y educación, con saltos tecnológicos estocásticos), **m** importaciones de alto valor, **x** extracción propia, **f** extracción en el exterior y **w** redistribución.

## Problema inverso: cómo deciden realmente los países

1. **Acciones observadas** (`src/sources/acciones.py`): formación de capital, importaciones de manufacturas, rentas, I+D + educación pública, IED saliente y gasto social o transferencias, como % del PIB.
2. **Clonación de conducta** (`src/behavior.py`): regla de ajuste parcial en escala logit, z_t = ρ·z_{t−1} + β·estado + efecto país. Los hiperparámetros se eligen por validación fuera de muestra (el error medio es un 5 % menor que el de la persistencia).
3. **Recompensa revelada** (`src/irl.py`): estimador de Bajari, Benkard y Levin (2007). Con la regla observada y desviaciones simuladas del mismo mundo, con números aleatorios comunes, se buscan los pesos θ de la recompensa r = θ·φ con los que la conducta observada es mejor que sus desviaciones. Las características φ son bienestar, poder, ingreso de la élite, paz, autonomía en recursos e inercia (costo de ajuste). Se reporta el índice de racionalidad, bootstrap por países y heterogeneidad por zona, régimen y década.
4. **RL con la recompensa revelada** (`src/rl.py`, modo `irl`): PPO con esa recompensa, para comparar lo que "deberían" hacer los países con lo que hicieron.

## Validación

`src/validate.py` pronostica desde 49 orígenes (1970–2018) a 1, 5 y 10 años.

- Cada origen usa parámetros calibrados solo con datos hasta el último corte anterior (1970, 1980, 1990, 2000, 2010) y la regla de decisión estimada hasta ese año.
- Después del origen, golpes, regímenes, crisis, nacionalizaciones, clima y desastres son endógenos, y las series exógenas quedan congeladas. La excepción es la población, que se toma observada.
- Referencias: persistencia, derivas, AR(1), regresión panel directa, logit histórico y tendencia.
- Ablaciones: apagar cada teoría o módulo con los mismos parámetros.

## Calibración en dos etapas

- **Etapa 1** (`src/submodels.py`): golpes, transiciones de régimen, crisis, reacción fiscal y nacionalizaciones se estiman directamente con datos hasta el corte (logit / MCO).
- **Etapa 2** (`src/calibrate.py`): 22 parámetros estructurales por evolución diferencial sobre trayectorias simuladas. Se ajustan PIB per cápita, dispersión del crecimiento, conflicto, rentas de recursos, deuda, participación del 10 % más rico y cobertura de las bandas.

## Flujo de trabajo

```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python src/fetch_data.py           # PWT, UCDP, V-Dem, Banco Mundial, Natural Earth
python src/data_prep.py            # -> data/processed/panel.csv
for s in acciones elites finanzas comercio recursos geopolitica demografia clima; do
  python -c "import sys; sys.path.insert(0,'src'); from sources import $s; $s.build()"; done
python src/merge_sources.py        # -> data/processed/panel_full.csv (+ world_full.csv)
python src/calibrate.py            # calibración final 1950-2019 -> results/calibration.json
python -c "import sys; sys.path.insert(0,'src'); import validate; validate.run_rolling_calibration()"
python src/irl.py                  # reglas de decisión + recompensa revelada -> results/irl.json
python src/validate.py             # validación multi-corte -> results/validation.json
python src/rl.py                   # PPO: bienestar, poder, élite, irl -> results/policy_*.npy
python src/recommend.py            # recomendaciones incrementales -> results/recomendaciones.json
python src/osint.py                # capas OSINT abiertas -> dashboard/osint/*.json
python src/analyze.py              # -> results/dashboard_data.json
python src/build_dashboard.py      # -> dashboard/index.html + data.json, geo.json (publicar con osint/ e img/)
```

Las notas de investigación de cada módulo (datos, cobertura, literatura, ecuaciones y parámetros con citas) están en `docs/research/`.

## Ahorro, financiamiento y recomendaciones incrementales

- **Financiamiento** (`src/model.py`, `docs/research/financiamiento.md`):
  - Gastar por encima de la trayectoria de referencia se paga en un 54 % con ahorro propio (estimado con ΔCA/ΔI = −0,46) y el resto con deuda externa, hasta un techo de déficit del 13 % del PIB. Más allá del techo, el país recorta el consumo por la fuerza.
  - La deuda externa extra paga la tasa del país y se amortiza en unos 10 años.
  - El capital tiene costos de ajuste cuadráticos, con χ calibrado en 12.
  - Las políticas de RL eligen también cuánto gastar, entre el 10 % y el 60 % del PIB.
- **Recomendaciones incrementales** (`src/recommend.py`): PPO anclado a la regla de decisión estimada, con ajustes acotados a ×0,61–×1,65 y una penalización por alejarse. Se entrena en modo pronóstico con episodios de 20 años desde 1980–2019 y se compara con la regla bajo los mismos números aleatorios. Para cada país reporta el cambio por canal, el efecto en consumo, PIB, deuda y conflicto, la probabilidad de mejora y la robustez del signo entre conjuntos de parámetros calibrados con datos hasta 2000, 2010 y 2019.

## Globo 3D y capas OSINT

El dashboard es un globo 3D ([globe.gl](https://github.com/vasturiano/globe.gl)) con la capa del modelo por año y capas OSINT abiertas (`src/osint.py`):

| Capa | Fuente |
|---|---|
| Conflictos geolocalizados 1989–2023 | UCDP GED v24.1 |
| Rutas marítimas | Benden 2021, derivadas de AIS |
| Comercio bilateral | Correlates of War |
| Rutas aéreas | OpenFlights |
| Centrales eléctricas | WRI |
| Ductos, terminales de GNL y yacimientos | Global Energy Monitor |
| Reactores nuevos | GeoNuclearData |
| Cables submarinos | TeleGeography |
| Puertos | NGA World Port Index |
| Muestras reales de aviones (París) y barcos (Gotemburgo) | ADS-B / AIS |

El visor de artifacts no puede leer feeds en tiempo real. La versión con datos en vivo (OpenSky, AIS, noticias y sismos) está integrada en [Quasarbroker](https://github.com/QU01/Quasarbroker) (rama `claude/world-systems-agent-model-p0omqe`): módulo SISTEMA-MUNDO, API `/api/worldsystem/*` y selector MAPA 2D / GLOBO 3D.

## Resultados principales

**Ajuste en muestra (1950–2019, con financiamiento):**

- RMSE del log PIB per cápita: 0,51;
- cobertura de la banda p10–p90: 61 % (nominal 80 %);
- RMSE de deuda/PIB: 0,39;
- RMSE de la participación del top 10 %: 0,14.

**Problema inverso:**

- La regla estimada de ajuste parcial supera a la persistencia en 5 de 6 canales, en torno a un 5 % a 5–10 años.
- La recompensa revelada (BBL) da pesos inercia 0,84, poder 0,47, bienestar −0,28 y el resto ≈ 0. La conducta observada vence al 58 % de sus desviaciones; las recompensas teóricas explican 50–52 % y unos pesos al azar, 50 %.
- El centro valora la paz (0,97).

**Validación fuera de muestra (49 orígenes, 1970–2018):**

| Variable | Horizonte | Modelo | Mejor referencia |
|---|---|---|---|
| log PIB pc, CRPS | 5 años | **0,119** | 0,127 (panel) |
| log PIB pc, CRPS | 10 años | **0,180** | 0,215 (AR1) |
| log PIB pc, RMSE | 1 / 5 / 10 años | 0,116 / 0,222 / 0,323 | **0,061 / 0,190 / 0,300** (AR1) |
| Correlación del crecimiento | 10 años | **0,20** | 0,11 |
| Conflicto, Brier (AUC) | 5 años | 0,079 (0,84) | **0,066 (0,90)** logit histórico |
| Deuda/PIB, RMSE | 5 / 10 años | **0,31 / 0,45** | 0,33 / 0,47 persistencia |
| Temperatura global, RMSE | 5 / 10 años | **0,158 / 0,134 °C** | 0,182 / 0,209 tendencia |
| Rentas de recursos, RMSE | 10 años | **0,068** | 0,071 persistencia |

- La banda p10–p90 cubre un 60–70 % en lugar del 80 % nominal.
- Frente a la versión sin financiamiento, el ajuste en muestra mejora y el pronóstico fuera de muestra empeora algo (CRPS a 10 años 0,170 → 0,180).

**RL, con elección del gasto:**

- bienestar gasta el 28 % del PIB y se vuelve acreedor neto;
- poder gasta el 46 % y lleva la deuda mediana al 68 %;
- élite redistribuye el 20 %.

**Recomendaciones ancladas (objetivo de bienestar):**

- Recortar el gasto unos 10 puntos del PIB, sobre todo capital (−7) e importaciones de alto valor (−2,8).
- El consumo sube un 6 % en 2020–2030, el PIB cae un 6,5 % a 10 años y la deuda baja 29 puntos.
- El signo del gasto es robusto en 176 de 180 países.
- A 20 años la ganancia de consumo se reduce a +3,4 % y el PIB queda un 8 % abajo.
- Este resultado depende del costo de ajuste calibrado, que pierde el 27 % de la inversión histórica, así que hay que revisarlo antes de interpretarlo como recomendación.
- Con la recompensa revelada (poder) sale lo contrario: invertir 19 puntos más, endeudarse y recortar el consumo casi un 30 %.

**Proyección a 2030:**

- crecimiento del PIB per cápita mundial: 1,3 % anual;
- temperatura global: 1,39 °C;
- democracias: 57 %;
- deuda mediana: 48 % del PIB;
- probabilidad media de conflicto: 12 %.
