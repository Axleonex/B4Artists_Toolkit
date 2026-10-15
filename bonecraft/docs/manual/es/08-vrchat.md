# Herramientas de VRChat

[← Índice](index.md)

## Herramientas de VRChat

Las pestañas seleccionan grupos de herramientas. Setup Rigging, Skin, Review, Avatar Tools y Facial son secciones desplegables dentro de las pestañas, no pestañas distintas. Las rutas siguientes usan las etiquetas inglesas; su traducción depende de Language.

| Herramienta | Ruta |
| --- | --- |
| Humanoid / Hair / Export | CATS → Avatar Tools |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Performance / Clothing / Naming | CATS → VRChat Tools |

Preferencias: Edit → Preferences → Add-ons → BoneCraft → Tabs controla las pestañas. Scene Properties controla por separado los paneles Rig Builder y CATS en Properties → Scene. Show Helpers oculta explicaciones; Language cambia las etiquetas; Tools activa los paquetes. Ctrl+Shift+R abre el panel rápido.

---

### Configurar Huesos Humanoides

Mapea los huesos de tu esqueleto a las ranuras humanoides de VRChat y comprueba el mapeo.

Consulta la [guía 5: mapea tu avatar al sistema corporal de VRChat](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat).

---

### Añadir Física de Cabello

Configura cadenas PhysBone en cabello, orejas, colas y accesorios, con colisionadores.

Consulta la [guía 6: añade física de cabello](02-guides-a.md#guía-6-añade-física-de-cabello).

---

### Adjuntar Ropa

Combina la ropa con el esqueleto de tu avatar y transfiere sus pesos.

Consulta la [guía 7: adjunta ropa que se mueva con tu cuerpo](02-guides-a.md#guía-7-adjunta-ropa-que-se-mueva-con-tu-cuerpo).

---

### VRChat Naming Extras (extras de nombres de VRChat)

**Qué hace:** detecta el estilo de nombres de tu esqueleto y renombra huesos en bloque.

Consulta la [guía 4: corrige los nombres de los huesos de tu avatar](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar).

**Herramientas por lotes:** **Buscar y Reemplazar**, **Añadir Prefijo**, **Eliminar Prefijo**, **Añadir Sufijo**, **Eliminar Sufijo** y **Reemplazo por Regex**

---

### VRChat Viseme Mapping (mapeo de visemas de VRChat)

**Qué hace:** mapea los shape keys de tu malla a los 15 visemas de sincronización labial de VRChat.

Consulta la [guía 8: configura la sincronización labial](03-guides-b.md#guía-8-configura-la-sincronización-labial). Para crear visemas que tu avatar aún no tiene, consulta [Herramientas de CATS: Visemas](09-cats.md#visemas).

**Las 15 ranuras de visemas de VRChat:** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### Verificar Rendimiento

**Qué hace:** mide el rango de rendimiento de VRChat de tu avatar y ofrece correcciones.

Consulta la [guía 9: mejora el rendimiento de tu avatar](03-guides-b.md#guía-9-mejora-el-rendimiento-de-tu-avatar).

**Niveles de rendimiento (de mejor a peor):** Excellent → Good → Medium → Poor → Very Poor

**Herramientas:**
- **Calculate Performance Rank** (calcular rango de rendimiento) — el rango actual, desglosado por polígonos, mallas con skin, ranuras de material, huesos, PhysBones y contactos
- **Eliminar Huesos de Peso Cero**, **Combinar Mallas del Mismo Material**, **Eliminar Shape Keys No Utilizados** y **Eliminar Grupos de Vértices No Utilizados** — las correcciones del optimizador (**Modo Hipotético** muestra lo que cambiarían)
- Decimación VRChat — reduce el número de polígonos según una proporción (**Vista previa** primero, luego **Aplicar**), protegiendo los shape keys

---

### Exportar a VRChat

**Qué hace:** exporta tu avatar terminado como FBX para el SDK de VRChat en Unity. Los shape keys (blend shapes) se conservan, salvo que **Remove Shape Keys** esté activado.

**Configuración:**
- **Folder** (carpeta) — adónde va la exportación
- **Avatar** — el nombre del archivo exportado
- **Sidecar** — escribe además un archivo de ajustes `.bfvrc` para el importador de Unity de BoneCraft
- **Merge Meshes** (combinar mallas) — une las mallas de la copia de exportación en una
- **Separate Clothing** (ropa separada) — mantiene la ropa como mallas separadas
- **Remove Shape Keys** (eliminar shape keys) — aplica los shape keys a la base de la copia de exportación
- **Embed Textures** (incrustar texturas) — empaqueta las texturas en el FBX, para que Unity las encuentre
- **Helper Meshes** (mallas auxiliares) — incluye mallas ocultas o auxiliares; déjalo desactivado para avatares normales

**Botones:** **Exportar a VRChat (Unity)**, **Generar Sidecar**, **Copiar Ruta del Importador** (la ruta del script de importación de Unity de BoneCraft) y **Verificar / Preservar MToon** para materiales VRM. La sección también repite el estado humanoide con **Auto-Map Humanoid** (mapear humanoide automáticamente), **Normalize Names** (normalizar nombres) y **Validar**.

---

### Limpieza

La limpieza de la malla antes de exportar está en las herramientas de CATS: **Corregir Modelo**, **Unir Mallas** y **Aplicar Todas las Transformaciones**. Consulta [Herramientas de CATS](09-cats.md).

---

## Puente VRM

Las herramientas de VRM están en la pestaña **CATS** → **Importar / Exportar** → **VRM / VRoid**. Necesitan el complemento VRM; la sección lo instala (**Instalar Automáticamente desde GitHub**, **Instalar desde .zip en Disco…**, **Abrir Página de Extensiones**).

---

### Importación de VRM y VRoid

**Qué hace:** importa avatares `.vrm` (VRoid Studio, Virtual Cast y otros avatares VRM) con sus materiales, su esqueleto y sus shape keys.

- **Importar VRM…** — un archivo `.vrm`
- **Import VRoid (.vroid / .zip)…** (importar VRoid) — una descarga de VRoid Hub (`.zip`). Un proyecto de VRoid Studio (`.vroid`) muestra una tarjeta que explica cómo exportarlo antes a VRM.

---

### VRM Export (exportación VRM)

**Qué hace:** exporta tu personaje con rig a VRM, o al formato de una aplicación de destino.

**Configuración:**
- **Folder** y **File** (archivo) — adónde va y su nombre; la extensión sigue al destino
- **Destino** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo o Resonite
- **Scope** (alcance) — la armadura activa, o cada armadura con datos VRM
- Skip lint (omitir comprobación) — exportar sin la comprobación del destino; úsalo solo si entiendes el riesgo indicado

Haz clic en **Exportar…**.

---

### VRM Lint (comprobación VRM)

**Qué hace:** comprueba la armadura frente al destino elegido antes de exportar: mapeo humanoide, metadatos VRM, los visemas del destino y lo que espera la aplicación de destino.

**Verificar Ahora** ejecuta la comprobación sin cambiar nada. Los errores bloquean la exportación salvo que omitas la comprobación; los avisos explican lo que la aplicación de destino aún puede importar pero con peor funcionamiento.

Si la comprobación dice que faltan huesos humanoides aunque existen, haz clic en **Fix Humanoid Map** (corregir mapa humanoide): BoneCraft vuelve a detectar las ranuras humanoides y guarda el mapeo, sin renombrar ningún hueso.

**También aquí:** **Convertir SpringBones → PhysBones** (física del cabello de VRoid a VRChat) y **Mapear Visemas VRoid**.

---

## MMD Bridge (puente MMD)

Las herramientas de MMD están en la pestaña **CATS** → **Importar / Exportar** → **MMD / PMX**. Necesitan el complemento mmd_tools; la sección lo instala (**Instalar Automáticamente desde GitHub**, **Install from .zip on Disk...** (instalar desde un .zip en disco)).

---

### MMD Import (importación MMD)

- **Import PMX / PMD...** (importar PMX / PMD) — modelos MMD
- **Import VMD Motion...** (importar movimiento VMD) — animaciones MMD
- **Import VPD Pose...** (importar pose VPD) — poses MMD

---

### MMD Export (exportación MMD)

**Configuración:** la **Folder** y, para cada formato, un nombre de archivo y un alcance (el modelo activo, o cada modelo MMD de la escena): **PMX File** y **PMX Scope**, **VMD File** y **VMD Scope**, **VPD File** y **VPD Scope**.

**Botones:** **Export PMX...** (exportar PMX), **Export VMD Motion...** (exportar movimiento VMD) y **Export VPD Pose...** (exportar pose VPD)

**También aquí:** **Convert Bone Names -> Unity** (convertir nombres de huesos para Unity) y **Convert Physics -> PhysBones** (convertir física a PhysBones).

---

## Game Engine Export (exportación para juegos)

**Qué hace:** exporta para motores de juego con un perfil validado: Unreal (humanoide o universal), humanoide de Unity, humanoide de Godot, y FBX o GLB genéricos. Cada corrección que necesita el perfil se muestra y solo se aplica cuando haces clic en ella, nunca en silencio.

**Configuración:** el **Profile** (perfil), la **Animation** (animación) que incluir, **Root Motion** (movimiento de la raíz), **Interpolation** (interpolación) y la **T-Pose** usada para exportar (por defecto una pose en T para el humanoide de Unity y VRChat).

**Botones:**
- **Check for Export** (comprobar para exportar) — comprueba el rig frente al perfil y enumera lo encontrado
- **Apply Transforms (Fix)** (aplicar transformaciones (corrección)) — una de las correcciones explícitas que puede ofrecer la comprobación
- **Export (Profile)** (exportar (perfil)) — exporta con el perfil

**Dónde está:** pestaña **CATS** → **Importar / Exportar** → **Game Engine Export**

---

## Tablero de Tareas

**Qué hace:** un resumen del rig actual: una puntuación de salud, mejoras rápidas y una lista de tareas que BoneCraft ha encontrado (huesos humanoides que faltan, nombres sin resolver, visemas que faltan, avisos del validador de rig, etc.), agrupadas por categoría.

**Abrir verificación de salud** ahora ejecuta la validación del rig y abre los resultados. Selecciona una armadura o su malla vinculada. **Quick Wins** muestra hasta tres recomendaciones; **Remaining Tasks** no repite esas tarjetas. **Actualizar Tablero de Tareas** vuelve a comprobar.

**Dónde está:** pestaña **BoneCraft** → **Resumen** → **Tablero de Tareas**

---

### Inspector de Huesos

**Qué hace:** muestra en detalle el hueso seleccionado (su nombre, su padre, sus restricciones, sus propiedades personalizadas y sus drivers) y te deja editar propiedades sencillas sin entrar en Modo Edición.

**Dónde está:** pestaña **BoneCraft** → **Revisión** → **Inspector de Huesos**

Siguiente: [Herramientas de CATS](09-cats.md)
