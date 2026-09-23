# Atlas del Sistema-Mundo

Modelo agéntico híbrido que combina tres teorías macrohistóricas:

| Teoría | Qué aporta al modelo |
|---|---|
| **Sistema-mundo** (Wallerstein, Emmanuel, Amin) | Centro / semiperiferia / periferia según productividad relativa; intercambio desigual (τ), rentas de monopolio sobre bienes de alto valor (μ), IED que busca rendimiento y repatria beneficios. |
| **Demografía estructural** (Goldstone, Turchin) | Las élites capturan una parte del producto y de las rentas que entran al país → sobreproducción de élites, estancamiento del ingreso de masas, índice de estrés político PSI = MMP × EMP × SFD → riesgo de conflicto interno. |
| **Frontera metaétnica** (Turchin) | La cohesión colectiva (*asabiya*) crece en la frontera (periferia abierta y drenada por el centro) y decae en los centros ricos; eleva la capacidad estatal. |
| **Agotamiento de recursos** (Hubbert) | Capacidad bruta de extracción logística en lo ya extraído; el capital extractivo extranjero compite con el nacional por esa capacidad y acelera el agotamiento del anfitrión. |

Cada país es un agente que cada año produce `Y = A·K^α·R^ψ·(h·L)^(1−α−ψ)` (R = recursos naturales,
comprados a un precio mundial de equilibrio) y reparte un presupuesto discrecional entre seis canales:

* **k** capital doméstico · **r** tecnología/industria propia (saltos tecnológicos estocásticos, tipo Poisson)
* **m** importar bienes de alto valor del centro (consumo de calidad + tecnología incorporada, pero paga renta)
* **x** extracción propia de recursos naturales
* **f** invertir fuera en recursos de otros países (concesiones: compiten con la extracción del anfitrión; las rentas regresan menos una regalía)
* **w** redistribución (reduce la captura de élites y la movilización de masas)

### Recursos naturales

* Cada país tiene recursos recuperables últimos `U`; su **capacidad bruta de extracción** es logística en la
  fracción ya extraída `x = X/U`: `Cap = r_R·U·(x+ε)(1−x)` (curva de Hubbert). Sube mientras se abre el
  yacimiento y cae al agotarlo.
* Extracción = `Cap·(1−e^{−e})`, con `e` = capital extractivo (nacional + extranjero) / (c_R·Cap). El capital
  extranjero **compite** por la misma capacidad: se lleva su parte de la extracción, acelera el agotamiento y
  reduce la capacidad que le queda al país anfitrión, que solo conserva una regalía.
* Quien usa más recursos de los que controla (en casa o en concesiones fuera) paga un sobrecosto ζ, así que al
  agotar los propios conviene asegurarse recursos fuera.
* Las élites capturan una fracción mayor de la renta de recursos (maldición de los recursos) y la extracción
  extranjera alimenta la frontera metaétnica del anfitrión.
* Con Cobb-Douglas, la participación mundial de las rentas se toma de los datos (ψ_t); el modelo explica su
  reparto entre países.

Los saltos tecnológicos son en parte deterministas (difusión hacia la frontera, más rápida con
importaciones e IED) y en parte estocásticos (tasa creciente con la inversión en *r* y la asabiya;
tamaño creciente con la distancia a la frontera).

## Flujo de trabajo

```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python src/fetch_data.py      # PWT 10.01, UCDP/PRIO, V-Dem (espejos CRAN en GitHub) + Natural Earth
python src/data_prep.py       # -> data/processed/panel.csv (180 países, 1950-2019)
python src/calibrate.py       # calibración 1950-1990 + pronóstico ciego 1991-2019 -> results/calibration.json
python src/rl.py              # PPO multiagente, 3 regímenes de recompensa -> results/policy_*.npy
python src/analyze.py         # evaluación, arquetipos, curvas de respuesta -> results/dashboard_data.json
python src/build_dashboard.py # -> dashboard/index.html (autocontenido, abre en el navegador)
```

| Archivo | Contenido |
|---|---|
| `src/model.py` | Simulador vectorizado (R mundos Monte Carlo × N países) |
| `src/calibrate.py` | Evolución diferencial sobre momentos simulados + validación fuera de muestra |
| `src/rl.py` | PPO con parámetros compartidos (numpy + autograd) |
| `src/analyze.py` | Resultados, arquetipos (k-medias), curvas de respuesta de la política |
| `dashboard/` | Plantilla y dashboard con mapamundi animado |
| `results/` | Parámetros, métricas y políticas entrenadas |

## Datos

* **Penn World Table 10.01** (Feenstra, Inklaar y Timmer 2015): PIB real, población, stock de capital,
  capital humano, participación laboral, participaciones de inversión, exportaciones e importaciones.
* **Banco Mundial WDI** `NY.GDP.TOTL.RT.ZS`: rentas totales de recursos naturales (% del PIB), 1970–2019.
* **UCDP/PRIO Armed Conflict Dataset** (vía el paquete de R `peacesciencer`): años de conflicto interno.
* **V-Dem / Polity** (vía `peacesciencer`): no se usan en la dinámica, quedan en el panel para extensiones.
* **Natural Earth 1:110m** (paquete `world-atlas`): fronteras para el mapa.

## Resultados

Dashboard: `dashboard/index.html` (mapamundi animado 1950–2019, 6 escenarios, 12 capas).

### Validación (calibrado con 1950–1990, pronóstico ciego 1991–2019)

| log PIB pc, 2019 (180 países) | RMSE | Corr. crecimiento | Acierto de zona |
|---|---|---|---|
| **Modelo híbrido** | 0.52 | **0.24** | 0.83 |
| Persistencia | 0.72 | — | 0.88 |
| Deriva propia 1970–90 | 0.83 | 0.13 | 0.78 |
| Deriva global | 0.47 | −0.08 | 0.88 |
| Convergencia β | **0.47** | **0.24** | 0.88 |

| Conflicto interno 1991–2019 | AUC | Brier |
|---|---|---|
| Modelo (PSI + ingreso + asabiya) | 0.83 | **0.085** |
| Frecuencia pasada del país | **0.85** | 0.090 |

| Rentas de recursos / PIB (WDI) | RMSE 2000 | RMSE 2010 | RMSE 2019 | Spearman 2019 |
|---|---|---|---|---|
| Modelo | 0.057 | **0.072** | **0.055** | 0.88 |
| Persistencia de 1990 | **0.053** | 0.074 | 0.072 | **0.90** |

La banda p10–p90 del PIB cubre el 76 % de los casos en 2019 (ideal: 80 %).

### Políticas emergentes (PPO, 400 iteraciones × 3 recompensas)

1. **Agotados los recursos propios, se sale a buscar los ajenos.** La parte del presupuesto invertida en recursos fuera sube 17 / 11 / 4 puntos (poder / élite / bienestar) al pasar de reservas intactas a agotadas; la extracción propia hace lo contrario. Es una estrategia minoritaria (2–5 %) porque la capacidad logística limita lo que el capital adicional puede sacar.
2. **Los que salen fuera son otros extractivistas** (Omán, Turkmenistán, Surinam, Irak, Rusia), que reciclan sus rentas en concesiones ajenas.
3. **La competencia extractiva es un juego de poder:** con la recompensa de poder, el 53 % de la extracción periférica queda en manos extranjeras (35 % con bienestar); bajo estrés alto, hasta un 19 % del presupuesto va a recursos fuera.
4. **Élites rentistas que reparten:** estados petroleros con recompensa de élite extraen (16 %) y redistribuyen (12 %), con lo que frenan la sobreproducción de élites.
5. **Primero comprar, después fabricar:** la importación cae del 59 % al 3 % al acercarse a la frontera; la tecnología propia se concentra en los años 50.
6. **El estrés político se concentra en el centro** (PSI ≈ doble que en la periferia).
7. **Los recursos bajan el techo:** el Gini entre países baja a 0,26–0,30, pero el PIB per cápita mundial de RL se queda en unos 22–23 mil dólares; en 2019 queda un 37 % de las reservas y el precio se multiplica por 6–9 desde 1970.

### Límites

Un solo recurso genérico, sin descubrimientos ni sustitución (el precio sube de más); la participación mundial
de las rentas es exógena y las rentas anteriores a 1970 se rellenan con el valor de 1970; demografía exógena;
asabiya, élites, reservas últimas y propiedad de la extracción son latentes; sin redes bilaterales; RL con
parámetros compartidos y aprendizaje simultáneo. Las políticas son óptimas *dentro del modelo*.
