# Diccionario de datos - BD `integration`

Extraido de `data/definicion de tablas integracion.xlsx`.
Columnas: nombre, tipo, permite NULL, tipo de llave, descripcion.


## `afc_bus_total`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `id_business` | int | YES | MUL | Identificador de empresa |
| `id_route` | int | YES | MUL | Identificador de ruta |
| `id_bus` | int | NO | MUL | Identificador de autobús |
| `date` | date | NO | MUL | Fecha de consulta/transacción |
| `cash_fee_paid` | decimal | YES |  | Suma del dinero total ingresado en la transacción |
| `cash_amount_p` | decimal | YES |  | Suma del monto cobrado |
| `cash_overpay` | decimal | YES |  | Suma de la resta del total ingresado menos el monto cobrado |
| `cash_incomplete_fare` | decimal | YES |  | Suma de monto de tarifa incompleta |
| `cash_incomplete_fare_p` | int | YES |  | Suma de veces que sucedió una tarifa incompleta |
| `cash_passengers` | int | YES |  | Suma de pasajeros que pagaron con efectivo, solo pases completos |
| `recharge_amount_m` | decimal | YES |  | Suma de monto en recargas a monedero de tarjeta general |
| `recharge_amount_c` | decimal | YES |  | Suma de monto en recargas a crédito de tarjeta general |
| `recharge_count` | int | YES |  | Suma de veces que sucedió una recarga de tarjeta general |
| `recharge_amount_m_per` | decimal | YES |  | Suma de monto de recargas a monedero de tarjeta personalizada |
| `recharge_amount_c_per` | decimal | YES |  | Suma de monto en recargas a crédito de tarjeta personalizada |
| `recharge_count_per` | int | YES |  | Suma de veces que sucedió una recarga de tarjeta personalizada |
| `recharge_error_amount` | decimal | YES |  | Suma de monto de errores de recarga |
| `recharge_error_count` | int | YES |  | Suma de veces que sucedió un error de recarga |
| `card_amount_m` | decimal | YES |  | Suma de monto cobrado de monedero de tarjeta general |
| `card_amount_c` | decimal | YES |  | Suma de monto cobrado de crédito de tarjeta general |
| `card_passengers` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta general |
| `card_passengers_transfer` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta general que fue transferencia |
| `card_amount_m_per` | decimal | YES |  | Suma de monto cobrado de monedero de tarjeta personalizada |
| `card_amount_c_per` | decimal | YES |  | Suma de monto cobrado de crédito de tarjeta personalizada |
| `card_passengers_per` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta personalizada |
| `card_passengers_transfer_per` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta personalizada que fue transferencia |
| `bpd_amount` | decimal | YES |  | Suma de monto al que equivaldría el valor de BPD |
| `bpd_passengers` | int | YES |  | Suma de pasajeros con BPD |
| `bpd_passengers_transfer` | int | YES |  | Suma de pasajeros con BPD que fue transferencia |
| `physical_bpd_amount` | decimal | YES |  | Suma de monto al que equivaldría el valor de BPD físico (transvale) |
| `physical_bpd_passengers` | int | YES |  | Suma de pasajeros con BPD físico(transvale) |
| `all_cash` | decimal | YES |  | Suma de todo el efectivo ingresado, contando monto de viaje, overpay y tarifa incompleta |
| `all_passengers` | int | YES |  | Suma de todos los pasajeros de todos los tipos de pago |
| `total_amount` | decimal | YES |  | Suma del monto cobrado de todos los pases de todos los tipos de pago, solo pasajes completos |
| `updated_at` | datetime | YES | MUL | Fecha de modificación |
| `card_passengers_detail` | json | YES |  | Detallado en json del tipo de perfil de tarjeta |
| `bpd_passengers_detail` | json | YES |  | Detallado en json del tipo de perfil de tarjeta con BPD |

## `afc_station_device_total`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `id_business` | int | YES | MUL | Identificador de empresa |
| `id_station` | int | YES | MUL | Identificador de estación |
| `id_vehicle` | int | NO | MUL | Identificador de dispositivo de cobro |
| `date` | date | NO | MUL | Fecha de consulta/transacción |
| `cash_fee_paid` | decimal | YES |  | Suma del dinero total ingresado en la transacción |
| `cash_amount_p` | decimal | YES |  | Suma del monto cobrado |
| `cash_overpay` | decimal | YES |  | Suma de la resta del total ingresado menos el monto cobrado |
| `cash_incomplete_fare` | decimal | YES |  | Suma de monto de tarifa incompleta |
| `cash_incomplete_fare_p` | int | YES |  | Suma de veces que sucedió una tarifa incompleta |
| `cash_passengers` | int | YES |  | Suma de pasajeros que pagaron con efectivo, solo pases completos |
| `recharge_amount_m` | decimal | YES |  | Suma de monto en recargas a monedero de tarjeta general |
| `recharge_amount_c` | decimal | YES |  | Suma de monto en recargas a crédito de tarjeta general |
| `recharge_count` | int | YES |  | Suma de veces que sucedió una recarga de tarjeta general |
| `recharge_amount_m_per` | decimal | YES |  | Suma de monto de recargas a monedero de tarjeta personalizada |
| `recharge_amount_c_per` | decimal | YES |  | Suma de monto en recargas a crédito de tarjeta personalizada |
| `recharge_count_per` | int | YES |  | Suma de veces que sucedió una recarga de tarjeta personalizada |
| `recharge_error_amount` | decimal | YES |  | Suma de monto de errores de recarga |
| `recharge_error_count` | int | YES |  | Suma de veces que sucedió un error de recarga |
| `card_amount_m` | decimal | YES |  | Suma de monto cobrado de monedero de tarjeta general |
| `card_amount_c` | decimal | YES |  | Suma de monto cobrado de crédito de tarjeta general |
| `card_passengers` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta general |
| `card_passengers_transfer` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta general que fue transferencia |
| `card_amount_m_per` | decimal | YES |  | Suma de monto cobrado de monedero de tarjeta personalizada |
| `card_amount_c_per` | decimal | YES |  | Suma de monto cobrado de crédito de tarjeta personalizada |
| `card_passengers_per` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta personalizada |
| `card_passengers_transfer_per` | int | YES |  | Suma de pasajeros con tarjeta de tarjeta personalizada que fue transferencia |
| `bpd_amount` | decimal | YES |  | Suma de monto al que equivaldría el valor de BPD |
| `bpd_passengers` | int | YES |  | Suma de pasajeros con BPD |
| `bpd_passengers_transfer` | int | YES |  | Suma de pasajeros con BPD que fue transferencia |
| `sale_amount` | decimal | YES |  | Suma de monto de venta de tarjetas |
| `sale_count` | int | YES |  | Suma de tarjetas vendidas |
| `sale_error_amount` | decimal | YES |  | Suma de monto de ventas con error |
| `sale_error_count` | int | YES |  | Suma de errores de venta de tarjetas |
| `physical_bpd_amount` | decimal | YES |  | Suma de monto al que equivaldría el valor de BPD físico (transvale) |
| `physical_bpd_passengers` | int | YES |  | Suma de pasajeros con BPD físico(transvale) |
| `transfer_mod_m` | double | YES |  | Suma de transferencias de monto de monedero de tarjeta en modulo de atención |
| `transfer_mod_c` | double | YES |  | Suma de transferencias de monto de crédito de tarjeta en modulo de atención |
| `transfer_mod_count` | int | YES |  | Suma de transferencias realizadas en modulo de atención |
| `all_cash` | decimal | YES |  | Suma de todo el efectivo ingresado, contando monto de viaje, overpay y tarifa incompleta |
| `all_passengers` | int | YES |  | Suma de todos los pasajeros de todos los tipos de pago |
| `total_amount` | decimal | YES |  | Suma del monto cobrado de todos los pases de todos los tipos de pago, solo pasajes completos |
| `updated_at` | datetime | YES | MUL | Fecha de modificación |
| `extern_recharges` | int | YES |  | Suma de recargas externas hechas en módulo de atención, los errores sucedidos en sistemas externos pero atendidos en nuestros módulos |
| `extern_recharges_amount` | decimal | YES |  | Suma de monto de recargas externas hechas en módulo de atención |
| `card_passengers_detail` | json | YES |  | Detallado en json del tipo de perfil de tarjeta, los errores sucedidos en sistemas externos pero atendidos en nuestros módulos |
| `bpd_passengers_detail` | json | YES |  | Detallado en json del tipo de perfil de tarjeta con BPD |

## `afc_tariff`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id_tariff` | int | NO | PRI | Identificador |
| `id_business` | int | NO |  | Identificador de empresa |
| `tariff` | int | NO |  | Monto a cobrar en efectivo |
| `applied_from` | date | NO |  | Fecha inicial de aplicación |
| `applied_to` | date | YES |  | Fecha final de aplicación |
| `is_current` | tinyint | NO |  | Bandera para saber si está activa dicha tarifa |
| `card_tariff` | int | YES |  | Monto a cobrar en tarjeta |
| `tariff_2` | int | YES |  | Campo en desuso, para proceso antiguo |

## `bus`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id_bus` | int | NO | PRI | Identificador |
| `busnumber` | varchar | NO |  | Etiqueta impresa en autobus |
| `plate` | varchar | NO |  | Numero de placa |
| `model` | varchar | NO |  | Modelo |
| `brand` | varchar | NO |  | Marca |
| `status` | int | NO |  | Estado activo/inactivo/eliminado |
| `id_dvr` | int | YES |  | Campo en desuso, para proceso antiguo |
| `id_ebjdevice` | int | YES |  | Campo en desuso, para proceso antiguo |
| `id_route` | int | NO |  | Identificador de ruta |
| `id_afc` | int | YES |  | Campo en desuso, para proceso antiguo |
| `id_ms` | int | YES |  | Identificador de dispositivo de cobro con monedas |
| `id_oct` | int | YES |  | Identificador de terminal para el conductor |
| `can_recharge` | tinyint | YES |  | Bandera para saber si tiene permitido la recarga de tarjetas |
| `id_ceiba_device` | int | YES | UNI | Campo en desuso, para proceso antiguo |
| `send_gps_info` | tinyint | YES |  | Identificador para saber si tiene permitido enviar información GPS |

## `bus_location_info`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `id_bus` | int | NO |  | Identificador de autobús |
| `near` | int | YES |  | Identificador de punto de control mas cercano |
| `last` | int | YES |  | Identificador de punto de control pasado |
| `next` | int | YES |  | Identificador de punto de control siguiente |
| `distance_near` | double | YES |  | Distancia, en metros de punto más cercano |
| `updated_at` | timestamp | YES |  | Hora a la que se actualizó la información |
| `direction` | int | YES |  | Dirección de ruta, ida/vuelta |
| `distance_between` | double | YES |  | Campo en desuso, para proceso antiguo |
| `distance_last` | double | YES |  | Distancia en metros con el punto anterior |
| `distance_next` | double | YES |  | Distancia en metros con el punto siguiente |
| `status` | int | YES |  | Bandera para saber si está en ruta o no |
| `arrival_time_schedule` | datetime | YES |  | Tiempo de llegada aproximada para el siguiente punto de control |
| `diff_time` | int | YES |  | Tiempo para saber si va retrasado o adelantado |
| `arrival_time_last` | datetime | YES |  | Tiempo en el que llegó al punto pasado |
| `status_start_time` | timestamp | YES |  | Tiempo en el que comenzó a ir en ruta o fuera de ruta |

## `business`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id_business` | int | NO | PRI | Identificador |
| `name` | varchar | NO |  | Nombre de la empresa |
| `tel` | varchar | NO |  | Telefono |
| `status` | int | NO |  | Estado activo/inactivo/eliminado |
| `id_dvr_ug` | int | YES |  | Campo en desuso, para proceso antiguo |
| `id_afc_group` | int | YES |  | Campo en desuso, para proceso antiguo |
| `id_tracking` | int | YES |  | Campo en desuso, para proceso antiguo |
| `id_entidad` | int | YES |  | Identificador de empresa ante ente regulador |
| `operador_sir_fimpe` | varchar | YES | MUL | Identificador en texto de empresa ante ente regulador |
| `require_update_bl` | tinyint | YES |  | Campo en desuso, para proceso antiguo |
| `ftp_path` | text | YES |  | Ruta interna de archivos en servidor |
| `default_lat` | double | YES |  | Latitud por defecto para mostrar en mapa |
| `default_lon` | double | YES |  | Longitud por defecto para mostrar en mapa |
| `default_zoom` | int | YES |  | Zoom por defecto para mostrar en mapa |
| `start_date` | date | YES |  | Fecha desde que inicio operación |
| `process_data` | tinyint | YES |  | Bandera para saber si debe procesar archivos en servidor |

## `codigo_perfil`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `name` | varchar | YES |  | Nombre |

## `current_bus_driver`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `id_driver` | int | NO |  | Identificador de conductor |
| `id_bus` | int | NO |  | Identificador de autobús |
| `device_type` | int | NO |  | Identificador de tipo de dispositivo de cobro, terminal de conductor o lector de monedas |
| `operation_dt` | datetime | NO |  | Día de operación |
| `updated_at` | datetime | YES |  | Fecha Hora de actualización |

## `in_device_history_location`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id_history` | int | NO | PRI | Identificador |
| `time` | timestamp | NO | MUL | Fecha Hora de actualización |
| `latitude` | double | NO |  | Latitud |
| `longitude` | double | NO |  | Longitud |
| `speed` | double | NO |  | Velocidad en km/h |
| `dev_date` | varchar | NO |  | Fecha de cuando se realizó la lectura en el dispositivo |
| `dev_time` | varchar | NO |  | Hora de cuando se realizó la lectura en el dispositivo |
| `altitude` | double | NO |  | Altitud |
| `degree_course` | double | NO |  | Dirección de movimiento en grados |
| `cardinal_course` | varchar | NO |  | Dirección de movimiento en texto |
| `id_ebjdevice` | int | NO | MUL | Identificador de dispositivo |
| `id_bus` | int | NO |  | Identificador de autobús |
| `id_route` | int | NO |  | Identificador de ruta |
| `type_bus` | int | YES |  | Campo en desuso, para proceso antiguo |

## `in_payment_type`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `name` | varchar | NO |  | Nombre de tipo de pago |
| `description` | varchar | NO |  | Descripción |

## `in_route_area`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `number` | int | NO |  | Numero de ordenamiento |
| `latitude` | double | NO |  | Latitud |
| `longitude` | double | NO |  | Longitud |
| `id_route` | int | NO |  | Identificador de ruta |

## `in_route_point`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `number` | int | YES |  | Numero de ordenamiento |
| `latitude` | double | YES |  | Latitud |
| `longitude` | double | YES |  | Longitud |
| `direction` | varchar | YES |  | Dirección de ruta, ida/vuelta |
| `id_route` | int | YES | MUL | Identificador de ruta |

## `in_route_point_control`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `number` | int | NO |  | Numero de ordenamiento |
| `name` | varchar | NO |  | Nombre |
| `latitude` | double | NO |  | Latitud |
| `longitude` | double | NO |  | Longitud |
| `id_route` | int | NO |  | Identificador de ruta |
| `direction` | int | YES |  | Dirección de ruta, ida/vuelta |

## `mac_station`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `sta_no` | int | YES |  | Numero de estación |
| `id` | int | NO | PRI | Identificador |
| `name` | varchar | NO |  | Nombre |
| `type` | int | YES |  | Tipo de estación si es de 2 entradas o 4 entradas |
| `id_route` | int | NO |  | Identificador de ruta |
| `status` | tinyint | YES |  | Estado activo/inactivo/eliminado |
| `model` | tinyint | YES |  | Modelo si es express o parador |

## `route`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id_route` | int | NO | PRI | Identificador |
| `name` | varchar | NO |  | Nombre |
| `description` | varchar | NO |  | Descripción |
| `id_business` | int | NO |  | Identificador de empresa |
| `id_dvr_dg` | int | YES |  | Campo en desuso, para proceso antiguo |
| `id_ruta_estacion` | int | YES | MUL | identificador interno para rutas o estaciones |
| `type` | int | YES |  | Bandera para saber si es de estaciones, de alimentadoras de macrobus o autobuses de ruta empresa |
| `prev_route` | varchar | YES |  | Nombre de ruta antigua, antes del cambio |
| `status` | tinyint | YES |  | Estado activo/inactivo/eliminado |
| `id_parent_route` | int | YES |  | Identificador si es una subruta |

## `tipo_evento`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `name` | varchar | YES |  | Nombre del tipo evento |

## `transaction_1`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `uid` | varchar | YES | MUL | Numero impreso de tarjeta |
| `fee_paid` | int | YES |  | Dinero total ingresado en la transacción |
| `payment_type` | int | YES | MUL | Identificador de tipo de pago |
| `balance_bef_transaction` | int | YES |  | Saldo antes de la transacción en pagos con tarjeta |
| `balance_aft_transaction` | int | YES |  | Saldo después de la transacción en pagos con tarjeta |
| `serialMedioPago` | varchar | YES |  | Texto que identifica al creador de la tarjeta en pagos con tarjeta |
| `fechaFinValidezAplicacion` | date | YES |  | Fecha de vigencia de la tarjeta fisica |
| `consecutivoAplicacion_bef_transaction` | int | YES |  | Consecutivo de la transacción previa |
| `numeroAccionAplicada_aft_transaction` | int | YES |  | Consecutivo después de la transacción |
| `codigoPerfil` | int | YES | MUL | Identificador de código perfil |
| `fechaFinPerfil` | date | YES |  | Fecha de fin de perfil |
| `idProducto` | varchar | YES | MUL | Identificador de producto que fue debitado, monedero/crédito/bpd1/bpd2 |
| `idEntidad` | int | YES | MUL | Identificador de empresa ante ente regulador |
| `fechaHoraEvento` | datetime | YES | MUL | Fecha Hora de cobro |
| `tipoEvento` | int | YES |  | Identificador para saber si fue pase normal o transferencia |
| `montoEvento` | int | YES |  | Monto cobrado |
| `consecutivoEvento` | int | YES |  | Consecutivo de validación de la tarjeta |
| `idSAM` | varchar | YES |  | Identificador del SAM que realizó el cobro |
| `consecutivoSAM` | varchar | YES |  | Consecutivo de validación del SAM |
| `idDispositivo` | int | YES | MUL | Identificador de dispositivo de cobro |
| `idUbicacion` | int | YES |  | Campo en desuso, para proceso antiguo |
| `tipoTransporte` | int | YES | MUL | Identificador para saber tipo de transporte macrobus/alimentadoras/ruta empresa |
| `idRutaEstacion` | int | YES | MUL | Identificador de ruta estación |
| `numeroTransbordos` | int | YES |  | Numero de transbordo en nuestro sistema, el 3ro es gratis |
| `limiteTransbordos` | datetime | YES |  | Fecha hora limite para transbordar |
| `numeroPassbacks` | int | YES |  | Numero máximo para pasar la tarjeta, 0 sin limite |
| `idTipoDispositivo` | int | YES |  | Identificador de tipo de dispositivo de cobro |
| `et_idProducto` | varchar | YES | MUL | Campo en desuso, para proceso antiguo |
| `et_montoEvento` | int | YES |  | Campo en desuso, para proceso antiguo |
| `et_consecutivoEvento` | int | YES |  | Campo en desuso, para proceso antiguo |
| `et_consecutivoSAM` | varchar | YES |  | Campo en desuso, para proceso antiguo |
| `pt_idProducto` | varchar | YES |  | Identificador de producto de validación anterior |
| `pt_idEntidad` | int | YES |  | identificador de empresa de validación anterior |
| `pt_fechaHoraEvento` | datetime | YES |  | Fecha hora de validación anterior |
| `pt_tipoEvento` | int | YES |  | Identificador para saber si fue pase normal o transferencia de validación anterior |
| `pt_montoEvento` | int | YES |  | Monto cobrado de validación anterior |
| `pt_consecutivoEvento` | int | YES |  | Consecutivo de validación anterior |
| `pt_idDispositivo` | int | YES |  | Identificador de dispositivo de cobro de validación anterior |
| `pt_tipoTransporte` | int | YES |  | Identificador para saber tipo de transporte macrobus/alimentadoras/ruta empresa de validación anterior |
| `pt_idRutaEstacion` | int | YES |  | Identificador de ruta estación de validación anterior |
| `gps_lat` | double | YES |  | Latitud donde se realizo la validación |
| `gps_lon` | double | YES |  | Longitud donde se realizo la validación |
| `id_driver` | varchar | YES |  | Identificador de conductor |
| `outputdata_filename` | varchar | YES |  | Nombre de archivo en dónde se almacenó la validación para envío a servidor |
| `serialno` | varchar | YES | MUL | Número de serie de equipo de cobro |
| `inserted_at` | timestamp | YES | MUL | Fecha hora de inserción en base de datos |
| `fechaConciliciacion` | date | YES | MUL | Fecha a la que pertenece la validación, si está se realiza entre las 00:00 y las 04:30 se toma cómo que fue del día anterior |
| `tr_no` | int | YES |  | Número de transacción en el equipo de cobro |
| `mac_pt_sta_id` | int | YES |  | Identificador de estación de validación anterior |
| `mac_vehc_id` | int | YES | MUL | Identificador de dispositivo de cobro de estación |
| `mac_sta_id` | int | YES | MUL | Identificador de estación |

## `transaction_5`

| columna | tipo | null | llave | descripcion |
|---|---|---|---|---|
| `id` | int | NO | PRI | Identificador |
| `uid` | varchar | YES | MUL | Numero impreso de tarjeta |
| `fee_paid` | int | YES |  | Dinero total ingresado en la transacción |
| `payment_type` | int | YES | MUL | Identificador de tipo de pago |
| `balance_bef_transaction` | int | YES |  | Saldo antes de la transacción en pagos con tarjeta |
| `balance_aft_transaction` | int | YES |  | Saldo después de la transacción en pagos con tarjeta |
| `serialMedioPago` | varchar | YES |  | Texto que identifica al creador de la tarjeta en pagos con tarjeta |
| `fechaFinValidezAplicacion` | date | YES |  | Fecha de vigencia de la tarjeta fisica |
| `consecutivoAplicacion_bef_transaction` | int | YES |  | Consecutivo de la transacción previa |
| `numeroAccionAplicada_aft_transaction` | int | YES |  | Consecutivo después de la transacción |
| `codigoPerfil` | int | YES | MUL | Identificador de código perfil |
| `fechaFinPerfil` | date | YES |  | Fecha de fin de perfil |
| `idProducto` | varchar | YES | MUL | Identificador de producto que fue debitado, monedero/crédito/bpd1/bpd2 |
| `idEntidad` | int | YES | MUL | Identificador de empresa ante ente regulador |
| `fechaHoraEvento` | datetime | YES | MUL | Fecha Hora de cobro |
| `tipoEvento` | int | YES |  | Identificador para saber si fue pase normal o transferencia |
| `montoEvento` | int | YES |  | Monto cobrado |
| `consecutivoEvento` | int | YES |  | Consecutivo de validación de la tarjeta |
| `idSAM` | varchar | YES |  | Identificador del SAM que realizó el cobro |
| `consecutivoSAM` | varchar | YES |  | Consecutivo de validación del SAM |
| `idDispositivo` | int | YES | MUL | Identificador de dispositivo de cobro |
| `idUbicacion` | int | YES |  | Campo en desuso, para proceso antiguo |
| `tipoTransporte` | int | YES |  | Identificador para saber tipo de transporte macrobus/alimentadoras/ruta empresa |
| `idRutaEstacion` | int | YES |  | Identificador de ruta estación |
| `numeroTransbordos` | int | YES |  | Numero de transbordo en nuestro sistema, el 3ro es gratis |
| `limiteTransbordos` | datetime | YES |  | Fecha hora limite para transbordar |
| `numeroPassbacks` | int | YES |  | Numero máximo para pasar la tarjeta, 0 sin limite |
| `idTipoDispositivo` | int | YES |  | Identificador de tipo de dispositivo de cobro |
| `et_idProducto` | varchar | YES | MUL | Campo en desuso, para proceso antiguo |
| `et_montoEvento` | int | YES |  | Campo en desuso, para proceso antiguo |
| `et_consecutivoEvento` | int | YES |  | Campo en desuso, para proceso antiguo |
| `et_consecutivoSAM` | varchar | YES |  | Campo en desuso, para proceso antiguo |
| `pt_idProducto` | varchar | YES |  | Identificador de producto de validación anterior |
| `pt_idEntidad` | int | YES |  | identificador de empresa de validación anterior |
| `pt_fechaHoraEvento` | datetime | YES |  | Fecha hora de validación anterior |
| `pt_tipoEvento` | int | YES |  | Identificador para saber si fue pase normal o transferencia de validación anterior |
| `pt_montoEvento` | int | YES |  | Monto cobrado de validación anterior |
| `pt_consecutivoEvento` | int | YES |  | Consecutivo de validación anterior |
| `pt_idDispositivo` | int | YES |  | Identificador de dispositivo de cobro de validación anterior |
| `pt_tipoTransporte` | int | YES |  | Identificador para saber tipo de transporte macrobus/alimentadoras/ruta empresa de validación anterior |
| `pt_idRutaEstacion` | int | YES |  | Identificador de ruta estación de validación anterior |
| `gps_lat` | double | YES |  | Latitud donde se realizo la validación |
| `gps_lon` | double | YES |  | Longitud donde se realizo la validación |
| `id_driver` | varchar | YES |  | Identificador de conductor |
| `outputdata_filename` | varchar | YES |  | Nombre de archivo en dónde se almacenó la validación para envío a servidor |
| `serialno` | varchar | YES | MUL | Número de serie de equipo de cobro |
| `inserted_at` | timestamp | YES | MUL | Fecha hora de inserción en base de datos |
| `fechaConciliciacion` | date | YES | MUL | Fecha a la que pertenece la validación, si está se realiza entre las 00:00 y las 04:30 se toma cómo que fue del día anterior |
| `tr_no` | int | YES |  | Número de transacción en el equipo de cobro |
