# Cola de espera por estación — metodología, supuestos y limitaciones

Acompaña a `cola_espera.ipynb` (generado desde `scripts/build_cola.py`) y al código de
`src/stations.py` y `src/queues.py`.

Datos: dump del 2026-09-02, ventana 2026-07-03 a 2026-09-02.

---

## 1. Alcance

**Sólo la troncal Macrobús T1** (`route.id_route = 2`, `id_ruta_estacion 79001001`).

T01 quedó fuera pese a estar en el brief, y no por decisión de alcance sino porque el dato
no existe. En T01 la validación es **a bordo**, así que el evento AFC *es* el abordaje y no
hay cola de espera que reconstruir. Tres evidencias independientes:

| Evidencia | T1 (troncal) | T01 |
|---|---|---|
| `idDispositivo` de la validación | 182 torniquetes, mapean a 27 estaciones | 25 valores = exactamente `bus.id_bus` de las unidades T01 |
| `idRutaEstacion` | 79001001, y el 100 % mapea a estación | valor único 100 (la ruta) |
| `afc_bus_total.all_passengers` | **0** pasajeros a bordo | 818 519 pasajeros a bordo |

Es decir: en la troncal nadie valida arriba del camión y en T01 nadie valida en estación.
La premisa del brief se confirma para T1 y se invierte para T01.

Alimentadoras (ruta 31) fuera de alcance por instrucción.

## 2. Cadena de identidad

Ninguno de los enlaces es obvio, y el nombre de la columna estorba:

```
transaction_1.idDispositivo
  → afc_station_device_total.id_vehicle
  → afc_station_device_total.id_station
  → mac_station.id / .name
```

- `transaction_1.idRutaEstacion` **no** es la estación pese al nombre: es
  `route.id_ruta_estacion`, o sea la ruta.
- `transaction_1.idUbicacion` es `0` en toda la troncal. Inservible.
- Cobertura de la cadena: **100 %** de las 5 523 090 validaciones de la troncal.

Para el GPS aplican además los desfases de identidad ya documentados en `CLAUDE.md`
(`id_bus + 10000`, `id_route = id_ruta_estacion`). Resueltos en `src/fleet.py`.

## 3. Geometría de estaciones

`in_route_point_control` con `id_route = 2` reparte las estaciones entre direcciones: 25 en
`direction = 3` y las dos de los extremos (Fray Angélico, Mirador) en `direction` 1 y 2.
Juntas dan las **27 estaciones** que tienen torniquetes en el AFC. Las Juntas existe en
`mac_station` pero no tiene torniquetes y no participa.

El enlace entre geometría y AFC es por **nombre normalizado** (sin acentos ni puntuación).
Tres pares se escriben distinto en cada catálogo y están fijados a mano en
`stations.catalogo_estaciones`:

| `in_route_point_control` | `mac_station` |
|---|---|
| Esculturas | Escultura |
| Monte Olivete | Monte Olivette |
| Independencia Norte | Independencia Nte. |

La función falla explícitamente si el resultado no son 27 filas, para que un cambio de
catálogo no pase inadvertido.

## 4. Detección de pasos de camión

### Radio

**150 m** alrededor de cada estación. Acotado por ambos lados:

- **Por arriba:** la separación mínima entre estaciones es 336 m (Esculturas ↔ Fray
  Angélico). Con 150 m los discos no se traslapan.
- **Por abajo:** el GPS muestrea cada ~20 s. A 50 km/h la unidad avanza 278 m entre pings,
  así que un radio menor dejaría pasar unidades sin registrar ninguna posición.

### Agrupación en visitas

Pings contiguos de la misma unidad en la misma estación forman una visita. Dos pings
separados por más de **15 min** son visitas distintas (una vuelta completa no baja de
~30 min, así que el umbral no puede partir una visita real).

### Reconstrucción de pasos no observados

Aun con 150 m, la detección directa da ~450 pasos/día en las estaciones centrales contra
~526 vueltas/día — un **86 %**. Los pasos perdidos son unidades rápidas que cruzan el disco
entre dos pings. Importan porque un paso no detectado hace creer al modelo que nadie recogió
a esa gente, e **infla la cola**.

La corrección aprovecha que la ruta es fija y sin ramales: si una unidad aparece en la
estación de orden 5 y luego en la de orden 8, forzosamente pasó por 6 y 7. Se interpolan sus
tiempos linealmente sobre el orden, sólo cuando el hueco temporal es compatible con marcha
continua (≤ 25 min). Un hueco mayor significa que la unidad salió de circulación, y ahí no se
inventa nada.

Las filas reconstruidas quedan marcadas con `interpolado = True`.

### Validación

La mediana de pasos por estación tras la reconstrucción es **525/día**, contra **526
vueltas/día** que `src/departures.py` deriva por un camino completamente distinto (salidas de
terminal detectadas en las zonas terminales). Dos métodos independientes convergen, lo que
da confianza en que la reconstrucción no está inventando pasos.

**26 % de los pasos usados son reconstruidos, no observados.**

## 5. Modelos de cola

Los dos flujos —personas que entran y camiones que pasan— sólo interactúan en los instantes
de paso, así que no hace falta simular minuto a minuto. Basta contar cuántas personas
validaron entre un camión y el siguiente:

```
llegadas_i = validaciones entre el paso i-1 y el paso i
cola_i     = personas presentes cuando llega el camión i
```

### (a) Vaciado total

Supuesto del brief: cada camión se lleva a todos.

```
cola_i = llegadas_i
```

Es un **piso**: si con este supuesto ya salen colas grandes, la realidad sólo puede ser peor.

Resultado, día hábil 06–20 h: media **6.8**, mediana **3**, p95 **26**, p99 **57**.

### (b) Capacidad finita

El camión se lleva a lo más `C` personas y el resto se queda:

```
cola_i = max(0, cola_{i-1} − C) + llegadas_i
```

Con `C → ∞` se recupera (a). Cada día y cada estación arrancan con la cola en cero, porque
el servicio se interrumpe de noche.

### Comparación y capacidad crítica

No hay dato de capacidad en la BD. En lugar de inventar un número, se barre `C`:

| capacidad | % de pasos que dejan gente | personas al cierre del día | cola media |
|---|---|---|---|
| 10 | 36.2 | 725 | 300.1 |
| 20 | 12.8 | 312 | 129.4 |
| 30 | 6.3 | 155 | 88.1 |
| 40 | 3.9 | 54 | 60.4 |
| 60 | 1.8 | 0.5 | 23.2 |
| 80 | 1.0 | 0.0 | 11.5 |
| 160 | 0.2 | 0.0 | 7.0 |

La transición es nítida alrededor de **C ≈ 60**. Por debajo el sistema no desaloja y la
gente se acumula hasta el cierre; por encima el residual se va a cero y la cola media
converge al valor de (a) — 6.96 con C=160 contra 6.78 con vaciado total.

**Conclusión:** el supuesto de vaciado total del brief es defendible siempre que la
capacidad efectiva por paso supere ~60 personas. Un articulado de BRT ronda 100–160, así que
probablemente se sostiene, pero hay que confirmarlo.

Esto además acota la pregunta pendiente de capacidad: para este análisis **no hace falta el
número exacto, basta saber si supera 60**.

## 6. Limitaciones

Ordenadas por cuánto pesan sobre las conclusiones.

### 6.1 Sesgo en las dos terminales

Mirador y Fray Angélico registran ~265 pasos/día contra ~525 del resto, con intervalo
mediano de 3.0–3.2 min contra 1.5–1.6 min. La causa: ahí la unidad llega, hace base y sale,
y los pings quedan contiguos, así que llegada y salida se fusionan en **una sola visita** en
lugar de contarse como dos pasos.

Efecto: sus colas están sobreestimadas del orden de **2×**. **Deben leerse como cota
superior, no como estimación.** No es menor — Fray Angélico es la estación de mayor volumen
de la troncal (696 610 validaciones).

Corregirlo requiere separar "llegada de una vuelta" de "salida de la siguiente" dentro de la
zona terminal, cruzando con los eventos que ya produce `src/departures.py`. Pendiente.

### 6.2 El AFC no registra el sentido

Por cada estación pasan camiones en ambas direcciones, y una persona espera uno concreto. La
validación no dice cuál. Tratar todos los pasos como si sirvieran a toda la cola
**sobreestima la capacidad de desalojo** en aproximadamente 2×.

El sentido de cada *paso* sí es inferible (`stations.con_sentido`, por el orden creciente o
decreciente de estaciones), pero el de cada *persona* no lo es a partir del AFC. Para
repartir la cola habría que modelar la matriz origen-destino, que no está en estos datos.

### 6.3 Un cuarto de los pasos es reconstruido

26 % de los pasos vienen de interpolación (§4). El supuesto —ruta fija, sin ramales— es
sólido, pero los tiempos interpolados son lineales sobre el orden de estaciones y no
consideran que unos tramos son más lentos que otros.

### 6.4 La capacidad es un parámetro, no un dato

Ver §5. La BD no guarda capacidad ni costo por unidad, en ninguna de sus 303 columnas.

### 6.5 Sólo se observa la demanda atendida

El AFC registra a quien entra a la estación, no a quien vio la fila y desistió, ni a quien no
salió de su casa. **La cola estimada es un piso de la demanda real.** Esta limitación es de
fondo y no se resuelve con más procesamiento de estos datos.

### 6.6 Cobertura del cruce

96.5 % de las validaciones quedan asignadas a un intervalo entre pasos. El 3.5 % restante
cae fuera de la franja de servicio (05–23 h) o antes del primer paso del día.

## 7. Qué sigue

- **Corregir el sesgo de terminales** (§6.1) cruzando con `src/departures.py`.
- **Materializar a Parquet** en `data/export/` las features por estación y ventana, listadas
  en `cola_espera.ipynb` §10. El loop de entrenamiento no debe tocar MySQL.
- **Confirmar con el cliente** si la capacidad efectiva por paso supera 60 (§5). Es la única
  pregunta que hace falta responder para cerrar el modelo de cola.
