# Tutorial: Crescent Rose con Mechanisms

[← Índice](index.md)

<style>
@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--qué-construiste"] { break-before: page; break-after: avoid; }
}
</style>

## Qué construirás

Crescent Rose es una guadaña que también es un rifle. Crearás su rig con Mechanisms: un deslizador transforma la guadaña en rifle y otro lo pliega a su forma compacta. Usaremos todos los tipos actuales salvo Gear Link: ocho Hinges, tres Slides, un Telescope, un Piston y un Follow, además de dos Sequences y tres Forms.

Son poses didácticas para un modelo de aficionados. Mechanisms no detecta colisiones ni crea una réplica físicamente diseñada; comprueba las holguras al adaptar el rig.

El resultado es `examples/crescent-rose/CrescentRose_Mechanisms.blend`; ábrelo para comparar.

## Antes de empezar

- Archivo inicial: `examples/crescent-rose/CrescentRose_parts.blend`, dividido en 15 objetos. `CrescentRose_Mechanisms.blend` es el rig terminado.
- Reserva una sesión para preparar el FBX y otra para Mechanisms. Guarda puntos de control; son ejercicios extensos.
- Lee primero los conceptos de pieza, articulación, vínculo, control, Sequence y Form en [Mechanisms](07-mechanisms.md).
- Las capturas muestran Bforartists y BoneCraft en inglés. **Language** cambia los paneles propios de BoneCraft; el resto depende del idioma de Bforartists. Si BoneCraft no admite el idioma del programa, sus paneles quedan en inglés.
- Para el FBX original, sigue P1–P8; con el archivo preparado empieza en el paso 1. Ambas rutas usan las mismas 15 piezas.
- Las instrucciones y capturas reales se comprobaron con BoneCraft `9.1.2` y Bforartists `5.2.0`, con su mapa de teclas predeterminado.

Los números rojos indican dónde pulsar, escribir o comprobar. Sigue 1, 2, 3 en cada imagen; la numeración se reinicia. Un recuadro señala una comprobación; un círculo, el objetivo de interacción.

## Preparar el FBX original (P1-P8)

Omite esta sección si usas `CrescentRose_parts.blend`. Empieza en un archivo nuevo y conserva juntos el FBX y `CrescentRoseTextures`. Estos pasos se repitieron en Bforartists 5.2.0 con su mapa predeterminado. Usa el selector visible de modo: Tab puede alternar superposiciones en vez de entrar en Edit Mode.

### P1 - Importar el FBX

En una escena vacía, elige **File > Import > FBX (.fbx) (Legacy)** y `CrescentRose.fbx`, con Scale `1.00`. Usa el importador Legacy. El Outliner muestra una raíz y tres mallas por material: `Black01`, `Blades01`, `Red01`. Pulsa Numpad 3 para vista derecha y Home para encuadrar.

![P1 - Importar el FBX](../images/crescent-rose/en/prep-01-import-fbx.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Selecciona CrescentRose.fbx. 2: Mantén Scale en 1.00. 3: Pulsa Import FBX con el importador Legacy.*

### P2 - Mantener la posición y ajustar el tamaño

En Object Mode, selecciona las tres mallas y usa **Object > Parent > Clear and Keep Transformation**. Elimina la raíz que ya no se utiliza. Con las tres seleccionadas, aplica **Object > Apply > Rotation & Scale**. El arma mide unos `0.32 m`: escala las tres juntas por `6.25` (Ctrl+R en este mapa Bforartists, escribe 6.25 y confirma) y vuelve a aplicar Rotation & Scale. El conjunto mide unos `1.997 m`. Hazlo una sola vez; el archivo preparado ya está escalado.

Dimensions mide solo cada malla de material; comprueba la altura conjunta del extremo inferior al superior. Las tres deben tener rotación 0 y escala 1 antes de separar.

![P2 - Mantener la posición y ajustar el tamaño (1)](../images/crescent-rose/en/prep-02-unparent-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: F3 y buscar Clear Parent Keep Transform. 2: Elegir Clear and Keep Transformation en las tres mallas antes de borrar la raíz.*

![P2 - Mantener la posición y ajustar el tamaño (2)](../images/crescent-rose/en/prep-02-scale.png){style="max-width:100%;max-height:115mm;width:auto;height:auto"}

*1: Tras escalar juntas por 6.25, aplicar Rotation & Scale; Rotation debe ser 0. 2: Scale debe ser 1 en todos los ejes.*

### P3 - Conectar los materiales

En Shading y Material Preview, carga para cada material sus imágenes `BaseColor`, `Metallic`, `Roughness` y `Normal` desde `CrescentRoseTextures`. Conecta Color de Image Texture a la entrada correspondiente de Principled BSDF. BaseColor usa **sRGB**; Metallic, Roughness y Normal usan `Non-Color`. Para Normal intercala **Normal Map**, conserva `Tangent Space`, conecta Color de imagen a Color y Normal del nodo a Normal de Principled BSDF. Conserva los UV.

Repite para los materiales de hoja y cuerpo rojo. Comprueba el espacio de color tras elegir cada imagen: pertenece a la imagen. El arma debe verse roja, negra y metálica, sin el rosa de texturas ausentes.

![P3 - Conectar los materiales (1)](../images/crescent-rose/en/prep-03-materials.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: BaseColor Color a BSDF Base Color. 2: BaseColor en sRGB. 3: Mapas de datos en Non-Color. 4: Normal > Normal Map > BSDF Normal con Tangent Space.*

![P3 - Conectar los materiales (2)](../images/crescent-rose/en/prep-03-shaded.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Revisar el material de la hoja. 2: Revisar cuerpo rojo/negro en Material Preview, sin texturas rosas ausentes.*

### P4 - Separar las piezas sueltas

Selecciona las tres mallas, elige **Edit Mode**, selecciona toda la geometría y usa **Mesh > Separate > By Loose Parts**. Vuelve a Object Mode. Deben quedar **37** objetos de malla. Los sufijos numéricos pueden variar: identifica las piezas por forma y posición.

![P4 - Separar las piezas sueltas (1)](../images/crescent-rose/en/prep-04-separate-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Edit Mode y toda la geometría seleccionada. 2: F3, buscar Separate Loose y elegir By Loose Parts.*

![P4 - Separar las piezas sueltas (2)](../images/crescent-rose/en/prep-04-separate.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Comprobar 37 objetos después de separar. 2: Seleccionar por forma y posición en el Outliner; los sufijos pueden variar.*

### P5 - Unir los 15 grupos móviles

Selecciona las piezas que se moverán juntas, usa **Object > Join** (Ctrl+J) y renombra el resultado en el Outliner. Para parejas a ambos lados, orbita y comprueba que seleccionaste ambas. Trabaja desde la punta hacia dentro, luego cuerpo y asta. Los materiales describen el aspecto, no el nombre final.

| Objeto final | Piezas que unir | Vértices tras unir |
|---|---|---|
| `BladeTip` | Pomo negro de articulación y punta metálica | 252 |
| `Blade2` | Dos placas metálicas del segundo segmento y dos cubiertas rojas | 1000 |
| `Blade1` | Dos placas metálicas del primer segmento junto a la cabeza | 512 |
| `HeadMount` | Bloque negro trasero, tapa superior y núcleo; dos placas rojas internas y dos cubiertas superiores finas | 1395 |
| `PlateL` | Una placa roja exterior de la cabeza en X negativo | 676 |
| `PlateR` | Una placa roja exterior en X positivo | 676 |
| `RearSpike` | Dos hojas de punta metálica, dos tapas rojas de pivote y dos placas rojas de montaje | 1194 |
| `Receiver` | Cuerpo negro y pomo pequeño, aro metálico sobre el cerrojo, carcasa roja larga | 2609 |
| `Grip` | Bloque rojo de empuñadura bajo el cuerpo | 194 |
| `Magazine` | Tubo negro bajo el cuerpo | 96 |
| `Bolt` | Cilindro rojo de cerrojo y sus dos piezas de pomo | 362 |
| `Pole` | Asta metálica inferior y collar rojo | 148 |
| `ButtSpike` | Punta metálica inferior | 110 |
| `StrutBase` | Varilla roja fina entre cuerpo y cabeza | 34 |
| `StrutRod` | Funda negra con muescas alrededor de la varilla | 108 |

Deben quedar **15 mallas y 9,366 vértices**. No unas las placas exteriores a Blade1 ni las dos piezas del tirante entre sí. El tirante ya tiene dos piezas: no necesita bisecarse. El paso 2 repite los nombres y sus padres.

![P5 - Unir los 15 grupos móviles (1)](../images/crescent-rose/en/prep-05-group-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Renombrar los grupos unidos con los 15 nombres de la tabla.*

![P5 - Unir los 15 grupos móviles (2)](../images/crescent-rose/en/prep-05-blade1.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Seleccionar las dos placas metálicas Blade1, en lados opuestos. 2: Comprobar ambas, unir y llamar Blade1 al resultado.*

![P5 - Unir los 15 grupos móviles (3)](../images/crescent-rose/en/prep-05-join-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Abrir Object con solo las piezas de un grupo seleccionadas. 2: Join (Ctrl+J); usa la selección de dos piezas mostrada arriba.*

### P6 - Centrar los orígenes

En Object Mode selecciona las 15 mallas. Usa **Object > Set Origin > Origin to Geometry**, con Center `Bounds Center`. Comprueba rotación 0 y escala 1, sin padres ni armadura. Son orígenes de preparación; el paso 6 moverá los pivotes a las articulaciones reales.

![P6 - Centrar los orígenes (1)](../images/crescent-rose/en/prep-06-origin-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Object. 2: Set Origin. 3: Origin to Geometry y Bounds Center en las opciones.*

![P6 - Centrar los orígenes (2)](../images/crescent-rose/en/prep-06-origins.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Origen naranja centrado en la malla. 2: Rotation 0. 3: Scale 1. Los pivotes se moverán después.*

### P7 - Redimensionar y empaquetar texturas

En Image Editor elige cada uno de los **12 mapas usados** (cuatro por material). **Image > Resize**, ancho y alto **1024**, confirma y usa **Image > Pack**. Repite para todos. Empaquetar guarda los píxeles redimensionados dentro del blend; no sobrescribas los JPEG originales. Revisa Material Preview.

![P7 - Redimensionar y empaquetar texturas](../images/crescent-rose/en/prep-07-pack-textures.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Image > Resize, ancho y alto 1024. 2: Comprobar 1024 x 1024. 3: Pack. Repetir para los 12 mapas usados.*

### P8 - Guardar y reabrir

Guarda como `CrescentRose_parts.blend`. Reábrelo y comprueba las 15 mallas con sus nombres, transformaciones y materiales rojos/negros. Los 12 mapas deben funcionar sin depender de la carpeta original. Usa vista derecha y Home, y continúa en el paso 1.

![P8 - Guardar y reabrir](../images/crescent-rose/en/prep-08-save-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: File > Save As, después Open para reabrir. 2: Comprobar las 15 mallas nombradas. 3: Revisar materiales y nombre del archivo reabierto en la barra de título.*

## A. Abrir el archivo



### Paso 1 — Abrir las piezas

Abre `examples/crescent-rose/CrescentRose_parts.blend`, activa Material Preview y pulsa Numpad 3 para vista derecha: hoja a la izquierda, punta inferior hacia abajo. Home encuadra el arma.

**Resultado esperado:** guadaña roja y negra de unos 2 m, sin selección.

![Paso 1 — Abrir las piezas](../images/crescent-rose/en/01-open-file.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Material Preview. 2: Numpad 3 hasta Right Orthographic y Home para encuadrar.*

### Paso 2 — Conocer las piezas

El Outliner contiene 15 objetos; cada uno se mueve como un bloque.

| Objeto | Descripción | Sigue a |
|---|---|---|
| `Receiver` | Cuerpo del rifle con mira, gatillo y alza | el rig |
| `Grip` | Empuñadura bajo el cuerpo | `Receiver` |
| `Magazine` | Cargador cilíndrico | `Receiver` |
| `Bolt` | Cerrojo | `Receiver` |
| `Pole` | Asta inferior y collar | `Receiver` |
| `ButtSpike` | Punta inferior | `Pole` |
| `HeadMount` | Bloque de cabeza que sujeta la hoja | `Receiver` |
| `Blade1` | Primer segmento de hoja, junto a la cabeza | `HeadMount` |
| `Blade2` | Segundo segmento | `Blade1` |
| `BladeTip` | Punta | `Blade2` |
| `RearSpike` | Punta trasera de la cabeza | `HeadMount` |
| `PlateL`, `PlateR` | Placas laterales exteriores | `HeadMount` |
| `StrutBase` | Varilla fina entre cuerpo y cabeza | `Receiver` |
| `StrutRod` | Funda con muescas de esa varilla | `HeadMount` |

Para el FBX original, sigue P1–P8. El archivo preparado se creó con esas acciones de interfaz; el script de preparación ofrece una tabla de agrupación como referencia.

![Paso 2 — Conocer las piezas](../images/crescent-rose/en/02-the-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Identificar tres segmentos de hoja. 2: Comparar nombres del cuerpo, cabeza y asta con la tabla. 3: Mantener separados StrutBase y StrutRod.*

### Paso 3 — Encontrar Mechanisms

Abre BoneCraft en la Tool Shelf izquierda (si está oculta, T sobre la vista y Tools en Region Toggle) y despliega **Mechanisms**. Ensancha la estantería arrastrando su borde derecho. También está en **Properties > Scene** cuando Scene Properties tiene Show activado en preferencias. Las capturas usan la Tool Shelf. Con una malla activa y sin rig, busca **Add Parts from Selection** arriba. Selecciona todas las piezas en el paso 4 antes de pulsarlo; las secciones numeradas se habilitan al añadirlas.

![Paso 3 — Encontrar Mechanisms](../images/crescent-rose/en/03-mechanisms-section.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pestaña BoneCraft. 2: Abrir Mechanisms. 3: Localizar Add Parts from Selection antes de seleccionar todas las piezas.*

## B. Piezas



### Paso 4 — Add Parts from Selection

Sobre la vista, pulsa A para seleccionar los 15 objetos y luego **Add Parts from Selection**.

**Resultado esperado:** nueva armadura `Mechanism Rig` con las piezas debajo en el Outliner. Las mallas siguen seleccionadas. **1. Parts** enumera 15 piezas. La pestaña BoneCraft empieza ahora con Overview del rig, que puedes plegar.

![Paso 4 — Add Parts from Selection](../images/crescent-rose/en/04-add-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: A sobre la vista selecciona las 15 mallas. 2: Add Parts from Selection.*

### Paso 5 — Rides on

Cada pieza sigue a aquella a la que está unida. En **1. Parts**, selecciona `Blade1`, abre **Rides on** y elige `HeadMount`. Repite para todas según la tabla del paso 2. `Receiver` conserva «the rig».

![Paso 5 — Rides on](../images/crescent-rose/en/05-rides-on.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Blade1 en Parts. 2: Rides on > HeadMount. Repetir según la tabla de padres.*

### Paso 6 — Pivotes

Una bisagra gira alrededor del pivote de su pieza. Hoja, cabeza y empuñadura deben girar en sus articulaciones, no en sus centros. Selecciona `Blade1` en la lista, pulsa **Edit Pivot**, selecciona el marcador y usa Ctrl+W (Move en Bforartists) para colocarlo donde el segmento se une a la cabeza; pulsa **Apply Pivot**. Trabaja en vista lateral ortográfica para conservar la coordenada transversal.

Repite: `Blade2` en su unión a `Blade1`; `BladeTip` en la unión a `Blade2`; `HeadMount` en su punto inferior junto al tirante; `Grip` arriba; `RearSpike` en su unión a la cabeza; `PlateL` y `PlateR` en el centro del perno redondo donde Blade1 se une a la cabeza; `StrutBase` abajo y `StrutRod` arriba. La captura orienta: unos milímetros no producen diferencia visible.

![Paso 6 — Pivotes (1)](../images/crescent-rose/en/06-edit-pivot-button.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Seleccionar Blade1 en Parts. 2: Edit Pivot y después mover/aplicar el marcador.*

![Paso 6 — Pivotes (2)](../images/crescent-rose/en/06-edit-pivot.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Ctrl+W para mover el marcador a la unión de la hoja. 2: Apply Pivot guarda la posición.*

## C. Cabeza



### Paso 7 — Add Joint → Hinge

Abre **Add Joint → Hinge**. La construcción guiada comienza; cabecera y barra de estado indican qué hacer en cada paso.

![Paso 7 — Add Joint → Hinge](../images/crescent-rose/en/07-head-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Joint. 2: Hinge; la guía espera una pieza.*

### Paso 8 — Seleccionar la cabeza

La cabecera pide la pieza que gira. En vista derecha, una placa tapa la cabeza: pulsa el bloque trasero, detrás de las placas (círculo). Si indica `PlateR`, Esc, reinicia **Add Joint > Hinge** y pulsa más atrás. Oculta obstáculos antes de empezar: la guía consume los atajos ordinarios mientras está activa.

![Paso 8 — Seleccionar la cabeza](../images/crescent-rose/en/08-head-hinge-click.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Bloque negro trasero de HeadMount, detrás de la placa roja. Comprobar que la guía nombra HeadMount.*

### Paso 9 — X y Enter

Cuando pida el eje, pulsa X: la cabeza gira sobre el eje transversal y la guía repite una vista previa del movimiento. Enter lo confirma.

**Resultado esperado:** `HeadMount Hinge` en **2. Joints & Links** y su deslizador en **4. Controls**. Usa deslizadores en Object Mode; para controles óseos de la vista selecciona la armadura y entra en Pose Mode.

![Paso 9 — X y Enter](../images/crescent-rose/en/09-head-hinge-axis.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: X y Enter según la guía. 2: Observar la cabeza girar sobre su pivote antes de confirmar.*

### Paso 10 — Límites

Selecciona `HeadMount Hinge`, establece **Min** 0 y **Max** 120. Los positivos giran la cabeza abajo y atrás. Conserva el límite de 120°; Rifle usará un objetivo de 90° junto con las bisagras de la hoja.

![Paso 10 — Límites](../images/crescent-rose/en/10-head-hinge-limits.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: HeadMount Hinge. 2: Min 0. 3: Max 120; doble clic, escribir y Enter.*

### Paso 11 — Probar

Pulsa el botón de reproducción de la fila. La cabeza recorre 120° y vuelve, restaurando su pose.

![Paso 11 — Probar](../images/crescent-rose/en/11-test-head.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Triángulo de reproducción de HeadMount Hinge. Observar el recorrido y el regreso.*

## D. Cadena de la hoja



### Paso 12 — Tres bisagras más

Repite pasos 7–10 para `Blade1`, `Blade2`, `BladeTip`: **Add Joint → Hinge**, pieza, X, Enter y **Max** 120. Cada segmento sigue al anterior y las bisagras forman una cadena.

![Paso 12 — Tres bisagras más](../images/crescent-rose/en/12-blade-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Crear y seleccionar las bisagras de Blade1, Blade2, BladeTip. 2: Max 120 para cada una, eje X.*

### Paso 13 — Probar la cadena

Pliega **2. Joints & Links** y abre **4. Controls**. En Object Mode pon `Blade1 Hinge`, `Blade2 Hinge`, `BladeTip Hinge` a 60°, uno por uno: doble clic en el campo, Ctrl+A, valor, Enter. Los segmentos posteriores siguen a los anteriores y la cadena se enrolla. Devuelve los tres a 0.

![Paso 13 — Probar la cadena](../images/crescent-rose/en/13-blade-chain.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Escribir 60 en los tres deslizadores. 2: Comprobar la cadena y devolverlos a 0.*

## E. Placas y tirante



### Paso 14 — Bisagras de las placas

Añade igual una Hinge a `PlateR`, **Max** 30. Para `PlateL`, oculta tras la cabeza desde la derecha, pulsa Ctrl+Numpad 3 para vista izquierda, añade su Hinge y vuelve con Numpad 3.

![Paso 14 — Bisagras de las placas](../images/crescent-rose/en/14-plate-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Crear PlateR Hinge y PlateL Hinge; usar la vista opuesta para PlateL. 2: Max 30 para ambas.*

### Paso 15 — Add Link → Follow

Un control moverá ambas placas. Antes de iniciar, Numpad 1 para vista frontal, selecciona `Blade2` y usa F3 > Frame Selected para acercar la cabeza. Las placas exteriores quedan a izquierda y derecha. **Add Link > Follow**, pulsa `PlateL` a la izquierda (líder), luego `PlateR` a la derecha (seguidora) y Enter.

![Paso 15 — Add Link → Follow](../images/crescent-rose/en/15-follow.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: PlateL primero, líder. 2: PlateR después, seguidora. Enter.*

### Paso 16 — Rangos

Con Follow seleccionado, verifica **Source Range** 0…30 y **Target Range** 0…30, rellenados automáticamente. En **Name** llámalo `PlateR Follow`.

![Paso 16 — Rangos](../images/crescent-rose/en/16-follow-ranges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Nombre PlateR Follow. 2: Source Range de 0 a 30. 3: Target Range de 0 a 30.*

### Paso 17 — Add Link → Piston

El tirante debe apuntar entre cuerpo y cabeza mientras esta se pliega. Antes de iniciar, usa Numpad 3, selecciona `StrutRod` en el Outliner y F3 > Frame Selected. Luego **Add Link > Piston**. Acerca la vista primero: la guía consume los atajos de navegación.

![Paso 17 — Add Link → Piston](../images/crescent-rose/en/17-piston.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Link tras encuadrar StrutRod. 2: Piston; primero pide el cilindro.*

### Paso 18 — Cilindro y vástago

Pulsa primero la pieza de cilindro `StrutBase`, varilla roja visible en las muescas; después la pieza de vástago `StrutRod`, funda negra. Los roles cilindro/vástago describen los extremos del vínculo; los nombres del modelo describen sus piezas de origen. Enter, nombra el vínculo `Head Strut` y deja **Stretch** desactivado.

**Resultado esperado:** al cambiar `HeadMount Hinge` en Controls, ambas piezas del tirante se apuntan mutuamente. Devuelve el valor a 0.

![Paso 18 — Cilindro y vástago (1)](../images/crescent-rose/en/18-piston-parts.png){style="max-width:100%;max-height:100mm;width:auto;height:auto"}

*1: StrutBase rojo expuesto primero. 2: Funda negra StrutRod después. Enter.*

![Paso 18 — Cilindro y vástago (2)](../images/crescent-rose/en/18-piston-settings.png){style="max-width:100%;max-height:70mm;width:auto;height:auto"}

*1: Nombre Head Strut. 2: Stretch sin marcar; probar HeadMount Hinge y devolver a 0.*

## F. Rifle



### Paso 19 — Bisagras de empuñadura y punta trasera

**Add Joint → Hinge** en `Grip`, X, Enter, **Min** 0, **Max** 90. Repite en `RearSpike`, X, Enter, Min 0, Max 90. Selecciona `RearSpike Hinge` y cambia `Axis X` a `-1`, con Y y Z en 0: invierte el plegado hacia la cabeza en Compact. Grip conserva X positivo. Comprueba ambas articulaciones en la lista. Plegarán empuñadura y punta para Compact en el paso 25.

![Paso 19 — Bisagras de empuñadura y punta trasera (1)](../images/crescent-rose/en/19-grip-hinge.png){style="max-width:100%;max-height:110mm;width:auto;height:auto"}

*1: Grip Hinge. 2: Axis X 1, Y y Z 0. 3: Max 90, Min 0.*

![Paso 19 — Bisagras de empuñadura y punta trasera (2)](../images/crescent-rose/en/19-rear-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: RearSpike Hinge. 2: Axis X -1. 3: Max 90, Min 0.*

### Paso 20 — Slides de Magazine y Bolt

**Add Joint → Slide** en `Magazine`, Z, Enter, **Max** 0.04. Repite para `Bolt`, Z, Enter, **Max** 0.06. Los Slides usan unidades de escena: 0.06 son 6 cm.

![Paso 20 — Slides de Magazine y Bolt (1)](../images/crescent-rose/en/20-slides.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Magazine Slide. 2: Eje Z (Z=1, X=Y=0). 3: Max 0.04, Min 0.*

![Paso 20 — Slides de Magazine y Bolt (2)](../images/crescent-rose/en/20-bolt-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Bolt Slide. 2: Eje Z (Z=1, X=Y=0). 3: Max 0.06, Min 0.*

### Paso 21 — Pole Slide

Añade Slide a `Pole`, Z, Enter y **Max** 0.6. Los positivos retraen el asta hacia el cuerpo. Pon `Pole Slide` en 0.6 en **4. Controls**, observa y vuelve a 0.

![Paso 21 — Pole Slide](../images/crescent-rose/en/21-pole-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole Slide. 2: Eje Z (Z=1, X=Y=0). 3: Max 0.6, Min 0.*

### Paso 22 — Pole Telescope

**Add Joint → Telescope**. Pulsa `Pole` (base), luego `ButtSpike` (segmento), Enter, Z, Enter. Pon **Length** 0.2. Su control independiente sube la punta hasta 20 cm sobre Z positivo, hacia el asta. Prueba y restaura 0.

![Paso 22 — Pole Telescope (1)](../images/crescent-rose/en/22-telescope-pick.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole como base. 2: ButtSpike como segmento. Enter, Z, Enter.*

![Paso 22 — Pole Telescope (2)](../images/crescent-rose/en/22-telescope.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole Telescope. 2: Eje Z. 3: Length 0.2; probar y restablecer 0.*

## G. Secuencias



### Paso 23 — Add Sequence

En **3. Sequences**, pulsa **Add Sequence** y haz doble clic en su nombre para llamarla `Scythe to Rifle`. Enter.

![Paso 23 — Add Sequence](../images/crescent-rose/en/23-add-sequence.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Sequence. 2: Doble clic en el nombre, escribir Scythe to Rifle y Enter.*

### Paso 24 — Grabar un grupo de movimientos

Pulsa **Move Slider to End**: el deslizador pasa a `100%` y el botón dice Record Step 1. En **4. Controls**, pon `BladeTip Hinge` 70 y `Blade2 Hinge` 120. Pulsa Record Step 1: guarda dos objetivos, uno por control, y restablece ambos a 0.

La grabación sigue preparada tras cada captura; posa el siguiente grupo y pulsa el Record Step mostrado sin volver a armarla.

| Grupo | Controles y objetivos | Botón |
|---|---|---|
| 2 | `Blade1 Hinge` 10, `PlateL Hinge` 30 | Record Step 3 |
| 3 | `HeadMount Hinge` 90 | Record Step 5 |
| 4 | `Pole Slide` 0.6 | Record Step 6 |

El número del botón cuenta objetivos guardados más uno, no clics de grabación. Los cuatro grupos producen seis objetivos. Si cambias los controles, usa el número que muestre el botón.

![Paso 24 — Grabar un grupo de movimientos (1)](../images/crescent-rose/en/24-capture-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Move Slider to End una vez. El botón pasa a Record Step 1.*

![Paso 24 — Grabar un grupo de movimientos (2)](../images/crescent-rose/en/24-record-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Blade2=120, BladeTip=70. 2: Record Step 1 guarda ambos objetivos y restablece sus deslizadores.*

### Paso 25 — Los pasos

Cada objetivo grabado tiene una entrada con **Target**, suavizado, **Start** y **End**. Da a las entradas del mismo grupo iguales Start/End: hoja 0…0.25; placas y primer segmento 0.25…0.5; cabeza 0.5…0.8; asta 0.8…1. Antes de su tramo conserva el inicio y después mantiene el final. Estos campos usan 0–1; los deslizadores Controls muestran 0–100%.

Mantén `Ease In Out`. Crea `Rifle to Compact`: graba primero `Grip Hinge` 90 y `RearSpike Hinge` 90 (dos entradas, ambas 0…0.5); luego `Magazine Slide` 0.04 y `Bolt Slide` 0.06 (dos entradas, ambas 0.5…1). El botón pasa de Record Step 1 a Record Step 3 para el segundo grupo.

Al terminar cada secuencia, pulsa **Cancel** en el aviso de captura. Termina la grabación, conserva los objetivos y devuelve el deslizador a 0. Una advertencia de solapamiento mientras sigue armada se refiere al intervalo propuesto para la siguiente captura; no añadas un grupo vacío.

![Paso 25 — Los pasos (1)](../images/crescent-rose/en/25-sequence-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Target es el valor de articulación. 2: Ease In Out. 3: Start. 4: End. Repetir en las seis entradas con estos valores.*

![Paso 25 — Los pasos (2)](../images/crescent-rose/en/25-compact-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Grip y RearSpike: Target 90, Start 0, End 0.5. 2: Magazine y Bolt: 0.04 / 0.06, Start 0.5, End 1. Ease In Out.*

![Paso 25 — Los pasos (3)](../images/crescent-rose/en/25-cancel-capture.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Cancel en el aviso termina la captura, conserva entradas y devuelve la secuencia a 0.*

### Paso 26 — Probar la secuencia

Pulsa **Test** junto al botón de grabación. Recorre 0% → 100% → 0% y restaura el valor anterior a la prueba. Prueba `Scythe to Rifle` desde Scythe; prueba `Rifle to Compact` con la primera secuencia al 100%. Después devuelve ambas a 0%.

**Resultado esperado:** se enrolla la hoja, cierran las placas, la cabeza se pliega junto al cuerpo y el asta sube. Todo vuelve después.

![Paso 26 — Probar la secuencia](../images/crescent-rose/en/26-sequence-test.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Test junto a grabación. 2: Observar plegado y retorno. Probar Compact con Scythe to Rifle al 100%.*

## H. Formas



### Paso 27 — Save Form

En **4. Controls**, con todo en 0, pulsa **Save Form** y renombra la entrada `Scythe` con doble clic. Pon `Scythe to Rifle` en `100%` y guarda `Rifle`. Pon también `Rifle to Compact` en `100%` y guarda `Compact`. Deja las articulaciones individuales a 0: las secuencias aportan el movimiento.

Llevar la secuencia seleccionada al final puede volver a armar la grabación; guardar una Form no graba otro paso. Seleccionar `Scythe` y **Go to Form** devuelve ambas secuencias a 0 y desarma la captura. Rifle o Compact pueden armarla de nuevo al estar al 100%; no pulses Record Step salvo que quieras añadir un objetivo.

![Paso 27 — Save Form](../images/crescent-rose/en/27-save-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Ambas secuencias y todas las articulaciones a 0. 2: Save Form. 3: Renombrar Scythe con doble clic; repetir para Rifle y Compact.*

### Paso 28 — Go to Form

Selecciona una forma y pulsa **Go to Form**. **Go and Key** hace lo mismo e inserta claves para todos los controles en el fotograma actual; así animas la transformación.

![Paso 28 — Go to Form](../images/crescent-rose/en/28-go-to-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Elegir forma guardada. 2: Go to Form. Go and Key también inserta claves.*

### Paso 29 — Rifle



![Paso 29 — Rifle](../images/crescent-rose/en/29-result-rifle.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Rifle. 2: Go to Form. 3: Comparar porcentajes de secuencia con la pose mostrada.*

### Paso 30 — Compact



![Paso 30 — Compact](../images/crescent-rose/en/30-result-compact.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Compact. 2: Go to Form. 3: Comparar porcentajes con la pose. Volver a Scythe y guardar el archivo.*

## Qué construiste

| Registro | Huesos | Función |
|---|---|---|
| 15 piezas | `MCH-<part>` y `DEF-<part>` | La malla de cada pieza sigue a su hueso `DEF-` |
| 8 Hinges, 3 Slides, 1 Telescope | `CTRL-<part>` | Controles; sus valores son los deslizadores de **4. Controls** |
| 1 Piston | `MCH-<part>-aim`, `MCH-<part>-target` | Mantiene las dos piezas del tirante apuntándose |
| 1 Follow | ninguno | `PlateR` gira con `PlateL` |
| 2 Sequences | `CTRL-SEQ-<name>` | Un deslizador por secuencia |
| 3 Forms | ninguno | Valores de deslizadores guardados |

El ejemplo renovado pasó Rig Validator sin problemas y las pruebas de reapertura con Auto Run Python Scripts desactivado, incluidos todos los controles y las tres Forms.

## Prueba después

- Activa **Curve** en `PlateR Follow` y modifica el mapeo en Graph Editor.
- Guarda una cuarta forma `Carry`, con hoja plegada y cabeza levantada.
- Inserta claves con **Go and Key** y exporta los huesos `DEF-`; consulta [Herramientas de VRChat](08-vrchat.md).

## Gear Link

Crescent Rose no tiene una pareja de engranajes y este rig no usa Gear Link. Este vínculo gira una Hinge al girar otra según la relación de dientes: manivela y rueda, o cremallera que convierte giro en desplazamiento. Consulta [Gear Link](07-mechanisms.md#gear-link-enlace-de-engranaje).

## Créditos

Modelo Crescent Rose de amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0; dividido, escalado y preparado para este tutorial. Crescent Rose es un diseño de Rooster Teeth Productions; este recurso didáctico fue creado por aficionados.

[← Índice](index.md)
