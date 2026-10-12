# Soluciones rápidas y glosario

[← Índice](index.md)

## Índice de soluciones rápidas

Usa esta sección cuando algo haya salido mal y necesites la respuesta rápido.

| Problema | Dónde mirar |
|---|---|
| La subida falla — huesos no reconocidos | [Guía 4](02-guides-a.md#guía-4-corrige-los-nombres-de-los-huesos-de-tu-avatar) + [VRChat Naming Extras](08-vrchat.md#vrchat-naming-extras-extras-de-nombres-de-vrchat) |
| Avatar en pose en T / no sigue el movimiento | [Guía 5](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat) + [Configurar Huesos Humanoides](08-vrchat.md#configurar-huesos-humanoides) |
| La malla se deforma de forma rara / la piel se estira | [Transferencia de pesos](05-rig-tools.md#transferencia-de-pesos) + [Espejo de Pesos](05-rig-tools.md#espejo-de-pesos), o recalcula con el [Recálculo automático de pesos de huesos](05-rig-tools.md#recálculo-automático-de-pesos-de-huesos) |
| Un lado del cuerpo tiene pesos distintos | [Espejo de Pesos](05-rig-tools.md#espejo-de-pesos) |
| El cabello atraviesa la cabeza | [Guía 6, paso 5](02-guides-a.md#paso-5--añadir-colisionadores-recomendado) — añade colisionadores |
| La física del cabello no se mueve | [Guía 6](02-guides-a.md#guía-6-añade-física-de-cabello) — comprueba la detección de cadenas y el preajuste PhysBone |
| La ropa atraviesa el cuerpo | [Guía 7](02-guides-a.md#guía-7-adjunta-ropa-que-se-mueva-con-tu-cuerpo) — ejecuta **Detectar colisiones** |
| La sincronización labial no funciona | [Guía 8](03-guides-b.md#guía-8-configura-la-sincronización-labial) + [VRChat Viseme Mapping](08-vrchat.md#vrchat-viseme-mapping-mapeo-de-visemas-de-vrchat) |
| El avatar tiene rendimiento Very Poor | [Guía 9](03-guides-b.md#guía-9-mejora-el-rendimiento-de-tu-avatar) + [Verificar Rendimiento](08-vrchat.md#verificar-rendimiento) |
| La importación de VRM falla | [Guía 2, paso 1](02-guides-a.md#paso-1--instalar-el-complemento-vrm) — instala el complemento VRM |
| La importación de MMD falla | [Guía 3, paso 1](02-guides-a.md#paso-1--instalar-mmd_tools) — instala mmd_tools |
| El validador de rig muestra errores | [Validador de Rig](05-rig-tools.md#validador-de-rig) — ejecuta la validación y sigue los mensajes |
| Los huesos han desaparecido / no se ve ningún hueso | [Colecciones de huesos](05-rig-tools.md#colecciones-de-huesos) → **Show All Collections** (mostrar todas las colecciones) |
| No encuentras los paneles de BoneCraft | BoneCraft y Rig Builder están en la Tool Shelf izquierda (pulsa T), CATS en la barra lateral derecha (pulsa N) — consulta [Dónde está cada cosa](01-start.md#dónde-está-cada-cosa) |
| Una pestaña está en el lado equivocado | Preferencias → Complementos → BoneCraft → Tabs → Left (izquierda) o Right (derecha) |
| Exportación bloqueada: se indican huesos humanoides que faltan aunque existen | Ejecuta **Mapear Todo Automáticamente** y luego **Fix Humanoid Map** (corregir mapa humanoide) en la comprobación de la sección VRM / VRoid. Si un hueso obligatorio de verdad no existe, el rig necesita tenerlo primero: consulta la [guía 5](02-guides-a.md#guía-5-mapea-tu-avatar-al-sistema-corporal-de-vrchat) |
| El FBX exportado muestra formas auxiliares o tubos gigantes | Deja **Helper Meshes** (mallas auxiliares) desactivado salvo que necesites mallas de control o de formas personalizadas |
| Unity o Unreal importan materiales grises | Exporta con **Embed Textures** (incrustar texturas) activado y luego usa las opciones de importación/extracción de materiales de Unity o la importación de materiales FBX de Unreal |
| Todos los pesos están en los huesos equivocados | Vuelve a ejecutar **Generar rig** del asistente, usa la [Transferencia de pesos](05-rig-tools.md#transferencia-de-pesos), o **Smart Automatic Weights** (pesos automáticos inteligentes) en la pestaña CATS |
| Dos rigs tienen que ser uno | [Guía 11: une dos rigs](03-guides-b.md#guía-11-une-dos-rigs) |
| Una forma correctiva no se activa | Comprueba el eje del hueso y el ángulo en [Shape keys correctivos](05-rig-tools.md#shape-keys-correctivos) |
| La animación se ve mal en otro rig | [Redireccionar](05-rig-tools.md#redireccionar) — comprueba el mapeo de huesos |
| Una herramienta de CATS avisa «Run Fix Model first» | Ejecuta **Corregir Modelo** — [El pipeline de CATS](04-cats-pipeline.md) |
| La boca se rasga o se parte al hablar | Se saltó **Corregir Modelo** — vuelve a ejecutar desde la fase 1 — [Guía 13, fase 1](03-guides-b.md#fase-1--corregir-modelo) |
| Los ojos del avatar se quedan mirando hacia abajo en VRChat | El seguimiento ocular se ejecutó antes de **Corregir Modelo** — vuelve a ejecutar desde **Corregir Modelo** — [CATS: Seguimiento Ocular](09-cats.md#seguimiento-ocular) |
| Un shape key hace estallar la malla al activarse | **Pose a Shape Key** se ejecutó antes de **Corregir Modelo** — vuelve a ejecutar desde **Corregir Modelo** — [CATS: Pose y Shape Keys](09-cats.md#pose-y-shape-keys) |
| El avatar aparece con el tamaño equivocado en VRChat | Las transformaciones se aplicaron antes de terminar el pipeline — reimporta desde el archivo de origen y empieza de nuevo con **Corregir Modelo** |
| Los nombres de los huesos están en japonés / chino / coreano | [CATS: Traducir Nombres de Huesos](09-cats.md#traducir-nombres-de-huesos) |
| El avatar no tiene sincronización labial ni shape keys de boca | [CATS: Visemas](09-cats.md#visemas) — genera 15 visemas a partir de 3 formas base |
| Un mecanismo muestra «changed by hand» | [Mechanisms (mecanismos)](07-mechanisms.md) — usa **Keep mine** (conservar lo mío) o **Restaurar** |

## Glosario

**Armadura (Armature):** la palabra de Bforartists para un esqueleto: un conjunto de huesos que se puede posar y animar.

**Blend shape:** consulta Shape key.

**Hueso (Bone):** un segmento de un esqueleto. Los huesos forman una jerarquía (padre → hijo) en la que los huesos hijos siguen a sus padres.

**Colección de huesos (Bone collection):** un grupo de huesos con nombre. Puedes mostrar u ocultar una colección entera de una vez.

**CATS:** las herramientas de CATS: preparación de modelos para VRChat con un pipeline guiado (limpieza, visemas, seguimiento ocular, transformaciones). Están en la pestaña CATS.

**Pipeline de CATS (CATS pipeline):** el orden en seis fases de las herramientas de CATS: Corregir Modelo → Atlas de Materiales → Visemas → Seguimiento Ocular → Pose a Shape Key → Aplicar transformaciones. Las herramientas avisan cuando una fase anterior de la que dependen no está hecha.

**Shape key correctivo (Corrective shape key):** un shape key que se activa cuando un hueso alcanza un ángulo, para corregir la malla en poses extremas.

**Hueso de deformación (Deform bone):** un hueso que mueve la malla. No todos los huesos deforman; algunos son solo controles.

**Seguimiento ocular (Eye tracking):** la herramienta de CATS que configura los huesos de los ojos (`LeftEye`, `RightEye`) y las restricciones de rotación que VRChat usa para mover los ojos.

**FBT (Full Body Tracking):** una función de VRChat que sigue todo tu cuerpo con hardware adicional (como Vive Trackers), incluidas las caderas y los pies. **Corregir FBT** ajusta el hueso raíz para ello.

**FBX:** un formato de archivo que lleva modelos 3D, esqueletos y animaciones entre programas. El formato estándar para VRChat.

**Corregir Modelo (Fix Model):** la limpieza de CATS: vértices duplicados, geometría suelta y normales incorrectas. Siempre el primer paso de CATS.

**FK (cinemática directa, Forward Kinematics):** posar girando por turnos cada hueso de una cadena: hombro, luego codo, luego muñeca. Natural para poses amplias del cuerpo.

**IK (cinemática inversa, Inverse Kinematics):** posar colocando el extremo de una cadena (una mano o un pie); los huesos intermedios lo siguen. Natural para colocar con precisión manos y pies.

**Humanoide (Humanoid):** el sistema de avatares de VRChat que mapea los huesos a ranuras estándar del cuerpo, para que todos los avatares usen los mismos controles de movimiento.

**Mecanismo (Mechanism):** un rig para un accesorio o una pieza de máquina: una articulación (Hinge, Slide, Telescope) o un enlace (Piston, Gear Link, Follow), construido con huesos y restricciones normales. Consulta [Mechanisms (mecanismos)](07-mechanisms.md).

**Malla (Mesh):** la superficie 3D que forma el cuerpo visible de tu avatar.

**MMD (MikuMikuDance):** un programa gratuito de animación 3D popular en Japón y en la comunidad de anime. Usa archivos de modelo `.pmx` y archivos de animación `.vmd`.

**Morph target:** consulta Shape key.

**Registro de Operaciones (Operation Ledger):** la lista de CATS con cada operación que has ejecutado, con su hora y su resultado.

**PhysBone:** el componente de VRChat que hace que los huesos se balanceen, reboten y choquen. Se usa para cabello, colas y accesorios colgantes.

**Estado del Pipeline (Pipeline Status):** la lista de CATS de las seis fases, con una marca en cada fase terminada.

**PMX:** el formato principal de modelos 3D de MikuMikuDance.

**Modo Pose (Pose Mode):** el modo para posar y animar huesos. Selecciona la armadura y pulsa Ctrl+Tab, o usa el menú desplegable de modos de arriba a la izquierda de la vista.

**Rig / rigging:** construir un esqueleto dentro de un modelo 3D y conectar la malla a él para poder posarlo y animarlo.

**Shape key:** una versión guardada de una malla en una posición deformada. Los shape keys se mezclan con distintas intensidades; mueven las expresiones faciales, la sincronización labial y los cambios de forma del cuerpo.

**SDK (Software Development Kit):** en VRChat, el VRChat Creator Companion y sus herramientas de Unity para subir avatares.

**Spline IK:** una cadena de huesos que sigue una curva. Se usa para colas, tentáculos, cabello largo y columnas.

**Pose en T (T-pose):** una pose de referencia: de pie y con los brazos estirados a los lados.

**Tool Shelf:** el panel del lado izquierdo de la vista 3D (pulsa T), donde están por defecto las pestañas BoneCraft y Rig Builder.

**Vértice (Vertex):** un solo punto en el espacio 3D. Las mallas están hechas de muchos vértices unidos por aristas y caras.

**Grupo de vértices (Vertex group):** un conjunto de vértices con nombre; define qué vértices mueve un hueso.

**Visema (Viseme):** una forma de boca para un sonido del habla. VRChat usa 15 visemas para la sincronización labial.

**Peso / pintura de pesos (Weight / weight painting):** valores de 0.0 a 1.0 que dicen con cuánta fuerza mueve cada hueso cada vértice. La pintura de pesos es la forma visual de ajustarlos.

**Asistente (Wizard):** el Asistente Auto-Rig del Constructor de Rig: coloca marcadores en tu malla y construye el rig a partir de ellos.

**Hueso de peso cero (Zero-weight bone):** un hueso que no mueve ningún vértice. Cuesta rendimiento sin cambiar el aspecto del avatar; **Corregir Modelo** y el optimizador de rendimiento los eliminan.

Siguiente: [Novedades](11-whats-new.md)
