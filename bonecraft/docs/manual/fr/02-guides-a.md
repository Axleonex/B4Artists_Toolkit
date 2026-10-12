# Guides 1–7

[← Contenu](index.md)

## Guide 1: amener votre premier avatar dans VRChat

Pour un maillage d'entraînement avant d'utiliser votre propre avatar, suivez le [atelier mannequin illustré](06-rig-builder.md#atelier-mannequin-illustré): Simple Human, un mannequin sans rigless, Auto-Rig, puis IK/FK.

> **Durée :** Environ 45 à 60 minutes pour une première exécution complète
> **Résultat :** Un avatar truqué, prêt pour VRChat, exporté pour le SDK VRChat

**Avant de commencer, vérifiez ceci :**
- [] Votre modèle 3D est importé dans Bforartists (Fichier > Importer, choisissez votre format)
- [] Le modèle est dans une pose en T (bras tendus sur les côtés, corps droit) – ou à proximité
- [] Le modèle n'a pas de géométrie brisée évidente (pas de triangles flottants aléatoires)
- [] Vous pouvez voir votre modèle dans la fenêtre 3D sous la forme d'une forme grise unie

---

### Étape 1 — Ouvrir le Constructeur de Rig

Ouvrez l'onglet **Rig Builder** sur l'étagère à outils de gauche (appuyez sur**T** dans la fenêtre 3D). Le même Rig Builder se trouve dans l'onglet**Properties** de l'éditeur**Scene** tandis que Préférences → Onglets → Propriétés de la scène → Afficher est activé. Il se compose de trois parties : le**Auto-Rig Wizard**, le Quick Rig (armatures prêtes à l'emploi) et le**Mannequin**.

Développez **Auto-Rig Wizard** et cliquez sur**Start Auto-Rig**.

Vous pouvez également démarrer l'assistant à partir du menu Ajouter → Armature → Assistant de rig automatique de la fenêtre 3D, puis continuer dans Rig Builder.

---

### Étape 2 — Sélectionner votre maillage

L'assistant répertorie les maillages de la scène. Cliquez sur le maillage de votre avatar dans cette liste, puis cliquez sur **Next**.

**Ce que vous devriez voir :** Une ligne "Selected :" avec le nom de votre maillage, puis l'étape de type de rig.

---

### Étape 3 — Choisir le type de rig

Cliquez sur **Body + Face** pour un avatar dont vous souhaitez animer le visage (clignements des yeux, expressions, synchronisation labiale), ou sur**Body Only** pour un corps sans commandes faciales. Sous Options de génération,**Kinematics** définit IK/FK, IK uniquement ou FK uniquement. Cliquez sur**Next**.

---

### Étape 4 — Placer les marqueurs du corps

C'est l'étape la plus importante. Les marqueurs sont des points qui indiquent BoneCraft où se trouve chaque articulation majeure : le bassin, la colonne vertébrale, le cou et la tête, les épaules, les bras, les mains, les jambes et les pieds. BoneCraft en extrait les os.

**La méthode rapide :** dans la zone Détection intelligente, cliquez sur**Detect Markers**. BoneCraft trace les membres de votre maillage et place chaque marqueur, chacun en toute confiance. Cliquez sur**Accept High** pour conserver les sûrs, et sur**Reset Low** pour effacer les douteux afin de pouvoir les placer vous-même.**Guess Markers from Mesh** est une estimation plus simple à partir des proportions du maillage.

**Avec l'outil fenêtre :** pour placer plusieurs marqueurs, activez Placer des marqueurs de rig dans la barre d'outils de la fenêtre en mode Objet. L'en-tête de l'outil nomme le marqueur suivant et comporte des verrous d'axe et un commutateur de miroir. Cliquez sur le maillage pour placer et confirmer ce marqueur ; l'outil passe au marqueur suivant non confirmé. Une fois l'étape terminée, cliquez sur**Next** dans l'assistant.

**Un marqueur à la fois :** chaque marqueur possède une rangée de boutons d'icônes. Passez la souris sur un bouton pour lire son info-bulle.

1. Cliquez sur **Place Marker** (l'icône en forme de flèche) sur la ligne du marqueur, puis cliquez au bon endroit sur votre avatar.
2. Cliquez sur **Confirm Marker** (la coche) lorsqu'elle est correctement positionnée.**Reset Marker** (la flèche circulaire) efface un marqueur placé afin que vous puissiez le placer à nouveau.

**Symétrie :** **Toggle Symmetry** (la première icône sur la rangée d'un marqueur gauche ou droit) place le marqueur de l'autre côté chaque fois que vous placez celui-ci.**Mirror L to R** et**Mirror R to L** copient chaque marqueur confirmé de l'autre côté.

Lorsque chaque marqueur est placé, cliquez sur **Confirm All Placed**, puis sur**Next**.

---

### Étape 5 — Placer les marqueurs des doigts

Sous Détails des doigts, choisissez le nombre de doigts à construire: « 5 — Main humaine complète » pour une main standard, ou moins (jusqu'à « 0 — Aucun doigt »). Cliquez sur **Guess Finger Markers**. BoneCraft trouve chaque doigt à partir de la forme de la main et le trace de la jointure au bout du doigt. Ajustez tout marqueur désactivé, puis cliquez sur**Next**.

---

### Étape 6 — Placer les marqueurs du visage (Body + Face uniquement)

Cliquez sur **Guess Face Markers**, puis ajustez les yeux, les paupières, les sourcils, les coins de la bouche et la mâchoire selon vos besoins. Les marqueurs oculaires restent là où vous les placez. Cliquez sur**Next**.

---

### Étape 7 — Vérifier et générer

L'étape de révision répertorie tous les avertissements et les options de génération. Cliquez sur **Generate Rig**.

**Ce que vous devriez voir :** Un squelette (os oranges) à l'intérieur de votre avatar, avec des membres IK/FK, des os de doigts et, pour un rig Corps + Visage, un rig visage et la peau de votre avatar qui y est attachée pour qu'elle se déforme lorsque les os bougent. La dernière étape propose**Build Control Rig** pour les options de révision Générer l'installation ne s'applique pas, et**Close Wizard**  ; [Constructeur de plates-formes](06-rig-builder.md) décrit les deux.

> **Poids de peau** = nombres qui décident quels os déplacent quelles parties du maillage de votre avatar. BoneCraft les définit automatiquement ; vous pouvez les affiner avec les outils de poids (voir [Outils de plate-forme](05-rig-tools.md) ).

---

### Étape 8 — Mapper vers les os humanoïdes de VRChat

Ouvrez l'onglet **CATS** dans la barre latérale droite (appuyez sur**N**), développez**Avatar Tools**, puis**Set Up Humanoid Bones**. Cliquez sur**Auto-Map All**  : BoneCraft connecte vos os aux emplacements du corps que VRChat utilise pour déplacer un avatar avec vous. Cliquez sur**Normalize Names** pour attribuer aux os mappés les noms attendus par VRChat, puis**Validate**.

**Ce que vous devriez voir :** Les emplacements requis (hanches, colonne vertébrale, tête, bras gauche, etc.) affichent chacun un os. Le guide 5 explique les emplacements.

---

### Étape 9 — Exporter pour VRChat

Dans l'onglet **CATS**, développez**Avatar Tools** →**Export to VRChat**. Définissez le nom**Folder** et**Avatar**, puis cliquez sur**Export to VRChat (Unity)**.

**Ce que vous devriez voir :** L'avatar exporté dans le dossier de votre choix, prêt pour le VRChat Creator Companion et le SDK VRChat dans Unity.

---

**Ce que cela débloque :** Vous disposez désormais d'un avatar VRChat truqué. À partir de là, vous pouvez ajouter la physique des cheveux (Guide 6), attacher des vêtements (Guide 7), configurer la synchronisation labiale (Guide 8) et vérifier les performances (Guide 9). Pour un nettoyage unique et une configuration de VRChat avec les outils CATS, voir [Guide 13](03-guides-b.md#guide-13-préparer-votre-avatar-pour-vrchat-avec-cats).

---

## Guide 2: amener un avatar VRoid dans VRChat

> **Durée :** Environ 15 à 25 minutes
> **Résultat :** Votre avatar VRoid prêt pour l'export VRChat

**Avant de commencer, vérifiez ceci :**
- [] Vous avez exporté votre avatar depuis VRoid Studio en tant que fichier `.vrm`, ou vous l'avez téléchargé depuis le hub VRoid en tant que fichier `.zip`.
- [] BoneCraft est installé et activé

---

### Étape 1 — Installer l'add-on VRM

BoneCraft utilise le module complémentaire VRM pour lire les fichiers `.vrm`. Dans l'onglet **CATS**, développez**Import / Export** →**VRM / VRoid**. S'il indique que le module complémentaire n'est pas installé, cliquez sur**Auto-Install Latest from GitHub**. Sans connexion Internet, téléchargez vous-même le module complémentaire et utilisez**Install from.zip on Disk…**  ;**Open Extensions Page** ouvre sa page de téléchargement.

---

### Étape 2 — Importer votre avatar

Dans la même section **VRM / VRoid**, cliquez sur**Import VRM…** et choisissez votre fichier `.vrm`. Pour un téléchargement VRoid, cliquez sur**Import VRoid (.vroid /.zip)…** et choisissez le `.zip`.

Si vous choisissez un fichier de projet VRoid Studio (`.vroid` ), BoneCraft affiche à la place une carte "VRoid Studio Project" : un projet n'est pas encore un avatar. Exportez-le vers VRM dans VRoid Studio, puis importez ce fichier.

**Ce que vous devriez voir :** Votre personnage VRoid dans la fenêtre avec son squelette en place.

---

### Étape 3 — Mapper vers les os humanoïdes de VRChat

Dans l'onglet **CATS** →**Avatar Tools** →**Set Up Humanoid Bones**, cliquez sur**Auto-Map All**. Les squelettes VRoid suivent une disposition standard, donc cela remplit généralement chaque emplacement. Si un emplacement est incorrect,**Fix Humanoid Map** dans la section**VRM / VRoid** (sous Lint) répare les confusions habituelles de nom VRoid.

---

### Étape 4 — Corriger les noms d'os

Cliquez sur **Normalize Names** dans**Set Up Humanoid Bones**. VRoid a ses propres noms d'os ; cela donne aux os mappés les noms attendus par VRChat.

---

### Étape 5 — Configurer les visèmes (synchronisation labiale)

Les avatars VRoid ont déjà la forme de la bouche pour la synchronisation labiale. Dans la section **VRM / VRoid**, cliquez sur**Map VRoid Visemes**. BoneCraft fait correspondre les clés de forme de VRoid aux formes de synchronisation labiale de VRChat.

---

### Étape 6 — Physique des cheveux (facultatif)

Les cheveux VRoid utilisent SpringBones. **Convert SpringBones → PhysBones** dans la section**VRM / VRoid** les transforme en VRChat PhysBones. Le guide 6 couvre la physique des cheveux plus en détail.

---

### Étape 7 — Exporter

Exportez comme dans le Guide 1, étape 9.

**Ce que cela débloque :** Votre avatar VRoid est prêt pour le compagnon créateur VRChat. Vous pouvez également vérifier les performances (Guide 9) avant de télécharger.

---

## Guide 3: amener un avatar MMD dans VRChat

> **Durée :** Environ 20 à 30 minutes
> **Résultat :** Votre modèle MMD `.pmx` prêt pour VRChat

**Avant de commencer, vérifiez ceci :**
- [] Vous disposez d'un fichier de modèle `.pmx` ou `.pmd` MMD
- [] BoneCraft est installé

---

### Étape 1 — Installer mmd_tools

BoneCraft utilise le module complémentaire mmd_tools pour lire les fichiers MMD. Dans l'onglet **CATS**, développez**Import / Export** →**MMD / PMX**. S'il indique que mmd_tools n'est pas installé, cliquez sur**Auto-Install Latest from GitHub** (ou**Install from.zip on Disk...** avec une copie téléchargée).

---

### Étape 2 — Importer votre fichier PMX

Dans la section **MMD / PMX**, cliquez sur**Import PMX / PMD...** et choisissez votre modèle.

**Ce que vous devriez voir :** Votre personnage MMD dans la fenêtre avec les noms d'os japonais.

---

### Étape 3 — Corriger les noms d'os

VRChat ne peut pas lire les noms d'os japonais de MMD. Dans la section **MMD / PMX**, cliquez sur**Convert Bone Names -> Unity**. Pour les noms dans une autre langue, utilisez l'onglet**CATS** →**CATS** →**Translate Bone Names**: choisissez le**Language** et exécutez-le.

---

### Étape 4 — Nettoyer le modèle

Les modèles MMD ont souvent une géométrie supplémentaire et de nombreuses pièces séparées. Dans l'onglet **CATS** →**CATS**, exécutez d'abord**Fix Model**, puis**Join Meshes** pour combiner les parties du corps en un seul maillage (recommandé pour VRChat ). [Guide 13](03-guides-b.md#guide-13-préparer-votre-avatar-pour-vrchat-avec-cats) parcourt l'ensemble du pipeline CATS dans l'ordre.

---

### Étape 5 — Mapper vers les os humanoïdes de VRChat

Dans l'onglet **CATS** →**Avatar Tools** →**Set Up Humanoid Bones**, cliquez sur**Auto-Map All**. Les squelettes MMD sont proches de ceux de VRChat, donc la plupart des emplacements se remplissent automatiquement. Pour un emplacement vide, cliquez sur son bouton et choisissez l'os.

---

### Étape 6 — Physique et export

**Convert Physics -> PhysBones** dans la section**MMD / PMX** transforme la physique des cheveux et des jupes du corps rigide de MMD en VRChat PhysBones. Exportez ensuite comme dans le Guide 1, étape 9.

**Ce que cela débloque :** Votre avatar MMD est prêt pour VRChat. Vous pouvez ajouter la physique des cheveux (Guide 6) et configurer la synchronisation labiale (Guide 8) avant de télécharger.

---

## Guide 4: corriger les noms d'os de votre avatar

> **Durée :** Environ 5 à 15 minutes
> **Résultat :** Les os VRChat doivent être renommés en noms compatibles VRChat

**Avant de commencer, vérifiez ceci :**
- [] Votre avatar est ouvert avec son squelette (armature) visible

---

### Étape 1 — Détecter le style de nommage actuel

Dans l'onglet **CATS**, développez**VRChat Tools**, recherchez son groupe Dénomination et cliquez sur**Detect**. BoneCraft affiche le style de dénomination trouvé (par exemple Mixamo, VRoid ou Unity ) et une partition ;**Force Rescan** vérifie à nouveau après avoir modifié les noms.

Pour les noms d'os en japonais, chinois, coréen, portugais, espagnol ou français, utilisez plutôt l'onglet **CATS** →**CATS** →**Translate Bone Names**  : choisissez le**Language** et exécutez-le. Il convertit les noms en anglais en une seule étape.

---

### Étape 2 — Renommer avec les noms VRChat

Mappez d'abord les os (Guide 5, étape 2), puis cliquez sur **Normalize Names** dans**Set Up Humanoid Bones**  : chaque os mappé reçoit le nom attendu par VRChat.

**Ce que vous devriez voir :** Noms d'os tels que `Hips`, `Spine`, `Chest` et `LeftUpperArm`.

---

### Étape 3 — Corrections manuelles (si nécessaire)

Le groupe Nommage dans **VRChat Tools** dispose également d'outils par lots pour les os restants :

- **Find and Replace** — remplacez un morceau de texte par un autre dans chaque nom d'os
- **Add Prefix** et**Add Suffix**: ajoutez du texte au début ou à la fin de chaque nom d'os
- **Remove Prefix** et**Remove Suffix** — supprimez-le à nouveau
- **Regex Replace** — le même, avec une expression régulière

**Ce que cela débloque :** Les noms d'os corrects permettent à la cartographie humanoïde (Guide 5) de fonctionner automatiquement. Sans eux, VRChat ne peut pas dire comment votre personnage doit se déplacer.

---

## Guide 5: mapper votre avatar sur le système corporel de VRChat

> **Durée :** Environ 10 à 15 minutes
> **Résultat :** Le squelette de votre avatar connecté au système de mouvement humanoïde de VRChat

**Avant de commencer, vérifiez ceci :**
- [] Les os de votre avatar sont nommés judicieusement (voir Guide 4 sinon)
- [] Le squelette est sélectionné
- [] Vous êtes dans **Object Mode** (vérifiez la liste déroulante en haut à gauche de la fenêtre)

---

### Étape 1 — Ouvrir Configurer les Os Humanoïdes

Dans l'onglet **CATS**, développez**Avatar Tools** →**Set Up Humanoid Bones**.

---

### Étape 2 — Mappage automatique

Cliquez sur **Auto-Map All**. BoneCraft scanne votre squelette et remplit les emplacements du corps.

> Une fente humanoïde est comme un crochet étiqueté que VRChat utilise: « Les hanches vont ici, la tête va ici, la main gauche va ici. » BoneCraft adapte vos os à ces crochets. Le mappage humanoïde est désormais relu correctement lorsque vous rouvrez un fichier.

**Ce que vous devriez voir :** Les emplacements requis (15 : hanches, colonne vertébrale, tête, haut des bras, avant-bras, mains, haut des jambes, bas des jambes et pieds) et les emplacements facultatifs (poitrine, haut de la poitrine, cou et autres), chacun avec un os, et la part des emplacements requis qui sont remplis.

---

### Étape 3 — Vérifier le mappage

Cliquez sur **Validate**. BoneCraft vérifie que chaque emplacement requis possède un os et que la hiérarchie a du sens.

---

### Étape 4 — Remplir les emplacements vides à la main

Un emplacement sans os affiche "(cliquez pour cartographier)". Cliquez dessus et choisissez le bon os. Cliquez ensuite à nouveau sur **Validate**, puis sur**Normalize Names** pour que les os mappés reçoivent les noms de VRChat.

---

### Étape 5 — Configurer le suivi oculaire (facultatif)

Si votre avatar a des os des yeux, utilisez l'onglet **CATS** →**CATS** →**Eye Tracking**  : cliquez sur**Auto-Detect** pour trouver les os des yeux (ou choisissez les os**Left Eye** et**Right Eye** ), définissez les limites et cliquez sur**Create Eye Tracking**. [Guide 13, Phase 3](03-guides-b.md#phase-3--suivi-oculaire) explique les paramètres.

**Ce que cela débloque :** Une fois la cartographie humanoïde effectuée, votre avatar se déplace correctement dans VRChat  : IK (cinématique inverse, le système qui fait que vos mains dans le jeu suivent vos vrais contrôleurs) fonctionne et votre avatar suit vos mouvements du monde réel.

---

## Guide 6: ajouter la physique des cheveux

> **Durée :** Environ 15 à 25 minutes
> **Résultat :** Les cheveux (et autres parties molles) de votre avatar se balancent naturellement dans VRChat

**Avant de commencer, vérifiez ceci :**
- [] Votre avatar est ouvert avec le squelette sélectionné
- [] La configuration des os humanoïdes est terminée (Guide 5)

> PhysBone = Composant de VRChat qui fait rebondir et balancer les os comme s'ils avaient du poids. BoneCraft les installe sur des chaînes d'os: cheveux, oreilles, queues, jupes et accessoires.

---

### Étape 1 — Ouvrir Ajouter la Physique des Cheveux

Dans l'onglet **CATS**, développez**Avatar Tools** →**Add Hair Physics**. Il comprend quatre parties : détection de la chaîne capillaire, génération de la chaîne capillaire, configuration PhysBone et collisionneurs de physique capillaire.

---

### Étape 2 — Trouver les chaînes de cheveux

Si vos cheveux ont déjà des os, cliquez sur **Detect Hair Physics Chains**. BoneCraft recherche les chaînes d'os qui ressemblent à des cheveux (os liés bout à bout à partir d'une racine) et répertorie chacune d'entre elles avec son os racinaire et sa longueur.

Si vos cheveux n'ont pas encore d'os, sélectionnez les mailles capillaires et utilisez Hair Chain Generation: choisissez le **Density** (Faible, Moyen ou Élevé: combien de chaînes), puis cliquez sur**Generate**.**Replace** les reconstruit avec une nouvelle densité.

---

### Étape 3 — Choisir un préréglage PhysBone

Sélectionnez un os d'une chaîne. Sous Configuration PhysBone, cliquez sur le préréglage qui correspond : **Hair**,**Skirt** (jupes et capes) ou**Tail** (queues et cordes).

**Ce que vous devriez voir :** Les paramètres de la chaîne : traction, ressort, rigidité, gravité et angle maximum.

---

### Étape 4 — Réglage fin (facultatif)

Le panneau affiche les valeurs de la chaîne ; il ne les modifie pas. Plus de rigidité fait qu'une chaîne se plie moins, plus de gravité la tire vers le bas et un angle maximum plus petit limite la distance dans laquelle elle oscille. Pour des valeurs différentes, cliquez sur un autre préréglage ou modifiez le composant PhysBone dans Unity après avoir importé l'avatar.

---

### Étape 5 — Ajouter des colliders (recommandé)

Les collisionneurs sont des formes invisibles qui empêchent les cheveux de traverser la tête et le corps. Sous Hair Physics Colliders, cliquez sur **Place Default Colliders** pour ajouter des collisionneurs standard sur la tête, les épaules et la poitrine.**Add Collider** et**Remove Collider** ajoutent ou suppriment un à la fois.

**Ce que cela débloque :** Les cheveux de votre avatar bougent désormais naturellement dans VRChat lorsque vous tournez la tête, sautez ou dansez. Les mêmes étapes fonctionnent pour les queues, les oreilles, les jupes et les accessoires pendants.

---

## Guide 7: attacher des vêtements qui bougent avec votre corps

> **Durée :** Environ 20 à 30 minutes
> **Résultat :** Un vêtement attaché au squelette de votre avatar, bougeant avec votre corps

**Avant de commencer, vérifiez ceci :**
- [] Votre avatar de base a un squelette fini et son corps est peint en poids
- [] Le vêtement est dans le même dossier (avec sa propre armature s'il en est fourni)
- [] Les vêtements s'adaptent à peu près au corps de votre avatar

---

### Étape 1 — Ouvrir Attacher les Vêtements

Dans l'onglet **CATS**, développez**VRChat Tools** et recherchez son groupe Vêtements. Il comporte trois parties : la correspondance des os, la détection des collisions et la fusion des vêtements.

---

### Étape 2 — Faire correspondre les os

Si le vêtement est livré avec sa propre armature, sélectionnez-le et cliquez sur **Match Bones**. BoneCraft associe chaque os de vêtement à l'os équivalent de votre avatar (le bras gauche du vêtement avec le bras gauche de votre avatar, et ainsi de suite).

**Ce que vous devriez voir :** Une liste de paires d'os : os du vêtement → os de l'avatar. Pour les vêtements sans armature, sautez cette étape.

---

### Étape 3 — Fusionner le vêtement

Sélectionnez le vêtement - son armature et ses mailles, ou seulement ses mailles s'il n'a pas d'armature - puis Maj-cliquez en dernier sur l'armature de votre avatar, c'est donc l'objet actif. Cliquez sur **Merge Clothing**. Avec une armature de vêtements, BoneCraft déplace les vêtements sur votre squelette et fusionne les os; sans cela, il transfère le poids de votre corps vers les mailles des vêtements.

> Poids (weight painting) = nombres qui indiquent à chaque point d'un maillage à quel point chaque os le déplace. Si votre manche gauche pèse sur l’os du bras gauche, déplacer cet os entraîne la manche avec lui.

**Ce que vous devriez voir :** Les vêtements sous le squelette de votre avatar. Bouger un os déplace à la fois le corps et les vêtements.

---

### Étape 4 — Vérifier les traversées

Cliquez sur **Detect Collisions** pour rechercher les endroits où les vêtements traversent le corps. Corrigez-les en y ajustant les poids (voir les outils de poids dans [Outils de plate-forme](05-rig-tools.md) ).

**Ce que cela débloque :** Des vêtements qui bougent naturellement avec votre corps. Répétez l’opération pour chaque pièce de tenue.

Suivant: [Guides 8 à 13](03-guides-b.md)
