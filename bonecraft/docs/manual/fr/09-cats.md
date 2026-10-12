# Outils CATS

[← Contenu](index.md)

Les outils CATS se trouvent dans l'onglet **CATS** de la barre latérale droite (appuyez sur**N**), dans la section**CATS** et dans l'onglet**Properties** de l'éditeur**Scene** lorsque Préférences → Onglets → Propriétés de la scène → Afficher est activé. Le commutateur de fenêtre CATS et le commutateur Propriétés de la scène contrôlent leurs propres copies indépendamment. Ils suivent le pipeline décrit dans [Le pipeline CATS](04-cats-pipeline.md). Choisissez l'armature sur laquelle ils travaillent en haut de la section.

Dans la version 9.1, plusieurs panneaux placent les paramètres facultatifs dans un pli sous leurs boutons d'action. Les entrées nécessaires avant d'exécuter un outil passent toujours en premier : les commutateurs de nettoyage du modèle de correction, la langue source de Translate Bone Names et les formes de la bouche ou des os des yeux. Les outils Bone qui proposent l'ajustement de la dernière opération s'exécutent immédiatement et vous permettent d'ajuster leurs options par la suite. Passez la souris sur un bouton ou une option pour lire son info-bulle.

---

## Corriger le modèle

**Phase du pipeline :** 1 (toujours en premier)

**Ce qu'il fait :** Un nettoyage en un clic avant toute autre opération CATS. Il supprime les problèmes cachés qui autrement se briseraient silencieusement à chaque étape ultérieure.

**Options (chacune peut être désactivée) :**
- Appliquer des modificateurs
- Supprimer les doubles : fusionner les sommets en double à la même position
- Recalculer les normales : corriger les surfaces à l'envers
- Supprimer la géométrie lâche – faces non attachées au corps
- Supprimer les groupes de sommets vides
- Supprimer les os de poids nul – les os qui ne bougent aucun sommet
- Supprimer les contraintes et les corps rigides que VRChat ne peut pas utiliser

Cliquez sur **Fix Model** pour les exécuter sur le maillage sélectionné en un seul passage.

---

## Traduire les Noms d'Os

**Ce qu'il fait :** Traduit les noms d'os de votre squelette en noms anglais VRChat. Il fonctionne hors ligne, à partir d'un dictionnaire intégré de noms d'os connus.

**Langues prises en charge :** Japonais (日本語, le plus courant, de MMD et de nombreux modèles communautaires), chinois (中文), coréen (한국어), portugais (Português), espagnol (Español) et français (Français).

**Contrôles clés :** le**Language** des noms de source et le bouton de traduction (**Translate Bone Names** ).

Il s'agit de la langue des noms d'os du modèle, et non de la langue de votre interface : pour un modèle japonais MMD, utilisez-le quelle que soit la langue dans laquelle Bforartists est défini.

---

## Joindre les Maillages

**Ce qu'il fait :** Combine les objets maillés de votre avatar en un seul maillage. VRChat fonctionne mieux avec un maillage par avatar. Lorsque les maillages ont des clés de forme différentes, CATS complète celles manquantes avec des formes neutres, de sorte que le maillage joint ait un ensemble cohérent.

**Contrôles clés :** la liste des maillages (actualisez-la avec le bouton à côté), puis**Join Meshes**.

**Quand l'utiliser :** une fois que tous les vêtements et accessoires sont attachés et lestés, et après avoir réparé le modèle. Rejoindre avant Fix Model propage les problèmes de sommets en double d'un objet à un autre ; le maillage joint conserve ensuite les sommets fantômes de chaque objet original, et les visèmes générés le déchirent au niveau des coutures.

---

## Combinateur d'atlas de matériaux

**Phase du pipeline :** 2 (facultatif)

**Ce qu'il fait :** Cuit plusieurs matériaux dans une seule feuille de texture (un atlas). Moins de matériaux donnent un meilleur classement de performance VRChat.

**Contrôles clés :**
- **Analyze** — répertorie vos matériaux et textures, avec des diagnostics, des groupes en double et des remplacements de taille. Choisissez les matériaux et les textures à inclure: décochez ceux que vous souhaitez conserver tels quels.
- **Smart Combine Materials** — le chemin recommandé: prépare l'atlas et pointe chaque maillage dessus; l'atlas UV devient UV0 pour l'export
- **Bake Atlas** — une cuisson nature ;**Add Group** et**Remove Group** cuisent des groupes de matériaux séparément
- Remplacer les paramètres hérités : taille de l'atlas, méthode UV et graine, préréglage d'emballage, remplissage de cuisson, étape de rotation de l'îlot et passes de cuisson (Albédo par défaut ; Normal, Émission et Rugosité peuvent être cuits en tant que sorties séparées)
- **Preserve Backup Duplicate** — conserve une copie des originaux
- **Accept — Delete Backup** — conserve le résultat et supprime la sauvegarde
- **Revert — Restore Originals** — revient aux matériaux d'origine
- **Copy Debug Report** — copie les diagnostics dans le presse-papiers pour un rapport de bogue

Les matériaux VRM / MToon conservent leur transparence: le mode alpha est respecté et comparé à la texture alpha réelle, l'émission ne souffle pas et les carreaux problématiques sont signalés en magenta après cuisson.

**Crédits de lignée :** ce flux de travail poursuit la lignée d'intégration CATS, crédite le plug-in original Cats Blender, crédite Grim-es/material-combiner-addon pour la lignée Material Combiner et crédite UV Toolkit d'Alexander Belyakov ainsi que le référentiel d'archives oRazeD/UVToolkit pour l'inspiration du flux de travail UV. BoneCraft implémente ses propres assistants UV d'atlas au lieu d'inclure la source UVToolkit.

---

## Visèmes

**Phase du pipeline :** 3

**Ce qu'il fait :** Crée les 15 visèmes VRChat à partir de trois formes de bouche de base.

**Contrôles clés :** **A Shape**,**O Shape** et**CH Shape** (choisissez-les, ou**Auto-Detect** ), puis**Generate Visemes**. Développez les options sous les boutons pour choisir d'écraser ou non les visèmes existants avant la génération. Voir [Guide 13, Phase 2](03-guides-b.md#phase-2--génération-des-visèmes).

---

## Suivi Oculaire

**Phase du pipeline :** 4 (exécutée après Fix Model)

Sans Fix Model au préalable, la détection oculaire peut se verrouiller sur la géométrie en double restante au lieu des yeux réels et placer les contraintes dans un espace vide – les avatars arrivent dans VRChat regardant le sol.

**Ce qu'il fait :** Recherche les os des yeux de votre avatar, les nomme comme l'exige VRChat (`LeftEye` et `RightEye` ) et crée les contraintes de rotation qui déplacent naturellement les yeux dans VRChat.

**Contrôles clés :**
- **Auto-Detect** — recherche les os qui correspondent aux noms et positions des os de l'œil
- **Left Eye** et**Right Eye** — les os des yeux, si vous les cueillez vous-même
- **Up Limit**,**Down Limit** et**Side Limit** — jusqu'où les yeux peuvent se tourner
- **Create Eye Tracking** — renomme les os et crée les contraintes

---

## Pose et Clés de Forme

**Phase du pipeline :** 5 (facultatif)

### Pose en Clé de Forme

Transforme la pose actuelle en une nouvelle clé de forme – pour des expressions personnalisées ou une forme de repos corrigée. Posez l'armature en mode Pose, revenez en mode Objet, puis cliquez sur **Pose to Shape Key** et nommez la clé de forme.

### Clé de Forme en Basis

L'inverse: insère une clé de forme dans la forme neutre du maillage. Utilisez-le pour verrouiller définitivement une pose de repos corrigée. Exécutez-le également après Fix Model.

---

## Transformations et FBT

**Phase du pipeline :** 6 (dernière)

### Appliquer Toutes les Transformations

Applique la position, la rotation et l'échelle au maillage et à l'armature ensemble, de sorte que tout se lit comme des valeurs propres. Le SDK VRChat en a besoin : une échelle non appliquée donne aux avatars une taille incorrecte dans VRChat.

### Corriger le FBT

Une correction de transformation pour les configurations de suivi complet du corps : déplace l'os racine au niveau du sol.

### Supprimer le FBT

Supprime à nouveau la correction Fix FBT.

---

## Outils d'Os

- **Create Root Bone** — ajoute un os racine (nommé par**Root Name** ) au bas de la hiérarchie
- **Merge Bones** — fusionne les os plus courts que le**Merge Threshold** dans leurs parents
- **Duplicate Bones** — duplique les os sélectionnés

---

## Outils d'Armature

**Ce qu'il fait :** Fusionne une armature dans une autre, par exemple l'armature d'une tenue dans celle du corps.

**Contrôles clés :**
- **Base / Root** — l'armature qui reste (le résultat garde son nom)
- **Incoming** — l'armature qui s'y fond ; les os du même nom se replient dans la base
- Naming Prep – fait correspondre les noms d’os des deux rigs avant de les fusionner. Cela fonctionne sur n'importe quelle rig, pas seulement les importations Mixamo: choisissez Mixamo Prefixed et cliquez sur **Normalize Merge Names**, puis choisissez Mixamo Stripped et normalisez à nouveau; les deux rigs se terminent par les mêmes noms.
- Options pour parenter automatiquement les os et joindre les maillages par la suite
- **Merge Incoming Into Base** — fusionne

Pour une fusion par étapes avec aperçus, utilisez Bone Merge (voir [Constructeur de plates-formes](06-rig-builder.md#fusion-dos) ).

---

## Outils de Maillage

- **Separate by Materials** — un maillage par matériau
- **Separate by Loose Parts** — un maillage par pièce connectée
- **Separate by Shape Keys** - divise les parties déplacées par les clés de forme

---

## Smart Automatic Weights (poids automatiques intelligents)

**Smart Automatic Weights** ouvre une boîte de dialogue : vérifiez le maillage cible et l'armature, puis choisissez Corps à recalculer à partir de l'installation existante ou Vêtements à transférer à partir d'un maillage source pondéré. La boîte de dialogue utilise des valeurs par défaut intelligentes et conserve une sauvegarde cachée.**Advanced Recalculation** développe une indication d'emplacement pour les commandes complètes dans BoneCraft → Skin → Outils de poids ; il n'ouvre pas ces contrôles ici. Voir [Outils de plate-forme](05-rig-tools.md#recalcul-automatique-des-poids-dos).

---

## État du Pipeline et Registre des Opérations

L'état du pipeline indique laquelle des six phases est terminée. Le grand livre des opérations répertorie chaque opération CATS avec son heure et son résultat (modifié, propre ou en échec); **Copy** le met dans le presse-papiers et**Clear** le vide. Voir [Le pipeline CATS](04-cats-pipeline.md).

Suivant: [Correctifs rapides et glossaire](10-reference.md)
