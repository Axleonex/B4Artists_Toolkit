# Primeros pasos

[← Contenidos](index.md)

## ¿Qué es BoneCraft?

BoneCraft es un complemento para Bforartists que te ayuda a manipular personajes y accesorios, y preparar avatares 3D para VRChat, VRoid / VRM y MMD. Agrega paneles y botones que automatizan los pasos más tediosos: construir una rig, pintar pesos, arreglar nombres de huesos, configurar sincronización de labios y seguimiento ocular, y exportar.

**Lo que BoneCraft no puede hacer:**
- No puede modelar ni esculpir la forma del cuerpo de tu avatar.
- No puede crear texturas o materiales desde cero.
- No se puede cargar directamente en VRChat (aún necesita el VRChat Creator Companion/SDK)

---

## BoneCraft y BoneForge

BoneCraft se ejecuta solo en Bforartists (la bifurcación Blender ). Para el Blender estándar hay un complemento independiente, BoneForge, con un conjunto más pequeño de herramientas. Instale uno u otro, nunca ambos. En el estándar Blender, BoneCraft no se carga: muestra un aviso con un botón para obtener Bforartists.

|Área|BoneForge (estándar Blender )|BoneCraft (Bforartists )|
| --- | --- | --- |
|CATS Limpieza de avatar, Combinador de materiales, controles derivados de UVToolkit|Incluido|Incluido|
|Ayudantes de avatar básicos (estilo Mixamo)|Incluido|Incluido|
|Rig Builder: detección de articulaciones, asistente, rig de control, activo humanoide básico|No incluido|Incluido|
|Controles del animador y selector de controles|No incluido|Incluido|
|Mecanismos para utilería y máquinas.|No incluido|Incluido|
|Reorientación avanzada y exportación de juegos basada en perfiles|No incluido|Incluido|

## Instalar BoneCraft

**Lo que necesitas:**
- Bforartists (BoneCraft se prueba en Bforartists 5.2)
- El archivo BoneCraft `.zip`

**Pasos:**

1. Abra Bforartists.
2. Abra **Edit** →**Preferences** →**Add-ons**.
3. Haga clic en **Install from Disk…** y seleccione el archivo BoneCraft `.zip`.
4. Marque la casilla de verificación junto a BoneCraft para habilitarlo.
5. Expanda la entrada de BoneCraft para ver su configuración: **Language**,**Tabs**,**Shelf Width**,**Show Helpers** y la lista**Tools**.

**Deberías ver:** las pestañas BoneCraft y Rig Builder en el estante de herramientas izquierdo (presiona**T**) y la pestaña CATS en la barra lateral derecha (presiona**N**).

## Dónde está cada cosa

BoneCraft agrega tres pestañas a la ventana gráfica 3D:

|Pestaña|Lado predeterminado|Secciones|
| --- | --- | --- |
|BoneCraft |Estante de herramientas izquierdo (presione T)|Descripción general, configuración del rig, máscara, mecanismos, revisión|
|Constructor de rigs|Estante de herramientas izquierdo (presione T)|Constructor de rigs: asistente de rig automática, rig rápida, maniquí|
|CATS |Barra lateral derecha (presione N)|CATS, Herramientas Avatar, Herramientas VRChat, Importar/Exportar|

**Mover una pestaña:** abra**Edit** →**Preferences** →**Add-ons** → BoneCraft →**Tabs**. Cada pestaña tiene un interruptor de presentación y dos botones, izquierda y derecha. Un cambio se aplica de inmediato. Mientras una pestaña está oculta, sus botones izquierdo y derecho se vuelven grises, pero aún funcionan.

**Editor de propiedades:** Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools e Importar/Exportar también se muestran en la pestaña Escena del editor de Propiedades, mientras que**Scene Properties** está activado en Preferencias → Pestañas. Este interruptor se activa. Haga clic en su botón**Show** para ocultar o mostrar todas estas secciones; azul significa que se muestran. No cambia las pestañas de la ventana gráfica ni la pestaña de datos de armadura. Con una armadura seleccionada, las herramientas de armadura de BoneCraft también aparecen en la pestaña Datos de armadura, independientemente de estos interruptores de visibilidad. Las secciones Rig Builder, Mechanisms y CATS utilizan la pestaña Escena en su lugar. Para eliminar una herramienta en todas partes, desactive su paquete en la lista**Tools** o desactive el complemento.

**Ancho de estante:** Comienza a ampliar estantes estrechos. Amplía los estantes que contienen pestañas BoneCraft una vez si están por debajo del mínimo izquierdo o derecho: 240 y 260 píxeles de forma predeterminada, en una escala de interfaz de usuario de 1×. Un estante que luego arrastras para estrecharlo permanece en el ancho elegido. Apague el interruptor para gestionar los anchos usted mismo; sus campos de ancho se vuelven inactivos.

**Menús y pestañas integradas del estante de herramientas:** en 9.1, también puedes acceder a las herramientas desde los menús de encabezado de la ventana gráfica 3D:

|Ubicación|Herramientas|
| --- | --- |
|Agregar → Armadura|Quick Rig, Asistente de Auto-Rig, Maniquí para Active Rig|
|Pose → BoneCraft (Modo Pose)|Herramientas de pose, el selector, colecciones de huesos, configuración y comprobaciones del rig.|
|Pesos → BoneCraft (modo Pintura de peso)|Inundar, reflejar y normalizar pesos|
|Objeto → Mecanismos (modo objeto)|Agregue piezas, uniones y enlaces; movimiento de prueba|
|Estante de herramientas → Pose o pesos → BoneCraft |Botones para posturas comunes o operaciones con peso.|

Los botones del estante Pose y Pesos muestran texto cuando el estante es ancho y se convierten en una cuadrícula de íconos cuando es estrecho. Pase el cursor sobre un ícono para leer su información sobre herramientas. Estos puntos de acceso utilizan las mismas herramientas que las pestañas propias de BoneCraft; su disponibilidad depende de los paquetes de herramientas habilitados.

**Herramientas de ventana gráfica:** Colocar marcadores de rig coloca el siguiente marcador del Asistente de rig automática cuando haces clic en la malla; El mecanismo de construcción inicia una unión guiada o un enlace al hacer clic en una pieza. Consulte [Constructor de plataformas](06-rig-builder.md#asistente-auto-rig) y [Mecanismos](07-mechanisms.md#articulaciones-y-enlaces-un-ejemplo-de-cada) para conocer su configuración y controles.

**Ejecutar primero, ajustar después:** herramientas como Quick Rig, Fit Dropped Rig, Weight Mirror, Weight Transfer, Flood to Custom, Ribbon, Spline IK y Delta Mush se ejecutan al hacer clic. Inmediatamente después, use el panel Ajustar última operación en la ventana gráfica para cambiar sus opciones. Ajústelo antes de ejecutar otra operación. Otros paneles colocan configuraciones opcionales en un pliegue debajo de los botones de acción; expándalo cuando necesites esa configuración. Un panel que necesita una selección diferente puede permanecer visible y explicar qué seleccionar.

**Mostrar ayudas:** BoneCraft explica sus secciones con líneas breves de "qué/cuándo" y notas de "Cómo funciona esto". Desmarca**Show Helpers** en las preferencias del complemento para ocultarlos. En la sección Herramientas de Avatar,**Compact Mode** es un acceso directo para el mismo interruptor.

**Idioma:** la configuración**Language** en las preferencias del complemento cambia los propios paneles de BoneCraft a inglés, 日本語, 한국어, 中文, Français, Português o Español.

**Reparar el modelo primero, siempre:** en la pestaña CATS, comience siempre con**Fix Model** antes que cualquier otra herramienta CATS. La canalización CATS utiliza un libro de contabilidad para realizar un seguimiento de los pasos que ha realizado y cada herramienta le advierte si la ejecuta fuera de servicio. Ver [La tubería CATS](04-cats-pipeline.md).

**Panel rápido:** presione**Ctrl+Shift+R** en la ventana gráfica 3D para abrir el panel de rig de BoneCraft como una ventana emergente debajo del cursor.

---

## ¿Por dónde empiezo?

Elige la descripción que mejor se adapte a ti:

> **"Eres una persona que tiene un archivo de modelo 3D nuevo (archivo FBX, OBJ o Blender ) y desea prepararlo para VRChat desde cero."**
> → Ir a [Guía 1: Obtenga su primer avatar en VRChat](02-guides-a.md#guía-1-lleva-tu-primer-avatar-a-vrchat)

> **"Usted es una persona que creó su avatar en VRoid Studio y exportó un archivo VRM."**
> → Ir a [Guía 2: Traiga un avatar VRoid a VRChat](02-guides-a.md#guía-2-lleva-un-avatar-de-vroid-a-vrchat)

> **"Eres una persona que tiene un modelo MMD (archivo PMX ) y desea utilizarlo en VRChat."**
> → Ir a [Guía 3: Traiga un avatar MMD a VRChat](02-guides-a.md#guía-3-lleva-un-avatar-de-mmd-a-vrchat)

> **"Eres una persona que ya tiene un avatar manipulado pero no lo carga porque los huesos tienen nombres incorrectos."**
> → Ir a [Guía 4: arregla los nombres de los huesos de tu avatar](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar)

> **"Eres una persona que tiene un avatar manipulado y quiere tenerlo completamente listo para VRChat: sincronización de labios, seguimiento ocular, malla limpia, todo a la vez".**
> → Ir a [Guía 13: Prepare su avatar VRChat con CATS](03-guides-b.md#guía-13-prepara-tu-avatar-para-vrchat-con-cats)

> **"Eres una persona que quiere solucionar un problema específico."**
> → Ir al [Índice de solución rápida](10-reference.md#índice-de-soluciones-rápidas)

Siguiente: [Guías 1 a 7](02-guides-a.md)
