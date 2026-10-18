# Constructor de Rig

[← Índice](index.md)

Para una demostración narrada de ambos métodos, consulta el [recorrido IK/FK para principiantes y archivo de práctica](https://github.com/Axleonex/B4Artists_Toolkit/blob/main/bonecraft/docs/tutorials/ikfk-beginner.md).

## Construir un rig nuevo

El Constructor de Rig crea un rig para un personaje. Está en su pestaña **Rig Builder** de la Tool Shelf izquierda (**T**) y en **Properties → Scene** mientras Preferences → Tabs → Scene Properties → Show esté activado. En una estantería estrecha usa etiquetas compactas. Auto-Rig Wizard aparece primero, seguido de Quick Rig y Mannequin. También puedes iniciar el asistente o añadir un Quick Rig desde Add → Armature.

---

### Asistente Auto-Rig

**Qué hace:** una guía paso a paso que coloca marcadores en tu malla y construye a partir de ellos un rig con pesos. Es la forma principal de hacer el rig de un personaje desde cero.

La [guía 1](02-guides-a.md#guía-1-lleva-tu-primer-avatar-a-vrchat) lo recorre paso a paso.

**Pasos:** Seleccionar malla → Tipo de rig → Marcadores del cuerpo → Marcadores de los dedos → Marcadores de la cara → Revisión → Generar

**Controles principales:**
- **Start Auto-Rig** abre el asistente. **Back** y **Cancel** están arriba; **Next** está abajo en selección de malla, tipo y marcadores. Review usa **Generate Rig**; el final, **Close Wizard**.
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

**Colocar varios marcadores con la herramienta de vista:** inicia el asistente y avanza a los marcadores de cuerpo, dedos o cara. En Object Mode activa Place Rig Markers en la barra de herramientas de la vista. La cabecera indica el siguiente marcador sin confirmar y ofrece bloqueos de ejes y simetría. Pulsa la malla elegida en el asistente para colocar y confirmar ese marcador. Respeta la simetría del asistente; los botones individuales Place siguen funcionando. Al completar el paso pulsa **Next** en el asistente. Pulsar fuera de la malla no coloca nada.

---

### Quick Rig (rig rápido)

**Qué hace:** añade una armadura con un clic: Basic Humanoid de BoneCraft (19 huesos, sin Rigify) o un metarig de Rigify. Es más rápido que el asistente, pero menos personalizado.

**Controles principales:**
- Basic Humanoid y metarigs de Rigify; si está apagado, usa **Enable Rigify** primero.
- Pulsa un rig para añadirlo y después ajusta adaptación a la malla, pesos automáticos, **Add IK/FK Controllers** e **Initial Pose** en Adjust Last Operation.
- **T-Pose** y **A-Pose** cambian la pose de reposo del rig seleccionado.
- En Troubleshooting está **Diagnose Quick Rig (print to console)**. Con una armadura que no sea metarig también aparece **Inspect Active Rig Controls**.
- Con un metarig de Rigify activo aparece **Generate Control Rig (active metarig)** en lugar de Inspect Active Rig Controls: genera su rig de control de Rigify.

**Catálogo BoneCraft Rigs:** los nueve rigs incluidos comparten el catálogo **Starter Rigs** en la estantería nativa inferior de assets. Abre su menú de catálogos a la izquierda, elige bibliotecas **All** y activa **Starter Rigs** una vez para añadir su pestaña junto a las demás. Selecciónala para explorar los rigs. **Add → Armature → Starter Rig Catalog** abre el selector que comprueba dependencias y permite ajustar y añadir un rig.

Basic Humanoid no necesita Rigify. Las demás miniaturas dicen **Rigify**. Si está desactivado, elegir o soltar una ofrece **Enable Rigify & Add Rig** o Cancel. Aceptar activa el Rigify instalado y continúa; cancelar no añade nada. También puedes activarlo en Quick Rig; el selector de rigs ofrece Enable Rigify en su menú contextual cuando hace falta. Los controles de la esquina superior izquierda de la vista se retiraron en 9.2.5. Si falta una dependencia o un preset en la versión instalada, se explica el problema sin añadir un rig sustituto.

Pulsa una miniatura o arrástrala a la vista. Con una malla seleccionada, el rig se adapta a ella; pesos automáticos y generación de controles empiezan desactivados. Cámbialos después en **Adjust Last Operation**. Sin malla seleccionada, selecciona el nuevo rig, elige **Mesh** en Quick Rig y pulsa **Fit Dropped Rig**. El ajuste cambia la escala y la posición del esqueleto; revisa y edita las articulaciones antes de generar controles o pesos. Soltar fuera de la vista, Esc o clic derecho cancela sin añadir nada.

**Dónde está:** Rig Builder → Quick Rig; también Add → Armature → Quick Rig.

---
### Maniquí

**Qué hace:** crea una malla de vista previa alrededor de un rig existente para revisar deformaciones sin un personaje terminado. Selecciona primero la armadura o una malla emparentada a ella. Si no tienes rig, añádelo con Quick Rig. Sustituye el maniquí por tu propia malla antes del uso final.

**Controles principales:**
- **Quick Mannequin** usa valores fijos y sustituye el maniquí anterior de ese rig.
- **Add Mannequin** usa los ajustes de escena y sustituye el existente de forma predeterminada. Replace Existing está en Adjust Last Operation después de pulsar.
- **Regenerate** reconstruye la vista previa con sus ajustes guardados.
- **Remove** elimina la malla del maniquí y conserva la armadura.
- Despliega Options bajo los botones para **Mode**, **Body Type**, densidad y **Radius Scale**. Advanced contiene escalas regionales y opciones de salida. Para aplicar nuevos ajustes de escena pulsa otra vez **Add Mannequin**.

**Dónde está:** Rig Builder → Mannequin.

---
## Taller ilustrado del maniquí

<style>
section.chapter:has(#ch-06-rig-builder) img { max-width:100%; max-height:155mm; width:auto; height:auto; }
@media print {
  [id="06-rig-builder--taller-ilustrado-del-maniquí"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--parte-"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--parte-"] + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

Sigue las partes A, B y C en orden. Cada paso tiene una captura real; los números rojos corresponden a su leyenda. Se capturaron con **BoneCraft 9.1.2** en `Bforartists 5.2.0`. En Blender pueden variar los paneles y atajos; usa los nombres de los comandos como referencia.

Esta práctica crea una vista previa de cápsulas para aprender rigging, no un personaje terminado: cabeza, manos y torso son provisionales. Empieza en un archivo nuevo y conserva ambos puntos de control para repetir la conversión sin perder el metarig original.

En `examples/mannequin/`, `SimpleHuman_Mannequin.blend` contiene el resultado neutro de A; `Mannequin_AutoRig.blend` contiene el ejemplo posado de C con los pesos corregidos.

### Parte A: de Simple Human a maniquí



#### A1. Activar Rigify

Empieza en una escena nueva. Abre **Scene Properties → Rig Builder → Quick Rig**. Si no aparecen los presets de Rigify, pulsa **Enable Rigify**. Usaremos el metarig `Simple Human` de Rigify; **BoneCraft Basic Humanoid (19 bones)** es otro preset.

![A1. Activar Rigify](../images/rig-builder/en/a01-enable-rigify.png)

*1 — Scene Properties. 2 — Enable Rigify.*

#### A2. Añadir Simple Human

Pulsa `Simple Human` en Quick Rig. Obtendrás un metarig editable, todavía sin malla. En esta versión tiene 29 huesos.

![A2. Añadir Simple Human](../images/rig-builder/en/a02-simple-human.png)

*1 — Preset Simple Human.*

#### A3. Revisar el metarig

Con el puntero en la vista 3D, pulsa `Numpad 1` para Front Orthographic. Comprueba que se ve todo el esqueleto y encuádralo con la rueda. El metarig puede empezar en Pose Mode.

![A3. Revisar el metarig](../images/rig-builder/en/a03-metarig.png)

*1 — Vista frontal. 2 — Esqueleto Simple Human.*

#### A4. Volver a Object Mode

Elige **Object Mode** en el selector de modo de la vista. Mantén seleccionado `SimpleHumanArmature`. Cambia a este modo antes de modificar la pose de reposo o generar el maniquí.

![A4. Volver a Object Mode](../images/rig-builder/en/a04-object-mode.png)

*1 — Selector de modo. 2 — Object Mode.*

#### A5. Usar una pose T

En Quick Rig, pulsa **T-Pose**: los brazos quedan horizontales. Para un cuerpo propio, ajusta el metarig en Edit Mode antes de generar su vista previa. En esta práctica mantén simétricas las articulaciones.

![A5. Usar una pose T](../images/rig-builder/en/a05-t-pose.png)

*1 — Comando T-Pose.*

#### A6. Generar el maniquí

Abre **Mannequin → Options**. Usa `Mode: Universal`, `Body Type: Neutral`, **Medium** y `Radius Scale: 1.00`. En Advanced deja las escalas regionales en 1.00, elige `Joined (non-manifold)`, **Flat colour** y activa **Joint Smoothing**. Desactiva Unified Volume. Después pulsa **Add Mannequin**. La captura muestra la malla de cápsulas resultante. Add aplica las opciones actuales; Regenerate reutiliza las guardadas.

![A6. Generar el maniquí](../images/rig-builder/en/a06-final-settings.png)

*1 — Add Mannequin. 2 — Universal y ajustes del cuerpo. 3 — Salida Joined y suavizado.*

#### A7. Probar una pose

Selecciona la armadura, entra en **Pose Mode** y pulsa el hueso del antebrazo izquierdo (la izquierda del personaje queda a tu derecha en vista frontal). Gíralo ligeramente con Rotate; el maniquí lo sigue. Es una vista previa con pesos sobre el metarig, todavía sin los controles de animación de C.

![A7. Probar una pose](../images/rig-builder/en/a07-select-forearm.png)

*1 — Pose Mode. 2 — Antebrazo seleccionado y gizmo de transformación.*

#### A8. Restablecer y guardar

Con el puntero en la vista, selecciona todos los huesos de pose. Pulsa **F3**, busca `Clear Pose Transforms` y elige **All**. Comprueba que vuelve la pose T. Guarda con **File → Save As** como `SimpleHuman_Mannequin.blend`. Conserva este punto de control.

![A8. Restablecer y guardar](../images/rig-builder/en/a09-clear-pose.png)

*1 — Buscar Clear Pose Transforms. 2 — All restablece los huesos de pose seleccionados.*

### Parte B: maniquí sin rig mediante Auto-Rig



#### B1. Seleccionar la malla

Continúa desde el punto neutro de A. En **Object Mode**, selecciona `SimpleHumanArmature_Mannequin` en el Outliner. Quitaremos su rig antes de ejecutar el asistente. Guarda el resultado con otro nombre para conservar A.

![B1. Seleccionar la malla](../images/rig-builder/en/b01-select-mesh.png)

*1 — Selecciona la malla, no la armadura.*

#### B2. Convertir la vista previa en malla

Con solo el maniquí seleccionado y en su pose T restablecida, pulsa **F3**, busca `Convert Mesh` y ejecútalo. Conserva la geometría neutra visible y elimina el modificador Armature.

![B2. Convertir la vista previa en malla](../images/rig-builder/en/b02-convert-mesh.png)

*1 — Comando Convert Mesh.*

#### B3. Quitar el padre

Pulsa **Alt+P** y elige `Clear and Keep Transformation`. Desvincula la malla del metarig anterior sin moverla.

![B3. Quitar el padre](../images/rig-builder/en/b03-clear-parent.png)

*1 — Clear and Keep Transformation.*

#### B4. Eliminar los pesos antiguos

Abre **Object Data Properties → Vertex Groups**. En el menú de la lista, elige `Delete All Groups`. Esos grupos pertenecen al metarig anterior; el asistente creará otros. Hazlo solo en esta malla de práctica desechable.

![B4. Eliminar los pesos antiguos](../images/rig-builder/en/b04-clear-groups.png)

*1 — Menú Vertex Groups. 2 — Delete All Groups.*

#### B5. Comprobar la malla sin rig

Oculta `SimpleHumanArmature` con su ojo del Outliner. El maniquí debe seguir visible, sin modificador Armature y con Vertex Groups vacío. Este será el modelo sin rig. BoneCraft 9.1.2 genera maniquíes desde una armadura; desvincular esta vista previa permite obtener la malla de práctica.

![B5. Comprobar la malla sin rig](../images/rig-builder/en/b05-rigless-check.png)

*1 — Ocultar el metarig anterior. 2 — Lista de modificadores vacía.*

#### B6. Activar Rig Builder en la vista

Abre **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Activa **Rig Builder** y elige **Left**. Cierra Preferences y pulsa **T** sobre la vista si la Tool Shelf está oculta. Usa esta pestaña para colocar marcadores: en el programa probado con 9.1.2, Place Marker iniciado desde Scene Properties no aceptaba clics en la vista.

![B6. Activar Rig Builder en la vista](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — Activar Rig Builder. 2 — Ubicación en la Tool Shelf izquierda.*

#### B7. Iniciar Auto-Rig

Con la malla sin rig seleccionada, pulsa **Start Auto-Rig**. La captura muestra el botón equivalente en Scene Properties; el mismo comando está arriba de la pestaña Rig Builder que acabas de activar.

![B7. Iniciar Auto-Rig](../images/rig-builder/en/b06-start-wizard.png)

*1 — Start Auto-Rig.*

#### B8. Elegir la malla de entrada

En `Select Mesh`, elige el maniquí, verifica la confirmación de selección y pulsa **Next**. No elijas un widget u otra vista previa.

![B8. Elegir la malla de entrada](../images/rig-builder/en/b07-select-input.png)

*1 — Maniquí de entrada. 2 — Next.*

#### B9. Elegir un rig con ambos métodos

Selecciona **Body Only** y `Kinematics: IK + FK`. Mantén **Generate Control Shapes** activado y pulsa **Next**. El maniquí de cápsulas no tiene topología facial, así que no necesita Body + Face.

![B9. Elegir un rig con ambos métodos](../images/rig-builder/en/b08-body-ikfk.png)

*1 — Body Only. 2 — IK + FK. 3 — Next.*

#### B10. Detectar los marcadores

En Body Markers, pulsa **Detect Markers** dentro de Smart Detection. Son propuestas iniciales: revisa cada una. Mantén **Mirror Symmetry** activado para este maniquí simétrico.

![B10. Detectar los marcadores](../images/rig-builder/en/b09-detect-markers.png)

*1 — Detect Markers. 2 — Mirror Symmetry.*

#### B11. Revisar las posiciones

Comprueba la parte superior de la cabeza, base del cuello, pelvis, muñecas y tobillos respecto a la malla. Esta vista previa segmentada da varias propuestas de baja confianza. Corrige tanto los puntos principales como los de precisión opcionales antes de generar. La confianza describe la detección original; una marca verde al inicio de la fila indica que la colocación actual está confirmada.

![B11. Revisar las posiciones](../images/rig-builder/en/b10-review-markers.png)

*1 — Resumen de confianza. 2 — Filas de marcadores corporales.*

#### B12. Colocar una muñeca

En **Rig Builder** de la vista, pulsa el cuentagotas **Place Marker** de Wrist Left y luego la superficie de la muñeca. Si ya está confirmado, restablece primero esa fila para mostrar el botón de colocación. La muñeca izquierda del personaje aparece a la derecha en vista frontal.

![B12. Colocar una muñeca](../images/rig-builder/en/b11-place-wrist.png)

*1 — Control de colocación Wrist Left. 2 — Pulsar la superficie de la muñeca.*

#### B13. Revisar muñecas y tobillos

Las dos filas de muñecas deben tener marcas verdes y coordenadas X opuestas. Repite con `Ankle Left`; la simetría coloca Ankle Right. Sitúa cada tobillo en su articulación, no en la punta del pie. Comprueba la simetría en tu malla; no copies coordenadas de un personaje de otro tamaño.

![B13. Revisar muñecas y tobillos](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — Par de muñecas confirmado. 2 — Muñeca reflejada en la malla.*

#### B14. Afinar hombros y codos

Ve a Precision Markers. Restablece y coloca `Shoulder Left` en el pivote del brazo y `Elbow Left` en el hueco del codo. Confirma sus parejas reflejadas. Mantén la muñeca en el extremo del antebrazo junto a la mano. Estos puntos definen la cadena del brazo: corrige las propuestas sobre una cápsula incorrecta.

![B14. Afinar hombros y codos](../images/rig-builder/en/b13-arm-precision.png)

*1 — Filas de hombro y codo. 2 — Hombro. 3 — Codo.*

#### B15. Afinar caderas y rodillas

Coloca `Hip Left` arriba del muslo y `Knee Left` en el hueco entre muslo y espinilla. Comprueba el lado opuesto que genera la simetría. Mantén la pelvis en la línea central, entre las caderas.

![B15. Afinar caderas y rodillas](../images/rig-builder/en/b14-leg-precision.png)

*1 — Filas de cadera y rodilla. 2 — Superficie de cadera. 3 — Hueco de rodilla.*

#### B16. Comprobar profundidad y puntas

Pulsa `Numpad 3` sobre la vista. Comprueba los puntos en Right Orthographic y también de frente. Coloca `Toe Left` cerca del frente del pie y verifica su pareja. Un marcador correcto de frente puede quedar demasiado adelantado o retrasado de lado.

![B16. Comprobar profundidad y puntas](../images/rig-builder/en/b15-side-depth.png)

*1 — Right Orthographic. 2 — Fila del marcador Toe. 3 — Superficie del pie.*

#### B17. Colocar los talones

Restablece cualquier talón mal detectado y coloca `Heel Left` atrás del pie en vista lateral. Comprueba Heel Right. Aunque son opcionales, dejarlos ambos en cero produjo una advertencia de proximidad en la versión probada; colocarlos en los pies la eliminó.

![B17. Colocar los talones](../images/rig-builder/en/b16-place-heels.png)

*1 — Par de talones confirmado. 2 — Posición del talón.*

#### B18. Confirmar y continuar

Revisa cabeza, base del cuello, pelvis y cada pareja de puntos. Pulsa **Confirm All Placed** y **Next**. Las marcas verdes indican confirmación; en 9.1.2 pueden seguir apareciendo las etiquetas originales de confianza REVIEW/ADJUST.

![B18. Confirmar y continuar](../images/rig-builder/en/b17-confirm-markers.png)

*1 — Confirm All Placed. 2 — Next.*

#### B19. Omitir los dedos

Elige `0 — No Fingers` y pulsa **Next**. Hay cápsulas de manos, pero no geometría de dedos. En una mano real, elige el número adecuado y coloca sus marcadores.

![B19. Omitir los dedos](../images/rig-builder/en/b18-no-fingers.png)

*1 — No Fingers. 2 — Next.*

#### B20. Revisar y generar

Exige **All checks passed** antes de seguir. Usa **IK + FK**, formas de control activadas, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers` y **Game Ready**. Desactiva Twist Bones, Skirt Bones, Preserve Volume y Joint Correctives. Pulsa **Generate Rig**. Son ajustes para este maniquí sencillo, no una receta universal de exportación.

![B20. Revisar y generar](../images/rig-builder/en/b19-review-generate.png)

*1 — Comprobación de marcadores. 2 — Ajustes de generación. 3 — Generate Rig.*

#### B21. Construir los controles

Tras generar, pulsa **Build Control Rig**. Generate Rig crea el cuerpo y sus pesos; Build Control Rig añade la capa de control que usaremos. No vuelvas a pulsar Quick Mannequin: la malla de entrada ya existe, aunque el panel final muestre su oferta genérica.

![B21. Construir los controles](../images/rig-builder/en/b20-build-controls.png)

*1 — Build Control Rig.*

#### B22. Cerrar el asistente

Espera la confirmación del rig de control y pulsa **Close Wizard**. Aparece la nueva armadura en el Outliner. Mantén oculto el metarig Simple Human anterior. El nuevo rig debe deformar la malla: ver huesos no basta para validarlo.

![B22. Cerrar el asistente](../images/rig-builder/en/b21-close-wizard.png)

*1 — El botón de construcción queda desactivado. 2 — Close Wizard.*

### Parte C: comprobar pesos y usar IK/FK

En esta versión, la armadura generada se llama

```text
BoneForge_Rig
```

: usa ese nombre en el Outliner y en la herramienta de pesos.

`FK (Forward Kinematics)` transmite giros por la jerarquía: brazo, antebrazo y mano. Sirve para movimientos amplios y libres. `IK (Inverse Kinematics)` parte del extremo: mueve la muñeca o el tobillo y el solucionador dobla la cadena para alcanzarlo. Sirve para apoyar pies o manos sobre una superficie.

Para balancear un brazo usa hombro y codo FK; los hijos siguen al padre. Para colocar la mano usa el objetivo IK de muñeca; para apoyar un pie, el de tobillo. El control polo determina hacia dónde se dobla el codo o la rodilla, no la posición final de muñeca/tobillo. Al cambiar de método, revisa el ajuste antes de insertar claves.

Compararemos el mismo brazo en ambos modos. Cada extremidad tiene su propio interruptor. `Bake IK / Bake FK` convierten animación; cambiar una pose no sustituye hornear o insertar claves. Consulta [Control Layer](05-rig-tools.md#control-layer-capa-de-control-ikfk).

#### C1. Abrir la capa de control

Selecciona la **armadura generada**, entra en **Pose Mode** y abre **BoneCraft → Review → Control Layer**. Hay un interruptor para cada brazo y pierna. Empieza con **arm-L → FK**. Los lados corresponden al personaje; arm-L aparece a tu derecha de frente.

![C1. Abrir la capa de control](../images/rig-builder/en/c02-control-layer.png)

*1 — Pose Mode. 2 — Control Layer e interruptor arm-L.*

#### C2. Mostrar los controles

Abre **Object Data Properties → Bone Collections** de la armadura. Usa las estrellas Solo de `Controls` y **FK** para aislar sus formas. Activa **In Front** en Viewport Display si la malla las tapa. Después incluye **IK** para ver sus objetivos. La lista nativa también sirve si el panel Collections de BoneCraft no se dibuja en este programa.

![C2. Mostrar los controles](../images/rig-builder/en/c03-visible-controls.png)

*1 — Estrellas Solo de Controls y FK. 2 — In Front.*

#### C3. Seleccionar el control FK

De frente, pulsa el control circular del codo izquierdo del personaje. La selección debe llamarse **forearm.fk-L**. Gira alrededor del codo; el control del hombro giraría el brazo y sus hijos.

![C3. Seleccionar el control FK](../images/rig-builder/en/c04-select-fk.png)

*1 — Control forearm.fk-L seleccionado. 2 — FK activo para arm-L.*

#### C4. Girar y revisar la deformación

Gira el control sobre **Y** global unos `−45°`. Usa Rotate; en el mapa Bforartists mostrado, **Ctrl+E**, **Y**, **-45**, **Enter**. En Blender, el atajo predeterminado es **R**. La captura muestra adrede un fallo inicial: la cápsula del brazo se inclina con el antebrazo. No des por terminado el rig.

![C4. Girar y revisar la deformación](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — Movimiento incorrecto del brazo durante la prueba FK.*

#### C5. Recalcular los pesos

Si falla la prueba, entra en **Object Mode**, selecciona la malla y abre **BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**. En Mesh to Reweight elige el maniquí; en Existing Armature, la **armadura generada**. Usa **Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0`, `Minimum Weight: 0.001` y **Keep Weight Backup** activado. Ejecuta **Automatic Bone Weight Recalculation**. Así se reparó esta vista previa segmentada en la versión probada.

![C5. Recalcular los pesos](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — Malla y armadura. 2 — Bone Heat. 3 — Ajustes de sustitución y copia. 4 — Recalcular.*

#### C6. Verificar la flexión reparada

Selecciona otra vez la armadura generada y entra en **Pose Mode**. El brazo debe quedar horizontal del hombro al codo mientras sube el antebrazo. El objeto oculto `WEIGHTS_BACKUP_…` conserva los pesos anteriores. Prueba las demás extremidades antes de animar tu personaje; un esqueleto generado no garantiza un buen skinning.

![C6. Verificar la flexión reparada](../images/rig-builder/en/c05-fk-result.png)

*1 — Brazo inmóvil. 2 — El antebrazo dobla por el codo.*

#### C7. Cambiar el mismo brazo a IK

Pulsa **arm-L → IK**. El objetivo se ajusta a la pose actual y el brazo debe seguir levantado. Añade **IK** a las colecciones Solo visibles si los objetivos están ocultos. Cambia qué controles conducen la cadena; no graba una animación.

![C7. Cambiar el mismo brazo a IK](../images/rig-builder/en/c06-switch-ik.png)

*1 — Interruptor IK de arm-L. 2 — Pose conservada al cambiar.*

#### C8. Seleccionar el objetivo IK

Pulsa el control de muñeca y verifica **forearm.ik-L**. Aunque su nombre diga antebrazo, es el objetivo final de la cadena del brazo. Muévelo para colocar la mano; el solucionador ajusta hombro y codo.

![C8. Seleccionar el objetivo IK](../images/rig-builder/en/c07-select-ik.png)

*1 — Objetivo de muñeca seleccionado. 2 — Nombre de selección.*

#### C9. Mover el objetivo y comparar

Mueve la muñeca un poco hacia dentro sobre **X** global: `−0.15 m` en este ejemplo. Usa **Ctrl+W**, **X**, `-0.15`, **Enter** o arrastra la flecha X de Move. En Blender, el atajo predeterminado es **G**. Compara con FK: el extremo dirige y ambos segmentos lo siguen. Mantén el objetivo al alcance del brazo.

![C9. Mover el objetivo y comparar](../images/rig-builder/en/c08-move-ik.png)

*1 — Extremo de muñeca. 2 — Respuesta de la cadena. 3 — Desplazamiento X de ejemplo.*

#### C10. Volver a FK y guardar

Pulsa **arm-L → FK**: sus controles se ajustan a la pose IK. Comprueba que la malla no salta y guarda con **File → Save As** como `Mannequin_AutoRig.blend`. La captura muestra FK activo. Para una copia neutra, deja las cuatro extremidades en FK, selecciona los controles visibles y usa **F3 → Clear Pose Transforms → All**, como en A; guarda con otro nombre.

**Comprobación final:** conservaste la vista previa original, obtuviste un maniquí sin rig, generaste cuerpo y controles, corregiste pesos y comparaste giro FK con movimiento IK. Conserva el archivo para practicar y sustituye la geometría provisional en producción.

![C10. Volver a FK y guardar](../images/rig-builder/en/c10-save-complete.png)

*1 — FK activo de nuevo. 2 — Pose conservada. 3 — Nombre del archivo guardado.*

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

**Dónde está:** BoneCraft → Setup Rigging → Bone Merge

Siguiente: [Mechanisms (mecanismos)](07-mechanisms.md)
