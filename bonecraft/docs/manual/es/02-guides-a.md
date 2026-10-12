# Guías 1–7

[← Contenidos](index.md)

## Guía 1: lleva tu primer avatar a VRChat

Para practicar una malla antes de usar tu propio avatar, sigue [taller de maniquíes ilustrados](06-rig-builder.md#taller-de-maniquíes-ilustrados): Simple Human, un maniquí sin rig, Auto-Rig y luego IK/FK.

> **Tiempo:** Entre 45 y 60 minutos para una primera ejecución completa
> **Resultado:** Un avatar manipulado y listo para VRChat exportado para el SDK VRChat

**Antes de comenzar, comprueba esto:**
- [] Su modelo 3D se importa a Bforartists (Archivo > Importar, elija su formato)
- [] El modelo está en una pose de T (brazos hacia los lados, cuerpo erguido), o cerca de ella.
- [] El modelo no tiene una geometría rota obvia (sin triángulos flotantes aleatorios)
- [] Puede ver su modelo en la ventana gráfica 3D como una forma gris sólida

---

### Paso 1 — Abrir el Constructor de Rig

Abra la pestaña **Rig Builder** en el estante de herramientas izquierdo (presione**T** en la ventana gráfica 3D). El mismo Rig Builder está en la pestaña**Properties** del editor**Scene** mientras Preferencias → Pestañas → Propiedades de escena → Mostrar está activado. Consta de tres partes:**Auto-Rig Wizard**, Quick Rig (armaduras listas para usar) y**Mannequin**.

Expanda **Auto-Rig Wizard** y haga clic en**Start Auto-Rig**.

También puede iniciar el asistente desde el menú Agregar → Armadura → Asistente de montaje automático de la ventana gráfica 3D y luego continuar en Rig Builder.

---

### Paso 2 — Seleccionar tu malla

El asistente enumera las mallas de la escena. Haz clic en la malla de tu avatar en esa lista, luego haz clic en **Next**.

**Lo que deberías ver:** Una línea "Seleccionado:" con el nombre de tu malla, luego el paso del tipo de rig.

---

### Paso 3 — Elegir el tipo de rig

Haga clic en **Body + Face** para un avatar cuyo rostro desee animar (parpadeos, expresiones, sincronización de labios) o en**Body Only** para un cuerpo sin controles faciales. En Opciones de generación,**Kinematics** establece IK/FK, IK únicamente o FK únicamente. Haga clic en**Next**.

---

### Paso 4 — Colocar los marcadores del cuerpo

Este es el paso más importante. Los marcadores son puntos que muestran BoneCraft dónde se encuentra cada articulación principal: la pelvis, la columna, el cuello y la cabeza, los hombros, los brazos, las manos, las piernas y los pies. BoneCraft les saca los huesos.

**La forma rápida:** en el cuadro Detección inteligente, haga clic en**Detect Markers**. BoneCraft traza las extremidades en tu malla y coloca cada marcador, cada uno con confianza. Haga clic en**Accept High** para conservar los seguros y en**Reset Low** para borrar los dudosos y poder colocarlos usted mismo.**Guess Markers from Mesh** es una suposición más simple a partir de las proporciones de la malla.

**Con la herramienta de ventana gráfica:** para colocar varios marcadores, active Colocar marcadores de rig en la barra de herramientas de la ventana gráfica en Modo Objeto. El encabezado de la herramienta nombra el siguiente marcador y tiene bloqueos de eje y un interruptor de espejo. Haga clic en la malla para colocar y confirmar ese marcador; la herramienta pasa al siguiente marcador no confirmado. Cuando finalice el paso, haga clic en**Next** en el asistente.

**Un marcador a la vez:** cada marcador tiene una fila de botones con iconos. Pase el cursor sobre un botón para leer su información sobre herramientas.

1. Haz clic en **Place Marker** (el ícono de flecha) en la fila del marcador, luego haz clic en el lugar correcto de tu avatar.
2. Haga clic en **Confirm Marker** (la marca de verificación) cuando esté correctamente colocado.**Reset Marker** (la flecha circular) borra un marcador colocado para que puedas volver a colocarlo.

**Simetría:** **Toggle Symmetry** (el primer ícono en la fila de un marcador izquierdo o derecho) coloca el marcador del otro lado cada vez que colocas este.**Mirror L to R** y**Mirror R to L** copian cada marcador confirmado al otro lado.

Cuando se coloquen todos los marcadores, haga clic en **Confirm All Placed** y luego en**Next**.

---

### Paso 5 — Colocar los marcadores de los dedos

En Detalle de los dedos, elija cuántos dedos desea construir: "5 - Mano humana completa" para una mano estándar, o menos (hasta "0 - Sin dedos"). Haga clic en **Guess Finger Markers**. BoneCraft encuentra cada dedo a partir de la forma de la mano y lo traza desde el nudillo hasta la punta del dedo. Ajuste cualquier marcador que esté desactivado y luego haga clic en**Next**.

---

### Paso 6 — Colocar los marcadores de la cara (solo Body + Face)

Haga clic en **Guess Face Markers** y luego ajuste los ojos, los párpados, las cejas, las comisuras de la boca y la mandíbula según sea necesario. Los marcadores de ojos permanecen donde los pones. Haga clic en**Next**.

---

### Paso 7 — Revisar y generar

El paso de revisión enumera las advertencias y las opciones de generación. Haga clic en **Generate Rig**.

**Lo que deberías ver:** Un esqueleto (huesos anaranjados) dentro de tu avatar, con IK/FK extremidades, huesos de los dedos y, para una rig Body + Face, una rig facial y la piel de tu avatar adherida a él para que se deforme cuando los huesos se mueven. El último paso ofrece**Build Control Rig** para las opciones de revisión Generate Rig no se aplica y**Close Wizard**; [Constructor de plataformas](06-rig-builder.md) describe ambos.

> **Pesos de piel** = números que deciden qué huesos mueven qué partes de la malla de tu avatar. BoneCraft los configura automáticamente; puede refinarlos con las herramientas de peso (consulte [Herramientas de plataforma](05-rig-tools.md) ).

---

### Paso 8 — Mapear a los huesos humanoides de VRChat

Abra la pestaña **CATS** en la barra lateral derecha (presione**N**), expanda**Avatar Tools** y luego**Set Up Humanoid Bones**. Haz clic en**Auto-Map All**: BoneCraft conecta tus huesos a las ranuras del cuerpo que VRChat usa para mover un avatar contigo. Haga clic en**Normalize Names** para darle a los huesos mapeados los nombres que espera VRChat y luego en**Validate**.

**Lo que deberías ver:** Cada una de las ranuras requeridas (Caderas, Columna, Cabeza, Brazo superior izquierdo, etc.) muestra un hueso. La Guía 5 explica las tragamonedas.

---

### Paso 9 — Exportar para VRChat

En la pestaña **CATS**, expanda**Avatar Tools** →**Export to VRChat**. Configure el nombre**Folder** y**Avatar**, luego haga clic en**Export to VRChat (Unity)**.

**Lo que deberías ver:** El avatar exportado en la carpeta elegida, listo para VRChat Creator Companion y el SDK VRChat en Unity.

---

**Qué desbloquea:** Ahora tienes un avatar VRChat manipulado. Desde aquí puedes agregar la física del cabello (Guía 6), colocar ropa (Guía 7), configurar la sincronización de labios (Guía 8) y verificar el rendimiento (Guía 9). Para una limpieza integral y una configuración de VRChat con las herramientas CATS, consulte [Guía 13](03-guides-b.md#guía-13-prepara-tu-avatar-para-vrchat-con-cats).

---

## Guía 2: lleva un avatar de VRoid a VRChat

> **Tiempo:** Entre 15 y 25 minutos
> **Resultado:** Su avatar VRoid está listo para exportar VRChat

**Antes de comenzar, comprueba esto:**
- [] Exportaste tu avatar de VRoid Studio como un archivo `.vrm` o lo descargaste de VRoid Hub como `.zip`.
- [] BoneCraft está instalado y habilitado

---

### Paso 1 — Instalar el complemento VRM

BoneCraft utiliza el complemento VRM para leer archivos `.vrm`. En la pestaña **CATS**, expanda**Import / Export** →**VRM / VRoid**. Si dice que el complemento no está instalado, haga clic en**Auto-Install Latest from GitHub**. Sin conexión a Internet, descargue el complemento usted mismo y use**Install from.zip on Disk…**;**Open Extensions Page** abre su página de descarga.

---

### Paso 2 — Importar tu avatar

En la misma sección **VRM / VRoid**, haga clic en**Import VRM…** y elija su archivo `.vrm`. Para descargar VRoid, haga clic en**Import VRoid (.vroid /.zip)…** y elija `.zip`.

Si elige un archivo de proyecto de VRoid Studio (`.vroid` ), BoneCraft muestra una tarjeta "Proyecto de Studio VRoid ": un proyecto aún no es un avatar. Exportarlo a VRM en VRoid Studio, luego importe ese archivo.

**Lo que deberías ver:** Tu personaje VRoid en la ventana gráfica con su esqueleto en su lugar.

---

### Paso 3 — Mapear a los huesos humanoides de VRChat

En la pestaña **CATS** →**Avatar Tools** →**Set Up Humanoid Bones**, haga clic en**Auto-Map All**. Los esqueletos VRoid siguen un diseño estándar, por lo que normalmente llena todos los espacios. Si una ranura está mal,**Fix Humanoid Map** en la sección**VRM / VRoid** (bajo Lint) repara las confusiones habituales de nombres VRoid.

---

### Paso 4 — Corregir los nombres de los huesos

Haga clic en **Normalize Names** en**Set Up Humanoid Bones**. VRoid tiene sus propios nombres de huesos; esto le da a los huesos mapeados los nombres que espera VRChat.

---

### Paso 5 — Configurar los visemas (sincronización labial)

Los avatares VRoid ya tienen formas de boca para sincronización de labios. En la sección **VRM / VRoid**, haga clic en**Map VRoid Visemes**. BoneCraft hace coincidir las claves de forma de VRoid con las formas de sincronización de labios de VRChat.

---

### Paso 6 — Física del cabello (opcional)

El cabello VRoid utiliza SpringBones. **Convert SpringBones → PhysBones** en la sección**VRM / VRoid** los convierte en VRChat PhysBones. La Guía 6 cubre la física del cabello con más detalle.

---

### Paso 7 — Exportar

Exporte como en la Guía 1, Paso 9.

**Qué desbloquea:** Tu avatar VRoid está listo para el Creator Companion VRChat. También puede verificar el rendimiento (Guía 9) antes de cargar.

---

## Guía 3: lleva un avatar de MMD a VRChat

> **Tiempo:** Entre 20 y 30 minutos
> **Resultado:** Su modelo MMD `.pmx` está listo para VRChat

**Antes de comenzar, comprueba esto:**
- [] Tienes un archivo de modelo `.pmx` o `.pmd` MMD
- [] BoneCraft está instalado

---

### Paso 1 — Instalar mmd_tools

BoneCraft utiliza el complemento mmd_tools para leer archivos MMD. En la pestaña **CATS**, expanda**Import / Export** →**MMD / PMX**. Si dice que mmd_tools no está instalado, haga clic en**Auto-Install Latest from GitHub** (o**Install from.zip on Disk...** con una copia descargada).

---

### Paso 2 — Importar tu archivo PMX

En la sección **MMD / PMX**, haga clic en**Import PMX / PMD...** y elija su modelo.

**Lo que deberías ver:** Tu personaje MMD en la ventana gráfica con nombres de huesos japoneses.

---

### Paso 3 — Corregir los nombres de los huesos

VRChat no puede leer los nombres de huesos japoneses de MMD. En la sección **MMD / PMX**, haga clic en**Convert Bone Names -> Unity**. Para nombres en otro idioma, use la pestaña**CATS** →**CATS** →**Translate Bone Names**: elija**Language** y ejecútelo.

---

### Paso 4 — Limpiar el modelo

Los modelos MMD suelen tener geometría adicional y muchas piezas separadas. En la pestaña **CATS** →**CATS**, ejecute primero**Fix Model** y luego**Join Meshes** para combinar las partes del cuerpo en una malla (recomendado para VRChat ). [Guía 13](03-guides-b.md#guía-13-prepara-tu-avatar-para-vrchat-con-cats) recorre todo el proceso CATS en orden.

---

### Paso 5 — Mapear a los huesos humanoides de VRChat

En la pestaña **CATS** →**Avatar Tools** →**Set Up Humanoid Bones**, haga clic en**Auto-Map All**. Los esqueletos de MMD están cerca de los de VRChat, por lo que la mayoría de los espacios se llenan automáticamente. Para una ranura vacía, haga clic en su botón y elija el hueso.

---

### Paso 6 — Física y exportación

**Convert Physics -> PhysBones** en la sección**MMD / PMX** convierte la física del cabello y la falda del cuerpo rígido de MMD en VRChat PhysBones. Luego exporte como en la Guía 1, Paso 9.

**Qué desbloquea:** Tu avatar MMD está listo para VRChat. Puedes agregar física del cabello (Guía 6) y configurar la sincronización de labios (Guía 8) antes de cargarlo.

---

## Guía 4: corrige los nombres de los huesos de tu avatar

> **Tiempo:** Entre 5 y 15 minutos
> **Resultado:** Es necesario cambiar el nombre de los huesos VRChat a nombres compatibles con VRChat

**Antes de comenzar, comprueba esto:**
- [] Tu avatar está abierto con su esqueleto (armadura) visible.

---

### Paso 1 — Detectar el estilo de nombres actual

En la pestaña **CATS**, expanda**VRChat Tools**, busque su grupo de nombres y haga clic en**Detect**. BoneCraft muestra el estilo de nomenclatura que encontró (por ejemplo Mixamo, VRoid o Unity ) y una puntuación;**Force Rescan** vuelve a comprobar después de cambiar los nombres.

Para nombres de huesos en japonés, chino, coreano, portugués, español o francés, use la pestaña **CATS** →**CATS** →**Translate Bone Names**: elija**Language** y ejecútelo. Convierte los nombres al inglés en un solo paso.

---

### Paso 2 — Renombrar con los nombres de VRChat

Primero asigne los huesos (Guía 5, Paso 2), luego haga clic en **Normalize Names** en**Set Up Humanoid Bones**: cada hueso mapeado recibe el nombre que espera VRChat.

**Lo que deberías ver:** Nombres de huesos como `Hips`, `Spine`, `Chest` y `LeftUpperArm`.

---

### Paso 3 — Correcciones manuales (si hace falta)

El grupo de nombres en **VRChat Tools** también tiene herramientas por lotes para los huesos que quedan:

- **Find and Replace**: reemplaza un fragmento de texto por otro en cada nombre de hueso
- **Add Prefix** y**Add Suffix**: agregue texto al principio o al final de cada nombre de hueso
- **Remove Prefix** y**Remove Suffix**: quítelo de nuevo
- **Regex Replace**: lo mismo, con una expresión regular

**Qué desbloquea:** Los nombres correctos de los huesos permiten que el mapeo humanoide (Guía 5) funcione automáticamente. Sin ellos, VRChat no puede saber cómo debe moverse tu personaje.

---

## Guía 5: mapea tu avatar al sistema corporal de VRChat

> **Tiempo:** Entre 10 y 15 minutos
> **Resultado:** El esqueleto de tu avatar conectado al sistema de movimiento humanoide de VRChat

**Antes de comenzar, comprueba esto:**
- [] Los huesos de tu avatar tienen nombres sensatos (consulta la Guía 4 si no)
- [] El esqueleto está seleccionado.
- [] Estás en **Object Mode** (verifica el menú desplegable en la parte superior izquierda de la ventana gráfica)

---

### Paso 1 — Abrir Configurar Huesos Humanoides

En la pestaña **CATS**, expanda**Avatar Tools** →**Set Up Humanoid Bones**.

---

### Paso 2 — Mapeo automático

Haga clic en **Auto-Map All**. BoneCraft escanea tu esqueleto y llena los espacios del cuerpo.

> Una ranura humanoide es como un gancho etiquetado que VRChat usa: "Las caderas van aquí, la cabeza va aquí, la mano izquierda va aquí". BoneCraft combina tus huesos con estos ganchos. El mapeo humanoide ahora se lee correctamente cuando vuelves a abrir un archivo.

**Lo que deberías ver:** Los espacios requeridos (15: caderas, columna vertebral, cabeza, ambos brazos, antebrazos, manos, parte superior de las piernas, parte inferior de las piernas y pies) y los opcionales (pecho, parte superior del pecho, cuello y otros), cada uno con un hueso y la proporción de espacios requeridos que están llenos.

---

### Paso 3 — Comprobar el mapeo

Haga clic en **Validate**. BoneCraft comprueba que cada ranura requerida tenga un hueso y que la jerarquía tenga sentido.

---

### Paso 4 — Rellenar a mano las ranuras vacías

Una ranura sin hueso muestra "(haga clic para mapear)". Haz clic en él y elige el hueso correcto. Luego haga clic en **Validate** nuevamente y en**Normalize Names** para que los huesos mapeados obtengan los nombres de VRChat.

---

### Paso 5 — Configurar el seguimiento ocular (opcional)

Si tu avatar tiene huesos de los ojos, usa la pestaña **CATS** →**CATS** →**Eye Tracking**: haz clic en**Auto-Detect** para encontrar los huesos de los ojos (o elige los huesos**Left Eye** y**Right Eye** ), establece los límites y haz clic en**Create Eye Tracking**. [Guía 13, Fase 3](03-guides-b.md#fase-3--seguimiento-ocular) explica la configuración.

**Qué desbloquea:** Una vez realizado el mapeo humanoide, tu avatar se mueve correctamente en VRChat: IK (cinemática inversa, el sistema que hace que tus manos en el juego sigan a tus controladores reales) funciona y tu avatar sigue tus movimientos en el mundo real.

---

## Guía 6: añade física de cabello

> **Tiempo:** Entre 15 y 25 minutos
> **Resultado:** El cabello de tu avatar (y otras partes suaves) se balancea naturalmente en VRChat

**Antes de comenzar, comprueba esto:**
- [] Tu avatar está abierto con el esqueleto seleccionado.
- [] La configuración de huesos humanoides está lista (Guía 5)

> PhysBone = Componente de VRChat que hace que los huesos reboten y se balanceen como si tuvieran peso. BoneCraft los monta sobre cadenas de huesos: pelo, orejas, colas, faldas y complementos.

---

### Paso 1 — Abrir Añadir Física de Cabello

En la pestaña **CATS**, expanda**Avatar Tools** →**Add Hair Physics**. Consta de cuatro partes: Detección de cadena capilar, Generación de cadena capilar, Configuración PhysBone y Colisionadores de física capilar.

---

### Paso 2 — Encontrar las cadenas de cabello

Si tu cabello ya tiene huesos, haz clic en **Detect Hair Physics Chains**. BoneCraft encuentra las cadenas de huesos que parecen cabellos (huesos unidos de extremo a extremo desde una raíz) y enumera cada uno con su hueso de raíz y su longitud.

Si tu cabello aún no tiene huesos, selecciona las mallas capilares y usa Hair Chain Generation: elige **Density** (Bajo, Medio o Alto: cuántas cadenas), luego haz clic en**Generate**.**Replace** los vuelve a construir con una nueva densidad.

---

### Paso 3 — Elegir un preajuste de PhysBone

Selecciona un hueso de una cadena. En Configuración de PhysBone, haga clic en el ajuste preestablecido que se ajuste: **Hair**,**Skirt** (faldas y capas) o**Tail** (colas y cuerdas).

**Lo que deberías ver:** Los parámetros de la cadena: tracción, resorte, rigidez, gravedad y ángulo máximo.

---

### Paso 4 — Ajuste fino (opcional)

El panel muestra los valores de la cadena; no los edita. Más rigidez hace que la cadena se doble menos, más gravedad la tira hacia abajo y un ángulo máximo más pequeño limita la distancia que oscila. Para valores diferentes, haga clic en otro ajuste preestablecido o cambie el componente PhysBone en Unity después de importar el avatar.

---

### Paso 5 — Añadir colisionadores (recomendado)

Los colisionadores son formas invisibles que impiden que el cabello pase por la cabeza y el cuerpo. En Hair Physics Colliders, haga clic en **Place Default Colliders** para agregar colisionadores estándar en la cabeza, los hombros y el pecho.**Add Collider** y**Remove Collider** agregan o eliminan uno a la vez.

**Qué desbloquea:** El cabello de tu avatar ahora se mueve naturalmente en VRChat cuando giras la cabeza, saltas o bailas. Los mismos pasos funcionan para colas, orejas, faldas y accesorios colgantes.

---

## Guía 7: adjunta ropa que se mueva con tu cuerpo

> **Tiempo:** Entre 20 y 30 minutos
> **Resultado:** Una prenda de vestir adherida al esqueleto de tu avatar, que se mueve con tu cuerpo.

**Antes de comenzar, comprueba esto:**
- [] Tu avatar base tiene un esqueleto terminado y su cuerpo está pintado con peso.
- [] La prenda está en el mismo archivo (con su propia armadura si vino con ella)
- [] La ropa se ajusta aproximadamente al cuerpo de tu avatar.

---

### Paso 1 — Abrir Adjuntar Ropa

En la pestaña **CATS**, expanda**VRChat Tools** y busque su grupo Ropa. Consta de tres partes: combinación de huesos, detección de colisiones y combinación de ropa.

---

### Paso 2 — Emparejar los huesos

Si la ropa viene con su propia armadura, selecciónala y haz clic en **Match Bones**. BoneCraft empareja cada hueso de la ropa con el hueso equivalente de tu avatar (el brazo izquierdo de la ropa con el brazo izquierdo de tu avatar, etc.).

**Lo que deberías ver:** Una lista de pares de huesos: hueso de ropa → hueso de avatar. Para ropa sin armadura, omita este paso.

---

### Paso 3 — Combinar la ropa

Selecciona la ropa (su armadura y mallas, o solo sus mallas si no tiene armadura) y luego presiona Mayús y haz clic en la armadura de tu avatar al final, para que sea el objeto activo. Haga clic en **Merge Clothing**. Con una armadura de ropa, BoneCraft mueve la ropa sobre tu esqueleto y fusiona los huesos; sin uno, transfiere el peso de tu cuerpo a las mallas de la ropa.

> Pesos (pintura de pesos) = números que le dicen a cada punto de una malla cuánto lo mueve cada hueso. Si la manga izquierda tiene peso sobre el hueso del brazo izquierdo, mover ese hueso arrastra la manga con él.

**Lo que deberías ver:** La ropa debajo del esqueleto de tu avatar. Mover un hueso mueve tanto el cuerpo como la ropa.

---

### Paso 4 — Comprobar los atravesamientos

Haga clic en **Detect Collisions** para buscar lugares donde la ropa atraviesa el cuerpo. Arréglelos ajustando los pesos allí (consulte las Herramientas de peso en [Herramientas de plataforma](05-rig-tools.md) ).

**Qué desbloquea:** Ropa que se mueve naturalmente con tu cuerpo. Repita para cada pieza del atuendo.

Siguiente: [Guías 8 a 13](03-guides-b.md)
