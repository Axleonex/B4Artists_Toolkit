# Soluciones rápidas y glosario

[← Contenidos](index.md)

## Índice de soluciones rápidas

Utilice esta sección cuando algo haya salido mal y necesite la respuesta rápidamente.

|problema|donde buscar|
|---|---|
|La carga falla: no se reconocen los huesos|[Guía 4](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar) + [VRChat Extras de nombres](08-vrchat.md#vrchat-naming-extras-extras-de-nombres-de-vrchat) |
|Avatar en pose T/no sigue el movimiento|[Guía 5](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat) + [Configurar huesos humanoides](08-vrchat.md#configurar-huesos-humanoides) |
|La malla se deforma extrañamente/la piel se estira|[Transferencia de peso](05-rig-tools.md#transferencia-de-pesos) + [Espejo de peso](05-rig-tools.md#espejo-de-pesos), o recalcular con [Recálculo automático del peso óseo](05-rig-tools.md#recálculo-automático-de-pesos-de-huesos) |
|Un lado del cuerpo tiene diferentes pesos.|[Espejo de peso](05-rig-tools.md#espejo-de-pesos) |
|Pasadores para el cabello a través de la cabeza.|[Guía 6, Paso 5](02-guides-a.md#paso-5--añadir-colisionadores-recomendado) — agregar colisionadores|
|La física del cabello no se mueve.|[Guía 6](02-guides-a.md#guía-6-añade-física-de-cabello): comprueba la detección de cadena y el ajuste preestablecido de PhysBone|
|Clips de ropa a través del cuerpo.|[Guía 7](02-guides-a.md#guía-7-adjunta-ropa-que-se-mueva-con-tu-cuerpo) — ejecutar **Detect Collisions** |
|La sincronización de labios no funciona|[Guía 8](03-guides-b.md#guía-8-configura-la-sincronización-labial) + [VRChat Mapeo de visema](08-vrchat.md#vrchat-viseme-mapping-mapeo-de-visemas-de-vrchat) |
|Avatar tiene un rendimiento muy pobre|[Guía 9](03-guides-b.md#guía-9-mejora-el-rendimiento-de-tu-avatar) + [Comprobar rendimiento](08-vrchat.md#verificar-rendimiento) |
|VRM La importación de falla|[Guía 2, Paso 1](02-guides-a.md#paso-1--instalar-el-complemento-vrm): instala el complemento VRM |
|MMD La importación de falla|[Guía 3, Paso 1](02-guides-a.md#paso-1--instalar-mmd_tools) — instalar mmd_tools|
|El validador de rigs muestra errores|[Validador de plataforma](05-rig-tools.md#validador-de-rig): ejecuta la validación y sigue los mensajes|
|Los huesos desaparecieron / no puedo ver ningún hueso|[Colecciones de huesos](05-rig-tools.md#colecciones-de-huesos) → **Show All Collections** |
|No puedo encontrar los paneles de BoneCraft |BoneCraft y Rig Builder están en el estante de herramientas izquierdo (presione T), CATS en la barra lateral derecha (presione N); consulte [donde estan las cosas](01-start.md#dónde-está-cada-cosa) |
|Quiero un ejemplo completo de mecanismos.|[Tutorial: Crescent Rose](12-crescent-rose.md): 8 pasos de preparación y 30 pasos de mecanismos con capturas de pantalla y el archivo terminado en `examples/crescent-rose/` |
|Una pestaña está en el lado equivocado|Preferencias → Complementos → BoneCraft → Pestañas → Izquierda o Derecha|
|Faltan secciones de BoneCraft en Propiedades → Escena|Preferencias → Complementos → BoneCraft → Pestañas → Propiedades de escena → Mostrar; azul significa encendido. Consulte también los paquetes de herramientas en Herramientas|
|Quiero ocultar BoneCraft en Propiedades → Escena|Desactive Propiedades de escena → Mostrar en Preferencias → Pestañas. Deja las pestañas de la ventana gráfica y la pestaña de datos de armadura en paz.|
|Una herramienta se ejecuta antes de que pueda elegir sus opciones.|En 9.1, ajuste sus opciones inmediatamente después en el panel Ajustar última operación de la ventana gráfica, antes de ejecutar otra operación.|
|Colocar marcadores de rig no coloca un marcador|Inicie el Asistente de montaje automático, vaya a un paso de marcador, use el Modo objeto y haga clic en la malla seleccionada por el asistente; consulte [Constructor de plataformas](06-rig-builder.md#asistente-auto-rig) |
|El mecanismo de construcción no sabe qué piezas usar|Primero agregue piezas de la selección, seleccione el rig del mecanismo o una de sus piezas, elija el tipo en el encabezado de la herramienta y luego haga clic en la primera pieza; consulte [Mecanismos](07-mechanisms.md#articulaciones-y-enlaces-un-ejemplo-de-cada).|
|Exportación bloqueada: huesos humanoides desaparecidos aunque existen|Ejecute **Auto-Map All**, luego**Fix Humanoid Map** en la pelusa de la sección VRM /VRoid. Si realmente no existe un hueso requerido, el rig lo necesita primero: ver [Guía 5](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat) |
|El FBX exportado muestra formas o tubos auxiliares gigantes.|Mantenga **Helper Meshes** apagado a menos que necesite control o mallas con formas personalizadas|
|Unity o Unreal importa materiales grises|Exporte con **Embed Textures** activado, luego use las opciones de importación/extracción de material de Unity o la importación de material FBX de Unreal.|
|Todas las pesos están en los huesos equivocados|Vuelva a ejecutar Generar rig del asistente, use [Transferencia de peso](05-rig-tools.md#transferencia-de-pesos) o **Smart Automatic Weights** en la pestaña CATS |
|Dos rigs deben ser una|[Guía 11: Fusionar dos rigs juntas](03-guides-b.md#guía-11-une-dos-rigs) |
|La forma correctiva no se enciende.|Verifique el eje y el ángulo del hueso en [Teclas de forma correctivas](05-rig-tools.md#shape-keys-correctivos) |
|La animación se ve mal en una rig diferente|[Reorientar](05-rig-tools.md#redireccionar) — comprobar el mapeo óseo|
|Una herramienta CATS advierte "Ejecutar primero el modelo de reparación"|Ejecutar modelo de reparación: [La tubería CATS](04-cats-pipeline.md) |
|La boca se desgarra o se parte al hablar.|Se omitió el modelo de reparación; vuelva a ejecutarlo desde la fase 1: [Guía 13, Fase 1](03-guides-b.md#fase-1--corregir-modelo) |
|Los ojos de Avatar se atascan mirando hacia abajo en VRChat |El seguimiento ocular se ejecutó antes de Fix Model; se volvió a ejecutar desde Fix Model: [CATS: Seguimiento ocular](09-cats.md#seguimiento-ocular) |
|La tecla de forma hace que la malla explote cuando se activa|Pose to Shape Key se ejecutó antes de Fix Model; se volvió a ejecutar desde Fix Model: [CATS: Claves de pose y forma](09-cats.md#pose-y-shape-keys) |
|El avatar aparece con el tamaño incorrecto en VRChat |Las transformaciones se aplicaron antes de finalizar la canalización: vuelva a importar desde el archivo fuente y reinicie desde Fix Model.|
|Los nombres de los huesos son japonés/chino/coreano.|[CATS: Traducir nombres de huesos](09-cats.md#traducir-nombres-de-huesos) |
|Avatar no tiene sincronización de labios ni teclas con forma de boca|[CATS: Visemas](09-cats.md#visemas): genera 15 visemas a partir de 3 formas base|
|Un mecanismo muestra "cambiado a mano"|[Mecanismos](07-mechanisms.md): use **Keep mine** o**Restore** |

## Glosario

**Ajustar última operación:** El panel de vista para cambiar las opciones de la operación que acaba de ejecutar. Muchas herramientas BoneCraft 9.1 se ejecutan primero y toman sus opciones aquí; ajústelos antes de ejecutar otra operación.

**Armature:** Bforartists ' palabra para esqueleto: un conjunto de huesos que se pueden posar y animar.

**Forma de fusión:** Ver clave de formas.

**Hueso:** Un segmento de un esqueleto. Los huesos forman una jerarquía (padre → hijo) en la que los huesos hijos siguen a sus padres.

**Colección de huesos:** Un grupo de huesos con nombre. Puedes mostrar u ocultar una colección completa a la vez.

**CATS:** Las herramientas CATS: preparación del modelo para VRChat con una canalización guiada (limpieza, visemas, seguimiento ocular, transformaciones). Están en la pestaña CATS.

**Tubería CATS:** El orden de seis fases de las herramientas CATS: Corregir modelo → Atlas de materiales → Visemas → Seguimiento ocular → Pose para dar forma → Aplicar transformaciones. Las herramientas advierten cuando una fase anterior de la que dependen no ha finalizado.

**Tecla de forma correctiva:** Una tecla de forma que se activa cuando un hueso alcanza un ángulo, para fijar la malla en posturas extremas.

**Hueso deforme:** Hueso que mueve la malla. No todos los huesos se deforman; algunos son sólo controles.

**Seguimiento ocular:** La herramienta CATS que configura los huesos del ojo (`LeftEye`, `RightEye` ) y las restricciones de rotación que utiliza VRChat para mover los ojos.

**FBT (seguimiento de cuerpo completo):** Una función VRChat que rastrea todo tu cuerpo con hardware adicional (como Vive Trackers), incluidas las caderas y los pies. Fix FBT ajusta el hueso de la raíz.

**FBX:** Un formato de archivo que transporta modelos 3D, esqueletos y animaciones entre programas. El formato estándar para VRChat.

**Modelo de reparación:** La limpieza CATS: vértices duplicados, geometría suelta y normales incorrectas. Siempre el primer paso CATS.

**FK (Cinemática hacia adelante):** Posando rotando cada hueso de una cadena por turno: hombro, luego codo y luego muñeca. Natural para posturas de cuerpo amplio.

**IK (Cinemática Inversa):** Posar colocando el extremo de una cadena (una mano o un pie); los huesos intermedios siguen. Natural para una colocación precisa de manos y pies.

**Humanoide:** El sistema de avatar de VRChat que asigna huesos a ranuras corporales estándar, por lo que cada avatar usa los mismos controles de movimiento.

**Mecanismo:** Una rig para un puntal o pieza de máquina: una articulación (bisagra, corredera, telescopio) o un vínculo (pistón, vínculo de engranaje, seguimiento), construido a partir de huesos y restricciones comunes. Ver [Mecanismos](07-mechanisms.md).

**Malla:** La superficie 3D que forma el cuerpo visible de tu avatar.

**MMD (MikuMikuDance):** Software gratuito de animación 3D popular en Japón y en la comunidad del anime. Utiliza archivos de modelo `.pmx` y archivos de animación `.vmd`.

**Objetivo de transformación:** Consulte Tecla de forma.

**Libro mayor de operaciones:** La lista CATS de cada operación que ejecutó, con su tiempo y resultado.

**PhysBone:** Componente de VRChat que hace que los huesos se balanceen, reboten y choquen. Se utiliza para cabello, colas y accesorios colgantes.

**Estado de la canalización:** La lista CATS de las seis fases, con una marca de verificación para cada fase que se realiza.

**PMX:** El formato principal de modelo 3D de MikuMikuDance.

**Modo Pose:** El modo para posar y animar huesos. Seleccione la armadura y presione Ctrl+Tab, o use el menú desplegable de modo en la parte superior izquierda de la ventana gráfica.

**Rig/rigging:** Construir un esqueleto dentro de un modelo 3D y conectarle la malla para que pueda posarse y animarse.

**Clave de forma:** Una versión guardada de una malla en una posición deformada. Las teclas de forma se combinan con diferentes puntos fuertes; impulsan las expresiones faciales, la sincronización de labios y las transformaciones corporales.

**SDK (Kit de desarrollo de software):** Para VRChat, VRChat Creator Companion y sus herramientas Unity para cargar avatares.

**Spline IK:** Una cadena de huesos que sigue una curva. Se utiliza para colas, tentáculos, pelo largo y espinas.

**T-pose:** Una pose de referencia: de pie con los brazos extendidos a los lados.

**Estante de herramientas:** El panel en el lado izquierdo de la ventana gráfica 3D (presione T), donde se encuentran de forma predeterminada las pestañas BoneCraft y Rig Builder.

**Vértice:** Un único punto en el espacio 3D. Las mallas están formadas por muchos vértices unidos por aristas y caras.

**Grupo de vértices:** Un conjunto de vértices con nombre; define qué vértices se mueve un hueso.

**Viseme:** Forma de boca para un sonido del habla. VRChat utiliza 15 visemas para la sincronización de labios.

**Peso/peso pintura:** Valores de 0.0 a 1.0 que dicen con qué fuerza cada hueso mueve cada vértice. La pintura con peso es la forma visual de ajustarlos.

**Asistente:** El asistente de montaje automático del constructor de rigs: coloca marcadores en la malla y construye la rig a partir de ellos.

**Hueso de peso cero:** Un hueso que no mueve ningún vértice. Cuesta rendimiento sin cambiar la apariencia del avatar; Fix Model y el optimizador de rendimiento los eliminan.

Siguiente: [¿Qué hay de nuevo?](11-whats-new.md)
