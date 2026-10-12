# Constructor de Rig

[← Índice](index.md)

## Construir un rig nuevo

El Constructor de Rig crea un rig nuevo para un personaje. Está en su propia pestaña **Rig Builder** de la Tool Shelf izquierda (pulsa **T**), y siempre en la pestaña **Escena** del editor de **Propiedades**. En una Tool Shelf estrecha cambia a una distribución compacta con etiquetas cortas.

---

### Asistente Auto-Rig

**Qué hace:** una guía paso a paso que coloca marcadores en tu malla y construye a partir de ellos un rig con pesos. Es la forma principal de hacer el rig de un personaje desde cero.

La [guía 1](02-guides-a.md#guía-1-lleva-tu-primer-avatar-a-vrchat) lo recorre paso a paso.

**Pasos:** Seleccionar malla → Tipo de rig → Marcadores del cuerpo → Marcadores de los dedos → Marcadores de la cara → Revisión → Generar

**Controles principales:**
- **Iniciar Auto-Rig**, y **Atrás**, **Cancelar** y **Siguiente** arriba y abajo de cada paso
- La lista de mallas (haz clic en tu malla) y luego el tipo de rig: **Body + Face** (cuerpo y cara), **Body Only** (solo cuerpo) o **Face Only** (solo cara, para una armadura existente)
- **Detect Markers** (detectar marcadores; en Smart Detection) — recorre las extremidades de la malla y coloca cada marcador del cuerpo con un grado de confianza; **Accept High** (aceptar confianza alta) conserva los seguros y **Reset Low** (restablecer confianza baja) borra los dudosos
- **Adivinar marcadores desde la malla** y **Adivinar precisión** (cuerpo), **Adivinar marcadores de dedos** (los marcadores de los dedos se colocan a partir de la forma de la mano) y **Adivinar marcadores faciales**
- Detalle de Dedos — cuántos dedos construir, de «0 — No Fingers» a «5 — Full Human Hand»
- La fila de cada marcador: **Place Marker** (colocar marcador; icono de flecha), **Confirm Marker** (confirmar marcador; marca de verificación) y **Reset Marker** (restablecer marcador; flecha circular); **Toggle Symmetry** (alternar simetría; primer icono) en los marcadores izquierdos y derechos
- **Mirror L to R** (reflejar de izquierda a derecha) y **Mirror R to L** (reflejar de derecha a izquierda) — copian los marcadores confirmados a través de la línea central
- **Confirmar todos colocados** — confirma cada marcador colocado del paso
- **Generar rig** — construye el rig a partir de los marcadores confirmados; luego, en el último paso, **Construir rig de control** (ver más abajo) y **Cerrar asistente**

**Lo que construye Generar rig:**
- Un rig de cuerpo con los segmentos de columna y cuello elegidos, y brazos y piernas IK/FK, solo IK o solo FK (la opción **Cinemática**)
- Los huesos de los dedos para el número elegido
- Para **Body + Face**: un rig facial, con formas de control cuando **Generar formas de control** está activado
- Pesos de piel con la calidad elegida. Las mallas densas se pesan mediante una malla proxy más ligera, así que un personaje de 678 000 vértices tarda alrededor de un minuto en lugar de fallar en silencio.

**Construir rig de control:** el paso de revisión también muestra **Twist Bones** (huesos de torsión), **Skirt Bones** (huesos de falda), **Face Controls** (controles faciales) y **Joint Correctives** (correctivos de articulación). Generar rig no los aplica. Pertenecen al rig de control para motores (huesos de torsión, huesos de falda que siguen a las piernas, controles de mirada y parpadeo, y shape keys correctivos de articulación). Después de Generar rig, el último paso ofrece **Construir rig de control**, que construye ese rig en la armadura generada con las opciones elegidas. Haz clic en él antes de **Cerrar asistente**, porque cerrarlo restablece las opciones del asistente. El panel Control Layer (Herramientas de rig) solo aparece en un rig construido así.

**Dónde está:** Rig Builder → Asistente Auto-Rig

---

### Quick Rig (rig rápido)

**Qué hace:** añade con un clic una armadura ya hecha: el Basic Humanoid de BoneCraft (19 huesos, sin necesidad de Rigify) o uno de los metarigs de Rigify. Más rápido que el asistente, menos ajustado.

**Controles principales:**
- El botón Basic Humanoid y los metarigs de Rigify (**Habilitar Rigify** primero, si Rigify está desactivado)
- Opciones para el siguiente clic: **Ajustar Rig a la Malla Activa**, pesos automáticos, **Agregar Controladores IK/FK** y **Pose Inicial**
- **T-Pose** y **Pose A** — cambiar la pose de reposo del rig seleccionado
- **Inspeccionar Controles del Rig Activo** y **Diagnosticar Rig Rápido (imprimir en consola)** — comprobar lo que se ha construido
- **Generar Rig de Control (metarig activo)** — con un metarig de Rigify activo, genera su rig de control de Rigify

**La biblioteca de assets BoneCraft Rigs:** el Basic Humanoid también es un asset. Arrástralo desde la estantería de assets sobre tu personaje. Con el rig soltado seleccionado, Quick Rig muestra «Dropped rig: fit it to a mesh» (rig soltado: ajústalo a una malla): elige la **Mesh** (malla), decide si ajustarlo y darle pesos, y haz clic en **Fit Dropped Rig** (ajustar rig soltado).

**Dónde está:** Rig Builder → Quick Rig

---

### Maniquí

**Qué hace:** construye una figura humana sencilla con rig, como sustituto cuando aún no tienes un modelo. Es solo una vista previa: sustitúyelo por tu propia malla antes del uso final.

**Controles principales:**
- **Maniquí rápido** — construye uno con proporciones predeterminadas
- **Agregar maniquí** — construye uno con los ajustes de abajo
- **Regenerar** y **Eliminar** — reconstruirlo con ajustes nuevos, o borrarlo junto con su rig
- **Modo**, **Tipo de cuerpo** y **Escala de radio**, con más opciones en Avanzado

**Dónde está:** Rig Builder → Maniquí

---

### Redireccionamiento de animación

Pasar una animación de un esqueleto a otro se trata en [Herramientas de rig: Redireccionar](05-rig-tools.md#redireccionar).

---

## Fusión de Huesos

**Qué hace:** combina dos armaduras en una (por ejemplo un rig de cuerpo y un rig de ropa o de cabello), conservando todos los pesos.

La [guía 11](03-guides-b.md#guía-11-une-dos-rigs) la recorre paso a paso.

**Las tres etapas:**
1. Alcance — elegir las dos armaduras y revisar en qué se diferencian
2. Renombrar — resolver conflictos de nombres y marcar los huesos nuevos
3. Fusionar — previsualizar y luego fusionar

**Controles principales:**
- **Base** — la armadura que se queda; la otra se fusiona en ella y luego se oculta
- **Analyze** (analizar) — compara los dos esqueletos; **Acknowledge Scope — Proceed to Rename** (confirmar alcance — pasar a renombrar) abre la etapa 2
- **Normalize Both Armatures** (normalizar ambas armaduras) — renombra los huesos estándar de ambos rigs a un mismo estándar de nombres (Mixamo Prefixed, Mixamo Stripped o personalizado)
- **Auto-Propose Renames** (proponer renombrados automáticamente) — sugiere nombres para los huesos propios del rig que se fusiona
- **Apply Rename** (aplicar renombrado) — renombra una entrada (un paso de deshacer); **Apply Batch Pattern** (aplicar patrón por lotes) renombra muchas con un patrón (con `{bone}`, `{side}` e `{index}`)
- **Mark as Unique** (marcar como único) — conserva un hueso como hueso nuevo en lugar de fusionarlo
- **Verify Rename — Proceed to Merge** (verificar renombrado — pasar a fusionar) — abre la etapa 3
- **Run Merge Preview** (ejecutar vista previa de fusión) — informa de lo que haría la fusión, sin cambiar nada
- **Combinar Armaduras** — hace una copia de seguridad de ambas armaduras y las fusiona

**Dónde está:** pestaña BoneCraft → Fusión de Huesos

Siguiente: [Mechanisms (mecanismos)](07-mechanisms.md)
