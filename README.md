---
Universidad Carlos III de Madrid
---

## Máster Universitario en Ingeniería de Telecomunicación
## 2025-2026

## Trabajo Fin de Máster
# Emulación realista del acceso radio 5G

---

## Juan Manuel Espinosa Moral

### Tutor/es
### Ana García Armada
### Leganés, 17 de junio de 2026

Este repositorio contiene el material desarrollado para un trabajo de fin de máster.
Para mayor claridad, distinguimos tres clases de elementos en este repositorio
(en el resumen se indica cuál es cada uno):

- Los que tienen que ver con el emulador:
    1. Los que se usan para compilar el emulador.
    Esta clase de elementos incluye el código fuente, el cual, se debe copiar en una réplica del repositorio de _FikoRE_ \[1\],
    añadiendo o sobreescribiendo los ficheros correspondientes.
    En particular, este repositorio contiene el código fuente de una versión alternativa del emulador con métricas de planificación de paquetes adicionales.
    2. Los que se usan con el emulador compilado.
    3. Los que se usan con la información resultante de las simulaciones.
- Los relacionados con la entrega del trabajo de fin de máster.
- Los relacionados con la gestión del repositorio.

En breve, se publicará el acceso a la memoria del trabajo de fin de máster.

## Resumen

- `.gitignore`:
Fichero _.gitignore_.
Este es un fichero de gestión del repositorio.
- `README.md`:
Fichero _README_.
Este es un fichero de gestión del repositorio.
- `comparaciones`:
Datos de las comparaciones entre simulaciones.
Esta información se usó en la entrega del trabajo de fin de máster.
- `computos_y_graficas`:
Datos del análisis de las simulaciones.
Esta información se usó en la entrega del trabajo de fin de máster.
- `config`:
Ficheros de configuración de simulación para el emulador.
Se usan con el emulador compilado.
- `data`:
Capturas de tráfico de red para inyectar en una simulación.
Se usan con el emulador compilado.
- `documentacion`:
Documentación del emulador.
Esta información se usó en la entrega del trabajo de fin de máster.
- `include-b`:
Ficheros _.h_ para el código fuente de la versión alternativa del emulador.
Se copian en el directorio _include_ del código fuente del emulador, sobreescribiéndose los ficheros.
Se usan para compilar el emulador.
- `memoria`:
Ficheros de _LaTeX_ de la memoria del trabajo.
- `py_analizers`:
_Scripts_ de _Python_ para analizar las simulaciones.
Se usan con la información resultante de las simulaciones.
- `run_scripts`: _Scripts_ de _Bash_ para ejecutar las simulaciones.
Se usan con el emulador compilado.
- `scripts`: _Scripts_ de _Bash_ y _Python_ para otros cometidos.
Se usan para varios fines.
- `simulaciones.md`:
Lista de las simulaciones realizadas.
Esta información se usó en la entrega del trabajo de fin de máster.
- `src-b`:
Ficheros _.c_ para el código fuente de la versión alternativa del emulador.
Se copian en el directorio _src_ del código fuente del emulador, sobreescribiéndose los ficheros.
Se usan para compilar el emulador.

\[1\]: https://github.com/nokia/5g-network-emulator
