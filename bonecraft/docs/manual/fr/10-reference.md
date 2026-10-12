# Solutions rapides et glossaire

[← Contenu](index.md)

## Index des solutions rapides

Utilisez cette section lorsque quelque chose ne va pas et que vous avez besoin d’une réponse rapide.

|Problème|Où chercher|
|---|---|
|Le téléchargement échoue : les os ne sont pas reconnus|[Guide 4](02-guides-a.md#guide-4-corriger-les-noms-dos-de-votre-avatar) + [VRChat Suppléments de dénomination](08-vrchat.md#vrchat-naming-extras-extras-de-nommage-vrchat) |
|Avatar en pose en T / ne suit pas les mouvements|[Guide 5](02-guides-a.md#guide-5-mapper-votre-avatar-sur-le-système-corporel-de-vrchat) + [Configurer les os humanoïdes](08-vrchat.md#configurer-les-os-humanoïdes) |
|Le maillage se déforme bizarrement / la peau s'étire|[Transfert de poids](05-rig-tools.md#transfert-de-poids) + [Miroir de poids](05-rig-tools.md#miroir-des-poids), ou recalculer avec [Recalcul automatique du poids osseux](05-rig-tools.md#recalcul-automatique-des-poids-dos) |
|Un côté du corps a des poids différents|[Miroir de poids](05-rig-tools.md#miroir-des-poids) |
|Pinces à cheveux passant par la tête|[Guide 6, étape 5](02-guides-a.md#étape-5--ajouter-des-colliders-recommandé) — ajouter des collisionneurs|
|La physique des cheveux ne bouge pas|[Guide 6](02-guides-a.md#guide-6-ajouter-la-physique-des-cheveux) — vérifier la détection de la chaîne et le préréglage PhysBone|
|Pinces à vêtements à travers le corps|[Guide 7](02-guides-a.md#guide-7-attacher-des-vêtements-qui-bougent-avec-votre-corps) — exécutez **Detect Collisions** |
|La synchronisation labiale ne fonctionne pas|[Guide 8](03-guides-b.md#guide-8-configurer-la-synchronisation-labiale) + [VRChat Cartographie des visèmes](08-vrchat.md#vrchat-viseme-mapping-mappage-des-visèmes-vrchat) |
|L'avatar a de très mauvaises performances|[Guide 9](03-guides-b.md#guide-9-améliorer-les-performances-de-votre-avatar) + [Vérifier les performances](08-vrchat.md#vérifier-les-performances) |
|L'importation VRM échoue|[Guide 2, étape 1](02-guides-a.md#étape-1--installer-ladd-on-vrm) — installez le module complémentaire VRM |
|L'importation MMD échoue|[Guide 3, étape 1](02-guides-a.md#étape-1--installer-mmd_tools) — installer mmd_tools|
|Le validateur de rig affiche des erreurs|[Validateur de plate-forme](05-rig-tools.md#validateur-de-rig) — exécutez la validation et suivez les messages|
|Les os ont disparu / je ne vois aucun os|[Collections d'os](05-rig-tools.md#collections-dos) → **Show All Collections** |
|Impossible de trouver les panneaux de BoneCraft |BoneCraft et Rig Builder se trouvent sur l'étagère à outils de gauche (appuyez sur T), CATS sur la barre latérale droite (appuyez sur N) — voir [Où sont les choses](01-start.md#où-trouver-chaque-chose) |
|Je veux un exemple complet de mécanismes|[Tutoriel : Crescent Rose](12-crescent-rose.md) — 8 étapes de préparation et 30 étapes de mécanismes avec captures d'écran, et le fichier fini dans `examples/crescent-rose/` |
|Un onglet est du mauvais côté|Préférences → Modules complémentaires → BoneCraft → Onglets → Gauche ou Droite|
|Les sections BoneCraft sont manquantes dans Propriétés → Scène|Préférences → Modules complémentaires → BoneCraft → Onglets → Propriétés de la scène → Afficher ; le bleu signifie allumé. Vérifiez également les packages d'outils dans Outils|
|Je souhaite masquer BoneCraft dans Propriétés → Scène|Désactivez Propriétés de la scène → Afficher dans Préférences → Onglets. Il laisse les onglets de la fenêtre d'affichage et l'onglet des données d'armature seuls.|
|Un outil s'exécute avant que je puisse choisir ses options|Dans la version 9.1, ajustez ses options immédiatement après dans le panneau Ajuster la dernière opération de la fenêtre, avant d'exécuter une autre opération.|
|Placer des marqueurs de rig ne place pas de marqueur|Démarrez l'assistant de montage automatique, accédez à une étape de marqueur, utilisez le mode objet et cliquez sur le maillage sélectionné de l'assistant — voir [Constructeur de plates-formes](06-rig-builder.md#assistant-auto-rig) |
|Build Mechanism ne sait pas quelles pièces utiliser|Ajoutez d'abord des pièces à partir de la sélection, sélectionnez d'abord l'ossature du mécanisme ou l'une de ses pièces, choisissez le type dans l'en-tête de l'outil, puis cliquez sur la première pièce — voir [Mécanismes](07-mechanisms.md#articulations-et-liens-un-exemple-de-chaque) |
|Exportation bloquée : des os humanoïdes signalés manquants alors qu'ils existent|Exécutez **Auto-Map All**, puis**Fix Humanoid Map** dans la section VRM / VRoid. Si un os requis n'existe pas réellement, l'infrastructure en a besoin en premier : voir [Guide 5](02-guides-a.md#guide-5-mapper-votre-avatar-sur-le-système-corporel-de-vrchat).|
|Le FBX exporté montre des formes ou des tubes d'assistance géants|Gardez **Helper Meshes** désactivé, sauf si vous avez besoin de maillages de contrôle ou de forme personnalisée.|
|Unity ou Unreal importe des matériaux gris|Exportez avec **Embed Textures** activé, puis utilisez les options d'importation/extraction de matériaux de Unity ou l'importation de matériaux FBX d'Unreal.|
|Les poids sont tous sur les mauvais os|Réexécutez Générer l'installation de l'assistant, utilisez [Transfert de poids](05-rig-tools.md#transfert-de-poids) ou **Smart Automatic Weights** dans l'onglet CATS.|
|Deux rigs doivent en faire une|[Guider 11 : Fusionner deux rigs ensemble](03-guides-b.md#guide-11-fusionner-deux-rigs) |
|La forme corrective ne s'allume pas|Vérifiez l'axe et l'angle de l'os dans [Clés de forme correctives](05-rig-tools.md#clés-de-forme-correctives) |
|L'animation semble incorrecte sur une autre rig|[Recibler](05-rig-tools.md#recibler) — vérifiez la cartographie osseuse|
|Un outil CATS avertit « Exécutez d'abord le modèle de correction »|Exécuter le modèle de correctif — [Le pipeline CATS](04-cats-pipeline.md) |
|La bouche se déchire ou se fend en parlant|Le modèle de correctif a été ignoré - réexécution à partir de la phase 1 - [Guide 13, Phase 1](03-guides-b.md#phase-1--corriger-le-modèle) |
|Les yeux de l'avatar restent baissés dans VRChat |Le suivi oculaire a été exécuté avant Fix Model - réexécution à partir de Fix Model - [CATS  : suivi oculaire](09-cats.md#suivi-oculaire) |
|La touche de forme fait exploser le maillage lorsqu'elle est déclenchée|Pose to Shape Key a été exécuté avant Fix Model - réexécution à partir de Fix Model - [CATS  : Clés de pose et de forme](09-cats.md#pose-et-clés-de-forme) |
|L'avatar apparaît à la mauvaise taille dans VRChat |Les transformations ont été appliquées avant la fin du pipeline : réimportez à partir du fichier source et redémarrez à partir de Fix Model|
|Les noms des os sont japonais/chinois/coréen|[CATS  : Traduire les noms d'os](09-cats.md#traduire-les-noms-dos) |
|Avatar n'a pas de synchronisation labiale ni de touches de forme de bouche|[CATS: Visèmes](09-cats.md#visèmes) — génère 15 visèmes à partir de 3 formes de base|
|Un mécanisme affiche "changé à la main"|[Mécanismes](07-mechanisms.md) — utilisez **Keep mine** ou**Restore** |

## Glossaire

**Ajuster la dernière opération :** Le panneau d'affichage permettant de modifier les options de l'opération que vous venez d'exécuter. De nombreux outils BoneCraft 9.1 s'exécutent en premier et proposent leurs options ici ; ajustez-les avant d’exécuter une autre opération.

**Armature:** Bforartists ' mot pour un squelette: un ensemble d'os qui peuvent être posés et animés.

**Forme de mélange :** Voir la clé de forme.

**Os :** Un segment d'un squelette. Les os forment une hiérarchie (parent → enfant) dans laquelle les os enfants suivent leurs parents.

**Collection d'os :** Un groupe nommé d'os. Vous pouvez afficher ou masquer une collection entière à la fois.

**CATS  :** Les outils CATS  : préparation de modèle pour VRChat avec un pipeline guidé (nettoyage, visèmes, eye tracking, transformations). Ils se trouvent dans l'onglet CATS.

**Pipeline CATS  :** L'ordre en six phases des outils CATS  : Corriger le modèle → Atlas des matériaux → Visèmes → Suivi oculaire → Poser à la forme → Appliquer les transformations. Les outils avertissent lorsqu’une phase antérieure dont ils dépendent n’est pas terminée.

**Clé de forme corrective :** Une clé de forme qui s'active lorsqu'un os atteint un angle, pour fixer le maillage dans des poses extrêmes.

**Déformer l'os :** Un os qui déplace le maillage. Tous les os ne se déforment pas; certains ne sont que des contrôles.

**Suivi oculaire :** L'outil CATS qui configure les os de l'œil (`LeftEye`, `RightEye` ) et les contraintes de rotation utilisées par VRChat pour déplacer les yeux.

**FBT (Full Body Tracking) :** Une fonctionnalité VRChat qui suit l'ensemble de votre corps avec du matériel supplémentaire (tel que les Vive Trackers), y compris les hanches et les pieds. Fix FBT ajuste l'os racine pour cela.

**FBX  :** Un format de fichier qui transporte des modèles 3D, des squelettes et des animations entre les programmes. Le format standard pour VRChat.

**Modèle correctif :** Nettoyage du CATS  : sommets en double, géométrie lâche et normales incorrectes. Toujours la première étape CATS.

**FK (Forward Kinematics) :** Pose en faisant tourner tour à tour chaque os d'une chaîne : épaule, puis coude, puis poignet. Naturel pour les poses à corps large.

**IK (Cinématique inverse):** Pose en plaçant le bout d'une chaîne (une main ou un pied); les os entre les deux suivent. Naturel pour un placement précis des mains et des pieds.

**Humanoïde :** Le système d'avatar de VRChat mappe les os aux emplacements standard du corps, de sorte que chaque avatar utilise les mêmes commandes de mouvement.

**Mécanisme :** Plate-forme pour une hélice ou une pièce de machine : une articulation (charnière, glissière, télescope) ou un lien (piston, maillon d'engrenage, suivi), construit à partir d'os et de contraintes ordinaires. Voir [Mécanismes](07-mechanisms.md).

**Mesh :** La surface 3D qui constitue le corps visible de votre avatar.

**MMD (MikuMikuDance) :** Logiciel d'animation 3D gratuit populaire au Japon et dans la communauté des anime. Utilise les fichiers de modèle `.pmx` et les fichiers d'animation `.vmd`.

**Cible de morphing :** Voir la clé de forme.

**Ledger des opérations :** Liste CATS de chaque opération que vous avez exécutée, avec son heure et son résultat.

**PhysBone :** Composant de VRChat qui fait osciller, rebondir et entrer en collision les os. Utilisé pour les cheveux, les queues et les accessoires pendants.

**État du pipeline :** Liste CATS des six phases, avec une coche pour chaque phase effectuée.

**PMX  :** Format de modèle 3D principal de MikuMikuDance.

**Mode Pose :** Le mode de pose et d'animation des os. Sélectionnez l'armature et appuyez sur Ctrl+Tab, ou utilisez la liste déroulante des modes en haut à gauche de la fenêtre.

**Rig / rigging :** Construire un squelette à l'intérieur d'un modèle 3D et y connecter le maillage afin qu'il puisse être posé et animé.

**Clé de forme :** Une version enregistrée d'un maillage dans une position déformée. Les touches de forme se mélangent à différentes forces ; ils déterminent les expressions faciales, la synchronisation labiale et les morphologies corporelles.

**SDK (Software Development Kit) :** Pour VRChat, le VRChat Creator Companion et ses outils Unity pour télécharger des avatars.

**Spline IK  :** Chaîne d'os qui suit une courbe. Utilisé pour les queues, les tentacules, les cheveux longs et les épines.

**Pose en T :** Une pose de référence : debout, les bras tendus sur les côtés.

**Étagère à outils :** Le panneau sur le côté gauche de la vue 3D (appuyez sur T), où se trouvent par défaut les onglets BoneCraft et Rig Builder.

**Sommet :** Un point unique dans l'espace 3D. Les maillages sont constitués de nombreux sommets reliés par des arêtes et des faces.

**Groupe de sommets :** Un ensemble nommé de sommets ; il définit les sommets qu'un os se déplace.

**Viseme :** Une forme de bouche pour un son de parole. VRChat utilise 15 visèmes pour la synchronisation labiale.

**Poids/peinture de poids :** Valeurs de 0,0 à 1,0 qui indiquent la force avec laquelle chaque os déplace chaque sommet. La peinture au poids est le moyen visuel de les ajuster.

**Assistant :** L'assistant de rig automatique du Rig Builder : place des marqueurs sur votre maillage et construit le rig à partir d'eux.

**Os de poids nul :** Un os qui ne bouge aucun sommet. Cela coûte des performances sans changer l’apparence de l’avatar ; Fix Model et l'optimiseur de performances les suppriment.

Suivant: [Quoi de neuf](11-whats-new.md)
