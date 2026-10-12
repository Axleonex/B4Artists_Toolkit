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

| Domaine | BoneForge (Blender standard) | BoneCraft (Bforartists) |
| --- | --- | --- |
| Nettoyage d'avatar CATS, Material Combiner, contrôles dérivés d'UVToolkit | Inclus | Inclus |
| Aides de base pour avatars (style Mixamo) | Inclus | Inclus |
| Constructeur de Rig : détection des articulations, assistant, rig de contrôle, asset Basic Humanoid | Non inclus | Inclus |
| Contrôles d'animateur et Control Picker | Non inclus | Inclus |
| Mechanisms pour accessoires et machines | Non inclus | Inclus |
| Reciblage avancé et export pour jeux par profil | Non inclus | Inclus |

## Installer BoneCraft

**Ce qu'il vous faut :**
- Bforartists (BoneCraft est testé sur Bforartists 5.2)
- Le fichier `.zip` de BoneCraft

**Étapes :**

1. Ouvrez Bforartists.
2. Ouvrez **Édition** (Edit) → **Préférences** (Preferences) → **Add-ons**.
3. Cliquez sur **Installer depuis le disque…** (Install from Disk…) et choisissez le fichier `.zip` de BoneCraft.
4. Cochez la case à côté de BoneCraft pour l'activer.
5. Dépliez l'entrée de BoneCraft pour voir ses réglages : **Tabs** (onglets), **Show Helpers** (afficher les aides), **Language** (langue) et la liste **Outils**.

**Ce que vous devriez voir :** les onglets BoneCraft et Rig Builder sur la Tool Shelf de gauche (touche **T**) et l'onglet CATS dans la barre latérale de droite (touche **N**).

## Où trouver chaque chose

BoneCraft ajoute trois onglets à la vue 3D :

| Onglet | Côté par défaut | Sections |
| --- | --- | --- |
| BoneCraft | Tool Shelf de gauche (touche T) | Vue d'ensemble, Configurer le Rigging, Peau, Mechanisms, Révision |
| Rig Builder | Tool Shelf de gauche (touche T) | Constructeur de Rig : Quick Rig, Assistant Auto-Rig, Mannequin |
| CATS | Barre latérale de droite (touche N) | CATS, VRChat, Importer / Exporter |

**Déplacer un onglet :** ouvrez **Édition** → **Préférences** → **Add-ons** → BoneCraft → **Tabs**. Chaque onglet a un interrupteur d'affichage et deux boutons, Left (gauche) et Right (droite). Un changement s'applique tout de suite. Quand un onglet est masqué, ses boutons Left et Right deviennent gris, mais ils fonctionnent toujours.

**Toujours dans l'éditeur Propriétés :** le Constructeur de Rig, Mechanisms, CATS, VRChat et Importer / Exporter sont aussi affichés dans l'onglet Scène de l'éditeur Propriétés, quelle que soit la sélection. Avec une armature sélectionnée, les sections de BoneCraft sont aussi affichées dans l'onglet Données de l'armature. Les interrupteurs d'affichage ne masquent jamais ces copies. Pour retirer un outil partout, désactivez son paquet dans la liste **Outils**, ou désactivez l'add-on.

**Show Helpers (afficher les aides) :** BoneCraft explique ses sections avec de courtes lignes « quoi / quand » et des notes « How this works » (comment ça marche). Décochez **Show Helpers** dans les préférences de l'add-on pour les masquer. Dans la section VRChat, **Mode Compact** est un raccourci vers le même interrupteur.

**Langue :** le réglage **Language** (langue) dans les préférences de l'add-on change les panneaux propres à BoneCraft en English, 日本語, 한국어, 中文, Français, Português ou Español.

**Corriger le modèle d'abord, à chaque fois :** dans l'onglet CATS, commencez toujours par **Corriger le modèle** avant tout autre outil CATS. Le pipeline CATS tient un registre des étapes que vous avez faites, et chaque outil vous avertit si vous le lancez dans le désordre. Voir [Le pipeline CATS](04-cats-pipeline.md).

**Panneau rapide :** appuyez sur **Ctrl+Shift+R** dans la vue 3D pour ouvrir le panneau de rig de BoneCraft en fenêtre contextuelle sous le curseur.

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
