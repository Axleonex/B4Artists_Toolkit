# Novedades

[← Contenidos](index.md)

Lo más nuevo primero.

## 9.1.2 (octubre de 2026)

- **Cambio de Propiedades de escena:** Preferencias > Pestañas tiene una nueva fila Propiedades de escena. Su botón Mostrar (azul mientras está encendido) muestra u oculta todas las secciones de BoneCraft en la pestaña Propiedades > Escena (Rig Builder, Mecanismos, CATS, Herramientas Avatar, Herramientas VRChat, Importar/Exportar) sin deshabilitar el complemento. Comienza y deja las pestañas de la ventana gráfica y la pestaña Armadura en paz. Ver [donde estan las cosas](01-start.md#dónde-está-cada-cosa).

## 9.1.1 (octubre de 2026)

- **Íconos más claros:** cada ícono ahora significa una cosa en todas partes. Alrededor de 60 botones obtuvieron un ícono Bforartists que se ajusta mejor (por ejemplo, Aplicar todas las transformaciones, Diezmar, Normalizar nombres, Traducir, Fusionar, Separar, Mezclar pose y Sincronización de labios), y un botón muestra el mismo ícono en cada panel.
- **Paneles más tranquilos:** los títulos y el texto fijo ya no llevan íconos de temas. Las sugerencias que informan un estado muestran el ícono de información, advertencia o verificación.
- **Cuadrícula de íconos legibles:** cada botón en las pestañas Estante de herramientas de postura y pesos tiene su propio ícono, por lo que un estante estrecho sigue siendo legible.

## 9.1.0 (octubre de 2026)

- **Herramientas donde Bforartists incluye las suyas:** Entradas BoneCraft en los menús Agregar → Armadura, Pose, Pesos y Objeto, y un panel de botones BoneCraft en las pestañas Estante de herramientas Pose y Pesos de Bforartists.
- **Actúe primero, ajuste después:** Quick Rig, Fit Dropped Rig, las herramientas de peso, Ribbon, Spline IK, Delta Mush y las herramientas de hueso CATS se ejecutan a la vez con los valores que utilizó por última vez; los ajusta después en el panel Ajustar última operación. Menos ventanas emergentes de "¿estás seguro?".
- **Acciones primero, opciones plegadas:** varios paneles muestran sus botones primero y las configuraciones opcionales en un pliegue debajo. Las entradas requeridas permanecen antes de la acción, al igual que los interruptores de limpieza de Fix Model. Las configuraciones parecen configuraciones (casillas de verificación, nunca botones) y los encabezados de los paneles no tienen íconos.
- **Herramientas de gestos:** Colocar marcadores de rig (haga clic en la malla para colocar el siguiente marcador del Asistente de rig automática) y Crear mecanismo (haga clic en una pieza para iniciar una unión o enlace) se encuentran en la barra de herramientas de la ventana gráfica.
- **Secciones de avatar:** Avatar Tools contiene mapeo humanoide, cabello, visemas y exportación. La sección separada Herramientas VRChat agrupa las utilidades de rendimiento, ropa y nombres. Las guías utilizan estos nombres de paneles actuales.
- **Información sobre herramientas:** cada operador y cada opción se explican por sí solos.
- **Mostrar, no ocultar:** las secciones permanecen visibles y dicen qué seleccionar cuando el rig ya no está, el Asistente de montaje automático aparece primero en Rig Builder y los estantes comienzan lo suficientemente anchos para leer.
- **Fixes:** Generar Spline IK funciona nuevamente; Add Influence utiliza el hueso elegido; Las vistas previas de viseme usan su conjunto.

## 9.0.0 (octubre de 2026)

- **Mecanismos:** una nueva sección de la pestaña BoneCraft (y de la pestaña Propiedades Escena) que equipa accesorios y máquinas: Bisagra, Deslizamiento, Telescopio, Pistón, Enlace de Engranaje, Seguimiento y Secuencia, construido con pasos guiados y verificado con Prueba. BoneCraft nunca sobrescribe una edición manual: usted elige**Keep mine** para conservarla o**Restore** para reconstruirla. Ver [Mecanismos](07-mechanisms.md).
- **Archivo de ejemplo:** `examples/crescent-rose/` contiene Crescent Rose equipado con mecanismos (guadaña, rifle y formas compactas), y el [capitulo 12](12-crescent-rose.md) del manual lo construye paso a paso.
- **Lados de las pestañas:** cada pestaña de la ventana gráfica puede ubicarse en el estante de herramientas izquierdo o en la barra lateral derecha (Preferencias → Pestañas → Izquierda/Derecha). BoneCraft y Rig Builder comienzan a la izquierda, CATS a la derecha.
- **Rig Builder:** siempre en la pestaña Propiedades Escena, además de su propia pestaña de ventana gráfica con un diseño compacto para un estante de herramientas estrecho. Una rig Humanoid básica se envía en la biblioteca de activos BoneCraft Rigs; Fit Dropped Rig se adapta a un rig que se dejó caer desde el estante de activos.
- **Pestaña CATS:** Importar/Exportar se movió a la pestaña CATS. CATS, VRChat e Importar/Exportar también están siempre en la pestaña Escena.
- **Mostrar ayudantes:** una preferencia muestra u oculta el texto didáctico de BoneCraft; El modo compacto es su atajo.
- **Rig Validator:** los nombres de los huesos con guiones pasan; los controladores advierten sólo sobre expresiones que necesitan Python; También se comprueban los mecanismos de montaje. La tarea del validador del Panel de tareas informa nuevamente.
- **Nombre:** el complemento se llama BoneCraft.

## 8.9.x (septiembre–octubre de 2026)

- **8.9.6:** toda la pieza del vestido sigue los huesos de la falda (sin recortes en la cadera); Correctores de esquinas con labios pegajosos que te abren la mandíbula.
- **8.9.5:** IK/FK interruptor de codo sin pop; detección de hombros simétrica; los marcadores de ojos ya no se rompen; el Selector de control muestra la selección; comisuras de la boca más redondeadas; una corrección de vestido sobre el muslo; clavículas relajadas; Exportación de pose T.
- **8.9.4:** rodillas más redondeadas (los correctivos reemplazan Preservar Volumen); teclas de contacto para curvas profundas; una mezcla de costuras en los hombros.
- **8.9.3:** Huesos de la falda de dos segmentos que siguen a las piernas y son empujados por ellas.
- **8.9.2:** parpadea con las teclas de forma (sin pliegues de la tapa); una abertura de boca ovalada.
- **8.9.1:** desollado mucho más rápido en mallas densas (678.000 vértices: 232 s a 57 s); calor óseo a través de una malla proxy más ligera en lugar de fallar silenciosamente.
- **8.9.0:** claves de forma correctiva de juntas; controles faciales (apuntar con los ojos, parpadear, seguir los labios); Ropa que se dobla con las articulaciones.
- También en 8.9: recálculo automático del peso óseo y una selección de atlas más clara.

## 8.7–8.8 (septiembre de 2026)

- **8.8.0:** el panel de reorientación funciona en hosts Blender 5; marcadores de dedos colocados según la forma de la mano; IK se estira hasta la piel; una opción de Preservar volumen; una solución de enlace de Delta Mush.
- **8.7.0:** un rig de control integrado; detección de articulaciones rastreadas en las extremidades; retargeting con dirección coincidente; torcer los huesos.

## 8.5–8.6 (julio de 2026)

- **8.6.1–8.6.3:** Atlas de materiales: diagnóstico de baldosas después del horneado; Transparencia de MToon comparada con la textura real alfa y mantenida durante el atlas; mejor partición de materiales mezclados.
- **8.5.5–8.5.10:** Materiales VRM / MToon: se respeta el modo alfa, alfa funciona en 5 hosts Blender, sin explosión de emisiones, diagnóstico magenta y nombres de atlas seguros.
- **8.5.4:** el mapeo humanoide se lee correctamente; Guía de preparación de nombres.
- **8.5.2–8.5.3:** importar una descarga VRoid (.zip); una tarjeta de entrega del proyecto VRoid.
- **8.5.1:** Exportación FBX que mantiene formas combinadas.

## Versiones anteriores

**8.5.0:** Smart Combine ahora convierte a `atlas_uv` en el UV0 de exportación de forma predeterminada después del horneado. El mapa UV de origen previo al atlas se elimina de la malla del atlas generada a menos que**Keep Source UV Maps** esté habilitado en la configuración avanzada. Los controles derivados de CATS /Material Combiner/UVToolkit ahora se comparten con la compilación abierta Blender; La exclusividad de B4Artists permanece en los sistemas de producción, control, reorientación/exportación y lanzamiento exclusivo de B4Artists.

8.5.0 también actualiza el flujo de trabajo de exportación y validación. Las exportaciones VRChat, VRM, MMD y Unreal ahora exponen controles de carpetas y nombres de archivos en los paneles BoneCraft en lugar de obligarlo a confiar solo en los valores predeterminados del explorador de archivos de Blender. VRChat /Unity y Unreal FBX exportan de forma predeterminada a **Embed Textures** para facilitar la importación de material, mientras que la exportación de VRChat mantiene las mallas de formas auxiliares/de control fuera de FBX a menos que**Helper Meshes** esté habilitado. El panel VRM ahora incluye**Lint Now** más**Fix Humanoid Map**, que puede reparar el mapeo de alias humanoide obsoleto antes de exportarlo sin cambiar el nombre de sus huesos.

**8.4.5:** Smart Combine ahora obliga a las texturas de origen a tomar muestras de los rayos UV del pre-atlas conservados durante el horneado, valida la malla del atlas generada antes de ocultar los originales y restablece todas las caras del atlas a la ranura final del material del atlas para evitar trozos de ropa o batas grises o revueltos.

**8.4.4:** Material Atlas Combiner agrega controles de inspección de paridad de calidad antes del horneado: diagnóstico de sombreado/material, etiquetas de función de textura, marcadores de fuente duplicados/compartidos, anulaciones de tamaño por material, ajustes preestablecidos de empaque, horneado de salida opcional Normal/Emisión/Rugosidad y bloqueadores de verificación previa para el empaque de canales metálicos/ORM hasta que se verifique esa ruta.

**8.4.3:** Material Atlas Combiner incluye métodos de empaquetamiento UV seleccionables dentro del flujo de trabajo existente de Material Atlas. Incluye paquete inteligente, paquete de cuadrícula, variación sembrada, paquete orientado, ajuste de límites 0-1, variación avanzada y paso de rotación, con detalles del método UV registrados en el informe de depuración y el libro de contabilidad de horneado.

**8.4.2:** Material Atlas Combiner ahora apunta al UV del atlas generado durante el horneado, mientras que los nodos de textura de origen copiados leen explícitamente el UV previo al atlas. Esto corrige los resultados del atlas de batas/ropa rotos causados por las texturas de origen y el atlas horneado que muestra diferentes mapas UV. Las filas de material y textura seleccionables de 8.4.1 siguen estando disponibles.

**7.1.3 (limpieza de etiquetas de preferencias):** Se cambió el nombre de dos opciones de preferencias de complementos para que ahora coincidan con la pestaña de la barra lateral que controlan. "VRChat Avatar Tools" ahora tiene la etiqueta**CATS** (coincide con la pestaña de la barra lateral CATS ). "Tablero de tareas y barra lateral" ahora tiene la etiqueta**Rig Builder** (coincide con la pestaña de la barra lateral de Rig Builder). No se eliminaron herramientas; solo cambiaron las etiquetas de activación/desactivación en Editar > Preferencias > Complementos > BoneCraft.

**7.1.1:** BoneCraft ahora incluye las herramientas CATS: un conjunto completo de herramientas de preparación de modelos diseñadas específicamente para que los avatares de VRChat estén limpios, optimizados y completamente configurados. CATS vive en su propia pestaña de la barra lateral y utiliza un sistema de canalización que lo guía a través del orden correcto de operaciones en todo momento.

Siguiente: [Tutorial: Crescent Rose con Mecanismos](12-crescent-rose.md)
