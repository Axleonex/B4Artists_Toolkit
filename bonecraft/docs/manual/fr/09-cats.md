# Outils CATS

[← Sommaire](index.md)

Les outils CATS sont dans l'onglet **CATS** de la barre latérale de droite (touche **N**), dans la section **CATS**, et toujours dans l'onglet **Scène** de l'éditeur **Propriétés**. Ils suivent le pipeline décrit dans [Le pipeline CATS](04-cats-pipeline.md). Choisissez en haut de la section l'armature sur laquelle ils travaillent.

---

## Corriger le modèle

**Phase du pipeline :** 1 (toujours en premier)

**Ce qu'il fait :** un nettoyage en un clic avant toute autre opération CATS. Il retire des problèmes cachés qui, sinon, casseraient sans bruit chaque étape suivante.

**Options (chacune peut être désactivée) :**
- Appliquer les modificateurs
- Supprimer les doublons — fusionner les sommets en double à la même position
- Recalculer les normales — corriger les surfaces retournées
- Supprimer la géométrie isolée — les faces non rattachées au corps
- Supprimer les groupes de sommets vides
- Supprimer les os de poids zéro — les os qui ne déplacent aucun sommet
- Supprimer les contraintes et les corps rigides que VRChat ne peut pas utiliser

Cliquez sur **Corriger le modèle** pour les lancer sur le maillage sélectionné en un seul passage.

---

## Traduire les Noms d'Os

**Ce qu'il fait :** traduit les noms d'os de votre squelette en noms VRChat anglais. Il fonctionne hors ligne, à partir d'un dictionnaire intégré de noms d'os connus.

**Langues prises en charge :** japonais (日本語, la plus courante, venant de MMD et de nombreux modèles de la communauté), chinois (中文), coréen (한국어), portugais (Português), espagnol (Español) et français.

**Contrôles principaux :** la **Langue** des noms source, et le bouton de traduction (**Traduire les Noms d'Os**).

Il s'agit de la langue des noms d'os du modèle, pas de la langue de votre interface : pour un modèle MMD japonais, utilisez-le quelle que soit la langue réglée dans Bforartists.

---

## Joindre les Maillages

**Ce qu'il fait :** combine les objets maillage de votre avatar en un seul maillage. VRChat fonctionne au mieux avec un maillage par avatar. Quand les maillages ont des clés de forme différentes, CATS complète celles qui manquent avec des formes neutres, pour que le maillage joint ait un seul ensemble cohérent.

**Contrôles principaux :** la liste des maillages (actualisez-la avec le bouton à côté), puis **Joindre les Maillages**.

**Quand l'utiliser :** une fois tous les vêtements et accessoires attachés et pondérés, et après Corriger le modèle. Joindre avant Corriger le modèle propage les problèmes de sommets en double d'un objet à l'autre ; le maillage joint garde alors des sommets fantômes de chaque objet d'origine, et les visèmes générés le déchirent aux jointures.

---

## Combinateur d'atlas de matériaux

**Phase du pipeline :** 2 (facultatif)

**Ce qu'il fait :** cuit plusieurs matériaux dans une seule planche de texture (un atlas). Moins de matériaux donnent un meilleur rang de performance VRChat.

**Contrôles principaux :**
- **Analyze** (analyser) — liste vos matériaux et textures, avec diagnostics, groupes de doublons et tailles forcées. Choisissez quels matériaux et quelles textures inclure : décochez ceux que vous voulez garder tels quels.
- **Smart Combine Materials** (combinaison intelligente des matériaux) — la voie recommandée : cuit l'atlas et fait pointer chaque maillage vers lui ; l'UV de l'atlas devient l'UV0 pour l'export
- **Cuire l'atlas** — une cuisson simple ; **Add Group** (ajouter un groupe) et **Remove Group** (retirer un groupe) cuisent séparément des groupes de matériaux
- Remplacer les Paramètres Hérités — taille de l'atlas, méthode et graine des UV, préréglage d'empaquetage, marge de cuisson, pas de rotation des îlots, et passes de cuisson (Albedo par défaut ; Normal, Emission et Roughness peuvent être cuites en sorties séparées)
- **Preserve Backup Duplicate** (conserver un double de sauvegarde) — garde une copie des originaux
- **Accepter — Supprimer la sauvegarde** — garde le résultat et supprime la sauvegarde
- **Revenir — Restaurer les Originaux** — revient aux matériaux d'origine
- **Copy Debug Report** (copier le rapport de débogage) — copie les diagnostics dans le presse-papiers pour un rapport de bogue

Les matériaux VRM / MToon gardent leur transparence : le mode alpha est respecté et vérifié par rapport à l'alpha réel de la texture, l'émission ne sature pas, et les tuiles à problème sont signalées en magenta après la cuisson.

**Filiation et crédits :** ce flux de travail prolonge la filiation de l'intégration CATS, crédite le Cats Blender Plugin d'origine, crédite Grim-es/material-combiner-addon pour la filiation Material Combiner, et crédite UV Toolkit d'Alexander Belyakov ainsi que le dépôt d'archive oRazeD/UVToolkit pour l'inspiration du flux de travail UV. BoneCraft implémente ses propres aides UV d'atlas au lieu d'inclure le code source d'UVToolkit.

---

## Visèmes

**Phase du pipeline :** 3

**Ce qu'il fait :** crée les 15 visèmes VRChat à partir de trois formes de bouche de base.

**Contrôles principaux :** **Forme A**, **Forme O** et **Forme CH** (choisissez-les, ou **Détection Automatique**), une option pour écraser les visèmes existants, et **Générer les Visèmes**. Voir le [guide 13, phase 2](03-guides-b.md#phase-2--génération-des-visèmes).

---

## Suivi Oculaire

**Phase du pipeline :** 4 (à lancer après Corriger le modèle)

Sans Corriger le modèle d'abord, la détection des yeux peut s'accrocher à de la géométrie en double restante au lieu des vrais yeux, et placer les contraintes dans le vide : les avatars arrivent dans VRChat en fixant le sol.

**Ce qu'il fait :** trouve les os des yeux de votre avatar, les nomme comme VRChat l'exige (`LeftEye` et `RightEye`), et crée les contraintes de rotation qui font bouger les yeux naturellement dans VRChat.

**Contrôles principaux :**
- **Détection Automatique** — trouve les os qui correspondent aux noms et aux positions des os des yeux
- **Œil Gauche** et **Œil Droit** — les os des yeux, si vous les choisissez vous-même
- **Limite Supérieure**, **Limite Inférieure** et **Limite Latérale** — jusqu'où les yeux peuvent tourner
- **Créer le Suivi Oculaire** — renomme les os et crée les contraintes

---

## Pose et Clés de Forme

**Phase du pipeline :** 5 (facultatif)

### Pose en Clé de Forme

Transforme la pose actuelle en une nouvelle clé de forme, pour des expressions personnalisées ou une forme de repos corrigée. Posez l'armature en Mode Pose, revenez en Mode Objet, puis cliquez sur **Pose en Clé de Forme** et nommez la clé de forme.

### Clé de Forme en Basis

L'inverse : cuit une clé de forme dans la forme de repos neutre du maillage. Utilisez-le pour fixer pour de bon une pose de repos corrigée. Lancez-le aussi après Corriger le modèle.

---

## Transformations et FBT

**Phase du pipeline :** 6 (en dernier)

### Appliquer Toutes les Transformations

Applique la position, la rotation et l'échelle au maillage et à l'armature ensemble, pour que tout se lise avec des valeurs propres. Le SDK VRChat en a besoin : une échelle non appliquée donne aux avatars une mauvaise taille dans VRChat.

### Corriger le FBT

Une correction de transformation pour les configurations Full Body Tracking : déplace l'os racine au niveau du sol.

### Supprimer le FBT

Retire de nouveau la correction de Corriger le FBT.

---

## Outils d'Os

- **Créer l'Os Racine** — ajoute un os racine (nommé par **Nom de la Racine**) en bas de la hiérarchie
- **Fusionner les Os** — fusionne dans leurs parents les os plus courts que le **Seuil de Fusion**
- **Dupliquer les Os** — duplique les os sélectionnés

---

## Outils d'Armature

**Ce qu'il fait :** fusionne une armature dans une autre, par exemple l'armature d'une tenue dans celle du corps.

**Contrôles principaux :**
- **Base / Root** (base / racine) — l'armature qui reste (le résultat garde son nom)
- **Incoming** (entrante) — l'armature qui fusionne dedans ; les os de même nom se replient dans la base
- Naming Prep (préparation du nommage) — fait correspondre les noms d'os des deux rigs avant la fusion. Il fonctionne sur n'importe quel rig, pas seulement les imports Mixamo : choisissez Mixamo Prefixed et cliquez sur **Normalize Merge Names** (normaliser les noms de fusion), puis choisissez Mixamo Stripped et normalisez de nouveau ; les deux rigs finissent avec les mêmes noms.
- Des options pour parenter les os automatiquement et pour joindre les maillages ensuite
- **Merge Incoming Into Base** (fusionner l'entrante dans la base) — fusionne

Pour une fusion par étapes avec aperçus, utilisez Fusion d'Os (voir [Constructeur de Rig](06-rig-builder.md#fusion-dos)).

---

## Outils de Maillage

- **Séparer par Matériaux** — un maillage par matériau
- **Séparer par Parties Détachées** — un maillage par morceau connexe
- **Séparer par Clés de Forme** — détache les parties que les clés de forme déplacent

---

## Smart Automatic Weights (poids automatiques intelligents)

Recalcule les poids du maillage à partir du rig existant : **Smart Automatic Weights**, avec **Advanced Recalculation** (recalcul avancé) pour tous ses réglages. Le même outil est dans l'onglet BoneCraft (Peau → Outils de Poids), décrit dans [Outils de rig](05-rig-tools.md#recalcul-automatique-des-poids-dos).

---

## État du Pipeline et Registre des Opérations

L'État du Pipeline montre lesquelles des six phases sont faites. Le Registre des Opérations liste chaque opération CATS avec son heure et son résultat (Changed, Clean ou Failed) ; **Copier** le met dans le presse-papiers et **Effacer** le vide. Voir [Le pipeline CATS](04-cats-pipeline.md).

Suite : [Solutions rapides et glossaire](10-reference.md)
