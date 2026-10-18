# Tutoriel : Crescent Rose avec Mechanisms

[← Sommaire](index.md)

<style>
@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--ce-que-vous-avez-construit"] { break-before: page; break-after: avoid; }
}
</style>

## Ce que vous allez construire

Crescent Rose est une faux qui se transforme en fusil. Vous allez équiper son modèle avec Mechanisms : un curseur transforme la faux en fusil, un autre replie le fusil en forme compacte. Vous utiliserez tous les types actuels d'articulations et liaisons sauf Gear Link : huit Hinges, trois Slides, un Telescope, un Piston, un Follow, puis deux Sequences et trois Forms.

Ces formes sont des poses pédagogiques pour ce modèle de fan. Mechanisms ne détecte pas les collisions et ne produit pas une réplique mécanique physiquement conçue : vérifiez les dégagements lorsque vous adaptez le rig.

Résultat : `examples/crescent-rose/CrescentRose_Mechanisms.blend`. Ouvrez-le à tout moment pour comparer.

## Avant de commencer

- Fichiers : partez de `examples/crescent-rose/CrescentRose_parts.blend`, déjà séparé en 15 objets. `CrescentRose_Mechanisms.blend` contient le rig terminé.
- Temps : prévoyez une séance pour préparer le FBX et une autre pour Mechanisms. Ces exercices sont conséquents ; sauvegardez entre les étapes.
- Vocabulaire : lisez d'abord la présentation dans [Mechanisms](07-mechanisms.md) : pièce, articulation, liaison, commande, Sequence et Form.
- Langue : les captures montrent Bforartists et BoneCraft en anglais. Les panneaux BoneCraft suivent **Language** dans ses préférences ; le reste suit la langue de Bforartists. Dans une langue non traduite par BoneCraft, ses panneaux restent anglais et cette édition s'applique.
- Départ : suivez P1-P8 pour le FBX original, ou passez à l'étape 1 avec le fichier préparé. Les deux parcours utilisent les mêmes 15 pièces.
- Version : instructions et captures réelles vérifiées avec BoneCraft `9.1.2` dans Bforartists `5.2.0`, raccourcis par défaut.

Les numéros rouges indiquent où cliquer, saisir ou vérifier. Suivez l'ordre de la légende (1, 2, 3) ; les numéros recommencent à chaque image. Un cadre indique un résultat à vérifier ; un cercle, une pièce ou un bouton à manipuler.

## Préparer le FBX original (P1-P8)

Ignorez cette section avec `CrescentRose_parts.blend`. Travaillez dans un nouveau fichier ; gardez le FBX source avec son dossier `CrescentRoseTextures`. Étapes rejouées dans Bforartists 5.2.0, raccourcis par défaut. Utilisez le menu des modes visible : Tab peut basculer les superpositions au lieu d'entrer en Edit Mode.

### P1 - Importer le FBX

Scène vide : **File > Import > FBX (.fbx) (Legacy)**, choisissez `CrescentRose.fbx`, laissez Scale à `1.00`. Utilisez l'importeur Legacy. L'Outliner contient une racine et trois maillages de matériaux : `Black01`, `Blades01`, `Red01`. Numpad 3 donne la vue droite ; Home les cadre.

![P1 - Importer le FBX](../images/crescent-rose/en/prep-01-import-fbx.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Sélectionnez CrescentRose.fbx. 2 : Gardez Scale à 1.00. 3 : Import FBX avec l'importeur Legacy.*

### P2 - Conserver le placement et régler la taille

En Object Mode, sélectionnez les trois maillages. Faites **Object > Parent > Clear and Keep Transformation**, puis retirez la racine inutilisée. Les trois sélectionnés, faites **Object > Apply > Rotation & Scale**. L'arme importée mesure environ `0.32 m`. Agrandissez les trois ensemble de `6.25` (Ctrl+R lance Scale avec ces raccourcis Bforartists ; saisissez 6.25 et confirmez), puis réappliquez Rotation & Scale. L'ensemble mesure alors environ `1.997 m`. Une seule fois : le fichier préparé est déjà à l'échelle.

![P2 - Conserver le placement et régler la taille](../images/crescent-rose/en/prep-02-unparent-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1 : F3, cherchez Clear Parent Keep Transform. 2 : Clear and Keep Transformation sur les trois maillages avant de supprimer la racine.*

![P2 - Conserver le placement et régler la taille](../images/crescent-rose/en/prep-02-scale.png){style="max-width:100%;max-height:115mm;width:auto;height:auto"}

*1 : Après l'agrandissement commun de 6.25, appliquez Rotation & Scale ; Rotation doit être 0. 2 : Scale doit être 1 sur tous les axes.*

Dimensions d'un objet mesure seulement son maillage de matériau. Mesurez l'étendue totale de bas en haut pour l'arme. Les trois objets doivent avoir rotation zéro et échelle 1 avant séparation.

### P3 - Connecter les matériaux

Passez à l'espace Shading et Material Preview. Pour chacun des trois matériaux, chargez les images correspondantes `BaseColor`, `Metallic`, `Roughness`, `Normal` depuis `CrescentRoseTextures`. Reliez Image Texture Color à l'entrée correspondante de Principled BSDF. BaseColor utilise **sRGB** ; les trois autres, `Non-Color`. Pour Normal, insérez **Normal Map**, gardez `Tangent Space`, reliez Color de l'image à Color du nœud et sa sortie Normal à BSDF Normal. Gardez les UV existants.

![P3 - Connecter les matériaux](../images/crescent-rose/en/prep-03-materials.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : BaseColor Color vers BSDF Base Color. 2 : BaseColor en sRGB. 3 : Cartes de données en Non-Color. 4 : Image Normal > Normal Map > BSDF Normal, Tangent Space.*

![P3 - Connecter les matériaux](../images/crescent-rose/en/prep-03-shaded.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Vérifiez le matériau de lame. 2 : Vérifiez les matériaux rouge/noir en Material Preview ; aucune texture manquante rose.*

Répétez pour les matériaux lame et rouge. Vérifiez l'espace colorimétrique après chaque choix : ce réglage appartient à l'image. L'arme doit être rouge, noire et métallique, sans rose de texture manquante.

### P4 - Séparer les éléments disjoints

Sélectionnez les trois maillages, choisissez **Edit Mode** dans le menu des modes, sélectionnez toute la géométrie, puis **Mesh > Separate > By Loose Parts**. Revenez en Object Mode : il y a **37** objets maillés. Les suffixes numériques peuvent varier ; identifiez-les par position et forme.

![P4 - Séparer les éléments disjoints](../images/crescent-rose/en/prep-04-separate-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1 : Edit Mode, sélectionnez toute la géométrie. 2 : F3, cherchez Separate Loose et choisissez By Loose Parts.*

![P4 - Séparer les éléments disjoints](../images/crescent-rose/en/prep-04-separate.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Vérifiez les 37 objets. 2 : Sélectionnez par forme et position dans l'Outliner ; les suffixes peuvent varier.*

### P5 - Joindre les 15 groupes mobiles

Sélectionnez les éléments qui bougent ensemble et faites **Object > Join** (Ctrl+J), puis renommez le résultat dans l'Outliner. Pour les paires opposées, orbitez pour sélectionner les deux et vérifiez avant de joindre. Travaillez de la pointe vers l'intérieur, puis sur le corps et le manche. Chaque îlot source est listé ; un nom de matériau décrit l'apparence, pas le nom final.

| Objet final | Éléments à joindre | Sommets |
|---|---|---:|
| `BladeTip` | Bouton noir d'articulation de pointe et pointe métallique | 252 |
| `Blade2` | Deux plaques métalliques du second segment et deux caches rouges | 1000 |
| `Blade1` | Deux plaques métalliques du premier segment près de la tête | 512 |
| `HeadMount` | Bloc arrière noir, capuchon supérieur et noyau ; deux plaques rouges internes et deux caches fins supérieurs | 1395 |
| `PlateL` | Plaque rouge externe côté X négatif | 676 |
| `PlateR` | Plaque rouge externe côté X positif | 676 |
| `RearSpike` | Deux lames métalliques, deux capuchons rouges de pivot, deux plaques rouges de fixation | 1194 |
| `Receiver` | Corps noir et petit bouton, anneau métallique au-dessus du verrou, long boîtier rouge | 2609 |
| `Grip` | Bloc rouge de poignée sous le corps | 194 |
| `Magazine` | Tube noir sous le corps | 96 |
| `Bolt` | Cylindre rouge du verrou et ses deux boutons | 362 |
| `Pole` | Tige inférieure métallique et collier rouge | 148 |
| `ButtSpike` | Pointe métallique inférieure | 110 |
| `StrutBase` | Tige rouge fine entre corps et tête | 34 |
| `StrutRod` | Manchon noir cranté autour de cette tige | 108 |

Total : **15 maillages, 9 366 sommets**. Ne joignez pas les plaques externes à Blade1, ni les deux éléments d'entretoise ensemble. L'entretoise est déjà séparée : aucun bisect requis. L'étape 2 reprend les noms et leurs parents.

![P5 - Joindre les 15 groupes mobiles](../images/crescent-rose/en/prep-05-group-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Renommez les 15 groupes dans l'Outliner selon le tableau.*

![P5 - Joindre les 15 groupes mobiles](../images/crescent-rose/en/prep-05-blade1.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Sélectionnez les deux plaques métalliques Blade1 opposées. 2 : Vérifiez les deux sélections, puis Join et nommez Blade1.*

![P5 - Joindre les 15 groupes mobiles](../images/crescent-rose/en/prep-05-join-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1 : Ouvrez Object après avoir sélectionné seulement un groupe. 2 : Join (Ctrl+J). Ce recadrage montre la commande ; utilisez la sélection à deux pièces illustrée au-dessus.*

### P6 - Centrer les origines

En Object Mode, sélectionnez les 15 maillages. Faites **Object > Set Origin > Origin to Geometry**, option Center : `Bounds Center`. Vérifiez rotation zéro et échelle 1. Toujours aucun parent ni armature. Ces origines facilitent la préparation ; l'étape 6 déplacera les pivots aux vraies articulations.

![P6 - Centrer les origines](../images/crescent-rose/en/prep-06-origin-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1 : Object. 2 : Survolez Set Origin. 3 : Origin to Geometry ; choisissez Bounds Center dans les options.*

![P6 - Centrer les origines](../images/crescent-rose/en/prep-06-origins.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Origine orange centrée sur le maillage. 2 : Rotation 0. 3 : Scale 1. Les pivots seront déplacés plus tard.*

### P7 - Redimensionner et empaqueter les textures

Dans Image Editor, sélectionnez chacune des **12 cartes utilisées** (quatre par matériau). **Image > Resize**, largeur et hauteur **1024**, confirmez, puis **Image > Pack**. Répétez pour chaque carte. Pack conserve les pixels redimensionnés dans le blend ; n'écrasez pas les JPEG source. Vérifiez ensuite Material Preview.

![P7 - Redimensionner et empaqueter les textures](../images/crescent-rose/en/prep-07-pack-textures.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Image > Resize, largeur et hauteur 1024. 2 : Vérifiez 1024 × 1024. 3 : Pack. Répétez pour les 12 cartes.*

### P8 - Sauvegarder et rouvrir le fichier préparé

Sauvegardez votre copie sous `CrescentRose_parts.blend`. Rouvrez et vérifiez les 15 maillages nommés, leurs transformations et les matériaux rouge/noir. Les 12 cartes doivent être disponibles sans le dossier original. Reprenez vue droite et Home, puis étape 1.

![P8 - Sauvegarder et rouvrir le fichier préparé](../images/crescent-rose/en/prep-08-save-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : File pour Save As, puis Open pour recharger. 2 : Vérifiez les 15 maillages nommés. 3 : Vérifiez les matériaux ; la barre de titre identifie le fichier rouvert.*

## A. Ouvrir le fichier



### Étape 1 — Ouvrir le fichier des pièces

Ouvrez `examples/crescent-rose/CrescentRose_parts.blend`. Passez en Material Preview, Numpad 3 pour la vue droite : lame à gauche, pointe inférieure vers le bas. Home cadre l'arme.

![Étape 1 — Ouvrir le fichier des pièces](../images/crescent-rose/en/01-open-file.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Material Preview. 2 : Numpad 3 jusqu'à Right Orthographic ; Home pour cadrer.*

**Résultat attendu :** faux rouge et noire d'environ 2 m, aucun objet sélectionné.

### Étape 2 — Découvrir les pièces

L'Outliner contient 15 objets ; chacun bouge d'un seul bloc :

| Objet | Description | Rides on |
|---|---|---|
| `Receiver` | Corps du fusil, lunette, détente et viseur | le rig |
| `Grip` | Poignée sous le corps | `Receiver` |
| `Magazine` | Chargeur cylindrique | `Receiver` |
| `Bolt` | Verrou | `Receiver` |
| `Pole` | Manche inférieur et collier | `Receiver` |
| `ButtSpike` | Pointe inférieure | `Pole` |
| `HeadMount` | Bloc portant la lame | `Receiver` |
| `Blade1` | Premier segment près de la tête | `HeadMount` |
| `Blade2` | Deuxième segment | `Blade1` |
| `BladeTip` | Pointe | `Blade2` |
| `RearSpike` | Pointe arrière de la tête | `HeadMount` |
| `PlateL`, `PlateR` | Plaques latérales externes | `HeadMount` |
| `StrutBase` | Tige fine entre corps et tête | `Receiver` |
| `StrutRod` | Manchon cranté de cette tige | `HeadMount` |

![Étape 2 — Découvrir les pièces](../images/crescent-rose/en/02-the-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Identifiez les trois segments de lame. 2 : Comparez les noms du corps, de la tête et du manche au tableau. 3 : Gardez StrutBase et StrutRod séparés.*

Pour le FBX original, suivez P1-P8. Le fichier préparé fourni provient de ces actions d'interface ; le script de préparation du dépôt donne un tableau de regroupement de référence.

### Étape 3 — Trouver Mechanisms

Ouvrez BoneCraft dans la Tool Shelf gauche (si masquée : T dans la vue 3D, puis Tools dans Region Toggle), dépliez **Mechanisms**. Élargissez en tirant le bord droit. La même section existe dans **Properties > Scene** si Scene Properties est sur Show dans les préférences BoneCraft. Les captures utilisent la Tool Shelf. Maillage actif, sans rig : repérez **Add Parts from Selection** en haut. Sélectionnez toutes les pièces à l'étape 4 avant de cliquer ; les sous-sections numérotées deviennent utilisables après l'ajout.

![Étape 3 — Trouver Mechanisms](../images/crescent-rose/en/03-mechanisms-section.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Onglet BoneCraft. 2 : Mechanisms. 3 : Repérez Add Parts from Selection ; sélectionnez les maillages avant utilisation.*

## B. Pièces



### Étape 4 — Add Parts from Selection

Pointeur dans la vue 3D, A sélectionne les 15 objets. Cliquez sur **Add Parts from Selection**.

![Étape 4 — Add Parts from Selection](../images/crescent-rose/en/04-add-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : A dans la vue 3D sélectionne les 15 maillages. 2 : Add Parts from Selection.*

**Résultat attendu :** nouvelle armature « Mechanism Rig » dans l'Outliner, avec les pièces dessous. Les maillages restent sélectionnés. **1. Parts** contient les 15 pièces ; BoneCraft commence maintenant par Overview du rig, que vous pouvez replier.

### Étape 5 — Rides on

Une pièce est portée par celle à laquelle elle est attachée. Choisissez `Blade1` dans **1. Parts**, puis `HeadMount` dans « Rides on » sous la liste. Répétez selon le tableau de l'étape 2. `Receiver` garde « the rig ».

![Étape 5 — Rides on](../images/crescent-rose/en/05-rides-on.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Blade1 dans Parts. 2 : Rides on → HeadMount. Répétez selon le tableau des parents.*

### Étape 6 — Pivots

Une charnière tourne autour du pivot de sa pièce. Les segments de lame, tête et poignée doivent tourner à l'articulation, pas au centre. `Blade1` sélectionné dans la liste : **Edit Pivot**, sélectionnez le marqueur, Ctrl+W pour Move dans Bforartists, placez-le à la jonction segment/tête, puis **Apply Pivot**. Travaillez de profil orthographique pour conserver la position latérale. Répétez pour `Blade2` (jonction Blade1), `BladeTip` (jonction Blade2), `HeadMount` (point inférieur où arrive l'entretoise), `Grip` (bord supérieur), `RearSpike` (jonction tête), `PlateL` et `PlateR` (centre du boulon rond où Blade1 rejoint la tête), `StrutBase` (bas), `StrutRod` (haut). La capture guide le placement ; quelques millimètres ne changent pas visiblement le résultat.

![Étape 6 — Pivots](../images/crescent-rose/en/06-edit-pivot-button.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1 : Blade1 dans Parts. 2 : Edit Pivot ; déplacez puis appliquez le marqueur comme ci-dessous.*

![Étape 6 — Pivots](../images/crescent-rose/en/06-edit-pivot.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Ctrl+W place le marqueur sur l'articulation de lame. 2 : Apply Pivot conserve la position.*

## C. La tête



### Étape 7 — Add Joint → Hinge

Ouvrez **Add Joint → Hinge**. Le guide démarre ; l'en-tête et la barre d'état expliquent chaque étape.

![Étape 7 — Add Joint → Hinge](../images/crescent-rose/en/07-head-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Add Joint. 2 : Hinge. Le guide attend une pièce.*

### Étape 8 — Cliquer sur la tête

L'en-tête demande la pièce qui tourne. De droite, la plaque externe masque la tête : cliquez sur le bloc arrière, derrière les plaques (cercle). Si l'en-tête indique `PlateR`, Esc, relancez **Add Joint > Hinge**, cliquez plus en arrière. Masquez les obstacles avant de lancer le guide : il intercepte les raccourcis clavier ordinaires.

![Étape 8 — Cliquer sur la tête](../images/crescent-rose/en/08-head-hinge-click.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Cliquez sur le bloc noir arrière de HeadMount derrière la plaque rouge. Vérifiez le nom HeadMount.*

### Étape 9 — X puis Enter

L'en-tête demande l'axe. Appuyez sur X : la tête tourne autour de l'axe latéral, avec aperçu en boucle. Enter conserve le résultat.

![Étape 9 — X puis Enter](../images/crescent-rose/en/09-head-hinge-axis.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : À l'invite d'axe, X puis Enter. 2 : Observez la rotation autour du pivot avant confirmation.*

**Résultat attendu :** `HeadMount Hinge` dans **2. Joints & Links**, son curseur dans **4. Controls**. Utilisez les curseurs en Object Mode. Pour les commandes d'os dans la vue 3D, sélectionnez l'armature et passez en Pose Mode.

### Étape 10 — Limites

Sélectionnez `HeadMount Hinge` dans la liste : **Min** 0, **Max** 120. Les valeurs positives tournent la tête vers le bas et l'arrière. Gardez la course de 120 degrés ; la séquence Rifle utilisera une cible de 90 degrés avec les charnières de lame.

![Étape 10 — Limites](../images/crescent-rose/en/10-head-hinge-limits.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : HeadMount Hinge. 2 : Min 0. 3 : Max 120 ; double-clic sur le nombre, saisissez, puis Enter.*

### Étape 11 — Tester

Cliquez sur le bouton lecture de la ligne. La tête va à 120°, revient, puis la pose est restaurée.

![Étape 11 — Tester](../images/crescent-rose/en/11-test-head.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Triangle lecture de HeadMount Hinge. Observez l'aller-retour.*

## D. Chaîne de lame



### Étape 12 — Trois autres charnières

Répétez 7 à 10 pour `Blade1`, `Blade2`, `BladeTip` : **Add Joint → Hinge**, cliquez sur le segment, X, Enter, puis **Max** 120. Chaque segment est porté par le précédent : les charnières forment une chaîne.

![Étape 12 — Trois autres charnières](../images/crescent-rose/en/12-blade-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Créez et sélectionnez chaque charnière Blade1, Blade2, BladeTip. 2 : Max 120 et axe X pour chacune.*

### Étape 13 — Essayer la chaîne

Repliez **2. Joints & Links**, dépliez **4. Controls**. En Object Mode, donnez 60 degrés à `Blade1 Hinge`, `Blade2 Hinge` et `BladeTip Hinge`, l'un après l'autre. Double-clic dans le champ, Ctrl+A, saisie, Enter. Les derniers segments suivent les premiers et la chaîne s'enroule. Remettez les trois à 0.

![Étape 13 — Essayer la chaîne](../images/crescent-rose/en/13-blade-chain.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Saisissez 60 dans les trois curseurs de lame. 2 : Vérifiez l'enroulement commun. Remettez les trois à 0.*

## E. Plaques et entretoise



### Étape 14 — Charnières des plaques

Ajoutez pareil une Hinge à `PlateR`, **Max** 30. `PlateL` est derrière la tête en vue droite : Ctrl+Numpad 3 pour la vue gauche, ajoutez sa Hinge, revenez avec Numpad 3.

![Étape 14 — Charnières des plaques](../images/crescent-rose/en/14-plate-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Créez les charnières PlateR et PlateL ; changez de côté pour atteindre PlateL. 2 : Max 30 chacune.*

### Étape 15 — Add Link → Follow

Une seule commande doit déplacer les deux plaques. Avant le guide : Numpad 1 pour la face, sélectionnez `Blade2`, puis F3 > Frame Selected pour rapprocher la tête. Les plaques sont aux bords gauche et droit. **Add Link > Follow**, cliquez `PlateL` à gauche (meneuse), puis `PlateR` à droite (suiveuse), Enter.

![Étape 15 — Add Link → Follow](../images/crescent-rose/en/15-follow.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : PlateL d'abord, pièce meneuse. 2 : PlateR ensuite, pièce suiveuse. Enter.*

### Étape 16 — Plages

Follow sélectionné, vérifiez les valeurs remplies automatiquement : **Source Range** 0…30, **Target Range** 0…30. Renommez `PlateR Follow` dans **Name**.

![Étape 16 — Plages](../images/crescent-rose/en/16-follow-ranges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Nom PlateR Follow. 2 : Source Range 0 à 30. 3 : Target Range 0 à 30.*

### Étape 17 — Add Link → Piston

L'entretoise doit rester orientée entre corps et tête pendant le repli. Avant le guide : Numpad 3, sélectionnez `StrutRod` dans l'Outliner, F3 > Frame Selected. **Add Link > Piston**. Cadrez d'abord : le guide intercepte les raccourcis de navigation.

![Étape 17 — Add Link → Piston](../images/crescent-rose/en/17-piston.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Add Link après cadrage de StrutRod. 2 : Piston ; le guide demande d'abord le cylindre.*

### Étape 18 — Cylindre et tige

Cliquez d'abord le cylindre : `StrutBase`, tige fine visible dans les crans du manchon. Puis la tige : `StrutRod`, le manchon. Dans la vue rapprochée, cliquez le rouge exposé avant le noir. Les rôles cylindre/tige décrivent les extrémités de liaison ; les noms d'objets décrivent les pièces source. Enter, nommez `Head Strut`, laissez **Stretch** désactivé.

**Résultat attendu :** changez `HeadMount Hinge` dans Controls : les deux éléments de l'entretoise se visent mutuellement. Remettez à zéro.

![Étape 18 — Cylindre et tige](../images/crescent-rose/en/18-piston-parts.png){style="max-width:100%;max-height:100mm;width:auto;height:auto"}

*1 : StrutBase rouge exposé d'abord. 2 : Manchon noir StrutRod ensuite. Enter.*

![Étape 18 — Cylindre et tige](../images/crescent-rose/en/18-piston-settings.png){style="max-width:100%;max-height:70mm;width:auto;height:auto"}

*1 : Nom Head Strut. 2 : Stretch décoché ; testez HeadMount Hinge et restaurez 0.*

## F. Le fusil



### Étape 19 — Charnières de poignée et pointe arrière

**Add Joint → Hinge** sur `Grip`, X, Enter, **Min** 0, **Max** 90. Répétez sur `RearSpike`, X, Enter, **Min** 0, **Max** 90. Sélectionnez `RearSpike Hinge`, réglez `Axis X à -1`, Y et Z à 0. Cela inverse le repli vers la tête rabattue dans Compact ; Grip reste sur X positif. Vérifiez les deux charnières dans la liste. Elles replient poignée et pointe arrière à l'étape 25.

![Étape 19 — Charnières de poignée et pointe arrière](../images/crescent-rose/en/19-grip-hinge.png){style="max-width:100%;max-height:110mm;width:auto;height:auto"}

*1 : Grip Hinge. 2 : Axis X 1, Y/Z 0. 3 : Max 90, Min 0.*

![Étape 19 — Charnières de poignée et pointe arrière](../images/crescent-rose/en/19-rear-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : RearSpike Hinge. 2 : Axis X -1. 3 : Max 90, Min 0.*

### Étape 20 — Glissières Magazine et Bolt

**Add Joint → Slide** sur `Magazine`, Z, Enter, **Max** 0.04. Puis Slide sur `Bolt`, Z, Enter, **Max** 0.06. Les valeurs sont en unités de scène : 0.06 = 6 cm.

![Étape 20 — Glissières Magazine et Bolt](../images/crescent-rose/en/20-slides.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Magazine Slide après Add Joint > Slide. 2 : Axe Z (Z = 1, X = Y = 0). 3 : Max 0.04, Min 0.*

![Étape 20 — Glissières Magazine et Bolt](../images/crescent-rose/en/20-bolt-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Bolt Slide après Add Joint > Slide. 2 : Axe Z (Z = 1, X = Y = 0). 3 : Max 0.06, Min 0.*

### Étape 21 — Glissière du manche

Slide sur `Pole`, Z, Enter, **Max** 0.6. Les valeurs positives remontent le manche dans le corps. Donnez 0.6 à `Pole Slide` dans **4. Controls** pour voir la rétraction, puis restaurez zéro.

![Étape 21 — Glissière du manche](../images/crescent-rose/en/21-pole-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Pole Slide après Add Joint > Slide. 2 : Axe Z (Z = 1, X = Y = 0). 3 : Max 0.6, Min 0.*

### Étape 22 — Télescope du manche

**Add Joint → Telescope**. Cliquez `Pole` (base), puis `ButtSpike` (segment), Enter, Z, Enter. **Length** 0.2. Sa commande indépendante déplace la pointe jusqu'à 20 cm sur Z positif, dans le manche. Testez et remettez à zéro.

![Étape 22 — Télescope du manche](../images/crescent-rose/en/22-telescope-pick.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Pole comme base. 2 : ButtSpike comme segment. Enter, Z, Enter.*

![Étape 22 — Télescope du manche](../images/crescent-rose/en/22-telescope.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Pole Telescope. 2 : Vérifiez l'axe Z. 3 : Length 0.2 ; testez et restaurez zéro.*

## G. Séquences



### Étape 23 — Add Sequence

Dans **3. Sequences**, **Add Sequence**, puis double-clic sur le nom dans la liste pour saisir `Scythe to Rifle`. Enter.

![Étape 23 — Add Sequence](../images/crescent-rose/en/23-add-sequence.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Add Sequence. 2 : Double-cliquez le nouveau nom, Scythe to Rifle, Enter.*

### Étape 24 — Enregistrer un groupe de mouvements

**Move Slider to End** place la séquence à `100%` et devient Record Step 1. Posez le premier groupe via **4. Controls** : `BladeTip Hinge` 70, `Blade2 Hinge` 120. Record Step 1 enregistre deux cibles, une par commande déplacée, puis remet leurs deux curseurs à zéro.

![Étape 24 — Enregistrer un groupe de mouvements](../images/crescent-rose/en/24-capture-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Un clic sur Move Slider to End. Le bouton devient Record Step 1.*

![Étape 24 — Enregistrer un groupe de mouvements](../images/crescent-rose/en/24-record-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Blade2 = 120, BladeTip = 70. 2 : Record Step 1 stocke les deux cibles et remet les curseurs à zéro.*

*Groupes suivants.* L'enregistrement reste armé après capture. Posez le groupe suivant et cliquez le bouton Record Step affiché, sans réarmer :

| Groupe | Commandes à poser | Bouton après les groupes précédents |
|---|---|---|
| 2 | `Blade1 Hinge` 10 et `PlateL Hinge` 30 | Record Step 3 |
| 3 | `HeadMount Hinge` 90 | Record Step 5 |
| 4 | `Pole Slide` 0.6 | Record Step 6 |

Le numéro vaut nombre de cibles stockées + 1. Deux commandes l'avancent de deux ; il ne compte pas les clics. Les quatre groupes donnent six cibles. Si vous changez les commandes, utilisez le numéro réellement affiché.

### Étape 25 — Les étapes

Chaque cible enregistrée possède une entrée sous la séquence : **Target**, interpolation, **Start** et **End** sur le curseur. Donnez les mêmes Start/End aux deux entrées d'un groupe : lame d'abord (0…0.25), plaques et premier segment ensuite (0.25…0.5), tête (0.5…0.8), manche (0.8…1). Avant sa plage, l'étape garde sa valeur initiale ; après, sa valeur finale. Start/End vont de 0 à 1, tandis que les curseurs Controls montrent 0 à 100%.

Gardez `Ease In Out`. Ajoutez `Rifle to Compact` : enregistrez `Grip Hinge` 90 et `RearSpike Hinge` 90 (deux entrées 0…0.5), puis `Magazine Slide` 0.04 et `Bolt Slide` 0.06 (deux entrées 0.5…1). Le bouton passe de Record Step 1 à Record Step 3 pour ce second groupe. Après chaque séquence, **Cancel** dans la bannière termine la capture, garde les entrées et remet le curseur de séquence à zéro. L'avertissement de chevauchement pendant l'armement décrit l'intervalle proposé suivant ; n'ajoutez pas de groupe vide.

![Étape 25 — Les étapes](../images/crescent-rose/en/25-sequence-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Target est la valeur d'articulation enregistrée. 2 : Ease In Out. 3 : Start. 4 : End. Répétez pour les six entrées selon les valeurs illustrées.*

![Étape 25 — Les étapes](../images/crescent-rose/en/25-compact-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Grip et RearSpike : Target 90, Start 0, End 0.5. 2 : Magazine et Bolt : 0.04 / 0.06, Start 0.5, End 1. Gardez Ease In Out.*

![Étape 25 — Les étapes](../images/crescent-rose/en/25-cancel-capture.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1 : Après la séquence, Cancel dans cette bannière termine la capture, garde les entrées et remet la séquence à zéro.*

### Étape 26 — Tester la séquence

Cliquez **Test** près du bouton d'enregistrement. Le curseur va de 0% à 100% puis 0%, et retrouve sa valeur antérieure. Testez `Scythe to Rifle` depuis Scythe ; `Rifle to Compact` avec la première séquence à 100%. Remettez ensuite les deux à 0%.

![Étape 26 — Tester la séquence](../images/crescent-rose/en/26-sequence-test.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Test près de l'enregistrement. 2 : Observez repli et retour. Testez Compact avec Scythe to Rifle à 100%.*

**Résultat attendu :** lame enroulée, plaques fermées, tête rabattue le long du corps, manche remonté. Puis retour de l'ensemble.

## H. Formes



### Étape 27 — Save Form

Dans **4. Controls**, tous les curseurs à 0, **Save Form**, puis double-clic dans la liste pour nommer `Scythe`. Mettez `Scythe to Rifle` à `100%`, sauvegardez et nommez `Rifle`. Mettez aussi `Rifle to Compact` à `100%`, sauvegardez et nommez `Compact`. Les curseurs d'articulation individuels restent à zéro : les séquences les pilotent. Mettre la séquence sélectionnée à sa fin peut réarmer la capture ; sauvegarder une Form n'enregistre pas une étape. `Scythe` puis **Go to Form** remet les deux séquences à zéro et désarme. Rifle ou Compact peut réarmer puisque la séquence sélectionnée atteint 100% ; ne cliquez Record Step que pour ajouter volontairement une cible.

![Étape 27 — Save Form](../images/crescent-rose/en/27-save-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Deux séquences et toutes les articulations à 0. 2 : Save Form. 3 : Double-clic, nom Scythe ; répétez pour Rifle et Compact.*

### Étape 28 — Go to Form

Choisissez une forme, puis **Go to Form**. **Go and Key** fait pareil et insère une clé pour chaque commande à l'image courante : cela anime la transformation.

![Étape 28 — Go to Form](../images/crescent-rose/en/28-go-to-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Forme sauvegardée. 2 : Go to Form. Go and Key ajoute les clés d'animation.*

### Étape 29 — Le fusil

![Étape 29 — Le fusil](../images/crescent-rose/en/29-result-rifle.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Rifle. 2 : Go to Form. 3 : Comparez les pourcentages des séquences à la pose illustrée.*

### Étape 30 — Compact

![Étape 30 — Compact](../images/crescent-rose/en/30-result-compact.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1 : Compact. 2 : Go to Form. 3 : Comparez les pourcentages des séquences à la pose illustrée.*

Revenez à `Scythe` et sauvegardez.

## Ce que vous avez construit

| Élément | Os | Fonction |
|---|---|---|
| 15 pièces | `MCH-<part>` et `DEF-<part>` | Chaque maillage est parenté à son os `DEF-` |
| 8 Hinges, 3 Slides, 1 Telescope | `CTRL-<part>` | Commandes et curseurs de **4. Controls** |
| 1 Piston | `MCH-<part>-aim` et `MCH-<part>-target` | Les éléments de l'entretoise se visent mutuellement |
| 1 Follow | aucun | `PlateR` tourne avec `PlateL` |
| 2 Sequences | `CTRL-SEQ-<name>` | Un curseur chacune |
| 3 Forms | aucun | Valeurs de curseurs sauvegardées |

L'exemple actualisé a passé Rig Validator sans problème signalé, puis les vérifications de rechargement avec Auto Run Python Scripts désactivé, y compris chaque commande et les trois Forms.

## Pour aller plus loin

- Activez **Curve** sur `PlateR Follow` et modifiez la correspondance dans Graph Editor.
- Sauvegardez une quatrième forme `Carry`, lame repliée et tête relevée.
- Animez les formes avec **Go and Key**, puis exportez les os `DEF-` (voir [Outils VRChat](08-vrchat.md)).

## Gear Link

Crescent Rose n'a pas de paire d'engrenages, donc pas de Gear Link. Celui-ci entraîne une Hinge par une autre selon un rapport de dents : manivelle/roue ou crémaillère transformant rotation en translation. Voir [Gear Link](07-mechanisms.md#gear-link-lien-dengrenage).

## Crédits

Modèle Crescent Rose par amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0 ; séparé, mis à l'échelle et équipé pour ce tutoriel. Crescent Rose est une création de Rooster Teeth Productions ; cet asset pédagogique est réalisé par un fan.

[← Sommaire](index.md)
