# El pipeline de CATS

[← Contenidos](index.md)

**Lea esto antes de usar cualquier herramienta CATS por primera vez.**

Las herramientas CATS no son un menú de opciones independientes: son una canalización. Cada paso se basa en el anterior. Ejecutarlos fuera de orden produce resultados rotos que permanecen invisibles hasta que ya esté en VRChat, y para entonces no se pueden arreglar sin comenzar de nuevo. Puedes saltarte una fase que tu avatar no necesita, pero las fases que ejecutes deben mantener este orden.

---

## Las seis fases, en orden

El Estado de canalización de la pestaña CATS enumera las fases y marca cada una cuando finaliza:

1. **Fix Model** — Limpiar la malla: eliminar duplicados y geometría rota, arreglar las normales. Todos los demás pasos dependen de este.

2. **Material Atlas**: combine los materiales del avatar en una hoja de textura (opcional, para rendimiento).

3. **Visemes**: genere las 15 formas de boca de sincronización labial VRChat a partir de sus tres formas base (A, O, CH).

4. **Eye Tracking**: configura el movimiento ocular de VRChat con los huesos de los ojos de tu avatar.

5. **Pose to Shape Key**: capture poses o expresiones personalizadas como claves de formas.

6. **Apply All Transforms**: Congela todas las posiciones, rotaciones y escalas para que tu avatar tenga transformaciones limpias para cargar.

---

## Estado del Pipeline y Registro de Operaciones

El estado de la tubería muestra una línea por fase. Cuando finaliza una fase, su línea muestra una marca de verificación. El estado se mantiene en la escena, por lo que permanece con su archivo.

El Libro mayor de operaciones enumera todas las operaciones CATS que ejecutó, la más reciente en último lugar, con su tiempo y resultado: Cambiada (cambió el modelo), Limpia (no es necesario cambiar nada) o Fallida. **Copy** coloca el libro mayor en el portapapeles (útil cuando pides ayuda);**Clear** lo vacía.

El orden es un consejo, no un bloqueo: una herramienta cuya fase anterior no se realizó todavía se ejecuta, pero muestra una advertencia como "Ejecutar primero el modelo de corrección para obtener mejores resultados". Tome la advertencia en serio.

---

## Por qué este orden

Cada fase cambia la malla o el esqueleto de maneras que depende de la siguiente:

- **Reparar modelo debe ser el primero** porque cambia el recuento de vértices, elimina duplicados y corrige las normales. Cualquier herramienta que lea las posiciones de los vértices (generación de visemas, detección de huesos del ojo, captura de poses) produce resultados incorrectos en una malla que todavía tiene vértices duplicados o rotos.

- **Visemas antes del seguimiento ocular** porque ambos cambian la clave de forma y los datos óseos. En este orden, las claves de forma existen antes de que se escriban las restricciones.

- **Seguimiento ocular antes de Pose to Shape** porque Pose to Shape captura toda la malla, incluida la deformación provocada por los huesos. Con las restricciones oculares colocadas primero, la posición neutra de los ojos en la forma guardada es la correcta.

- **Aplica Transformaciones al final** porque congela todo para siempre. Cualquier geometría no fijada, claves de forma no asignadas o restricciones incorrectas quedan bloqueadas. Después de aplicar transformaciones, las únicas formas de volver a una fase anterior son deshacer (Ctrl+Z) o volver a importar desde el archivo fuente.

---

## Qué se rompe si te saltas un paso

**Omitir modelo de corrección:**
Cada herramienta posterior funciona en una malla que puede contener vértices duplicados en la misma posición. Un visema generado puede mover el vértice visible pero no su duplicado oculto, por lo que en VRChat los dos se separan y desgarran la boca en cada forma de sincronización labial. El seguimiento ocular puede vincular sus limitaciones a la malla ocular duplicada en lugar de a la visible, fijando los ojos en una mirada fija. Apply Transforms luego incorpora todos estos errores.

**Omitir Visemes:**
Sin visemas generados o mapeados, tu avatar no tiene sincronización de labios. Si su avatar ya tiene teclas de forma de viseme, asígnelas en VRChat Viseme Mapping (Guía 8) en lugar de generar otras nuevas; Pipeline Status luego muestra Visemes sin marcar, lo cual está bien.

**Omitir seguimiento ocular:**
Tu avatar no tiene movimiento ocular en VRChat y mira al frente. Esto es aceptable cuando no tiene huesos oculares.

**Saltar pose a forma:**
Opcional: omítalo si no tienes expresiones personalizadas para guardar.

Siguiente: [Herramientas de plataforma](05-rig-tools.md)
