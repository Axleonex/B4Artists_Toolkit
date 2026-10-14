# Herramientas de rig

[← Índice](index.md)

Este capítulo explica en detalle las herramientas de rigging, animación y pesos de BoneCraft. Úsalo cuando quieras entender mejor una función, o cuando las guías no cubran tu situación concreta.

Cada entrada dice qué hace la herramienta, cuándo usarla, sus controles principales y dónde está. Algunas herramientas solo aparecen en cierto modo, y la línea «Dónde está» de cada entrada lo indica: por ejemplo, los controles de rig en Modo Pose, el espejo y la transferencia de pesos en el modo Pintura de pesos, y Delta Mush en Modo Objeto.

---

## Herramientas de interfaz de rig

Estas herramientas te ayudan a gestionar la parte visual del trabajo con armaduras: qué huesos se ven, cómo se organizan y un acceso rápido.

---

### Colecciones de huesos

**Qué hace:** muestra las colecciones de huesos de tu esqueleto como filas. Haz clic en el nombre de una colección para seleccionar sus huesos; el icono del ojo la muestra u oculta.

> Una colección de huesos es un grupo de huesos con nombre, por ejemplo «IK Controls», «Face Bones» y «Deform Bones». Ocultar una colección oculta esos huesos en la vista, para que puedas centrarte en una parte del rig.

**Controles principales:**
- Cada fila: el color de acento, **Toggle Collection Visibility** (alternar visibilidad; icono de ojo), el nombre de la colección (selecciona sus huesos), **Solo Collection** (colección en solitario; icono S) y **Rename Collection Display** (renombrar visualización; icono de engranaje), que da a la fila un nombre visible personalizado
- **Show All Collections** (mostrar todas las colecciones) y **Hide All Collections** (ocultar todas las colecciones) (iconos de ojo abierto y cerrado sobre la lista) — todo de una vez
- Secciones — agrupar varias colecciones bajo un encabezado plegable

**Dónde está:** pestaña BoneCraft → Revisión → Colecciones

---

### Marcadores de Visibilidad

**Qué hace:** guarda qué colecciones de huesos están visibles, para cambiar de golpe entre vistas guardadas.

**Ejemplo de uso:** preparas una vista con solo los huesos de la cara para trabajar expresiones y la guardas como «Face Only». Luego muestras todo para pintar pesos y lo guardas como «Full Rig». Ahora un clic cambia entre ambas.

**Controles principales:** cada ranura es una fila.
- El nombre del marcador — haz clic en él para aplicar la vista guardada
- **Save Bookmark** (guardar marcador; icono de disco) — guarda la visibilidad actual en la ranura
- La muestra de color — da un color al marcador
- **Clear Bookmark** (vaciar marcador) y **Remove Bookmark** (eliminar marcador; iconos de cerrar) — vacían la ranura o quitan una ranura añadida
- **Agregar marcador** — añade una ranura

**Marcadores predeterminados:** FK Arms, IK Body, Face Only, Full Rig

**Dónde está:** pestaña BoneCraft → Revisión → Colecciones → Marcadores de Visibilidad

---

### Panel rápido por atajo

**Qué hace:** abre el panel de rig de BoneCraft (colecciones y marcadores) como ventana emergente donde esté el cursor.

**Cómo usarlo:** pulsa **Ctrl+Shift+R** en la vista 3D. Haz clic fuera de la ventana para cerrarla.

**Dónde está:** el atajo **Ctrl+Shift+R** en la vista 3D (no tiene panel propio)

---

## Herramientas de animación

---

### Biblioteca de Poses

**Qué hace:** guarda poses con nombre y miniatura que puedes aplicar a tu rig con un clic.

**Controles principales:**
- **Guardar** — guarda las posiciones actuales de los huesos como una pose con nombre, con una miniatura de la vista
- **Aplicar** — lleva los huesos a la pose guardada
- **Mezclar** — aplica la pose con intensidad parcial, mezclada con la posición actual
- **Espejo** — aplica la pose invertida de izquierda a derecha
- **Eliminar**, **Renombrar** y **Categoría** — gestionar la lista; **Filtro** muestra una sola categoría
- **Exportar** e **Importar** — guardar en un archivo `.bfpose` o cargar desde uno

**Dónde está:** pestaña BoneCraft → Revisión → Biblioteca de Poses

---

### Control Picker (selector de controles)

**Qué hace:** un mapa en el que se puede hacer clic de los controles de tu rig. Haz clic en una forma para seleccionar su hueso; el selector resalta lo seleccionado.

**Controles principales:**
- **Generate Picker** (generar selector) — construye la distribución a partir de tu rig
- **Edit Layout** (editar distribución) — mover, cambiar de tamaño y reetiquetar los controles (**Move Picker Control** (mover control), **Resize Picker Control** (cambiar tamaño del control) y **Relabel Picker Control** (reetiquetar control) aparecen como iconos en la fila de cada control) y ajustarlos a una cuadrícula con **Snap** (ajustar); **Reconstruir diseño** la vuelve a construir
- **Reflejar selección** — selecciona los controles simétricos
- **Selector emergente** — abre el selector en una ventana flotante, que también tiene **Add Selection Set** (añadir conjunto de selección)

**Dónde está:** pestaña BoneCraft → Revisión → Control Picker

---

### Control Layer (capa de control, IK/FK)

**Qué hace:** controles de animador para las extremidades de un rig construido con **Construir rig de control**: cambiar una extremidad entre IK y FK sin que salte, y hornear una en la otra a lo largo de un rango de fotogramas.

**Controles principales:**
- **IK** y **FK** — cambian la extremidad y ajustan los nuevos controles a donde está, para que el codo o la rodilla no salten
- **Bake IK** (hornear en IK) y **Bake FK** (hornear en FK) — convierten la animación a IK o a FK en un rango de fotogramas
- **Pole Follow** (seguimiento del polo), **Pin** (fijar) y **Lock-Free** (sin bloqueo), y **Global Rig Scale** (escala global del rig), que mantiene los bloqueos protegidos

**Dónde está:** pestaña BoneCraft → Revisión → Control Layer (con un rig construido con **Construir rig de control** seleccionado; consulta [Constructor de Rig](06-rig-builder.md))

---

### Herramientas Rigify

**Qué hacen:** detectan un rig de control de Rigify y conectan el panel de colecciones, los marcadores y los deslizadores de propiedades de BoneCraft con los controles estándar de Rigify.

> Rigify es el sistema integrado de Bforartists para generar rigs listos para animar. Si construiste tu rig con Rigify, esto conecta la interfaz de BoneCraft con los controles IK/FK de Rigify.

**Controles principales:**
- **Mejora Automática** — configura los paneles de BoneCraft para el rig de Rigify seleccionado
- **Volver a Ejecutar el Mejoramiento** — los reconstruye desde cero
- **Habilitar Rigify** y **Generar Rig de Control (metarig activo)** están en Quick Rig (consulta [Constructor de Rig](06-rig-builder.md))
- Propiedades Rigify — los deslizadores de IK/FK, estiramiento, espacio padre y seguimiento de cabeza/cuello del rig

**Dónde están:** pestaña BoneCraft → Configurar Rigging → Herramientas Rigify (y la sección Propiedades Rigify)

---

### Redireccionar

**Qué hace:** pasa una animación de un esqueleto a otro, por ejemplo un clip de captura de movimiento a tu avatar. Los huesos se emparejan por nombre y por dirección, así que las extremidades mantienen su orientación; las clavículas se emparejan de forma flexible para que los hombros no giren de más.

**Controles principales:**
- **Importar Clip** y **Explorar Biblioteca** — cargar un clip, o definir una carpeta de biblioteca; haz clic en el nombre de un clip para seleccionarlo
- **Auto-Match Bones** (emparejar huesos automáticamente; la marca de verificación en la fila de un clip) — empareja los huesos de origen y destino (la lista Mapeo de Huesos del panel muestra las parejas)
- **Vista previa** y **Detener vista previa** — probar el resultado
- **Aplicar** — hornea el clip en tu rig

**Dónde está:** pestaña BoneCraft → Configurar Rigging → Redireccionar

---

### Shape keys correctivos

**Qué hacen:** shape keys que se activan cuando un hueso alcanza un ángulo, para corregir pellizcos o hundimientos en poses extremas.

**Ejemplo de uso:** el codo de tu personaje se hunde al doblarlo del todo. Esculpes un codo corregido y lo vinculas al hueso del brazo para que se aplique solo a medida que el codo se dobla.

**Controles principales:**
- Nueva Corrección — elige el **Shape Key**, el **Hueso Driver**, el eje de rotación, el ángulo en el que la forma está del todo activa y lo gradual de su entrada, y haz clic en **Crear Correctivo**
- La lista de correctivos: haz clic en el nombre del shape key de un correctivo para seleccionarlo; **Editar** y **Eliminar**, debajo de la lista, actúan sobre el seleccionado

**Dónde están:** pestaña BoneCraft → Malla → Correctivos (la malla necesita un shape key base)

---

### Herramientas de Gráfico

**Qué hacen:** herramientas de animación para pulir fotogramas clave y curvas.

- **Desglose Interactivo** (Breakdowner; atajo **Ctrl+Shift+B** en la vista 3D) — arrastra a izquierda y derecha para mezclar la pose actual entre los fotogramas clave cercanos
- **Aplicar Delta** (Movedor Delta; atajo **Ctrl+Shift+D** en la vista 3D) — desplaza los huesos seleccionados una cantidad exacta en el espacio de pantalla o del mundo
- **Capturar** e **Intercambiar** (Curvas en Búfer) — guardar una copia de las curvas e intercambiar entre ella y tus cambios
- **Horneado Inteligente** — hornea en claves la animación impulsada por restricciones, descartando claves redundantes (**Tol** fija cuánto)
- **Filtro de Euler** — corrige los saltos de rotación causados por el bloqueo de cardán
- Mangos Tangentes — definir el tipo de mango de las claves seleccionadas: **Auto**, **Vector**, **Aligned** (alineado), **Free** (libre) o **Auto Clamped** (auto limitado)

**Dónde están:** pestaña BoneCraft → Revisión → Herramientas de Gráfico

---

## Herramientas de pesos

Estas herramientas controlan cómo se deforma tu malla cuando se mueven los huesos. Los pesos indican a cada parte de la malla qué huesos seguir y cuánto.

---

### Recálculo automático de pesos de huesos

**Qué hace:** vuelve a calcular los pesos de una malla a partir del rig existente, sin cambiar la malla. En mallas densas trabaja a través de una malla proxy más ligera, para no fallar en silencio.

**Controles principales:** la malla y la armadura de destino, el método, la mezcla y el suavizado, el número máximo de influencias de huesos por vértice, un peso mínimo y una copia de seguridad de los pesos anteriores. Ejecuta **Automatic Bone Weight Recalculation** (recálculo automático de pesos de huesos). La pestaña CATS tiene un atajo: **Smart Automatic Weights** (pesos automáticos inteligentes).

**Dónde está:** pestaña BoneCraft → Malla → Herramientas de Peso

---

### Espejo de Pesos

**Qué hace:** copia los pesos de un lado de tu avatar al otro. Imprescindible para personajes simétricos.

**Controles principales:**
- **Espejar Todos los Pesos** — refleja cada grupo de huesos a su lado opuesto
- **Espejar Peso Activo** — refleja solo el grupo de huesos activo
- Eje de simetría y dirección del espejo (en ambos sentidos, de izquierda a derecha o de derecha a izquierda)
- **Espejo de Topología** — empareja los vértices por la topología de la malla en lugar de por la posición
- **Distancia de Búsqueda** — a qué distancia pueden estar dos vértices y seguir contando como pareja (súbela en mallas que no sean perfectamente simétricas)
- **Seleccionar No Coincidentes** — selecciona los vértices sin pareja; **Normalizar Pesos** hace después que los pesos sumen 1.0

**Dónde está:** pestaña BoneCraft, en modo Pintura de pesos → Espejo de Pesos

---

### Transferencia de pesos

**Qué hace:** copia los pesos de una malla de origen a la malla activa. Se usa al unir ropa a un cuerpo, o al pasar pesos de una malla de alta resolución a otra más ligera.

**Controles principales:**
- Malla de origen, método de transferencia y filtro de huesos
- **Normalizar Después de Transferir** — mantiene la suma de los pesos en 1.0
- **Transferir Pesos** — la ejecuta; el resultado muestra la distancia media y la máxima, y **Seleccionar Vértices con Problemas** selecciona los vértices que se emparejaron mal

**Dónde está:** pestaña BoneCraft, en modo Pintura de pesos → Transferencia de pesos (también en Malla → Herramientas de Peso)

---

### Tabla de Pesos

**Qué hace:** muestra los pesos exactos del vértice seleccionado para cada hueso, para que puedas escribir valores precisos.

**Cómo usarla:** selecciona un vértice en el modo Pintura de pesos; la tabla enumera sus huesos y pesos. Con varios vértices seleccionados, **Normalizar todos los vértices** los normaliza todos.

**Dónde está:** pestaña BoneCraft, en modo Pintura de pesos → Tabla de Pesos

---

### Relleno por Inundación

**Qué hace:** fija con un clic el peso del grupo activo en los vértices seleccionados: **Inundar a 0.0**, **Inundar a 1.0**, o **Inundar** con un **Valor Personalizado** (con **Normalización Personalizada**).

**Dónde está:** pestaña BoneCraft → Malla → Herramientas de Peso

---

### Deformar vs Controlar

**Qué hace:** separa los huesos del rig en huesos de deformación (mueven la malla) y huesos de control (los mueve el animador), etiqueta los huesos de deformación, les da nombres de deformación y exporta un esqueleto solo de deformación.

**Dónde está:** pestaña BoneCraft, en Modo Pose → Deformar vs Controlar

---

### Delta Mush

**Qué hace:** una deformación suavizante que reduce los pellizcos en las articulaciones. La malla conserva su forma en reposo pero se deforma de forma más limpia en movimiento.

**Controles principales:** iteraciones, fuerza del suavizado, bordes fijados, suavizar solo la deformación, y si se ejecuta antes que la armadura. El botón de añadir agrega el modificador y lo vincula a la forma de reposo.

**Dónde está:** BoneCraft → Skin → Delta Mush (Object Mode; Mesh)

---

### Envoltura por Proximidad

**Qué hace:** hace que una malla siga la superficie de otra, como una segunda piel. Útil para ropa ceñida al cuerpo.

**Controles principales:** la malla conductora a seguir, el tipo de atenuación y la distancia máxima; el botón de vincular une la malla.

**Dónde está:** BoneCraft → Skin → Proximity Wrap (Object Mode; Mesh)

---

## Controles de rig

Estas herramientas aparecen en la pestaña BoneCraft en Modo Pose.

---

### Cambio de Espacio

**Qué hace:** cambia el espacio que sigue un hueso durante la animación. Una mano que sujeta un accesorio puede pasar con un clic de seguir al cuerpo a quedarse quieta en el mundo.

**Controles principales:**
- **Añadir Espacio** y **Remove Space** (quitar espacio; icono X bajo Gestionar Espacios) — los espacios que puede seguir un hueso (World, Origin u otro hueso)
- Un botón por espacio, con su nombre; el espacio actual lleva ●. Haz clic en el botón de otro espacio para cambiar el hueso a él

**Dónde está:** pestaña BoneCraft, en Modo Pose → Cambio de Espacio

---

### Spline IK

**Qué hace:** hace que una cadena de huesos siga una curva. Se usa para colas, tentáculos, cuerdas, cabello largo y columnas que necesitan un movimiento suave y amplio.

**Controles principales:** **Longitud de la Cadena**, **Resolución de Curva**, **Estirar**, **Modo de Torsión**, **Preservar Volumen**; **Generar Spline IK** y **Eliminar Spline IK**.

**Dónde está:** pestaña BoneCraft, en Modo Pose → Spline IK

---

### Dinámica de Cadena

**Qué hace:** movimiento secundario de tipo físico en una cadena de huesos: los huesos se quedan atrás cuando el padre se mueve y rebotan cuando se detiene. Se usa para mechones de cabello, colas y accesorios.

**Controles principales:** rigidez, amortiguación, masa y gravedad; añadir dinámica a la cadena seleccionada. La colisión usa una forma de esfera simplificada, así que las superficies cóncavas pueden no colisionar bien.

**Dónde está:** pestaña BoneCraft, en Modo Pose → Dinámica de Cadena

---

### Cinta

**Qué hace:** construye una cinta de Bendy Bones (huesos que se curvan y tuercen con suavidad) para labios, cejas, cinturones y otras zonas blandas y curvas.

**Controles principales:** **Huesos de Control** y **Ancho de la Cinta**; **Generar Cinta** y **Eliminar Cinta**.

**Dónde está:** pestaña BoneCraft, en Modo Pose → Cinta

---

### Biblioteca de Visemas

**Qué hace:** crea y gestiona conjuntos de visemas (formas de boca) vinculados a shape keys, y genera claves de sincronización labial a partir de texto. Para el mapeo de visemas de VRChat usa VRChat Viseme Mapping; para generar visemas desde cero usa la sección Visemas de CATS.

**Controles principales:**
- **Nuevo Conjunto** y **Eliminar** — crear o borrar un conjunto de visemas
- En cada conjunto, un botón por visema (icono de altavoz) lo previsualiza
- Sincronización Labial — de texto a claves de visemas, con fotogramas por fonema y suavizado

**Dónde está:** CATS → Avatar Tools → Viseme Library (Armature); Lip Sync (Pose Mode)

---

### Clave Conducida por Conjunto

**Qué hace:** vincula un valor a otro sin expresiones de Python. Posa el conductor (por ejemplo un hueso de ceja), fija el valor conducido (por ejemplo un shape key «Brow Raised») y registra el punto; BoneCraft construye la curva del driver.

**Controles principales:**
- **Hueso Driver** y **Atributo del Driver** — lo que conduce
- **Hueso Objetivo** y **Atributo Objetivo** — lo que es conducido
- **Establecer Valor** y **Registrar Punto** — registrar un punto en la curva
- **Crear SDK** — construye el driver

**Dónde está:** pestaña BoneCraft, en Modo Pose → Clave Conducida por Conjunto

---

### Validador de Rig

**Qué hace:** comprueba tu rig con un conjunto de reglas e informa de los problemas: nombres, huesos que faltan, restricciones rotas, jerarquía, pesos, drivers que necesitan Python y las reglas de Mechanisms. Los nombres de huesos con guiones (como `DEF-upper_arm.L`) pasan.

**Controles principales:**
- **Ejecutar validación** — ejecuta cada comprobación y enumera los resultados
- **Export Report** (exportar informe) — guarda los resultados en un archivo

El Tablero de Tareas (pestaña BoneCraft → Resumen → Tablero de Tareas) muestra una tarea del validador cuando falla una comprobación.

**Dónde está:** pestaña BoneCraft → Revisión → Validador de Rig

---

### Notas del Rig

**Qué hacen:** notas escritas unidas a los huesos del rig: lo que configuraste, recordatorios, notas para colaboradores.

**Controles principales:** **Añadir Nota**, y **Eliminar** en cada nota. Léame del Rig muestra las notas del rig como una página de solo lectura.

**Dónde están:** pestaña BoneCraft → Resumen → Notas del Rig, y Revisión → Léame del Rig

Siguiente: [Constructor de Rig](06-rig-builder.md)
