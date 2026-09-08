# Macrobús — Modelo de RL para despacho de unidades

## Qué se está construyendo

Un agente de aprendizaje por refuerzo que decide **a qué hora sale cada camión** a ruta.
Cliente: empresa transportista que opera Macrobús (Guadalajara).

Objetivo doble, en tensión:

- **Minimizar** el número de unidades despachadas (costo operativo).
- **Maximizar** los pasajeros transportados por vuelta (ingreso / nivel de servicio).

### Qué simplifica el problema

- La ruta es **fija**: todas las unidades dan la misma vuelta.
- Todas las vueltas son de **la misma distancia**.
- La telemetría es **100% automática vía GPS**, sin captura manual.

O sea: no hay que resolver ruteo ni asignación espacial. La decisión es **temporal**
(headway / momento de despacho) y el estado es demanda esperada + posición de la flota.

### Qué lo complica

Las unidades tienen **capacidades distintas** y por lo tanto **costos distintos**. La
acción no es sólo *cuándo* despachar, sino *con qué unidad*.

## Estado del repo (2026-09-07)

Hecho el EDA; falta el modelo. `test/` sigue vacío.

- `eda.ipynb` — entregable de EDA, ya ejecutado con salidas. **No editarlo a mano**: se
  genera desde `scripts/build_eda.py`.
- `src/` — ayudantes de análisis: `db.py` (conexión + cache Parquet), `fleet.py`
  (resolución de identidad), `departures.py` (inferencia de salidas), `demand.py`
  (perfiles de demanda AFC).
- `.macrobus/` — venv, **Python 3.14.7**. Instalados y funcionando: numpy, pandas, scipy,
  scikit-learn, plotly, matplotlib, pymysql, sqlalchemy, pyarrow, jupyter.
  Falta verificar wheels `cp314` para torch / gymnasium / stable-baselines3.
- `data/` — dumps SQL, Excel de definiciones y `cache/` de Parquet. Ignorado por git.
- `docs/` — diccionario de datos y notas del entorno.

## Entorno de datos

Los dumps viven en un container MySQL, no se leen como archivo. Detalle en
`docs/entorno-datos.md`.

```bash
docker compose up -d
bash scripts/load_dumps.sh          # sólo la primera vez
bash scripts/load_dumps.sh --reset  # recargar desde cero
```

- MySQL: `127.0.0.1:3307`, root / `macro`, BD `integration`
- Adminer: http://127.0.0.1:8080
- CLI: `docker compose exec mysql mysql -uroot -pmacro integration`

### Reglas del entorno — no revertir

- El tuning de InnoDB va como **flags en `command:`** del compose. Un `.cnf` montado
  desde Windows queda world-writable y `mysqld` lo descarta dejando sólo un warning.
- El datadir es un **volumen nombrado** (`macro_mysql_data`), nunca un bind mount a
  Windows: el FS compartido de Docker Desktop estrangula a InnoDB.
- `innodb_doublewrite=0` y `flush_log_at_trx_commit=0` son deliberados. La BD es
  reconstruible desde los dumps, no hay estado propio que perder.

## Mapa de datos

Diccionario completo (303 columnas, 18 tablas) en `docs/diccionario_datos.md`.
Las que importan para el modelo:

| Tabla | Contenido |
|---|---|
| `in_device_history_location` | GPS cada ~20 s: `latitude`, `longitude`, `speed`, `degree_course`, `id_bus`, `id_ebjdevice` |
| `transaction_1` | Validaciones AFC del Macrobús T1: `fechaHoraEvento`, `idRutaEstacion`, `tipoEvento` |
| `transaction_5` | Validaciones AFC de la ruta T01 (mismo esquema que `transaction_1`) |
| `afc_bus_total` | Agregado diario por camión, incluye `all_passengers` |
| `in_route_point_control` | Puntos de control con lat/lon y `direction`; sirve para cortar la vuelta en tramos |
| `bus_location_info` | `last` / `next` punto de control, `diff_time` (adelanto o retraso) |
| `bus` | 188 unidades: `id_route`, `model`, `brand` |

**Rutas.** `route.id_route`: `2` = Macrobús T1 (troncal), `7` = T01,
`31` = Alimentadoras (ruta padre de A03…A21). Los dumps vienen filtrados a
`id_route in (2,31,7)`.

### Gotchas verificados

Los dos primeros invalidan análisis en silencio. Están resueltos en `src/fleet.py` y
`src/departures.py`; usar esos módulos en vez de escribir los joins a mano.

**1. Dos relojes distintos en la misma BD.** No todo está en UTC:

| Columna | Tipo | Zona real |
|---|---|---|
| `in_device_history_location.time` | `TIMESTAMP` | **UTC** — restarle 6 h |
| `transaction_*.fechaHoraEvento` | `DATETIME` | **hora local** — no convertir |

`TIMESTAMP` se normaliza a UTC al guardar, `DATETIME` se guarda literal. Como el dump se
tomó con `TIME_ZONE='+00:00'`, sólo las `TIMESTAMP` salieron en UTC. Comprobado contra
`dev_date`/`dev_time`, la hora local que reporta el equipo GPS.

**2. Los identificadores del GPS no son lo que dicen.** Un join ingenuo
`gps.id_bus = bus.id_bus` resuelve **12 filas de 19 millones** y no marca error:

| Campo del GPS | Qué es realmente |
|---|---|
| `id_route` | `route.id_ruta_estacion` — la troncal es `79001001`, no `2` |
| `id_bus` (≠ 0) | `bus.id_bus + 10000` |
| `id_bus` = 0 | ruta T01; el enlace es `id_ebjdevice` → **`bus.id_oct`** (no `bus.id_ebjdevice`) |

Cobertura con ambos mecanismos: 19 156 260 de 19 156 273 pings.

**3. Otros.** `transaction_1` y `transaction_5` comparten esquema pero son rutas distintas;
unificar antes de agregar. Campos "en desuso" según el diccionario, no construir features
sobre ellos: `bus.id_dvr`, `bus.id_afc`, `bus.id_ceiba_device`,
`in_device_history_location.type_bus`, `bus_location_info.distance_between`.

## Hueco abierto que bloquea la recompensa

**Ninguna de las 303 columnas guarda capacidad de pasajeros ni costo por unidad.** Lo más
cercano es `bus.model` (valores `'1'` y `'2'`) y `bus.brand` (Dina, Mercedes Benz,
International).

La función de recompensa depende de ambos datos. Hay que pedirle al cliente una tabla de
mapeo `model` / `brand` → capacidad y costo por vuelta. Mientras tanto, tratar el costo
como **parámetro configurable**, no como dato derivado de la BD.

## Lo que encontró el EDA (`eda.ipynb`)

- **No hay tabla de despachos.** La hora de salida se infiere del GPS: se detecta cuándo la
  unidad abandona un radio de 250 m alrededor de la terminal. `src/departures.py`.
  32 616 salidas en jul–sep 2026, recorrido mediano 42.3 min (p90 53.6).
- **La oferta no sigue a la demanda.** En la franja 06–20 h de día hábil, la oferta varía
  1.25× pico/valle y la demanda 1.90×, con correlación **−0.03**. Ese desacople es la
  oportunidad del modelo.
- Cuidado al medir esa correlación: incluir las horas de arranque y cierre (05 h, 21–22 h)
  la infla hasta +0.52 de forma espuria, porque ahí ambas curvas suben y bajan juntas por
  el horario de servicio. Comparar siempre dentro de la franja núcleo.
- Ventana de servicio 05:00–22:00 local; headway mediano ~3 min con desviación del orden de
  la media, señal de *bunching*. Mediana de 40 unidades en servicio por día.

## Lo que encontró el análisis de cola (`cola_espera.ipynb`, `docs/cola-de-espera.md`)

- **Las dos rutas troncales cobran distinto.** En T1 la validación es en torniquete de
  estación (0 pasajeros a bordo en `afc_bus_total`, 100 % mapea a una de 27 estaciones);
  en T01 es **a bordo** (`transaction_5.idDispositivo` = `bus.id_bus`). Sólo T1 permite
  reconstruir cola de espera: en T01 el evento AFC ya es el abordaje.
- **Cadena para llegar de una validación a su estación:** `transaction_1.idDispositivo` →
  `afc_station_device_total.id_vehicle` → `.id_station` → `mac_station`. Cuidado:
  `idRutaEstacion` es la RUTA, no la estación, y `idUbicacion` es 0 en toda la troncal.
- **La cola es corta:** mediana 3 personas, p95 26 (día hábil 06–20 h). Con un camión cada
  ~1.6 min por estación, la espera no es hoy el cuello de botella.
- **La cola amplifica la demanda:** razón pico/valle 2.30 contra 1.90 de la demanda, con
  correlación +0.94 con demanda y −0.05 con oferta. Lo que el despacho no absorbe, lo
  absorbe el andén.
- **`bus_location_info` es snapshot, no histórico** (257 filas, una por unidad). No sirve
  para reconstruir eventos pasados.
- **Sesgo conocido:** en Mirador y Fray Angélico llegada y salida se fusionan en una visita,
  así que registran ~265 pasos/día contra ~525 del resto y sus colas están infladas ~2×.

## Nota de arquitectura

MySQL sirve para explorar y para alimentar la interfaz. **No** para el loop de
entrenamiento: un agente de RL itera episodios miles de veces y golpear la BD por step es
inviable. El plan es materializar features a nivel de vuelta en Parquet — `data/export/`
ya está mapeado al `secure-file-priv` del container.
