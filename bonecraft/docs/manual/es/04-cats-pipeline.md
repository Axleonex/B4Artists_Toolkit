# El pipeline de CATS

[← Índice](index.md)

**Lee esto antes de usar cualquier herramienta de CATS por primera vez.**

Las herramientas de CATS no son un menú de opciones independientes: son un pipeline. Cada paso se apoya en el anterior. Ejecutarlas fuera de orden produce resultados rotos que siguen invisibles hasta que ya estás en VRChat, y para entonces no se pueden arreglar sin empezar de nuevo. Puedes saltarte una fase que tu avatar no necesite, pero las fases que ejecutes deben mantener este orden.

---

## Las seis fases, en orden

El Estado del Pipeline de la pestaña CATS enumera las fases y marca cada una cuando está hecha:

1. **Corregir Modelo** — Limpia la malla: quita duplicados y geometría rota, corrige las normales. Todos los demás pasos dependen de este.

2. **Atlas de Materiales** — Combina los materiales del avatar en una sola hoja de textura (opcional, para el rendimiento).

3. **Visemas** — Genera las 15 formas de boca de sincronización labial de VRChat a partir de tus tres formas base (A, O, CH).

4. **Seguimiento Ocular** — Configura el movimiento de ojos de VRChat con los huesos de los ojos de tu avatar.

5. **Pose a Shape Key** — Captura poses o expresiones personalizadas como shape keys.

6. **Aplicar Todas las Transformaciones** — Congela toda la posición, la rotación y la escala para que tu avatar tenga transformaciones limpias al subirlo.

---

## Estado del Pipeline y Registro de Operaciones

El Estado del Pipeline muestra una línea por fase. Cuando una fase termina, su línea muestra una marca. El estado se guarda en la escena, así que se queda con tu archivo.

El Registro de Operaciones enumera cada operación de CATS que has ejecutado, la más reciente al final, con su hora y su resultado: Changed (cambió el modelo), Clean (no hacía falta cambiar nada) o Failed (falló). **Copiar** pone el registro en el portapapeles (útil cuando pides ayuda); **Limpiar** lo vacía.

El orden es un consejo, no un bloqueo: una herramienta cuya fase anterior no está hecha se ejecuta igualmente, pero muestra un aviso como «Run Fix Model first for best results» (ejecuta primero Corregir Modelo para obtener los mejores resultados). Tómate en serio ese aviso.

---

## Por qué este orden

Cada fase cambia la malla o el esqueleto de un modo del que depende la siguiente:

- **Corregir Modelo debe ir primero** porque cambia el número de vértices, quita duplicados y corrige las normales. Cualquier herramienta que lea posiciones de vértices (generación de visemas, detección de huesos de ojos, captura de poses) da resultados incorrectos en una malla que aún tiene vértices duplicados o rotos.

- **Visemas antes que Seguimiento Ocular** porque ambos cambian shape keys y datos de huesos. En este orden, los shape keys existen antes de que se escriban las restricciones.

- **Seguimiento Ocular antes que Pose a Shape Key** porque Pose a Shape Key captura toda la malla, incluida la deformación causada por los huesos. Con las restricciones de los ojos ya puestas, la posición neutra de los ojos en la forma guardada es correcta.

- **Aplicar transformaciones al final** porque lo congela todo para siempre. Cualquier geometría sin corregir, shape key sin mapear o restricción incorrecta queda fijada. Después de aplicar las transformaciones, las únicas formas de volver a una fase anterior son deshacer (Ctrl+Z) o reimportar desde el archivo de origen.

---

## Qué se rompe si te saltas un paso

**Saltarse Corregir Modelo:**
Cada herramienta posterior trabaja sobre una malla que puede tener vértices duplicados en la misma posición. Un visema generado puede mover entonces el vértice visible pero no su duplicado oculto, de modo que en VRChat ambos se separan y rasgan la boca en cada forma de sincronización labial. El seguimiento ocular puede unir sus restricciones a la malla de ojo duplicada en lugar de la visible, dejando los ojos fijos con la mirada perdida. Aplicar transformaciones después hornea todos estos errores.

**Saltarse Visemas:**
Sin visemas generados o mapeados, tu avatar no tiene sincronización labial. Si tu avatar ya tiene shape keys de visemas, mapéalos en VRChat Viseme Mapping (guía 8) en lugar de generar otros nuevos; el Estado del Pipeline deja entonces Visemas sin marcar, y está bien.

**Saltarse Seguimiento Ocular:**
Tu avatar no mueve los ojos en VRChat y mira fijamente al frente. Es aceptable si no tiene huesos de ojos.

**Saltarse Pose a Shape Key:**
Opcional: sáltalo si no tienes expresiones personalizadas que guardar.

Siguiente: [Herramientas de rig](05-rig-tools.md)
