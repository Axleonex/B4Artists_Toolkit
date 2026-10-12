# Outils VRChat

[← Contenu](index.md)

## Outils VRChat

Les outils VRChat se trouvent dans l'onglet **CATS** dans la barre latérale droite (appuyez sur**N**), dans la section**Avatar Tools**. Ses sous-sections couvrent les os humanoïdes, la physique des cheveux, la cartographie et l'exportation des visèmes. La section distincte**VRChat Tools** située en dessous regroupe les utilitaires Performance, Clothing et Naming. La même section se trouve dans l'onglet**Properties** de l'éditeur**Scene** tandis que Préférences → Onglets → Propriétés de la scène → Afficher est activé. Ce commutateur ne masque pas l'onglet de la fenêtre CATS.

---

### Configurer les Os Humanoïdes

Cartographie les os de votre squelette sur les emplacements humanoïdes du VRChat et vérifie la cartographie.

Voir [Guide 5 : Mappez votre avatar sur le système corporel de VRChat](02-guides-a.md#guide-5-mapper-votre-avatar-sur-le-système-corporel-de-vrchat).

---

### Ajouter la Physique des Cheveux

Installe des chaînes PhysBone sur les cheveux, les oreilles, les queues et les accessoires, avec des collisionneurs.

Voir [Guide 6 : Ajouter la physique des cheveux](02-guides-a.md#guide-6-ajouter-la-physique-des-cheveux).

---

### Attacher les Vêtements

**Où le trouver :** Onglet CATS → Outils VRChat → Vêtements

Fusionne les vêtements sur le squelette de votre avatar et transfère son poids.

Voir [Guide 7 : Attachez des vêtements qui bougent avec votre corps](02-guides-a.md#guide-7-attacher-des-vêtements-qui-bougent-avec-votre-corps).

---

### VRChat Naming Extras (extras de nommage VRChat)

**Où le trouver :** Onglet CATS → Outils VRChat → Dénomination

**Ce qu'il fait :** Détecte le style de dénomination de votre squelette et renomme les os en masse.

Voir [Guider 4 : Corrigez les noms d'os de votre avatar](02-guides-a.md#guide-4-corriger-les-noms-dos-de-votre-avatar).

**Outils par lots :** **Find and Replace**,**Add Prefix**,**Remove Prefix**,**Add Suffix**,**Remove Suffix** et**Regex Replace**

---

### VRChat Viseme Mapping (mappage des visèmes VRChat)

**Ce qu'il fait :** Mappe les clés de forme de votre maillage sur les 15 visèmes de synchronisation labiale de VRChat.

Voir [Guider 8 : Configurer la synchronisation labiale](03-guides-b.md#guide-8-configurer-la-synchronisation-labiale). Pour créer des visèmes que votre avatar ne possède pas encore, voir [CATS Outils : Visèmes](09-cats.md#visèmes).

**15 emplacements pour visèmes de VRChat  :** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### Vérifier les Performances

**Où le trouver :** Onglet CATS → Outils VRChat → Performances

**Ce qu'il fait :** Mesure le classement des performances VRChat de votre avatar et propose des correctifs.

Voir [Guide 9 : Améliorez les performances de votre avatar](03-guides-b.md#guide-9-améliorer-les-performances-de-votre-avatar).

**Niveaux de performances (du meilleur au pire) :** Excellent → Bon → Moyen → Mauvais → Très mauvais

**Outils :**
- **Calculate Performance Rank** — le rang actuel, avec une répartition par polygones, maillages skinnés, emplacements de matériaux, os, PhysBones et contacts
- **Remove Zero-Weight Bones**,**Merge Same-Material Meshes**,**Remove Unused Shape Keys** et**Remove Unused Vertex Groups** — les correctifs de l'optimiseur (**What-If Mode** montre ce qu'ils changeraient)
- Décimation VRChat  : réduit le nombre de polygones selon un rapport (**Preview** d'abord, puis**Apply** ), garantissant ainsi la sécurité des clés de forme.

---

### Exporter vers VRChat

**Ce qu'il fait :** Exporte votre avatar terminé en tant que FBX pour le SDK VRChat dans Unity. Les clés de forme (mélange de formes) sont conservées sauf si**Remove Shape Keys** est activé.

**Paramètres :**
- **Folder** — où va l'exportation
- **Avatar** — le nom du fichier exporté
- **Sidecar** — écrit également un fichier de paramètres `.bfvrc` pour l'importateur BoneCraft de Unity.
- **Merge Meshes** — joint les maillages de la copie d'exportation en un seul
- **Separate Clothing** — conserve les vêtements sous forme de mailles séparées
- **Remove Shape Keys** — applique les clés de forme à la base de la copie d'exportation
- **Embed Textures** — regroupe les textures dans le FBX, afin que Unity les trouve
- **Helper Meshes** — inclut des maillages cachés ou auxiliaires ; laissez-le désactivé pour les avatars normaux

**Boutons :** **Export to VRChat (Unity)**,**Generate Sidecar**,**Copy Importer Path** (le chemin du script d'importation Unity de BoneCraft ) et**Check / Preserve MToon** pour les matériaux VRM. La section répète également le statut humanoïde avec**Auto-Map Humanoid**,**Normalize Names** et**Validate**.

---

### Nettoyage

Le nettoyage du maillage avant l'exportation réside dans les outils CATS  : **Fix Model**,**Join Meshes** et**Apply All Transforms**. Voir [CATS Outils](09-cats.md).

---

## Pont VRM

Les outils VRM se trouvent dans l'onglet **CATS** →**Import / Export** →**VRM / VRoid**. Ils ont besoin du module complémentaire VRM; la section l'installe (**Auto-Install Latest from GitHub**,**Install from.zip on Disk…**,**Open Extensions Page** ).

---

### Import VRM et VRoid

**Ce qu'il fait :** Importe les avatars `.vrm` (VRoid Studio, Virtual Cast et autres avatars VRM ) avec leurs matériaux, squelettes et clés de forme.

- **Import VRM…** — un fichier `.vrm`
- **Import VRoid (.vroid /.zip)…** — un téléchargement du hub VRoid (`.zip` ). Un projet VRoid Studio (`.vroid` ) affiche une carte qui explique comment l'exporter vers VRM en premier.

---

### VRM Export (export VRM)

**Ce qu'il fait :** Exporte votre personnage truqué au format VRM ou au format d'une application cible.

**Paramètres :**
- **Folder** et**File** — où il va et son nom ; l'extension suit la cible
- **Target** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo ou Resonite
- **Scope** — l'armature active ou chaque armature avec les données VRM
- Skip Lint – exportation sans vérification de la cible ; à utiliser uniquement lorsque vous comprenez le risque signalé

Cliquez sur **Export…**.

---

### VRM Lint (vérification VRM)

**Ce qu'il fait :** Vérifie l'armature par rapport à la cible choisie avant l'exportation : cartographie humanoïde, métadonnées VRM, visèmes de la cible et attentes de l'application cible.

**Lint Now** exécute le contrôle sans rien modifier. Les erreurs bloquent l'exportation, sauf si vous ignorez les peluches ; les avertissements expliquent ce que l'application cible peut encore importer mais fonctionner moins bien.

Si la charpie indique que des os humanoïdes sont manquants alors qu'ils existent, cliquez sur **Fix Humanoid Map**  : BoneCraft détecte à nouveau les emplacements humanoïdes et enregistre le mappage, sans renommer aucun os.

**Aussi ici :** **Convert SpringBones → PhysBones** (physique des cheveux VRoid à VRChat ) et**Map VRoid Visemes**.

---

## MMD Bridge (pont MMD)

Les outils MMD se trouvent dans l'onglet **CATS** →**Import / Export** →**MMD / PMX**. Ils ont besoin du module complémentaire mmd_tools ; la section l'installe (**Auto-Install Latest from GitHub**,**Install from.zip on Disk...** ).

---

### MMD Import (import MMD)

- **Import PMX / PMD...** — Modèles MMD
- **Import VMD Motion...** — Animations MMD
- **Import VPD Pose...** — MMD pose

---

### MMD Export (export MMD)

**Paramètres :** le**Folder**, puis pour chaque format un nom de fichier et une étendue (le modèle actif, ou chaque modèle MMD de la scène):**PMX File** et**PMX Scope**,**VMD File** et**VMD Scope**,**VPD File** et**VPD Scope**.

**Boutons :** **Export PMX...**,**Export VMD Motion...** et**Export VPD Pose...**

**Aussi ici :** **Convert Bone Names -> Unity** et**Convert Physics -> PhysBones**.

---

## Game Export (export pour jeux)

**Ce qu'il fait :** Exportations pour les moteurs de jeu avec un profil validé : Unreal (humanoïde ou universel), humanoïde Unity, humanoïde Godot et FBX ou GLB générique. Chaque correctif dont le profil a besoin est affiché et appliqué uniquement lorsque vous cliquez dessus, jamais silencieusement.

**Paramètres :** le**Profile**, le**Animation** à inclure, le**Root Motion**, le**Interpolation** et le**T-Pose** utilisé pour l'exportation (par défaut, une pose en T pour l'humanoïde Unity et le VRChat ).

**Boutons :**
- **Check for Export** — vérifie l'installation par rapport au profil et répertorie les résultats
- **Apply Transforms (Fix)** — l'un des correctifs explicites que le contrôle peut offrir
- **Export (Profile)** — exporte avec le profil

**Où le trouver :** Onglet**CATS** →**Import / Export** →**Game Export**

---

## Tableau des tâches

**Ce qu'il fait :** Un résumé de la rig actuelle : un score de santé, des gains rapides et une liste des tâches BoneCraft trouvées (os humanoïdes manquants, noms non résolus, visèmes manquants, avertissements du validateur de rig, etc.), regroupées par catégorie.**Open Health Check** ouvre les détails ;**Refresh Task Board** vérifie à nouveau.

**Où le trouver :** Onglet**BoneCraft** →**Overview** →**Task Board**

---

### Inspecteur d'Os

**Ce qu'il fait :** Affiche l'os sélectionné en détail (son nom, son parent, ses contraintes, ses propriétés personnalisées et ses pilotes) et vous permet de modifier des propriétés simples sans passer en mode édition.

**Où le trouver :** Onglet**BoneCraft** →**Review** →**Bone Inspector**

Suivant: [CATS Outils](09-cats.md)
