# Herramientas de rig

[← Contenidos](index.md)

Este capítulo cubre en detalle las herramientas de rigging, animación y peso de BoneCraft. Úselo cuando desee comprender una característica más profundamente o cuando las guías no cubran su situación exacta.

Cada entrada dice qué hace la herramienta, cuándo la usarías, sus controles principales y dónde encontrarla. La línea "Dónde encontrarlo" de cada entrada nombra el modo necesario para usarlo: por ejemplo, controles de rig en modo Pose, espejo de peso y transferencia de peso en modo pintura con peso, y Delta Mush en modo objeto. Algunas secciones permanecen visibles con un mensaje sobre qué seleccionar cuando sus herramientas no se pueden ejecutar.

En 9.1, muchas herramientas se ejecutan a la vez y colocan sus opciones en el panel Ajustar última operación. Cambie esas opciones inmediatamente después del clic, antes de ejecutar otra operación. Los menús Pose → BoneCraft y Pesos → BoneCraft, y los paneles de botones BoneCraft en las pestañas del estante de herramientas Pose y Pesos de Bforartists ofrecen accesos directos a operaciones comunes. [Empezando](01-start.md#dónde-está-cada-cosa) enumera estos puntos de acceso.

---

## Herramientas de interfaz de rig

Estas herramientas le ayudan a gestionar el aspecto visual del trabajo con armaduras: qué huesos son visibles, cómo están organizados y acceso rápido.

---

### Colecciones de huesos

**Qué hace:** Muestra las colecciones de huesos de su esqueleto como filas. Haga clic en el nombre de una colección para seleccionar sus huesos; el icono del ojo lo muestra u oculta.

> Una colección de huesos es un grupo de huesos con nombre, por ejemplo, "Controles IK ", "Huesos de la cara" y "Deformar huesos". Ocultar una colección oculta esos huesos en la ventana gráfica, para que puedas concentrarte en una parte del rig.

**Controles clave:**
- Cada fila: el color de acento, **Toggle Collection Visibility** (icono de ojo), el nombre de la colección (selecciona sus componentes),**Solo Collection** y**Rename Collection Display**, que establece un nombre para mostrar personalizado para la fila. Pase el cursor sobre un botón de solo ícono para identificarlo por su información sobre herramientas
- **Show All Collections** y**Hide All Collections** (iconos de ojos abiertos y cerrados encima de la lista): todo a la vez
- Secciones: agrupa varias colecciones bajo un encabezado plegable

**Dónde encontrarlo:** Pestaña BoneCraft → Revisar → Colecciones

---

### Marcadores de Visibilidad

**Qué hace:** Guarda qué colecciones de huesos son visibles, para que puedas cambiar entre vistas guardadas a la vez.

**Uso de ejemplo:** Configura una vista con solo los huesos de la cara para el trabajo de expresión y la guarda como "Solo cara". Luego muestra todo para pintar con peso y lo guarda como "Full Rig". Ahora un clic cambia entre ellos.

**Controles clave:** cada ranura es una fila.
- El nombre del marcador: haga clic en él para aplicar la vista guardada.
- **Save Bookmark**: guarda la visibilidad actual en la ranura; coloque el cursor sobre su ícono para ver la información sobre herramientas
- La muestra de color: codifica con colores el marcador
- **Clear Bookmark** y**Remove Bookmark** (iconos de cierre): vacíe la ranura o elimine una agregada
- **Add Bookmark**: agrega una ranura

**Marcadores predeterminados:** Brazos FK, Cuerpo IK, Solo cara, Plataforma completa

**Dónde encontrarlo:** Pestaña BoneCraft → Revisar → Colecciones → Marcadores de visibilidad

---

### Panel rápido por atajo

**Qué hace:** Abre el panel de rig de BoneCraft (colecciones y marcadores) como una ventana emergente dondequiera que esté el cursor.

**Cómo utilizar:** Presione**Ctrl+Shift+R** en la ventana gráfica 3D. Haga clic fuera de la ventana emergente para cerrarla.

**Dónde encontrarlo:** el acceso directo**Ctrl+Shift+R** en la ventana gráfica 3D (no tiene panel propio)

---

## Herramientas de animación

---

### Biblioteca de Poses

**Qué hace:** Almacena poses nombradas con miniaturas que puedes aplicar a tu rig con un solo clic.

**Controles clave:**
- **Save**: almacena las posiciones actuales de los huesos como una pose con nombre, con una miniatura de la ventana gráfica
- **Apply**: ajusta los huesos a la pose guardada
- **Blend**: aplica la pose con fuerza parcial, mezclada con la posición actual
- **Mirror**: aplica la pose volteada de izquierda a derecha
- **Delete**,**Rename** y**Category**: gestionan la lista;**Filter** muestra una categoría
- **Export** y**Import**: guardar o cargar desde un archivo `.bfpose`

La mezcla se aplica inmediatamente. Establezca la intensidad de la mezcla en Ajustar última operación después de hacer clic en él.

**Dónde encontrarlo:** Pestaña BoneCraft → Revisar → Biblioteca de poses

---

### Control Picker (selector de controles)

**Qué hace:** Un mapa en el que se puede hacer clic de los controles de su rig. Haga clic en una forma para seleccionar su hueso; el selector resalta lo que está seleccionado.

**Controles clave:**
- **Generate Picker**: crea el diseño desde su rig
- **Edit Layout**: mueva, cambie el tamaño y vuelva a etiquetar los controles (**Move Picker Control**,**Resize Picker Control** y**Relabel Picker Control** aparecen como íconos en la fila de cada control) y**Snap** en una cuadrícula;**Rebuild Layout** lo construye de nuevo
- **Mirror Selection**: selecciona los controles reflejados
- **Pop-up Picker**: abre el selector en una ventana flotante, que también tiene**Add Selection Set**

**Dónde encontrarlo:** Pestaña BoneCraft → Revisar → Selector de control

---

### Control Layer (capa de control, IK/FK)

Para ver una comparación práctica ilustrada, siga [Pesas de prueba y uso IK/FK](06-rig-builder.md#parte-c-comprobar-los-pesos-y-usar-ikfk).

**Qué hace:** Controles del animador para las extremidades de un rig fabricado por**Build Control Rig**: cambia una extremidad entre IK y FK sin que la extremidad salte y fusiona una con la otra en un rango de fotogramas.

**Controles clave:**
- **IK** y**FK**: cambie la extremidad y ajuste los nuevos controles a donde está la extremidad, para que el codo o la rodilla no salten
- **Bake IK** y**Bake FK**: convierte la animación en un rango de cuadros a IK o a FK.
- **Pole Follow**,**Pin** y**Lock-Free**, y**Global Rig Scale**, que mantiene cerraduras protegidas

**Dónde encontrarlo:** Pestaña BoneCraft → Revisar → Capa de control (con un rig fabricado por**Build Control Rig** seleccionado; ver [Constructor de plataformas](06-rig-builder.md) )

---

### Herramientas Rigify

**Qué hace:** Detecta un rig de control Rigify y conecta el panel de colección, los marcadores y los controles deslizantes de propiedades de BoneCraft a los controles estándar de Rigify.

> Rigify es el sistema integrado de Bforartists para generar rigs listos para animación. Si construyó su rig con Rigify, esto conecta la interfaz de usuario de BoneCraft a los controles IK/FK de Rigify.

**Controles clave:**
- **Auto-Enhance**: configura los paneles de BoneCraft para el rig Rigify seleccionado
- **Re-run Enhancement**: los reconstruye desde cero
- **Enable Rigify** está en Quick Rig; ampliar su página de Solución de problemas para**Generate Control Rig (active metarig)** (ver [Constructor de plataformas](06-rig-builder.md) )
- Propiedades de Rigify: los controles deslizantes de seguimiento de cabeza/cuello IK/FK, estiramiento, espacio principal y cabeza/cuello del rig

**Dónde encontrarlo:** Pestaña BoneCraft → Configurar Rigging → Herramientas Rigify (y la sección Propiedades de Rigify )

---

### Redireccionar

**Qué hace:** Mueve la animación de un esqueleto a otro (por ejemplo, un clip de captura de movimiento a tu avatar). Los huesos se relacionan por nombre y dirección, de modo que las extremidades mantienen su orientación; Las clavículas están unidas libremente para que los hombros no giren demasiado.

**Controles clave:**
- **Import Clip** y**Browse Library**: carga un clip o configura una carpeta de biblioteca; haga clic en el nombre de un clip para seleccionarlo
- **Auto-Match Bones** (la marca de verificación en la fila de un clip): empareja los huesos de origen y de destino (la lista de mapeo de huesos del panel muestra los pares)
- **Preview** y**Stop Preview**: prueba el resultado
- **Apply**: hornea el clip en tu rig

**Dónde encontrarlo:** Pestaña BoneCraft → Configurar rigging → Retarget

---

### Shape keys correctivos

**Qué hace:** Teclas de forma que se activan cuando un hueso alcanza un ángulo, para corregir pellizcos o colapsos en posturas extremas.

**Ejemplo de uso:** El codo de tu personaje colapsa cuando está completamente doblado. Esculpes un codo corregido y lo vinculas al hueso del brazo para que se aplique automáticamente cuando el codo se dobla.

**Controles clave:**
- Nuevo correctivo: elija el **Shape Key**, el**Driver Bone**, el eje de rotación, el ángulo en el que la forma está completamente y cómo se desvanece gradualmente, luego**Create Corrective**
- La lista de correctivos: haga clic en el nombre de la clave de forma de un correctivo para seleccionarlo; **Edit** y**Delete** en la lista actúan sobre el seleccionado

La edición comienza desde los valores actuales del correctivo. Cambie su ángulo y caída en Ajustar última operación después de hacer clic en él.

**Dónde encontrarlo:** Pestaña BoneCraft → Máscara → Correctivos (la malla necesita una clave de forma básica)

---

### Herramientas de Gráfico

**Qué hace:** Herramientas de refinamiento de animación para fotogramas clave y curvas.

- **Interactive Breakdown** (Desglose; método abreviado**Ctrl+Shift+B** en la ventana gráfica 3D): arrastre hacia la izquierda y hacia la derecha para combinar la pose actual entre los fotogramas clave más cercanos
- **Apply Delta** (Delta Mover; método abreviado**Ctrl+Shift+D** en la ventana gráfica 3D): empuja los huesos seleccionados con un desplazamiento exacto en el espacio de la pantalla o el espacio mundial
- **Capture** y**Swap** (Curvas de búfer): conserve una copia de las curvas e intercámbielas con sus ediciones.
- **Smart Bake**: crea animaciones basadas en restricciones en las claves, eliminando claves redundantes (**Tol** establece cuánto)
- **Euler Filter**: corrige los cambios de rotación causados por el bloqueo del cardán
- Controladores tangentes: establezca tipos de controladores en teclas seleccionadas: **Auto**,**Vector**,**Aligned**,**Free** o**Auto Clamped**.

**Dónde encontrarlo:** Pestaña BoneCraft → Revisar → Herramientas gráficas

---

## Herramientas de pesos

Estas herramientas controlan cómo se deforma la malla cuando los huesos se mueven. Los pesos le indican a cada parte de la malla qué huesos seguir y cuánto.

---

### Recálculo automático de pesos de huesos

**Qué hace:** Vuelve a calcular los pesos de una malla del rig existente, sin cambiar la malla. En mallas densas, funciona a través de una malla proxy más ligera, por lo que no falla silenciosamente.

**Controles clave:** elige la malla y la armadura del objetivo, luego el modo Cuerpo o Ropa. Body calcula los pesos a partir del rig existente; La ropa los transfiere desde una malla fuente correctamente ponderada. Establezca el método, la combinación y el suavizado, la cantidad máxima de influencias óseas por vértice, un peso mínimo y si desea mantener una copia de seguridad, luego ejecute**Automatic Bone Weight Recalculation**. Estas configuraciones están encima del botón. El acceso directo CATS,**Smart Automatic Weights**, abre un cuadro de diálogo para la malla de destino, la armadura y el modo, además de la malla de origen en el modo Ropa.

**Dónde encontrarlo:** Pestaña BoneCraft → Máscara → Herramientas de peso

---

### Espejo de Pesos

**Qué hace:** Copia los pesos de un lado de tu avatar al otro. Esencial para personajes simétricos.

**Controles clave:**
- **Mirror All Weights**: refleja cada grupo de huesos en su lado opuesto
- **Mirror Active Weight**: refleja solo el grupo óseo activo
- Eje de simetría y dirección del espejo (en ambos sentidos, de izquierda a derecha o de derecha a izquierda)
- **Topology Mirror** — empareja vértices por topología de malla en lugar de posición
- **Search Distance**: qué tan separados pueden estar dos vértices y seguir contando como un par (aumente el valor para mallas que no son perfectamente simétricas)
- **Select Unmatched**: selecciona vértices sin pareja;**Normalize Weights** hace que los pesos sumen 1,0 después

Primero haga clic en un botón de espejo, luego configure el eje, la dirección, el modo de topología y la distancia de búsqueda en Ajustar la última operación. **Mirror Active Weight** también se encuentra en Pesos → BoneCraft y en la pestaña Estante de herramientas de pesos.

**Dónde encontrarlo:** Pestaña BoneCraft, en modo Pintura de peso → Espejo de peso

---

### Transferencia de pesos

**Qué hace:** Copia los pesos de una malla de origen a la malla activa. Se utiliza para sujetar ropa a un cuerpo o mover pesos de una malla de alta resolución a una inferior.

**Controles clave:**
- Elija la malla de origen antes de transferir
- Después del clic, configure el método de transferencia y el filtro óseo en Ajustar última operación
- **Normalize** en Ajustar última operación: mantiene los pesos sumando 1,0
- **Transfer Weights**: lo ejecuta; el resultado muestra la distancia media y máxima, y**Select Problem Vertices** selecciona los vértices que no coinciden

**Dónde encontrarlo:** pestaña BoneCraft, en modo Pintura con peso → Transferencia de peso (también en Piel → Herramientas de peso)

---

### Tabla de Pesos

**Qué hace:** Muestra los pesos exactos del vértice seleccionado para cada hueso y le permite establecer un valor preciso.

**Cómo utilizar:** Seleccione un vértice en el modo Pintura ponderada; la tabla enumera sus huesos y pesos. Haga clic en el ícono de la mano en la fila de un hueso, luego configure**Weight** en Ajustar última operación. Add Influence usa el hueso que elijas; establezca también su nuevo peso en Ajustar última operación. Con varios vértices seleccionados,**Normalize All Vertices** los normaliza todos.

**Dónde encontrarlo:** Pestaña BoneCraft, en modo Pintura de pesos → Tabla de pesos

---

### Relleno por Inundación

**Qué hace:** Establece el peso del grupo activo en los vértices seleccionados con un solo clic:**Flood to 0.0**,**Flood to 1.0** o**Flood to Custom**. Después de la inundación en Personalizado, configure**Value** y**Normalize** en Ajustar última operación. El menú y el estante de Pesos llaman a los botones de valor fijo Inundar a cero e Inundar a uno.

**Dónde encontrarlo:** Pestaña BoneCraft → Piel → Herramientas de peso; también Pesas → BoneCraft y Estante de herramientas → Pesas → BoneCraft

---

### Deformar vs Controlar

**Qué hace:** Clasifica los huesos de la rig en huesos deformados (mueven la malla) y huesos de control (el animador los mueve), etiqueta huesos deformados, les cambia el nombre a un nombre deformado y exporta un esqueleto solo deformado.

**Dónde encontrarlo:** Pestaña BoneCraft, en modo Pose → Deformar vs Control

---

### Delta Mush

**Qué hace:** Una deformación suavizante que reduce los pellizcos en las articulaciones. La malla mantiene su forma en reposo pero se deforma más limpiamente en movimiento.

**Cómo utilizar:** Haga clic en**Add Delta Mush** para agregar el modificador y vincularlo al resto de la forma. Inmediatamente después, configure**Iterations**,**Smooth Strength**,**Pin Borders** y**Only Smooth Deform** en Ajustar última operación. Una vez que existe el modificador, el panel muestra**Rebind** y**Remove**, con un pliegue de Configuración que contiene las iteraciones del modificador, la fuerza de suavizado y los controles de fijación de bordes.

**Dónde encontrarlo:** Pestaña BoneCraft, en Modo Objeto con una malla seleccionada → Delta Mush

---

### Envoltura por Proximidad

**Qué hace:** Hace que una malla siga la superficie de otra, como una segunda piel. Útil para prendas que abrazan el cuerpo.

**Cómo utilizar:** seleccione la malla de destino, elija un**Driver Mesh** diferente y luego haga clic en**Bind Proximity Wrap**. Mantenga la armadura del conductor en su posición de reposo al realizar el atado. Las Opciones se pliegan debajo del botón y enumeran**Falloff Type** y**Max Distance**; en 9.1.2 estos valores se almacenan con la configuración pero no cambian su enlace de Deformación de Superficie. Una vez encuadernado, el panel muestra**Rebind** y**Unbind**. Desvincular desactiva el modificador en la ventana gráfica y renderiza; no lo elimina.

**Dónde encontrarlo:** Pestaña BoneCraft, en Modo Objeto con una malla seleccionada → Ajuste de proximidad

---

## Controles de rig

Estas herramientas aparecen en la pestaña BoneCraft en Modo Pose.

---

### Cambio de Espacio

**Qué hace:** Cambia el espacio que sigue un hueso durante la animación. Una mano que sostiene un objeto puede pasar de seguir el cuerpo a quedarse quieto en el mundo con un solo clic.

**Controles clave:**
- **Add Space** y**Remove Space** (icono X en Administrar espacios): los espacios que puede seguir un hueso (Mundo, Origen u otro hueso)
- Un botón por espacio, que lleva su nombre; el espacio actual está marcado ●. Haga clic en el botón de otro espacio para cambiarle el hueso.

**Dónde encontrarlo:** Pestaña BoneCraft, en modo Pose → Cambio espacial

---

### Spline IK

**Qué hace:** Hace que una cadena de huesos siga una curva. Se utiliza para colas, tentáculos, cuerdas, pelo largo y espinas que necesitan un movimiento suave y amplio.

**Cómo utilizar:** Active el hueso inicial y luego haga clic en**Generate Spline IK**. Configure**Chain Length**,**Curve Resolution**,**Stretch** y**Volume Preservation** en Ajustar última operación.**Remove Spline IK** elimina la configuración.

**Dónde encontrarlo:** Pestaña BoneCraft, en modo Pose → Spline IK

---

### Dinámica de Cadena

**Qué hace:** Movimiento secundario similar a la física en una cadena ósea: los huesos se quedan atrás cuando el padre se mueve y rebotan cuando se detiene. Se utiliza para mechones de cabello, colas y accesorios.

**Cómo utilizar:** seleccione la cadena de hueso y haga clic en**Add Chain Dynamics**. Configure**Stiffness**,**Damping**,**Mass** y**Gravity Scale** en Ajustar última operación. El panel también enumera los parámetros en un pliegue de Configuración debajo de la acción. Una vez que existe la dinámica, muestra**Bake** y**Remove**. La colisión utiliza una forma de esfera simplificada, por lo que es posible que las superficies cóncavas no colisionen correctamente.

**Dónde encontrarlo:** Pestaña BoneCraft, en modo Pose → Dinámica de cadena

---

### Cinta

**Qué hace:** Forma una cinta de Bendy Bones (huesos que se curvan y giran suavemente) para labios, cejas, cinturones y otras áreas curvas suaves.

**Cómo utilizar:** Seleccione la cadena de huesos y haga clic en**Generate Ribbon**, luego configure**Control Bones** y**Ribbon Width** en Ajustar última operación.**Remove Ribbon** elimina la configuración.

**Dónde encontrarlo:** Pestaña BoneCraft, en Modo Pose → Cinta

---

### Biblioteca de Visemas

**Qué hace:** Crea y administra conjuntos de visemas (formas de boca) vinculados a claves de formas y genera claves de sincronización de labios a partir de texto. Para el mapeo de visema VRChat, utilice el mapeo de visema VRChat; para generar visemas desde cero utilice la sección CATS Visemes.

**Controles clave:**
- **New Set** y**Delete**: crear o eliminar un conjunto de visemas
- En cada conjunto, un botón por visema (con un ícono de altavoz) lo muestra como vista previa
- Lip Sync: texto a teclas de visema, con fotogramas por fonema y suavizado

**Dónde encontrarlo:** Pestaña BoneCraft, con una armadura seleccionada → Biblioteca Viseme

---

### Clave Conducida por Conjunto

**Qué hace:** Vincula un valor a otro sin expresiones de Python. Posicione al conductor (por ejemplo, el hueso de una ceja), establezca el valor impulsado (por ejemplo, una tecla de forma "Ceja levantada") y registre el punto; BoneCraft construye la curva del conductor.

**Controles clave:**
- **Driver Bone** y**Driver Attribute**: qué impulsa
- **Target Bone** y**Target Attribute**: qué se impulsa
- **Set Value** y**Record Point**: registran un punto en la curva
- **Create SDK**: crea el controlador

**Dónde encontrarlo:** Pestaña BoneCraft, en modo Pose → Establecer clave impulsada

---

### Validador de Rig

**Qué hace:** Compara tu rig con un conjunto de reglas e informa problemas: nombres, huesos faltantes, restricciones rotas, jerarquía, pesos, controladores que necesitan Python y las reglas de mecanismos. Los nombres de huesos con guiones (como `DEF-upper_arm.L` ) pasan.

**Controles clave:**
- **Run Validation**: ejecuta todas las comprobaciones y enumera los resultados
- **Export Report**: guarda los resultados en un archivo

El Panel de tareas (pestaña BoneCraft → Descripción general → Panel de tareas) muestra una tarea del validador cuando falla una verificación.

**Dónde encontrarlo:** Pestaña BoneCraft → Revisar → Validador de rig

---

### Notas del Rig

**Qué hace:** Notas escritas adjuntas a los huesos de la rig: lo que configuras, recordatorios, notas para los colaboradores.

**Controles clave:** **Add Note** y**Remove** en cada nota. Rig Readme muestra las notas del rig como una página de solo lectura.

**Dónde encontrarlo:** Pestaña BoneCraft → Descripción general → Notas y revisión del rig → Léame del rig

Siguiente: [Constructor de plataformas](06-rig-builder.md)
