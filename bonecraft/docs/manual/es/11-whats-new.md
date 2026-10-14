# Novedades

[← Índice](index.md)

Lo más reciente primero.

## 9.2.2 — Interfaz actual

Las pestañas seleccionan grupos de herramientas. Setup Rigging, Skin, Review, Avatar Tools y Facial son secciones desplegables dentro de las pestañas, no pestañas distintas. Las rutas siguientes usan las etiquetas inglesas; su traducción depende de Language.

- Bone Merge → BoneCraft → Setup Rigging
- Delta Mush / Proximity Wrap → BoneCraft → Skin
- Viseme Library / Lip Sync → CATS → Avatar Tools
- VRChat Viseme Mapping / Face Tracking → CATS → VRChat Tools → Facial

## 9.1.2 (octubre de 2026)

- **Interruptor Propiedades de escena:** Preferencias > Pestañas tiene una nueva fila Propiedades de escena. Su botón Mostrar (azul mientras está activo) muestra u oculta todas las secciones de BoneCraft en Propiedades > pestaña Escena (Constructor de Rig, Mecanismos, CATS, VRChat, Importar / Exportar) sin desactivar el complemento. Empieza activado y no cambia las pestañas de la vista 3D ni la pestaña Armadura.

## 9.1.1 (octubre de 2026)

- **Iconos más claros:** cada icono significa ahora una sola cosa en todas partes. Unos 60 botones tienen un icono de Bforartists más adecuado (por ejemplo Aplicar todas las transformaciones, Diezmar, Normalizar nombres, Traducir, Fusionar, Separar, Mezclar pose y Sincronía labial), y un botón muestra el mismo icono en todos los paneles.
- **Paneles más tranquilos:** los títulos y los textos fijos ya no llevan iconos de tema. Los avisos que informan de un estado muestran el icono de información, de advertencia o de confirmación.
- **Cuadrícula de iconos legible:** cada botón de las pestañas Pose y Pesos de la barra de herramientas tiene su propio icono, así que una barra estrecha sigue siendo legible.

## 9.1.0 (octubre de 2026)

- **Herramientas donde Bforartists pone las suyas:** entradas de BoneCraft en los menús Añadir → Armadura, Pose, Pesos y Objeto, y un panel de botones de BoneCraft en las pestañas Pose y Pesos de la barra de herramientas de Bforartists.
- **Primero actuar, luego ajustar:** Rig rápido, Ajustar rig soltado, las herramientas de pesos, Cinta, Spline IK, Delta Mush y las herramientas de huesos de CATS se ejecutan al momento con los últimos valores usados; se ajustan después en el panel Ajustar última operación. Menos ventanas de «¿estás seguro?».
- **Primero las acciones, opciones plegadas:** los paneles muestran primero sus botones y sus ajustes en un pliegue debajo. Los ajustes parecen ajustes (casillas, nunca botones) y las cabeceras de panel no llevan iconos.
- **Herramientas de gesto:** Colocar marcadores de rig (haz clic en la malla para colocar el siguiente marcador del Asistente de Auto-Rig) y Construir mecanismo (haz clic en una pieza para empezar una articulación o un enlace) están en la barra de herramientas del visor.
- **Descripciones emergentes:** cada operador y cada opción se explica.
- **Mostrar, no ocultar:** las secciones siguen visibles y dicen qué seleccionar cuando no hay rig, el Asistente de Auto-Rig va primero en Rig Builder y los paneles laterales empiezan con un ancho legible.
- **Correcciones:** Generar Spline IK vuelve a funcionar; Añadir influencia usa el hueso elegido; las vistas previas de visemas usan su conjunto.

## 9.0.0 (octubre de 2026)

- **Mechanisms:** una nueva sección de la pestaña BoneCraft (y de la pestaña Escena de Propiedades) que hace el rig de accesorios y máquinas: Hinge, Slide, Telescope, Piston, Gear Link, Follow y Sequence, construidos con pasos guiados y comprobados con Test. BoneCraft nunca sobrescribe un cambio hecho a mano: eliges **Keep mine** para conservarlo o **Restaurar** para reconstruir. Consulta [Mechanisms (mecanismos)](07-mechanisms.md).
- **Lados de las pestañas:** cada pestaña de la vista puede ir en la Tool Shelf izquierda o en la barra lateral derecha (Preferencias → Tabs → Left / Right). BoneCraft y Rig Builder empiezan a la izquierda, CATS a la derecha.
- **Constructor de Rig:** siempre en la pestaña Escena de Propiedades, además de su propia pestaña en la vista con una distribución compacta para una Tool Shelf estrecha. Un rig Basic Humanoid viene en la biblioteca de assets BoneCraft Rigs; Fit Dropped Rig ajusta un rig soltado desde la estantería de assets.
- **Pestaña CATS:** Importar / Exportar se ha movido a la pestaña CATS. CATS, VRChat e Importar / Exportar también están siempre en la pestaña Escena.
- **Show Helpers:** una sola preferencia muestra u oculta el texto didáctico de BoneCraft; el Modo Compacto es su atajo.
- **Validador de Rig:** los nombres de huesos con guiones pasan; los drivers solo avisan en expresiones que necesitan Python; también se comprueban los rigs de Mechanisms. La tarea del validador en el Tablero de Tareas vuelve a informar.
- **Nombre:** el complemento se llama BoneCraft.

## 8.9.x (septiembre–octubre de 2026)

- **8.9.6:** toda la pieza del vestido sigue a los huesos de falda (sin que las caderas la atraviesen); correctivos de las comisuras con la mandíbula abierta, con labios pegajosos.
- **8.9.5:** cambio IK/FK del codo sin saltos; detección simétrica de los hombros; los marcadores de los ojos ya no se ajustan solos; el Control Picker muestra la selección; comisuras más redondas; una corrección del vestido sobre el muslo; clavículas de redireccionamiento más flexibles; exportación en pose en T.
- **8.9.4:** rodillas más redondas (los correctivos sustituyen a Preserve Volume); claves de contacto para flexiones profundas; una mezcla en la unión del hombro.
- **8.9.3:** huesos de falda de dos segmentos que siguen a las piernas y son empujados por ellas.
- **8.9.2:** parpadeo con shape keys (sin pliegues en los párpados); una apertura de boca ovalada.
- **8.9.1:** skinning mucho más rápido en mallas densas (678 000 vértices: de 232 s a 57 s); el calor de huesos pasa por una malla proxy más ligera en lugar de fallar en silencio.
- **8.9.0:** shape keys correctivos de articulación; controles faciales (mirada, parpadeo, seguimiento de labios); ropa que se dobla con las articulaciones.
- También en la 8.9: recálculo automático de pesos de huesos y una selección del atlas más clara.

## 8.7–8.8 (septiembre de 2026)

- **8.8.0:** el panel de redireccionamiento funciona en anfitriones Blender 5; marcadores de dedos colocados a partir de la forma de la mano; estiramiento IK hasta la piel; una opción Preserve Volume; una corrección del vínculo de Delta Mush.
- **8.7.0:** un rig de control integrado; detección de articulaciones recorriendo las extremidades; redireccionamiento con direcciones emparejadas; huesos de torsión.

## 8.5–8.6 (julio de 2026)

- **8.6.1–8.6.3:** Atlas de Materiales: diagnóstico de teselas tras el horneado; la transparencia MToon se compara con el alfa real de la textura y se conserva al crear el atlas; mejor partición de materiales mixtos.
- **8.5.5–8.5.10:** materiales VRM / MToon: se respeta el modo alfa, el alfa funciona en anfitriones Blender 5, la emisión no se satura, diagnóstico en magenta y nombres de atlas seguros.
- **8.5.4:** el mapeo humanoide se vuelve a leer correctamente; guía de Naming Prep.
- **8.5.2–8.5.3:** importación de una descarga de VRoid (.zip); una tarjeta de traspaso para proyectos de VRoid.
- **8.5.1:** exportación FBX que conserva los blend shapes.

## Versiones anteriores

**8.5.0:** Smart Combine ahora convierte `atlas_uv` en el UV0 de exportación por defecto tras el horneado. El mapa UV de origen anterior al atlas se quita de la malla de atlas generada, salvo que actives **Keep Source UV Maps** (conservar mapas UV de origen) en los ajustes avanzados. Los controles de CATS / Material Combiner / derivados de UVToolkit ahora se comparten con la versión abierta de Blender; la exclusividad de B4Artists se mantiene en los sistemas de rigging de producción, control, redireccionamiento/exportación y publicación exclusivos de B4Artists.

La 8.5.0 también actualiza el flujo de exportación y validación. Las exportaciones de VRChat, VRM, MMD y Unreal ahora muestran controles de carpeta y nombre de archivo en los paneles de BoneCraft, en lugar de obligarte a depender solo de los valores predeterminados del explorador de archivos de Blender. Las exportaciones FBX de VRChat/Unity y Unreal usan **Embed Textures** por defecto para facilitar la importación de materiales, mientras que la exportación de VRChat deja fuera del FBX las mallas auxiliares y de formas de control salvo que **Helper Meshes** esté activado. El panel VRM ahora incluye **Verificar Ahora** y **Fix Humanoid Map**, que puede reparar antes de exportar un mapeo de alias humanoide obsoleto sin renombrar tus huesos.

**8.4.5:** Smart Combine ahora obliga a las texturas de origen a muestrear durante el horneado el UV anterior al atlas que se conservó, valida la malla de atlas generada antes de ocultar los originales y reasigna todas las caras del atlas a la ranura de material final del atlas, para evitar trozos de túnica o ropa grises o revueltos.

**8.4.4:** el Combinador de atlas de materiales añade controles de inspección de calidad antes del horneado: diagnóstico de shaders/materiales, etiquetas de función de las texturas, marcadores de orígenes duplicados/compartidos, tamaños forzados por material, preajustes de empaquetado, horneados opcionales de salidas Normal/Emission/Roughness y bloqueos previos del empaquetado de canales Metallic/ORM hasta que esa vía esté verificada.

**8.4.3:** el Combinador de atlas de materiales incluye métodos de empaquetado UV seleccionables dentro del flujo existente de Atlas de Materiales. Incluye Smart Pack, Grid Pack, Seeded Variation, Oriented Pack, Fit 0-1 Bounds, Advanced Variation y Rotation Step, y los detalles del método UV se registran en el informe de depuración y en el registro de horneado.

**8.4.2:** el Combinador de atlas de materiales ahora apunta al UV del atlas generado durante el horneado, mientras que los nodos de textura de origen copiados leen explícitamente el UV anterior al atlas. Esto corrige los resultados de atlas rotos de túnicas/ropa, causados por texturas de origen y un atlas horneado que muestreaban mapas UV distintos. Las filas de materiales y texturas seleccionables de la 8.4.1 siguen disponibles.

**7.1.3 (limpieza de etiquetas de preferencias):** se renombraron dos interruptores de las preferencias del complemento para que coincidan con la pestaña de la barra lateral que controlan. «VRChat Avatar Tools» ahora se llama **CATS** (como la pestaña CATS). «Task Board & Sidebar» ahora se llama **Rig Builder** (como la pestaña Rig Builder). No se quitó ninguna herramienta: solo cambiaron las etiquetas de activar/desactivar en Editar > Preferencias > Complementos > BoneCraft.

**7.1.1:** BoneCraft incluye ahora las herramientas de CATS: un conjunto completo de herramientas de preparación de modelos pensado para dejar los avatares de VRChat limpios, optimizados y totalmente configurados. CATS tiene su propia pestaña en la barra lateral y usa un sistema de pipeline que te guía cada vez por el orden correcto de las operaciones.
