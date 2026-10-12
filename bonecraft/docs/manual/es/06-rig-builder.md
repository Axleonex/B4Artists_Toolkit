# Constructor de Rig

[← Contenidos](index.md)

## Construir un rig nuevo

Rig Builder crea una nueva rig para un personaje. Está en su propia pestaña **Rig Builder** en el estante de herramientas izquierdo (presione**T**) y en la pestaña**Properties** del editor**Scene** mientras Preferencias → Pestañas → Propiedades de escena → Mostrar está activado. En un estante de herramientas estrecho, cambia a un diseño compacto con etiquetas cortas. El Auto-Rig Wizard es el primero en aparecer, seguido de Quick Rig y Mannequin. También puede iniciar el asistente o agregar un Quick Rig desde el menú Agregar → Armadura de la ventana gráfica.

---

### Asistente Auto-Rig

**Qué hace:** Una guía paso a paso que coloca marcadores en la malla y construye un rig completo con pesos a partir de ellos. La forma principal de manipular un personaje desde cero.

[Guía 1](02-guides-a.md#guía-1-lleva-tu-primer-avatar-a-vrchat) lo explica paso a paso.

**Pasos:** Seleccione Malla → Tipo de rig → Marcadores de cuerpo → Marcadores de dedos → Marcadores de cara → Revisar → Generar

**Controles clave:**
- **Start Auto-Rig** abre el asistente.**Back** y**Cancel** están en la cima;**Next** se encuentra en la parte inferior de los pasos de malla, tipo de rig y marcador. La revisión utiliza**Generate Rig** en lugar de Siguiente; el paso final utiliza**Close Wizard**
- La lista de malla (haga clic en su malla), luego el tipo de rig: **Body + Face**,**Body Only** o**Face Only** (para una armadura existente)
- **Detect Markers** (en Detección inteligente): traza las extremidades en la malla y coloca cada marcador corporal con confianza;**Accept High** se queda con los seguros y**Reset Low** despeja los dudosos
- **Guess Markers from Mesh** y**Guess Precision** (cuerpo),**Guess Finger Markers** (los marcadores de dedos se colocan a partir de la forma de la mano) y**Guess Face Markers**
- Detalle de los dedos: cuántos dedos construir, desde "0 - Sin dedos" hasta "5 - Mano humana completa"
- La fila de cada marcador: **Place Marker** (icono de flecha),**Confirm Marker** (marca de verificación) y**Reset Marker** (flecha circular);**Toggle Symmetry** (primer icono) en los marcadores izquierdo y derecho
- **Mirror L to R** y**Mirror R to L**: copie los marcadores confirmados a través de la línea central
- **Confirm All Placed**: confirma cada marcador colocado del paso
- **Generate Rig**: construye el rig a partir de los marcadores confirmados; luego, en el último paso,**Build Control Rig** (ver más abajo) y**Close Wizard**

**Qué construye Generate Rig:**
- Un rig para el cuerpo con los segmentos de columna y cuello que usted eligió, y brazos y piernas IK/FK, solo IK o solo FK (la opción **Kinematics** )
- Huesos de los dedos para el número de dedos que elijas
- Para **Body + Face**: un rig frontal, con formas de control cuando**Generate Control Shapes** está activado
- Pesos de piel de la calidad elegida. Las mallas densas se ponderan a través de una malla proxy más ligera, por lo que un personaje de 678.000 vértices tarda aproximadamente un minuto en lugar de fallar silenciosamente.

**Construir equipo de control:** el paso de revisión también muestra**Twist Bones**,**Skirt Bones**,**Face Controls** y**Joint Correctives**. Generate Rig no los aplica. Pertenecen al rig de control del motor (huesos giratorios, huesos de falda que siguen las piernas, controles de apuntamiento ocular y parpadeo, y teclas de forma correctiva de las articulaciones). Después de Generar rig, el último paso ofrece**Build Control Rig**, que construye esa rig en la armadura generada con las opciones que usted elija. Haga clic en él antes de**Close Wizard**, porque al cerrarlo se restablecen las opciones del asistente. El panel Capa de control (Herramientas de rig) aparece solo en una rig construida de esta manera.

**Dónde encontrarlo:** Rig Builder → Asistente de Auto-Rig

**Coloque varios marcadores con la herramienta de ventana gráfica:** inicie el asistente y avance al paso del marcador de cuerpo, dedo o cara. En el modo Objeto, active Colocar marcadores de rig en la barra de herramientas de la ventana gráfica. El encabezado de la herramienta nombra el siguiente marcador no confirmado y muestra bloqueos de eje y un interruptor de espejo. Haga clic en la malla del asistente para colocar y confirmar ese marcador. La simetría sigue la configuración del asistente; Los botones Colocar por marcador siguen funcionando. Cuando la herramienta indique que el paso está realizado, presione**Next** en el asistente. Al hacer clic en otro lugar no se coloca un marcador.

---

### Quick Rig (rig rápido)

**Qué hace:** Agrega una armadura ya preparada con un solo clic: el humanoide básico de BoneCraft (19 huesos, no se necesita Rigify ) o uno de los metarigs de Rigify. Más rápido que el mago, menos personalizado.

**Controles clave:**
- El botón Humanoide básico y los metarigs Rigify (**Enable Rigify** primero, si Rigify está desactivado)
- Haga clic en un botón de rig para agregarlo inmediatamente, luego ajuste el ajuste a la malla, los pesos automáticos, **Add IK/FK Controllers** y**Initial Pose** en Ajustar la última operación
- **T-Pose** y**A-Pose**: cambian la postura de descanso del rig seleccionado
- Expanda Solución de problemas para **Diagnose Quick Rig (print to console)**. Con una armadura no metarig activa también muestra**Inspect Active Rig Controls**
- Con un metarig Rigify activo, Solución de problemas muestra **Generate Control Rig (active metarig)** en lugar de Inspeccionar controles de rig activos; genera el rig de control Rigify

**La biblioteca de activos BoneCraft Rigs:** el humanoide básico también es un activo. Arrástralo desde el estante de recursos a tu personaje. Con el rig caído seleccionado, Quick Rig muestra "Equipo caído: ajústelo a una malla": seleccione el**Mesh**, luego haga clic en**Fit Dropped Rig**. Inmediatamente después, utilice**Fit Rig to Mesh** y**Parent + Auto-Weight Mesh** en Ajustar última operación para elegir el ajuste y el peso. Una nueva operación tiene por defecto el ajuste y el ponderación automáticos.

**Dónde encontrarlo:** Rig Builder → Quick Rig; Agregar → Armadura → Quick Rig también agrega los rigs prefabricados

---

### Maniquí

**Qué hace:** Crea una malla de vista previa alrededor de una rig existente para que puedas inspeccionar su deformación sin una malla de caracteres terminada. Primero seleccione la armadura, o una malla vinculada a ella. Si aún no tienes un rig, agrega uno con Quick Rig. El maniquí es sólo una vista previa: reemplácelo con su propia malla antes de su uso final.

**Controles clave:**
- **Quick Mannequin**: crea una vista previa con valores predeterminados fijos, reemplazando el maniquí anterior para esta rig
- **Add Mannequin**: crea una vista previa utilizando la configuración de la escena; reemplaza un maniquí existente por defecto. Reemplazar existente está en Ajustar la última operación después del clic
- **Regenerate**: reconstruye la vista previa existente utilizando su configuración guardada
- **Remove** — elimina la malla del maniquí y mantiene la armadura
- Expanda Opciones debajo de los botones para **Mode**,**Body Type**, densidad y**Radius Scale**; Opciones internas avanzadas contiene las escalas de región y la configuración de salida. Para usar la configuración de escena modificada, haga clic en**Add Mannequin** nuevamente

**Dónde encontrarlo:** Rig Builder → Maniquí

---

## Taller de maniquíes ilustrados.

<!-- Keep each illustrated step together and preserve the manual's print scale. -->
<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--taller-de-maniquíes-ilustrados"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--parte-a-humano-simple-a-maniquí"],[id="06-rig-builder--parte-b-maniquí-sin-rig-mediante-auto-rig"],[id="06-rig-builder--parte-c-comprobar-los-pesos-y-usar-ikfk"]) { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--parte-a-humano-simple-a-maniquí"],[id="06-rig-builder--parte-b-maniquí-sin-rig-mediante-auto-rig"],[id="06-rig-builder--parte-c-comprobar-los-pesos-y-usar-ikfk"]) + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

Siga estas tres partes en orden: [A - Humano simple a maniquí](#parte-a-humano-simple-a-maniquí), [B — maniquí sin rig a través de Auto-Rig](#parte-b-maniquí-sin-rig-mediante-auto-rig) y [C — pesos de prueba y uso IK/FK](#parte-c-comprobar-los-pesos-y-usar-ikfk). Cada paso numerado tiene una captura de pantalla de la interfaz real; Los números rojos coinciden con el título. Las capturas de pantalla se capturaron con la versión **BoneCraft 9.1.2** en `Bforartists 5.2.0`. La disposición del panel y los accesos directos de Blender pueden diferir; los comandos nombrados son la referencia.

Este ejercicio produce una vista previa simple para aprender a manipular. Su cabeza, manos y torso son marcadores de posición y no es un modelo de personaje terminado. Comience en un archivo nuevo; mantenga los dos puntos de control guardados para que pueda repetir la conversión sin perder el metarig original.

El repositorio incluye ambos puntos de control en `examples/mannequin/`: `SimpleHuman_Mannequin.blend` es el resultado neutral de la Parte A y `Mannequin_AutoRig.blend` es el ejemplo completo y planteado de la Parte C con pesos corregidos.

### Parte A: Humano simple a maniquí

#### A1. Habilitar Rigify

Empiece en una nueva escena. Abra **Scene Properties → Rig Builder → Quick Rig**. Si los ajustes preestablecidos de Rigify no están disponibles, haga clic en**Enable Rigify**. Este tutorial utiliza el metarig Rigify `Simple Human`;**BoneCraft Basic Humanoid (19 bones)** es un ajuste preestablecido diferente.

![A1: Habilitar Rigify](../images/rig-builder/en/a01-enable-rigify.png)

*1 — Propiedades de escena. 2: habilite Rigify.*

#### A2. Agregar humano simple

Haga clic en `Simple Human` en Quick Rig. El resultado es un metarig editable, aún no una malla. Tiene 29 huesos en esta versión.

![A2: Agregar humano simple](../images/rig-builder/en/a02-simple-human.png)

*1 — Preajuste Humano simple.*

#### A3. Inspeccionar el metarig

Mueva el puntero a la ventana gráfica y presione `Numpad 1` para Ortográfico frontal. Compruebe que todo el esqueleto sea visible. Utilice la rueda del ratón para enmarcarlo. El nuevo metarig puede comenzar en modo Pose.

![A3: Inspeccionar el metarig](../images/rig-builder/en/a03-metarig.png)

*1 — Vista frontal. 2 — Esqueleto humano simple.*

#### A4. Volver al modo objeto

Utilice el menú desplegable del modo de ventana gráfica y elija **Object Mode**. Mantenga seleccionado `SimpleHumanArmature`. Elija Modo objeto antes de cambiar la pose de reposo o generar el maniquí.

![A4: Regresar al modo Objeto](../images/rig-builder/en/a04-object-mode.png)

*1 — Menú desplegable de modo. 2 — Modo objeto.*

#### A5. Usa una pose en T

En Quick Rig, haga clic en **T-Pose**. Los brazos se extienden horizontalmente. Para un cuerpo personalizado, ajuste el metarig en Modo Edición antes de generar su vista previa; Mantenga las articulaciones izquierda y derecha simétricas para este ejercicio.

![A5: Usa una pose en T](../images/rig-builder/en/a05-t-pose.png)

*1 — Comando T-Pose.*

#### A6. Generar el maniquí

Expanda **Mannequin → Options**. Establezca `Mode: Universal`, `Body Type: Neutral`,**Medium** y `Radius Scale: 1.00`. En Avanzado, mantenga las escalas de región en 1,00, elija `Joined (non-manifold)`,**Color plano** y habilite**Joint Smoothing**. Deje el volumen unificado desactivado. Haga clic en**Add Mannequin** después de configurar estas opciones. La captura de pantalla muestra la malla de cápsula resultante. Utilice Agregar para las opciones actuales; Regenerar reutiliza la configuración del maniquí guardada.

![A6: generar el maniquí](../images/rig-builder/en/a06-final-settings.png)

*1 — Agregar maniquí. 2 — Ajustes universales y de carrocería. 3 — Salida unida y suavizado.*

#### A7. Prueba una postura de hueso

Selecciona la armadura, cambia a **Pose Mode** y haz clic en el hueso del antebrazo izquierdo (la izquierda del personaje está a tu derecha en la vista frontal). Gírelo ligeramente con la herramienta Girar; El maniquí vinculado sigue el movimiento. Esta es una vista previa ponderada en el metarig. Aún no tiene los controles de animación utilizados en la Parte C.

![A7: Prueba una postura de hueso](../images/rig-builder/en/a07-select-forearm.png)

*1 — Modo Pose. 2 — Antebrazo seleccionado y su dispositivo de transformación.*

#### A8. Restaurar y guardar la vista previa

Con el puntero en la ventana gráfica, seleccione todos los huesos de pose. Presione **F3**, busque `Clear Pose Transforms` y elija**Todos**. Confirme que el maniquí vuelva a su pose de T. Utilice**File → Save As** y asigne al archivo el nombre `SimpleHuman_Mannequin.blend`. Mantenga este punto de control antes de continuar.

![A8: restaurar y guardar la vista previa](../images/rig-builder/en/a09-clear-pose.png)

*1 — Borrar búsqueda de transformaciones de pose. 2 — Todo restablece los huesos de pose seleccionados.*

### Parte B: Maniquí sin rig mediante Auto-Rig

#### B1. Selecciona la malla del maniquí

Continúe desde el punto de control neutral en la Parte A. Cambie a **Object Mode** y seleccione `SimpleHumanArmature_Mannequin` en el Outliner. Eliminaremos deliberadamente su rig antes de ejecutar el asistente. Guarde el resultado con un nombre de archivo diferente para conservar la Parte A.

![B1: Selecciona la malla del maniquí](../images/rig-builder/en/b01-select-mesh.png)

*1 — Seleccione la malla, no la armadura.*

#### B2. Hornea la vista previa en una malla

Con solo el maniquí seleccionado, presione **F3**, busque `Convert Mesh` y ejecútelo. Esto mantiene la geometría neutra visible y elimina el modificador de armadura. Haga esto con el maniquí en su postura de T restaurada.

![B2: Hornear la vista previa en una malla](../images/rig-builder/en/b02-convert-mesh.png)

*1 — Comando Convertir malla.*

#### B3. Borrar el padre

Presione **Alt+P** y elija `Clear and Keep Transformation`. Esto desprende la malla del viejo metarig sin moverlo.

![B3: borrar el padre](../images/rig-builder/en/b03-clear-parent.png)

*1 — Limpiar y mantener la transformación.*

#### B4. Quitar las pesos viejas

Abra **Object Data Properties → Vertex Groups**. En el menú desplegable de la lista, elija `Delete All Groups`. Estos grupos pertenecen al antiguo metarig; el asistente creará otros nuevos. Esta acción es para esta malla de entrenamiento desechable.

![B4: Retire los pesos viejos](../images/rig-builder/en/b04-clear-groups.png)

*1 — Menú Grupos de vértices. 2 — Eliminar todos los grupos.*

#### B5. Verificar el punto de control sin rig

Oculte el antiguo `SimpleHumanArmature` usando su ícono de ojo Outliner. Verifique que el maniquí permanezca visible, que su panel Modificadores no tenga ningún modificador de Armadura y que su lista de Grupos de Vértices esté vacía. Esta es la entrada del maniquí sin rig. BoneCraft 9.1.2 genera maniquíes a partir de una armadura; Separar esta vista previa es el camino hacia una malla de entrenamiento sin rigs.

![B5: Verificar el punto de control sin plataforma](../images/rig-builder/en/b05-rigless-check.png)

*1 — Ocultar el antiguo metarig. 2 — Pila de modificadores vacía.*

#### B6. Habilite la pestaña Rig Builder de la ventana gráfica

Abra **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Habilite**Rig Builder** y elija**Left**. Cierre Preferencias, coloque el puntero sobre la ventana gráfica y presione**T** si el estante de herramientas izquierdo está oculto. Utilice esta pestaña de ventana gráfica para colocar marcadores: en el host 9.1.2 probado, iniciar Colocar marcador desde Propiedades de escena no aceptaba clics en la ventana gráfica.

![B6: Habilite la pestaña Rig Builder de la ventana gráfica](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — Habilitar Rig Builder. 2 — Ubicación del estante de herramientas izquierdo.*

#### B7. Iniciar montaje automático

Con el maniquí sin rig seleccionado, haga clic en **Start Auto-Rig**. La captura de pantalla muestra el botón Propiedades de escena equivalente; el mismo comando está en la parte superior de la pestaña Rig Builder de la ventana gráfica habilitada en el paso anterior.

![B7: Iniciar montaje automático](../images/rig-builder/en/b06-start-wizard.png)

*1 — Iniciar montaje automático.*

#### B8. Elija la malla de entrada

En `Select Mesh`, seleccione el modelo y verifique la verificación de malla seleccionada, luego haga clic en **Next**. No elija un widget u otro objeto de vista previa.

![B8: Elija la malla de entrada](../images/rig-builder/en/b07-select-input.png)

*1 — Entrada de maniquí. 2 — Siguiente.*

#### B9. Elija una rig de carrocería con ambos métodos

Seleccione **Body Only** y `Kinematics: IK + FK`. Mantenga**Generate Control Shapes** habilitado. Haga clic en**Next**. Este maniquí cápsula no tiene topología facial, por lo que Body + Face es innecesario.

![B9: Elija una rig de carrocería con ambos métodos](../images/rig-builder/en/b08-body-ikfk.png)

*1 — Sólo cuerpo. 2 — IK + FK. 3 — Siguiente.*

#### B10. Detectar marcadores corporales iniciales

En Marcadores corporales, haga clic en **Detect Markers** en Detección inteligente. Trate sus conjeturas como punto de partida. Mantenga**Mirror Symmetry** habilitado para este maniquí simétrico. No acepte todas las conjeturas sin comprobarlas.

![B10: Detectar marcadores corporales iniciales](../images/rig-builder/en/b09-detect-markers.png)

*1 — Detectar marcadores. 2 — Simetría de espejo.*

#### B11. Revisar las posiciones detectadas

Verifique la parte superior de la cabeza, la base del cuello, la pelvis, las muñecas y los tobillos contra la malla visible. Esta vista previa segmentada produce varias conjeturas de baja confianza. Revise y corrija tanto los puntos de referencia principales como los puntos de referencia de precisión opcionales antes de generarlos. Las etiquetas de confianza describen la detección original; una marca verde al comienzo de una fila indica que la ubicación actual está confirmada.

![B11: Revisar las posiciones detectadas](../images/rig-builder/en/b10-review-markers.png)

*1 — Resumen de confianza de la detección. 2 - Filas de marcador corporal.*

#### B12. Coloque una muñeca sobre la malla.

En la pestaña de la ventana gráfica **Rig Builder**, haga clic en el cuentagotas**Place Marker** en la muñeca izquierda y luego haga clic en la superficie de la muñeca en la ventana gráfica. Para un marcador ya confirmado, restablezca esa fila primero para exponer su botón de ubicación. En la vista frontal, la muñeca izquierda del personaje está a la derecha de la pantalla.

![B12: Colocar una muñeca sobre la malla.](../images/rig-builder/en/b11-place-wrist.png)

*1 — Control de colocación de la muñeca izquierda. 2 — Haz clic en la superficie de la muñeca.*

#### B13. Revisa la muñeca y los tobillos reflejados.

Verifique que ambas filas de muñecas ahora muestren marcas verdes y coordenadas X opuestas. Repita la colocación para `Ankle Left`; la simetría suministra el tobillo derecho. Coloque cada tobillo en su articulación, no en el dedo del pie. Verifique la simetría con la malla en lugar de copiar las coordenadas del ejemplo en un personaje de diferente tamaño.

![B13: Comprobar la muñeca y los tobillos reflejados.](../images/rig-builder/en/b12-mirrored-wrist.png)

*1: par de muñecas confirmado. 2 — Muñeca reflejada en la malla.*

#### B14. Refinar hombros y codos

Desplácese hasta Marcadores de precisión. Restablezca y coloque `Shoulder Left` en el pivote de la parte superior del brazo y `Elbow Left` en el espacio del codo. Confirme sus socios reflejados. Mantenga la muñeca en el extremo de la mano del antebrazo. Estos puntos determinan la cadena del brazo, por lo que un hombro o codo adivinado en la cápsula incorrecta necesita corrección.

![B14: Refinar hombros y codos](../images/rig-builder/en/b13-arm-precision.png)

*1 — Filas de marcadores de hombros y codos. 2 — Hombro. 3 — Codo.*

#### B15. Refinar caderas y rodillas

Coloque `Hip Left` en la parte superior del muslo y `Knee Left` en el espacio entre muslo y espinilla. Verifique el lado opuesto suministrado por simetría. Mantenga la pelvis en la línea central, entre las caderas.

![B15: Afinar caderas y rodillas](../images/rig-builder/en/b14-leg-precision.png)

*1 — Fila de cadera y rodilla. 2 — Superficie de la cadera. 3 — Espacio entre las rodillas.*

#### B16. Verifique la profundidad y los dedos de los pies desde el costado.

Presione `Numpad 3` con el puntero sobre la ventana gráfica. Verifique los puntos de referencia en ortografía derecha y desde el frente. Coloque `Toe Left` cerca de la parte delantera del pie; verificar su socio reflejado. Un marcador puede parecer correcto desde el frente pero estar demasiado adelante o detrás del cuerpo.

![B16: Verifique la profundidad y los dedos desde el costado](../images/rig-builder/en/b15-side-depth.png)

*1 — Ortográfica derecha. 2 - Fila del marcador del dedo del pie. 3 — Superficie del pie.*

#### B17. Coloca los talones

Restablezca un talón adivinado erróneamente y luego coloque `Heel Left` cerca de la parte posterior del pie en la vista lateral. Verifique el talón derecho. Aunque estos marcadores son opcionales, dejar ambos en cero produjo una advertencia de proximidad en la versión probada. Colocarlos en los pies aclaró esa advertencia.

![B17: Colocar los talones](../images/rig-builder/en/b16-place-heels.png)

*1 — Par de talones confirmado. 2 — Ubicación del talón.*

#### B18. Confirmar y continuar

Revise la parte superior de la cabeza, la base del cuello y la pelvis, así como cada punto de referencia emparejado. Haga clic en **Confirm All Placed** y luego en**Next**. Las marcas verdes al lado de los nombres indican el estado de confirmación; las etiquetas de confianza REVISAR/AJUSTAR originales pueden permanecer visibles en 9.1.2.

![B18: Confirmar y continuar](../images/rig-builder/en/b17-confirm-markers.png)

*1 — Confirmar todo lo colocado. 2 — Siguiente.*

#### B19. Saltate los dedos para esta malla

Elija `0 — No Fingers` y haga clic en **Next**. Este maniquí tiene cápsulas para las manos pero no tiene geometría para los dedos. En una malla de mano real, elija el recuento apropiado y coloque sus marcadores de dedos en su lugar.

![B19: Saltar los dedos para esta malla](../images/rig-builder/en/b18-no-fingers.png)

*1 — Sin dedos. 2 — Siguiente.*

#### B20. Revisar y generar

Solicite **All checks passed** antes de continuar. Utilice**IK + FK**, formas de control en, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers` y**Game Ready** para este ejercicio. Desactive los huesos torcidos, los huesos de la falda, la preservación del volumen y los correctivos para las articulaciones. Haga clic en**Generate Rig**. Estas configuraciones describen este modelo de entrenamiento simple, no una prescripción de exportación universal.

![B20: Revisar y generar](../images/rig-builder/en/b19-review-generate.png)

*1 — Verificaciones de marcadores. 2 — Configuración de generación. 3 — Generar rig.*

#### B21. Construye los controles del animador.

Después de la generación, haga clic en **Build Control Rig**. Generate Rig suministra la rig de carrocería y las pesos; Build Control Rig agrega la capa de control que se usa a continuación. No vuelva a hacer clic en Maniquí rápido: la malla de entrada ya está presente, incluso si el panel de finalización muestra su oferta de maniquí genérico.

![B21: construir los controles del animador](../images/rig-builder/en/b20-build-controls.png)

*1 — Construir rig de control.*

#### B22. Termina el asistente

Espere a que aparezca el mensaje de finalización del rig de control y luego haga clic en **Close Wizard**. La nueva armadura aparece en el Outliner. Mantenga oculto el antiguo metarig de Simple Human. La nueva rig debe deformar la malla; Simplemente ver huesos en la ventana gráfica no es validación suficiente.

![B22: Termina el asistente](../images/rig-builder/en/b21-close-wizard.png)

*1: el botón Crear ahora está deshabilitado. 2 — Cerrar asistente.*

### Parte C: comprobar los pesos y usar IK/FK

La armadura generada tiene este nombre de objeto en la versión probada (úselo en Outliner y en la herramienta de peso):

```text
BoneForge_Rig
```

`FK (Forward Kinematics)` **FK (cinemática directa)** propaga las rotaciones por una jerarquía: gira el brazo, después el antebrazo y después la mano. Es adecuada para movimientos amplios y extremidades libres. `IK (Inverse Kinematics)`**IK (cinemática inversa)** parte de un extremo: mueve el objetivo de la muñeca o del tobillo y el solucionador flexiona la cadena para alcanzarlo. Es adecuada para pies apoyados y manos que deben tocar una superficie.

|Tarea|Control para usar|que mirar|
|---|---|---|
|balancear un brazo|FK controles de hombro y codo|Los controles infantiles siguen a sus padres.|
|coloca una mano|IK objetivo de muñeca|Hombro y codo se resuelven hacia el objetivo.|
|planta un pie|IK objetivo de tobillo para esa pierna|Mueve el cuerpo mientras el objetivo alcanzable permanece en su lugar.|
|Apunte a doblar el codo o la rodilla.|Control de poste IK |El poste establece la dirección de curvatura; no es el objetivo de muñeca/tobillo|
|Cambiar método|Botones IK/FK de la extremidad|Verifique la pose tomada antes de introducir la animación|

El siguiente ejercicio compara un brazo en ambos modos. Cada miembro tiene su propio interruptor. `Bake IK / Bake FK` son herramientas de conversión de animaciones; un interruptor de una sola posición no reemplaza el horneado o la codificación de una animación. Consulte [Capa de control](05-rig-tools.md#control-layer-capa-de-control-ikfk) para conocer los otros controles.

#### C1. Abrir la capa de control

Seleccione **armadura generada**, elija**Pose Mode**, luego abra**BoneCraft → Review → Control Layer**. Hay un interruptor IK/FK independiente para cada brazo y pierna. Comience con**arm-L → FK**. Izquierda y derecha se refieren al personaje, por lo que brazo-L aparece a tu derecha en la vista frontal.

![C1: Abrir la capa de control](../images/rig-builder/en/c02-control-layer.png)

*1 — Modo Pose. 2 — Capa de control e interruptor de brazo-L.*

#### C2. Mostrar los controles del animador.

Abra **Object Data Properties → Bone Collections** de la armadura. Utilice las estrellas Solo para `Controls` y**FK** para aislar sus formas de control. Habilite**In Front** en Visualización de ventana gráfica cuando los controles estén ocultos por la malla. Posteriormente incluya**IK** cuando utilice objetivos. Esta lista de colecciones nativas también funciona si el panel Colecciones BoneCraft no logra dibujar en este host.

![C2: Mostrar los controles del animador.](../images/rig-builder/en/c03-visible-controls.png)

*1 — Controles y estrellas FK Solo. 2 — Delante.*

#### C3. Seleccione el control del antebrazo FK

En la vista frontal, haz clic en el control circular en el codo izquierdo del personaje. Verifique que el nombre de selección de la ventana gráfica sea **forearm.fk-L**. Un control de antebrazo FK gira alrededor del codo; seleccionar el control del hombro rotaría la parte superior del brazo y sus hijos.

![C3: Seleccione el control del antebrazo FK](../images/rig-builder/en/c04-select-fk.png)

*1 — Control antebrazo.fk-L seleccionado. 2 — FK está activo para brazo-L.*

#### C4. Girar e inspeccionar la deformación.

Gire el control FK seleccionado sobre **Y** global, aproximadamente `−45°` para este ejemplo de vista frontal. Utilice la herramienta Girar; en el mapa de teclas Bforartists que se muestra,**Ctrl+E**,**Y**, escriba**-45**, luego**Enter** realiza esa rotación. El atajo de rotación predeterminado de Blender es**R**. La captura de pantalla muestra deliberadamente el problema de peso inicial: la cápsula del brazo se inclina con el antebrazo. No acepte esto como una rig terminada.

![C4: Girar e inspeccionar la deformación.](../images/rig-builder/en/c05-fk-weight-check.png)

*1: Movimiento incorrecto de la parte superior del brazo durante la prueba FK.*

#### C5. Recalcular los pesos del maniquí.

Si la prueba de pose anterior falla, cambie a **Object Mode**, seleccione la malla y abra**BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**. Configure Malla para Recargar peso al maniquí y Armadura existente a**armadura generada**. Elija**Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0` y `Minimum Weight: 0.001`. Mantenga**Keep Weight Backup** activado y luego ejecute**Automatic Bone Weight Recalculation**. Esto reparó la vista previa segmentada en la versión probada.

![C5: Recalcular los pesos del maniquí](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — Malla y armadura. 2 - Calor de huesos. 3 — Configuración de reemplazo y copia de seguridad. 4 — Recalcular.*

#### C6. Verifique la curva FK reparada

Seleccione nuevamente la armadura generada y regrese a **Pose Mode**. La parte superior del brazo ahora debe permanecer horizontal desde el hombro hasta el codo mientras el antebrazo se eleva desde el codo. El objeto oculto `WEIGHTS_BACKUP_…` conserva los pesos antiguos. Prueba también otras extremidades antes de usar tu propio personaje en la animación. Un esqueleto generado por sí solo no es prueba de un desollado correcto.

![C6: Verificar la curva FK reparada](../images/rig-builder/en/c05-fk-result.png)

*1 — La parte superior del brazo permanece en su lugar. 2 — El antebrazo se dobla a la altura del codo.*

#### C7. Cambie el mismo brazo a IK

Haga clic en **arm-L → IK**. El interruptor ajusta el objetivo a la postura actual, por lo que el brazo debe permanecer en su postura elevada. Agregue**IK** a las colecciones Solo visibles si sus objetivos están ocultos. Cambios de conmutación que controlan la cadena; no significa que se haya grabado una nueva animación.

![C7: Cambie el mismo brazo a IK](../images/rig-builder/en/c06-switch-ik.png)

*1 — interruptor brazo-L IK. 2 — Pose mantenida al cambiar.*

#### C8. Seleccione el objetivo de muñeca IK

Haga clic en el control en la muñeca y verifique el nombre de selección **forearm.ik-L**. A pesar de su nombre de antebrazo, este es el objetivo final de la cadena del brazo. Mueva este objetivo para colocar la mano; el solucionador cambia los ángulos de los hombros y los codos para alcanzarlo.

![C8: Seleccione el objetivo de muñeca IK](../images/rig-builder/en/c07-select-ik.png)

*1 — Objetivo de muñeca seleccionado. 2 — Nombre de la selección.*

#### C9. Mueve el objetivo y compara

Mueva el objetivo de muñeca ligeramente hacia adentro a lo largo de **X** global. En este ejemplo, `−0.15 m` crea una curva visiblemente diferente. En el mapa de teclas que se muestra, use**Ctrl+W**,**X**, escriba `-0.15` y luego**Enter**, o arrastre la flecha X de la herramienta Mover. El atajo de movimiento predeterminado de Blender es**G**. Compare todo el brazo con el ejemplo FK: el punto final conduce y ambos segmentos del brazo siguen. Mantenga el objetivo al alcance del brazo.

![C9: Mueve el objetivo y compara](../images/rig-builder/en/c08-move-ik.png)

*1: punto final de la muñeca. 2 — La cadena responde. 3 — Ejemplo de movimiento X.*

#### C10. Vuelve atrás y guarda el ejemplo.

Haga clic en **arm-L → FK** nuevamente. Los controles FK se ajustan a la pose actual de IK. Verifique que la malla no salte, luego use**File → Save As** para guardar `Mannequin_AutoRig.blend`. La captura de pantalla muestra el ejemplo guardado con FK activo. Para una copia de entrenamiento neutral, mantenga las cuatro extremidades en FK, seleccione todos los controles de pose visibles y use**F3 → Clear Pose Transforms → All** como en la Parte A; guárdelo con un nombre separado.

![C10: Retroceder y guardar el ejemplo.](../images/rig-builder/en/c10-save-complete.png)

*1 — FK activo nuevamente. 2 — Pose preservada. 3 — Nombre del archivo guardado.*

**Verificación de finalización:** conservó la vista previa del metarig original, separó un maniquí sin rig, generó un nuevo rig de carrocería y sus controles, corrigió los pesos de la vista previa y comparó una rotación FK con un movimiento objetivo IK. Mantenga el rig guardado como ejemplo de aprendizaje; reemplace la vista previa con una geometría de caracteres adecuada para la producción.

---

### Redireccionamiento de animación

Mover la animación de un esqueleto a otro se trata en [Herramientas de rig: reorientación](05-rig-tools.md#redireccionar).

---

## Fusión de Huesos

**Qué hace:** Combina dos armaduras en una (por ejemplo, una rig para el cuerpo y una rig para la ropa o el cabello) manteniendo cada peso.

[Guía 11](03-guides-b.md#guía-11-une-dos-rigs) lo explica paso a paso.

**Las tres etapas:**
1. Alcance: elija las dos armaduras y revise en qué se diferencian
2. Cambiar nombre: resuelve conflictos de nombres y marca huesos nuevos
3. Fusionar: vista previa y luego fusionar

**Controles clave:**
- **Base** — la armadura que permanece; la otra armadura se fusiona con ella y luego se oculta
- **Analyze** — compara los dos esqueletos;**Acknowledge Scope — Proceed to Rename** abre etapa 2
- **Normalize Both Armatures**: cambia el nombre de los huesos estándar de ambos rigs a un estándar de nomenclatura (Mixamo prefijado, Mixamo despojado o personalizado)
- **Auto-Propose Renames**: sugiere nombres para los propios huesos de la rig fusionada
- **Apply Rename**: cambia el nombre de una entrada (un paso para deshacer);**Apply Batch Pattern** renombra muchos con un patrón (con `{bone}`, `{side}` y `{index}` )
- **Mark as Unique**: mantiene un hueso como hueso nuevo en lugar de fusionarlo
- **Verify Rename — Proceed to Merge** — abre la etapa 3
- **Run Merge Preview**: informa lo que haría la fusión, sin cambiar nada
- **Merge Armatures**: realiza una copia de seguridad de ambas armaduras y las fusiona

**Dónde encontrarlo:** Pestaña BoneCraft → Fusión de huesos

Siguiente: [Mecanismos](07-mechanisms.md)
