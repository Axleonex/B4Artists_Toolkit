# Herramientas de VRChat

[← Contenidos](index.md)

## Herramientas de VRChat

Las herramientas VRChat están en la pestaña **CATS** en la barra lateral derecha (presione**N**), en la sección**Avatar Tools**. Sus subsecciones cubren huesos humanoides, física del cabello, mapeo de visemas y exportación. La sección separada**VRChat Tools** debajo agrupa las utilidades de rendimiento, ropa y nombres. La misma sección está en la pestaña**Properties** del editor**Scene** mientras Preferencias → Pestañas → Propiedades de escena → Mostrar está activado. Este modificador no oculta la pestaña de la ventana gráfica CATS.

---

### Configurar Huesos Humanoides

Asigna los huesos de tu esqueleto a las ranuras humanoides de VRChat y verifica el mapeo.

Ver [Guía 5: Asigne su avatar al sistema corporal de VRChat](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat).

---

### Añadir Física de Cabello

Configura cadenas PhysBone en cabello, orejas, colas y accesorios, con colisionadores.

Ver [Guía 6: Agregar la física del cabello](02-guides-a.md#guía-6-añade-física-de-cabello).

---

### Adjuntar Ropa

**Dónde encontrarlo:** Pestaña CATS → VRChat Herramientas → Ropa

Fusiona ropa con el esqueleto de tu avatar y transfiere su peso.

Ver [Guía 7: Coloque ropa que se mueva con su cuerpo](02-guides-a.md#guía-7-adjunta-ropa-que-se-mueva-con-tu-cuerpo).

---

### VRChat Naming Extras (extras de nombres de VRChat)

**Dónde encontrarlo:** Pestaña CATS → Herramientas VRChat → Nomenclatura

**Qué hace:** Detecta el estilo de denominación de tu esqueleto y cambia el nombre de los huesos de forma masiva.

Ver [Guía 4: arregla los nombres de los huesos de tu avatar](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar).

**Herramientas por lotes:** **Find and Replace**,**Add Prefix**,**Remove Prefix**,**Add Suffix**,**Remove Suffix** y**Regex Replace**

---

### VRChat Viseme Mapping (mapeo de visemas de VRChat)

**Qué hace:** Asigna las claves de forma de tu malla a los 15 visemas de sincronización de labios de VRChat.

Ver [Guía 8: Configurar sincronización de labios](03-guides-b.md#guía-8-configura-la-sincronización-labial). Para crear visemas que tu avatar aún no tiene, consulta [CATS Herramientas: Visemas](09-cats.md#visemas).

**VRChat 15 ranuras de visema:** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### Verificar Rendimiento

**Dónde encontrarlo:** Pestaña CATS → Herramientas VRChat → Rendimiento

**Qué hace:** Mide el rango de rendimiento VRChat de tu avatar y ofrece correcciones.

Ver [Guía 9: Mejora el rendimiento de tu avatar](03-guides-b.md#guía-9-mejora-el-rendimiento-de-tu-avatar).

**Niveles de rendimiento (de mejor a peor):** Excelente → Bueno → Medio → Deficiente → Muy deficiente

**Herramientas:**
- **Calculate Performance Rank**: el rango actual, con un desglose por polígonos, mallas sin piel, ranuras de material, huesos, PhysBones y contactos.
- **Remove Zero-Weight Bones**,**Merge Same-Material Meshes**,**Remove Unused Shape Keys** y**Remove Unused Vertex Groups**: las correcciones del optimizador (**What-If Mode** muestra lo que cambiarían)
- VRChat Decimación: reduce el recuento de polígonos en una proporción (**Preview** primero, luego**Apply** ), manteniendo seguras las claves de forma.

---

### Exportar a VRChat

**Qué hace:** Exporta su avatar terminado como FBX para el SDK VRChat en Unity. Las claves de forma (mezcla de formas) se mantienen a menos que**Remove Shape Keys** esté activado.

**Configuración:**
- **Folder**: hacia dónde va la exportación
- **Avatar**: el nombre del archivo exportado
- **Sidecar**: también escribe un archivo de configuración `.bfvrc` para el importador Unity de BoneCraft.
- **Merge Meshes**: une las mallas de la copia de exportación en una sola
- **Separate Clothing**: mantiene la ropa como mallas separadas
- **Remove Shape Keys**: aplica las claves de forma a la base de la copia de exportación
- **Embed Textures**: empaqueta las texturas en FBX, para que Unity las encuentre.
- **Helper Meshes**: incluye mallas ocultas o auxiliares; déjalo apagado para avatares normales

**Botones:** **Export to VRChat (Unity)**,**Generate Sidecar**,**Copy Importer Path** (la ruta del script de importación Unity de BoneCraft ) y**Check / Preserve MToon** para materiales VRM. La sección también repite el estado humanoide con**Auto-Map Humanoid**,**Normalize Names** y**Validate**.

---

### Limpieza

La limpieza de malla antes de la exportación se encuentra en las herramientas CATS: **Fix Model**,**Join Meshes** y**Apply All Transforms**. Ver [Herramientas CATS](09-cats.md).

---

## Puente VRM

Las herramientas VRM se encuentran en la pestaña **CATS** →**Import / Export** →**VRM / VRoid**. Necesitan el complemento VRM; la sección lo instala (**Auto-Install Latest from GitHub**,**Install from.zip on Disk…**,**Open Extensions Page** ).

---

### Importación de VRM y VRoid

**Qué hace:** Importa avatares `.vrm` (VRoid Studio, Virtual Cast y otros avatares VRM ) con sus materiales, esqueleto y claves de forma.

- **Import VRM…** — un archivo `.vrm`
- **Import VRoid (.vroid /.zip)…**: una descarga del concentrador VRoid (`.zip` ). Un proyecto de VRoid Studio (`.vroid` ) muestra una tarjeta que explica cómo exportarlo primero a VRM.

---

### VRM Export (exportación VRM)

**Qué hace:** Exporta tu personaje manipulado a VRM o al formato de una aplicación de destino.

**Configuración:**
- **Folder** y**File**: dónde va y su nombre; la extensión sigue el objetivo
- **Target** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo o Resonite
- **Scope**: la armadura activa o cada armadura con datos VRM
- Saltar pelusa: exportar sin la verificación de destino; Úselo sólo cuando comprenda el riesgo informado.

Haga clic en **Export…**.

---

### VRM Lint (comprobación VRM)

**Qué hace:** Comprueba la armadura con el objetivo elegido antes de exportar: mapeo humanoide, metadatos VRM, visemas del objetivo y expectativas de la aplicación de destino.

**Lint Now** ejecuta la verificación sin cambiar nada. Los errores bloquean la exportación a menos que te saltes la pelusa; Las advertencias explican lo que la aplicación de destino aún puede importar pero que funciona peor.

Si la pelusa dice que faltan huesos humanoides aunque existen, haga clic en **Fix Humanoid Map**: BoneCraft detecta las ranuras humanoides nuevamente y guarda el mapeo, sin cambiar el nombre de ningún hueso.

**También aquí:** **Convert SpringBones → PhysBones** (física del cabello de VRoid a VRChat ) y**Map VRoid Visemes**.

---

## MMD Bridge (puente MMD)

Las herramientas MMD se encuentran en la pestaña **CATS** →**Import / Export** →**MMD / PMX**. Necesitan el complemento mmd_tools; la sección lo instala (**Auto-Install Latest from GitHub**,**Install from.zip on Disk...** ).

---

### MMD Import (importación MMD)

- Modelos **Import PMX / PMD...** — MMD
- **Import VMD Motion...** — Animaciones MMD
- **Import VPD Pose...** — MMD posa

---

### MMD Export (exportación MMD)

**Configuración:** el**Folder**, luego para cada formato un nombre de archivo y un alcance (el modelo activo, o cada modelo MMD en la escena):**PMX File** y**PMX Scope**,**VMD File** y**VMD Scope**,**VPD File** y**VPD Scope**.

**Botones:** **Export PMX...**,**Export VMD Motion...** y**Export VPD Pose...**

**También aquí:** **Convert Bone Names -> Unity** y**Convert Physics -> PhysBones**.

---

## Game Export (exportación para juegos)

**Qué hace:** Exportaciones para motores de juegos con un perfil validado: Unreal (humanoide o universal), humanoide Unity, humanoide Godot y FBX o GLB genérico. Cada corrección que necesita el perfil se muestra y se aplica solo cuando haces clic en él, nunca de forma silenciosa.

**Configuración:** **Profile**,**Animation** para incluir,**Root Motion**,**Interpolation** y**T-Pose** utilizados para exportar (de forma predeterminada, una pose en T para Unity humanoide y VRChat ).

**Botones:**
- **Check for Export**: compara el rig con el perfil y enumera los hallazgos
- **Apply Transforms (Fix)**: una de las soluciones explícitas que puede ofrecer el cheque
- **Export (Profile)** — exporta con el perfil

**Dónde encontrarlo:** Pestaña**CATS** →**Import / Export** →**Game Export**

---

## Tablero de Tareas

**Qué hace:** Un resumen de la rig actual: una puntuación de salud, ganancias rápidas y una lista de tareas que encontró BoneCraft (huesos humanoides faltantes, nombres no resueltos, visemas faltantes, advertencias del validador de rig, etc.), agrupadas por categoría.**Open Health Check** abre los detalles;**Refresh Task Board** vuelve a comprobarlo.

**Dónde encontrarlo:** Pestaña**BoneCraft** →**Overview** →**Task Board**

---

### Inspector de Huesos

**Qué hace:** Muestra el hueso seleccionado en detalle (su nombre, padre, restricciones, propiedades personalizadas y controladores) y le permite editar propiedades simples sin ingresar al modo de edición.

**Dónde encontrarlo:** Pestaña**BoneCraft** →**Review** →**Bone Inspector**

Siguiente: [Herramientas CATS](09-cats.md)
