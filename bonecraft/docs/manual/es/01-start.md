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

| Área | BoneForge (Blender estándar) | BoneCraft (Bforartists) |
| --- | --- | --- |
| Limpieza de avatares CATS, Material Combiner, controles derivados de UVToolkit | Incluido | Incluido |
| Ayudas básicas para avatares (estilo Mixamo) | Incluido | Incluido |
| Constructor de Rig: detección de articulaciones, asistente, rig de control, asset Basic Humanoid | No incluido | Incluido |
| Controles de animador y el Control Picker | No incluido | Incluido |
| Mechanisms para accesorios y máquinas | No incluido | Incluido |
| Redireccionamiento avanzado y exportación para juegos por perfiles | No incluido | Incluido |

## Instalar BoneCraft

**Lo que necesitas:**
- Bforartists (BoneCraft está probado en Bforartists 5.2)
- El archivo `.zip` de BoneCraft

**Pasos:**

1. Abre Bforartists.
2. Abre **Editar** (Edit) → **Preferencias** (Preferences) → **Complementos** (Add-ons).
3. Haz clic en **Instalar desde disco…** (Install from Disk…) y elige el archivo `.zip` de BoneCraft.
4. Marca la casilla junto a BoneCraft para activarlo.
5. Despliega la entrada de BoneCraft para ver sus ajustes: **Tabs** (pestañas), **Show Helpers** (mostrar ayudas), **Language** (idioma) y la lista **Herramientas**.

**Lo que deberías ver:** las pestañas BoneCraft y Rig Builder en la Tool Shelf izquierda (pulsa **T**) y la pestaña CATS en la barra lateral derecha (pulsa **N**).

## Dónde está cada cosa

BoneCraft añade tres pestañas a la vista 3D:

| Pestaña | Lado predeterminado | Secciones |
| --- | --- | --- |
| BoneCraft | Tool Shelf izquierda (pulsa T) | Resumen, Configurar Rigging, Malla, Mechanisms, Revisión |
| Rig Builder | Tool Shelf izquierda (pulsa T) | Constructor de Rig: Quick Rig, Asistente Auto-Rig, Maniquí |
| CATS | Barra lateral derecha (pulsa N) | CATS, VRChat, Importar / Exportar |

**Mover una pestaña:** abre **Editar** → **Preferencias** → **Complementos** → BoneCraft → **Tabs**. Cada pestaña tiene un interruptor para mostrarla y dos botones, Left (izquierda) y Right (derecha). El cambio se aplica al momento. Mientras una pestaña está oculta, sus botones Left y Right se ven en gris, pero siguen funcionando.

**Siempre en el editor de Propiedades:** el Constructor de Rig, Mechanisms, CATS, VRChat e Importar / Exportar también se muestran en la pestaña Escena del editor de Propiedades, sea cual sea la selección. Con una armadura seleccionada, las secciones de BoneCraft también se muestran en la pestaña de datos de la armadura. Los interruptores para mostrar nunca ocultan estas copias. Para quitar una herramienta de todas partes, desactiva su paquete en la lista **Herramientas**, o desactiva el complemento.

**Show Helpers (mostrar ayudas):** BoneCraft explica sus secciones con líneas breves de «qué / cuándo» y notas «How this works» (cómo funciona). Desmarca **Show Helpers** en las preferencias del complemento para ocultarlas. En la sección VRChat, **Modo Compacto** es un atajo al mismo interruptor.

**Idioma:** el ajuste **Language** (idioma) de las preferencias del complemento cambia los paneles propios de BoneCraft a English, 日本語, 한국어, 中文, Français, Português o Español.

**Corregir Modelo primero, siempre:** en la pestaña CATS, empieza siempre con **Corregir Modelo** antes que cualquier otra herramienta de CATS. El pipeline de CATS lleva un registro de los pasos que has hecho, y cada herramienta te avisa si la ejecutas fuera de orden. Consulta [El pipeline de CATS](04-cats-pipeline.md).

**Panel rápido:** pulsa **Ctrl+Shift+R** en la vista 3D para abrir el panel de rig de BoneCraft como ventana emergente bajo el cursor.

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
