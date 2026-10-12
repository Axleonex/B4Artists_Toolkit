# Guides 1–7

[← Sommaire](index.md)

## Guide 1 : amener votre premier avatar dans VRChat

> **Durée :** environ 45 à 60 minutes pour un premier passage complet
> **Résultat :** un avatar riggé, prêt pour VRChat, exporté pour le SDK VRChat

**Avant de commencer, vérifiez ces points :**
- [ ] Votre modèle 3D est importé dans Bforartists (Fichier > Importer, choisissez votre format)
- [ ] Le modèle est en T-pose (bras tendus sur les côtés, corps droit), ou presque
- [ ] Le modèle n'a pas de géométrie visiblement cassée (pas de triangles flottant au hasard)
- [ ] Vous voyez votre modèle dans la vue 3D comme une forme grise pleine

---

### Étape 1 — Ouvrir le Constructeur de Rig

Ouvrez l'onglet **Rig Builder** sur la Tool Shelf de gauche (touche **T** dans la vue 3D). Le même Constructeur de Rig se trouve aussi toujours dans l'onglet **Scène** de l'éditeur **Propriétés**. Il a trois parties : Quick Rig (armatures toutes prêtes), l'**Assistant Auto-Rig** et **Mannequin**.

Dépliez **Assistant Auto-Rig** et cliquez sur **Démarrer l'auto-rig**.

---

### Étape 2 — Sélectionner votre maillage

L'assistant liste les maillages de la scène. Cliquez sur le maillage de votre avatar dans cette liste, puis sur **Suivant**.

**Ce que vous devriez voir :** une ligne « Selected: » avec le nom de votre maillage, puis l'étape du type de rig.

---

### Étape 3 — Choisir le type de rig

Cliquez sur **Body + Face** (corps et visage) pour un avatar dont vous voulez animer le visage (clignements, expressions, synchronisation labiale), ou sur **Body Only** (corps seul) pour un corps sans contrôles faciaux. Dans les options de génération, **Cinématique** règle IK/FK, IK seul ou FK seul. Cliquez sur **Suivant**.

---

### Étape 4 — Placer les marqueurs du corps

C'est l'étape la plus importante. Les marqueurs sont des points qui indiquent à BoneCraft où se trouve chaque articulation principale : le bassin, la colonne, le cou et la tête, les épaules, les bras, les mains, les jambes et les pieds. BoneCraft en déduit les os.

**La méthode rapide :** dans le cadre Smart Detection (détection intelligente), cliquez sur **Detect Markers** (détecter les marqueurs). BoneCraft suit les membres dans votre maillage et place chaque marqueur, chacun avec un indice de confiance. Cliquez sur **Accept High** (accepter la confiance élevée) pour garder les marqueurs sûrs, et sur **Reset Low** (réinitialiser la faible confiance) pour effacer les douteux et les placer vous-même. **Deviner les marqueurs depuis le maillage** est une estimation plus simple d'après les proportions du maillage.

**À la main :** chaque marqueur a une ligne de boutons à icône.
1. Cliquez sur **Place Marker** (placer le marqueur ; l'icône de flèche) sur la ligne du marqueur, puis cliquez au bon endroit sur votre avatar.
2. Cliquez sur **Confirm Marker** (confirmer le marqueur ; la coche) quand il est bien placé. **Reset Marker** (réinitialiser le marqueur ; la flèche circulaire) efface un marqueur placé pour que vous le placiez de nouveau.

**Symétrie :** **Toggle Symmetry** (basculer la symétrie ; la première icône sur la ligne d'un marqueur gauche ou droit) place le marqueur de l'autre côté chaque fois que vous placez celui-ci. **Mirror L to R** (refléter de gauche à droite) et **Mirror R to L** (refléter de droite à gauche) copient chaque marqueur confirmé de l'autre côté.

Quand tous les marqueurs sont placés, cliquez sur **Confirmer tous placés**, puis sur **Suivant**.

---

### Étape 5 — Placer les marqueurs des doigts

Sous Détail des Doigts, choisissez combien de doigts construire : « 5 — Full Human Hand » pour une main standard, ou moins (jusqu'à « 0 — No Fingers »). Cliquez sur **Deviner les marqueurs de doigts**. BoneCraft trouve chaque doigt d'après la forme de la main et le suit de la jointure jusqu'au bout. Ajustez les marqueurs décalés, puis cliquez sur **Suivant**.

---

### Étape 6 — Placer les marqueurs du visage (Body + Face uniquement)

Cliquez sur **Deviner les marqueurs faciaux**, puis ajustez au besoin les yeux, les paupières, les sourcils, les coins de la bouche et la mâchoire. Les marqueurs des yeux restent là où vous les placez. Cliquez sur **Suivant**.

---

### Étape 7 — Vérifier et générer

L'étape de vérification liste les avertissements éventuels et les options de génération. Cliquez sur **Générer le rig**.

**Ce que vous devriez voir :** un squelette (os orange) à l'intérieur de votre avatar, avec des membres IK/FK, les os des doigts et, pour un rig Body + Face, un rig facial, et la peau de l'avatar attachée à ce squelette, de sorte qu'elle se déforme quand les os bougent. La dernière étape propose **Construire le rig de contrôle** pour les options de vérification que Générer le rig n'applique pas, et **Fermer l'assistant** ; [Constructeur de Rig](06-rig-builder.md) décrit les deux.

> **Poids de peau** = des nombres qui décident quels os déplacent quelles parties du maillage de votre avatar. BoneCraft les règle automatiquement ; vous pouvez les affiner avec les outils de poids (voir [Outils de rig](05-rig-tools.md)).

---

### Étape 8 — Mapper vers les os humanoïdes de VRChat

Ouvrez l'onglet **CATS** dans la barre latérale de droite (touche **N**), dépliez **VRChat** puis **Configurer les Os Humanoïdes**. Cliquez sur **Tout mapper automatiquement** : BoneCraft relie vos os aux emplacements du corps que VRChat utilise pour faire bouger un avatar avec vous. Cliquez sur **Normalize Names** (normaliser les noms) pour donner aux os mappés les noms attendus par VRChat, puis sur **Valider**.

**Ce que vous devriez voir :** les emplacements obligatoires (Hips, Spine, Head, LeftUpperArm, etc.) affichent chacun un os. Le guide 5 explique les emplacements.

---

### Étape 9 — Exporter pour VRChat

Dans l'onglet **CATS**, dépliez **VRChat** → **Exporter vers VRChat**. Réglez le **Folder** (dossier) et le nom de l'**Avatar**, puis cliquez sur **Exporter vers VRChat (Unity)**.

**Ce que vous devriez voir :** l'avatar exporté dans le dossier choisi, prêt pour le VRChat Creator Companion et le SDK VRChat dans Unity.

---

**Ce que cela débloque :** vous avez maintenant un avatar VRChat riggé. À partir de là, vous pouvez ajouter la physique des cheveux (guide 6), attacher des vêtements (guide 7), configurer la synchronisation labiale (guide 8) et vérifier les performances (guide 9). Pour un nettoyage et une configuration VRChat tout-en-un avec les outils CATS, voir le [guide 13](03-guides-b.md#guide-13--préparer-votre-avatar-pour-vrchat-avec-cats).

---

## Guide 2 : amener un avatar VRoid dans VRChat

> **Durée :** environ 15 à 25 minutes
> **Résultat :** votre avatar VRoid prêt à être exporté pour VRChat

**Avant de commencer, vérifiez ces points :**
- [ ] Vous avez exporté votre avatar depuis VRoid Studio en fichier `.vrm`, ou l'avez téléchargé depuis VRoid Hub en `.zip`
- [ ] BoneCraft est installé et activé

---

### Étape 1 — Installer l'add-on VRM

BoneCraft utilise l'add-on VRM pour lire les fichiers `.vrm`. Dans l'onglet **CATS**, dépliez **Importer / Exporter** → **VRM / VRoid**. S'il indique que l'add-on n'est pas installé, cliquez sur **Installation Automatique depuis GitHub**. Sans connexion Internet, téléchargez l'add-on vous-même et utilisez **Installer depuis .zip sur Disque…** ; **Ouvrir la Page des Extensions** ouvre sa page de téléchargement.

---

### Étape 2 — Importer votre avatar

Dans la même section **VRM / VRoid**, cliquez sur **Importer VRM…** et choisissez votre fichier `.vrm`. Pour un téléchargement VRoid, cliquez sur **Import VRoid (.vroid / .zip)…** (importer VRoid) et choisissez le `.zip`.

Si vous choisissez un fichier de projet VRoid Studio (`.vroid`), BoneCraft affiche à la place une carte « VRoid Studio Project » : un projet n'est pas encore un avatar. Exportez-le en VRM dans VRoid Studio, puis importez ce fichier.

**Ce que vous devriez voir :** votre personnage VRoid dans la vue, avec son squelette en place.

---

### Étape 3 — Mapper vers les os humanoïdes de VRChat

Dans l'onglet **CATS** → **VRChat** → **Configurer les Os Humanoïdes**, cliquez sur **Tout mapper automatiquement**. Les squelettes VRoid suivent une disposition standard, donc cela remplit généralement tous les emplacements. Si un emplacement est faux, **Fix Humanoid Map** (corriger la carte humanoïde) dans la section **VRM / VRoid** (sous Lint) répare les confusions de noms VRoid habituelles.

---

### Étape 4 — Corriger les noms d'os

Cliquez sur **Normalize Names** dans **Configurer les Os Humanoïdes**. VRoid a ses propres noms d'os ; cette étape donne aux os mappés les noms attendus par VRChat.

---

### Étape 5 — Configurer les visèmes (synchronisation labiale)

Les avatars VRoid ont déjà les formes de bouche pour la synchronisation labiale. Dans la section **VRM / VRoid**, cliquez sur **Cartographier les Visèmes VRoid**. BoneCraft associe les clés de forme de VRoid aux formes de synchronisation labiale de VRChat.

---

### Étape 6 — Physique des cheveux (facultatif)

Les cheveux VRoid utilisent des SpringBones. **Convertir SpringBones → PhysBones** dans la section **VRM / VRoid** les transforme en PhysBones VRChat. Le guide 6 traite la physique des cheveux plus en détail.

---

### Étape 7 — Exporter

Exportez comme au guide 1, étape 9.

**Ce que cela débloque :** votre avatar VRoid est prêt pour le VRChat Creator Companion. Vous pouvez aussi vérifier les performances (guide 9) avant l'envoi.

---

## Guide 3 : amener un avatar MMD dans VRChat

> **Durée :** environ 20 à 30 minutes
> **Résultat :** votre modèle MMD `.pmx` prêt pour VRChat

**Avant de commencer, vérifiez ces points :**
- [ ] Vous avez un fichier de modèle MMD `.pmx` ou `.pmd`
- [ ] BoneCraft est installé

---

### Étape 1 — Installer mmd_tools

BoneCraft utilise l'add-on mmd_tools pour lire les fichiers MMD. Dans l'onglet **CATS**, dépliez **Importer / Exporter** → **MMD / PMX**. S'il indique que mmd_tools n'est pas installé, cliquez sur **Installation Automatique depuis GitHub** (ou sur **Install from .zip on Disk...** (installer depuis un .zip sur le disque) avec une copie téléchargée).

---

### Étape 2 — Importer votre fichier PMX

Dans la section **MMD / PMX**, cliquez sur **Import PMX / PMD...** (importer PMX / PMD) et choisissez votre modèle.

**Ce que vous devriez voir :** votre personnage MMD dans la vue, avec des noms d'os japonais.

---

### Étape 3 — Corriger les noms d'os

VRChat ne sait pas lire les noms d'os japonais de MMD. Dans la section **MMD / PMX**, cliquez sur **Convert Bone Names -> Unity** (convertir les noms d'os pour Unity). Pour des noms dans une autre langue, utilisez l'onglet **CATS** → **CATS** → **Traduire les Noms d'Os** : choisissez la **Langue** et lancez-le.

---

### Étape 4 — Nettoyer le modèle

Les modèles MMD ont souvent de la géométrie en trop et de nombreuses pièces séparées. Dans l'onglet **CATS** → **CATS**, lancez d'abord **Corriger le modèle**, puis **Joindre les Maillages** pour combiner les parties du corps en un seul maillage (recommandé pour VRChat). Le [guide 13](03-guides-b.md#guide-13--préparer-votre-avatar-pour-vrchat-avec-cats) parcourt tout le pipeline CATS dans l'ordre.

---

### Étape 5 — Mapper vers les os humanoïdes de VRChat

Dans l'onglet **CATS** → **VRChat** → **Configurer les Os Humanoïdes**, cliquez sur **Tout mapper automatiquement**. Les squelettes MMD sont proches de ceux de VRChat, donc la plupart des emplacements se remplissent automatiquement. Pour un emplacement vide, cliquez sur son bouton et choisissez l'os.

---

### Étape 6 — Physique et export

**Convert Physics -> PhysBones** (convertir la physique en PhysBones) dans la section **MMD / PMX** transforme la physique à corps rigides des cheveux et des jupes MMD en PhysBones VRChat. Puis exportez comme au guide 1, étape 9.

**Ce que cela débloque :** votre avatar MMD est prêt pour VRChat. Vous pouvez ajouter la physique des cheveux (guide 6) et configurer la synchronisation labiale (guide 8) avant l'envoi.

---

## Guide 4 : corriger les noms d'os de votre avatar

> **Durée :** environ 5 à 15 minutes
> **Résultat :** les os dont VRChat a besoin renommés avec des noms compatibles VRChat

**Avant de commencer, vérifiez ces points :**
- [ ] Votre avatar est ouvert et son squelette (armature) est visible

---

### Étape 1 — Détecter le style de nommage actuel

Dans l'onglet **CATS**, dépliez **VRChat** → **VRChat Naming Extras** (extras de nommage VRChat) et cliquez sur **Détecter**. BoneCraft affiche le style de nommage trouvé (par exemple Mixamo, VRoid ou Unity) et un score ; **Forcer une nouvelle analyse** vérifie à nouveau après un changement de noms.

Pour des noms d'os en japonais, chinois, coréen, portugais, espagnol ou français, utilisez plutôt l'onglet **CATS** → **CATS** → **Traduire les Noms d'Os** : choisissez la **Langue** et lancez-le. Il convertit les noms en anglais en une seule étape.

---

### Étape 2 — Renommer avec les noms VRChat

Mappez d'abord les os (guide 5, étape 2), puis cliquez sur **Normalize Names** dans **Configurer les Os Humanoïdes** : chaque os mappé reçoit le nom attendu par VRChat.

**Ce que vous devriez voir :** des noms d'os comme `Hips`, `Spine`, `Chest` et `LeftUpperArm`.

---

### Étape 3 — Corrections manuelles (si nécessaire)

**VRChat Naming Extras** propose aussi des outils par lot pour les os restants :

- **Rechercher et remplacer** — remplace un morceau de texte par un autre dans chaque nom d'os
- **Ajouter un préfixe** et **Ajouter un suffixe** — ajoutent du texte au début ou à la fin de chaque nom d'os
- **Supprimer le préfixe** et **Supprimer le suffixe** — le retirent
- **Remplacement par Regex** — la même chose, avec une expression régulière

**Ce que cela débloque :** des noms d'os corrects permettent au mappage humanoïde (guide 5) de fonctionner automatiquement. Sans eux, VRChat ne peut pas savoir comment votre personnage doit bouger.

---

## Guide 5 : mapper votre avatar sur le système corporel de VRChat

> **Durée :** environ 10 à 15 minutes
> **Résultat :** le squelette de votre avatar relié au système de mouvement humanoïde de VRChat

**Avant de commencer, vérifiez ces points :**
- [ ] Les os de votre avatar ont des noms cohérents (sinon, voir le guide 4)
- [ ] Le squelette est sélectionné
- [ ] Vous êtes en **Mode Objet** (vérifiez le menu déroulant en haut à gauche de la vue)

---

### Étape 1 — Ouvrir Configurer les Os Humanoïdes

Dans l'onglet **CATS**, dépliez **VRChat** → **Configurer les Os Humanoïdes**.

---

### Étape 2 — Mappage automatique

Cliquez sur **Tout mapper automatiquement**. BoneCraft analyse votre squelette et remplit les emplacements du corps.

> Un emplacement humanoïde est comme un crochet étiqueté qu'utilise VRChat : « les hanches vont ici, la tête va ici, la main gauche va ici ». BoneCraft associe vos os à ces crochets. Le mappage humanoïde est désormais relu correctement quand vous rouvrez un fichier.

**Ce que vous devriez voir :** les emplacements obligatoires (15 : Hips, Spine, Head, les deux bras, avant-bras, mains, cuisses, jambes et pieds) et les facultatifs (Chest, UpperChest, Neck et d'autres), chacun avec un os, ainsi que la part des emplacements obligatoires remplis.

---

### Étape 3 — Vérifier le mappage

Cliquez sur **Valider**. BoneCraft vérifie que chaque emplacement obligatoire a un os et que la hiérarchie est cohérente.

---

### Étape 4 — Remplir les emplacements vides à la main

Un emplacement sans os affiche « (click to map) » (cliquer pour mapper). Cliquez dessus et choisissez le bon os. Puis cliquez de nouveau sur **Valider**, et sur **Normalize Names** pour que les os mappés reçoivent les noms de VRChat.

---

### Étape 5 — Configurer le suivi oculaire (facultatif)

Si votre avatar a des os d'yeux, utilisez l'onglet **CATS** → **CATS** → **Suivi Oculaire** : cliquez sur **Détection Automatique** pour trouver les os des yeux (ou choisissez les os **Œil Gauche** et **Œil Droit**), réglez les limites et cliquez sur **Créer le Suivi Oculaire**. Le [guide 13, phase 3](03-guides-b.md#phase-3--suivi-oculaire) explique les réglages.

**Ce que cela débloque :** une fois le mappage humanoïde fait, votre avatar bouge correctement dans VRChat : l'IK (cinématique inverse, le système qui fait suivre vos vraies manettes par vos mains en jeu) fonctionne, et votre avatar suit vos mouvements réels.

---

## Guide 6 : ajouter la physique des cheveux

> **Durée :** environ 15 à 25 minutes
> **Résultat :** les cheveux de votre avatar (et d'autres parties souples) qui se balancent naturellement dans VRChat

**Avant de commencer, vérifiez ces points :**
- [ ] Votre avatar est ouvert et le squelette sélectionné
- [ ] Configurer les Os Humanoïdes est fait (guide 5)

> PhysBone = le composant de VRChat qui fait rebondir et balancer les os comme s'ils avaient du poids. BoneCraft les configure sur des chaînes d'os : cheveux, oreilles, queues, jupes et accessoires.

---

### Étape 1 — Ouvrir Ajouter la Physique des Cheveux

Dans l'onglet **CATS**, dépliez **VRChat** → **Ajouter la Physique des Cheveux**. Il a quatre parties : Hair Chain Detection (détection des chaînes de cheveux), Hair Chain Generation (génération des chaînes de cheveux), PhysBone Configuration (configuration des PhysBones) et Hair Physics Colliders (colliders de physique des cheveux).

---

### Étape 2 — Trouver les chaînes de cheveux

Si vos cheveux ont déjà des os, cliquez sur **Detect Hair Physics Chains** (détecter les chaînes de physique des cheveux). BoneCraft trouve les chaînes d'os qui ressemblent à des cheveux (des os reliés bout à bout depuis une racine) et liste chacune avec son os racine et sa longueur.

Si vos cheveux n'ont pas encore d'os, sélectionnez les maillages des cheveux et utilisez Hair Chain Generation : choisissez la **Densité** (Low, Medium ou High : combien de chaînes), puis cliquez sur **Générer**. **Remplacer** les reconstruit avec une nouvelle densité.

---

### Étape 3 — Choisir un préréglage PhysBone

Sélectionnez un os d'une chaîne. Sous PhysBone Configuration, cliquez sur le préréglage adapté : **Cheveux**, **Jupe** (jupes et capes) ou **Queue** (queues et cordes).

**Ce que vous devriez voir :** les paramètres de la chaîne : Pull, Spring, Stiffness, Gravity et Max Angle.

---

### Étape 4 — Réglage fin (facultatif)

Le panneau affiche les valeurs de la chaîne ; il ne les modifie pas. Plus de Stiffness la fait moins plier, plus de Gravity la tire vers le bas, un Max Angle plus petit limite son amplitude. Pour d'autres valeurs, cliquez sur un autre préréglage, ou modifiez le composant PhysBone dans Unity après avoir importé l'avatar.

---

### Étape 5 — Ajouter des colliders (recommandé)

Les colliders sont des formes invisibles qui empêchent les cheveux de traverser la tête et le corps. Sous Hair Physics Colliders, cliquez sur **Place Default Colliders** (placer les colliders par défaut) pour ajouter des colliders standard sur la tête, les épaules et la poitrine. **Add Collider** (ajouter un collider) et **Remove Collider** (retirer un collider) en ajoutent ou en retirent un à la fois.

**Ce que cela débloque :** les cheveux de votre avatar bougent maintenant naturellement dans VRChat quand vous tournez la tête, sautez ou dansez. Les mêmes étapes fonctionnent pour les queues, les oreilles, les jupes et les accessoires pendants.

---

## Guide 7 : attacher des vêtements qui bougent avec votre corps

> **Durée :** environ 20 à 30 minutes
> **Résultat :** un vêtement attaché au squelette de votre avatar, qui bouge avec votre corps

**Avant de commencer, vérifiez ces points :**
- [ ] Votre avatar de base a un squelette terminé, et son corps est peint en poids
- [ ] Le vêtement est dans le même fichier (avec sa propre armature s'il en avait une)
- [ ] Le vêtement épouse à peu près le corps de votre avatar

---

### Étape 1 — Ouvrir Attacher les Vêtements

Dans l'onglet **CATS**, dépliez **VRChat** → **Attacher les Vêtements**. Il a trois parties : Bone Matching (correspondance des os), Collision Detection (détection des collisions) et Clothing Merge (fusion des vêtements).

---

### Étape 2 — Faire correspondre les os

Si le vêtement est venu avec sa propre armature, sélectionnez-la et cliquez sur **Faire correspondre les os**. BoneCraft associe chaque os du vêtement à l'os équivalent de votre avatar (le bras gauche du vêtement avec le bras gauche de l'avatar, et ainsi de suite).

**Ce que vous devriez voir :** une liste de paires d'os : os du vêtement → os de l'avatar. Pour un vêtement sans armature, sautez cette étape.

---

### Étape 3 — Fusionner le vêtement

Sélectionnez le vêtement (son armature et ses maillages, ou seulement ses maillages s'il n'a pas d'armature), puis cliquez en dernier sur l'armature de votre avatar avec Maj, pour qu'elle soit l'objet actif. Cliquez sur **Fusionner les vêtements**. Avec une armature de vêtement, BoneCraft déplace le vêtement sur votre squelette et fusionne les os ; sans armature, il transfère les poids de votre corps aux maillages du vêtement.

> Poids (peinture de poids) = des nombres qui indiquent à chaque point d'un maillage de combien chaque os le déplace. Si votre manche gauche a du poids sur l'os du bras gauche, bouger cet os entraîne la manche avec lui.

**Ce que vous devriez voir :** le vêtement sous le squelette de votre avatar. Bouger un os déplace à la fois le corps et le vêtement.

---

### Étape 4 — Vérifier les traversées

Cliquez sur **Détecter les collisions** pour trouver les endroits où le vêtement traverse le corps. Corrigez-les en ajustant les poids à ces endroits (voir les outils de poids dans [Outils de rig](05-rig-tools.md)).

**Ce que cela débloque :** des vêtements qui bougent naturellement avec votre corps. Répétez pour chaque pièce de la tenue.

Suite : [Guides 8–13](03-guides-b.md)
