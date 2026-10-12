# Outils VRChat

[← Sommaire](index.md)

## Outils VRChat

Les outils VRChat sont dans l'onglet **CATS** de la barre latérale de droite (touche **N**), dans la section **VRChat**. Ses sous-sections suivent l'ordre dans lequel vous en avez besoin : configuration VRChat (extras de nommage et os humanoïdes), corps et physique (cheveux, vêtements, visèmes), puis performances et export. La même section est toujours dans l'onglet **Scène** de l'éditeur **Propriétés**.

---

### Configurer les Os Humanoïdes

Mappe les os de votre squelette sur les emplacements humanoïdes de VRChat et vérifie le mappage.

Voir le [guide 5 : mapper votre avatar sur le système corporel de VRChat](02-guides-a.md#guide-5--mapper-votre-avatar-sur-le-système-corporel-de-vrchat).

---

### Ajouter la Physique des Cheveux

Configure des chaînes PhysBone sur les cheveux, les oreilles, les queues et les accessoires, avec des colliders.

Voir le [guide 6 : ajouter la physique des cheveux](02-guides-a.md#guide-6--ajouter-la-physique-des-cheveux).

---

### Attacher les Vêtements

Fusionne les vêtements sur le squelette de votre avatar et transfère leurs poids.

Voir le [guide 7 : attacher des vêtements qui bougent avec votre corps](02-guides-a.md#guide-7--attacher-des-vêtements-qui-bougent-avec-votre-corps).

---

### VRChat Naming Extras (extras de nommage VRChat)

**Ce qu'il fait :** détecte le style de nommage de votre squelette et renomme les os en masse.

Voir le [guide 4 : corriger les noms d'os de votre avatar](02-guides-a.md#guide-4--corriger-les-noms-dos-de-votre-avatar).

**Outils par lot :** **Rechercher et remplacer**, **Ajouter un préfixe**, **Supprimer le préfixe**, **Ajouter un suffixe**, **Supprimer le suffixe** et **Remplacement par Regex**

---

### VRChat Viseme Mapping (mappage des visèmes VRChat)

**Ce qu'il fait :** mappe les clés de forme de votre maillage sur les 15 visèmes de synchronisation labiale de VRChat.

Voir le [guide 8 : configurer la synchronisation labiale](03-guides-b.md#guide-8--configurer-la-synchronisation-labiale). Pour créer des visèmes que votre avatar n'a pas encore, voir [Outils CATS : Visèmes](09-cats.md#visèmes).

**Les 15 emplacements de visèmes de VRChat :** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### Vérifier les Performances

**Ce qu'il fait :** mesure le rang de performance VRChat de votre avatar et propose des corrections.

Voir le [guide 9 : améliorer les performances de votre avatar](03-guides-b.md#guide-9--améliorer-les-performances-de-votre-avatar).

**Niveaux de performance (du meilleur au pire) :** Excellent → Good → Medium → Poor → Very Poor

**Outils :**
- **Calculate Performance Rank** (calculer le rang de performance) — le rang actuel, détaillé par polygones, maillages skinnés, emplacements de matériaux, os, PhysBones et contacts
- **Supprimer les Os de Poids Zéro**, **Fusionner les maillages de même matériau**, **Supprimer les Clés de Forme Non Utilisées** et **Supprimer les Groupes de Sommets Non Utilisés** — les corrections de l'optimiseur (**Mode Hypothétique** montre ce qu'elles changeraient)
- Décimation VRChat — réduit le nombre de polygones selon un ratio (**Aperçu** d'abord, puis **Appliquer**), en préservant les clés de forme

---

### Exporter vers VRChat

**Ce qu'il fait :** exporte votre avatar terminé en FBX pour le SDK VRChat dans Unity. Les clés de forme (blend shapes) sont conservées, sauf si **Remove Shape Keys** est activé.

**Paramètres :**
- **Folder** (dossier) — où va l'export
- **Avatar** — le nom du fichier exporté
- **Sidecar** — écrit aussi un fichier de réglages `.bfvrc` pour l'importateur Unity de BoneCraft
- **Merge Meshes** (fusionner les maillages) — joint les maillages de la copie d'export en un seul
- **Separate Clothing** (vêtements séparés) — garde les vêtements en maillages séparés
- **Remove Shape Keys** (supprimer les clés de forme) — applique les clés de forme à la base de la copie d'export
- **Embed Textures** (intégrer les textures) — emballe les textures dans le FBX, pour qu'Unity les trouve
- **Helper Meshes** (maillages d'aide) — inclut les maillages cachés ou d'aide ; laissez-le désactivé pour les avatars normaux

**Boutons :** **Exporter vers VRChat (Unity)**, **Générer le sidecar**, **Copier le chemin de l'importateur** (le chemin du script d'import Unity de BoneCraft), et **Vérifier / Préserver MToon** pour les matériaux VRM. La section répète aussi l'état humanoïde avec **Auto-Map Humanoid** (mapper l'humanoïde automatiquement), **Normalize Names** (normaliser les noms) et **Valider**.

---

### Nettoyage

Le nettoyage du maillage avant l'export se fait dans les outils CATS : **Corriger le modèle**, **Joindre les Maillages** et **Appliquer Toutes les Transformations**. Voir [Outils CATS](09-cats.md).

---

## Pont VRM

Les outils VRM sont dans l'onglet **CATS** → **Importer / Exporter** → **VRM / VRoid**. Ils ont besoin de l'add-on VRM ; la section l'installe (**Installation Automatique depuis GitHub**, **Installer depuis .zip sur Disque…**, **Ouvrir la Page des Extensions**).

---

### Import VRM et VRoid

**Ce qu'il fait :** importe des avatars `.vrm` (VRoid Studio, Virtual Cast et d'autres avatars VRM) avec leurs matériaux, leur squelette et leurs clés de forme.

- **Importer VRM…** — un fichier `.vrm`
- **Import VRoid (.vroid / .zip)…** (importer VRoid) — un téléchargement VRoid Hub (`.zip`). Un projet VRoid Studio (`.vroid`) affiche une carte qui explique comment l'exporter d'abord en VRM.

---

### VRM Export (export VRM)

**Ce qu'il fait :** exporte votre personnage riggé en VRM, ou au format d'une application cible.

**Paramètres :**
- **Folder** et **File** (fichier) — l'emplacement et le nom ; l'extension suit la cible
- **Cible** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo ou Resonite
- **Scope** (portée) — l'armature active, ou chaque armature avec des données VRM
- Skip lint (ignorer la vérification) — exporter sans la vérification de la cible ; à n'utiliser que si vous comprenez le risque signalé

Cliquez sur **Exporter…**.

---

### VRM Lint (vérification VRM)

**Ce qu'il fait :** vérifie l'armature par rapport à la cible choisie avant l'export : mappage humanoïde, métadonnées VRM, visèmes de la cible, et attentes de l'application cible.

**Vérifier maintenant** lance la vérification sans rien modifier. Les erreurs bloquent l'export, sauf si vous ignorez la vérification ; les avertissements expliquent ce que l'application cible peut encore importer, mais avec un moins bon fonctionnement.

Si la vérification dit que des os humanoïdes manquent alors qu'ils existent, cliquez sur **Fix Humanoid Map** (corriger la carte humanoïde) : BoneCraft détecte de nouveau les emplacements humanoïdes et enregistre le mappage, sans renommer aucun os.

**Aussi ici :** **Convertir SpringBones → PhysBones** (physique des cheveux VRoid vers VRChat) et **Cartographier les Visèmes VRoid**.

---

## MMD Bridge (pont MMD)

Les outils MMD sont dans l'onglet **CATS** → **Importer / Exporter** → **MMD / PMX**. Ils ont besoin de l'add-on mmd_tools ; la section l'installe (**Installation Automatique depuis GitHub**, **Install from .zip on Disk...** (installer depuis un .zip sur le disque)).

---

### MMD Import (import MMD)

- **Import PMX / PMD...** (importer PMX / PMD) — modèles MMD
- **Import VMD Motion...** (importer un mouvement VMD) — animations MMD
- **Import VPD Pose...** (importer une pose VPD) — poses MMD

---

### MMD Export (export MMD)

**Paramètres :** le **Folder**, puis pour chaque format un nom de fichier et une portée (le modèle actif, ou chaque modèle MMD de la scène) : **PMX File** et **PMX Scope**, **VMD File** et **VMD Scope**, **VPD File** et **VPD Scope**.

**Boutons :** **Export PMX...** (exporter PMX), **Export VMD Motion...** (exporter un mouvement VMD) et **Export VPD Pose...** (exporter une pose VPD)

**Aussi ici :** **Convert Bone Names -> Unity** (convertir les noms d'os pour Unity) et **Convert Physics -> PhysBones** (convertir la physique en PhysBones).

---

## Game Export (export pour jeux)

**Ce qu'il fait :** exporte pour les moteurs de jeu avec un profil validé : Unreal (humanoïde ou universel), humanoïde Unity, humanoïde Godot, et FBX ou GLB génériques. Chaque correction dont le profil a besoin est affichée et n'est appliquée que lorsque vous cliquez dessus, jamais en silence.

**Paramètres :** le **Profile** (profil), l'**Animation** à inclure, **Root Motion** (mouvement de la racine), **Interpolation**, et la **T-Pose** utilisée pour l'export (par défaut une T-pose pour l'humanoïde Unity et VRChat).

**Boutons :**
- **Check for Export** (vérifier pour l'export) — vérifie le rig par rapport au profil et liste les constats
- **Apply Transforms (Fix)** (appliquer les transformations (correction)) — l'une des corrections explicites que la vérification peut proposer
- **Export (Profile)** (exporter (profil)) — exporte avec le profil

**Où le trouver :** onglet **CATS** → **Importer / Exporter** → **Game Export**

---

## Tableau des tâches

**Ce qu'il fait :** un résumé du rig actuel : un score de santé, des gains rapides, et une liste des tâches trouvées par BoneCraft (os humanoïdes manquants, noms non résolus, visèmes manquants, avertissements du validateur de rig, etc.), regroupées par catégorie. **Ouvrir la vérification de santé** ouvre le détail ; **Actualiser le tableau des tâches** vérifie de nouveau.

**Où le trouver :** onglet **BoneCraft** → **Vue d'ensemble** → **Tableau des tâches**

---

### Inspecteur d'Os

**Ce qu'il fait :** montre en détail l'os sélectionné (son nom, son parent, ses contraintes, ses propriétés personnalisées et ses drivers) et permet de modifier des propriétés simples sans passer en Mode Édition.

**Où le trouver :** onglet **BoneCraft** → **Révision** → **Inspecteur d'Os**

Suite : [Outils CATS](09-cats.md)
