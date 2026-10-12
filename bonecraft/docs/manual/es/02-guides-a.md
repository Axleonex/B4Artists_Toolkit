# Guías 1–7

[← Índice](index.md)

## Guía 1: lleva tu primer avatar a VRChat

> **Tiempo:** unos 45–60 minutos para una primera pasada completa
> **Resultado:** un avatar con rig, listo para VRChat, exportado para el SDK de VRChat

**Antes de empezar, comprueba esto:**
- [ ] Tu modelo 3D está importado en Bforartists (Archivo > Importar, elige tu formato)
- [ ] El modelo está en pose en T (brazos estirados a los lados, cuerpo erguido), o casi
- [ ] El modelo no tiene geometría claramente rota (ni triángulos sueltos flotando)
- [ ] Ves tu modelo en la vista 3D como una forma gris sólida

---

### Paso 1 — Abrir el Constructor de Rig

Abre la pestaña **Rig Builder** en la Tool Shelf izquierda (pulsa **T** en la vista 3D). El mismo Constructor de Rig está siempre también en la pestaña **Escena** del editor de **Propiedades**. Tiene tres partes: Quick Rig (armaduras ya hechas), el **Asistente Auto-Rig** y **Maniquí**.

Despliega **Asistente Auto-Rig** y haz clic en **Iniciar Auto-Rig**.

---

### Paso 2 — Seleccionar tu malla

El asistente enumera las mallas de la escena. Haz clic en la malla de tu avatar en esa lista y luego en **Siguiente**.

**Lo que deberías ver:** una línea «Selected:» con el nombre de tu malla y, después, el paso del tipo de rig.

---

### Paso 3 — Elegir el tipo de rig

Haz clic en **Body + Face** (cuerpo y cara) para un avatar cuya cara quieras animar (parpadeos, expresiones, sincronización labial), o en **Body Only** (solo cuerpo) para un cuerpo sin controles faciales. En las opciones de generación, **Cinemática** elige IK/FK, solo IK o solo FK. Haz clic en **Siguiente**.

---

### Paso 4 — Colocar los marcadores del cuerpo

Este es el paso más importante. Los marcadores son puntos que muestran a BoneCraft dónde está cada articulación principal: la pelvis, la columna, el cuello y la cabeza, los hombros, los brazos, las manos, las piernas y los pies. BoneCraft calcula los huesos a partir de ellos.

**La forma rápida:** en el recuadro Smart Detection (detección inteligente), haz clic en **Detect Markers** (detectar marcadores). BoneCraft recorre las extremidades de tu malla y coloca cada marcador, cada uno con un grado de confianza. Haz clic en **Accept High** (aceptar confianza alta) para quedarte con los seguros y en **Reset Low** (restablecer confianza baja) para borrar los dudosos y colocarlos tú. **Adivinar marcadores desde la malla** es una estimación más sencilla a partir de las proporciones de la malla.

**A mano:** cada marcador tiene una fila de botones con icono.
1. Haz clic en **Place Marker** (colocar marcador; el icono de flecha) en la fila del marcador y luego en el punto correcto de tu avatar.
2. Haz clic en **Confirm Marker** (confirmar marcador; la marca de verificación) cuando esté bien colocado. **Reset Marker** (restablecer marcador; la flecha circular) borra un marcador colocado para que puedas colocarlo de nuevo.

**Simetría:** **Toggle Symmetry** (alternar simetría; el primer icono en la fila de un marcador izquierdo o derecho) coloca el marcador del otro lado cada vez que colocas este. **Mirror L to R** (reflejar de izquierda a derecha) y **Mirror R to L** (reflejar de derecha a izquierda) copian cada marcador confirmado al otro lado.

Cuando todos los marcadores estén colocados, haz clic en **Confirmar todos colocados** y luego en **Siguiente**.

---

### Paso 5 — Colocar los marcadores de los dedos

En Detalle de Dedos, elige cuántos dedos construir: «5 — Full Human Hand» para una mano normal, o menos (hasta «0 — No Fingers»). Haz clic en **Adivinar marcadores de dedos**. BoneCraft encuentra cada dedo a partir de la forma de la mano y lo sigue desde el nudillo hasta la punta. Ajusta los marcadores desviados y haz clic en **Siguiente**.

---

### Paso 6 — Colocar los marcadores de la cara (solo Body + Face)

Haz clic en **Adivinar marcadores faciales** y ajusta según haga falta los ojos, los párpados, las cejas, las comisuras de la boca y la mandíbula. Los marcadores de los ojos se quedan donde los pones. Haz clic en **Siguiente**.

---

### Paso 7 — Revisar y generar

El paso de revisión enumera los avisos y las opciones de generación. Haz clic en **Generar rig**.

**Lo que deberías ver:** un esqueleto (huesos naranjas) dentro de tu avatar, con extremidades IK/FK, huesos de los dedos y, en un rig Body + Face, un rig facial, y la piel de tu avatar unida a él para que se deforme cuando se mueven los huesos. El último paso ofrece **Construir rig de control** para las opciones de la revisión que Generar rig no aplica, y **Cerrar asistente**; [Constructor de Rig](06-rig-builder.md) describe ambos.

> **Pesos de piel** = números que deciden qué huesos mueven qué partes de la malla de tu avatar. BoneCraft los fija automáticamente; puedes afinarlos con las herramientas de pesos (consulta [Herramientas de rig](05-rig-tools.md)).

---

### Paso 8 — Mapear a los huesos humanoides de VRChat

Abre la pestaña **CATS** en la barra lateral derecha (pulsa **N**), despliega **VRChat** y luego **Configurar Huesos Humanoides**. Haz clic en **Mapear Todo Automáticamente**: BoneCraft conecta tus huesos con las ranuras del cuerpo que VRChat usa para mover un avatar contigo. Haz clic en **Normalize Names** (normalizar nombres) para dar a los huesos mapeados los nombres que espera VRChat y luego en **Validar**.

**Lo que deberías ver:** las ranuras obligatorias (Hips, Spine, Head, LeftUpperArm, etc.) muestran cada una un hueso. La guía 5 explica las ranuras.

---

### Paso 9 — Exportar para VRChat

En la pestaña **CATS**, despliega **VRChat** → **Exportar a VRChat**. Indica la **Folder** (carpeta) y el nombre del **Avatar**, y haz clic en **Exportar a VRChat (Unity)**.

**Lo que deberías ver:** el avatar exportado en la carpeta elegida, listo para el VRChat Creator Companion y el SDK de VRChat en Unity.

---

**Lo que esto desbloquea:** ya tienes un avatar de VRChat con rig. A partir de aquí puedes añadir física de cabello (guía 6), adjuntar ropa (guía 7), configurar la sincronización labial (guía 8) y comprobar el rendimiento (guía 9). Para una limpieza y configuración de VRChat todo en uno con las herramientas de CATS, consulta la [guía 13](03-guides-b.md#guía-13-prepara-tu-avatar-para-vrchat-con-cats).

---

## Guía 2: lleva un avatar de VRoid a VRChat

> **Tiempo:** unos 15–25 minutos
> **Resultado:** tu avatar de VRoid listo para exportarlo a VRChat

**Antes de empezar, comprueba esto:**
- [ ] Has exportado tu avatar desde VRoid Studio como archivo `.vrm`, o lo has descargado de VRoid Hub como `.zip`
- [ ] BoneCraft está instalado y activado

---

### Paso 1 — Instalar el complemento VRM

BoneCraft usa el complemento VRM para leer archivos `.vrm`. En la pestaña **CATS**, despliega **Importar / Exportar** → **VRM / VRoid**. Si indica que el complemento no está instalado, haz clic en **Instalar Automáticamente desde GitHub**. Sin conexión a Internet, descarga tú el complemento y usa **Instalar desde .zip en Disco…**; **Abrir Página de Extensiones** abre su página de descarga.

---

### Paso 2 — Importar tu avatar

En la misma sección **VRM / VRoid**, haz clic en **Importar VRM…** y elige tu archivo `.vrm`. Para una descarga de VRoid, haz clic en **Import VRoid (.vroid / .zip)…** (importar VRoid) y elige el `.zip`.

Si eliges un archivo de proyecto de VRoid Studio (`.vroid`), BoneCraft muestra en su lugar una tarjeta «VRoid Studio Project»: un proyecto todavía no es un avatar. Expórtalo a VRM en VRoid Studio e importa ese archivo.

**Lo que deberías ver:** tu personaje de VRoid en la vista, con su esqueleto en su sitio.

---

### Paso 3 — Mapear a los huesos humanoides de VRChat

En la pestaña **CATS** → **VRChat** → **Configurar Huesos Humanoides**, haz clic en **Mapear Todo Automáticamente**. Los esqueletos de VRoid siguen una distribución estándar, así que esto suele rellenar todas las ranuras. Si una ranura está mal, **Fix Humanoid Map** (corregir mapa humanoide) en la sección **VRM / VRoid** (bajo Lint) repara las confusiones de nombres habituales de VRoid.

---

### Paso 4 — Corregir los nombres de los huesos

Haz clic en **Normalize Names** en **Configurar Huesos Humanoides**. VRoid tiene sus propios nombres de huesos; esto da a los huesos mapeados los nombres que espera VRChat.

---

### Paso 5 — Configurar los visemas (sincronización labial)

Los avatares de VRoid ya tienen las formas de boca para la sincronización labial. En la sección **VRM / VRoid**, haz clic en **Mapear Visemas VRoid**. BoneCraft empareja los shape keys de VRoid con las formas de sincronización labial de VRChat.

---

### Paso 6 — Física del cabello (opcional)

El cabello de VRoid usa SpringBones. **Convertir SpringBones → PhysBones** en la sección **VRM / VRoid** los convierte en PhysBones de VRChat. La guía 6 trata la física del cabello con más detalle.

---

### Paso 7 — Exportar

Exporta como en la guía 1, paso 9.

**Lo que esto desbloquea:** tu avatar de VRoid está listo para el VRChat Creator Companion. También puedes comprobar el rendimiento (guía 9) antes de subirlo.

---

## Guía 3: lleva un avatar de MMD a VRChat

> **Tiempo:** unos 20–30 minutos
> **Resultado:** tu modelo `.pmx` de MMD listo para VRChat

**Antes de empezar, comprueba esto:**
- [ ] Tienes un archivo de modelo MMD `.pmx` o `.pmd`
- [ ] BoneCraft está instalado

---

### Paso 1 — Instalar mmd_tools

BoneCraft usa el complemento mmd_tools para leer archivos MMD. En la pestaña **CATS**, despliega **Importar / Exportar** → **MMD / PMX**. Si indica que mmd_tools no está instalado, haz clic en **Instalar Automáticamente desde GitHub** (o en **Install from .zip on Disk...** (instalar desde un .zip en disco) con una copia descargada).

---

### Paso 2 — Importar tu archivo PMX

En la sección **MMD / PMX**, haz clic en **Import PMX / PMD...** (importar PMX / PMD) y elige tu modelo.

**Lo que deberías ver:** tu personaje de MMD en la vista, con nombres de huesos en japonés.

---

### Paso 3 — Corregir los nombres de los huesos

VRChat no puede leer los nombres de huesos japoneses de MMD. En la sección **MMD / PMX**, haz clic en **Convert Bone Names -> Unity** (convertir nombres de huesos para Unity). Para nombres en otro idioma, usa la pestaña **CATS** → **CATS** → **Traducir Nombres de Huesos**: elige el **Idioma** y ejecútalo.

---

### Paso 4 — Limpiar el modelo

Los modelos de MMD suelen tener geometría de más y muchas piezas separadas. En la pestaña **CATS** → **CATS**, ejecuta primero **Corregir Modelo** y luego **Unir Mallas** para combinar las partes del cuerpo en una sola malla (recomendado para VRChat). La [guía 13](03-guides-b.md#guía-13-prepara-tu-avatar-para-vrchat-con-cats) recorre todo el pipeline de CATS en orden.

---

### Paso 5 — Mapear a los huesos humanoides de VRChat

En la pestaña **CATS** → **VRChat** → **Configurar Huesos Humanoides**, haz clic en **Mapear Todo Automáticamente**. Los esqueletos de MMD se parecen a los de VRChat, así que la mayoría de las ranuras se rellenan solas. Para una ranura vacía, haz clic en su botón y elige el hueso.

---

### Paso 6 — Física y exportación

**Convert Physics -> PhysBones** (convertir física a PhysBones) en la sección **MMD / PMX** convierte la física de cuerpos rígidos del cabello y la falda de MMD en PhysBones de VRChat. Luego exporta como en la guía 1, paso 9.

**Lo que esto desbloquea:** tu avatar de MMD está listo para VRChat. Puedes añadir física de cabello (guía 6) y configurar la sincronización labial (guía 8) antes de subirlo.

---

## Guía 4: corrige los nombres de los huesos de tu avatar

> **Tiempo:** unos 5–15 minutos
> **Resultado:** los huesos que necesita VRChat renombrados con nombres compatibles con VRChat

**Antes de empezar, comprueba esto:**
- [ ] Tu avatar está abierto y su esqueleto (armadura) es visible

---

### Paso 1 — Detectar el estilo de nombres actual

En la pestaña **CATS**, despliega **VRChat** → **VRChat Naming Extras** (extras de nombres de VRChat) y haz clic en **Detectar**. BoneCraft muestra el estilo de nombres que ha encontrado (por ejemplo Mixamo, VRoid o Unity) y una puntuación; **Forzar Nuevo Escaneo** vuelve a comprobar después de cambiar nombres.

Para nombres de huesos en japonés, chino, coreano, portugués, español o francés, usa en su lugar la pestaña **CATS** → **CATS** → **Traducir Nombres de Huesos**: elige el **Idioma** y ejecútalo. Convierte los nombres al inglés en un solo paso.

---

### Paso 2 — Renombrar con los nombres de VRChat

Mapea primero los huesos (guía 5, paso 2) y luego haz clic en **Normalize Names** en **Configurar Huesos Humanoides**: cada hueso mapeado recibe el nombre que espera VRChat.

**Lo que deberías ver:** nombres de huesos como `Hips`, `Spine`, `Chest` y `LeftUpperArm`.

---

### Paso 3 — Correcciones manuales (si hace falta)

**VRChat Naming Extras** también tiene herramientas por lotes para los huesos que quedan:

- **Buscar y Reemplazar** — sustituye un fragmento de texto por otro en cada nombre de hueso
- **Añadir Prefijo** y **Añadir Sufijo** — añaden texto al principio o al final de cada nombre de hueso
- **Eliminar Prefijo** y **Eliminar Sufijo** — lo quitan de nuevo
- **Reemplazo por Regex** — lo mismo, con una expresión regular

**Lo que esto desbloquea:** unos nombres de huesos correctos permiten que el mapeo humanoide (guía 5) funcione automáticamente. Sin ellos, VRChat no sabe cómo debe moverse tu personaje.

---

## Guía 5: mapea tu avatar al sistema corporal de VRChat

> **Tiempo:** unos 10–15 minutos
> **Resultado:** el esqueleto de tu avatar conectado al sistema de movimiento humanoide de VRChat

**Antes de empezar, comprueba esto:**
- [ ] Los huesos de tu avatar tienen nombres razonables (si no, consulta la guía 4)
- [ ] El esqueleto está seleccionado
- [ ] Estás en **Modo Objeto** (mira el menú desplegable de arriba a la izquierda de la vista)

---

### Paso 1 — Abrir Configurar Huesos Humanoides

En la pestaña **CATS**, despliega **VRChat** → **Configurar Huesos Humanoides**.

---

### Paso 2 — Mapeo automático

Haz clic en **Mapear Todo Automáticamente**. BoneCraft examina tu esqueleto y rellena las ranuras del cuerpo.

> Una ranura humanoide es como un gancho etiquetado que usa VRChat: «las caderas van aquí, la cabeza va aquí, la mano izquierda va aquí». BoneCraft empareja tus huesos con esos ganchos. Ahora el mapeo humanoide se vuelve a leer correctamente cuando abres de nuevo un archivo.

**Lo que deberías ver:** las ranuras obligatorias (15: Hips, Spine, Head, ambos brazos, antebrazos, manos, muslos, piernas y pies) y las opcionales (Chest, UpperChest, Neck y otras), cada una con un hueso, y la proporción de ranuras obligatorias rellenas.

---

### Paso 3 — Comprobar el mapeo

Haz clic en **Validar**. BoneCraft comprueba que cada ranura obligatoria tiene un hueso y que la jerarquía tiene sentido.

---

### Paso 4 — Rellenar a mano las ranuras vacías

Una ranura sin hueso muestra «(click to map)» (haz clic para mapear). Haz clic en ella y elige el hueso correcto. Después haz clic de nuevo en **Validar**, y en **Normalize Names** para que los huesos mapeados reciban los nombres de VRChat.

---

### Paso 5 — Configurar el seguimiento ocular (opcional)

Si tu avatar tiene huesos de ojos, usa la pestaña **CATS** → **CATS** → **Seguimiento Ocular**: haz clic en **Detección Automática** para encontrar los huesos de los ojos (o elige los huesos **Ojo Izquierdo** y **Ojo Derecho**), ajusta los límites y haz clic en **Crear Seguimiento Ocular**. La [guía 13, fase 3](03-guides-b.md#fase-3--seguimiento-ocular) explica los ajustes.

**Lo que esto desbloquea:** con el mapeo humanoide hecho, tu avatar se mueve bien en VRChat: el IK (cinemática inversa, el sistema que hace que tus manos en el juego sigan a tus mandos reales) funciona, y tu avatar sigue tus movimientos reales.

---

## Guía 6: añade física de cabello

> **Tiempo:** unos 15–25 minutos
> **Resultado:** el cabello de tu avatar (y otras partes blandas) moviéndose con naturalidad en VRChat

**Antes de empezar, comprueba esto:**
- [ ] Tu avatar está abierto con el esqueleto seleccionado
- [ ] Configurar Huesos Humanoides está hecho (guía 5)

> PhysBone = el componente de VRChat que hace que los huesos reboten y se balanceen como si tuvieran peso. BoneCraft los configura en cadenas de huesos: cabello, orejas, colas, faldas y accesorios.

---

### Paso 1 — Abrir Añadir Física de Cabello

En la pestaña **CATS**, despliega **VRChat** → **Añadir Física de Cabello**. Tiene cuatro partes: Hair Chain Detection (detección de cadenas de cabello), Hair Chain Generation (generación de cadenas de cabello), PhysBone Configuration (configuración de PhysBone) y Hair Physics Colliders (colisionadores de física de cabello).

---

### Paso 2 — Encontrar las cadenas de cabello

Si tu cabello ya tiene huesos, haz clic en **Detect Hair Physics Chains** (detectar cadenas de física de cabello). BoneCraft encuentra las cadenas de huesos que parecen cabello (huesos unidos extremo con extremo desde una raíz) y enumera cada una con su hueso raíz y su longitud.

Si tu cabello aún no tiene huesos, selecciona las mallas del cabello y usa Hair Chain Generation: elige la **Densidad** (Low, Medium o High: cuántas cadenas) y haz clic en **Generar**. **Reemplazar** las vuelve a crear con una densidad nueva.

---

### Paso 3 — Elegir un preajuste de PhysBone

Selecciona un hueso de una cadena. En PhysBone Configuration, haz clic en el preajuste adecuado: **Cabello**, **Falda** (faldas y capas) o **Cola** (colas y cuerdas).

**Lo que deberías ver:** los parámetros de la cadena: Pull, Spring, Stiffness, Gravity y Max Angle.

---

### Paso 4 — Ajuste fino (opcional)

El panel muestra los valores de la cadena; no los edita. Más Stiffness la hace doblarse menos, más Gravity la tira hacia abajo, un Max Angle menor limita cuánto se balancea. Para otros valores, haz clic en otro preajuste, o cambia el componente PhysBone en Unity después de importar el avatar.

---

### Paso 5 — Añadir colisionadores (recomendado)

Los colisionadores son formas invisibles que impiden que el cabello atraviese la cabeza y el cuerpo. En Hair Physics Colliders, haz clic en **Place Default Colliders** (colocar colisionadores predeterminados) para añadir colisionadores estándar en la cabeza, los hombros y el pecho. **Add Collider** (añadir colisionador) y **Remove Collider** (quitar colisionador) añaden o quitan uno cada vez.

**Lo que esto desbloquea:** el cabello de tu avatar ahora se mueve con naturalidad en VRChat cuando giras la cabeza, saltas o bailas. Los mismos pasos sirven para colas, orejas, faldas y accesorios colgantes.

---

## Guía 7: adjunta ropa que se mueva con tu cuerpo

> **Tiempo:** unos 20–30 minutos
> **Resultado:** una prenda unida al esqueleto de tu avatar, que se mueve con tu cuerpo

**Antes de empezar, comprueba esto:**
- [ ] Tu avatar base tiene un esqueleto terminado y su cuerpo tiene pesos pintados
- [ ] La prenda está en el mismo archivo (con su propia armadura, si venía con una)
- [ ] La prenda se ajusta más o menos al cuerpo de tu avatar

---

### Paso 1 — Abrir Adjuntar Ropa

En la pestaña **CATS**, despliega **VRChat** → **Adjuntar Ropa**. Tiene tres partes: Bone Matching (emparejamiento de huesos), Collision Detection (detección de colisiones) y Clothing Merge (combinación de ropa).

---

### Paso 2 — Emparejar los huesos

Si la prenda venía con su propia armadura, selecciónala y haz clic en **Hacer coincidir huesos**. BoneCraft empareja cada hueso de la prenda con el hueso equivalente de tu avatar (el brazo izquierdo de la prenda con el brazo izquierdo de tu avatar, y así sucesivamente).

**Lo que deberías ver:** una lista de pares de huesos: hueso de la prenda → hueso del avatar. Para ropa sin armadura, sáltate este paso.

---

### Paso 3 — Combinar la ropa

Selecciona la prenda (su armadura y sus mallas, o solo sus mallas si no tiene armadura) y, por último, haz Mayús+clic en la armadura de tu avatar para que sea el objeto activo. Haz clic en **Combinar Ropa**. Con una armadura de ropa, BoneCraft pasa la prenda a tu esqueleto y fusiona los huesos; sin ella, transfiere los pesos de tu cuerpo a las mallas de la prenda.

> Pesos (pintura de pesos) = números que indican a cada punto de una malla cuánto lo mueve cada hueso. Si tu manga izquierda tiene peso en el hueso del brazo izquierdo, mover ese hueso arrastra la manga con él.

**Lo que deberías ver:** la prenda bajo el esqueleto de tu avatar. Al mover un hueso se mueven a la vez el cuerpo y la prenda.

---

### Paso 4 — Comprobar los atravesamientos

Haz clic en **Detectar colisiones** para encontrar los lugares donde la ropa atraviesa el cuerpo. Corrígelos ajustando ahí los pesos (consulta las herramientas de pesos en [Herramientas de rig](05-rig-tools.md)).

**Lo que esto desbloquea:** ropa que se mueve con naturalidad con tu cuerpo. Repite para cada prenda del conjunto.

Siguiente: [Guías 8–13](03-guides-b.md)
