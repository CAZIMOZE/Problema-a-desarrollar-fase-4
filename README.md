# Sistema Integral de Gestión – Software FJ

Aplicación orientada a objetos desarrollada en Python (sin uso de motores de bases de datos) para gestionar clientes, servicios tecnológicos (reservas de salas, alquiler de equipos y asesorías especializadas) y reservas, garantizando estabilidad ante errores mediante manejo avanzado de excepciones y registro en archivos de log.

## Hoja de Ruta y Trazabilidad de Desarrollo (14 Fases)

El desarrollo del sistema en `Fase4.py` está estructurado de forma incremental para garantizar trazabilidad en cada commit:

### Bloque 1: Cimientos, Logs y Excepciones
- [x] **Fase 1:** Inicialización del script `Fase4.py` e importación de librerías estándar (`abc`, `datetime`, `os`, `re`).
- [x] **Fase 2:** Implementación de `GestorLogs` para persistencia de eventos y errores en `.log` usando `try/except/finally`.
- [x] **Fase 3:** Jerarquía de excepciones personalizadas (`SoftwareFJError` y 6 excepciones especializadas).

### Bloque 2: Abstracción y Entidades Base
- [x] **Fase 4:** Clase abstracta base `EntidadSistema` (`ABC`) con validaciones y resumen obligatorio.
- [x] **Fase 5:** Clase `Cliente` con encapsulación privada (`@property`) y validación estricta de datos personales.

### Bloque 3: Jerarquía de Servicios y Polimorfismo
- [x] **Fase 6:** Clase abstracta `Servicio` con métodos abstractos y sobrecarga simulada en el cálculo de costos.
- [x] **Fase 7:** Servicio especializado `ReservaSala` (capacidad y equipamiento audiovisual).
- [x] **Fase 8:** Servicio especializado `AlquilerEquipo` (control de stock y seguro obligatorio).
- [x] **Fase 9:** Servicio especializado `AsesoriaEspecializada` (niveles de complejidad y recargos por urgencia).

### Bloque 4: Gestión de Reservas y Motor Central
- [x] **Fase 10:** Clase `Reserva` con control de estados (`PENDIENTE`, `CONFIRMADA`, `CANCELADA`) y encadenamiento de excepciones (`raise ... from ...`).
- [ ] **Fase 11:** Motor central `SistemaSoftwareFJ` para administración de listas en memoria y control de integridad.
- [ ] **Fase 12:** Pruebas de bordes y verificación de captura de excepciones encadenadas en el archivo `.log`.

### Bloque 5: Simulación Integral y Cierre
- [ ] **Fase 13:** Simulación de 10+ operaciones completas (casos válidos e inválidos de clientes, servicios y reservas).
- [ ] **Fase 14:** Auditoría final del archivo de logs y cierre de documentación.