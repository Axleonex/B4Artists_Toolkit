# Guías 8–13

[← Contenidos](index.md)

## Guía 8: configura la sincronización labial

> **Tiempo:** Entre 10 y 20 minutos
> **Resultado:** La boca de tu avatar se mueve correctamente cuando hablas en VRChat

**Antes de comenzar, comprueba esto:**
- [] La malla de la cabeza de tu avatar tiene teclas de forma de boca (también llamadas formas de combinación o objetivos de transformación: las diferentes posiciones de la boca para hablar)
- [] Sabes aproximadamente cómo se llaman las claves de forma (mira en la lista de Claves de forma de las propiedades de Datos de objeto de la malla)

> Viseme = forma de boca para un sonido. `aa` es el sonido "ahh", `O` el sonido "ohh", y así sucesivamente. VRChat utiliza 15 visemas para impulsar la sincronización de labios de tu avatar.
>
> Tecla de forma (mezclar forma) = una versión guardada de su malla en otra posición. Tu llave de forma con la boca abierta es tu malla con la boca abierta.

---

### Paso 1 — Abrir VRChat Viseme Mapping

En la pestaña **CATS** en la barra lateral derecha, expanda**Avatar Tools** →**VRChat Viseme Mapping**.

---

### Paso 2 — Mapear automáticamente los visemas

Haga clic en **Auto-Map All Visemes**. BoneCraft lee las claves de forma de su malla y las relaciona con las 15 ranuras de viseme de VRChat por nombre.

**Lo que deberías ver:** La lista de visemas, donde la mayoría de las ranuras muestran una clave de forma asignada.

---

### Paso 3 — Rellenar las ranuras que faltan

Una ranura sin clave de forma muestra "(sin asignar)". Haga clic en el botón de una ranura para abrir una lista de búsqueda de las claves de forma de su malla y elija la más cercana (escriba para filtrar la lista). Elija "(sin asignar)" para borrar un espacio. Partidos comunes:

|VRChat visema|como suena|Clave de forma a buscar|
|---|---|---|
|`aa` |"ahh"|boca_abierta, A, aa|
|`O` |"oh"|boca_o, oh, oh|
|`CH` |"ch" / "sh"|boca_ch, CH|
|`PP` |labios juntos (P, B, M)|boca_m, MM, labios_juntos|
|`SS` |"sss" / "zzz"|boca_s, SS|

**¿No hay ninguna clave de forma de visema?** Si la boca tiene al menos tres formas base (A, O y CH), la sección**Visemes** de la pestaña CATS crea las 15 a partir de ellas. Sin ninguna forma de boca, haz esas tres primero. Ver [Guía 13, Fase 2](#fase-2--generación-de-visemas).

---

### Paso 4 — Comprobar una forma de boca

Para ver una forma de boca mapeada, establezca el valor de su clave de forma en 1.0 en la lista Claves de forma de la malla (Propiedades → Datos del objeto), luego configúrelo nuevamente en 0.

---

### Paso 5 — Seguimiento facial (opcional)

Debajo de la lista de visemas, **Face Tracking (SteamVR)** prepara formas de expresión para hardware de seguimiento facial. Es opcional: la mayoría de los usuarios no lo necesitan.

**Qué desbloquea:** La boca de tu avatar se mueve cuando hablas en VRChat. Las expresiones se basan en las claves de forma que acabas de asignar.

---

## Guía 9: mejora el rendimiento de tu avatar

> **Tiempo:** Entre 15 y 25 minutos
> **Resultado:** Un mejor rango de rendimiento VRChat y una carga más rápida para otros jugadores

**Antes de comenzar, comprueba esto:**
- [] Tu avatar está completo (equipado, vestido, sincronización de labios configurada)
- [] Conoce su rango objetivo (Bueno o Excelente para la mayoría de los usuarios)

> Clasificación de rendimiento = calificación VRChat de qué tan exigente es tu avatar. Otros jugadores pueden ocultar los avatares muy pobres. Los avatares buenos y excelentes se cargan rápidamente y siempre se muestran.

---

### Paso 1 — Comprobar el rango actual

En la pestaña **CATS**, expanda**VRChat Tools** y busque su grupo Rendimiento. Haga clic en**Calculate Performance Rank**. BoneCraft muestra la clasificación general y un desglose (polígonos, mallas sin piel, ranuras de material, huesos, PhysBones y contactos) con qué tan lejos está cada uno del siguiente nivel.

---

### Paso 2 — Limpiar

El optimizador VRChat en la misma sección enumera soluciones seguras. **What-If Mode** está activado al principio: cada corrección informa lo que cambiaría sin cambiar nada. Desmárquelo, porque las correcciones solo informan mientras está activado y ejecute las correcciones que desee:

1. **Remove Zero-Weight Bones**: elimina huesos que no mueven ninguna parte de la malla
2. **Merge Same-Material Meshes** — une mallas que comparten un material
3. **Remove Unused Shape Keys**: elimina claves de formas que nada usa
4. **Remove Unused Vertex Groups**: elimina grupos de peso vacíos

---

### Paso 3 — Reducir el número de polígonos (si hace falta)

Si el recuento de polígonos es demasiado alto, utilice VRChat Decimación en la misma sección con la malla seleccionada: establezca la proporción objetivo (0,5 divide a la mitad los polígonos, 0,8 elimina el 20%), haga clic en **Preview** para ver el resultado y en**Apply** para conservarlo. Las claves de forma están protegidas mientras se diezman.

> Comience en 0.8 y vaya hacia abajo: las pequeñas reducciones rara vez cambian la apariencia del avatar, pero pueden mejorar mucho el rendimiento.

---

### Paso 4 — Combinar materiales (opcional)

Si tu avatar usa muchos materiales, combínalos en una hoja de textura (un atlas). En la pestaña **CATS** →**CATS** →**Material Atlas**:

1. Haga clic en **Analyze** para ver sus materiales y texturas. Elija cuáles incluir.
2. Haga clic en **Smart Combine Materials** (o**Bake Atlas** para un horneado simple). BoneCraft hornea el atlas y apunta cada malla hacia él; se mantiene una copia de seguridad de los originales.
3. Haga clic en **Accept — Delete Backup** para conservar el resultado o en**Revert — Restore Originals** para regresar.

[CATS Herramientas: Combinador de materiales Atlas](09-cats.md#combinador-de-atlas-de-materiales) explica cada configuración.

---

### Paso 5 — Volver a comprobar el rango

Haga clic en **Calculate Performance Rank** nuevamente para ver la mejora.

**Qué desbloquea:** Una mejor clasificación significa que más jugadores ven tu avatar. Un avatar Bueno o Excelente se carga rápidamente, usa menos GPU y se muestra a otros jugadores de forma predeterminada.

---

## Guía 10: guarda y reutiliza poses

> **Tiempo:** Entre 5 y 10 minutos
> **Resultado:** Una biblioteca guardada de poses que puedes aplicar con un solo clic

**Antes de comenzar, comprueba esto:**
- [] Tu avatar tiene un esqueleto terminado.
- [] Estás en **Pose Mode** (selecciona la armadura y presiona Ctrl+Tab, o usa el menú desplegable de modo en la parte superior izquierda de la ventana gráfica)

---

### Paso 1 — Abrir la biblioteca de poses

En la pestaña **BoneCraft** en el estante de herramientas izquierdo, expanda**Review** →**Pose Library**.

---

### Paso 2 — Posar tu avatar

Mueva los huesos a la posición que desee mantener: gire los brazos, incline la cabeza; cualquier combinación de posiciones de los huesos es una postura.

---

### Paso 3 — Guardar la pose

Haz clic en **Save** y dale un nombre a la pose (por ejemplo, "Signo de la paz" o "Pensamiento").**Category** lo archiva en un grupo como "Saludos"; el**Filter** en la parte superior muestra una categoría a la vez. Se captura una miniatura de la ventana gráfica con la pose.

---

### Paso 4 — Aplicar una pose guardada

Seleccione una pose y haga clic en **Apply**.

- **Blend** — aplica la pose con fuerza parcial, para mezclar dos poses
- **Mirror**: aplica la pose volteada de izquierda a derecha

**Rename** y**Delete** administran la lista.

---

### Paso 5 — Exportar e importar poses

**Export** guarda su biblioteca de poses en un archivo `.bfpose` que puede conservar con el proyecto o compartir.**Import** carga poses desde un archivo `.bfpose`.

**Qué desbloquea:** Una biblioteca de poses personales que puedes reutilizar en todos los proyectos, combinar para obtener claves de animación o compartir con otros usuarios de BoneCraft.

---

## Guía 11: une dos rigs

> **Tiempo:** Entre 25 y 40 minutos, según la complejidad
> **Resultado:** Dos esqueletos combinados en uno, manteniendo todos los pesos

**Antes de comenzar, comprueba esto:**
- [] El avatar base y el segundo rig (un rig de ropa o accesorio) están en el mismo archivo.
- [] Ambos están equipados y pesados.

> Fusión de rigs = absorber un esqueleto en otro, por lo que terminas con un esqueleto combinado. Útil cuando un body rig y un hair o outfit deben convertirse en uno.

---

### Paso 1 — Abrir Fusión de Huesos

En la pestaña **BoneCraft**, expanda la sección**Bone Merge**. Funciona en tres etapas; cada uno se abre cuando el anterior está terminado.

---

### Paso 2 — Etapa 1: alcance

Elija la armadura **Base** (el esqueleto del cuerpo que permanece) y la armadura que se fusiona con ella (la ropa o el accesorio para el cabello, que se agrega a la base y luego se oculta). Haga clic en**Analyze**.

BoneCraft compara los dos esqueletos y enumera:
- ✓ Emparejados: huesos que existen en ambos y se alinean
- \+ Solo fuente: huesos de la rig fusionada sin coincidencias en la base
- − Solo objetivo: huesos base que la rig fusionada no tiene

Cuando haya leído la lista, haga clic en **Acknowledge Scope — Proceed to Rename**.

---

### Paso 3 — Etapa 2: renombrar

Para cada hueso de origen, decida qué es:

- Asígnale el nombre del hueso base que representa y haz clic en **Apply Rename**
- Haga clic en **Mark as Unique** si es un hueso nuevo sin equivalente (se agrega a la base tal como está)

**Normalize Both Armatures** cambia el nombre de los huesos estándar (columna vertebral, brazos, piernas, etc.) que BoneCraft reconoce en ambos rigs.**Auto-Propose Renames** sugiere nombres para el resto a partir de la posición de cada hueso;**Apply Batch Pattern** cambia el nombre de muchos huesos con un patrón.

Cuando se resuelva cada hueso de origen, haga clic en **Verify Rename — Proceed to Merge**.

---

### Paso 4 — Etapa 3: fusionar

Primero haga clic en **Run Merge Preview**: informa qué hará la combinación sin cambiar nada.

Cuando el informe se vea bien, haga clic en **Merge Armatures**. BoneCraft respalda ambas armaduras y luego las combina.

**Lo que deberías ver:** Una armadura que contiene todos los huesos de ambos esqueletos, con cada malla sujeta a ella.

**Qué desbloquea:** Un rig único que es más fácil de exportar y editar. Necesario para cualquier avatar con ropa o accesorios separados.

---

## Guía 12: soluciona problemas de subida

> **Tiempo:** Entre 5 y 15 minutos, según el problema

**Antes de comenzar:** Encuentre su problema en la lista a continuación y vaya a esa sección.

---

### «La subida falló — huesos no reconocidos»

Tus huesos tienen nombres que VRChat no entiende. → [Guía 4: arregla los nombres de los huesos de tu avatar](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar)

---

### «El avatar está en pose en T / no se mueve conmigo en VRChat»

El mapeo humanoide falta o es incorrecto. → [Guía 5: Asigne su avatar al sistema corporal de VRChat](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat)

---

### «La malla se deforma de forma rara / la piel se estira mal»

Es necesario ajustar los pesos óseos. → Consulte Transferencia de peso y Espejo de peso en [Herramientas de plataforma](05-rig-tools.md), o ejecute **Smart Automatic Weights** en la pestaña CATS.

---

### «El cabello atraviesa la cabeza»

Faltan colisionadores de pelo o son demasiado pequeños. → [Guía 6: Agregar la física del cabello](02-guides-a.md#guía-6-añade-física-de-cabello), Paso 5.

---

### «El avatar tiene rendimiento Very Poor y otros jugadores lo bloquean»

→ [Guía 9: Mejora el rendimiento de tu avatar](#guía-9-mejora-el-rendimiento-de-tu-avatar)

---

### «La sincronización labial no funciona»

Los visemas no están mapeados correctamente. → [Guía 8: Configurar sincronización de labios](#guía-8-configura-la-sincronización-labial)

---

### «El validador de rig muestra errores»

En la pestaña **BoneCraft**, expanda**Review** →**Rig Validator** y haga clic en**Run Validation**. Cada resultado nombra el problema y el hueso; siga su sugerencia o consulte el [Índice de solución rápida](10-reference.md#índice-de-soluciones-rápidas).**Export Report** guarda los resultados en un archivo.

---

### «La importación de VRM no funciona»

Es posible que el complemento VRM no esté instalado. → [Guía 2](02-guides-a.md#guía-2-lleva-un-avatar-de-vroid-a-vrchat), Paso 1.

---

### «La importación de MMD no funciona»

Es posible que el complemento mmd_tools no esté instalado. → [Guía 3](02-guides-a.md#guía-3-lleva-un-avatar-de-mmd-a-vrchat), Paso 1.

---

## Guía 13: prepara tu avatar para VRChat con CATS

> **Tiempo:** Entre 20 y 35 minutos para una ejecución completa del proceso
> **Resultado:** Un avatar limpio y optimizado con sincronización de labios, seguimiento ocular y transformaciones correctas, listo para cargar VRChat

**Antes de comenzar, lea esto primero:**

Las herramientas CATS siguen un proceso: cada fase debe realizarse en orden. El Estado de canalización de la pestaña CATS muestra una marca de verificación para cada fase que ha realizado (Reparar modelo, Atlas de materiales, Visemas, Seguimiento ocular, Pose para dar forma, Aplicar transformaciones) y el Libro mayor de operaciones enumera cada operación CATS que ejecutó. Una herramienta cuya fase anterior no se completó todavía se ejecuta, pero muestra una advertencia como "Ejecutar primero el modelo de reparación para obtener mejores resultados".

**Comience siempre con Fix Model. Cada vez. Sin excepción.**

Lea [La tubería CATS](04-cats-pipeline.md) antes de continuar, si aún no lo ha hecho.

**Antes de comenzar, comprueba esto:**
- [] Su avatar se importa y es visible en la ventana gráfica 3D
- [] La pestaña CATS está abierta en la barra lateral derecha (presione N si la barra lateral está oculta)
- [] Tu avatar está seleccionado (haz clic en él en la ventana gráfica o en el esquema)

---

### Fase 1 — Corregir Modelo

Fix Model es la base obligatoria para todo lo demás en CATS. Ejecútelo primero, incluso si su modelo se ve bien: elimina problemas ocultos que, de otro modo, dañarían silenciosamente las herramientas posteriores.

**Qué hace Fix Model** (cada parte se puede desactivar en sus opciones):
- Aplica modificadores
- Elimina vértices duplicados y geometría suelta (triángulos flotando lejos del cuerpo)
- Vuelve a calcular las normales (las direcciones que deciden qué lado de la malla mira hacia afuera)
- Elimina grupos de vértices vacíos y huesos de peso cero.
- Elimina restricciones y cuerpos rígidos que VRChat no puede utilizar.

**Pasos:**
1. En la pestaña **CATS**, expanda**CATS** →**Fix Model**
2. Asegúrate de que la malla de tu avatar esté seleccionada.
3. Haga clic en **Fix Model** y espere; para mallas grandes, esto demora unos segundos.
4. Verifique que el estado de la canalización muestre una marca de verificación ( ✓ ) para corregir el modelo

**Lo que deberías ver:** Tu avatar se ve igual o un poco más limpio. El estado de la canalización verifica el modelo de reparación y el libro mayor de operaciones enumera la ejecución.

> **Si su modelo desaparece o se ve del revés después de Corregir modelo:** las normales de la malla se invirtieron. Seleccione la malla, ingrese al Modo de edición (pestaña), seleccione todo (A), luego use Malla > Normales > Voltear. Luego ejecute Fix Model nuevamente.

---

### Fase 2 — Generación de visemas

Ejecutar después: Reparar modelo ✓

La sección Visemes crea las 15 formas de boca de sincronización labial VRChat a partir de tres formas básicas que ya tienes. Si tu avatar ya tiene claves de forma de visema completas, puedes omitir esta fase, pero compruébalas en VRChat Viseme Mapping (Guía 8).

VRChat necesita 15 formas de boca (visemes) para impulsar los labios de tu avatar cuando habla. La mayoría de los avatares tienen sólo unas pocas formas de boca básicas. CATS combina las formas de tu base para hacer el resto.

Las tres formas base:
- **A Shape** — boca bien abierta (la forma "ahh")
- **O Shape** — boca redondeada (la forma "ohh")
- **CH Shape** — boca estrecha y abierta con dientes visibles (la forma "ch" / "sh")

**Pasos:**
1. En la pestaña **CATS**, expanda**CATS** →**Visemes**
2. Haga clic en **Auto-Detect** para completar las tres formas, o selecciónelas usted mismo (para claves con nombres como `mouth_open`, `vrc.v_O` o `mouth_wide`, elija la que más se parezca)
3. Haga clic en **Generate Visemes**
4. CATS crea 15 claves de forma con los nombres de VRChat (`vrc.v_aa`, `vrc.v_O`, `vrc.v_CH`, etc.)
5. Verifique que el estado de la tubería muestre Visemes ✓

**Lo que deberías ver:** 15 nuevas claves de forma en la lista de claves de forma de la malla (Propiedades → Datos del objeto → Claves de forma).

> **Si tu avatar no tiene ninguna clave con forma de boca:** crea al menos A, O y CH tú mismo (esculpe o edítalas como claves con forma) antes de que CATS pueda generar el resto. Consulte la entrada del Glosario para Clave de forma.

---

### Fase 3 — Seguimiento Ocular

Ejecutar después: Reparar modelo ✓

Eye Tracking configura los huesos de los ojos de tu avatar para el seguimiento ocular integrado de VRChat, de modo que los ojos se muevan naturalmente y miren a otros jugadores.

**Qué hace:**
- Encuentra los huesos del ojo izquierdo y derecho.
- Los nombra como requiere VRChat (`LeftEye` y `RightEye` )
- Agrega las restricciones de rotación que VRChat necesita para mover los ojos.
- Limita la rotación de los ojos a un rango natural (arriba, abajo y hacia los lados)

Sin Fix Model primero, la detección de ojos puede bloquear los vértices duplicados sobrantes en lugar de los ojos reales y colocar las restricciones en el lugar equivocado: los avatares llegan a VRChat con ambos ojos atascados mirando hacia abajo.

**Pasos:**
1. En la pestaña **CATS**, expanda**CATS** →**Eye Tracking**
2. Haga clic en **Auto-Detect**: CATS busca huesos cuyos nombres o posiciones coincidan con los huesos del ojo.
3. Verifique los campos **Left Eye** y**Right Eye**; Elige los huesos tú mismo si están equivocados.
4. Configure **Up Limit**,**Down Limit** y**Side Limit** si es necesario
5. Haga clic en **Create Eye Tracking**
6. Verifique que el estado de la canalización muestre Eye Tracking ✓

**Lo que deberías ver:** Se cambió el nombre de ambos huesos del ojo, con restricciones de rotación en el panel Restricciones óseas.

> **Si CATS no puede encontrar los huesos de los ojos:** es posible que su esqueleto no tenga ninguno. Algunos formatos (especialmente los modelos MMD más antiguos) parpadean con teclas de forma en lugar de huesos. Omita esta fase: VRChat vuelve a la animación del ojo con forma clave cuando no hay huesos del ojo.

---

### Fase 4 — Pose a Shape Key

Ejecutar después: Reparar modelo ✓

Pose to Shape Key convierte la pose actual de tu avatar en una clave de forma. Úselo para capturar expresiones personalizadas o poses de descanso para el menú de expresiones de VRChat.

Sin Fix Model primero, el orden de los vértices aún puede contener espacios de duplicados eliminados, por lo que la clave de forma captura la geometría distorsionada: claves de forma que hacen que la malla explote hacia afuera cuando se activa en VRChat.

**Pasos:**
1. Posa tu avatar en modo Pose (selecciona la armadura, presiona Ctrl+Tab)
2. Mueve los huesos a la expresión o posición que deseas capturar.
3. Volver al modo Objeto (Ctrl+Tab nuevamente)
4. En la pestaña **CATS**, expanda**CATS** →**Pose & Shape Keys**
5. Haga clic en **Pose to Shape Key** y asigne un nombre a la nueva clave de forma.
6. Verifique que el estado de la tubería muestre Pose To Shape ✓

**Lo que deberías ver:** Una nueva clave de forma en la lista de la malla. Establece su valor en 1,0 para comprobar que muestra la pose.

> **Clave de forma a la base:** la herramienta complementaria hace lo contrario: crea una clave de forma en la forma de resto neutral de la malla. Úselo para fijar una postura de descanso corregida. Ejecútelo también después de Fix Model.

---

### Fase 5 — Aplicar transformaciones

Ejecutar después: cada fase anterior que necesitas

La última fase. Aplicar Transformaciones congela todas las posiciones, rotaciones y escalas en la malla y el esqueleto, por lo que todo se lee como valores limpios (posición 0,0,0 / rotación 0°,0°,0° / escala 1.0). El SDK VRChat necesita transformaciones limpias: la escala no aplicada en particular hace que los avatares aparezcan con el tamaño incorrecto o con físicas que se comportan mal.

La aplicación de transformaciones antes de las fases anteriores incorpora sus problemas a la malla para siempre: avatares que se ven bien en Bforartists pero que aparecen a una fracción de su altura en VRChat.

**Las herramientas en Transformaciones y FBT:**
- **Apply All Transforms**: aplica posición, rotación y escala a la malla y la armadura juntas
- **Fix FBT**: una corrección de transformación para configuraciones de seguimiento de cuerpo completo (mueve el hueso de la raíz al nivel del suelo)
- **Remove FBT**: elimina esa corrección nuevamente

**Pasos:**
1. Confirme que las fases que su avatar necesita estén marcadas en Estado de canalización (Material Atlas y Pose To Shape son opcionales, y Visemes permanece sin marcar cuando mapeó visemas existentes).
2. En la pestaña **CATS**, expanda**CATS** →**Transforms & FBT**
3. Haga clic en **Apply All Transforms**
4. Verifique que el estado de la canalización muestre Aplicar transformaciones ✓
5. Exporta tu avatar (VRChat → Exportar a VRChat, Guía 1 Paso 9)

**Lo que deberías ver:** Aplicar transformaciones marcada, después de las fases que necesitabas. Tu avatar está listo para VRChat Creator Companion.

---

**Qué desbloquea:** Un avatar completamente procesado con geometría limpia, los 15 visemas, seguimiento ocular (cuando tiene huesos oculares), cualquier expresión personalizada que hayas hecho y transformaciones limpias: todo lo que una carga VRChat necesita para funcionar la primera vez.

Siguiente: [La tubería CATS](04-cats-pipeline.md)
