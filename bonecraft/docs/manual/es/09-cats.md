# Herramientas de CATS

[← Contenidos](index.md)

Las herramientas CATS están en la pestaña **CATS** en la barra lateral derecha (presione**N**), en la sección**CATS** y en la pestaña**Properties** del editor**Scene** mientras Preferencias → Pestañas → Propiedades de escena → Mostrar está activado. El interruptor de ventana gráfica CATS y el interruptor de Propiedades de escena controlan sus propias copias de forma independiente. Siguen el proceso descrito en [La tubería CATS](04-cats-pipeline.md). Elige la armadura en la que trabajan en la parte superior de la sección.

En 9.1, varios paneles colocan configuraciones opcionales en un pliegue debajo de sus botones de acción. Las entradas necesarias antes de ejecutar una herramienta siguen siendo lo primero: arreglar los interruptores de limpieza del modelo, traducir el idioma de origen de los nombres de los huesos y las formas de la boca o los huesos de los ojos. Las herramientas óseas que ofrecen Ajustar última operación se ejecutan inmediatamente y le permiten ajustar sus opciones posteriormente. Pase el cursor sobre un botón u opción para leer su información sobre herramientas.

---

## Corregir Modelo

**Fase de tramitación:** 1 (siempre primero)

**Qué hace:** Una limpieza con un solo clic antes de cualquier otra operación CATS. Elimina problemas ocultos que, de otro modo, se estropearían silenciosamente en cada paso posterior.

**Opciones (cada una se puede desactivar):**
- Aplicar modificadores
- Eliminar dobles: fusionar vértices duplicados en la misma posición
- Recalcular normales: arreglar superficies de adentro hacia afuera
- Eliminar geometría suelta: caras no unidas al cuerpo
- Eliminar grupos de vértices vacíos
- Eliminar huesos de peso cero: huesos que no se mueven sin vértices
- Eliminar restricciones y cuerpos rígidos que VRChat no puede usar

Haga clic en **Fix Model** para ejecutarlos en la malla seleccionada en una sola pasada.

---

## Traducir Nombres de Huesos

**Qué hace:** Traduce los nombres de los huesos de su esqueleto a nombres en inglés VRChat. Funciona sin conexión, a partir de un diccionario integrado de nombres de huesos conocidos.

**Idiomas admitidos:** Japonés (日本語, el más común, de MMD y muchos modelos comunitarios), chino (中文), coreano (한국어), portugués (Português), español (Español) y francés (Français).

**Controles clave:** el**Language** de los nombres de las fuentes y el botón de traducción (**Translate Bone Names** ).

Se trata del idioma de los nombres de los huesos del modelo, no del idioma de la interfaz: para un modelo japonés MMD, utilícelo en cualquier idioma en el que esté configurado Bforartists.

---

## Unir Mallas

**Qué hace:** Combina los objetos de malla de tu avatar en una sola malla. VRChat funciona mejor con una malla por avatar. Cuando las mallas tienen diferentes claves de forma, CATS rellena las que faltan con formas neutras, de modo que la malla unida tenga un conjunto consistente.

**Controles clave:** la lista de mallas (actualícela con el botón al lado), luego**Join Meshes**.

**Cuándo usarlo:** después de colocar y pesar toda la ropa y los accesorios, y después de Fix Model. Unirse antes de Fix Model propaga los problemas de vértices duplicados de un objeto a otro; la malla unida mantiene los vértices fantasmas de cada objeto original, y los visemas generados lo desgarran en las costuras.

---

## Combinador de atlas de materiales

**Fase de tramitación:** 2 (opcional)

**Qué hace:** Hornea varios materiales en una hoja de textura (un atlas). Menos materiales dan un mejor rango de rendimiento VRChat.

**Controles clave:**
- **Analyze**: enumera sus materiales y texturas, con diagnósticos, grupos duplicados y anulaciones de tamaño. Elige qué materiales y qué texturas incluir: desmarca los que quieras mantener como están.
- **Smart Combine Materials** — la ruta recomendada: hornea el atlas y apunta cada malla hacia él; el atlas UV se convierte en UV0 para exportación
- **Bake Atlas**: un horneado sencillo;**Add Group** y**Remove Group** hornean grupos de materiales por separado
- Anular configuraciones heredadas: tamaño del atlas, método UV y semilla, ajuste preestablecido de empaque, relleno de horneado, paso de rotación de la isla y pases de horneado (Albedo de forma predeterminada; Normal, Emisión y Rugosidad se pueden hornear como salidas separadas)
- **Preserve Backup Duplicate**: conserva una copia de los originales
- **Accept — Delete Backup**: mantiene el resultado y elimina la copia de seguridad
- **Revert — Restore Originals** — vuelve a los materiales originales
- **Copy Debug Report**: copia los diagnósticos al portapapeles para obtener un informe de error

VRM / MToon los materiales mantienen su transparencia: el modo alfa se respeta y se compara con la textura alfa real, la emisión no se apaga y los mosaicos problemáticos se marcan en magenta después del horneado.

**Créditos de linaje:** este flujo de trabajo continúa el linaje de integración CATS, acredita el complemento Cats Blender original, acredita a Grim-es/material-combiner-addon por el linaje Material Combiner y acredita el kit de herramientas UV de Alexander Belyakov más el repositorio de archivos oRazeD/UVToolkit por la inspiración del flujo de trabajo UV. BoneCraft implementa sus propios asistentes UV de atlas en lugar de incluir la fuente UVToolkit.

---

## Visemas

**Fase de tramitación:** 3

**Qué hace:** Crea los 15 visemas VRChat a partir de tres formas de boca base.

**Controles clave:** **A Shape**,**O Shape** y**CH Shape** (elíjalos, o**Auto-Detect** ), luego**Generate Visemes**. Expanda Opciones debajo de los botones para elegir si desea sobrescribir los visemas existentes antes de generarlos. Ver [Guía 13, Fase 2](03-guides-b.md#fase-2--generación-de-visemas).

---

## Seguimiento Ocular

**Fase de canalización:** 4 (ejecutar después del modelo de reparación)

Sin Fix Model primero, la detección de ojos puede aferrarse a la geometría duplicada sobrante en lugar de los ojos reales y poner las restricciones en el espacio vacío: los avatares llegan a VRChat mirando al suelo.

**Qué hace:** Encuentra los huesos de los ojos de tu avatar, les asigna el nombre que requiere VRChat (`LeftEye` y `RightEye` ) y crea las restricciones de rotación que mueven los ojos de forma natural en VRChat.

**Controles clave:**
- **Auto-Detect**: encuentra huesos que coinciden con los nombres y posiciones de los huesos del ojo
- **Left Eye** y**Right Eye**: los huesos de los ojos, si los escoges tú mismo
- **Up Limit**,**Down Limit** y**Side Limit**: hasta dónde pueden girar los ojos
- **Create Eye Tracking**: cambia el nombre de los huesos y crea las restricciones

---

## Pose y Shape Keys

**Fase de tramitación:** 5 (opcional)

### Pose a Shape Key

Convierte la pose actual en una nueva clave de forma, para expresiones personalizadas o una forma de descanso corregida. Coloque la armadura en modo Pose, regrese al modo Objeto, luego haga clic en **Pose to Shape Key** y asigne un nombre a la clave de forma.

### Shape Key a Basis

Lo contrario: hornea una forma clave en la forma de resto neutral de la malla. Úselo para fijar una postura de descanso corregida para siempre. Ejecútelo también después de Fix Model.

---

## Transformaciones y FBT

**Fase de tramitación:** 6 (última)

### Aplicar Todas las Transformaciones

Aplica posición, rotación y escala a la malla y la armadura juntas, para que todo se lea como valores limpios. El SDK VRChat necesita esto: la escala no aplicada hace que los avatares tengan el tamaño incorrecto en VRChat.

### Corregir FBT

Una corrección de transformación para configuraciones de seguimiento de cuerpo completo: mueve el hueso de la raíz al nivel del suelo.

### Eliminar FBT

Elimina nuevamente la corrección Fix FBT.

---

## Herramientas de Huesos

- **Create Root Bone**: agrega un hueso de raíz (nombrado por**Root Name** ) en la parte inferior de la jerarquía
- **Merge Bones**: fusiona huesos más cortos que el**Merge Threshold** con sus padres
- **Duplicate Bones**: duplica los huesos seleccionados

---

## Herramientas de Armadura

**Qué hace:** Fusiona una armadura con otra, por ejemplo, la armadura de un atuendo con la del cuerpo.

**Controles clave:**
- **Base / Root** — la armadura que permanece (el resultado mantiene su nombre)
- **Incoming** — la armadura que se fusiona con ella; Los huesos con el mismo nombre se pliegan en la base.
- Naming Prep: hace que los nombres de los huesos de las dos rigs coincidan antes de fusionarse. Funciona en cualquier rig, no solo en las importaciones de Mixamo: elija Mixamo Prefixed y haga clic en **Normalize Merge Names**, luego elija Mixamo Stripped y normalice nuevamente; Ambas rigs terminan con los mismos nombres.
- Opciones para emparentar los huesos automáticamente y unir las mallas posteriormente
- **Merge Incoming Into Base** - fusiona

Para una fusión por etapas con vistas previas, utilice Bone Merge (consulte [Constructor de plataformas](06-rig-builder.md#fusión-de-huesos) ).

---

## Herramientas de Malla

- **Separate by Materials** — una malla por material
- **Separate by Loose Parts**: una malla por pieza conectada
- **Separate by Shape Keys**: divide las partes que mueven las teclas de forma

---

## Smart Automatic Weights (pesos automáticos inteligentes)

**Smart Automatic Weights** abre un cuadro de diálogo: verifique la malla de destino y la armadura, luego elija Cuerpo para recalcular a partir del rig existente o Ropa para transferir desde una malla de origen ponderada. El cuadro de diálogo utiliza valores predeterminados inteligentes y mantiene una copia de seguridad oculta.**Advanced Recalculation** expande una sugerencia de ubicación para los controles completos en BoneCraft → Máscara → Herramientas de peso; no abre esos controles aquí. Ver [Herramientas de plataforma](05-rig-tools.md#recálculo-automático-de-pesos-de-huesos).

---

## Estado del Pipeline y Registro de Operaciones

El estado de la canalización muestra cuál de las seis fases está completa. El Libro mayor de operaciones enumera cada operación CATS con su tiempo y resultado (cambiado, limpio o fallido); **Copy** lo coloca en el portapapeles y**Clear** lo vacía. Ver [La tubería CATS](04-cats-pipeline.md).

Siguiente: [Soluciones rápidas y glosario](10-reference.md)
