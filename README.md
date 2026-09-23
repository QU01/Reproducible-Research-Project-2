# Atlas del Sistema-Mundo

Modelo agéntico híbrido que combina tres teorías macrohistóricas:

| Teoría | Qué aporta al modelo |
|---|---|
| **Sistema-mundo** (Wallerstein, Emmanuel, Amin) | Centro / semiperiferia / periferia según productividad relativa; intercambio desigual (τ), rentas de monopolio sobre bienes de alto valor (μ), IED que busca rendimiento y repatria beneficios. |
| **Demografía estructural** (Goldstone, Turchin) | Las élites capturan una parte del producto y de las rentas que entran al país → sobreproducción de élites, estancamiento del ingreso de masas, índice de estrés político PSI = MMP × EMP × SFD → riesgo de conflicto interno. |
| **Frontera metaétnica** (Turchin) | La cohesión colectiva (*asabiya*) crece en la frontera (periferia abierta y drenada por el centro) y decae en los centros ricos; eleva la capacidad estatal. |

Cada país es un agente que cada año produce `Y = A·K^α·(h·L)^(1−α)` y reparte un presupuesto
discrecional entre cinco canales:

* **k** capital doméstico · **r** tecnología/industria propia (saltos tecnológicos estocásticos, tipo Poisson)
* **m** importar bienes de alto valor del centro (consumo de calidad + tecnología incorporada, pero paga renta)
* **f** invertir en el exterior (capital hacia donde el rendimiento marginal es alto; los beneficios regresan)
* **w** redistribución (reduce la captura de élites y la movilización de masas)

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
* **UCDP/PRIO Armed Conflict Dataset** (vía el paquete de R `peacesciencer`): años de conflicto interno.
* **V-Dem / Polity** (vía `peacesciencer`): no se usan en la dinámica, quedan en el panel para extensiones.
* **Natural Earth 1:110m** (paquete `world-atlas`): fronteras para el mapa.

## Resultados

Dashboard: `dashboard/index.html` (mapamundi animado 1950–2019 con 6 escenarios y 8 capas).

### Validación (calibrado con 1950–1990, pronóstico ciego 1991–2019)

| log PIB pc, 2019 (180 países) | RMSE | Corr. crecimiento | Acierto de zona |
|---|---|---|---|
| **Modelo híbrido** | 0.54 | **0.22** | 0.84 |
| Persistencia | 0.72 | — | 0.88 |
| Deriva propia 1970–90 | 0.83 | 0.13 | 0.78 |
| Deriva global | 0.47 | −0.08 | 0.88 |
| Convergencia β | **0.47** | 0.24 | 0.88 |

| Conflicto interno 1991–2019 | AUC | Brier |
|---|---|---|
| Modelo (PSI + ingreso + asabiya) | 0.80 | **0.082** |
| Frecuencia pasada del país | **0.85** | 0.090 |

El modelo supera a la persistencia y a la deriva propia de cada país, pero no a las referencias
agregadas más simples en RMSE; aporta en ordenar el crecimiento relativo y en la calibración de la
probabilidad de conflicto. La banda p10–p90 cubre el 75 % de los casos en 2019 (ideal: 80 %).

### Políticas emergentes (PPO, 400 iteraciones × 3 recompensas)

1. **Primero comprar, después fabricar.** La periferia importa bienes de alto valor (38 %) e invierte en tecnología propia (23 %); al acercarse a la frontera, la importación cae del 55 % al 4 % y domina el capital: sustitución de importaciones espontánea.
2. **Tecnología temprano, capital tarde.** El peso de la tecnología pasa del 58 % (1950s) al 6 % (2010s); los saltos estocásticos rinden más cuanto antes llegan.
3. **Nadie elige ser rentista.** La inversión exterior se queda en ~1 %: la extracción del centro es estructural (τ, μ), no una elección.
4. **Bajo estrés, consumo importado.** Cuando sube el PSI, la política pasa del capital (87 %) a importar consumo (60 %).
5. **Élites autocontenidas.** Solo con la recompensa de élite aparece la redistribución (49 % en los 1950s): frena la sobreproducción de élites.
6. **El estrés se concentra en el centro.** El PSI del centro dobla al de la periferia en todos los escenarios, aunque el conflicto armado sigue siendo más periférico.
7. **Convergencia como techo teórico.** Gini entre países 2019: datos 0.47 · RL 0.32–0.36. Con la recompensa de poder (suma cero) hay menos movilidad ascendente (12 % vs 16 %).

Arquetipos (k-medias): *Acumulador* (centros tempranos: EE. UU., Canadá, Suiza, R. Unido, Golfo),
*Desarrollista tecnológico*, *Importador que aprende* y *Redistributivo* (solo con recompensa de élite).

### Límites

Demografía exógena; asabiya y élites son variables latentes con parámetros fijados, no estimados;
sin red de comercio bilateral; RL con parámetros compartidos y aprendizaje simultáneo (sin
equilibrio garantizado). Las políticas son óptimas *dentro del modelo*.
