# Ghost Tool 4.3.1: guía de uso

Traducción de la [guía inglesa 4.3.1](../GhostTool_User_Manual.md). Se conservan los nombres ingleses de los controles para encontrarlos en Bforartists. Esta traducción no ha recibido una revisión lingüística profesional.

Ghost Tool para Bforartists muestra mallas fantasma, trayectorias y marcadores de movimiento editables. La guía de la versión 4.3.1 incorpora la barra directa de la vista, cantidades Before/Ahead independientes, ajustes al mantener pulsado, arrastre persistente de marcadores y restauración actualizada de los marcadores de instantáneas.

Esta guía acompaña al [ZIP de instalación de Ghost Tool 4.3.1](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Actualizar el repositorio no actualiza automáticamente el complemento instalado: instale el nuevo ZIP y reinicie Bforartists. Consulte las [notas de versión](../releases/4.3.1/RELEASE-NOTES.md) y el [registro del paquete](../releases/4.3.1/package-receipt.json) para ver la versión y la suma de comprobación.

## Instalar y encontrar Ghost Tool

Descargue `b4_ghost_tool_v4.3.1.zip` e instálelo mediante Edit > Preferences > Add-ons > Install from Disk. Active Ghost Tool y reinicie Bforartists tras sustituir una versión instalada. Compruebe que Preferences indique 4.3.1. Un ZIP antiguo sigue instalando su versión original.

Ghost Tool utiliza Top Toolbar de forma predeterminada, en la fila nativa Tool Settings de la vista 3D. Con las cabeceras arriba, esta fila está justo debajo de la cabecera principal y sigue su alineación. Preferences también ofrece Right Sidebar (N) y Left Tool Shelf (T). Las opciones Top Header guardadas anteriormente migran a la barra visible; la preferencia ahora se llama Top Toolbar.

Los controles nativos de herramientas y modos siguen disponibles. Las vistas estrechas o divididas mantienen toda la barra Ghost en el mismo orden. Arrastre horizontalmente la fila con el botón central del ratón para llegar a controles fuera del área visible. Si está oculta, elija View > Show Ghost Toolbar. Guarde las preferencias normalmente para conservar su elección.

## Inicio rápido: inspeccionar un objetivo animado

Seleccione un objeto animado o hueso de pose y active el primer icono de fantasma. Pulse Ghosts para mostrar las vistas previas de malla; ajuste Before y Ahead por separado. Elija Wire o Solid para su apariencia. Mantenga Ghosts pulsado para escoger muestreo por pasos de fotogramas o por claves y ajustar opacidad, desvanecimiento o In Front.

Pulse Paths para mostrar una trayectoria. Si no existe ningún objetivo de trayectoria, la acción puede añadir el objetivo animado seleccionado. Use Add Selected Path para añadir otro o Follow Selection para seguir la selección actual. Active Markers Display para mostrar los puntos editables de una trayectoria añadida a la lista.

Pulse Drag y después seleccione y mueva marcadores en la vista 3D. Confirme un movimiento y elija otro marcador sin reiniciar Drag. Pulse Drag de nuevo o Escape para salir. Antes de editar, mantenga Drag pulsado para elegir cómo afecta a la animación la suelta del marcador.

## Leer la barra superior de izquierda a derecha

**Ghost Tool:** el primer icono activa o desactiva toda la herramienta. Es independiente del botón Ghosts que muestra las mallas. Al desactivarlo también se desarman los modos de edición de marcadores y manejadores. Manténgalo pulsado para Update Meshes While Scrubbing, Update Markers While Scrubbing y Freeze Updates.

**Ghosts:** muestra u oculta las mallas fantasma. Los números Before y Ahead tienen sus propios botones menos y más. Wire Ghosts y Solid Ghosts son selectores explícitos de estilo. Ocultar las mallas conserva el estilo elegido; seleccionar un estilo no es un interruptor de visibilidad.

**Paths:** muestra u oculta las trayectorias. Sus propios números Before y Ahead van seguidos de Add Selected Path y Follow Selection. Los objetivos añadidos permanecen al seleccionar otro objeto o hueso. Follow Selection añade una vista previa de la selección actual. Los objetivos de trayectoria y los marcadores de edición fijados son conceptos diferentes.

**Drag:** inicia el modo persistente Drag Markers. **Pin:** inicia la selección de un marcador para fijarlo o liberarlo. **Markers Display:** el botón con forma de rombo, inmediatamente a la derecha de Pin, muestra u oculta los marcadores editables de las trayectorias. Los textos al pasar el puntero identifican cada herramienta.

**Arc Style:** un clic abre directamente Solid, Speed Colored y Fade. Controla el arco de movimiento Ghost, no el estilo Wire o Solid de las mallas. Paths tiene su propio Line Style en el menú de pulsación prolongada. **Spacing Ticks:** alterna los indicadores de espaciado; manténgalo pulsado para Acceleration Indicators.

**Settings:** abre los controles avanzados de generación de marcadores, objetivos, rango, edición, comparación, física y apariencia. Generate y Clear ya no se repiten como iconos independientes en la fila superior. Siguen disponibles en los controles avanzados.

## Ajustar las cantidades Before y Ahead

Hay dos números junto a Ghosts y otros dos junto a Paths. El primero, Before, cuenta las muestras anteriores al fotograma actual. El segundo, Ahead, cuenta las posteriores. Son cantidades independientes, no un único control de densidad. Edite un número directamente o utilice sus botones menos y más de la barra superior. Cero desactiva las muestras de ese lado.

Las cantidades indican cuántas muestras solicitar; el muestreo determina dónde se sitúan. Con el cursor temporal en el fotograma 20, Ghosts Before 3, Ahead 2 y paso 2 solicitan muestras en 18, 16 y 14 antes, y 22 y 24 después, según la animación disponible y los límites de rango. La pose del fotograma actual no forma parte de esas muestras anteriores/posteriores.

By Keyframe utiliza las claves de animación del objetivo en lugar de fotogramas equidistantes. Su intervalo permite saltar claves. Editar los números de Paths selecciona la ventana basada en cantidad alrededor del cursor temporal. Los modos avanzados de rango siguen en Settings y usan sus propias reglas.

## Mantener pulsada una herramienta para sus ajustes

Un clic normal realiza la acción principal. Mantenga pulsado un botón compatible para abrir sus parámetros. Arc Style es la excepción: un clic abre inmediatamente sus tres opciones. Settings también abre su panel avanzado con un clic normal.

**Mantener Ghosts:** elija muestreo por pasos o por claves. El primero muestra Every (Frames); 1 utiliza cada fotograma. El segundo muestra Keyframe Interval, incluido un intervalo personalizado. Los ajustes visuales incluyen Opacity, In Front y Fade.

**Mantener Paths:** elija el muestreo y su intervalo en fotogramas o claves. Line Style, Frame Numbers y Bezier Handles controlan la visualización. Active Bezier Handles para inspeccionar o editar los manejadores de las curvas.

**Mantener Markers Display:** cambie el muestreo compartido con Motion Paths, los puntos de claves y los números de fotograma de los marcadores. Este menú está en la barra superior. No existe un tercer modo de muestreo independiente para marcadores: cambiarlo aquí cambia también Paths.

**Mantener Drag:** elija When Released, Curve Shape o Smooth Neighbours según corresponda, Nearby Frame Reach y Falloff. **Mantener Pin:** consulte las instrucciones o elija Unpin All Markers. **Mantener Follow Selection:** ajuste Highlight Active Path. **Mantener Spacing Ticks:** elija Acceleration Indicators.

## Usar la barra inferior de la Timeline

La tira Ghost compacta está en la misma fila que los botones nativos de la Timeline. No es una segunda fila personalizada debajo de su barra de herramientas. La actualización documental 4.3.1 no rediseña esta tira.

El orden es: activación general; mallas Ghosts; cantidades de mallas anteriores y posteriores; Wire y Solid; Drag Markers; rombo de marcadores editables; Paths; cantidades de trayectoria anteriores y posteriores. Cada pareja mantiene el orden anterior/posterior de la barra superior.

Mantenga Ghosts o Paths en la Timeline para Frame by Frame, By Keyframe, intervalos y visualización. More Ghost Settings abre las opciones completas. El rombo inferior es un interruptor directo; su menú independiente está en Markers Display de la barra superior. Las instantáneas están en Compare, dentro de los ajustes avanzados, no en la tira inferior.

## Arrastrar varios marcadores seguidos

Active Ghost Tool y muestre los marcadores editables de un objetivo animado. Drag arma el selector; el texto de estado solicita un marcador en la vista 3D. Pulsar una zona vacía lo deja esperando: acérquese a un marcador visible. Confirmar un movimiento mantiene Drag activo para el siguiente. Todos los botones Drag Markers comparten este modo.

Pulse Drag de nuevo o Escape para desactivarlo. Escape durante un movimiento cancela ese movimiento y restaura sus curvas y posiciones iniciales. Los movimientos ya confirmados son ediciones separadas; reviértalos con Undo. Desactivar la herramienta, perder el objetivo, cambiar de archivo/historial o desactivar el complemento también termina o cancela las sesiones afectadas.

El arrastre de manejadores de trayectoria también tiene espera persistente. Muestre Bezier Handles, inicie su acción de arrastre y seleccione manejadores visibles sucesivamente. Sigue disponible Shift+G. Alt alterna el comportamiento de alineación durante el arrastre. Escape cancela el movimiento de manejador en curso y sale del modo.

## Elegir movimientos suaves o angulosos

Mantenga Drag y examine When Released. Reshape Handles cambia los manejadores Bézier existentes para que la curva atraviese la muestra movida sin añadir una clave. Curve Shape ofrece Free, Locked y Smooth: Free permite cambios libres; Locked conserva los ángulos; Smooth redistribuye la influencia de los manejadores a lo largo del segmento.

Insert Keyframe escribe una clave real en el fotograma del marcador. Smooth Neighbours puede suavizar los manejadores de las claves adyacentes tras insertarla. Nearby Frame Reach y Falloff controlan cómo participan los fotogramas cercanos en el esculpido del movimiento.

La línea visible también depende de la densidad de muestreo. Muestras muy separadas producen una línea basta aunque la animación subyacente sea curva. Use un paso menor para inspeccionarla. Un giro brusco puede deberse a la interpolación, los manejadores o el modo de edición; añadir solamente muestras de visualización no cambia la forma de la curva animada.

## Fijar marcadores y gestionar objetivos de trayectoria

Pulse Pin y después un marcador visible para alternar su fijación. Pin es una selección puntual, no el modo persistente Drag; actívelo otra vez para elegir otro marcador. Puede fijar varios, no solo uno. Permanecen inmóviles durante el remodelado y un refresco conserva los registros fijados correspondientes. Mantenga Pin y elija Unpin All Markers para liberarlos juntos.

Añadir un objetivo de trayectoria conserva el objeto o hueso en la lista; no congela todas sus muestras de animación. Follow Selection cambia la vista previa de selección mientras permanecen los objetivos añadidos explícitamente. Gestione estos en la lista de Paths de Settings. Markers Display controla los puntos editables de esas trayectorias; Keyframe Dots es una ayuda visual distinta.

## Actualización en vivo y edición nativa

Live Update Markers y Live Update Skin están desactivados por defecto; las escenas existentes conservan sus valores guardados. Desactivados, desplazar el cursor temporal mantiene la última vista previa actualizada. Cambie este comportamiento bajo el icono Ghost principal. Freeze Updates también pausa los refrescos automáticos.

Durante movimientos, rotaciones, escalados y gestos nativos de gizmos, Ghost mantiene la última vista previa en lugar de recorrer fotogramas. Tras confirmar o cancelar, espera a que se estabilicen las ediciones y refresca los fantasmas existentes. Auto-key puede seguir activo; sin él, inserte la clave deseada después de confirmar la pose. Generate en los controles avanzados regenera los marcadores cuando haga falta.

Los controles avanzados mantienen Marker Targets, fuentes de onion skin, rango, subdivisión y apariencia. La visibilidad de marcadores y pieles en caché permite mostrar u ocultar sus vistas previas sin reconstruirlas. Clear All Ghosts elimina marcadores y onion skins; use visibilidad para solo ocultarlos. Los marcadores ocultos no pueden seleccionarse con el puntero ni por recuadro.

## Guardar, comparar y restaurar instantáneas

Abra Compare desde Settings. Antes de Save Snapshot, elija el alcance: Active Object / Selected Bones, Selected Path, canales de marcadores seleccionados o alcance explícito de escena. Compruebe el objetivo mostrado. Las instantáneas conservan muestras congeladas y claves/manejadores capturados; se guardan con la escena y sobreviven a reapertura y desactivación/reactivación del complemento.

Hide/Show cambia la superposición de una instantánea sin modificar la animación. Save Variant crea una alternativa independiente registrando su origen; eliminar el padre conserva la variante. Con diez instantáneas guardadas, elimine alguna antes de añadir otra. Captura, variantes, vinculación, visibilidad, borrado y restauración participan en Undo/Redo nativo.

Restore valida la identidad de escena, objeto, acción, slot, hueso y canal antes de escribir. Restaura curvas y registros de marcadores del alcance capturado y refresca la vista, incluso con actualizaciones en vivo apagadas o congeladas. No restaura objetos ajenos ni modificadores arbitrarios de Action. Las referencias antiguas con solo muestras restauran valores adecuados donde las curvas admiten remodelado.

Los objetivos sustituidos requieren vinculación deliberada. Se rechazan slots de acción compartidos: haga primero que la animación sea de usuario único. Bind to Active Target admite un objeto original y sus canales de huesos nombrados por referencia. Las referencias importadas multiobjeto permanecen visibles y sin vincular, sin reducirse a un objetivo. Se siguen los cambios de nombre de huesos. Tras reabrir, la identidad del canal identifica la curva; durante un gesto, una curva sustituida no recibe la reversión destinada a su original.

## Transferir instantáneas y usar herramientas avanzadas

Exporte instantáneas a JSON para transferir datos de comparación. La importación valida y combina registros, remapea identificadores duplicados y rechaza atómicamente versiones no compatibles o exceso de capacidad. Las referencias importadas o antiguas siguen visibles, pero restaurarlas exige vinculación explícita porque JSON no demuestra la identidad del objeto original. Si falla la importación, se preservan los registros existentes de escena que no puedan leerse.

Edit Motion conserva preajustes y controles de easing personalizados. Draw to Keys convierte el trazo de anotación más largo en una trayectoria de posición; las rayas transversales indican las claves. El diálogo conserva el objetivo elegido. Physics Feel, Look, Compare y demás herramientas avanzadas siguen accesibles en Settings y en las ubicaciones alternativas de barra lateral o estante.

## Solución de problemas y notas de versión

Si no aparece nada, confirme el primer icono Ghost, que el objetivo tenga animación, que la visualización correspondiente esté activa y que sus cantidades superen cero. Si faltan puntos editables, añada el objetivo a Paths y active Markers Display. Más muestras visibles pueden requerir un paso menor u otro intervalo de claves. El muestreo de marcadores sigue al de Paths.

Si falta la barra, seleccione Top Toolbar en las preferencias Ghost y View > Show Ghost Toolbar. Si se corta en una vista dividida, desplace horizontalmente la fila. Las preferencias de anchura del estante izquierdo siguen disponibles; su verificación completa de anchura/escala quedó incompleta en 4.2.11. Esta versión no afirma corregir todos esos casos.

La implementación directa recibió 188 comprobaciones específicas en segundo plano antes de esta actualización de versión/documentación: interfaz, edición, trayectorias, instantáneas, inicio, ubicación y caché. Son resultados de la implementación ya comprobada. El archivo 4.3.1 también tiene comprobadas la integridad ZIP, la versión y la coincidencia exacta con el código fuente; este empaquetado no afirma una nueva ejecución de pruebas funcionales. Indique objetivo, operación y paso fallido en el [seguimiento de incidencias](https://github.com/Axleonex/B4Artists_Toolkit/issues).
