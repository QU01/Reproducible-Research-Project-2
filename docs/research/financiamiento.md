# Ahorro, financiamiento y costos de ajuste

## Por qué hace falta este bloque

Antes de este bloque, las políticas de RL repartían un presupuesto fijo del 35 % del PIB, y el consumo era el resto. Gastar más no tenía más costo que ese consumo, y endeudarse con el exterior no era una opción. La política óptima llevaba el 92–95 % del gasto a capital doméstico, algo que ningún país hace.

En los datos pasan tres cosas que faltaban:

1. **La inversión adicional se financia en parte con ahorro propio y en parte con el exterior.** Esto se conoce como el hallazgo de Feldstein–Horioka (1980): el ahorro y la inversión nacionales se mueven juntos. Aun así, una parte del aumento de la inversión se refleja en déficit de cuenta corriente.
2. **El crédito externo tiene límites.** Los déficits de cuenta corriente rara vez superan cierto nivel sin una "parada súbita" (Calvo 1998; Milesi-Ferretti y Razin 1998). La deuda externa además paga primas crecientes y se tiene que amortizar.
3. **Invertir mucho más de lo normal rinde menos.** Hay costos de ajuste del capital (Hayashi 1982; Abel y Eberly 1994) y una capacidad de absorción limitada de la inversión pública (Presbitero 2016; Gurara et al. 2020).

## Datos

| Variable | Fuente | Cobertura |
|---|---|---|
| Formación bruta de capital fijo / PIB (`acc_k`) | Banco Mundial WDI, completado con PWT `csh_i` | 1950–2019, 10 292 país-año |
| Cuenta corriente / PIB (`ca_gdp`) | Global Macro Database (Müller et al. 2025) | 1950–2019, 7 662 país-año |
| Deuda pública / PIB | Global Macro Database, IMF HPDD | 8 330 país-año |

El ahorro nacional se obtiene por identidad: S = I + CA.

## Estimación (etapa 1, `src/submodels.py`, reestimada en cada corte)

**Parte de la inversión adicional financiada con ahorro propio (η).** Se estima en diferencias dentro de cada país con efectos de año:

ΔCA_it = (η − 1)·ΔI_it + año_t + ε_it

La muestra excluye saltos mayores a 15 puntos en I y a 20 puntos en CA. Los errores estándar son robustos (HC0).

| Muestra | ΔCA/ΔI | η | e.e. | n |
|---|---|---|---|---|
| 1950–1970 | −0,59 | 0,41 | 0,08 | 400 |
| 1950–1990 | −0,51 | 0,49 | 0,04 | 2 447 |
| 1950–2019 | −0,46 | 0,54 | 0,02 | 7 226 |
| 1990–2019 | −0,43 | 0,57 | 0,03 | 4 916 |
| Diferencias quinquenales | −0,42 | 0,58 | 0,06 | 1 294 |

Cuando un país sube su inversión en un punto del PIB, entre 0,4 y 0,6 puntos salen del exterior. Esto es coherente con que el coeficiente de Feldstein–Horioka haya caído con la apertura financiera. En nuestros datos, el coeficiente en cortes transversales por décadas es 0,15 en 1960, 0,23 en 1980 y 0,30 en 2000, con muestras cada vez más amplias.

**Techo del déficit (cm0).** Es el percentil 90 del déficit de cuenta corriente con los datos hasta el corte:
- 3,9 % del PIB con datos hasta 1970, porque bajo Bretton Woods la movilidad de capital era baja;
- 13 % con datos hasta 1990 y hasta 2019.

Probé a condicionar el techo con una regresión cuantílica sobre la centralidad y la deuda, y los signos salieron al revés de un límite de oferta de crédito. Los países del centro tienen déficits pequeños porque no los necesitan, y la deuda alta acompaña a déficits grandes. Por eso uso el percentil incondicional. El costo creciente del crédito lo recogen las primas por deuda y la probabilidad de crisis, que ya estaban en el modelo.

## Mecánica (`src/model.py`, bloque "financing")

Los canales que usan ahorro o divisas son k, r, m, x y f. La redistribución w es una transferencia interna y no cuenta. Sea B la suma de esos canales y B_ref su trayectoria de referencia:
- en modo observado, las acciones observadas;
- en modo pronóstico, la media de los 10 años anteriores al origen.

- **Gasto adicional:** ΔB = B − B_ref.
- **Endeudamiento deseado:** (1 − η)·ΔB.
- **Margen de crédito:** max(cm0 + CA_ref, 0), donde CA_ref es la cuenta corriente observada o su media previa al origen.
- **Endeudamiento efectivo:** si ΔB > 0, el mínimo entre el deseado y el margen. Si ΔB < 0, se presta al exterior.
- **Recorte forzado:** lo que excede el margen se paga con menos consumo.
- **Deuda externa adicional:** x' = x + endeudamiento − 0,10·x. Paga la tasa del país: la tasa real de EE. UU., más la prima periférica, más la prima por deuda sobre el umbral. El interés sale del ingreso nacional y va a los acreedores del centro. La amortización (unos 10 años de vencimiento) sale del consumo. Esta deuda se suma a la deuda total, así que también sube las primas y el riesgo de crisis.
- **Consumo:** el de antes más el endeudamiento, menos la amortización. Así, lo que no se financia con deuda sale del consumo.
- **Ingreso de las masas:** baja en proporción a su participación (1 − E) por la parte del gasto adicional que se paga con recursos propios y por la amortización. Esto eleva el potencial de movilización de masas (MMP) y el índice de estrés político (PSI).
- **Costo de ajuste del capital:** K' = (1 − δ)K + I − (χ/2)(I/K − δ − 0,04)²K. El costo tiene un tope del 90 % de I.

Con las acciones observadas, ΔB = 0 y no cambia nada: la calibración histórica solo se ve afectada por el costo de ajuste.

## Calibración de χ (etapa 2)

χ entra como parámetro libre, en un rango de 0 a 40, en la evolución diferencial. Con los demás parámetros fijos en su calibración anterior, la pérdida cambia así:

| χ | 0 | 1 | 3 | 10 | 20 | 40 | 80 |
|---|---|---|---|---|---|---|---|
| RMSE log PIB pc (R = 8) | 0,575 | 0,571 | 0,554 | **0,510** | 0,535 | 0,598 | 0,649 |

Los datos identifican un χ interior, cerca de 10. Con I/K en 0,2 (una inversión del 60 % del PIB con K/Y = 3), esto hace que buena parte de la inversión adicional se pierda.

## Limitaciones

- η es un coeficiente promedio. En realidad depende de la apertura financiera, del régimen cambiario y de si la inversión es pública o privada.
- El techo del déficit es fijo por corte. No hay paradas súbitas endógenas más allá de las crisis del modelo.
- La deuda externa adicional se modela aparte de la deuda pública observada. No hay composición por moneda, que es el "pecado original" de Eichengreen y Hausmann.
- No hay ahorro de los hogares con motivos de ciclo de vida. La parte η es una elasticidad reducida.

## Referencias

- Abel, A. y Eberly, J. (1994). A unified model of investment under uncertainty. *AER* 84(5).
- Calvo, G. (1998). Capital flows and capital-market crises: the simple economics of sudden stops. *J. Applied Economics* 1(1).
- Feldstein, M. y Horioka, C. (1980). Domestic saving and international capital flows. *Economic Journal* 90.
- Gurara, D., Kpodar, K., Presbitero, A. y Tessema, D. (2020). On the capacity to absorb public investment: how much is too much? *World Development* 136.
- Hayashi, F. (1982). Tobin's marginal q and average q: a neoclassical interpretation. *Econometrica* 50(1).
- Milesi-Ferretti, G. M. y Razin, A. (1998). Sharp reductions in current account deficits. *European Economic Review* 42.
- Müller, K., Xu, C., Lehbib, M. y Chen, Z. (2025). The Global Macro Database. NBER WP 33714.
- Presbitero, A. (2016). Too much and too fast? Public investment scaling-up and absorptive capacity. *J. Development Economics* 120.
