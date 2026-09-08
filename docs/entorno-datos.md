# Entorno de datos

## Por que un container y no leer los .sql

`data/integration.sql` son 6.1 GB de dump de MySQL 8.0. Un dump no tiene indices ni
acceso aleatorio: cada consulta exploratoria implicaria reparsear el archivo completo.
El container carga una sola vez y despues cualquier query corre sobre InnoDB indexado.

## Uso

```bash
docker compose up -d          # levanta MySQL + Adminer
bash scripts/load_dumps.sh    # carga los dumps (solo la primera vez)
bash scripts/load_dumps.sh --reset   # recarga desde cero
```

- MySQL: `127.0.0.1:3307`, usuario `root` / `macro`, BD `integration`
- Adminer: http://127.0.0.1:8080
- Cliente: `docker compose exec mysql mysql -uroot -pmacro integration`

El volumen `macro_mysql_data` vive dentro de la VM de Docker, no en el bind mount de
Windows: eso evita el cuello de botella del sistema de archivos compartido.

## Notas de configuracion

- El tuning de InnoDB va como flags en `command:` y no como `conf.d`. Un bind mount
  desde Windows queda world-writable y `mysqld` descarta esos archivos en silencio.
- `innodb_doublewrite=0` y `flush_log_at_trx_commit=0` sacrifican durabilidad por
  throughput. Es deliberado: la BD se reconstruye desde los dumps.
- Todo queda en **UTC** (`default_time_zone=+00:00`), igual que los dumps. La
  conversion a hora local va en la capa de features, no en la BD.

## Datos relevantes para el modelo

| Tabla | Contenido | Uso en el RL |
|---|---|---|
| `in_device_history_location` | GPS cada ~20 s: lat/lon, `speed`, `degree_course`, `id_bus` | Reconstruir vueltas y tiempos de recorrido |
| `transaction_1` | Validaciones AFC de Macrobus T1, con `fechaHoraEvento` e `idRutaEstacion` | Demanda observada (senal de recompensa) |
| `transaction_5` | Validaciones AFC de la ruta T01 | Idem |
| `afc_bus_total` | Agregado diario por camion, incluye `all_passengers` | Validacion cruzada de demanda |
| `in_route_point_control` | Puntos de control con lat/lon y `direction` | Segmentar la vuelta en tramos |
| `bus_location_info` | `last`/`next` punto de control, `diff_time` (adelanto/retraso) | Estado operativo por unidad |
| `bus` | 188 unidades, `id_route`, `model`, `brand` | Identidad de flota |

## Hueco de informacion detectado

El diccionario documenta 303 columnas en 18 tablas y **ninguna contiene capacidad ni
costo por unidad**. La funcion de recompensa descrita (minimizar camiones despachados,
maximizar pasajeros transportados) necesita ambos. Lo mas cercano es `bus.model`
(valores `'1'` y `'2'`) y `bus.brand` (Dina, Mercedes Benz, International).

Hay que pedir al cliente una tabla de mapeo `model`/`brand` -> capacidad (pasajeros) y
costo por vuelta. Sin eso, el termino de costo de la recompensa no es calculable.
