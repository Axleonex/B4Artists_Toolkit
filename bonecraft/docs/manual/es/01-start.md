# Primeros pasos

[← Índice](index.md)

## ¿Qué es BoneCraft?

BoneCraft es un complemento para Bforartists que te ayuda a hacer el rig de personajes y accesorios, y a preparar avatares 3D para VRChat, VRoid / VRM y MMD. Añade paneles y botones que automatizan los pasos más tediosos: construir un rig, pintar pesos, corregir nombres de huesos, configurar la sincronización labial y el seguimiento ocular, y exportar.

**Lo que BoneCraft no puede hacer:**
- No puede modelar ni esculpir la forma del cuerpo de tu avatar
- No puede crear texturas ni materiales desde cero
- No puede subir directamente a VRChat (sigues necesitando el VRChat Creator Companion / SDK)

---

## BoneCraft y BoneForge

BoneCraft solo funciona en Bforartists (el fork de Blender). Para Blender estándar hay un complemento aparte, BoneForge, con menos herramientas. Instala uno u otro, nunca los dos. En Blender estándar, BoneCraft no se carga: muestra un único aviso con un botón para conseguir Bforartists.

BoneForge 9.0.0 y posteriores son para Blender estándar. BoneCraft es un complemento distinto para Bforartists. Ambos tienen Auto-Rig Wizard, Quick Rig, Mannequin y herramientas compartidas CATS/Material Atlas. BoneCraft también tiene Mechanisms, Control Picker, rigs de control de producción, detección de articulaciones y exportación por perfiles. La disposición similar no añade esas herramientas a BoneForge.

## Instalar BoneCraft

**Lo que necesitas:**
- Bforartists (BoneCraft está probado en Bforartists 5.2)
- El archivo `.zip` de BoneCraft

**Pasos:**

1. Abre Bforartists.
2. Abre **Editar** (Edit) → **Preferencias** (Preferences) → **Complementos** (Add-ons).
3. Haz clic en **Instalar desde disco…** (Install from Disk…) y elige el archivo `.zip` de BoneCraft.
4. Marca la casilla junto a BoneCraft para activarlo.
5. Despliega la entrada de BoneCraft para ver sus ajustes: **Language**, **Tabs**, **Shelf Width**, **Show Helpers** y la lista **Herramientas**.

**Lo que deberías ver:** las pestañas BoneCraft y Rig Builder en la Tool Shelf izquierda (pulsa **T**) y la pestaña CATS en la barra lateral derecha (pulsa **N**).

## Dónde está cada cosa

Las pestañas seleccionan grupos de herramientas. Setup Rigging, Skin, Review, Avatar Tools y Facial son secciones desplegables dentro de las pestañas, no pestañas distintas. Las rutas siguientes usan las etiquetas inglesas; su traducción depende de Language.

| Pestaña | Ubicación predeterminada | Secciones |
| --- | --- | --- |
| Rig Builder | Tool Shelf izquierda (T) | Auto-Rig Wizard, Quick Rig - premade armatures, Mannequin |
| BoneCraft | Tool Shelf izquierda (T) | Overview, Setup Rigging, Skin, Mechanisms, Review |
| CATS | Barra lateral derecha (N) | CATS, Avatar Tools, VRChat Tools, Import / Export |

| Herramienta | Ruta |
| --- | --- |
| Bone Merge | BoneCraft → Setup Rigging → Bone Merge |
| Delta Mush / Proximity Wrap | BoneCraft → Skin → Delta Mush / Proximity Wrap |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library → Lip Sync |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Humanoid / Hair | CATS → Avatar Tools → Set Up Humanoid Bones / Add Hair Physics |
| VRChat export | CATS → Import / Export → Unity / VRChat |
| VRM / MMD / I/O Hub | CATS → Import / Export → VRM / VRoid, MMD / PMX, Game Engine Export |
| Performance / Clothing / Naming | CATS → VRChat Tools → Check Performance / Attach Clothing / VRChat Naming Extras |

Selecciona un esqueleto para el rig y la biblioteca de visemas; una malla en Modo Objeto para Delta Mush y Proximity Wrap. Lip Sync requiere un esqueleto en Modo Pose. Despliega las secciones con el triángulo. Options contiene ajustes opcionales; ajusta las herramientas de ejecución inmediata en Ajustar última operación antes de ejecutar otra operación.

Hay tres flujos faciales: la generación CATS crea claves de forma de la boca; Viseme Library / Lip Sync guarda poses y genera claves de animación; Facial asigna claves existentes a VRChat o configura seguimiento facial. Los controles derivados de UVToolkit están en CATS → Material Atlas → Override Inherited Settings → UV Packing; son el flujo compartido de atlas, no el complemento UVToolkit completo.

**Mover una pestaña:** Edit → Preferences → Add-ons → BoneCraft → Tabs. Cada pestaña tiene un interruptor y Left / Right; los cambios son inmediatos. Aunque esté oculta y los botones grises, Left / Right siguen funcionando.

**Editor Properties:** Scene Properties → Show en Preferences → Tabs está activado inicialmente; azul significa visible. Controla conjuntamente Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools e Import / Export en Properties → Scene. No cambia las pestañas de vista ni Armature Data. Las herramientas de armadura aparecen también en Armature Data al seleccionar una armadura, de forma independiente. Desactiva un paquete en Tools o el complemento para retirar sus herramientas de todas partes.

**Shelf Width:** Widen Narrow Shelves empieza activado y ensancha una vez las estanterías con pestañas BoneCraft que estén por debajo del mínimo Left / Right: 240 / 260 píxeles a escala UI 1×. Si luego arrastras a menor anchura, conserva tu elección. Desactívalo para gestionar la anchura manualmente; sus campos quedan inactivos.

**Menús de la vista y Tool Shelf nativa:**

| Ubicación | Herramientas |
|---|---|
| Add → Armature | Quick Rig, Auto-Rig Wizard, Mannequin for Active Rig |
| Pose → BoneCraft (Pose Mode) | Poses, selector, colecciones, configuración y comprobaciones del rig |
| Weights → BoneCraft (Weight Paint) | Rellenar, reflejar y normalizar pesos |
| Object → Mechanisms (Object Mode) | Piezas, articulaciones, vínculos y pruebas de movimiento |
| Tool Shelf → Pose / Weights → BoneCraft | Operaciones habituales de pose o pesos |

Los botones de Pose y Weights muestran texto con suficiente anchura y una cuadrícula de iconos al estrecharse; pasa el puntero para ver la ayuda. Usan las mismas herramientas y dependen de los paquetes activados.

**Herramientas de vista:** Place Rig Markers coloca el siguiente marcador del asistente al pulsar la malla. Build Mechanism inicia una articulación o vínculo guiado al pulsar una pieza. Consulta [Constructor de Rig](06-rig-builder.md#asistente-auto-rig) y [Mechanisms](07-mechanisms.md).

**Ejecutar primero y ajustar después:** Quick Rig, Fit Dropped Rig, Weight Mirror, Weight Transfer, Flood to Custom, Ribbon, Spline IK y Delta Mush se ejecutan al pulsar. Cambia sus opciones inmediatamente en Adjust Last Operation, antes de otra operación. Otros paneles guardan ajustes opcionales en desplegables bajo los botones; un panel puede seguir visible y explicar qué seleccionar.

**Show Helpers:** oculta las explicaciones «qué/cuándo» y «How this works» al desactivarlo en preferencias. Compact Mode de Avatar Tools es otro acceso al mismo interruptor.

**Language:** cambia los paneles de BoneCraft a English, 日本語, 한국어, 中文, Français, Português o Español.

**Fix Model primero:** en CATS comienza siempre con Fix Model. El registro del pipeline recuerda los pasos y advierte si se ejecutan fuera de orden. Consulta [El pipeline de CATS](04-cats-pipeline.md).

**Panel rápido:** Ctrl+Shift+R en la vista 3D abre el panel de rig bajo el cursor.

---

## ¿Por dónde empiezo?

Elige la descripción que mejor encaje contigo:

> **«Tienes un archivo de modelo 3D totalmente nuevo (FBX, OBJ o archivo de Blender) y quieres hacerle el rig para VRChat desde cero.»**
> → Ve a la [guía 1: lleva tu primer avatar a VRChat](02-guides-a.md#guía-1-lleva-tu-primer-avatar-a-vrchat)

> **«Has creado tu avatar en VRoid Studio y has exportado un archivo VRM.»**
> → Ve a la [guía 2: lleva un avatar de VRoid a VRChat](02-guides-a.md#guía-2-lleva-un-avatar-de-vroid-a-vrchat)

> **«Tienes un modelo de MMD (archivo PMX) y quieres usarlo en VRChat.»**
> → Ve a la [guía 3: lleva un avatar de MMD a VRChat](02-guides-a.md#guía-3-lleva-un-avatar-de-mmd-a-vrchat)

> **«Ya tienes un avatar con rig, pero no se sube porque los huesos tienen nombres incorrectos.»**
> → Ve a la [guía 4: corrige los nombres de los huesos de tu avatar](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar)

> **«Tienes un avatar con rig y quieres dejarlo totalmente listo para VRChat: sincronización labial, seguimiento ocular y malla limpia, todo de una vez.»**
> → Ve a la [guía 13: prepara tu avatar para VRChat con CATS](03-guides-b.md#guía-13-prepara-tu-avatar-para-vrchat-con-cats)

> **«Quieres resolver un problema concreto.»**
> → Ve al [Índice de soluciones rápidas](10-reference.md#índice-de-soluciones-rápidas)

Siguiente: [Guías 1–7](02-guides-a.md)
