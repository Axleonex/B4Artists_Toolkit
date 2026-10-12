# Herramientas de CATS

[← Índice](index.md)

Las herramientas de CATS están en la pestaña **CATS** de la barra lateral derecha (pulsa **N**), en la sección **CATS**, y siempre en la pestaña **Escena** del editor de **Propiedades**. Siguen el pipeline descrito en [El pipeline de CATS](04-cats-pipeline.md). Elige arriba en la sección la armadura con la que trabajan.

---

## Corregir Modelo

**Fase del pipeline:** 1 (siempre la primera)

**Qué hace:** una limpieza de un clic antes de cualquier otra operación de CATS. Elimina problemas ocultos que, si no, romperían en silencio cada paso posterior.

**Opciones (cada una se puede desactivar):**
- Aplicar modificadores
- Eliminar duplicados — combinar vértices duplicados en la misma posición
- Recalcular normales — corregir superficies del revés
- Eliminar geometría suelta — caras no unidas al cuerpo
- Eliminar grupos de vértices vacíos
- Eliminar huesos de peso cero — huesos que no mueven ningún vértice
- Eliminar restricciones y cuerpos rígidos que VRChat no puede usar

Haz clic en **Corregir Modelo** para ejecutarlas en la malla seleccionada de una sola vez.

---

## Traducir Nombres de Huesos

**Qué hace:** traduce los nombres de huesos de tu esqueleto a nombres de VRChat en inglés. Funciona sin conexión, a partir de un diccionario integrado de nombres de huesos conocidos.

**Idiomas admitidos:** japonés (日本語, el más común, de MMD y de muchos modelos de la comunidad), chino (中文), coreano (한국어), portugués (Português), español y francés (Français).

**Controles principales:** el **Idioma** de los nombres de origen y el botón de traducción (**Traducir Nombres de Huesos**).

Se trata del idioma de los nombres de huesos del modelo, no del idioma de tu interfaz: para un modelo MMD japonés, úsalo esté Bforartists en el idioma que esté.

---

## Unir Mallas

**Qué hace:** combina los objetos de malla de tu avatar en una sola malla. VRChat rinde mejor con una malla por avatar. Cuando las mallas tienen shape keys distintos, CATS rellena los que faltan con formas neutras, así que la malla unida tiene un único conjunto coherente.

**Controles principales:** la lista de mallas (actualízala con el botón de al lado) y luego **Unir Mallas**.

**Cuándo usarlo:** cuando toda la ropa y los accesorios estén unidos y con pesos, y después de Corregir Modelo. Unir antes de Corregir Modelo extiende los problemas de vértices duplicados de un objeto a otro; la malla unida conserva entonces vértices fantasma de cada objeto original, y los visemas generados la desgarran por las uniones.

---

## Combinador de atlas de materiales

**Fase del pipeline:** 2 (opcional)

**Qué hace:** hornea varios materiales en una sola hoja de textura (un atlas). Menos materiales dan un mejor rango de rendimiento en VRChat.

**Controles principales:**
- **Analyze** (analizar) — enumera tus materiales y texturas, con diagnósticos, grupos de duplicados y tamaños forzados. Elige qué materiales y qué texturas incluir: desmarca los que quieras dejar como están.
- **Smart Combine Materials** (combinación inteligente de materiales) — el camino recomendado: hornea el atlas y hace que cada malla apunte a él; el UV del atlas se convierte en el UV0 para exportar
- **Hornear Atlas** — un horneado simple; **Add Group** (añadir grupo) y **Remove Group** (quitar grupo) hornean grupos de materiales por separado
- Anular Configuraciones Heredadas — tamaño del atlas, método y semilla de UV, preajuste de empaquetado, margen de horneado, paso de rotación de islas y pasadas de horneado (Albedo por defecto; Normal, Emission y Roughness se pueden hornear como salidas separadas)
- **Preserve Backup Duplicate** (conservar duplicado de seguridad) — guarda una copia de los originales
- **Aceptar — Eliminar Copia de Seguridad** — conserva el resultado y borra la copia de seguridad
- **Revertir — Restaurar Originales** — vuelve a los materiales originales
- **Copy Debug Report** (copiar informe de depuración) — copia los diagnósticos al portapapeles para un informe de error

Los materiales VRM / MToon conservan su transparencia: se respeta el modo alfa y se compara con el alfa real de la textura, la emisión no se satura y las teselas con problemas se marcan en magenta tras el horneado.

**Linaje y créditos:** este flujo de trabajo continúa el linaje de integración de CATS, da crédito al Cats Blender Plugin original, da crédito a Grim-es/material-combiner-addon por el linaje de Material Combiner, y da crédito a UV Toolkit de Alexander Belyakov y al repositorio de archivo oRazeD/UVToolkit por la inspiración del flujo de trabajo de UV. BoneCraft implementa sus propias ayudas de UV para atlas en lugar de incluir el código fuente de UVToolkit.

---

## Visemas

**Fase del pipeline:** 3

**Qué hace:** crea los 15 visemas de VRChat a partir de tres formas base de boca.

**Controles principales:** **Forma A**, **Forma O** y **Forma CH** (elígelas, o usa **Detección Automática**), una opción para sobrescribir los visemas existentes y **Generar Visemas**. Consulta la [guía 13, fase 2](03-guides-b.md#fase-2--generación-de-visemas).

---

## Seguimiento Ocular

**Fase del pipeline:** 4 (ejecutar después de Corregir Modelo)

Sin Corregir Modelo antes, la detección de ojos puede engancharse a geometría duplicada sobrante en lugar de a los ojos reales y poner las restricciones en el vacío: los avatares llegan a VRChat mirando fijamente al suelo.

**Qué hace:** encuentra los huesos de los ojos de tu avatar, los nombra como exige VRChat (`LeftEye` y `RightEye`) y crea las restricciones de rotación que mueven los ojos con naturalidad en VRChat.

**Controles principales:**
- **Detección Automática** — encuentra huesos que coinciden con los nombres y posiciones de los huesos de los ojos
- **Ojo Izquierdo** y **Ojo Derecho** — los huesos de los ojos, si los eliges tú
- **Límite Superior**, **Límite Inferior** y **Límite Lateral** — cuánto pueden girar los ojos
- **Crear Seguimiento Ocular** — renombra los huesos y crea las restricciones

---

## Pose y Shape Keys

**Fase del pipeline:** 5 (opcional)

### Pose a Shape Key

Convierte la pose actual en un shape key nuevo, para expresiones personalizadas o una forma de reposo corregida. Posa la armadura en Modo Pose, vuelve al Modo Objeto, luego haz clic en **Pose a Shape Key** y pon nombre al shape key.

### Shape Key a Basis

Lo contrario: hornea un shape key en la forma de reposo neutra de la malla. Úsalo para fijar para siempre una pose de reposo corregida. Ejecútalo también después de Corregir Modelo.

---

## Transformaciones y FBT

**Fase del pipeline:** 6 (la última)

### Aplicar Todas las Transformaciones

Aplica posición, rotación y escala a la malla y a la armadura a la vez, para que todo se lea con valores limpios. El SDK de VRChat lo necesita: una escala sin aplicar hace que los avatares tengan un tamaño equivocado en VRChat.

### Corregir FBT

Una corrección de transformación para configuraciones de Full Body Tracking: mueve el hueso raíz al nivel del suelo.

### Eliminar FBT

Quita de nuevo la corrección de Corregir FBT.

---

## Herramientas de Huesos

- **Crear Hueso Raíz** — añade un hueso raíz (con el nombre de **Nombre de Raíz**) en la base de la jerarquía
- **Combinar Huesos** — combina en sus padres los huesos más cortos que el **Umbral de Combinación**
- **Duplicar Huesos** — duplica los huesos seleccionados

---

## Herramientas de Armadura

**Qué hace:** fusiona una armadura en otra, por ejemplo la armadura de un conjunto de ropa en la del cuerpo.

**Controles principales:**
- **Base / Root** (base / raíz) — la armadura que se queda (el resultado conserva su nombre)
- **Incoming** (entrante) — la armadura que se fusiona en ella; los huesos con el mismo nombre se integran en la base
- Naming Prep (preparación de nombres) — hace coincidir los nombres de huesos de los dos rigs antes de fusionar. Funciona con cualquier rig, no solo con importaciones de Mixamo: elige Mixamo Prefixed y haz clic en **Normalize Merge Names** (normalizar nombres para fusionar), luego elige Mixamo Stripped y normaliza otra vez; ambos rigs acaban con los mismos nombres.
- Opciones para emparentar los huesos automáticamente y para unir las mallas después
- **Merge Incoming Into Base** (fusionar la entrante en la base) — fusiona

Para una fusión por etapas con vistas previas, usa Fusión de Huesos (consulta [Constructor de Rig](06-rig-builder.md#fusión-de-huesos)).

---

## Herramientas de Malla

- **Separar por Materiales** — una malla por material
- **Separar por Partes Sueltas** — una malla por pieza conectada
- **Separar por Shape Keys** — separa las partes que mueven los shape keys

---

## Smart Automatic Weights (pesos automáticos inteligentes)

Vuelve a calcular los pesos de la malla a partir del rig existente: **Smart Automatic Weights**, con **Advanced Recalculation** (recálculo avanzado) para todos sus ajustes. La misma herramienta está en la pestaña BoneCraft (Malla → Herramientas de Peso), descrita en [Herramientas de rig](05-rig-tools.md#recálculo-automático-de-pesos-de-huesos).

---

## Estado del Pipeline y Registro de Operaciones

El Estado del Pipeline muestra cuáles de las seis fases están hechas. El Registro de Operaciones enumera cada operación de CATS con su hora y su resultado (Changed, Clean o Failed); **Copiar** lo pone en el portapapeles y **Limpiar** lo vacía. Consulta [El pipeline de CATS](04-cats-pipeline.md).

Siguiente: [Soluciones rápidas y glosario](10-reference.md)
