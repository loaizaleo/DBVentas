# base

Registros de ventas generados con `registradorV3.py`, listos para importar a la tabla `ventas` de MySQL.

Formato (CSV con encabezado):

```
fecha,cantidad,modelos_id
2025-10-22,1,72
```

| Archivo | Contenido |
|---|---|
| `ventas_log01.csv` | Ventas del 2025-10-12 al 2025-10-21. |
| `ventas_log.csv` | Ventas del 2025-10-22 al 2025-10-28. |
| `ventas_log_old.csv` | Ventas del 2025-11-24 al 2025-12-06. |

Para importarlos, vea la sección *Importar ventas* del README principal.
