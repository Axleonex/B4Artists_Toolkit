# Guías 8–13

[← Índice](index.md)

## Guía 8: configura la sincronización labial

> **Tiempo:** unos 10–20 minutos
> **Resultado:** la boca de tu avatar moviéndose correctamente cuando hablas en VRChat

**Antes de empezar, comprueba esto:**
- [ ] La malla de la cabeza de tu avatar tiene shape keys de boca (también llamados blend shapes o morph targets: las distintas posiciones de la boca para hablar)
- [ ] Sabes más o menos cómo se llaman los shape keys (mira la lista Shape Keys en las propiedades de Datos del objeto de la malla)

> Visema = una forma de boca para un sonido. `aa` es el sonido «a», `O` el sonido «o», y así sucesivamente. VRChat usa 15 visemas para mover la sincronización labial de tu avatar.
>
> Shape key (blend shape) = una versión guardada de tu malla en otra posición. Tu shape key de boca abierta es tu malla con la boca abierta.

---

### Paso 1 — Abrir VRChat Viseme Mapping

En la pestaña **CATS** de la barra lateral derecha, despliega **VRChat** → **VRChat Viseme Mapping** (mapeo de visemas de VRChat).

---

### Paso 2 — Mapear automáticamente los visemas

Haz clic en **Mapear Todos los Visemas Automáticamente**. BoneCraft lee los shape keys de tu malla y los empareja por nombre con las 15 ranuras de visemas de VRChat.

**Lo que deberías ver:** la lista de visemas, con la mayoría de las ranuras mostrando un shape key mapeado.

---

### Paso 3 — Rellenar las ranuras que faltan

Una ranura sin shape key muestra «(unmapped)» (sin mapear). Haz clic en el botón de una ranura para abrir una lista de búsqueda con los shape keys de tu malla y elige el más parecido (escribe para filtrar la lista). Elige «(unmapped)» para vaciar una ranura. Coincidencias habituales:

| Visema de VRChat | Cómo suena | Shape key que buscar |
|---|---|---|
| `aa` | «a» | mouth_open, A, aa |
| `O` | «o» | mouth_o, OH, oh |
| `CH` | «ch» / «sh» | mouth_ch, CH |
| `PP` | labios juntos (P, B, M) | mouth_m, MM, lips_together |
| `SS` | «sss» / «zzz» | mouth_s, SS |

**¿No hay ningún shape key de visema?** Si la boca tiene al menos tres formas base (A, O y CH), la sección **Visemas** de la pestaña CATS crea los 15 a partir de ellas. Si no hay ninguna forma de boca, crea primero esas tres. Consulta la [guía 13, fase 2](#fase-2--generación-de-visemas).

---

### Paso 4 — Comprobar una forma de boca

Para ver una forma de boca mapeada, pon el valor de su shape key en 1.0 en la lista Shape Keys de la malla (Propiedades → Datos del objeto) y luego vuelve a ponerlo en 0.

---

### Paso 5 — Seguimiento facial (opcional)

Debajo de la lista de visemas, **Seguimiento Facial (SteamVR)** prepara formas de expresión para hardware de seguimiento facial. Es opcional: la mayoría de los usuarios no lo necesitan.

**Lo que esto desbloquea:** la boca de tu avatar se mueve cuando hablas en VRChat. Las expresiones se basan en los shape keys que acabas de mapear.

---

## Guía 9: mejora el rendimiento de tu avatar

> **Tiempo:** unos 15–25 minutos
> **Resultado:** un mejor rango de rendimiento en VRChat y una carga más rápida para otros jugadores

**Antes de empezar, comprueba esto:**
- [ ] Tu avatar está terminado (con rig, con ropa, con sincronización labial configurada)
- [ ] Conoces tu rango objetivo (Good o Excellent para la mayoría de los usuarios)

> Rango de rendimiento = la valoración de VRChat de lo exigente que es tu avatar. Los avatares Very Poor pueden quedar ocultos para otros jugadores. Los avatares Good y Excellent cargan rápido y siempre se muestran.

---

### Paso 1 — Comprobar el rango actual

En la pestaña **CATS**, despliega **VRChat** → **Verificar Rendimiento**. Haz clic en **Calculate Performance Rank** (calcular rango de rendimiento). BoneCraft muestra el rango global y un desglose (polígonos, mallas con skin, ranuras de material, huesos, PhysBones y contactos), con lo lejos que está cada uno del siguiente nivel.

---

### Paso 2 — Limpiar

El Optimizador VRChat de la misma sección enumera correcciones seguras. El **Modo Hipotético** está activado al principio: cada corrección informa de lo que cambiaría sin cambiar nada. Desmárcalo, porque mientras está activo las correcciones solo informan, y ejecuta las correcciones que quieras:

1. **Eliminar Huesos de Peso Cero** — borra los huesos que no mueven ninguna parte de la malla
2. **Combinar Mallas del Mismo Material** — une las mallas que comparten un material
3. **Eliminar Shape Keys No Utilizados** — borra los shape keys que nada usa
4. **Eliminar Grupos de Vértices No Utilizados** — quita los grupos de pesos vacíos

---

### Paso 3 — Reducir el número de polígonos (si hace falta)

Si el número de polígonos es demasiado alto, usa la Decimación VRChat de la misma sección con la malla seleccionada: fija la proporción objetivo (0.5 reduce los polígonos a la mitad, 0.8 quita un 20 %), haz clic en **Vista previa** para ver el resultado y en **Aplicar** para conservarlo. Los shape keys quedan protegidos durante la decimación.

> Empieza en 0.8 y ve bajando: las reducciones pequeñas rara vez cambian el aspecto del avatar, pero pueden mejorar mucho el rendimiento.

---

### Paso 4 — Combinar materiales (opcional)

Si tu avatar usa muchos materiales, combínalos en una sola hoja de textura (un atlas). En la pestaña **CATS** → **CATS** → **Atlas de Materiales**:

1. Haz clic en **Analyze** (analizar) para ver tus materiales y texturas. Elige cuáles incluir.
2. Haz clic en **Smart Combine Materials** (combinación inteligente de materiales) (o en **Hornear Atlas** para un horneado simple). BoneCraft hornea el atlas y hace que cada malla apunte a él; se guarda una copia de seguridad de los originales.
3. Haz clic en **Aceptar — Eliminar Copia de Seguridad** para conservar el resultado, o en **Revertir — Restaurar Originales** para volver atrás.

[Herramientas de CATS: Combinador de atlas de materiales](09-cats.md#combinador-de-atlas-de-materiales) explica cada ajuste.

---

### Paso 5 — Volver a comprobar el rango

Haz clic de nuevo en **Calculate Performance Rank** para ver la mejora.

**Lo que esto desbloquea:** un rango mejor significa que más jugadores ven tu avatar. Un avatar Good o Excellent carga rápido, usa menos GPU y se muestra por defecto a otros jugadores.

---

## Guía 10: guarda y reutiliza poses

> **Tiempo:** unos 5–10 minutos
> **Resultado:** una biblioteca de poses guardadas que puedes aplicar con un clic

**Antes de empezar, comprueba esto:**
- [ ] Tu avatar tiene un esqueleto terminado
- [ ] Estás en **Modo Pose** (selecciona la armadura y pulsa Ctrl+Tab, o usa el menú desplegable de modos de arriba a la izquierda de la vista)

---

### Paso 1 — Abrir la biblioteca de poses

En la pestaña **BoneCraft** de la Tool Shelf izquierda, despliega **Revisión** → **Biblioteca de Poses**.

---

### Paso 2 — Posar tu avatar

Mueve los huesos a la posición que quieras guardar: gira los brazos, inclina la cabeza. Cualquier combinación de posiciones de huesos es una pose.

---

### Paso 3 — Guardar la pose

Haz clic en **Guardar** y pon un nombre a la pose (por ejemplo «Peace Sign» o «Thinking»). **Categoría** la archiva en un grupo como «Greetings»; el **Filtro** de arriba muestra una categoría cada vez. Con la pose se captura una miniatura de la vista.

---

### Paso 4 — Aplicar una pose guardada

Selecciona una pose y haz clic en **Aplicar**.

- **Mezclar** — aplica la pose con intensidad parcial, para mezclar dos poses
- **Espejo** — aplica la pose invertida de izquierda a derecha

**Renombrar** y **Eliminar** gestionan la lista.

---

### Paso 5 — Exportar e importar poses

**Exportar** guarda tu biblioteca de poses en un archivo `.bfpose` que puedes conservar con el proyecto o compartir. **Importar** carga poses desde un archivo `.bfpose`.

**Lo que esto desbloquea:** una biblioteca de poses propia que puedes reutilizar entre proyectos, mezclar para claves de animación o compartir con otros usuarios de BoneCraft.

---

## Guía 11: une dos rigs

> **Tiempo:** unos 25–40 minutos según la complejidad
> **Resultado:** dos esqueletos combinados en uno, con todos los pesos conservados

**Antes de empezar, comprueba esto:**
- [ ] El avatar base y el segundo rig (un rig de ropa o de accesorio) están en el mismo archivo
- [ ] Ambos tienen rig y pesos

> Unir rigs = absorber un esqueleto dentro de otro, para acabar con un solo esqueleto combinado. Útil cuando un rig de cuerpo y un rig de cabello o de ropa deben ser uno.

---

### Paso 1 — Abrir Fusión de Huesos

En la pestaña **BoneCraft**, despliega la sección **Fusión de Huesos**. Funciona en tres etapas; cada una se abre cuando termina la anterior.

---

### Paso 2 — Etapa 1: alcance

Elige la armadura **Base** (el esqueleto del cuerpo, que se queda) y la armadura que se fusiona en ella (el rig de ropa o de cabello, que se añade a la base y luego se oculta). Haz clic en **Analyze** (analizar).

BoneCraft compara los dos esqueletos y enumera:
- ✓ Matched (coincidentes) — huesos que existen en ambos y están alineados
- \+ Source only (solo origen) — huesos del rig que se fusiona sin equivalente en la base
- − Target only (solo destino) — huesos de la base que el rig que se fusiona no tiene

Cuando hayas leído la lista, haz clic en **Acknowledge Scope — Proceed to Rename** (confirmar alcance — pasar a renombrar).

---

### Paso 3 — Etapa 2: renombrar

Para cada hueso «solo origen», decide qué es:

- Dale el nombre del hueso de la base al que representa y haz clic en **Apply Rename** (aplicar renombrado)
- Haz clic en **Mark as Unique** (marcar como único) si es un hueso nuevo sin equivalente (se añade a la base tal cual)

**Normalize Both Armatures** (normalizar ambas armaduras) renombra los huesos estándar (columna, brazos, piernas, etc.) que BoneCraft reconoce en ambos rigs. **Auto-Propose Renames** (proponer renombrados automáticamente) sugiere nombres para el resto a partir de la posición de cada hueso; **Apply Batch Pattern** (aplicar patrón por lotes) renombra muchos huesos con un solo patrón.

Cuando cada hueso «solo origen» esté resuelto, haz clic en **Verify Rename — Proceed to Merge** (verificar renombrado — pasar a fusionar).

---

### Paso 4 — Etapa 3: fusionar

Haz clic primero en **Run Merge Preview** (ejecutar vista previa de fusión): informa de lo que hará la fusión sin cambiar nada.

Cuando el informe parezca correcto, haz clic en **Combinar Armaduras**. BoneCraft hace una copia de seguridad de ambas armaduras y luego las combina.

**Lo que deberías ver:** una sola armadura con todos los huesos de ambos esqueletos, y cada malla con pesos respecto a ella.

**Lo que esto desbloquea:** un único rig más fácil de exportar y editar. Necesario para cualquier avatar con rigs de ropa o accesorios separados.

---

## Guía 12: soluciona problemas de subida

> **Tiempo:** unos 5–15 minutos según el problema

**Antes de empezar:** busca tu problema en la lista de abajo y ve a esa sección.

---

### «La subida falló — huesos no reconocidos»

Tus huesos tienen nombres que VRChat no entiende. → [Guía 4: corrige los nombres de los huesos de tu avatar](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar)

---

### «El avatar está en pose en T / no se mueve conmigo en VRChat»

Falta el mapeo humanoide o está mal. → [Guía 5: mapea tu avatar al sistema corporal de VRChat](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat)

---

### «La malla se deforma de forma rara / la piel se estira mal»

Hay que ajustar los pesos de los huesos. → Consulta la transferencia de pesos y el espejo de pesos en [Herramientas de rig](05-rig-tools.md), o ejecuta **Smart Automatic Weights** (pesos automáticos inteligentes) en la pestaña CATS.

---

### «El cabello atraviesa la cabeza»

Faltan colisionadores de cabello o son demasiado pequeños. → [Guía 6: añade física de cabello](02-guides-a.md#guía-6-añade-física-de-cabello), paso 5.

---

### «El avatar tiene rendimiento Very Poor y otros jugadores lo bloquean»

→ [Guía 9: mejora el rendimiento de tu avatar](#guía-9-mejora-el-rendimiento-de-tu-avatar)

---

### «La sincronización labial no funciona»

Los visemas no están bien mapeados. → [Guía 8: configura la sincronización labial](#guía-8-configura-la-sincronización-labial)

---

### «El validador de rig muestra errores»

En la pestaña **BoneCraft**, despliega **Revisión** → **Validador de Rig** y haz clic en **Ejecutar validación**. Cada resultado nombra el problema y el hueso; sigue su sugerencia o consulta el [Índice de soluciones rápidas](10-reference.md#índice-de-soluciones-rápidas). **Export Report** (exportar informe) guarda los resultados en un archivo.

---

### «La importación de VRM no funciona»

Puede que el complemento VRM no esté instalado. → [Guía 2](02-guides-a.md#guía-2-lleva-un-avatar-de-vroid-a-vrchat), paso 1.

---

### «La importación de MMD no funciona»

Puede que el complemento mmd_tools no esté instalado. → [Guía 3](02-guides-a.md#guía-3-lleva-un-avatar-de-mmd-a-vrchat), paso 1.

---

## Guía 13: prepara tu avatar para VRChat con CATS

> **Tiempo:** unos 20–35 minutos para una pasada completa del pipeline
> **Resultado:** un avatar limpio y optimizado, con sincronización labial, seguimiento ocular y transformaciones correctas, listo para subirlo a VRChat

**Antes de empezar, lee esto primero:**

Las herramientas de CATS siguen un pipeline: cada fase debe hacerse en orden. El Estado del Pipeline de la pestaña CATS marca cada fase que has terminado (Corregir Modelo, Atlas de Materiales, Visemas, Seguimiento Ocular, Pose a Shape Key, Aplicar transformaciones), y el Registro de Operaciones enumera cada operación de CATS que has ejecutado. Una herramienta cuya fase anterior no está hecha se ejecuta igualmente, pero muestra un aviso como «Run Fix Model first for best results» (ejecuta primero Corregir Modelo para obtener los mejores resultados).

**Empieza siempre con Corregir Modelo. Cada vez. Sin excepción.**

Lee [El pipeline de CATS](04-cats-pipeline.md) antes de seguir, si aún no lo has hecho.

**Antes de empezar, comprueba esto:**
- [ ] Tu avatar está importado y visible en la vista 3D
- [ ] La pestaña CATS está abierta en la barra lateral derecha (pulsa N si la barra está oculta)
- [ ] Tu avatar está seleccionado (haz clic en él en la vista o en el outliner)

---

### Fase 1 — Corregir Modelo

Corregir Modelo es la base obligatoria de todo lo demás en CATS. Ejecútalo primero, aunque tu modelo parezca bien: elimina problemas ocultos que, si no, romperían en silencio las herramientas que vienen después.

**Lo que hace Corregir Modelo** (cada parte se puede desactivar en sus opciones):
- Aplica los modificadores
- Elimina vértices duplicados y geometría suelta (triángulos que flotan lejos del cuerpo)
- Recalcula las normales (las direcciones que deciden qué lado de la malla mira hacia fuera)
- Elimina los grupos de vértices vacíos y los huesos de peso cero
- Elimina las restricciones y los cuerpos rígidos que VRChat no puede usar

**Pasos:**
1. En la pestaña **CATS**, despliega **CATS** → **Corregir Modelo**
2. Asegúrate de que la malla de tu avatar está seleccionada
3. Haz clic en **Corregir Modelo** y espera; en mallas grandes tarda unos segundos
4. Comprueba que el Estado del Pipeline muestra una marca (✓) en Corregir Modelo

**Lo que deberías ver:** tu avatar se ve igual o algo más limpio. El Estado del Pipeline marca Corregir Modelo y el Registro de Operaciones muestra la ejecución.

> **Si tu modelo desaparece o se ve del revés tras Corregir Modelo:** las normales de la malla estaban invertidas. Selecciona la malla, entra en Modo Edición (Tab), selecciona todo (A) y usa Malla > Normales > Invertir. Luego ejecuta Corregir Modelo de nuevo.

---

### Fase 2 — Generación de visemas

Ejecutar después de: Corregir Modelo ✓

La sección Visemas crea las 15 formas de boca de sincronización labial de VRChat a partir de tres formas base que ya tienes. Si tu avatar ya tiene shape keys de visemas completos, puedes saltarte esta fase, pero compruébalos en VRChat Viseme Mapping (guía 8).

VRChat necesita 15 formas de boca (visemas) para mover los labios de tu avatar cuando hablas. La mayoría de los avatares solo tienen unas pocas formas básicas de boca. CATS combina tus formas base para crear el resto.

Las tres formas base:
- **Forma A** — boca muy abierta (la forma de la «a»)
- **Forma O** — boca redondeada (la forma de la «o»)
- **Forma CH** — boca entreabierta con los dientes visibles (la forma de «ch» / «sh»)

**Pasos:**
1. En la pestaña **CATS**, despliega **CATS** → **Visemas**
2. Haz clic en **Detección Automática** para rellenar las tres formas, o elígelas tú (para claves con nombres como `mouth_open`, `vrc.v_O` o `mouth_wide`, elige la más parecida)
3. Haz clic en **Generar Visemas**
4. CATS crea 15 shape keys con los nombres de VRChat (`vrc.v_aa`, `vrc.v_O`, `vrc.v_CH`, etc.)
5. Comprueba que el Estado del Pipeline muestra Visemas ✓

**Lo que deberías ver:** 15 shape keys nuevos en la lista Shape Keys de la malla (Propiedades → Datos del objeto → Shape Keys).

> **Si tu avatar no tiene ningún shape key de boca:** crea tú al menos A, O y CH (esculpe o edita esas formas como shape keys) antes de que CATS pueda generar el resto. Consulta la entrada Shape key del glosario.

---

### Fase 3 — Seguimiento Ocular

Ejecutar después de: Corregir Modelo ✓

El seguimiento ocular configura los huesos de los ojos de tu avatar para el seguimiento ocular integrado de VRChat, de modo que los ojos se muevan con naturalidad y miren a otros jugadores.

**Lo que hace:**
- Encuentra los huesos del ojo izquierdo y del derecho
- Los nombra como exige VRChat (`LeftEye` y `RightEye`)
- Añade las restricciones de rotación que VRChat necesita para mover los ojos
- Limita la rotación de los ojos a un rango natural (arriba, abajo y a los lados)

Sin Corregir Modelo antes, la detección de ojos puede engancharse a vértices duplicados sobrantes en lugar de los ojos reales y poner las restricciones en el lugar equivocado: los avatares llegan a VRChat con los dos ojos clavados mirando hacia abajo.

**Pasos:**
1. En la pestaña **CATS**, despliega **CATS** → **Seguimiento Ocular**
2. Haz clic en **Detección Automática**; CATS busca huesos cuyo nombre o posición coincidan con huesos de ojos
3. Revisa los campos **Ojo Izquierdo** y **Ojo Derecho**; elige tú los huesos si están mal
4. Ajusta el **Límite Superior**, el **Límite Inferior** y el **Límite Lateral** si hace falta
5. Haz clic en **Crear Seguimiento Ocular**
6. Comprueba que el Estado del Pipeline muestra Seguimiento Ocular ✓

**Lo que deberías ver:** ambos huesos de los ojos renombrados, con restricciones de rotación en el panel Restricciones de hueso.

> **Si CATS no encuentra huesos de ojos:** puede que tu esqueleto no tenga. Algunos formatos (sobre todo modelos MMD antiguos) parpadean con shape keys en lugar de huesos. Sáltate esta fase: VRChat recurre a la animación de ojos por shape keys cuando no hay huesos de ojos.

---

### Fase 4 — Pose a Shape Key

Ejecutar después de: Corregir Modelo ✓

Pose a Shape Key convierte la pose actual de tu avatar en un shape key. Úsalo para capturar expresiones personalizadas o poses de reposo para el menú de expresiones de VRChat.

Sin Corregir Modelo antes, el orden de los vértices aún puede tener huecos de los duplicados eliminados, así que el shape key captura geometría deformada: shape keys que hacen estallar la malla hacia fuera cuando se activan en VRChat.

**Pasos:**
1. Posa tu avatar en Modo Pose (selecciona la armadura, pulsa Ctrl+Tab)
2. Mueve los huesos a la expresión o posición que quieras capturar
3. Vuelve al Modo Objeto (Ctrl+Tab de nuevo)
4. En la pestaña **CATS**, despliega **CATS** → **Pose y Shape Keys**
5. Haz clic en **Pose a Shape Key** y pon nombre al nuevo shape key
6. Comprueba que el Estado del Pipeline muestra Pose a Shape Key ✓

**Lo que deberías ver:** un shape key nuevo en la lista de la malla. Pon su valor en 1.0 para comprobar que muestra la pose.

> **Shape Key a Basis:** la herramienta complementaria hace lo contrario: hornea un shape key en la forma de reposo neutra de la malla. Úsala para fijar una pose de reposo corregida. Ejecútala también después de Corregir Modelo.

---

### Fase 5 — Aplicar transformaciones

Ejecutar después de: todas las fases anteriores que necesites

La última fase. Aplicar transformaciones congela toda la posición, la rotación y la escala en la malla y el esqueleto, para que todo se lea con valores limpios (posición 0,0,0 / rotación 0°,0°,0° / escala 1.0). El SDK de VRChat necesita transformaciones limpias: en especial, una escala sin aplicar hace que los avatares aparezcan con el tamaño equivocado o con una física que se comporta mal.

Aplicar las transformaciones antes de las fases anteriores hornea sus problemas en la malla para siempre: avatares que se ven bien en Bforartists pero aparecen en VRChat a una fracción de su altura.

**Las herramientas de Transformaciones y FBT:**
- **Aplicar Todas las Transformaciones** — aplica posición, rotación y escala a la malla y a la armadura a la vez
- **Corregir FBT** — una corrección de transformación para configuraciones de Full Body Tracking (mueve el hueso raíz al nivel del suelo)
- **Eliminar FBT** — quita de nuevo esa corrección

**Pasos:**
1. Confirma que las fases que necesita tu avatar están marcadas en el Estado del Pipeline (Atlas de Materiales y Pose a Shape Key son opcionales, y Visemas queda sin marcar si mapeaste visemas existentes)
2. En la pestaña **CATS**, despliega **CATS** → **Transformaciones y FBT**
3. Haz clic en **Aplicar Todas las Transformaciones**
4. Comprueba que el Estado del Pipeline muestra Aplicar transformaciones ✓
5. Exporta tu avatar (VRChat → Exportar a VRChat, guía 1 paso 9)

**Lo que deberías ver:** Aplicar transformaciones marcado, después de las fases que necesitabas. Tu avatar está listo para el VRChat Creator Companion.

---

**Lo que esto desbloquea:** un avatar totalmente procesado, con geometría limpia, los 15 visemas, seguimiento ocular (cuando tiene huesos de ojos), las expresiones personalizadas que hayas creado y transformaciones limpias: todo lo que necesita una subida a VRChat para funcionar a la primera.

Siguiente: [El pipeline de CATS](04-cats-pipeline.md)
