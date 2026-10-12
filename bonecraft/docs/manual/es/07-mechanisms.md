# Mechanisms (mecanismos)

[← Índice](index.md)

## Qué hace Mechanisms

Mechanisms convierte piezas hard-surface en un rig mecánico que funciona: bisagras, deslizadores, telescopios, pistones, engranajes, seguidores y transformaciones completas reproducidas con un solo deslizador. Construye huesos y restricciones normales de Blender, así que puedes ver y cambiar todo lo que crea, y el rig funciona en Blender sin scripts. Los motores de juego reciben los huesos `DEF-`. La exportación a motores del movimiento horneado de los mecanismos llegará más adelante (consulta Límites de esta versión).

BoneCraft aporta las herramientas, no un arma. Las piezas las pones tú.

Palabras usadas en los paneles y en esta página:

| Palabra | Significado |
|---|---|
| *Pieza* (Part) | Un elemento que se mueve como un bloque sólido: un objeto, o un trozo suelto de una malla. Una pieza puede ir montada sobre otra pieza. |
| *Articulación* (Joint) | Cómo puede moverse una pieza: Hinge (gira), Slide (se desplaza), Telescope (extiende segmentos encajados). |
| *Enlace* (Link) | Lo que mueve una pieza por ti: Piston, Gear Link, Follow. |
| *Asa* (Handle) | El hueso que arrastras en la vista. Cada articulación tiene una. Su valor también es un deslizador del panel. |
| *Secuencia* (Sequence) | Una transformación reproducida por un solo deslizador, hecha de pasos. |
| *Forma* (Form) | Un conjunto guardado de valores de asas y secuencias, como «Stowed» (recogido) o «Rifle» (fusil). |

## Dónde está

- **Pestaña BoneCraft → Mechanisms** en la vista 3D. La pestaña BoneCraft está en la Tool Shelf izquierda (pulsa **T**), salvo que la hayas movido a la barra lateral derecha (**N**) en las Preferencias. Está entre Malla y Revisión. Se muestra cuando una malla está activa (para empezar un rig) o cuando está activa una armadura con mecanismos.
- **Editor de Propiedades → pestaña Escena → Mechanisms**, justo después del Constructor de Rig. Siempre está ahí. Sin nada utilizable seleccionado, muestra una línea: «Select a mesh to start, or an armature with mechanisms.» (selecciona una malla para empezar, o una armadura con mecanismos). Desactivar la pestaña BoneCraft de la vista no lo quita. Solo el interruptor de herramienta `mechanisms` (**Preferencias → Complementos → BoneCraft → Herramientas**) lo quita, junto con la copia de la vista. Las secciones de la pestaña Escena empiezan plegadas, así que haz clic en **Mechanisms** para desplegarlo.

Dentro de Mechanisms hay cuatro subsecciones: **1. Parts** (piezas), **2. Joints & Links** (articulaciones y enlaces), **3. Sequences** (secuencias) y **4. Controls** (controles). Aparecen en cuanto el rig tiene piezas. Antes de eso solo ves **Add Parts from Selection** (añadir piezas desde la selección).

Cada botón es un paso de deshacer. Si una construcción falla, todo lo que cambió se restablece y el panel muestra el motivo.

## Piezas

1. Selecciona los objetos de las piezas (o una malla hecha de trozos sueltos) en Modo Objeto.
2. Haz clic en **Add Parts from Selection**.
   - Varios objetos: una pieza por objeto. Cada objeto queda emparentado al hueso de su pieza y se queda donde está.
   - Una malla con trozos sueltos: una pieza por trozo. Cada trozo recibe un grupo de vértices para su hueso y la malla recibe un modificador Armadura.
   - La primera vez, BoneCraft crea el rig (una armadura) por ti.
3. Selecciona una pieza de la lista para editarla.

Para cada pieza:

- **Rides on:** (va montada en): elige la pieza con la que se mueve esta. Una pieza hija sigue a su pieza padre. «the rig» significa que va montada en la raíz del rig.
- **Size** (tamaño) fija la longitud del hueso, que fija el tamaño del asa.
- **Edit Pivot** (editar pivote) pone un marcador en la pieza. Arrástralo hasta donde la pieza debe girar o deslizarse y haz clic en **Apply Pivot** (aplicar pivote). Los huesos de la pieza se mueven ahí y el objeto se queda en su sitio.
- **Apply Transforms** (aplicar transformaciones) aparece cuando una pieza de objeto tiene rotación o escala sin aplicar. Haz clic en él. Las transformaciones sin aplicar inclinan los ejes.
- El botón **X** quita la pieza. Se niega mientras una articulación, un enlace u otra pieza la use, y los nombra.
- **Merge for VRChat** (combinar para VRChat; dos o más piezas de objeto) une las piezas de objeto en una malla, con un grupo de vértices por objeto anterior y un modificador Armadura. Hazlo al final. Las piezas unidas pasan a ser trozos sueltos de esa malla. Elimina cada grupo de vértices con el nombre de un hueso de esta armadura (salvo el hueso `DEF-` propio de la pieza), así que combina solo piezas que tengan rig únicamente con el rig de mecanismos.

Puedes renombrar el objeto de una pieza: las piezas están etiquetadas en sus objetos, así que la pieza vuelve a encontrar su objeto. Una copia del objeto (Mayús+D) no se queda con la pieza. Si se borra el objeto de una pieza, la pieza muestra «Part '<name>' is missing» (falta la pieza '<name>') con **Reassign** (reasignar) y **Eliminar**. Los demás mecanismos siguen funcionando.

- **Reassign** usa la malla que tengas seleccionada. Rechaza lo que no sea una malla y un objeto que ya use otra pieza de objeto. Los trozos sueltos de una misma malla pueden compartir esa malla.
- **Eliminar** quita la pieza (consulta Ediciones y cambios a mano, más abajo, para cuándo se rechaza).

## Articulaciones y enlaces, un ejemplo de cada

Añade una articulación con **Add Joint** (añadir articulación) y un enlace con **Add Link** (añadir enlace). Cada opción inicia una construcción guiada. Funcionan desde la pestaña de la vista y desde la pestaña Escena del editor de Propiedades; desde la pestaña Escena, la guía usa la vista 3D más grande de la pantalla. Reglas breves para toda construcción guiada:

- Haz clic en las piezas en la vista. Las piezas pulsadas reciben un contorno y un número.
- Cuando un paso necesita un eje, pulsa **X**, **Y** o **Z**, o **A** para alinearlo con la selección. **Align to Selection** (alinear con la selección) sirve para bisagras inclinadas. Necesita que la malla de la pieza siga en Modo Edición con una arista o una cara seleccionada cuando pulsas **A**, y la guía ignora **Tab**. Así que entra primero en Modo Edición en la malla de la pieza y selecciona una arista o una cara. Sigue en Modo Edición, inicia **Add Joint → Hinge**, haz clic en la pieza y pulsa **A**. Si no hay nada utilizable seleccionado, la guía te lo dice y puedes pulsar otra tecla.
- El último paso previsualiza el mecanismo moviéndose en bucle. **Intro** lo conserva. **Esc** lo quita.
- La cabecera y la barra de estado muestran una frase completa en cada paso. Con Show Helpers (mostrar ayudas) desactivado muestran una etiqueta corta.

Cada fila de la lista Joints & Links tiene cuatro botones de icono: **Test** (triángulo de reproducción), **Editar** (lápiz, muestra los ajustes), **Detach** (separar; cadena rota) y **Eliminar** (X).

Tras la construcción, el elemento seleccionado de la lista solo muestra los ajustes que usa su tipo.

### Hinge (bisagra)

Hinge de cuchilla, 0°…90°:

1. Add Parts from Selection con una pieza Blade (cuchilla).
2. **Add Joint → Hinge**. Haz clic en Blade. Pulsa **X**. Pulsa **Intro**.
3. Obtienes un asa semicircular, `CTRL-Blade`, y una *Blade Hinge* en la lista. Pon **Min** en 0 y **Max** en 90 (en ° para una Hinge).
4. Pruébalo: arrastra el asa semicircular. Se detiene en 90°. **Set Min** (fijar mín.) y **Set Max** (fijar máx.) copian la pose actual del asa en los límites.

Un límite menor que una vuelta completa debe quedar dentro de −180°…180°. Límites como 170°…190° se rechazan con un mensaje. Un rango de una vuelta completa o más (por ejemplo −180°…180°) gira libremente sin límite.

### Slide (deslizador)

Slide de cañón, 0…0.3:

1. **Add Joint → Slide**. Haz clic en la pieza Barrel (cañón). Pulsa **Y**. Pulsa **Intro**.
2. Obtienes un asa de flecha. Pon **Min** en 0 y **Max** en 0.3 (unidades de la escena).
3. Pruébalo: arrastra la flecha. El cañón se desliza y se detiene en 0.3.

### Telescope (telescopio)

Mástil con tres segmentos:

1. Crea la base y tres piezas de segmento.
2. **Add Joint → Telescope**. Haz clic en la base. Haz clic en cada segmento desde la base hacia fuera. Pulsa **Intro**. Pulsa la tecla del eje. Pulsa **Intro** para conservarlo.
3. Obtienes un asa de flecha en la base. **Length** (longitud) es el recorrido total; **Shares (empty = even)** (partes; vacío = iguales) lo reparte entre los segmentos. Para probar partes personalizadas, pon primero **Length** en 1 y escribe `0.5, 0.25, 0.25`. Las partes deben sumar la Length, para que la punta recorra toda la longitud. Un error de escritura (por ejemplo `0.5, abc`) se rechaza con el mismo mensaje sencillo: las partes deben ser números, uno por segmento, que sumen la Length.
4. Pruébalo: arrastra la única flecha. Los tres segmentos se extienden según sus partes. **Set Max** fija la Length a partir de la pose del asa.

### Piston (pistón)

Elevador: cilindro en el bastidor, vástago en el brazo.

1. Da primero una Hinge al brazo y haz que el brazo vaya montado en el bastidor.
2. **Add Link → Piston**. Haz clic en la pieza del cilindro (en el bastidor). Haz clic en la pieza del vástago (en el brazo).
3. Obtienes un Piston sin asa. Cada pieza apunta al punto de anclaje de la otra. **Estirar** (opcional) estira el vástago, para muelles y cables.
4. Pruébalo: mueve el asa del brazo. El pistón la sigue. Si todavía nada mueve el Piston, la construcción funciona pero no hay vista previa, y **Test** lo indica.

### Gear Link (enlace de engranaje)

Engranaje 20:40:

1. Ambas piezas necesitan antes una articulación. La pieza conductora necesita una Hinge. Para Gear y Belt, la pieza conducida necesita una Hinge; para Rack, una Slide.
2. **Add Link → Gear Link**. Haz clic en la pieza conductora. Haz clic en la pieza conducida.
3. En sus ajustes, pon **Source Teeth** (dientes de origen) en 20 y **Target Teeth** (dientes de destino) en 40 (o escribe un **Ratio**). **Kind** (tipo) es Gear, Belt o Rack. **Reverse** (invertir) invierte el sentido.
4. Pruébalo: gira el origen. Con **Kind** en Gear, el destino gira −0.5× lo mismo (+0.5× con Belt). Un Gear invierte el sentido, un Belt lo mantiene y un Rack convierte la rotación en desplazamiento (distancia por radián = **Ratio** × **Pinion Radius** (radio del piñón)).

Cómo lo construye BoneCraft depende del rango de la Hinge de origen:

- Menos de una vuelta completa: una restricción Transformación. Sigue todo lo que mueve el origen, secuencias incluidas.
- Una vuelta completa o más: un driver que no necesita Python. El destino gira sin fin con el origen. Solo sigue asas y engranajes. El Validador de Rig avisa cuando se perdería una secuencia o un Follow.

### Follow (seguidor)

Blade 0–90° levanta Cover (tapa) 0–40°:

1. Ambas piezas necesitan una Hinge o una Slide. Una Hinge de origen necesita límites menores que una vuelta completa; un origen que gira libremente se rechaza.
2. **Add Link → Follow**. Haz clic en la pieza que lidera (Blade). Haz clic en la pieza que sigue (Cover).
3. Los rangos empiezan como el rango completo de cada articulación. Pon **Source Range** (rango de origen) en 0…90 y **Target Range** (rango de destino) en 0…40. Más allá de cualquiera de los extremos, el destino se queda quieto.
4. Pruébalo: mueve el asa de Blade. Cover la sigue.
5. Marca **Curve** (curva) para remodelar la correspondencia en el editor de gráficos. BoneCraft nunca sobrescribe tu curva (consulta Ediciones y cambios a mano, más abajo).

### Sequence (secuencia)

Capture Step para plegar un arma:

1. En **3. Sequences**, haz clic en **Add Sequence** (añadir secuencia). Crea un asa de deslizador `CTRL-SEQ-<name>`.
2. Haz clic en **Capture Step** (capturar paso). El deslizador salta a su final (1).
3. Posa las asas de las articulaciones para el primer paso. Haz clic de nuevo en **Capture Step**. Cada asa que se haya movido se convierte en un paso con su valor objetivo, y las asas vuelven a cero.
4. Repite el paso 3 para más pasos. Cada paso nuevo ocupa por defecto el siguiente cuarto del deslizador.
5. Ajusta el **Destino**, la suavización (Linear, Ease In, Ease Out, Ease In Out, Snap), **Iniciar** y **End** (fin) de cada paso. Fuera de su tramo, un paso mantiene su valor final. Se pueden apilar varias secuencias.
6. Haz clic en **Test**: el deslizador reproduce 0 → 1 → 0.

Junto a **Capture Step** y **Test**, la secuencia seleccionada tiene **Detach** (cadena rota) y **Eliminar** (X). Una secuencia retenida (por ejemplo un paso cuya curva remodelaste) muestra su mensaje y un botón **Restaurar**. Restaurar regenera los pasos a partir del registro. Keep mine (conservar lo mío) no se ofrece para una secuencia.

## Test

**Test** (el botón de reproducción de la lista, y en 3. Sequences) recorre un mecanismo por todo su rango, ida y vuelta. No escribe claves y restablece la pose al terminar. Pulsa **Esc** para detenerlo antes; la pose también se restablece entonces. En un Gear Link o un Follow recorre el origen. En un Piston recorre la articulación que lo mueve. Vigila las piezas que choquen; BoneCraft no detecta colisiones.

## Formas

En **4. Controls**:

- Cada articulación y cada secuencia tiene un deslizador. Es el canal propio del asa, así que arrastrar el asa y usar el deslizador son lo mismo.
- **Save Form** (guardar forma) guarda con un nombre el valor de cada asa y de cada deslizador de secuencia. Renómbrala en la lista.
- **Go to Form** (ir a la forma) pone cada control en los valores guardados.
- **Go and Key** (ir y poner clave) hace lo mismo y además inserta claves en el fotograma actual.
- La **X** junto a la lista quita una forma.

## Lo que construye BoneCraft

Para cada pieza:

| Hueso | Función | Visible |
|---|---|---|
| `CTRL-<part>` | El asa. Su valor es el deslizador del panel. Solo Hinge, Slide y Telescope la crean. | Sí |
| `MCH-<part>` | Suma el asa y cada enlace y luego aplica los límites. | Oculto |
| `DEF-<part>` | Copia `MCH-<part>`. La malla está vinculada a él. Los motores reciben este hueso. | Oculto |

Los huesos están en las colecciones `Mechanism Controls`, `Mechanism MCH` y `Mechanism DEF`. Una pieza sin articulación solo tiene huesos `MCH-` y `DEF-`. El asa de un Telescope es `CTRL-<telescope name>`. La de una secuencia es `CTRL-SEQ-<name>`. Un Piston añade huesos `MCH-<part>-aim` y `MCH-<part>-target` para cada una de sus dos piezas.

Las restricciones de `MCH-<part>` siempre van en el mismo orden: Copiar transformaciones del asa, luego la contribución de cada enlace, luego el Límite de rotación o el Límite de posición de la articulación. `DEF-<part>` tiene una Copiar transformaciones desde `MCH-<part>`.

Todo lo que construye BoneCraft está etiquetado con su registro: los nombres de las restricciones empiezan por `BC·<id>·<role>`, y los huesos llevan las propiedades `bc_mech_id` y `bc_mech_role`. BoneCraft encuentra sus huesos por etiqueta, no por nombre, así que puedes renombrar cualquier hueso. Una reconstrucción lo vuelve a encontrar y no crea duplicados.

Con Show Helpers activado, cada articulación y cada enlace tiene una nota **How this works** (cómo funciona). Enumera las restricciones por nombre, dice qué hace cada una y tiene un botón **Seleccionar** (icono de flecha) para inspeccionar el hueso.

Tus propias restricciones, drivers y huesos nunca se tocan. Una restricción que añadas a un hueso MCH se queda debajo de las de BoneCraft tras una reconstrucción.

## Ediciones y cambios a mano

- Las **Value edits** (ediciones de valores: límites, ratio, rangos, tiempos, suavización, aspecto del asa) actualizan las restricciones existentes en su sitio. No hay reconstrucción.
- Las **Structural edits** (ediciones de estructura: el **Kind** de un Gear Link, la **Curve** de un Follow, el **Estirar** de un Piston) sustituyen las restricciones de ese mecanismo y solo reconstruyen ese mecanismo.
- **Changed by hand.** (cambiado a mano) Si editas una restricción de BoneCraft (por ejemplo un Límite), el mensaje del mecanismo termina en «(changed by hand)». BoneCraft nunca lo sobrescribe en silencio. Elige:
  - **Keep mine** (conservar lo mío) copia tus valores en el registro. Rechaza lo que no puede volver a leer y te dice que uses Restaurar o Detach.
  - **Restaurar** descarta tu edición y reconstruye a partir del registro.
- Un mecanismo retenido también retiene cada mecanismo que usa sus huesos, hasta que lo resuelvas.
- Una curva remodelada funciona igual. Si remodelas la curva de un Follow (**Curve** marcada) en el editor de gráficos y luego cambias un valor que la sustituiría, como su Target Range, el mensaje del Follow termina en «(changed by hand)». **Keep mine** conserva tu curva. **Restaurar** la regenera.
- Una secuencia retenida muestra su mensaje y **Restaurar** en **3. Sequences**, con **Detach** y **Eliminar** al lado. Keep mine no se ofrece para secuencias.
- **Detach** (botón de cadena rota) borra el registro y las etiquetas pero conserva los huesos y las restricciones como tu propio rig hecho a mano. Detach y Eliminar rechazan ambos un registro que otro registro usa, y nombran a quienes lo usan.
- **Eliminar** (botón X) quita el registro y todo lo que BoneCraft construyó para él.
- Un bucle de enlaces se rechaza antes de construir nada, y se nombra el bucle, por ejemplo «Blade Hinge → Cover Follow → Blade Hinge would loop.» (formaría un bucle)

El Validador de Rig y el Tablero de Tareas informan de bucles de enlaces, piezas que faltan, huesos DEF movidos desde fuera de su mecanismo, drivers que necesitan Python y Gear Links que pierden una secuencia o un Follow. La comprobación de nombres del validador acepta guiones (`CTRL-`, `MCH-`, `DEF-`), y su comprobación de drivers solo avisa en expresiones que necesitan Python, así que un rig de Mechanisms limpio no muestra errores de validación: solo el aviso único sobre el hueso `root` descrito en Límites de esta versión.

## Show Helpers (mostrar ayudas)

**Show Helpers** es una sola preferencia para todo BoneCraft: **Preferencias → Complementos → BoneCraft → Helpers**. Desactivada oculta el texto didáctico en todas partes: las líneas qué / cuándo, las notas **How this works** y las frases completas de los pasos guiados (que se convierten en etiquetas cortas). Los propios pasos, las listas, Test, los avisos y las descripciones emergentes de Blender siempre se quedan.

El botón **Modo Compacto** de VRChat es su atajo: Modo Compacto activado significa Show Helpers desactivado.

## Límites de esta versión

- Los mecanismos Click Turn, Track y Linkage llegarán más adelante.
- La exportación a motores del movimiento horneado de los mecanismos llegará más adelante, tras la comprobación a mano en escritorio. Hasta entonces, los huesos `DEF-` son los que hay que exportar.
- BoneCraft no detecta colisiones. Usa Test y mira.
- Un Gear Link que gira libremente solo sigue asas y engranajes.
- El hueso `root` del rig no está en ninguna colección de huesos, así que la comprobación de colecciones del Validador de Rig avisa sobre él y el Tablero de Tareas muestra «Rig validation warnings (1)» (avisos de validación del rig (1)).

Siguiente: [Herramientas de VRChat](08-vrchat.md)
