# Tutorial: Crescent Rose con Mecanismos

[← Contenidos](index.md)

<style>
section.chapter:has(#ch-12-crescent-rose) img {max-width:100%;width:auto;height:auto;}
img.manual-image-70 {max-height:70mm;}
img.manual-image-100 {max-height:100mm;}
img.manual-image-110 {max-height:110mm;}
img.manual-image-115 {max-height:115mm;}
img.manual-image-135 {max-height:135mm;}
img.manual-image-155 {max-height:155mm;}

@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--lo-que-construiste"] { break-before: page; break-after: avoid; }
}
</style>

## que construiras

Crescent Rose es la guadaña que también es un rifle. En este tutorial, equiparás un modelo con mecanismos, de modo que un control deslizante convierta la guadaña en un rifle y un segundo control deslizante pliegue el rifle en su forma compacta. En el camino, utilizas todos los mecanismos de articulación y enlace que tiene hoy en día, excepto Gear Link: ocho bisagras, tres correderas, un telescopio, un pistón y un seguidor, luego dos secuencias y tres formas.

Las formas son poses de enseñanza para este modelo hecho por fans. Los mecanismos no detectan colisiones ni crean una réplica diseñada físicamente: inspeccione los espacios libres al adaptar el rig.

El resultado es el archivo `examples/crescent-rose/CrescentRose_Mechanisms.blend`. Ábrelo en cualquier momento para comparar.

## Antes de empezar

- Los archivos: `examples/crescent-rose/CrescentRose_parts.blend` es el modelo ya dividido en 15 objetos parciales; Comience el tutorial desde allí. `CrescentRose_Mechanisms.blend` es el rig terminado.
- Tiempo: permita una sesión separada para la preparación de FBX y otra para la lección de Mecanismos; Estos son ejercicios sustanciales, no carreras de velocidad cronometradas. Guarde los puntos de control entre etapas.
- Palabras: lea primero "Qué hace los mecanismos" en [Mecanismos](07-mechanisms.md): define parte, unión, vínculo, identificador, secuencia y forma.
- Idioma: las capturas de pantalla muestran Bforartists en inglés con los paneles de BoneCraft en inglés. Los propios paneles de BoneCraft siguen la configuración de **Language** en sus preferencias; el resto de Bforartists sigue el lenguaje de interfaz de Bforartists. Si su Bforartists está en un idioma que BoneCraft no traduce, sus paneles permanecen en inglés y esta edición aún aplica.
- Ruta inicial: use P1-P8 a continuación para el FBX original, o salte al Paso 1 con el archivo preparado. Ambas rutas utilizan las mismas 15 partes.
- Versión: las instrucciones y las capturas de interfaz genuinas se verificaron con BoneCraft `9.1.2` en Bforartists `5.2.0`, usando su mapa de teclas predeterminado.

Las marcas numeradas en rojo identifican en qué hacer clic, escribir o inspeccionar. Siga la tecla de acción numerada de cada imagen en orden (1, luego 2, luego 3). Los números se reinician en cada imagen. Un resultado encuadrado es una marca; una parte o un botón encerrado en un círculo es el objetivo de la interacción.

## Prepare el FBX original (P1-P8)

Omita esta sección si está utilizando `CrescentRose_parts.blend`. Trabaje en un archivo nuevo y mantenga juntos el origen FBX y su carpeta `CrescentRoseTextures`. Estos pasos se reprodujeron en Bforartists 5.2.0 con el mapa de teclas predeterminado. Utilice el menú del modo visible: Tab puede alternar superposiciones en este mapa de teclas en lugar de ingresar al modo de edición.

### P1 - Importar el FBX

Comience con una escena vacía. Elija **File > Import > FBX (.fbx) (Legacy)**, seleccione `CrescentRose.fbx` y deje la escala de importación en `1.00`. Utilice el importador heredado para esta receta. Outliner contiene una raíz y tres mallas de material: `Black01`, `Blades01` y `Red01`. Presione el teclado numérico 3 para ver la derecha y Inicio para enmarcarlos.

![P1: Opciones de importación heredadas de FBX con Scale 1.00](../images/crescent-rose/en/prep-01-import-fbx.png){.manual-image-155}

*1: Seleccione CrescentRose.fbx. 2: Mantenga la escala en 1,00. 3: Haga clic en Importar FBX; utilice el importador heredado.*

### P2: conservar la ubicación y establecer el tamaño

En Modo Objeto, seleccione las tres mallas. Utilice **Object > Parent > Clear and Keep Transformation**. Elimine la raíz que ahora no se utiliza de su escena de trabajo. Con las tres mallas seleccionadas, use**Object > Apply > Rotation & Scale**. El arma importada mide aproximadamente `0.32 m` de alto. Escale los tres juntos con `6.25` (en este mapa de teclas Bforartists, Ctrl+R inicia Escala; escriba 6.25 y confirme), luego aplique Rotación y Escala nuevamente. El arma completa ahora mide aproximadamente `1.997 m` de alto. Haga esto una vez; el atajo preparado ya está escalado.

![P2: crianza clara manteniendo la ubicación](../images/crescent-rose/en/prep-02-unparent-command.png){.manual-image-135}

*1: Presione F3 y busque Borrar transformación de conservación principal. 2: Elija Borrar y mantener transformación. Repita para las tres mallas antes de quitar la raíz.*

![P2: rotación y escala aplicadas en el arma importada.](../images/crescent-rose/en/prep-02-scale.png){.manual-image-115}

*1: Después de escalar las tres mallas juntas en 6,25, aplique Rotación y Escala; La rotación debe indicar 0. 2: la escala debe indicar 1 en todos los ejes.*

El campo Dimensiones de un objeto individual mide solo esa malla de material. Compruebe la extensión combinada de abajo hacia arriba al medir el arma. Los tres objetos deben mostrar rotación cero y escala 1 antes de la separación.

### P3 - Conectar los materiales

Cambie al espacio de trabajo Sombreado y Vista previa de material. Para cada uno de los tres materiales, cargue sus imágenes `BaseColor`, `Metallic`, `Roughness` y `Normal` correspondientes de `CrescentRoseTextures`. Conecte el color de textura de la imagen a la entrada BSDF de principios correspondiente. BaseColor utiliza **sRGB**; Metálico, Rugosidad y Uso Normal `Non-Color`. Para Normal, inserte un nodo**Normal Map**, mantenga `Tangent Space`, conecte el Color de la imagen a su Color y conecte su salida Normal a Principio BSDF Normal. Mantenga los UV existentes.

![P3: cuatro mapas de textura y un mapa normal del espacio tangente conectados para el material negro](../images/crescent-rose/en/prep-03-materials.png){.manual-image-155}

*1: Conecte el color BaseColor al color base BSDF. 2: Mantenga BaseColor en sRGB. 3: Establezca todos los mapas de datos en Sin color. 4: Conecte la imagen Normal > Mapa Normal > BSDF Normal, usando el Espacio Tangente.*

![P3: los tres materiales en Vista previa de materiales](../images/crescent-rose/en/prep-03-shaded.png){.manual-image-155}

*1: Verifique el material de la hoja. 2: Verifique los materiales del cuerpo rojo/negro en Vista previa del material; no faltan texturas rosadas.*

Repita las mismas conexiones para la hoja y los materiales rojos. Verifique el espacio de color de cada imagen después de elegirla; el escenario pertenece a la imagen. El arma debe ser roja, negra y metálica, sin que falten texturas rosas.

### P4 - Separar piezas sueltas

Seleccione las tres mallas de materiales, elija **Edit Mode** en el menú del modo de ventana gráfica, seleccione toda la geometría y luego use**Mesh > Separate > By Loose Parts**. Regrese al modo Objeto. Hay**37** objetos de malla en este punto. Los sufijos numéricos generados pueden variar, así que identifíquelos por posición y forma.

![P4: ingrese al modo de edición y elija por partes sueltas](../images/crescent-rose/en/prep-04-separate-command.png){.manual-image-135}

*1: Cambie al modo de edición y seleccione toda la geometría. 2: Presione F3, busque Separar sueltos y elija Por piezas sueltas.*

![P4: las 37 piezas sueltas tras la separación](../images/crescent-rose/en/prep-04-separate.png){.manual-image-155}

*1: Verifique que el total de objetos sea 37 después de la separación. 2: Utilice el Outliner para seleccionar piezas por forma y ubicación; los sufijos pueden variar.*

### P5 - Únete a los 15 grupos en movimiento

Selecciona las piezas que deben moverse juntas y usa **Object > Join** (Ctrl+J). Cambie el nombre del objeto resultante en el Outliner. Para piezas emparejadas en lados opuestos, orbite la vista para seleccionar ambas; Comprueba la selección antes de unirte. Trabaje desde la punta de la hoja hacia adentro, luego el receptor y el poste. La tabla enumera todas las islas de origen; el nombre de un material describe su apariencia, no el nombre final del objeto.

|Objeto final|Piezas para combinar|Vértices de malla después de unir|
|---|---|---:|
|`BladeTip` |Pomo de unión de punta negra y punta de metal|252|
|`Blade2` |Dos placas metálicas del segundo segmento y dos cubiertas rojas.|1000|
|`Blade1` |Dos placas metálicas del primer segmento más cercanas a la cabeza.|512|
|`HeadMount` |Bloque trasero, tapa superior y núcleo negros; dos placas interiores rojas y dos cubiertas superiores delgadas|1395|
|`PlateL` |Una placa de cabeza exterior roja en X negativo|676|
|`PlateR` |Una placa de cabeza exterior roja en X positivo|676|
|`RearSpike` |Dos hojas de púas de metal, dos tapas de pivote rojas y dos placas de montaje rojas|1194|
|`Receiver` |Cuerpo negro y perilla pequeña, anillo de metal sobre el perno, carcasa roja larga|2609|
|`Grip` |Bloque de agarre rojo debajo del receptor|194|
|`Magazine` |Tubo negro debajo del cuerpo.|96|
|`Bolt` |Cilindro de cerrojo rojo y sus dos pomos.|362|
|`Pole` |Eje inferior de metal y collar rojo.|148|
|`ButtSpike` |Punta inferior de metal|110|
|`StrutBase` |Varilla roja delgada entre el receptor y la cabeza.|34|
|`StrutRod` |Manga negra con muescas alrededor de esa varilla|108|

Debe haber **15 mallas y 9366 vértices** en total. No fusione las placas exteriores en Blade1 ni las dos piezas del puntal. El puntal ya tiene dos piezas separadas; no se necesita ninguna bisección. El paso 2 repite los nombres de las piezas terminadas y su posterior jerarquía de padres.

![P5: los 15 grupos en movimiento nombrados en el Outliner](../images/crescent-rose/en/prep-05-group-parts.png){.manual-image-155}

*1: Cambie el nombre de cada grupo unido en Outliner para que coincida con los 15 nombres de la tabla.*

![P5: las dos placas de origen Blade1 seleccionadas antes de unirse](../images/crescent-rose/en/prep-05-blade1.png){.manual-image-155}

*1: Seleccione las dos placas metálicas Blade1 en lados opuestos. 2: Verifique que ambos objetos estén seleccionados, luego use Unirse y cambie el nombre del resultado Blade1.*

![P5: Comando Unirse al menú Objeto](../images/crescent-rose/en/prep-05-join-command.png){.manual-image-135}

*1: Abrir objeto después de seleccionar solo las piezas de un grupo. 2: Elija Unirse (Ctrl+J). Este recorte de menú identifica el comando; use la selección de dos piezas que se muestra arriba.*

### P6 - Centrar los orígenes

En Modo Objeto, seleccione las 15 mallas. Elija **Object > Set Origin > Origin to Geometry** y establezca la opción Centro de la operación en `Bounds Center`. Verifique la rotación cero y la escala 1. Los objetos aún no tienen padres y no hay armadura. Estos son orígenes de preparación convenientes; Posteriormente, el paso 6 mueve los pivotes del mecanismo a sus uniones reales.

![P6: Objeto > Establecer origen > Origen a geometría](../images/crescent-rose/en/prep-06-origin-command.png){.manual-image-135}

*1: Abrir objeto. 2: Colocar el cursor sobre el origen. 3: Elija Origen a Geometría; configure Bounds Center en las opciones de operación.*

![P6: el origen Blade1 centrado con transformaciones aplicadas](../images/crescent-rose/en/prep-06-origins.png){.manual-image-155}

*1: El origen naranja ahora está centrado en la malla. 2: Confirmar rotación 0. 3: Confirmar escala 1. Los pivotes del mecanismo se mueven más tarde.*

### P7 - Redimensionar y empaquetar las texturas

En el Editor de imágenes selecciona cada uno de los **12 mapas usados** (cuatro por material). Elija**Image > Resize**, establezca el ancho y el alto en**1024**, confirme y luego elija**Image > Pack**. Repita para cada mapa usado. Al empaquetar la imagen redimensionada se conservan esos píxeles dentro de la mezcla; no sobrescriba los archivos JPEG de origen. Verifique la Vista previa del material después.

![P7: Menú de imagen con una textura redimensionada de 1024 por 1024](../images/crescent-rose/en/prep-07-pack-textures.png){.manual-image-155}

*1: Elija Imagen > Cambiar tamaño e ingrese 1024 para ancho y alto. 2: Verifique las dimensiones resultantes de 1024 x 1024. 3: Elige Paquete. Repita lo mismo para los 12 mapas usados.*

### P8: guarde y vuelva a abrir el archivo preparado

Guarde su copia de trabajo como `CrescentRose_parts.blend`. Vuelva a abrirlo y verifique las 15 mallas nombradas, sus transformaciones y los materiales rojo/negro. Los 12 mapas deberían permanecer disponibles sin depender del directorio de texturas original. Use la Vista derecha y Inicio nuevamente, luego continúe con el Paso 1.

![P8: el archivo preparado se reabrió con el arma texturizada intacta](../images/crescent-rose/en/prep-08-save-parts.png){.manual-image-155}

*1: Abra Archivo para Guardar como, luego Abrir para recargar su copia de trabajo. 2: Confirme que las 15 mallas nombradas sobrevivieron. 3: Verificar los materiales; la barra de título identifica el archivo reabierto.*

## A. Abra el archivo

### Paso 1: abra el archivo de piezas

Abra `examples/crescent-rose/CrescentRose_parts.blend`. Cambie la ventana gráfica al sombreado Vista previa del material y presione el teclado numérico 3 para ver la vista Derecha: la hoja apunta hacia la izquierda, la punta apunta hacia abajo. Pulsa Inicio para enmarcar el arma.

![Paso 1: el archivo de piezas en la vista derecha](../images/crescent-rose/en/01-open-file.png){.manual-image-155}

*1: Haga clic en Vista previa del material. 2: Presione el teclado numérico 3 hasta que la vista diga Ortográfica derecha; presiona Inicio para enmarcar el arma.*

**Lo que deberías estar viendo:** La guadaña en rojo y negro, de unos 2 m de altura, sin nada seleccionado.

### Paso 2: conozca las piezas

El Outliner enumera los 15 objetos. Cada una es una pieza que se mueve como un bloque:

|Objeto|que es|Paseos en|
|---|---|---|
|`Receiver` |El cuerpo del rifle con la mira, el gatillo y la mira.|la rig|
|`Grip` |El agarre debajo del receptor.|`Receiver` |
|`Magazine` |El cargador de cilindros|`Receiver` |
|`Bolt` |el perno|`Receiver` |
|`Pole` |El eje inferior y su collar.|`Receiver` |
|`ButtSpike` |El pico en la parte inferior|`Pole` |
|`HeadMount` |El bloque de cabeza del que cuelga la hoja|`Receiver` |
|`Blade1` |El primer segmento de la hoja, más cercano a la cabeza.|`HeadMount` |
|`Blade2` |El segundo segmento|`Blade1` |
|`BladeTip` |la propina|`Blade2` |
|`RearSpike` |La púa en la parte posterior de la cabeza.|`HeadMount` |
|`PlateL`, `PlateR` |Las placas laterales exteriores de la cabeza.|`HeadMount` |
|`StrutBase` |La delgada varilla entre el receptor y el cabezal.|`Receiver` |
|`StrutRod` |La manga con muescas alrededor de esa varilla|`HeadMount` |

![Paso 2: los 15 objetos parciales en el Outliner](../images/crescent-rose/en/02-the-parts.png){.manual-image-155}

*1: Identifique los tres segmentos de la hoja. 2: Relaciona los nombres del cuerpo, la cabeza y el poste con la tabla. 3: Mantenga StrutBase y StrutRod como objetos separados.*

Para el FBX original, siga P1-P8 arriba. El archivo preparado suministrado se creó a través de esas acciones de interfaz; el script de preparación del repositorio proporciona una tabla de agrupación de referencia.

### Paso 3: encontrar mecanismos

Abra la pestaña BoneCraft en el estante de herramientas izquierdo (si está oculto, presione T sobre la ventana gráfica y elija Herramientas en el menú de alternancia de región) y expanda **Mechanisms**. Amplíe el estante arrastrando su borde derecho hasta que el texto del panel tenga espacio. Como alternativa, la misma sección Mecanismos está disponible en**Properties > Scene** cuando Propiedades de escena está configurada en Mostrar en las preferencias de BoneCraft. Las capturas de pantalla utilizan el estante de herramientas. Con una malla activa y sin rig aún, busque**Add Parts from Selection** en la parte superior de la sección. Seleccione todas las partes en el Paso 4 antes de hacer clic en ellas; las subsecciones numeradas se vuelven utilizables después de agregar las partes.

![Paso 3: la sección Mecanismos de la pestaña BoneCraft](../images/crescent-rose/en/03-mechanisms-section.png){.manual-image-155}

*1: Haga clic en la pestaña BoneCraft. 2: Ampliar Mecanismos. 3: Buscar Agregar piezas de la selección; seleccione las mallas antes de usarla.*

## B. Partes

### Paso 4: agregar piezas de la selección

Pase el cursor sobre la ventana gráfica y presione A para seleccionar los 15 objetos. Haga clic en **Add Parts from Selection**.

![Paso 4: todas las piezas seleccionadas, Agregar piezas de la selección](../images/crescent-rose/en/04-add-parts.png){.manual-image-155}

*1: Pase el cursor sobre la ventana gráfica y presione A para seleccionar las 15 mallas. 2: Haga clic en Agregar piezas de la selección.*

**Lo que deberías ver:** Aparece una nueva armadura, "Mechanism Rig", en el Outliner con las piezas debajo. Los objetos de malla permanecen seleccionados después de la operación.**1. Parts** enumera las 15 piezas y la pestaña BoneCraft ahora comienza con la descripción general del rig, que puede contraer.

### Paso 5: sigue adelante

Una pieza se desplaza sobre la pieza a la que está unida. Haga clic en `Blade1` en la lista **1. Parts**, abra el menú "Viajes en" debajo de la lista y elija `HeadMount`. Haga lo mismo con cada pieza de la tabla del paso 2. `Receiver` se queda con "el rig".

![Paso 5: Blade1 se monta en HeadMount](../images/crescent-rose/en/05-rides-on.png){.manual-image-155}

*1: Seleccione Blade1 en la lista de Piezas. 2: Abra Rides on y elija HeadMount. Repita usando la tabla principal.*

### Paso 6: Pivotes

Una bisagra gira alrededor del pivote de su pieza. Los segmentos de la hoja, el cabezal y la empuñadura deben girar en sus articulaciones, no en sus centros. Con `Blade1` seleccionado en la lista, haga clic en **Edit Pivot**, seleccione el marcador, presione Ctrl+W para Mover en Bforartists, haga clic donde el segmento se encuentra con la cabeza y haga clic en**Apply Pivot**. Trabaje en la vista lateral ortográfica para que la posición de pivote lateral permanezca sin cambios. Repita para `Blade2` (donde se encuentra con `Blade1` ), `BladeTip` (donde se encuentra con `Blade2` ), `HeadMount` (su punto más bajo, donde se encuentra el puntal), `Grip` (su borde superior), `RearSpike` (donde se encuentra con la cabeza), `PlateL` y `PlateR` (el centro del perno redondo donde Blade1 se encuentra con la cabeza), `StrutBase` (su parte inferior) y `StrutRod` (su parte superior). La posición del marcador de la captura de pantalla es una guía; unos pocos milímetros no hacen ninguna diferencia visible.

![Paso 6: seleccione la pieza y haga clic en Editar pivote](../images/crescent-rose/en/06-edit-pivot-button.png){.manual-image-135}

*1: Seleccione Blade1 en Piezas. 2: Haga clic en Editar pivote; luego mueva y aplique el marcador como se muestra a continuación.*

![Paso 6: marcador de pivote de Blade1 en la articulación, aplicar pivote](../images/crescent-rose/en/06-edit-pivot.png){.manual-image-155}

*1: Mueva el marcador de pivote a la unión de la hoja con Ctrl+W. 2: Haga clic en Aplicar pivote para mantener esa ubicación.*

## C. La cabeza

### Paso 7: Agregar junta → Bisagra

Abra **Add Joint → Hinge**. Comienza una compilación guiada: el encabezado y la barra de estado le indican qué hacer en cada paso.

![Paso 7: el menú Agregar articulación, Bisagra](../images/crescent-rose/en/07-head-hinge.png){.manual-image-155}

*1: Abrir Agregar junta. 2: Haga clic en Bisagra. La construcción guiada ahora espera una pieza.*

### Paso 8: haz clic en la cabeza

El encabezado dice "haga clic en la parte que gira". En la vista derecha, la placa exterior se encuentra frente a la cabeza, así que haga clic en el bloque trasero de la cabeza, detrás de las placas (el círculo). Si el encabezado nombra `PlateR`, presione Esc, reinicie **Add Joint > Hinge** y haga clic más atrás. Si necesita ocultar una obstrucción, hágalo antes de iniciar la guía. La guía consume atajos de teclado normales mientras está activa.

![Paso 8: haga clic en el bloque trasero del cabezal](../images/crescent-rose/en/08-head-hinge-click.png){.manual-image-155}

*1: Haga clic en el bloque negro trasero de HeadMount, detrás de la placa exterior roja. Consulte los nombres de la guía HeadMount.*

### Paso 9: presione X, luego Enter

El encabezado ahora pregunta por el eje. Presione X: la cabeza gira alrededor del eje lateral y la guía previsualiza el movimiento en un bucle. Presione Enter para conservarlo.

![Paso 9: el paso del eje](../images/crescent-rose/en/09-head-hinge-axis.png){.manual-image-155}

*1: Siga las indicaciones del eje: presione X y luego Intro. 2: Observe cómo la cabeza gira alrededor de su pivote antes de confirmar.*

**Lo que deberías ver:** `HeadMount Hinge` en la lista**2. Joints & Links** y su control deslizante en**4. Controls**. Utilice estos controles deslizantes en el modo Objeto. Para usar los controles óseos de la ventana gráfica, seleccione la armadura y cambie al modo Pose.

### Paso 10: Límites

Con `HeadMount Hinge` seleccionado en la lista, establezca **Min** en 0 y**Max** en 120. Los valores positivos giran la cabeza hacia abajo y hacia atrás. Mantenga el límite de recorrido de 120 grados; La secuencia Rifle utilizará un objetivo de 90 grados junto con las bisagras de la hoja.

![Paso 10: Mín. 0, Máx. 120](../images/crescent-rose/en/10-head-hinge-limits.png){.manual-image-155}

*1: Seleccione Bisagra HeadMount. 2: Establezca Min en 0. 3: Establezca Max en 120; haga doble clic en el número, escriba y presione Entrar.*

### Paso 11: prueba

Haga clic en el botón de reproducción de la fila. La cabeza se mueve a 120° y hacia atrás, y se restablece la postura.

![Paso 11: prueba en la fila de bisagras](../images/crescent-rose/en/11-test-head.png){.manual-image-155}

*1: Haga clic en el pequeño triángulo de juego en la fila de bisagras HeadMount. Mira el barrido y regresa.*

## D. La cadena de cuchillas

### Paso 12: tres bisagras más

Repita los pasos 7 a 10 para `Blade1`, `Blade2` y `BladeTip`: **Add Joint → Hinge**, haga clic en el segmento, X, Intro, luego**Max** 120. Cada segmento se monta sobre el anterior, de modo que las tres bisagras formen una cadena.

![Paso 12: las tres bisagras de segmento de hoja y la bisagra de cabeza separada en la lista](../images/crescent-rose/en/12-blade-hinges.png){.manual-image-155}

*1: Cree y seleccione cada bisagra de hoja: Blade1, Blade2, BladeTip. 2: Establezca Max en 120 para cada uno; use X como eje.*

### Paso 13: prueba la cadena

Contraiga **2. Joints & Links** para hacer espacio y expandir**4. Controls**. En el modo Objeto, configure `Blade1 Hinge`, `Blade2 Hinge` y `BladeTip Hinge` en 60 grados, uno a la vez. Haga doble clic en un campo numérico, presione Ctrl+A, escriba el valor y presione Entrar. Los últimos segmentos se mueven con los anteriores y la cadena se curva. Establezca los tres valores nuevamente en 0 antes de continuar.

![Paso 13: las tres hojas se articulan a 60 grados en Controles](../images/crescent-rose/en/13-blade-chain.png){.manual-image-155}

*1: Ingrese 60 en cada uno de los tres controles deslizantes de las hojas. 2: Verifique que los rizos de la cadena estén juntos. Devuelve los tres controles deslizantes a 0.*

## E. Placas y puntal

### Paso 14: bisagras en las placas.

Agregue una bisagra en `PlateR` de la misma manera, **Max** 30. `PlateL` está oculto detrás de la cabeza en la vista derecha: presione Ctrl+Teclado numérico 3 para la vista izquierda, agregue su bisagra y regrese con el teclado numérico 3.

![Paso 14: Bisagra PlateL y Bisagra PlateR](../images/crescent-rose/en/14-plate-hinges.png){.manual-image-155}

*1: Haga bisagras PlateR y PlateL; utilice la vista lateral opuesta para alcanzar PlateL. 2: establece cada máximo en 30.*

### Paso 15: Agregar enlace → Seguir

Una manija debe mover ambas placas. Antes de comenzar la guía, presione el teclado numérico 1 para ver la vista frontal, seleccione `Blade2` y use F3 > Marco seleccionado para acercar la cabeza. Las dos placas exteriores aparecen en los bordes izquierdo y derecho. Abra **Add Link > Follow**, haga clic en `PlateL` en el borde izquierdo (la parte principal), luego en `PlateR` en el borde derecho (la siguiente parte) y presione Entrar.

![Paso 15: La vista frontal expone ambas placas exteriores para las selecciones Seguir](../images/crescent-rose/en/15-follow.png){.manual-image-155}

*1: Haga clic primero en PlateL, la parte principal. 2: Haga clic en PlateR en segundo lugar, la siguiente parte. Presione Entrar.*

### Paso 16: rangos

Con el nuevo Seguir seleccionado, verifique los valores **Source Range** 0…30 y**Target Range** 0…30 que se completan automáticamente. Cambie el nombre por `PlateR Follow` a**Name**.

![Paso 16: Rango de origen y rango de destino](../images/crescent-rose/en/16-follow-ranges.png){.manual-image-155}

*1: Asigne un nombre al enlace PlateR Seguir. 2: Verifique que el rango de origen sea de 0 a 30. 3: Verifique que el rango de destino sea de 0 a 30.*

### Paso 17: Agregar enlace → Pistón

El puntal debe seguir apuntando entre el receptor y la cabeza mientras la cabeza se pliega. Antes de comenzar la guía, presione el teclado numérico 3 para ver la derecha, seleccione `StrutRod` en el esquema y use F3 > Cuadro seleccionado. Abra **Add Link > Piston**. Establezca primero esta vista cercana; Los atajos de navegación se consumen mientras la guía está activa.

![Paso 17: el menú Agregar enlace, Pistón](../images/crescent-rose/en/17-piston.png){.manual-image-155}

*1: Abra Agregar enlace después de enmarcar StrutRod. 2: Elija pistón; el guía pregunta primero por el cilindro.*

### Paso 18: El cilindro y la varilla.

Primero haga clic en la parte del cilindro: `StrutBase`, la varilla delgada, que se muestra en las muescas del manguito. Luego haga clic en la pieza de la varilla: `StrutRod`, el manguito. Utilice la vista cercana para hacer clic primero en la varilla roja expuesta y luego en la funda negra. Las funciones del cilindro/varilla de la guía describen los extremos del eslabón; Los nombres de los objetos de este modelo describen sus piezas originales. Presione Entrar para aceptar, cambie el nombre del enlace a `Head Strut` y deje desactivado **Stretch**.

**Lo que deberías ver:** Cambia `HeadMount Hinge` en Controles: el puntal sigue, cada parte apuntando a la otra. Restaure el valor a cero.

![Paso 18: la guía del pistón, el cilindro rojo expuesto y luego la manga negra](../images/crescent-rose/en/18-piston-parts.png){.manual-image-100}

*1: Haga clic primero en el StrutBase rojo expuesto. 2: Haga clic en segundo lugar en la funda negra StrutRod. Presione Entrar.*

![Paso 18: Configuración de Head Strut con Stretch off](../images/crescent-rose/en/18-piston-settings.png){.manual-image-70}

*1: Cambie el nombre del enlace Head Strut. 2: Deje Estirar sin marcar; luego pruebe HeadMount Hinge y restaure 0.*

## F. El rifle

### Paso 19: bisagras de agarre y punta trasera

**Add Joint → Hinge** en `Grip`, X, Enter,**Min** 0,**Max** 90. Repita en `RearSpike`, X, Enter,**Min** 0,**Max** 90. Luego seleccione `RearSpike Hinge` en la lista y cambie su `Axis X to -1`, dejando Y y Z en 0. Esto invierte su dirección de plegado para que la punta trasera gire hacia la cabeza plegada en Compacto; mantenga Grip en X positivo. Confirme que tanto `Grip Hinge` como `RearSpike Hinge` aparecen en la lista conjunta. Estos dos controles pliegan la empuñadura y la púa trasera para lograr la forma compacta en el Paso 25.

![Paso 19: Bisagra de agarre, máx. 90](../images/crescent-rose/en/19-grip-hinge.png){.manual-image-110}

*1: Seleccione Bisagra de agarre. 2: Mantenga el eje X en 1, Y y Z en 0. 3: Establezca Max en 90; mantenga Min en 0.*

![Paso 19: Bisagra RearSpike con Axis X -1 y Max 90](../images/crescent-rose/en/19-rear-hinge.png){.manual-image-155}

*1: Seleccione Bisagra con punta trasera. 2: Establezca el Eje X en -1. 3: Establezca Máximo en 90; mantenga Min en 0.*

### Paso 20: Portaobjetos y portaobjetos

**Add Joint → Slide** en `Magazine`, presione Z, Enter,**Max** 0.04. Luego una diapositiva sobre `Bolt`, Z, Enter,**Max** 0.06. Las diapositivas miden en unidades de escena: 0,06 son 6 cm.

![Paso 20: Deslizamiento del cargador, eje Z y Max 0.04](../images/crescent-rose/en/20-slides.png){.manual-image-155}

*1: Seleccione Diapositiva de revista después de Agregar articulación > Diapositiva. 2: Utilice el eje Z (Z = 1, X = Y = 0). 3: Establezca Máximo en 0,04; mantenga Min en 0.*

![Paso 20: Deslizamiento del perno, eje Z y máx. 0,06](../images/crescent-rose/en/20-bolt-slide.png){.manual-image-155}

*1: Seleccione Corredera de perno después de Agregar junta > Corredera. 2: Utilice el eje Z (Z = 1, X = Y = 0). 3: Establezca Máx. en 0,06; mantenga Min en 0.*

### Paso 21: Deslizamiento del poste

Una diapositiva sobre `Pole`, Z, Enter, **Max** 0.6. Los valores positivos mueven el poste hacia el receptor. Configure `Pole Slide` en 0,6 en**4. Controls** para ver el eje retraerse y luego restablezcalo a cero.

![Paso 21: Configuración de Pole Slide, eje Z y Max 0,6](../images/crescent-rose/en/21-pole-slide.png){.manual-image-155}

*1: Seleccione Deslizamiento de poste después de Agregar junta > Deslizar. 2: Utilice el eje Z (Z = 1, X = Y = 0). 3: Establezca Máximo en 0,6; mantenga Min en 0.*

### Paso 22: Telescopio polar

**Add Joint → Telescope**. Haga clic en `Pole` (la base), luego en `ButtSpike` (el segmento), presione Enter, presione Z, presione Enter. Conjunto**Length** 0.2. Su control independiente mueve la púa hasta 20 cm a lo largo de Z positiva, dentro del poste en este modelo. Pruébelo y restablezca cero.

![Paso 22: selecciones telescópicas guiadas, poste como base y ButtSpike como segmento](../images/crescent-rose/en/22-telescope-pick.png){.manual-image-155}

*1: Haga clic en Polo como base. 2: Haga clic en ButtSpike como su segmento. Presione Enter, luego Z, luego Enter.*

![Paso 22: Configuración del telescopio polar, eje Z y longitud 0,2](../images/crescent-rose/en/22-telescope.png){.manual-image-155}

*1: Seleccione Telescopio polar. 2: Verifique que Z sea su eje. 3: Introduzca Longitud 0,2; Pruebe el control y restablezca el cero.*

## G. Secuencias

### Paso 23: Agregar secuencia

En **3. Sequences**, haga clic en**Add Sequence** y haga doble clic en su nombre en la lista para cambiarle el nombre a `Scythe to Rifle`. Presione Entrar.

![Paso 23: agregar secuencia](../images/crescent-rose/en/23-add-sequence.png){.manual-image-155}

*1: Haga clic en Agregar secuencia. 2: Haz doble clic en el nuevo nombre y escribe Scythe to Rifle. Presione Entrar.*

### Paso 24: graba un grupo de movimiento

Haga clic en **Move Slider to End**: el control deslizante de la secuencia salta a `100%` y el botón se convierte en Grabar paso 1. Ahora coloque el primer grupo de movimiento con los controles deslizantes en**4. Controls**: `BladeTip Hinge` 70 y `Blade2 Hinge` 120. Haga clic en Grabar paso 1. Esto almacena dos entradas de destino, una para cada movimiento. manejar, y restablece esos dos controles deslizantes conjuntos a cero.

![Paso 24: Mueva el control deslizante hasta el final antes de presentar el primer grupo](../images/crescent-rose/en/24-capture-step.png){.manual-image-155}

*1: Haga clic en Mover control deslizante para finalizar una vez. El botón cambia al Paso de grabación 1.*

![Paso 24: Grabe el paso 1 con Blade2 a 120 y BladeTip a 70 grados](../images/crescent-rose/en/24-record-step.png){.manual-image-155}

*1: Ingrese Blade2 = 120 y BladeTip = 70. 2: Haga clic en Grabar paso 1; Ambos objetivos se almacenan y los controles deslizantes de las articulaciones se reinician.*

*Grupos de movimiento restantes.* La grabación permanece armada después de cada captura. Coloque el siguiente grupo y haga clic en el botón Grabar paso que se muestra; no lo vuelvas a armar:

|grupo de movimiento|Posiciona estas manijas|Botón de grabación después de los grupos anteriores.|
|---|---|---|
|2|`Blade1 Hinge` 10 y `PlateL Hinge` 30|Grabar paso 3|
|3|`HeadMount Hinge` 90|Grabar el paso 5|
|4|`Pole Slide` 0.6|Grabar el paso 6|

El número del botón es el número de entradas de destino almacenadas más uno. Grabar dos manijas lo avanza dos; no cuenta los clics de grabación. Por lo tanto, los cuatro grupos de movimientos anteriores producen seis entradas de objetivos. Si cambia qué manijas se mueven, use el número que realmente se muestra.

### Paso 25 - Los pasos

Cada objetivo grabado tiene su propia entrada debajo de la secuencia, mostrando su **Target**, su facilidad y su**Start** y**End** en el control deslizante. Asigne a ambas entradas en cada grupo de movimiento el mismo inicio y final: la hoja se pliega primero (0…0,25), las placas y el primer segmento a continuación (0,25…0,5), la cabeza en tercer lugar (0,5…0,8) y el poste al final (0,8…1). Antes de su corte, un paso permanece en su valor inicial; después de su corte mantiene su valor final. Los campos Inicio/Fin usan 0-1, mientras que los controles deslizantes muestran 0-100%.

Mantenga cada entrada en `Ease In Out`. Luego agregue una segunda secuencia, `Rifle to Compact`: primer registro `Grip Hinge` 90 y `RearSpike Hinge` 90 (dos entradas, ambas 0…0,5); luego registre `Magazine Slide` 0.04 y `Bolt Slide` 0.06 (dos entradas, ambas 0.5…1). Su botón de grabación cambia del Paso de grabación 1 al Paso de grabación 3 para el segundo grupo. Una vez completada cada secuencia, haga clic en **Cancel** en el banner de captura. Esto finaliza la grabación, conserva las entradas almacenadas y devuelve el control deslizante de secuencia a cero. Una advertencia de superposición mientras está armado describe el siguiente intervalo de grabación propuesto; no agregue un grupo vacío adicional.

![Paso 25: los seis objetivos y intervalos de tiempo en Scythe to Rifle](../images/crescent-rose/en/25-sequence-steps.png){.manual-image-155}

*1: El objetivo es el valor conjunto registrado. 2: Elija Facilitar la entrada y salida. 3: Ingrese a Inicio. 4: Introduzca Fin. Repita estos campos para las seis entradas usando los valores mostrados.*

![Paso 25: los cuatro objetivos y intervalos de tiempo en Rifle to Compact](../images/crescent-rose/en/25-compact-steps.png){.manual-image-155}

*1: Grip y RearSpike utilizan Target 90, Inicio 0, Final 0,5. 2: Uso del cargador y del perno 0,04/0,06, inicio 0,5, final 1. Mantenga la facilidad de entrada y salida.*

![Paso 25: finalice la grabación con Cancelar en el banner de captura](../images/crescent-rose/en/25-cancel-capture.png){.manual-image-135}

*1: Después de finalizar una secuencia, haga clic en Cancelar en este banner de captura para finalizar la grabación. Esto mantiene las entradas y devuelve la secuencia a cero.*

### Paso 26: prueba la secuencia

Haga clic en **Test** junto al botón de grabación de pasos. El control deslizante recorre del 0% al 100% y al 0% y luego restaura su valor anterior a la prueba. Prueba `Scythe to Rifle` de Scythe; Pruebe `Rifle to Compact` con la primera secuencia al 100%. Devuelva ambos al 0% después.

![Paso 26: la secuencia del botón Probar durante el plegado](../images/crescent-rose/en/26-sequence-test.png){.manual-image-155}

*1: Haga clic en Probar junto al botón de grabación. 2: Mira el pliegue y regresa. Prueba Compacto con guadaña a rifle al 100 %.*

**Lo que deberías ver:** La hoja se curva, las placas se cierran, el cabezal se pliega hacia abajo a lo largo del receptor y el poste se desliza hacia arriba. Entonces todo vuelve.

## H. Formularios

### Paso 27: Guardar formulario

En **4. Controls**, con cada control deslizante en 0, haga clic en**Save Form**, luego haga doble clic en la nueva entrada de la lista para nombrarla `Scythe`. Establezca `Scythe to Rifle` en `100%` y guarde/nombre `Rifle`. Configure `Rifle to Compact` en `100%` también y guarde/nombre `Compact`. Deje todos los controles deslizantes de las articulaciones individuales en cero: las secuencias proporcionan su movimiento. Poner la secuencia seleccionada al final puede activar la grabación nuevamente; guardar un formulario no registra otro paso. Al elegir `Scythe` y**Go to Form**, ambas secuencias se devuelven a cero y se borra el estado armado. Ir a Rifle o Compact puede activar la grabación nuevamente porque la secuencia seleccionada está al 100%; no haga clic en Grabar paso a menos que desee agregar otro objetivo.

![Paso 27: guarde el formulario con cada control deslizante en 0](../images/crescent-rose/en/27-save-form.png){.manual-image-155}

*1: Comience con ambas secuencias y cada unión en 0. 2: Haga clic en Guardar formulario. 3: Haga doble clic en la nueva entrada de la lista y asígnele el nombre Scythe; repita para Rifle y Compact.*

### Paso 28: Ir al formulario

Haga clic en un formulario de la lista y haga clic en **Go to Form**.**Go and Key** hace lo mismo y teclea todos los controles en el fotograma actual, que es como animas la transformación.

![Paso 28: Rifle seleccionado, Ir al formulario](../images/crescent-rose/en/28-go-to-form.png){.manual-image-155}

*1: Seleccione el formulario guardado. 2: Haga clic en Ir al formulario. Go and Key también inserta claves de animación.*

### Paso 29 - El rifle

![Paso 29: el formulario Rifle](../images/crescent-rose/en/29-result-rifle.png){.manual-image-155}

*1: Seleccione Rifle. 2: Haga clic en Ir al formulario. 3: Compara los porcentajes de la secuencia con la pose de la imagen.*

### Paso 30: Compacto

![Paso 30: el formulario compacto](../images/crescent-rose/en/30-result-compact.png){.manual-image-155}

*1: Seleccione Compacto. 2: Haga clic en Ir al formulario. 3: Compara los porcentajes de la secuencia con la pose de la imagen.*

Vuelva a `Scythe` y guarde el archivo.

## lo que construiste

|Registro|huesos|que hace|
|---|---|---|
|15 partes|`MCH-<part>` y `DEF-<part>` |La malla de cada parte está relacionada con su hueso `DEF-`.|
|8 bisagras, 3 correderas, 1 telescopio|`CTRL-<part>` |Las manijas; sus valores son los controles deslizantes en **4. Controls** |
|1 pistón|`MCH-<part>-aim` y `MCH-<part>-target` |Mantenga las dos partes del puntal apuntadas entre sí.|
|1 seguir|ninguno|`PlateR` gira con `PlateL` |
|2 secuencias|`CTRL-SEQ-<name>` |Un control deslizante cada uno|
|3 formas|ninguno|Valores del control deslizante guardados|

El ejemplo actualizado pasó el Rig Validator sin reportar problemas. También pasó las comprobaciones de recarga con la ejecución automática de scripts de Python desactivada, incluidos cada control individual y los tres formularios.

## Intente siguiente

- Marque **Curve** en `PlateR Follow` y cambie la forma del mapeo en el Editor de gráficos.
- Guarde una cuarta forma, `Carry`, con la hoja doblada pero la cabeza hacia arriba.
- Introduzca los formularios sobre marcos con **Go and Key**, luego exporte los huesos `DEF-` (consulte [Herramientas VRChat](08-vrchat.md) ).

## Enlace de engranaje

Crescent Rose no tiene par de engranajes, por lo que este rig no tiene Gear Link. Un Gear Link hace girar una bisagra cuando otra gira, mediante una relación de dientes: una manivela y una rueda, o una cremallera que convierte la rotación en una corredera. Ver [Enlace de engranaje](07-mechanisms.md#gear-link-enlace-de-engranaje).

## Créditos

Modelo Crescent Rose de amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0; dividido en partes, escalado y manipulado para este tutorial. Crescent Rose es un diseño de Rooster Teeth Productions; Este es un recurso tutorial creado por fans.

[← Contenidos](index.md)
