# Prise en main

[← Contenu](index.md)

## Qu'est-ce que BoneCraft?

BoneCraft est un module complémentaire pour Bforartists qui vous aide à configurer des personnages et des accessoires, et à préparer des avatars 3D pour VRChat, VRoid / VRM et MMD. Il ajoute des panneaux et des boutons qui automatisent les étapes les plus fastidieuses : construire une rig, peindre des poids, corriger les noms des os, configurer la synchronisation labiale et le suivi oculaire, et exporter.

**Ce que BoneCraft ne peut pas faire :**
- Il ne peut pas modéliser ou sculpter la forme du corps de votre avatar
- Il ne peut pas créer de textures ou de matériaux à partir de zéro
- Il ne peut pas être téléchargé directement sur VRChat (vous avez toujours besoin du VRChat Creator Companion/SDK)

---

## BoneCraft et BoneForge

BoneCraft fonctionne uniquement dans Bforartists (la fourche Blender ). Pour le Blender standard, il existe un module complémentaire distinct, BoneForge, avec un ensemble d'outils plus petit. Installez l'un ou l'autre, jamais les deux. Dans la norme Blender, BoneCraft ne se charge pas : il affiche une notification avec un bouton pour obtenir Bforartists.

|Zone|BoneForge (norme Blender )|BoneCraft (Bforartists )|
| --- | --- | --- |
|Nettoyage d'avatar CATS, Material Combiner, contrôles dérivés d'UVToolkit|Inclus|Inclus|
|Aides d'avatar de base (style Mixamo)|Inclus|Inclus|
|Rig Builder : détection conjointe, assistant, rig de contrôle, atout humanoïde de base|Non inclus|Inclus|
|Contrôles de l'animateur et sélecteur de contrôle|Non inclus|Inclus|
|Mécanismes pour étais et machines|Non inclus|Inclus|
|Reciblage avancé et exportation de jeux basée sur le profil|Non inclus|Inclus|

## Installer BoneCraft

**Ce dont vous avez besoin :**
- Bforartists (BoneCraft est testé sur Bforartists 5.2)
- Le fichier BoneCraft `.zip`

**Étapes :**

1. Ouvrez Bforartists.
2. Ouvrez **Edit** →**Preferences** →**Add-ons**.
3. Cliquez sur **Install from Disk…** et sélectionnez le fichier BoneCraft `.zip`.
4. Cochez la case à côté de BoneCraft pour l'activer.
5. Développez l'entrée de BoneCraft pour voir ses paramètres : **Language**,**Tabs**,**Shelf Width**,**Show Helpers** et la liste**Tools**.

**Vous devriez voir :** les onglets BoneCraft et Rig Builder sur l'étagère à outils de gauche (appuyez sur**T**) et l'onglet CATS sur la barre latérale droite (appuyez sur**N**).

## Où trouver chaque chose

BoneCraft ajoute trois onglets à la fenêtre 3D :

|Onglet|Côté par défaut|Sections|
| --- | --- | --- |
|BoneCraft |Étagère à outils gauche (appuyez sur T)|Vue d'ensemble, configuration du gréement, peau, mécanismes, révision|
|Constructeur de rigs|Étagère à outils gauche (appuyez sur T)|Rig Builder : Assistant de montage automatique, Montage rapide, Mannequin|
|CATS |Barre latérale droite (appuyez sur N)|CATS, Outils Avatar, Outils VRChat, Importation/Exportation|

**Déplacer un onglet :** ouvrez**Edit** →**Preferences** →**Add-ons** → BoneCraft →**Tabs**. Chaque onglet comporte un commutateur d'affichage et deux boutons, Gauche et Droite. Un changement s’applique immédiatement. Lorsqu'un onglet est masqué, ses boutons Gauche et Droite deviennent gris, mais ils fonctionnent toujours.

**Éditeur de propriétés :** Rig Builder, Mécanismes, CATS, Outils Avatar, Outils VRChat et Importation/Exportation sont également affichés dans l'onglet Scène de l'éditeur de propriétés tandis que**Scene Properties** est activé dans Préférences → Onglets. Cet interrupteur démarre. Cliquez sur son bouton**Show** pour masquer ou afficher toutes ces sections ; le bleu signifie qu'ils sont affichés. Cela ne modifie pas les onglets de la fenêtre ni l'onglet Données d'armature. Lorsqu'une armature est sélectionnée, les outils d'armature de BoneCraft apparaissent également dans l'onglet Données d'armature, indépendamment de ces commutateurs de visibilité. Les sections Rig Builder, Mécanismes et CATS utilisent à la place l'onglet Scène. Pour supprimer un outil partout, désactivez son package dans la liste**Tools** ou désactivez le module complémentaire.

**Largeur des étagères :** L'élargissement des étagères étroites commence. Il élargit une fois les étagères contenant les onglets BoneCraft s'ils sont en dessous du minimum gauche ou droit : 240 et 260 pixels par défaut, à l'échelle 1 × de l'interface utilisateur. Une étagère que vous rétrécissez ensuite reste à la largeur que vous avez choisie. Éteignez l'interrupteur pour gérer vous-même les largeurs ; ses champs de largeur deviennent inactifs.

**Menus et onglets de l'étagère à outils intégrée :** dans la version 9.1, vous pouvez également accéder aux outils à partir des menus d'en-tête de la vue 3D :

|Emplacement|Outils|
| --- | --- |
|Ajouter → Armature|Quick Rig, Assistant Auto-Rig, Mannequin pour Active Rig|
|Pose → BoneCraft (Mode Pose)|Outils de pose, sélecteur, collectes d'os, configuration et vérifications du rig|
|Poids → BoneCraft (mode Peinture de poids)|Remplir, refléter et normaliser les poids|
|Objet → Mécanismes (Mode Objet)|Ajoutez des pièces, des joints et des liens ; tester le mouvement|
|Étagère à outils → Pose ou poids → BoneCraft |Boutons pour les opérations courantes de pose ou de poids|

Les boutons de l'étagère Pose et Poids affichent du texte lorsque l'étagère est large et deviennent une grille d'icônes lorsqu'elle est étroite. Passez la souris sur une icône pour lire son info-bulle. Ces points d'accès utilisent les mêmes outils que les propres onglets du BoneCraft  ; leur disponibilité suit les packages d'outils activés.

**Outils de fenêtre :** Placer les marqueurs de rig place le prochain marqueur de l'assistant de rig automatique lorsque vous cliquez sur le maillage ; Le mécanisme de construction démarre une liaison ou un lien guidé lorsque vous cliquez sur une pièce. Voir [Constructeur de plates-formes](06-rig-builder.md#assistant-auto-rig) et [Mécanismes](07-mechanisms.md#articulations-et-liens-un-exemple-de-chaque) pour leur configuration et leurs commandes.

**Exécutez d'abord, ajustez ensuite :** des outils tels que Quick Rig, Fit Dropped Rig, Weight Mirror, Weight Transfer, Flood to Custom, Ribbon, Spline IK et Delta Mush s'exécutent lorsque vous cliquez dessus. Immédiatement après, utilisez le panneau Ajuster la dernière opération dans la fenêtre pour modifier leurs options. Ajustez avant d’exécuter une autre opération. D'autres panneaux placent les paramètres facultatifs dans un pli sous les boutons d'action ; développez-le lorsque vous avez besoin de ces paramètres. Un panneau qui nécessite une sélection différente peut rester visible et expliquer quoi sélectionner.

**Afficher les aides :** BoneCraft explique ses sections avec de courtes lignes « quoi/quand » et des notes « Comment cela fonctionne ». Décochez**Show Helpers** dans les préférences du module complémentaire pour les masquer. Dans la section Outils Avatar,**Compact Mode** est un raccourci pour le même commutateur.

**Langue :** le paramètre**Language** dans les préférences du module complémentaire modifie les propres panneaux de BoneCraft en anglais, 日本語, 한국어, 中文, Français, Português ou Español.

**Corrigez d'abord le modèle, à chaque fois :** dans l'onglet CATS, commencez toujours par**Fix Model** avant tout autre outil CATS. Le pipeline CATS utilise un grand livre pour suivre les étapes que vous avez effectuées, et chaque outil vous avertit si vous l'exécutez dans le désordre. Voir [Le pipeline CATS](04-cats-pipeline.md).

**Panneau rapide :** appuyez sur**Ctrl+Maj+R** dans la vue 3D pour ouvrir le panneau de configuration de BoneCraft sous la forme d'une fenêtre contextuelle sous le curseur.

---

## Par où commencer?

Choisissez la description qui vous convient le mieux:

> **"Vous êtes une personne qui possède un tout nouveau fichier de modèle 3D (fichier FBX, OBJ ou Blender ) et souhaite le configurer pour VRChat à partir de zéro."**
> → Aller à [Guide 1 : Obtenez votre premier avatar dans VRChat](02-guides-a.md#guide-1-amener-votre-premier-avatar-dans-vrchat)

> **"Vous êtes une personne qui a créé votre avatar dans VRoid Studio et exporté un fichier VRM."**
> → Aller à [Guider 2 : Introduire un avatar VRoid dans VRChat](02-guides-a.md#guide-2-amener-un-avatar-vroid-dans-vrchat)

> **"Vous êtes une personne qui possède un modèle MMD (fichier PMX ) et souhaite l'utiliser dans VRChat."**
> → Aller à [Guider 3 : Introduire un avatar MMD dans VRChat](02-guides-a.md#guide-3-amener-un-avatar-mmd-dans-vrchat)

> **"Vous êtes une personne qui possède déjà un avatar truqué, mais il ne sera pas téléchargé car les os portent des noms erronés."**
> → Aller à [Guider 4 : Corrigez les noms d'os de votre avatar](02-guides-a.md#guide-4-corriger-les-noms-dos-de-votre-avatar)

> ** "Vous êtes une personne qui a un avatar truqué et souhaitez le rendre entièrement prêt pour VRChat  : synchronisation labiale, suivi oculaire, maillage propre, tout à la fois."**
> → Aller à [Guider 13 : Préparez votre avatar VRChat avec CATS](03-guides-b.md#guide-13-préparer-votre-avatar-pour-vrchat-avec-cats)

> **"Vous êtes une personne qui souhaite résoudre un problème spécifique."**
> → Accédez au [Index des solutions rapides](10-reference.md#index-des-solutions-rapides)

Suivant: [Guides 1 à 7](02-guides-a.md)
