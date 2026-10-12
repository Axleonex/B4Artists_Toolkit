# Solutions rapides et glossaire

[← Sommaire](index.md)

## Index des solutions rapides

Utilisez cette section quand quelque chose s'est mal passé et qu'il vous faut la réponse vite.

| Problème | Où regarder |
|---|---|
| L'envoi échoue — os non reconnus | [Guide 4](02-guides-a.md#guide-4--corriger-les-noms-dos-de-votre-avatar) + [VRChat Naming Extras](08-vrchat.md#vrchat-naming-extras-extras-de-nommage-vrchat) |
| Avatar en T-pose / ne suit pas les mouvements | [Guide 5](02-guides-a.md#guide-5--mapper-votre-avatar-sur-le-système-corporel-de-vrchat) + [Configurer les Os Humanoïdes](08-vrchat.md#configurer-les-os-humanoïdes) |
| Le maillage se déforme bizarrement / la peau s'étire | [Transfert de poids](05-rig-tools.md#transfert-de-poids) + [Miroir des poids](05-rig-tools.md#miroir-des-poids), ou recalculer avec le [Recalcul automatique des poids d'os](05-rig-tools.md#recalcul-automatique-des-poids-dos) |
| Un côté du corps a des poids différents | [Miroir des poids](05-rig-tools.md#miroir-des-poids) |
| Les cheveux traversent la tête | [Guide 6, étape 5](02-guides-a.md#étape-5--ajouter-des-colliders-recommandé) — ajouter des colliders |
| La physique des cheveux ne bouge pas | [Guide 6](02-guides-a.md#guide-6--ajouter-la-physique-des-cheveux) — vérifier la détection des chaînes et le préréglage PhysBone |
| Les vêtements traversent le corps | [Guide 7](02-guides-a.md#guide-7--attacher-des-vêtements-qui-bougent-avec-votre-corps) — lancer **Détecter les collisions** |
| La synchronisation labiale ne marche pas | [Guide 8](03-guides-b.md#guide-8--configurer-la-synchronisation-labiale) + [VRChat Viseme Mapping](08-vrchat.md#vrchat-viseme-mapping-mappage-des-visèmes-vrchat) |
| L'avatar est en performance Very Poor | [Guide 9](03-guides-b.md#guide-9--améliorer-les-performances-de-votre-avatar) + [Vérifier les Performances](08-vrchat.md#vérifier-les-performances) |
| L'import VRM échoue | [Guide 2, étape 1](02-guides-a.md#étape-1--installer-ladd-on-vrm) — installer l'add-on VRM |
| L'import MMD échoue | [Guide 3, étape 1](02-guides-a.md#étape-1--installer-mmd_tools) — installer mmd_tools |
| Le validateur de rig affiche des erreurs | [Validateur de Rig](05-rig-tools.md#validateur-de-rig) — lancer la validation et suivre les messages |
| Des os ont disparu / aucun os visible | [Collections d'os](05-rig-tools.md#collections-dos) → **Show All Collections** (afficher toutes les collections) |
| Impossible de trouver les panneaux de BoneCraft | BoneCraft et Rig Builder sont sur la Tool Shelf de gauche (touche T), CATS dans la barre latérale de droite (touche N) — voir [Où trouver chaque chose](01-start.md#où-trouver-chaque-chose) |
| Un onglet est du mauvais côté | Préférences → Add-ons → BoneCraft → Tabs → Left (gauche) ou Right (droite) |
| Export bloqué : os humanoïdes signalés manquants alors qu'ils existent | Lancer **Tout mapper automatiquement**, puis **Fix Humanoid Map** (corriger la carte humanoïde) dans la vérification de la section VRM / VRoid. Si un os obligatoire n'existe vraiment pas, le rig doit d'abord l'avoir : voir le [guide 5](02-guides-a.md#guide-5--mapper-votre-avatar-sur-le-système-corporel-de-vrchat) |
| Le FBX exporté montre des formes d'aide ou des tubes géants | Laisser **Helper Meshes** (maillages d'aide) désactivé, sauf si vous avez besoin de maillages de contrôle ou de formes personnalisées |
| Unity ou Unreal importe des matériaux gris | Exporter avec **Embed Textures** (intégrer les textures) activé, puis utiliser les options d'import/extraction des matériaux d'Unity ou l'import de matériaux FBX d'Unreal |
| Les poids sont tous sur les mauvais os | Relancer **Générer le rig** de l'assistant, utiliser le [Transfert de poids](05-rig-tools.md#transfert-de-poids), ou **Smart Automatic Weights** (poids automatiques intelligents) dans l'onglet CATS |
| Deux rigs doivent n'en faire qu'un | [Guide 11 : fusionner deux rigs](03-guides-b.md#guide-11--fusionner-deux-rigs) |
| Une forme corrective ne s'active pas | Vérifier l'axe de l'os et l'angle dans [Clés de forme correctives](05-rig-tools.md#clés-de-forme-correctives) |
| L'animation semble fausse sur un autre rig | [Recibler](05-rig-tools.md#recibler) — vérifier le mappage des os |
| Un outil CATS avertit « Run Fix Model first » | Lancer **Corriger le modèle** — [Le pipeline CATS](04-cats-pipeline.md) |
| La bouche se déchire ou se fend quand l'avatar parle | **Corriger le modèle** a été sauté — relancer depuis la phase 1 — [Guide 13, phase 1](03-guides-b.md#phase-1--corriger-le-modèle) |
| Les yeux de l'avatar restent bloqués vers le bas dans VRChat | Le suivi oculaire a été lancé avant **Corriger le modèle** — relancer depuis **Corriger le modèle** — [CATS : Suivi Oculaire](09-cats.md#suivi-oculaire) |
| Une clé de forme fait exploser le maillage quand elle est déclenchée | **Pose en Clé de Forme** a été lancé avant **Corriger le modèle** — relancer depuis **Corriger le modèle** — [CATS : Pose et Clés de Forme](09-cats.md#pose-et-clés-de-forme) |
| L'avatar apparaît à la mauvaise taille dans VRChat | Les transformations ont été appliquées avant la fin du pipeline — réimporter depuis le fichier source et recommencer à **Corriger le modèle** |
| Les noms d'os sont en japonais / chinois / coréen | [CATS : Traduire les Noms d'Os](09-cats.md#traduire-les-noms-dos) |
| L'avatar n'a ni synchronisation labiale ni clés de forme de bouche | [CATS : Visèmes](09-cats.md#visèmes) — générer 15 visèmes à partir de 3 formes de base |
| Un mécanisme affiche « changed by hand » | [Mechanisms (mécanismes)](07-mechanisms.md) — utiliser **Keep mine** (garder la mienne) ou **Restaurer** |

## Glossaire

**Armature :** le mot de Bforartists pour un squelette : un ensemble d'os qu'on peut poser et animer.

**Blend shape :** voir Clé de forme.

**Os (Bone) :** un segment d'un squelette. Les os forment une hiérarchie (parent → enfant) dans laquelle les os enfants suivent leurs parents.

**Collection d'os (Bone collection) :** un groupe d'os nommé. Vous pouvez afficher ou masquer une collection entière d'un coup.

**CATS :** les outils CATS : la préparation de modèles pour VRChat avec un pipeline guidé (nettoyage, visèmes, suivi oculaire, transformations). Ils sont dans l'onglet CATS.

**Pipeline CATS (CATS pipeline) :** l'ordre en six phases des outils CATS : Corriger le modèle → Atlas de Matériaux → Visèmes → Suivi Oculaire → Pose en Clé de Forme → Appliquer les transformations. Les outils avertissent quand une phase précédente dont ils dépendent n'est pas faite.

**Clé de forme corrective (Corrective shape key) :** une clé de forme qui s'active quand un os atteint un angle, pour corriger le maillage dans les poses extrêmes.

**Os de déformation (Deform bone) :** un os qui déplace le maillage. Tous les os ne déforment pas ; certains ne sont que des contrôles.

**Suivi oculaire (Eye tracking) :** l'outil CATS qui configure les os des yeux (`LeftEye`, `RightEye`) et les contraintes de rotation que VRChat utilise pour bouger les yeux.

**FBT (Full Body Tracking) :** une fonction de VRChat qui suit tout votre corps avec du matériel supplémentaire (comme des Vive Trackers), y compris les hanches et les pieds. **Corriger le FBT** ajuste l'os racine pour cela.

**FBX :** un format de fichier qui transporte des modèles 3D, des squelettes et des animations entre programmes. Le format standard pour VRChat.

**Corriger le modèle (Fix Model) :** le nettoyage CATS : sommets en double, géométrie isolée et mauvaises normales. Toujours la première étape CATS.

**FK (cinématique directe, Forward Kinematics) :** poser en faisant tourner chaque os d'une chaîne tour à tour : épaule, puis coude, puis poignet. Naturel pour les grandes poses du corps.

**IK (cinématique inverse, Inverse Kinematics) :** poser en plaçant l'extrémité d'une chaîne (une main ou un pied) ; les os intermédiaires suivent. Naturel pour placer précisément mains et pieds.

**Humanoïde (Humanoid) :** le système d'avatar de VRChat qui mappe les os sur des emplacements standard du corps, pour que chaque avatar utilise les mêmes contrôles de mouvement.

**Mécanisme (Mechanism) :** un rig pour un accessoire ou une pièce de machine : une articulation (Hinge, Slide, Telescope) ou un lien (Piston, Gear Link, Follow), construit à partir d'os et de contraintes ordinaires. Voir [Mechanisms (mécanismes)](07-mechanisms.md).

**Maillage (Mesh) :** la surface 3D qui forme le corps visible de votre avatar.

**MMD (MikuMikuDance) :** un logiciel d'animation 3D gratuit populaire au Japon et dans la communauté anime. Il utilise des fichiers de modèle `.pmx` et des fichiers d'animation `.vmd`.

**Morph target :** voir Clé de forme.

**Registre des Opérations (Operation Ledger) :** la liste CATS de chaque opération lancée, avec son heure et son résultat.

**PhysBone :** le composant de VRChat qui fait balancer, rebondir et entrer en collision les os. Sert pour les cheveux, les queues et les accessoires pendants.

**État du Pipeline (Pipeline Status) :** la liste CATS des six phases, avec une coche pour chaque phase terminée.

**PMX :** le principal format de modèle 3D de MikuMikuDance.

**Mode Pose (Pose Mode) :** le mode pour poser et animer les os. Sélectionnez l'armature et appuyez sur Ctrl+Tab, ou utilisez le menu déroulant des modes en haut à gauche de la vue.

**Rig / rigging :** construire un squelette dans un modèle 3D et y relier le maillage pour qu'on puisse le poser et l'animer.

**Clé de forme (Shape key) :** une version enregistrée d'un maillage dans une position déformée. Les clés de forme se mélangent à différentes intensités ; elles pilotent les expressions faciales, la synchronisation labiale et les morphes du corps.

**SDK (Software Development Kit) :** pour VRChat, le VRChat Creator Companion et ses outils Unity pour envoyer des avatars.

**Spline IK :** une chaîne d'os qui suit une courbe. Sert pour les queues, tentacules, cheveux longs et colonnes.

**T-pose :** une pose de référence : debout, bras tendus sur les côtés.

**Tool Shelf :** le panneau du côté gauche de la vue 3D (touche T), où se trouvent par défaut les onglets BoneCraft et Rig Builder.

**Sommet (Vertex) :** un seul point dans l'espace 3D. Les maillages sont faits de nombreux sommets reliés par des arêtes et des faces.

**Groupe de sommets (Vertex group) :** un ensemble de sommets nommé ; il définit quels sommets un os déplace.

**Visème (Viseme) :** une forme de bouche pour un son de parole. VRChat utilise 15 visèmes pour la synchronisation labiale.

**Poids / peinture de poids (Weight / weight painting) :** des valeurs de 0.0 à 1.0 qui disent avec quelle force chaque os déplace chaque sommet. La peinture de poids est la façon visuelle de les ajuster.

**Assistant (Wizard) :** l'Assistant Auto-Rig du Constructeur de Rig : il place des marqueurs sur votre maillage et construit le rig à partir d'eux.

**Os de poids zéro (Zero-weight bone) :** un os qui ne déplace aucun sommet. Il coûte en performances sans changer l'apparence de l'avatar ; **Corriger le modèle** et l'optimiseur de performances les retirent.

Suite : [Nouveautés](11-whats-new.md)
