# Tutoriel : Crescent Rose avec mécanismes

[← Contenu](index.md)

<style>
section.chapter:has(#ch-12-crescent-rose) img {max-width:100%;width:auto;height:auto;}
img.manual-image-70 {max-height:70mm;}
img.manual-image-100 {max-height:100mm;}
img.manual-image-110 {max-height:110mm;}
img.manual-image-115 {max-height:115mm;}
img.manual-image-135 {max-height:135mm;}
img.manual-image-155 {max-height:155mm;}

@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--ce-que-tu-as-construit"] { break-before: page; break-after: avoid; }
}
</style>

## Ce que vous construirez

Crescent Rose est la faux qui est aussi un fusil. Dans ce didacticiel, vous en installez un modèle avec des mécanismes, de sorte qu'un curseur transforme la faux en fusil et qu'un deuxième curseur plie le fusil pour lui donner sa forme compacte. Sur la façon dont vous utilisez tous les mécanismes d'articulation et de liaison dont dispose aujourd'hui, à l'exception de Gear Link : huit charnières, trois glissières, un télescope, un piston et un suivi, puis deux séquences et trois formes.

Les formes sont des poses pédagogiques pour ce modèle réalisé en éventail. Les mécanismes ne détectent pas les collisions et ne fabriquent pas de réplique physiquement conçue : inspectez les dégagements lors de l'adaptation de la rig.

Le résultat est le fichier `examples/crescent-rose/CrescentRose_Mechanisms.blend`. Ouvrez-le à tout moment pour comparer.

## Avant de commencer

- Les fichiers : `examples/crescent-rose/CrescentRose_parts.blend` est le modèle déjà divisé en 15 objets partiels ; démarrez le tutoriel à partir de là. `CrescentRose_Mechanisms.blend` est l'installation finie.
- Temps: prévoir une séance séparée pour la préparation au FBX et une autre pour la leçon de Mécanismes; ce sont des exercices substantiels, pas des courses de vitesse chronométrées. Enregistrez les points de contrôle entre les étapes.
- Mots : lisez d'abord « Ce que font les mécanismes » dans [Mécanismes](07-mechanisms.md)  : il définit la pièce, l'articulation, le lien, la poignée, la séquence et la forme.
- Langue : les captures d'écran montrent le Bforartists en anglais avec les panneaux du BoneCraft en anglais. Les propres panneaux du BoneCraft suivent le paramètre **Language** dans ses préférences ; le reste du Bforartists suit le langage d'interface du Bforartists. Si votre Bforartists est dans une langue que BoneCraft ne traduit pas, ses panneaux restent en anglais et cette édition s'applique toujours.
- Itinéraire de départ : utilisez P1-P8 ci-dessous pour le FBX d'origine, ou passez à l'étape 1 avec le fichier préparé. Les deux itinéraires utilisent les mêmes 15 parties.
- Version : les instructions et les captures d'interface authentiques ont été vérifiées avec BoneCraft `9.1.2` dans Bforartists `5.2.0`, en utilisant son clavier par défaut.

Les marques numérotées en rouge identifient les éléments sur lesquels cliquer, saisir ou inspecter. Suivez la touche d'action numérotée de chaque image dans l'ordre (1, puis 2, puis 3). Les nombres redémarrent dans chaque image. Un résultat encadré est une vérification ; une partie ou un bouton encerclé est la cible de l'interaction.

## Préparez le FBX d'origine (P1-P8)

Ignorez cette section si vous utilisez `CrescentRose_parts.blend`. Travaillez dans un nouveau fichier et conservez la source FBX et son dossier `CrescentRoseTextures` ensemble. Ces étapes ont été rejouées dans Bforartists 5.2.0 avec le clavier par défaut. Utilisez le menu du mode visible : l'onglet peut basculer les superpositions dans ce clavier plutôt que d'entrer en mode édition.

### P1 - Importer le FBX

Commencez par une scène vide. Choisissez **File > Import > FBX (.fbx) (Legacy)**, sélectionnez `CrescentRose.fbx` et laissez l'échelle d'importation sur `1.00`. Utilisez l'importateur Legacy pour cette recette. L'Outliner contient une racine et trois maillages de matériaux : `Black01`, `Blades01` et `Red01`. Appuyez sur le pavé numérique 3 pour la vue droite et Accueil pour les encadrer.

![P1 : options d'importation héritées FBX avec Scale 1.00](../images/crescent-rose/en/prep-01-import-fbx.png){.manual-image-155}

*1 : Sélectionnez CrescentRose.fbx. 2 : Gardez l’échelle à 1,00. 3 : Cliquez sur Importer FBX  ; utilisez l'importateur Legacy.*

### P2 - Préserver le placement et définir la taille

En mode Objet, sélectionnez les trois maillages. Utilisez **Object > Parent > Clear and Keep Transformation**. Supprimez la racine désormais inutilisée de votre scène de travail. Une fois les trois maillages sélectionnés, utilisez**Object > Apply > Rotation & Scale**. L'arme importée mesure environ `0.32 m`. Mettez à l'échelle les trois ensemble par `6.25` (dans ce clavier Bforartists, Ctrl+R démarre l'échelle ; tapez 6,25 et confirmez), puis appliquez à nouveau Rotation et échelle. L'arme complète mesure désormais environ `1.997 m`. Faites cela une fois ; le raccourci préparé est déjà mis à l'échelle.

![P2: une parentalité claire tout en préservant le placement](../images/crescent-rose/en/prep-02-unparent-command.png){.manual-image-135}

*1 : Appuyez sur F3 et recherchez Clear Parent Keep Transform. 2 : Choisissez Effacer et conserver la transformation. Répétez l’opération pour les trois maillages avant de retirer la racine.*

![P2 : rotation et échelle appliquées sur l'arme importée](../images/crescent-rose/en/prep-02-scale.png){.manual-image-115}

*1 : Après avoir redimensionné les trois maillages ensemble de 6,25, appliquez Rotation et échelle ; La rotation doit indiquer 0. 2 : L'échelle doit indiquer 1 sur tous les axes.*

Le champ Dimensions d'un objet individuel mesure uniquement ce maillage matériel. Vérifiez l'étendue combinée de bas en haut lors de la mesure de l'arme. Les trois objets doivent afficher une rotation zéro et une échelle 1 avant la séparation.

### P3 - Connecter les matériaux

Basculez vers l’espace de travail Ombrage et Aperçu du matériau. Pour chacun des trois matériaux, chargez ses images `BaseColor`, `Metallic`, `Roughness` et `Normal` correspondantes à partir de `CrescentRoseTextures`. Connectez la couleur de la texture de l'image à l'entrée BSDF basée sur des principes correspondante. BaseColor utilise **sRGB** ; Métallique, rugosité et utilisation normale `Non-Color`. Pour Normal, insérez un nœud**Normal Map**, conservez `Tangent Space`, connectez la couleur de l'image à sa couleur et connectez sa sortie normale à la norme BSDF basée sur des principes. Conservez les UV existants.

![P3 : quatre cartes de texture et une carte normale de l'espace tangent connecté pour le matériau noir](../images/crescent-rose/en/prep-03-materials.png){.manual-image-155}

*1 : Connectez la couleur BaseColor à la couleur de base BSDF. 2 : Gardez BaseColor sur sRGB. 3 : Définissez toutes les cartes de données sur Non-Couleur. 4 : Connectez l'image normale > Carte normale > BSDF Normal, en utilisant l'espace tangent.*

![P3 : les trois matériaux dans l'aperçu des matériaux](../images/crescent-rose/en/prep-03-shaded.png){.manual-image-155}

*1 : Vérifiez le matériau de la lame. 2 : Vérifiez les matériaux du corps rouge/noir dans l'aperçu des matériaux ; aucune texture rose manquante.*

Répétez les mêmes connexions pour la lame et les matériaux rouges. Vérifiez l'espace colorimétrique de chaque image après l'avoir choisie ; le décor appartient à l'image. L'arme doit être rouge, noire et métallique, sans aucune texture rose manquante.

### P4 - Séparer les pièces détachées

Sélectionnez les trois maillages de matériaux, choisissez **Edit Mode** dans le menu du mode fenêtre, sélectionnez toute la géométrie, puis utilisez**Mesh > Separate > By Loose Parts**. Revenez au mode objet. Il y a**37** objets maillés à ce stade. Leurs suffixes numériques générés peuvent varier, alors identifiez-les par position et forme.

![P4 : entrez en mode édition et choisissez Par pièces détachées](../images/crescent-rose/en/prep-04-separate-command.png){.manual-image-135}

*1 : passez en mode édition et sélectionnez toute la géométrie. 2 : Appuyez sur F3, recherchez Séparer les pièces détachées et choisissez Par pièces détachées.*

![P4: les 37 pièces détachées après séparation](../images/crescent-rose/en/prep-04-separate.png){.manual-image-155}

*1 : Vérifiez que le total des objets est de 37 après la séparation. 2 : Utilisez l'Outliner pour sélectionner les pièces par forme et par emplacement ; les suffixes peuvent varier.*

### P5 - Rejoignez les 15 groupes en mouvement

Sélectionnez les pièces qui doivent se déplacer ensemble et utilisez **Object > Join** (Ctrl+J). Renommez l'objet résultant dans l'Outliner. Pour les pièces appariées sur des côtés opposés, faites une orbite autour de la vue pour sélectionner les deux ; vérifiez la sélection avant de rejoindre. Travaillez à partir de la pointe de la lame vers l’intérieur, puis le récepteur et la perche. Le tableau répertorie chaque îlot source ; un nom de matériau décrit son apparence, et non son nom d'objet final.

|Objet final|Pièces à combiner|Sommets du maillage après la jointure|
|---|---|---:|
|`BladeTip` |Bouton à pointe noire et pointe en métal|252|
|`Blade2` |Deux plaques métalliques de deuxième segment et deux couvercles rouges|1000|
|`Blade1` |Deux plaques métalliques du premier segment les plus proches de la tête|512|
|`HeadMount` |Bloc arrière, top cap et noyau noirs ; deux plaques intérieures rouges et deux minces couvercles supérieurs|1395|
|`PlateL` |Une plaque de tête extérieure rouge sur le négatif X|676|
|`PlateR` |Une plaque de tête extérieure rouge sur X positif|676|
|`RearSpike` |Deux lames à pointes métalliques, deux capuchons de pivot rouges et deux plaques de montage rouges|1194|
|`Receiver` |Corps et petit bouton noirs, anneau métallique au-dessus du boulon, long boîtier rouge|2609|
|`Grip` |Bloc de poignée rouge sous le récepteur|194|
|`Magazine` |Tube noir sous le corps|96|
|`Bolt` |Cylindre à boulon rouge et ses deux pièces de bouton|362|
|`Pole` |Tige inférieure en métal et collier rouge|148|
|`ButtSpike` |Piquet inférieur en métal|110|
|`StrutBase` |Fine tige rouge entre le récepteur et la tête|34|
|`StrutRod` |Manchon cranté noir autour de cette tige|108|

Il doit y avoir **15 mailles et 9 366 sommets** au total. Ne fusionnez pas les plaques extérieures dans Blade1, ni les deux pièces de support ensemble. La jambe de force comporte déjà deux pièces distinctes ; aucune bissectrice n’est nécessaire. L'étape 2 répète les noms des pièces finies et leur parentage ultérieur.

![P5 : les 15 groupes mobiles nommés dans l'Outliner](../images/crescent-rose/en/prep-05-group-parts.png){.manual-image-155}

*1 : Renommez chaque groupe rejoint dans l'Outliner pour qu'il corresponde aux 15 noms du tableau.*

![P5 : les deux plaques sources Blade1 sélectionnées avant de les rejoindre](../images/crescent-rose/en/prep-05-blade1.png){.manual-image-155}

*1 : Sélectionnez les deux plaques métalliques Blade1 sur les côtés opposés. 2 : Vérifiez que les deux objets sont sélectionnés, puis utilisez Join et renommez le résultat Blade1.*

![P5 : menu Objet, commande Rejoindre](../images/crescent-rose/en/prep-05-join-command.png){.manual-image-135}

*1 : Ouvrez l'objet après avoir sélectionné uniquement les pièces d'un groupe. 2 : Choisissez Rejoindre (Ctrl+J). Ce recadrage de menu identifie la commande ; utilisez la sélection en deux pièces présentée ci-dessus.*

### P6 - Centrer les origines

En mode Objet, sélectionnez les 15 maillages. Choisissez **Object > Set Origin > Origin to Geometry** et définissez l'option Centre de l'opération sur `Bounds Center`. Vérifiez le zéro de rotation et l'échelle 1. Les objets n'ont toujours pas de parents et il n'y a pas d'armature. Ce sont des origines de préparation pratiques; L'étape 6 déplace ensuite les pivots du mécanisme vers leurs articulations réelles.

![P6: Objet > Définir l'origine > Origine à la géométrie](../images/crescent-rose/en/prep-06-origin-command.png){.manual-image-135}

*1 : Objet ouvert. 2 : Survolez l'origine. 3 : Choisissez Origine vers Géométrie ; définissez le centre des limites dans les options de fonctionnement.*

![P6 : l'origine Blade1 centrée avec les transformations appliquées](../images/crescent-rose/en/prep-06-origins.png){.manual-image-155}

*1: L'origine orange est désormais centrée sur le maillage. 2: Confirmez la rotation 0. 3: Confirmez l'échelle 1. Les pivots du mécanisme sont déplacés plus tard.*

### P7 - Redimensionner et compresser les textures

Dans l'éditeur d'images, sélectionnez chacune des **12 cartes utilisées** (quatre par matériau). Choisissez**Image > Resize**, définissez la largeur et la hauteur sur**1024**, confirmez, puis choisissez**Image > Pack**. Répétez l’opération pour chaque carte utilisée. Le compactage de l'image redimensionnée préserve ces pixels à l'intérieur du mélange ; n’écrasez pas les fichiers JPEG sources. Vérifiez ensuite l'aperçu du matériau.

![P7 : menu Image contenant une texture redimensionnée de 1024 par 1024](../images/crescent-rose/en/prep-07-pack-textures.png){.manual-image-155}

*1 : Choisissez Image > Redimensionner et saisissez 1024 pour la largeur et la hauteur. 2 : Vérifiez les dimensions 1024 x 1024 obtenues. 3 : Choisissez Pack. Répétez l’opération pour les 12 cartes utilisées.*

### P8 - Enregistrez et rouvrez le fichier préparé

Enregistrez votre copie de travail sous le nom `CrescentRose_parts.blend`. Rouvrez-le et vérifiez les 15 maillages nommés, leurs transformations et les matériaux rouge/noir. Les 12 cartes devraient rester disponibles sans dépendre du répertoire de texture d'origine. Utilisez à nouveau la vue de droite et l'accueil, puis passez à l'étape 1.

![P8: le fichier préparé rouvert avec l'arme texturée intacte](../images/crescent-rose/en/prep-08-save-parts.png){.manual-image-155}

*1 : ouvrez le fichier pour l'enregistrer sous, puis ouvrez-le pour recharger votre copie de travail. 2 : Confirmez que les 15 maillages nommés ont survécu. 3: Vérifiez les matériaux ; la barre de titre identifie le fichier rouvert.*

## A. Ouvrez le fichier

### Étape 1 — Ouvrez le fichier de pièces

Ouvrez `examples/crescent-rose/CrescentRose_parts.blend`. Basculez la fenêtre sur l'ombrage Aperçu du matériau et appuyez sur le pavé numérique 3 pour la vue de droite : la lame pointe vers la gauche, la crosse pointe vers le bas. Appuyez sur Accueil pour cadrer l'arme.

![Etape 1: le fichier pièces dans la vue de droite](../images/crescent-rose/en/01-open-file.png){.manual-image-155}

*1 : Cliquez sur Aperçu du matériau. 2 : Appuyez sur le pavé numérique 3 jusqu'à ce que la vue indique Right Orthographic ; appuyez sur Accueil pour cadrer l'arme.*

**Ce que vous devriez voir :** La faux en rouge et noir, d'environ 2 m de haut, sans rien sélectionné.

### Étape 2 — Rencontrez les pièces

L'Outliner répertorie les 15 objets. Chacun est une pièce qui se déplace comme un seul bloc :

|Objet|Qu'est-ce que c'est|monte sur|
|---|---|---|
|`Receiver` |Le corps du fusil avec la lunette, la gâchette et le viseur|le gréement|
|`Grip` |La poignée sous le récepteur|`Receiver` |
|`Magazine` |Le magasin à cylindres|`Receiver` |
|`Bolt` |Le boulon|`Receiver` |
|`Pole` |La tige inférieure et sa collerette|`Receiver` |
|`ButtSpike` |La pointe en bas|`Pole` |
|`HeadMount` |Le bloc de tête auquel la lame est suspendue|`Receiver` |
|`Blade1` |Le premier segment de lame, le plus proche de la tête|`HeadMount` |
|`Blade2` |La deuxième partie|`Blade1` |
|`BladeTip` |Le conseil|`Blade2` |
|`RearSpike` |La pointe à l'arrière de la tête|`HeadMount` |
|`PlateL`, `PlateR` |Les plaques latérales extérieures de la tête|`HeadMount` |
|`StrutBase` |La fine tige entre le récepteur et la tête|`Receiver` |
|`StrutRod` |Le manchon cranté autour de cette tige|`HeadMount` |

![Étape 2: les 15 objets partiels dans l'Outliner](../images/crescent-rose/en/02-the-parts.png){.manual-image-155}

*1 : Identifiez les trois segments de lame. 2: Associez les noms du corps, de la tête et des bâtons au tableau. 3 : Conservez StrutBase et StrutRod comme objets distincts.*

Pour le FBX original, suivez P1-P8 ci-dessus. Le fichier préparé fourni a été créé via ces actions d'interface ; le script de préparation du référentiel fournit une table de regroupement de références.

### Étape 3 — Trouver des mécanismes

Ouvrez l'onglet BoneCraft sur l'étagère à outils de gauche (s'il est masqué, appuyez sur T au-dessus de la fenêtre et choisissez Outils dans le menu Basculer la région) et développez **Mechanisms**. Élargissez l'étagère en faisant glisser son bord droit jusqu'à ce que le texte du panneau ait de la place. Alternativement, la même section Mécanismes est disponible dans**Properties > Scene** lorsque Propriétés de la scène est définie sur Afficher dans les préférences BoneCraft. Les captures d'écran utilisent l'étagère à outils. Avec un maillage actif et pas encore de rig, recherchez**Add Parts from Selection** en haut de la section. Sélectionnez toutes les pièces à l'étape 4 avant de cliquer dessus ; les sous-sections numérotées deviennent utilisables une fois les parties ajoutées.

![Étape 3: la section Mécanismes de l'onglet BoneCraft](../images/crescent-rose/en/03-mechanisms-section.png){.manual-image-155}

*1 : Cliquez sur l'onglet BoneCraft. 2 : Développer les mécanismes. 3 : Trouver Ajouter des pièces à partir de la sélection ; sélectionner les maillages avant de l'utiliser.*

## B. Pièces

### Étape 4 — Ajouter des pièces à partir de la sélection

Survolez la fenêtre et appuyez sur A pour sélectionner les 15 objets. Cliquez sur **Add Parts from Selection**.

![Étape 4 : toutes les pièces sélectionnées, ajouter des pièces de la sélection](../images/crescent-rose/en/04-add-parts.png){.manual-image-155}

*1 : survolez la fenêtre et appuyez sur A pour sélectionner les 15 maillages. 2 : Cliquez sur Ajouter des pièces à partir de la sélection.*

**Ce que vous devriez voir :** Une nouvelle armature, "Mechanism Rig", apparaît dans l'Outliner avec les pièces en dessous. Les objets maillés restent sélectionnés après l'opération.**1. Parts** répertorie les 15 pièces et l'onglet BoneCraft commence désormais par la présentation de l'installation, que vous pouvez réduire.

### Étape 5 - Continue

Une pièce repose sur la pièce à laquelle elle est attachée. Cliquez sur `Blade1` dans la liste **1. Parts**, ouvrez le menu « Rides on » sous la liste et choisissez `HeadMount`. Faites de même pour chaque pièce du tableau de l'étape 2. `Receiver` conserve "le rig".

![Étape 5 : Blade1 monte sur HeadMount](../images/crescent-rose/en/05-rides-on.png){.manual-image-155}

*1 : Sélectionnez Blade1 dans la liste des pièces. 2 : Ouvrez Rides et choisissez HeadMount. Répétez en utilisant la table parent.*

### Étape 6 — Pivots

Une charnière tourne autour du pivot de sa pièce. Les segments de lame, la tête et le manche doivent tourner au niveau de leurs articulations et non en leur centre. Avec `Blade1` sélectionné dans la liste, cliquez sur **Edit Pivot**, sélectionnez le marqueur, appuyez sur Ctrl+W pour Déplacer dans Bforartists, cliquez à l'endroit où le segment rencontre la tête, puis cliquez sur**Apply Pivot**. Travaillez dans la vue latérale orthographique afin que la position du pivot latéral reste inchangée. Répétez l'opération pour `Blade2` (où il rencontre `Blade1` ), `BladeTip` (où il rencontre `Blade2` ), `HeadMount` (son point le plus bas, là où la jambe de force le rencontre), `Grip` (son bord supérieur), `RearSpike` (où il rencontre la tête), `PlateL` et `PlateR` (le centre du boulon rond où Blade1 rencontre la tête), `StrutBase` (sa partie inférieure) et `StrutRod` (sa partie supérieure). La position du marqueur sur la capture d'écran est un guide ; quelques millimètres ne font aucune différence visible.

![Étape 6 : sélectionnez la pièce et cliquez sur Modifier le pivot](../images/crescent-rose/en/06-edit-pivot-button.png){.manual-image-135}

*1 : Sélectionnez Blade1 dans Pièces. 2 : Cliquez sur Modifier le pivot ; puis déplacez et appliquez le marqueur comme indiqué ci-dessous.*

![Étape 6 : marqueur de pivot de Blade1 au niveau de l'articulation, appliquer le pivot](../images/crescent-rose/en/06-edit-pivot.png){.manual-image-155}

*1 : Déplacez le marqueur de pivot vers l'articulation de la lame avec Ctrl+W. 2 : Cliquez sur Appliquer le pivot pour conserver cet emplacement.*

## C. La tête

### Étape 7 — Ajouter un joint → Charnière

Ouvrez **Add Joint → Hinge**. Une construction guidée démarre : l'en-tête et la barre d'état vous indiquent quoi faire à chaque étape.

![Étape 7 : le menu Ajouter un joint, Charnière](../images/crescent-rose/en/07-head-hinge.png){.manual-image-155}

*1 : Ouvrez Ajouter une articulation. 2 : Cliquez sur Charnière. La construction guidée attend maintenant une pièce.*

### Étape 8 — Cliquez sur la tête

L'en-tête dit "cliquez sur la pièce qui tourne". Dans la vue de droite, la plaque extérieure se trouve devant la tête, cliquez donc sur le bloc arrière de la tête, derrière les plaques (le cercle). Si l'en-tête s'intitule `PlateR`, appuyez sur Échap, redémarrez **Add Joint > Hinge** et cliquez plus en arrière. Si vous devez masquer un obstacle, faites-le avant de démarrer le guide. Le guide utilise des raccourcis clavier ordinaires lorsqu'il est actif.

![Étape 8: cliquez sur le bloc arrière de la tête](../images/crescent-rose/en/08-head-hinge-click.png){.manual-image-155}

*1 : Cliquez sur le bloc noir arrière du HeadMount, derrière la plaque extérieure rouge. Vérifiez les noms des guides HeadMount.*

### Étape 9 — Appuyez sur X, puis sur Entrée

L'en-tête demande maintenant l'axe. Appuyez sur X : la tête tourne autour de l'axe latéral et le guide prévisualise le mouvement en boucle. Appuyez sur Entrée pour le conserver.

![Étape 9: le pas de l'axe](../images/crescent-rose/en/09-head-hinge-axis.png){.manual-image-155}

*1 : Suivez l'invite de l'axe : appuyez sur X, puis sur Entrée. 2: Observez la rotation de la tête autour de son pivot avant de confirmer.*

**Ce que vous devriez voir :** `HeadMount Hinge` dans la liste**2. Joints & Links** et son curseur dans**4. Controls**. Utilisez ces curseurs en mode objet. Pour utiliser les poignées osseuses de la fenêtre, sélectionnez l'armature et passez en mode Pose.

### Étape 10 — Limites

Avec `HeadMount Hinge` sélectionné dans la liste, définissez **Min** sur 0 et**Max** sur 120. Les valeurs positives font baisser et reculer la tête. Gardez la limite de déplacement de 120 degrés ; la séquence de fusil utilisera une cible à 90 degrés avec les charnières de la lame.

![Étape 10 : Min 0, Max 120](../images/crescent-rose/en/10-head-hinge-limits.png){.manual-image-155}

*1 : Sélectionnez la charnière HeadMount. 2 : Réglez Min sur 0. 3 : Réglez Max sur 120 ; double-cliquez sur le numéro, saisissez-le et appuyez sur Entrée.*

### Étape 11 — Tester

Cliquez sur le bouton de lecture de la ligne. La tête s'incline à 120° et recule, et la pose est restaurée.

![Étape 11: Test sur la rangée de charnières](../images/crescent-rose/en/11-test-head.png){.manual-image-155}

*1 : Cliquez sur le petit triangle de jeu sur la rangée HeadMount Hinge. Regardez le balayage et revenez.*

## D. La chaîne de lames

### Étape 12 — Trois charnières supplémentaires

Répétez les étapes 7 à 10 pour `Blade1`, `Blade2` et `BladeTip`  : **Add Joint → Hinge**, cliquez sur le segment, X, Entrée, puis**Max** 120. Chaque segment repose sur celui qui le précède, de sorte que les trois charnières forment une chaîne.

![Étape 12: les trois charnières à segments de lame et la charnière à tête séparée dans la liste](../images/crescent-rose/en/12-blade-hinges.png){.manual-image-155}

*1 : Créez et sélectionnez chaque charnière de lame : Blade1, Blade2, BladeTip. 2 : Réglez Max à 120 pour chacun ; utilisez X comme axe.*

### Étape 13 — Essayez la chaîne

Réduisez **2. Joints & Links** pour libérer de l'espace et développer**4. Controls**. En mode objet, réglez `Blade1 Hinge`, `Blade2 Hinge` et `BladeTip Hinge` sur 60 degrés, un à la fois. Double-cliquez sur un champ numérique, appuyez sur Ctrl+A, saisissez la valeur et appuyez sur Entrée. Les derniers segments se déplacent avec les premiers et la chaîne s'enroule. Remettez les trois valeurs à 0 avant de continuer.

![Étape 13: les trois charnières des lames s'articulent à 60 degrés dans Controls](../images/crescent-rose/en/13-blade-chain.png){.manual-image-155}

*1 : Saisissez 60 dans chacun des trois curseurs de lame. 2 : Vérifiez que la chaîne s'enroule ensemble. Remettez les trois curseurs à 0.*

## E. Plaques et jambe de force

### Étape 14 — Charnières sur les plaques

Ajoutez une charnière sur `PlateR` de la même manière, **Max** 30. `PlateL` est caché derrière la tête dans la vue droite: appuyez sur Ctrl+Numpad 3 pour la vue gauche, ajoutez sa charnière et revenez avec Numpad 3.

![Étape 14 : Charnière PlateL et charnière PlateR](../images/crescent-rose/en/14-plate-hinges.png){.manual-image-155}

*1 : Fabriquez les charnières PlateR et PlateL ; utilisez la vue latérale opposée pour atteindre PlateL. 2 : Réglez chaque maximum sur 30.*

### Étape 15 — Ajouter un lien → Suivre

Une poignée doit déplacer les deux plaques. Avant de démarrer le guide, appuyez sur le pavé numérique 1 pour la vue de face, sélectionnez `Blade2` et utilisez F3 > Cadre sélectionné pour rapprocher la tête. Les deux plaques extérieures apparaissent sur les bords gauche et droit. Ouvrez **Add Link > Follow**, cliquez sur `PlateL` sur le bord gauche (la partie principale), puis sur `PlateR` sur le bord droit (la partie suivante) et appuyez sur Entrée.

![Étape 15: La vue de face expose les deux plaques extérieures pour les médiators Follow](../images/crescent-rose/en/15-follow.png){.manual-image-155}

*1 : Cliquez d'abord sur PlateL, la partie principale. 2: Cliquez sur PlateR deuxième, la partie suivante. Appuyez sur Entrée.*

### Étape 16 — Gammes

Une fois le nouveau suivi sélectionné, vérifiez les valeurs **Source Range** 0…30 et**Target Range** 0…30 renseignées automatiquement. Renommez-le `PlateR Follow` en**Name**.

![Étape 16 : Plage source et plage cible](../images/crescent-rose/en/16-follow-ranges.png){.manual-image-155}

*1 : Nommez le lien PlateR Follow. 2 : Vérifiez que la plage source est de 0 à 30. 3 : Vérifiez que la plage cible est de 0 à 30.*

### Étape 17 — Ajouter un lien → Piston

La jambe de force doit rester pointée entre le récepteur et la tête pendant que la tête se replie. Avant de démarrer le guide, appuyez sur le pavé numérique 3 pour la vue droite, sélectionnez `StrutRod` dans l'Outliner et utilisez F3 > Cadre sélectionné. Ouvrez **Add Link > Piston**. Définissez d'abord cette vue rapprochée ; les raccourcis de navigation sont utilisés lorsque le guide est actif.

![Étape 17: le menu Ajouter un lien, Piston](../images/crescent-rose/en/17-piston.png){.manual-image-155}

*1 : Ouvrez Ajouter un lien après avoir encadré StrutRod. 2 : Choisissez Piston ; le guide demande d’abord le cylindre.*

### Étape 18 — Le cylindre et la tige

Cliquez d'abord sur la partie du cylindre : `StrutBase`, la tige fine, qui apparaît dans les encoches du manchon. Cliquez ensuite sur la partie tige: `StrutRod`, le manchon. Utilisez la vue rapprochée pour cliquer d'abord sur la tige rouge exposée, puis sur le manchon noir. Les rôles cylindre/tige du guide décrivent les extrémités du maillon ; les noms d'objet de ce modèle décrivent ses pièces sources. Appuyez sur Entrée pour accepter, renommez le lien `Head Strut` et laissez **Stretch** désactivé.

**Ce que vous devriez voir :** Modifiez `HeadMount Hinge` dans les commandes : la jambe de force suit, chaque partie étant dirigée vers l'autre. Remettez la valeur à zéro.

![Etape 18: le guide piston, cylindre rouge exposé puis manchon noir](../images/crescent-rose/en/18-piston-parts.png){.manual-image-100}

*1 : Cliquez d'abord sur la StrutBase rouge exposée. 2 : Cliquez ensuite sur le manchon noir du StrutRod. Appuyez sur Entrée.*

![Étape 18 : Paramètres du support de tête avec étirement désactivé](../images/crescent-rose/en/18-piston-settings.png){.manual-image-70}

*1 : Renommez le lien Head Strut. 2 : laissez Étirer décochée ; puis testez la charnière HeadMount et restaurez 0.*

## F. Le fusil

### Étape 19 — Charnières de poignée et de pointe arrière

**Add Joint → Hinge** sur `Grip`, X, Enter,**Min** 0,**Max** 90. Répéter sur `RearSpike`, X, Enter,**Min** 0,**Max** 90. Sélectionnez ensuite `RearSpike Hinge` dans la liste et modifiez son `Axis X to -1`, en laissant Y et Z à 0. Cela inverse sa direction de pliage de sorte que la pointe arrière se retourne vers la tête pliée en Compact ; gardez Grip sur X positif. Confirmez que `Grip Hinge` et `RearSpike Hinge` apparaissent dans la liste commune. Ces deux commandes plient la poignée et la pointe arrière pour obtenir la forme compacte à l'étape 25.

![Étape 19: Charnière à poignée, Max 90](../images/crescent-rose/en/19-grip-hinge.png){.manual-image-110}

*1 : Sélectionnez Charnière à poignée. 2: Gardez l'axe X à 1, Y et Z à 0. 3: Réglez Max à 90; garder Min à 0.*

![Étape 19: Charnière RearSpike avec Axis X -1 et Max 90](../images/crescent-rose/en/19-rear-hinge.png){.manual-image-155}

*1 : Sélectionnez la charnière RearSpike. 2 : Réglez l’axe X sur -1. 3 : réglez Max sur 90 ; garder Min à 0.*

### Étape 20 - Glissières de chargeur et de boulon

**Add Joint → Slide** sur `Magazine`, appuyez sur Z, Entrée,**Max** 0,04. Puis une diapositive sur `Bolt`, Z, Enter,**Max** 0,06. Les diapositives mesurent en unités de scène : 0,06 correspond à 6 cm.

![Étape 20: Diapositive du magazine, axe Z et Max 0,04](../images/crescent-rose/en/20-slides.png){.manual-image-155}

*1 : Sélectionnez Diapositive de magazine après Ajouter un joint > Diapositive. 2 : Utilisez l'axe Z (Z = 1, X = Y = 0). 3 : réglez Max sur 0,04 ; garder Min à 0.*

![Étape 20: Glissière de boulon, axe Z et Max 0,06](../images/crescent-rose/en/20-bolt-slide.png){.manual-image-155}

*1 : Sélectionnez Glissière de boulon après Ajouter un joint > Glissière. 2 : Utilisez l'axe Z (Z = 1, X = Y = 0). 3 : réglez Max sur 0,06 ; garder Min à 0.*

### Étape 21 — Glissade sur poteau

Une diapositive sur `Pole`, Z, Enter, **Max** 0.6. Les valeurs positives déplacent le pôle vers le récepteur. Réglez `Pole Slide` sur 0,6 dans**4. Controls** pour voir l'arbre se rétracter, puis remettez-le à zéro.

![Étape 21: Paramètres de Pole Slide, axe Z et Max 0,6](../images/crescent-rose/en/21-pole-slide.png){.manual-image-155}

*1 : Sélectionnez Pole Slide après Ajouter un joint > Slide. 2 : Utilisez l'axe Z (Z = 1, X = Y = 0). 3 : réglez Max sur 0,6 ; garder Min à 0.*

### Étape 22 — Télescope polaire

**Add Joint → Telescope**. Cliquez sur `Pole` (la base), puis sur `ButtSpike` (le segment), appuyez sur Entrée, appuyez sur Z, appuyez sur Entrée. Ensemble**Length** 0.2. Sa commande séparée déplace la pointe jusqu'à 20 cm le long d'un Z positif, dans le poteau de ce modèle. Testez-le et restaurez zéro.

![Étape 22 : sélections guidées du télescope, pôle comme base et ButtSpike comme segment](../images/crescent-rose/en/22-telescope-pick.png){.manual-image-155}

*1 : Cliquez sur Poteau comme base. 2 : Cliquez sur ButtSpike comme segment. Appuyez sur Entrée, puis sur Z, puis sur Entrée.*

![Étape 22: Paramètres du télescope polaire, axe Z et longueur 0,2](../images/crescent-rose/en/22-telescope.png){.manual-image-155}

*1 : Sélectionnez le télescope polaire. 2 : Vérifiez que Z est son axe. 3 : Entrez la longueur 0,2 ; testez le contrôle et rétablissez zéro.*

## G. Séquences

### Étape 23 — Ajouter une séquence

Dans **3. Sequences**, cliquez sur**Add Sequence** et double-cliquez sur son nom dans la liste pour le renommer `Scythe to Rifle`. Appuyez sur Entrée.

![Étape 23 : Ajouter une séquence](../images/crescent-rose/en/23-add-sequence.png){.manual-image-155}

*1 : Cliquez sur Ajouter une séquence. 2 : Double-cliquez sur le nouveau nom et tapez Scythe to Rifle. Appuyez sur Entrée.*

### Étape 24 — Enregistrez un groupe de mouvements

Cliquez sur **Move Slider to End**  : le curseur de la séquence passe à `100%` et le bouton devient Enregistrer l'étape 1. Posez maintenant le premier groupe de mouvements avec les curseurs dans**4. Controls**  : `BladeTip Hinge` 70 et `Blade2 Hinge` 120. Cliquez sur Enregistrer l'étape 1. Cela stocke deux entrées cibles, une pour chaque élément déplacé. poignée et remet ces deux curseurs communs à zéro.

![Étape 24 : Déplacez le curseur vers la fin avant de poser le premier groupe](../images/crescent-rose/en/24-capture-step.png){.manual-image-155}

*1 : cliquez une fois sur Déplacer le curseur vers la fin. Le bouton devient Enregistrer l’étape 1.*

![Étape 24: Enregistrez l'étape 1 avec Blade2 à 120 et BladeTip à 70 degrés](../images/crescent-rose/en/24-record-step.png){.manual-image-155}

*1: Entrez Blade2 = 120 et BladeTip = 70. 2: Cliquez sur Enregistrer l'étape 1 ; les deux cibles sont stockées et les curseurs communs sont réinitialisés.*

*Groupes de mouvements restants.* L'enregistrement reste armé après chaque capture. Posez le groupe suivant et cliquez sur le bouton Enregistrer l'étape affiché ; ne l'armez plus :

|Groupe de mouvement|Posez ces poignées|Bouton d'enregistrement après les groupes précédents|
|---|---|---|
|2|`Blade1 Hinge` 10 et `PlateL Hinge` 30|Enregistrer l'étape 3|
|3|`HeadMount Hinge` 90|Enregistrer l'étape 5|
|4|`Pole Slide` 0,6|Enregistrer l'étape 6|

Le numéro du bouton est le nombre d'entrées cibles stockées plus une. L'enregistrement de deux poignées l'avance de deux ; il ne compte pas les clics d'enregistrement. Les quatre groupes de mouvements ci-dessus produisent donc six entrées cibles. Si vous changez les poignées qui se déplacent, utilisez le numéro réellement affiché.

### Étape 25 — Les étapes

Chaque cible enregistrée a sa propre entrée sous la séquence, affichant son **Target**, sa facilité et ses**Start** et**End** sur le curseur. Donnez aux deux entrées de chaque groupe de mouvements le même début et la même fin : la lame se plie en premier (0…0,25), les plaques et le premier segment ensuite (0,25…0,5), la tête en troisième (0,5…0,8) et le poteau en dernier (0,8…1). Avant sa tranche, un pas reste à sa valeur de départ; après sa tranche, il conserve sa valeur finale. Les champs Début/Fin utilisent 0-1, tandis que les curseurs Contrôles affichent 0-100 %.

Conservez chaque entrée sur `Ease In Out`. Ajoutez ensuite une deuxième séquence, `Rifle to Compact`  : premier enregistrement `Grip Hinge` 90 et `RearSpike Hinge` 90 (deux entrées, toutes deux 0…0,5) ; puis enregistrez `Magazine Slide` 0,04 et `Bolt Slide` 0,06 (deux entrées, toutes deux 0,5…1). Son bouton d'enregistrement passe de Record Step 1 à Record Step 3 pour le deuxième groupe. Une fois chaque séquence terminée, cliquez sur **Cancel** dans la bannière de capture. Cela met fin à l'enregistrement, conserve les entrées stockées et ramène ce curseur de séquence à zéro. Un avertissement de chevauchement pendant l'armement décrit le prochain intervalle d'enregistrement proposé ; n'ajoutez pas de groupe vide supplémentaire.

![Étape 25 : les six cibles et tranches de temps dans Scythe to Rifle](../images/crescent-rose/en/25-sequence-steps.png){.manual-image-155}

*1 : La cible est la valeur commune enregistrée. 2 : Choisissez Facilité d'entrée et de sortie. 3 : Entrez Démarrer. 4 : Entrez Fin. Répétez ces champs pour les six entrées en utilisant les valeurs affichées.*

![Étape 25 : les quatre cibles et tranches de temps dans Rifle to Compact](../images/crescent-rose/en/25-compact-steps.png){.manual-image-155}

*1 : Grip et RearSpike utilisent Target 90, Start 0, End 0.5. 2 : Le chargeur et le boulon utilisent 0,04/0,06, début 0,5, fin 1. Gardez la facilité d'entrée et de sortie.*

![Étape 25: terminer l'enregistrement avec Annuler dans la bannière de capture](../images/crescent-rose/en/25-cancel-capture.png){.manual-image-135}

*1 : Après avoir terminé une séquence, cliquez sur Annuler dans cette bannière de capture pour terminer l'enregistrement. Cela conserve les entrées et remet la séquence à zéro.*

### Étape 26 — Testez la séquence

Cliquez sur **Test** à côté du bouton d'enregistrement pas à pas. Le curseur passe de 0 % à 100 % à 0 %, puis restaure sa valeur d'avant le test. Testez `Scythe to Rifle` de Scythe ; testez `Rifle to Compact` avec la première séquence à 100%. Remettez ensuite les deux à 0 %.

![Etape 26: la séquence Bouton Test pendant le pli](../images/crescent-rose/en/26-sequence-test.png){.manual-image-155}

*1 : cliquez sur Test à côté du bouton d'enregistrement. 2 : Surveillez le pli et revenez. Testez Compact avec Scythe to Rifle à 100 %.*

**Ce que vous devriez voir :** La lame s'enroule, les plaques se ferment, la tête se replie le long du récepteur et la perche glisse vers le haut. Puis tout revient.

## H.Formulaires

### Étape 27 — Enregistrer le formulaire

Dans **4. Controls**, avec chaque curseur sur 0, cliquez sur**Save Form**, puis double-cliquez sur la nouvelle entrée de liste pour la nommer `Scythe`. Définissez `Scythe to Rifle` sur `100%` et enregistrez/nommez `Rifle`. Définissez également `Rifle to Compact` sur `100%` et enregistrez/nommez `Compact`. Laissez tous les curseurs articulaires individuels à zéro: les séquences fournissent leur mouvement. Mettre la séquence sélectionnée à sa fin peut armer à nouveau l'enregistrement ; l'enregistrement d'un formulaire n'enregistre pas une autre étape. Choisir `Scythe` et**Go to Form** remet les deux séquences à zéro et efface l'état armé. Aller sur Rifle ou Compact peut armer à nouveau l'enregistrement car la séquence sélectionnée est à 100 % ; ne cliquez pas sur Enregistrer l'étape sauf si vous avez l'intention d'ajouter une autre cible.

![Étape 27 : Enregistrez le formulaire avec chaque curseur à 0](../images/crescent-rose/en/27-save-form.png){.manual-image-155}

*1: Commencez avec les deux séquences et chaque joint à 0. 2: Cliquez sur Enregistrer le formulaire. 3 : Double-cliquez sur la nouvelle entrée de liste et nommez-la Scythe ; répéter pour Rifle et Compact.*

### Étape 28 — Accédez au formulaire

Cliquez sur un formulaire dans la liste, puis cliquez sur **Go to Form**.**Go and Key** fait la même chose et active chaque contrôle de l'image actuelle, c'est ainsi que vous animez la transformation.

![Étape 28 : Fusil sélectionné, accédez au formulaire](../images/crescent-rose/en/28-go-to-form.png){.manual-image-155}

*1 : Sélectionnez le formulaire enregistré. 2 : Cliquez sur Accéder au formulaire. Go and Key insère également des clés d'animation.*

### Étape 29 — Le fusil

![Étape 29: le formulaire Fusil](../images/crescent-rose/en/29-result-rifle.png){.manual-image-155}

*1 : Sélectionnez Fusil. 2 : Cliquez sur Accéder au formulaire. 3 : Vérifiez les pourcentages de séquence par rapport à la pose illustrée.*

### Étape 30 — Compacter

![Étape 30: le formulaire Compact](../images/crescent-rose/en/30-result-compact.png){.manual-image-155}

*1 : Sélectionnez Compacter. 2 : Cliquez sur Accéder au formulaire. 3 : Vérifiez les pourcentages de séquence par rapport à la pose illustrée.*

Revenez à `Scythe` et enregistrez le fichier.

## Ce que tu as construit

|Enregistrer|Os|Ce que ça fait|
|---|---|---|
|15 parties|`MCH-<part>` et `DEF-<part>` |Le maillage de chaque pièce est parent de son os `DEF-` |
|8 charnières, 3 glissières, 1 télescope|`CTRL-<part>` |Les poignées; leurs valeurs sont les curseurs dans **4. Controls** |
|1 piston|`MCH-<part>-aim` et `MCH-<part>-target` |Gardez les deux parties de la jambe de force orientées l'une vers l'autre|
|1 Suivre|aucun|`PlateR` tourne avec `PlateL` |
|2 séquences|`CTRL-SEQ-<name>` |Un curseur chacun|
|3 formulaires|aucun|Valeurs de curseur enregistrées|

L'exemple actualisé a réussi le Rig Validator sans aucun problème signalé. Il a également réussi les contrôles de rechargement avec l'exécution automatique des scripts Python désactivée, y compris chaque contrôle individuel et les trois formulaires.

## Essayez ensuite

- Cochez **Curve** sur `PlateR Follow` et remodelez le mappage dans l'éditeur graphique.
- Conservez une quatrième forme, `Carry`, avec la lame repliée mais la tête haute.
- Saisissez les formulaires sur les cadres avec **Go and Key**, puis exportez les os `DEF-` (voir [VRChat Outils](08-vrchat.md) ).

## Lien d'engrenage

Le Crescent Rose n'a pas de paire d'engrenages, donc cette rig n'a pas de Gear Link. Un Gear Link fait tourner une charnière lorsqu'une autre tourne, selon un rapport de dents : une manivelle et une roue, ou une crémaillère qui transforme la rotation en glissière. Voir [Lien d'engrenage](07-mechanisms.md#gear-link-lien-dengrenage).

## Crédits

Modèle Crescent Rose par amandangm, https://sketchfab.com/3d-models/crecent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0 ; divisé en parties, mis à l'échelle et truqué pour ce didacticiel. Crescent Rose est une conception de Rooster Teeth Productions; il s'agit d'un didacticiel créé par des fans.

[← Contenu](index.md)
