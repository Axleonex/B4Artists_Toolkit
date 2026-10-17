# Ghost Tool 4.3.1 - Guía de usuario

Traducción automática de la edición inglesa 4.3.1, sin certificación profesional. Los nombres de los controles se conservan en inglés para coincidir con la interfaz. [Fuente inglesa](../../GhostTool_User_Manual.md).

Ghost Tool para Bforartists muestra mallas fantasma, trayectorias y marcadores de movimiento editables. La versión 4.3.1 incorpora a esta guía la barra directa de la vista 3D, cantidades Before/Ahead independientes, ajustes mediante pulsación prolongada, arrastre continuo de marcadores y restauración actualizada de los marcadores de las instantáneas.

Esta guía acompaña al [ZIP de instalación de Ghost Tool 4.3.1](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Actualizar el código del repositorio no actualiza automáticamente el complemento instalado: instale el nuevo ZIP y reinicie Bforartists. Consulte las [notas de versión](../../releases/4.3.1/RELEASE-NOTES.md) y el [registro del paquete](../../releases/4.3.1/package-receipt.json) para comprobar la versión y la suma de verificación.

## Instalar y localizar Ghost Tool

Descargue `b4_ghost_tool_v4.3.1.zip` e instálelo desde Edit > Preferences > Add-ons > Install from Disk. Active Ghost Tool y reinicie Bforartists después de sustituir una versión instalada. Compruebe que Preferences indica 4.3.1. Un ZIP antiguo sigue instalando su versión original.

Por defecto, Ghost Tool usa Top Toolbar en la fila nativa Tool Settings de la vista 3D. Con las cabeceras nativas arriba, esta fila queda justo debajo de la cabecera principal y sigue su alineación. Las preferencias también ofrecen Right Sidebar (N) y Left Tool Shelf (T). La antigua opción guardada Top Header migra a la barra visible; ahora se llama Top Toolbar.

Los controles nativos de herramienta y modo siguen disponibles. Las vistas estrechas o divididas conservan toda la barra Ghost en el mismo orden; arrastre horizontalmente la fila con el botón central del ratón para llegar a los controles fuera de pantalla. Si están ocultos, elija View > Show Ghost Toolbar. Guarde las preferencias normalmente para conservar la presentación.

## Inicio rápido: examinar un objetivo animado

Seleccione un objeto animado o un hueso en modo Pose y active el primer icono de fantasma. Pulse Ghosts para mostrar las vistas previas de malla; ajuste Before y Ahead por separado. Elija Wire o Solid para su apariencia. Mantenga pulsado Ghosts para elegir muestreo por intervalo de fotogramas o por fotogramas clave y ajustar Opacity, Fade o In Front.

Pulse Paths para mostrar una trayectoria. Si no hay un objetivo de trayectoria, la acción puede añadir el objetivo animado seleccionado. Use Add Selected Path para otro objetivo o Follow Selection para seguir la selección actual. Active Markers Display para mostrar puntos editables de una trayectoria conservada en la lista.

Pulse Drag y seleccione y mueva marcadores en la vista 3D. Confirme un movimiento y seleccione otro marcador sin reiniciar Drag. Pulse Drag otra vez o Escape para salir. Antes de editar, mantenga pulsado Drag para elegir cómo afecta la liberación del marcador a la animación.

## Leer la barra superior de izquierda a derecha

**Ghost Tool:** el primer icono activa o desactiva toda la herramienta, independientemente del botón de mallas Ghosts. Desactivarla también desarma los modos de edición de marcadores y manejadores. Mantenga pulsado para Update Meshes While Scrubbing, Update Markers While Scrubbing y Freeze Updates.

**Ghosts:** muestra u oculta mallas fantasma. Los campos Before y Ahead contiguos tienen cada uno botones de menos y más. Wire Ghosts y Solid Ghosts seleccionan el estilo explícitamente. Ocultar las mallas conserva el estilo; elegir un estilo no sustituye al control de visibilidad.

**Paths:** muestra u oculta trayectorias. Sus propios campos Before y Ahead preceden a Add Selected Path y Follow Selection. Los objetivos añadidos permanecen al seleccionar otro objeto o hueso. Follow Selection añade una vista previa de la selección actual. Los objetivos de trayectoria y los marcadores de edición fijados son conceptos distintos.

**Drag:** inicia el modo continuo Drag Markers. **Pin:** inicia la selección de un marcador para fijarlo o liberarlo. **Markers Display:** el rombo inmediatamente a la derecha de Pin muestra u oculta los marcadores editables de trayectoria. Los nombres emergentes identifican las herramientas.

**Arc Style:** un clic abre directamente Solid, Speed Colored y Fade. Controla el arco de movimiento de los fantasmas, no el estilo Wire/Solid de las mallas. Paths tiene un Line Style independiente en su menú de pulsación prolongada. **Spacing Ticks:** alterna indicadores de espaciado; mantenga pulsado para Acceleration Indicators.

**Settings:** abre controles avanzados de generación de marcadores, objetivos, rangos, edición, comparación, física y apariencia. La fila superior ya no repite Generate y Clear como iconos independientes; siguen accesibles en los controles avanzados.

## Ajustar las cantidades Before y Ahead

Ghosts y Paths tienen dos números cada uno. El primero, Before, solicita muestras anteriores al fotograma actual; el segundo, Ahead, posteriores. Son cantidades independientes, no una densidad conjunta. Edite directamente o use menos/más en la barra superior. Cero desactiva las muestras del lado correspondiente.

Las cantidades indican cuántas muestras solicitar; el muestreo determina dónde se sitúan. En el fotograma 20, Ghosts Before 3, Ahead 2 y un intervalo de 2 solicitan muestras anteriores en 18, 16 y 14 y posteriores en 22 y 24, según la animación disponible y los límites del rango. La pose del cabezal de reproducción no cuenta entre esas muestras.

By Keyframe usa las claves de animación del objetivo en lugar de fotogramas espaciados uniformemente; su intervalo puede saltar claves. Editar las cantidades de Paths selecciona la ventana basada en cantidades alrededor del cabezal. Los modos avanzados de rango siguen en Settings con sus propias reglas.

## Mantener pulsada una herramienta para configurarla

Un clic normal ejecuta la acción principal. Mantener pulsado un botón compatible abre sus parámetros. Arc Style es la excepción: un clic abre inmediatamente sus tres opciones. Settings abre el panel avanzado con un clic normal.

**Mantener Ghosts pulsado:** elija muestreo por intervalo de fotogramas o por claves. El primero muestra Every (Frames); 1 significa cada fotograma. El segundo muestra Keyframe Interval, con intervalo personalizado. Opacity, In Front y Fade controlan la apariencia.

**Mantener Paths pulsado:** elija el muestreo y su intervalo de fotogramas o claves. Line Style, Frame Numbers y Bezier Handles controlan la presentación. Active Bezier Handles para examinar o editar los manejadores de las curvas.

**Mantener Markers Display pulsado:** cambie el muestreo compartido con Motion Paths, muestre puntos de fotogramas clave y alterne los números de fotograma de los marcadores. Este menú está en la barra superior. Los marcadores no tienen un tercer modo independiente: cambiarlo aquí también cambia Paths.

**Mantener Drag pulsado:** ajuste When Released, Curve Shape o Smooth Neighbours según el modo, Nearby Frame Reach y Falloff. **Pin:** instrucciones o Unpin All Markers. **Follow Selection:** Highlight Active Path. **Spacing Ticks:** Acceleration Indicators.

## Usar la barra inferior de Timeline

La franja compacta Ghost está en la misma fila que los botones nativos de Timeline. No es una segunda fila personalizada debajo. La actualización documental 4.3.1 no rediseña esta franja.

Su orden es: activación general; visualización de mallas Ghosts; cantidades de mallas anteriores y posteriores; Wire y Solid; Drag Markers; rombo de marcadores editables; visualización Paths; cantidades de trayectoria anteriores y posteriores. Cada pareja sigue el mismo orden antes/después de la barra superior.

Mantenga pulsado Ghosts o Paths en Timeline para Frame by Frame, By Keyframe, intervalos y ajustes visuales. More Ghost Settings abre las opciones completas. El rombo inferior alterna directamente los marcadores; su menú separado de pulsación prolongada está en Markers Display de la barra superior. Las instantáneas se encuentran en Compare, dentro de los ajustes avanzados, no en un botón inferior.

## Arrastrar marcadores repetidamente

Active Ghost Tool y muestre los marcadores editables de un objetivo animado. Drag prepara la selección; el texto de estado pide pulsar un marcador en la vista 3D. Un clic en espacio vacío mantiene la espera: acérquese a un marcador visible. Confirmar un movimiento deja Drag activo para la siguiente edición. Todos los botones que lanzan Drag Markers comparten el modo.

Pulse Drag de nuevo o Escape para detenerlo. Durante un movimiento, Escape cancela ese movimiento y restaura las curvas y posiciones originales. Los movimientos anteriores confirmados son ediciones separadas; use Undo para revertirlos. Desactivar la herramienta, perder un objetivo, cambiar de archivo/historial o cerrar el complemento también termina o cancela las sesiones afectadas.

El arrastre de manejadores de trayectoria también admite espera continua. Muestre Bezier Handles, inicie su arrastre y seleccione sucesivamente manejadores visibles. Shift+G sigue disponible. Alt alterna el comportamiento de manejadores alineados durante el arrastre. Escape cancela el movimiento en curso y sale del modo.

## Elegir ediciones suaves o angulosas

Mantenga pulsado Drag y examine When Released. Reshape Handles modifica los manejadores Bézier existentes para que la curva pase por la muestra desplazada sin añadir una clave. Curve Shape ofrece Free, Locked y Smooth: Free permite ajustes libres, Locked conserva los ángulos y Smooth redistribuye la influencia de los manejadores a lo largo del segmento.

Insert Keyframe escribe una clave real en el fotograma del marcador. Smooth Neighbours puede suavizar los manejadores de las claves adyacentes después de insertarla. Nearby Frame Reach y Falloff controlan la participación de los fotogramas cercanos en el esculpido.

La línea visible también depende de la densidad de muestras. Muestras muy separadas forman una línea tosca aunque la animación sea curva. Reduzca el intervalo para examinar el resultado. Un giro brusco puede venir de la interpolación, los manejadores o el modo de edición; añadir solo muestras visuales no cambia la curva de animación.

## Fijar marcadores y gestionar objetivos de trayectoria

Pulse Pin y luego un marcador visible para alternar su fijación. Pin realiza una selección puntual, no el modo continuo Drag; actívelo otra vez para otro marcador. Puede fijar varios. Permanecen inmóviles durante la remodelación, y la actualización conserva los registros fijados coincidentes. Mantenga pulsado Pin y elija Unpin All Markers para liberarlos todos.

Añadir un objetivo conserva el objeto o hueso en la lista de trayectorias; no congela todas sus muestras de animación. Follow Selection cambia la vista previa de selección mientras permanecen los objetivos añadidos explícitamente. Gestione estos objetivos en la lista de Settings. Markers Display muestra los puntos editables de las trayectorias conservadas; Keyframe Dots es una ayuda visual independiente.

## Actualizaciones en vivo y edición nativa

Live Update Markers y Live Update Skin están desactivados por defecto; las escenas existentes conservan sus valores guardados. Desactivados, recorrer los fotogramas mantiene la última vista previa actualizada. Cambie este comportamiento bajo el icono principal. Freeze Updates también pausa las actualizaciones automáticas.

Durante movimientos, rotaciones, escalados y gestos de gizmo nativos, Ghost mantiene la última vista previa en lugar de recorrer fotogramas de animación. Tras confirmar o cancelar, espera a que se estabilicen las ediciones y actualiza los fantasmas existentes. Auto-key puede seguir activo; sin él, inserte la clave deseada tras confirmar la pose. Generate, en los controles avanzados de marcadores, permite regenerar explícitamente.

Los controles avanzados mantienen Marker Targets, fuentes de onion skin, rangos, subdivisión y apariencia. La visibilidad de marcadores y pieles en caché muestra u oculta sus vistas previas sin reconstruirlas. Clear All Ghosts elimina marcadores y onion skins; use la visibilidad si solo desea ocultarlos. Los marcadores ocultos no se pueden seleccionar ni con clic ni por recuadro.

## Guardar, comparar y restaurar instantáneas

Abra Compare desde Settings. Antes de Save Snapshot, elija el ámbito: Active Object / Selected Bones, Selected Path, canales de marcadores seleccionados o ámbito explícito de escena. Compruebe el objetivo mostrado. Las instantáneas guardan muestras congeladas y claves/manejadores capturados en la escena, incluso tras guardar/reabrir o desactivar/reactivar el complemento.

Hide/Show cambia la superposición sin cambiar la animación. Save Variant crea una alternativa independiente con su origen registrado; eliminar el padre conserva la variante. Con diez instantáneas retenidas, elimine registros innecesarios antes de guardar otra. Captura, variantes, vinculación, visibilidad, eliminación y restauración participan en Undo/Redo nativo.

Restore valida escena, objeto, acción, slot, hueso y canal antes de escribir. Restaura las curvas y los registros de marcadores del ámbito capturado y actualiza la presentación, incluso con actualizaciones desactivadas o congeladas. No restaura objetos ajenos ni modificadores Action arbitrarios. Las referencias antiguas que solo contienen muestras restauran valores adecuados donde las curvas pueden remodelarse.

Los objetivos sustituidos requieren vinculación deliberada. Los slots de acción compartidos se rechazan; primero haga la animación de usuario único. Bind to Active Target admite un objeto original y sus canales de huesos con nombre por referencia. Las referencias importadas de varios objetos siguen visibles y sin vincular, sin reducirse a un único objetivo. Se siguen los cambios de nombre de huesos. Tras reabrir, la identidad del canal identifica la curva; durante un gesto, una curva sustituida no recibe escrituras de reversión destinadas a la original.

## Transferir instantáneas y usar herramientas avanzadas

Exporte instantáneas a JSON para transferir datos de comparación. La importación valida y fusiona registros, reasigna colisiones de IDs y rechaza atómicamente versiones incompatibles o excesos de capacidad. Las referencias importadas y antiguas siguen visibles, pero restaurar requiere vinculación explícita: JSON no demuestra la identidad del objeto original. Si una importación falla, se conservan los registros existentes ilegibles de la escena.

Edit Motion mantiene preajustes y controles personalizados de easing. Draw to Keys convierte el trazo de anotación más largo en una trayectoria de posición; las rayas transversales identifican claves. Su diálogo conserva el objetivo seleccionado. Physics Feel, Look, Compare y las demás herramientas avanzadas siguen en Settings y en las ubicaciones alternativas de barra lateral/estante.

## Solución de problemas y notas de versión

Si no aparece nada, compruebe el primer icono, que el objetivo esté animado, la visualización pertinente y cantidades superiores a cero. Si faltan puntos editables, añada el objetivo a Paths y active Markers Display. Ver más muestras puede requerir un intervalo menor u otro intervalo de claves. Los marcadores siguen el muestreo de Paths.

Si falta la barra, seleccione Top Toolbar en las preferencias Ghost y use View > Show Ghost Toolbar. Si está cortada en una vista dividida, desplace horizontalmente la fila nativa. Las preferencias de ancho del estante izquierdo siguen disponibles; su verificación completa por ancho/escala quedó incompleta en 4.2.11. Esta versión no promete corregir todos esos casos.

La implementación de herramientas directas recibió 188 comprobaciones específicas en segundo plano antes de esta actualización de versión/documentación, cubriendo interfaz, edición, trayectorias, instantáneas, inicio, ubicación y visualización en caché. Esos resultados describen la implementación previamente probada. El archivo 4.3.1 tiene comprobaciones separadas de integridad ZIP, metadatos y coincidencia byte a byte con el código; este empaquetado no declara nuevas pruebas funcionales. Use el [gestor de incidencias](https://github.com/Axleonex/B4Artists_Toolkit/issues) e indique objetivo, operación y paso fallido.
