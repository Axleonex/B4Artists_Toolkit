# Mechanisms (mecanismos)

[← Contenidos](index.md)

## Qué hace Mechanisms

Los mecanismos convierten las piezas de superficie dura en una rig mecánica funcional: bisagras,
Toboganes, telescopios, pistones, engranajes, seguidores y transformaciones enteras jugadas.
por un control deslizante. Construye huesos y restricciones Blender ordinarios, para que puedas ver
y cambie todo lo que hace, y el rig funciona en Blender sin scripts.
Los motores reciben los huesos `DEF-`. Exportación del movimiento del mecanismo horneado a motores.
viene más tarde (ver Límites de esta versión).

BoneCraft envía las herramientas, no un arma. Tú traes las piezas.

Un ejemplo completo, con una captura de pantalla para cada paso, es [Tutorial: Crescent Rose con Mecanismos](12-crescent-rose.md).

Palabras utilizadas en los paneles y en esta página:

|palabra|Significado|
|---|---|
|*Parte*|Una pieza que se mueve como un bloque sólido: un objeto o una pieza suelta de una malla. Una pieza puede montarse sobre otra.|
|*Conjunto*|Cómo se puede mover una pieza: Bisagra (gira), Deslizamiento (se mueve), Telescopio (extiende segmentos anidados).|
|*Enlace*|Lo que mueve una pieza para usted: pistón, engranaje, seguimiento.|
|*Mango*|El hueso que arrastras en la ventana gráfica. Cada articulación tiene uno. Su valor también es un control deslizante en el panel.|
|*Secuencia*|Una transformación realizada por un control deslizante, hecho de pasos.|
|*Formulario*|Un conjunto guardado de valores de manija y secuencia, como "Guardado" o "Rifle".|

## Dónde está

- **BoneCraft tab → Mechanisms** en la ventana gráfica 3D. La pestaña BoneCraft está activada.
el estante de herramientas izquierdo (presione **T**) a menos que lo haya movido a la barra lateral derecha
(**N**) en Preferencias. Se encuentra entre Skin y Review. Muestra cuando una malla
está activo (para arrancar un equipo) o cuando una armadura con mecanismos está activa; de lo contrario
explica qué seleccionar.
- **Properties editor → Scene tab → Mechanisms**, justo después de Rig Builder. es
se muestra mientras Preferencias → Pestañas → Propiedades de escena → Mostrar está activado. sin nada
utilizable seleccionado muestra una línea: "Seleccione una malla
para arrancar, o una armadura con mecanismos." Cambiar la pestaña de la ventana gráfica BoneCraft
off no lo elimina. El interruptor Propiedades de escena oculta solo la copia de la escena.
El interruptor de herramienta `mechanisms` (**Preferencias → Complementos → BoneCraft → Herramientas**)
elimina la herramienta de cada ubicación.
Las secciones de la pestaña Escena comienzan contraídas, así que haga clic en **Mechanisms** para expandirlas.
- **Object menu → Mechanisms** ofrece accesos directos para agregar piezas, uniones y enlaces.
y para probar el movimiento.
- **Viewport toolbar → Build Mechanism** inicia una unión guiada o un vínculo desde un
haga clic en una parte, en modo objeto o modo pose. Agregue las partes primero, luego seleccione
el equipo del mecanismo o una de sus partes y elija el tipo en el encabezado de la herramienta.

Dentro de Mecanismos hay cuatro subsecciones: **1. Parts**,**2. Articulaciones y
Enlaces**,**3. Secuencias** y**4. Controles**. Aparecen una vez que la rig ha
partes. Antes de eso, solo verás **Add Parts from Selection**.

Cada botón es un paso para deshacer. Si una compilación falla, todo lo que cambió se coloca
atrás y el panel muestra el motivo.

## Piezas

1. Seleccione los objetos de la pieza (o una malla hecha de piezas sueltas) en Modo Objeto.
2. Haga clic en **Add Parts from Selection**.
 - Varios objetos: una parte por objeto. Cada objeto está vinculado a su parte.
hueso y permanece donde está.
 - Una malla con piezas sueltas: una pieza por pieza. Cada pieza tiene un vértice.
grupo para su hueso y la malla obtiene un modificador de Armadura.
 - La primera vez, BoneCraft fabrica el equipo (una armadura) por usted.
3. Seleccione una parte de la lista para editarla.

Para cada parte:

- **Se mueve:** elige la parte con la que se mueve. Una parte hija sigue su
parte de los padres. "el equipo" significa que se monta en la raíz del equipo.
- **Size** establece la longitud del hueso, que establece el tamaño del mango.
- **Edit Pivot** pone un marcador en la pieza. Arrástralo a donde debería estar la pieza.
gire o deslice y luego haga clic en **Apply Pivot**. Los huesos de la pieza se mueven allí.
y el objeto permanece en su lugar.
- **Apply Transforms** aparece cuando la parte de un objeto tiene rotación no aplicada o
escala. Haz clic en él. Las transformaciones no aplicadas inclinan los ejes.
- El botón **X** elimina la pieza. Se niega mientras exista una unión, vínculo u otro
parte lo usa y los nombra.
- **Merge for VRChat** (dos o más partes del objeto) une las partes del objeto en
una malla con un grupo de vértices por objeto anterior y un modificador de armadura.
Haz esto al final. Las partes unidas se convierten en partes sueltas de esa malla. eso
elimina todos los grupos de vértices que llevan el nombre de un hueso de esta armadura (que no sean
propio hueso `DEF-` de la pieza), por lo tanto, combine solo las piezas que estén montadas en el
equipo de mecanismo solo.

Puede cambiar el nombre del objeto de una parte: las partes están etiquetadas en sus objetos, por lo que la parte
encuentra de nuevo su objeto. Una copia del objeto (Shift+D) no se hace cargo del
parte. Si se elimina el objeto de una parte, la parte muestra "Falta la parte '<nombre>'"
con **Reassign** y**Delete**. Otros mecanismos siguen funcionando.

- **Reassign** utiliza la malla que ha seleccionado. Rechaza una no malla, y
rechaza un objeto que otra parte del objeto ya utiliza. Partes sueltas de uno
mesh puede compartir esa malla.
- **Delete** elimina la pieza (consulte Edición a continuación para saber cuándo se rechaza).

## Articulaciones y enlaces, un ejemplo de cada

Agregue una junta con **Add Joint**, un enlace con**Add Link**. Cada elección inicia un
construcción guiada. Funcionan desde la pestaña de la ventana gráfica y desde la Escena del editor de Propiedades.
pestaña; desde la pestaña Escena, la guía utiliza la ventana gráfica 3D más grande de la pantalla.
Alternativamente, active Construir mecanismo en la barra de herramientas de la ventana gráfica, elija la articulación
o escriba un enlace en el encabezado de la herramienta y haga clic en su primera parte. Ese clic inicia el
mismo guía y suministra su primera elección. Continúe con las selecciones y opciones de ejes.
solicitado en la ventana gráfica; los menús Agregar articulación y Agregar enlace permanecen disponibles.

Reglas breves para cada construcción guiada:

- Haga clic en las partes de la ventana gráfica. Las partes en las que se hace clic obtienen un contorno y un número.
- Cuando un paso necesite un eje, presione **X**,**Y** o**Z**, o**A** para alinear con
la selección. **Align to Selection** es para bisagras en ángulo. Necesita la malla de la pieza.
para seguir en Modo Edición con un borde o cara seleccionada cuando presionas **A**,
y la guía ignora **Tab**. Entonces ingrese al Modo de Edición en la malla de la pieza y
seleccione primero una arista o una cara. Permanezca en el modo de edición, inicie **Agregar articulación →
Bisagra**, haga clic en la pieza, presione**A**. Si no se selecciona nada utilizable, la guía
te dice y puedes presionar otra tecla.
- El último paso muestra una vista previa del mecanismo que se mueve en un bucle. **Enter** lo conserva.
**Esc** lo elimina.
- El encabezado y la barra de estado muestran una oración completa para cada paso. Con espectáculo
Los ayudantes apagados muestran una etiqueta corta.

Cada fila de la lista Uniones y enlaces tiene cuatro botones de íconos: **Test** (reproducir
triángulo), **Edit** (lápiz, muestra los ajustes),**Detach** (cadena rota) y
**Delete** (X).

Después de la compilación, el elemento seleccionado en la lista muestra solo la configuración que
usos tipográficos.

### Hinge (bisagra)

Bisagra de hoja, 0°…90°:

1. Agregue piezas de la selección con una pieza de hoja.
2. **Add Joint → Hinge**. Haga clic en la hoja. Presione**X**. Presione**Enter**.
3. Obtienes una manija de medio círculo, `CTRL-Blade`, y una *Blade Hinge* en el
lista. Establezca **Min** 0 y**Max** 90 (° para una bisagra).
4. Pruébelo: arrastre el controlador de semicírculo. Se detiene a 90°. **Set Min** y
**Set Max** copia la pose actual del mango en los límites.

Un límite que está por debajo de un giro completo debe permanecer dentro de −180°…180°. Límites como
170°…190° se rechazan con un mensaje. Un alcance de un giro completo o más (por
ejemplo −180°…180°) gira libremente sin límite.

### Slide (deslizador)

Deslizamiento de barril, 0…0,3:

1. **Add Joint → Slide**. Haga clic en la parte Barril. Presione**Y**. Presione**Enter**.
2. Obtienes un mango de flecha. Configure **Min** 0 y**Max** 0.3 (unidades de escena).
3. Pruébalo: arrastra la flecha. El cañón se desliza y se detiene en 0,3.

### Telescope (telescopio)

Mástil de tres segmentos:

1. Haz la base y las tres partes del segmento.
2. **Add Joint → Telescope**. Haga clic en la base. Haga clic en cada segmento desde la base.
hacia afuera. Presione **Enter**. Presione la tecla del eje. Presione**Enter** para conservarlo.
3. Obtienes un mango de flecha en la base. **Length** es el recorrido total;
**Shares (empty = even)** lo divide entre los segmentos. Para probar personalizado
compartidos, primero configure **Length** en 1 y luego escriba `0.5, 0.25, 0.25`. las acciones
debe sumar la Longitud, de modo que la punta recorra toda su longitud. Un error tipográfico (por
ejemplo `0.5, abc` ) se rechaza con el mismo mensaje simple: las acciones
Deben ser números, uno por segmento, que sumen la Longitud.
4. Pruébalo: arrastra la flecha. Los tres segmentos se extienden por sus acciones.
**Set Max** establece la longitud desde la posición del mango.

### Piston (pistón)

Elevación: cilindro en el bastidor, varilla en el brazo.

1. Primero coloque una bisagra en el brazo y colóquelo para que se desplace sobre el marco.
2. **Add Link → Piston**. Haga clic en la parte del cilindro (en el marco). Haga clic en la varilla
parte (en el brazo).
3. Obtienes un pistón sin manija. Cada parte apunta al enlace de la otra.
punto. **Stretch** (opcional) estira la varilla, para resortes y cables.
4. Pruébalo: mueve el mango del brazo. El pistón sigue. Si nada mueve el
Piston todavía, la construcción funciona pero no tiene vista previa y **Test** lo dice.

### Gear Link (enlace de engranaje)

Marcha 20:40:

1. Ambas partes necesitan primero una articulación. La parte motriz necesita una bisagra. Para engranajes y
Correa la parte accionada necesita una bisagra; para Rack necesita una diapositiva.
2. **Add Link → Gear Link**. Haga clic en la parte de conducción. Haga clic en la parte conducida.
3. En su configuración establezca **Source Teeth** 20 y**Target Teeth** 40 (o escriba un
**Ratio** ).**Kind** es engranaje, correa o cremallera.**Reverse** invierte la dirección.
4. Pruébalo: gira la fuente. Con **Kind** Gear el objetivo gira −0.5× hasta donde
(+0,5× con Cinturón). Un engranaje invierte
dirección, un cinturón la mantiene y un estante convierte la rotación en una diapositiva (distancia
por radianes = **Ratio** ×**Pinion Radius** ).

La forma en que BoneCraft lo construye depende del rango de la bisagra de origen:

- Bajo un giro completo: una restricción de Transformación. Sigue todo lo que se mueve.
la fuente, Secuencias incluidas.
- Un giro completo o más: un conductor que no necesita Python. El objetivo gira para siempre
con la fuente. Sigue manijas y engranajes únicamente. El Rig Validator advierte
cuándo se perdería una secuencia o un seguimiento.

### Follow (seguidor)

La hoja 0–90° levanta la cubierta 0–40°:

1. Ambas partes necesitan una Bisagra o una Corredera. Una bisagra de origen necesita límites bajo un
giro completo; Se rechaza una fuente de giro libre.
2. **Add Link → Follow**. Haga clic en la parte principal (Blade). Haga clic en lo siguiente
parte (Cubierta).
3. Los rangos comienzan como el rango completo de cada articulación. Conjunto **Source Range**
0…90 y **Target Range** 0…40. Pasado cualquiera de los extremos, el objetivo se mantiene.
4. Pruébelo: mueva el mango de la hoja. La portada sigue.
5. Marque **Curve** para remodelar el mapeo en el Editor de gráficos. BoneCraft nunca
sobrescribe su curva (ver Edición a continuación).

### Sequence (secuencia)

Registre los pasos para doblar un arma:

1. En **3. Sequences**, haga clic en**Add Sequence**. Hace un mango deslizante.
`CTRL-SEQ-<name>`.
2. Haga clic en **Move Slider to End**. El control deslizante salta hasta su final (1) y el botón
se convierte en Paso de grabación seguido del número del siguiente paso.
3. Coloque los mangos de las articulaciones para el primer paso. Haga clic en Grabar paso 1.
Cada identificador que se movió se convierte en un paso con su valor objetivo, y el
las manijas vuelven a cero.
4. Repita los pasos 2 y 3 para más pasos. Cada nuevo paso ocupa el siguiente cuarto del
control deslizante de forma predeterminada.
5. Establezca **Target**, la facilidad (Lineal, Entrada fácil, Salida fácil, Entrada fácil, Ajuste),
**Start** y**End** para cada paso. Fuera de su corte, un escalón sostiene su extremo.
valor. Se pueden acumular varias secuencias.
6. Haga clic en **Test**: el control deslizante reproduce 0 → 1 → 0.

Al lado del botón de grabación por pasos y **Test**, la secuencia seleccionada tiene**Detach**
(cadena rota) y **Delete** (X). Una secuencia retenida (por ejemplo, un paso cuyo
curva que remodeló) muestra su mensaje y un botón **Restore**. Restaurar
regenera los pasos del registro. Keep mine no se ofrece para una Secuencia.

## Test

**Test** (el botón de reproducción en la lista y en 3. Secuencias) barre uno
mecanismo en toda su extensión y retroceso. No escribe claves y pone la pose.
atrás cuando termine. Presione **Esc** para detenerlo antes; la pose se restablece entonces
también. Para un Gear Link o Follow, barre la fuente. Para un pistón barre el
articulación que lo mueve. Esté atento a las partes que chocan; BoneCraft no detecta
colisiones.

## Formas

En **4. Controls**:

- Cada articulación y secuencia tiene un control deslizante. Es el canal propio del mango, por lo que
arrastrar el controlador y usar el control deslizante son lo mismo.
- **Save Form** registra cada identificador y valor del control deslizante de secuencia bajo un nombre.
Cambie el nombre en la lista.
- **Go to Form** establece cada control en los valores guardados.
- **Go and Key** hace lo mismo y también inserta claves en el fotograma actual.
- El **X** al lado de la lista elimina un formulario.

## Lo que construye BoneCraft

Para cada parte:

|hueso|Trabajo|Visibles|
|---|---|---|
|`CTRL-<part>` |El mango. Su valor es el control deslizante del panel. Sólo la bisagra, la corredera y el telescopio forman uno.|si|
|`MCH-<part>` |Agrega el identificador y cada enlace, luego aplica los límites.|Oculto|
|`DEF-<part>` |Copias `MCH-<part>`. La malla está unida a él. Los motores reciben este hueso.|Oculto|

Los huesos se encuentran en las colecciones `Mechanism Controls`, `Mechanism MCH` y
`Mechanism DEF`. Una parte sin articulación tiene solo huesos `MCH-` y `DEF-`. un
El mango del telescopio es `CTRL-<telescope name>`. Una secuencia es
`CTRL-SEQ-<name>`. Un pistón agrega huesos `MCH-<part>-aim` y `MCH-<part>-target`
para cada una de sus dos partes.

Las restricciones de `MCH-<part>` siempre vienen en el mismo orden: Copiar transformaciones
desde el mango, luego la contribución de cada eslabón, luego la rotación límite de la articulación
o Limitar ubicación. `DEF-<part>` tiene una copia de transformaciones de `MCH-<part>`.

Todo lo que construye BoneCraft está etiquetado con su registro: inicio de nombres de restricciones
con `BC·<id>·<role>`, y los huesos tienen las propiedades `bc_mech_id` y
`bc_mech_role`. BoneCraft encuentra sus huesos por etiqueta, no por nombre, para que usted pueda
cambiar el nombre de cualquier hueso. Una reconstrucción lo encuentra nuevamente y no hace ningún duplicado.

Con Show Helpers activado, cada unión y enlace tiene una nota **How this works**. eso
enumera las restricciones por nombre, dice lo que hace cada una y tiene un **Select**
(un icono de flecha) para inspeccionar el hueso.

Tus propias limitaciones, impulsores y huesos nunca se tocan. Una restricción que agregas
a un hueso MCH se mantiene por debajo del BoneCraft después de una reconstrucción.

## Ediciones y cambios a mano

- **Ediciones de valores** (límites, relación, rangos, sincronización, facilidad, apariencia de manejo) actualizan el
restricciones existentes. No hay reconstrucción.
- **Ediciones estructurales** (un**Kind** de Gear Link, un**Curve** de Follow, un
**Stretch** del pistón) reemplaza las limitaciones de ese mecanismo y reconstruye únicamente
ese mecanismo.
- **Cambiado a mano.** Si edita una restricción BoneCraft (por ejemplo, una
Límite), el mensaje del mecanismo termina con "(cambiado a mano)". BoneCraft nunca sobrescribe
eso en silencio. Elige:
 - **Keep mine** copia sus valores en el registro. Rechaza lo que no puede
Vuelve a leer y dice que uses Restaurar o Separar.
 - **Restore** descarta la edición y la reconstruye a partir del registro.
- Un mecanismo retenido también sostiene todos los mecanismos que utilizan sus huesos, hasta que
resolverlo.
- Una curva reformada es lo mismo. Si reforma una curva de seguimiento (**Curve**
marcado) en el Editor de gráficos y luego cambiar un valor que lo reemplazaría,
como su rango objetivo, el mensaje de seguimiento termina con "(cambiado a mano)". **Keep mine**
Mantiene tu curva. **Restore** lo regenera.
- Una Secuencia retenida muestra su mensaje y **Restore** en**3. Sequences**, con
**Detach** y**Delete** al lado. Keep mine no se ofrece para Secuencias.
- **Detach** (botón de cadena rota) elimina el registro y las etiquetas pero mantiene los huesos y
limitaciones como si fuera su propio equipo hecho a mano. Separar y eliminar ambos rechazan un registro
que utiliza otro registro y nombrar a los usuarios.
- **Delete** (botón X) elimina el registro y todo lo que BoneCraft creó para él.
- Se rechaza un bucle de enlace antes de que se cree algo y se nombra el bucle, por ejemplo.
ejemplo "Bisagra de hoja → Seguimiento de cubierta → Bisagra de hoja haría un bucle".

El Rig Validator y el Task Board informan bucles de enlace, piezas faltantes, DEF
huesos movidos desde fuera de su mecanismo, controladores que necesitan Python y Gear
Enlaces que pierden una Secuencia o Seguimiento. La verificación de nombres del validador acepta
guiones (`CTRL-`, `MCH-`, `DEF-` ), y la verificación de sus controladores advierte solo en
expresiones que necesitan Python, por lo que una rig de Mecanismos limpia no muestra validación
errores: solo la advertencia sobre el hueso `root` que se describe en Límites de esta versión.

## Show Helpers (mostrar ayudas)

**Show Helpers** es una preferencia para todos los BoneCraft:**Preferencias →
Complementos → BoneCraft → Ayudantes**. Off oculta el texto didáctico en todas partes: el qué/cuándo
líneas, las notas **How this works** y las oraciones completas de pasos guiados (aquellas
convertirse en etiquetas cortas). Los pasos en sí, las listas, Test, advertencias y
La información sobre herramientas flotante de Blender siempre permanece.

El botón VRChat **Compact Mode** es su acceso directo: Modo compacto activado significa Mostrar
Ayudantes fuera.

## Límites de esta versión

- Los mecanismos de giro, seguimiento y vinculación vienen más adelante.
- La exportación del motor del movimiento del mecanismo horneado llega más tarde, después de la mano de escritorio.
cheque. Hasta entonces los huesos `DEF-` son los huesos a exportar.
- BoneCraft no detecta colisiones. Utilice Probar y mirar.
- Un Gear Link que gira libremente sigue las manijas y los engranajes únicamente.
- El hueso `root` del rig no se encuentra en ninguna colección de huesos, por lo que el validador del rig
La verificación de colecciones advierte sobre esto y el panel de tareas muestra "Validación de plataforma".
advertencias (1)".

Siguiente: [Herramientas VRChat](08-vrchat.md)
