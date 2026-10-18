# Prise en main

[← Sommaire](index.md)

## Qu'est-ce que BoneCraft ?

BoneCraft est un add-on pour Bforartists qui vous aide à rigger des personnages et des accessoires, et à préparer des avatars 3D pour VRChat, VRoid / VRM et MMD. Il ajoute des panneaux et des boutons qui automatisent les étapes les plus fastidieuses : construire un rig, peindre les poids, corriger les noms d'os, configurer la synchronisation labiale et le suivi oculaire, et exporter.

**Ce que BoneCraft ne peut pas faire :**
- Il ne peut pas modéliser ni sculpter la forme du corps de votre avatar
- Il ne peut pas créer de textures ni de matériaux à partir de zéro
- Il ne peut pas envoyer directement sur VRChat (il vous faut toujours le VRChat Creator Companion / SDK)

---

## BoneCraft et BoneForge

BoneCraft ne fonctionne que dans Bforartists (le fork de Blender). Pour Blender standard, il existe un add-on séparé, BoneForge, avec moins d'outils. Installez l'un ou l'autre, jamais les deux. Dans Blender standard, BoneCraft ne se charge pas : il affiche un seul avis avec un bouton pour obtenir Bforartists.

BoneForge 9.0.0 et les versions suivantes ciblent Blender standard. BoneCraft est un add-on distinct pour Bforartists. Les deux proposent Auto-Rig Wizard, Quick Rig, Mannequin et les outils partagés CATS/Material Atlas. BoneCraft ajoute Mechanisms, Control Picker, les rigs de contrôle de production, la détection des articulations et les exports par profil. La disposition similaire ne les ajoute pas à BoneForge.

## Installer BoneCraft

**Ce qu'il vous faut :**
- Bforartists (BoneCraft est testé sur Bforartists 5.2)
- Le fichier `.zip` de BoneCraft

**Étapes :**

1. Ouvrez Bforartists.
2. Ouvrez **Édition** (Edit) → **Préférences** (Preferences) → **Add-ons**.
3. Cliquez sur **Installer depuis le disque…** (Install from Disk…) et choisissez le fichier `.zip` de BoneCraft.
4. Cochez la case à côté de BoneCraft pour l'activer.
5. Dépliez l'entrée de BoneCraft pour voir ses réglages : **Language** (langue), **Tabs** (onglets), **Shelf Width** (largeur), **Show Helpers** (aides) et la liste **Outils**.

**Ce que vous devriez voir :** les onglets BoneCraft et Rig Builder sur la Tool Shelf de gauche (touche **T**) et l'onglet CATS dans la barre latérale de droite (touche **N**).

## Où trouver chaque chose

Les onglets sélectionnent un groupe. Setup Rigging, Skin, Review, Avatar Tools et Facial sont des sections à déplier dans ces onglets, pas des onglets distincts. Les chemins ci-dessous conservent les labels anglais ; leur traduction dépend du réglage Language.

| Onglet | Position par défaut | Sections |
| --- | --- | --- |
| Rig Builder | Tool Shelf gauche (T) | Auto-Rig Wizard, Quick Rig - premade armatures, Mannequin |
| BoneCraft | Tool Shelf gauche (T) | Overview, Setup Rigging, Skin, Mechanisms, Review |
| CATS | Barre latérale droite (N) | CATS, Avatar Tools, VRChat Tools, Import / Export |

| Outil | Chemin à ouvrir |
| --- | --- |
| Bone Merge | BoneCraft → Setup Rigging → Bone Merge |
| Delta Mush / Proximity Wrap | BoneCraft → Skin → Delta Mush / Proximity Wrap |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library → Lip Sync |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Humanoid / Hair | CATS → Avatar Tools → Set Up Humanoid Bones / Add Hair Physics |
| VRChat export | CATS → Import / Export → Unity / VRChat |
| VRM / MMD / I/O Hub | CATS → Import / Export → VRM / VRoid, MMD / PMX, Game Engine Export |
| Performance / Clothing / Naming | CATS → VRChat Tools → Check Performance / Attach Clothing / VRChat Naming Extras |

Sélectionnez une armature pour le rig et la bibliothèque de visèmes ; un maillage en Mode Objet pour Delta Mush et Proximity Wrap. Lip Sync exige une armature en Mode Pose. Dépliez les sections avec leur triangle. Options contient les réglages facultatifs ; réglez les outils exécutés immédiatement dans Ajuster la dernière opération avant toute autre opération.

Trois fonctions faciales distinctes : la génération CATS crée les clés de forme de la bouche ; Viseme Library / Lip Sync conserve les poses et crée les clés d’animation ; Facial associe les clés existantes à VRChat ou configure le suivi du visage. Les contrôles dérivés de UVToolkit sont dans CATS → Material Atlas → Override Inherited Settings → UV Packing ; il s’agit du flux d’atlas partagé, pas de l’add-on UVToolkit complet.


**Déplacer un onglet :** **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Chaque onglet a un interrupteur et deux boutons Left/Right. Les changements sont immédiats. Quand l'onglet est masqué, ses boutons Left/Right deviennent gris mais restent utilisables.

**Éditeur Properties :** Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools et Import / Export existent aussi dans l'onglet Scene lorsque **Scene Properties** est activé dans Preferences → Tabs. Activé au départ ; **Show** masque/affiche l'ensemble, bleu signifie visible. Cela ne touche ni les onglets de vue 3D ni Armature data. Avec une armature sélectionnée, les outils d'armature BoneCraft figurent aussi dans Armature data, indépendamment de ces interrupteurs. Rig Builder, Mechanisms et les sections CATS utilisent Scene. Pour retirer un outil partout, désactivez son paquet dans **Tools**, ou l'add-on entier.

**Shelf Width :** Widen Narrow Shelves est activé au départ. Il élargit une seule fois les étagères BoneCraft sous les minima Left/Right : 240/260 pixels par défaut, à l'échelle d'interface 1×. Une largeur réduite ensuite à la main reste choisie. Désactivez pour gérer vous-même les largeurs ; les champs deviennent inactifs.

**Menus et Tool Shelf natifs :** accès depuis les menus d'en-tête de la vue 3D :

| Emplacement | Outils |
|---|---|
| Add → Armature | Quick Rig, Auto-Rig Wizard, Mannequin for Active Rig |
| Pose → BoneCraft (Pose Mode) | Poses, sélecteur, collections, configuration et vérifications |
| Weights → BoneCraft (Weight Paint) | Remplissage, miroir et normalisation |
| Object → Mechanisms (Object Mode) | Pièces, articulations, liaisons, test |
| Tool Shelf → Pose ou Weights → BoneCraft | Opérations courantes de pose ou de poids |

Les boutons Pose/Weights affichent du texte dans une étagère large, une grille d'icônes si elle est étroite. Survolez pour lire l'infobulle. Ce sont les mêmes outils ; leur disponibilité dépend des paquets activés.

**Outils de vue 3D :** Place Rig Markers place le prochain marqueur de l'assistant en cliquant sur le maillage ; Build Mechanism démarre une articulation ou liaison en cliquant une pièce. Voir [Rig Builder](06-rig-builder.md#assistant-auto-rig) et [Mechanisms](07-mechanisms.md) pour leurs réglages.

**Exécuter puis ajuster :** Quick Rig, Fit Dropped Rig, Weight Mirror, Weight Transfer, Flood to Custom, Ribbon, Spline IK et Delta Mush s'exécutent au clic. Réglez immédiatement dans Adjust Last Operation, avant toute autre opération. Les autres panneaux placent leurs réglages facultatifs dans un volet sous les actions. Un panneau peut rester visible et indiquer la sélection requise.

**Show Helpers :** masque les explications « quoi/quand » et « How this works » si décoché dans les préférences. **Compact Mode** dans Avatar Tools commande le même réglage.

**Language :** change les panneaux BoneCraft en English, 日本語, 한국어, 中文, Français, Português ou Español.

**Fix Model d'abord, toujours :** commencez tout travail CATS par **Fix Model**. Le registre suit les étapes et chaque outil avertit d'un ordre incorrect. Voir [Pipeline CATS](04-cats-pipeline.md).

**Panneau rapide :** **Ctrl+Shift+R** ouvre le panneau du rig sous le curseur dans la vue 3D.

---

## Par où commencer ?

Choisissez la description qui vous correspond le mieux :

> **« Vous avez un tout nouveau fichier de modèle 3D (FBX, OBJ ou fichier Blender) et voulez le rigger pour VRChat à partir de zéro. »**
> → Allez au [guide 1 : amener votre premier avatar dans VRChat](02-guides-a.md#guide-1--amener-votre-premier-avatar-dans-vrchat)

> **« Vous avez créé votre avatar dans VRoid Studio et exporté un fichier VRM. »**
> → Allez au [guide 2 : amener un avatar VRoid dans VRChat](02-guides-a.md#guide-2--amener-un-avatar-vroid-dans-vrchat)

> **« Vous avez un modèle MMD (fichier PMX) et voulez l'utiliser dans VRChat. »**
> → Allez au [guide 3 : amener un avatar MMD dans VRChat](02-guides-a.md#guide-3--amener-un-avatar-mmd-dans-vrchat)

> **« Vous avez déjà un avatar riggé, mais il refuse de s'envoyer parce que les os ont de mauvais noms. »**
> → Allez au [guide 4 : corriger les noms d'os de votre avatar](02-guides-a.md#guide-4--corriger-les-noms-dos-de-votre-avatar)

> **« Vous avez un avatar riggé et voulez le rendre entièrement prêt pour VRChat : synchronisation labiale, suivi oculaire, maillage propre, tout en une fois. »**
> → Allez au [guide 13 : préparer votre avatar pour VRChat avec CATS](03-guides-b.md#guide-13--préparer-votre-avatar-pour-vrchat-avec-cats)

> **« Vous voulez régler un problème précis. »**
> → Allez à l'[Index des solutions rapides](10-reference.md#index-des-solutions-rapides)

Suite : [Guides 1–7](02-guides-a.md)
