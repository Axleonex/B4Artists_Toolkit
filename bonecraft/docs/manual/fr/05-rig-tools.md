# Outils de rig

Depuis 9.1, de nombreux outils s'exécutent immédiatement ; réglez leurs options dans Adjust Last Operation juste après le clic, avant toute autre opération. Les menus Pose → BoneCraft, Weights → BoneCraft et les panneaux des Tool Shelf natives Pose/Weights proposent les mêmes actions courantes. Voir [Prise en main](01-start.md#où-trouver-chaque-chose). Certains panneaux restent visibles et expliquent la sélection requise.

[← Sommaire](index.md)

Ce chapitre détaille les outils de rigging, d'animation et de poids de BoneCraft. Utilisez-le pour mieux comprendre une fonction, ou quand les guides ne couvrent pas exactement votre situation.

Chaque entrée indique ce que fait l'outil, quand l'utiliser, ses contrôles principaux et où le trouver. Certains outils n'apparaissent que dans un mode donné, et la ligne « Où le trouver » de chaque entrée l'indique : par exemple, les contrôles de rig en Mode Pose, le miroir et le transfert de poids en mode Peinture de poids, et Delta Mush en Mode Objet.

---

## Outils d'interface de rig

Ces outils vous aident à gérer l'aspect visuel du travail avec les armatures : quels os sont visibles, comment ils sont organisés, et un accès rapide.

---

### Collections d'os

**Ce qu'il fait :** affiche les collections d'os de votre squelette sous forme de lignes. Cliquez sur le nom d'une collection pour sélectionner ses os ; l'icône d'œil l'affiche ou la masque.

> Une collection d'os est un groupe d'os nommé, par exemple « IK Controls », « Face Bones » et « Deform Bones ». Masquer une collection masque ces os dans la vue, pour vous concentrer sur une partie du rig.

**Contrôles principaux :**
- Chaque ligne : la couleur d'accent, **Toggle Collection Visibility** (basculer la visibilité ; icône d'œil), le nom de la collection (sélectionne ses os), **Solo Collection** (collection en solo) et **Rename Collection Display** (renommer l'affichage), qui donne un nom d'affichage personnalisé à la ligne
- **Show All Collections** (afficher toutes les collections) et **Hide All Collections** (masquer toutes les collections) (icônes d'œil ouvert et fermé au-dessus de la liste) — tout d'un coup
- Sections — regrouper plusieurs collections sous un en-tête repliable

Survolez une icône sans texte pour lire son infobulle.

**Où le trouver :** onglet BoneCraft → Révision → Collections

---

### Signets de Visibilité

**Ce qu'il fait :** enregistre quelles collections d'os sont visibles, pour passer d'une vue enregistrée à l'autre d'un coup.

**Exemple d'utilisation :** vous préparez une vue avec seulement les os du visage pour travailler les expressions et l'enregistrez sous « Face Only ». Puis vous affichez tout pour la peinture de poids et l'enregistrez sous « Full Rig ». Désormais, un clic passe de l'une à l'autre.

**Contrôles principaux :** chaque emplacement est une ligne.
- Le nom du signet — cliquez dessus pour appliquer la vue enregistrée
- **Save Bookmark** (enregistrer le signet) — enregistre la visibilité actuelle dans l'emplacement
- Le nuancier — donne une couleur au signet
- **Clear Bookmark** (vider le signet) et **Remove Bookmark** (supprimer le signet ; icônes de fermeture) — vident l'emplacement, ou retirent un emplacement ajouté
- **Ajouter un signet** — ajoute un emplacement

**Signets par défaut :** FK Arms, IK Body, Face Only, Full Rig

**Où le trouver :** onglet BoneCraft → Révision → Collections → Signets de Visibilité

---

### Panneau rapide par raccourci

**Ce qu'il fait :** ouvre le panneau de rig de BoneCraft (collections et signets) en fenêtre contextuelle à l'endroit du curseur.

**Comment l'utiliser :** appuyez sur **Ctrl+Shift+R** dans la vue 3D. Cliquez hors de la fenêtre pour la fermer.

**Où le trouver :** le raccourci **Ctrl+Shift+R** dans la vue 3D (il n'a pas de panneau à lui)

---

## Outils d'animation

---

### Bibliothèque de Poses

Blend s'applique immédiatement. Réglez l'intensité dans Adjust Last Operation après le clic.

**Ce qu'elle fait :** stocke des poses nommées avec des vignettes, à appliquer à votre rig en un clic.

**Contrôles principaux :**
- **Sauvegarder** — enregistre la position actuelle des os comme une pose nommée, avec une vignette de la vue
- **Appliquer** — place les os dans la pose enregistrée
- **Mélanger** — applique la pose avec une intensité partielle, mêlée à la position actuelle
- **Miroir** — applique la pose inversée de gauche à droite
- **Supprimer**, **Renommer** et **Catégorie** — gérer la liste ; **Filtre** affiche une seule catégorie
- **Exporter** et **Importer** — enregistrer dans un fichier `.bfpose` ou en charger un

**Où la trouver :** onglet BoneCraft → Révision → Bibliothèque de Poses

---

### Control Picker (sélecteur de contrôles)

**Ce qu'il fait :** une carte cliquable des contrôles de votre rig. Cliquez sur une forme pour sélectionner son os ; le sélecteur met en évidence ce qui est sélectionné.

**Contrôles principaux :**
- **Generate Picker** (générer le sélecteur) — construit la disposition à partir de votre rig
- **Edit Layout** (modifier la disposition) — déplacer, redimensionner et renommer les contrôles (**Move Picker Control** (déplacer le contrôle), **Resize Picker Control** (redimensionner le contrôle) et **Relabel Picker Control** (renommer le contrôle) apparaissent en icônes sur la ligne de chaque contrôle) et les aligner sur une grille avec **Snap** (aimanter) ; **Reconstruire la disposition** la reconstruit
- **Refléter la sélection** — sélectionne les contrôles symétriques
- **Sélecteur flottant** — ouvre le sélecteur dans une fenêtre flottante, qui a aussi **Add Selection Set** (ajouter un ensemble de sélection)

**Où le trouver :** onglet BoneCraft → Révision → Control Picker

---

### Control Layer (couche de contrôle, IK/FK)

Pour une comparaison illustrée, suivez [Vérifier les poids et utiliser IK/FK](06-rig-builder.md#partie-c--vérifier-les-poids-et-utiliser-ikfk).

**Ce qu'il fait :** des contrôles d'animateur pour les membres d'un rig construit par **Construire le rig de contrôle** : basculer un membre entre IK et FK sans qu'il saute, et cuire l'un dans l'autre sur une plage d'images.

**Contrôles principaux :**
- **IK** et **FK** — basculent le membre et calent les nouveaux contrôles là où se trouve le membre, pour que le coude ou le genou ne saute pas
- **Bake IK** (cuire en IK) et **Bake FK** (cuire en FK) — convertissent l'animation en IK ou en FK sur une plage d'images
- **Pole Follow** (suivi du pôle), **Pin** (épingler) et **Lock-Free** (sans verrou), et **Global Rig Scale** (échelle globale du rig), qui garde les verrous protégés

**Où le trouver :** onglet BoneCraft → Révision → Control Layer (avec un rig construit par **Construire le rig de contrôle** sélectionné ; voir [Constructeur de Rig](06-rig-builder.md))

---

### Outils Rigify

**Ce qu'ils font :** détectent un rig de contrôle Rigify et relient le panneau de collections, les signets et les curseurs de propriétés de BoneCraft aux contrôles standard de Rigify.

> Rigify est le système intégré à Bforartists pour générer des rigs prêts à animer. Si vous avez construit votre rig avec Rigify, cela relie l'interface de BoneCraft aux contrôles IK/FK de Rigify.

**Contrôles principaux :**
- **Amélioration automatique** — configure les panneaux de BoneCraft pour le rig Rigify sélectionné
- **Relancer l'Amélioration** — les reconstruit à partir de zéro
- **Enable Rigify** est dans Quick Rig ; dépliez Troubleshooting pour **Generate Control Rig (active metarig)** (voir [Rig Builder](06-rig-builder.md)).
- Propriétés Rigify — les curseurs IK/FK, étirement, espace parent et suivi tête/cou du rig

**Où les trouver :** onglet BoneCraft → Configurer le Rigging → Outils Rigify (et la section Propriétés Rigify)

---

### Recibler

**Ce qu'il fait :** transfère une animation d'un squelette à un autre, par exemple un clip de capture de mouvement sur votre avatar. Les os sont associés par nom et par direction, donc les membres gardent leur orientation ; les clavicules sont associées de façon souple pour que les épaules ne tournent pas trop.

**Contrôles principaux :**
- **Importer un clip** et **Parcourir la bibliothèque** — charger un clip, ou définir un dossier de bibliothèque ; cliquez sur le nom d'un clip pour le sélectionner
- **Auto-Match Bones** (associer les os automatiquement ; la coche sur la ligne d'un clip) — apparie les os source et cible (la liste Mappage des Os du panneau montre les paires)
- **Aperçu** et **Arrêter l'aperçu** — essayer le résultat
- **Appliquer** — cuit le clip sur votre rig

**Où le trouver :** onglet BoneCraft → Configurer le Rigging → Recibler

---

### Clés de forme correctives

Edit reprend les valeurs actuelles du correctif. Réglez angle et atténuation dans Adjust Last Operation après le clic.

**Ce qu'elles font :** des clés de forme qui s'activent quand un os atteint un angle, pour corriger les pincements ou les affaissements dans les poses extrêmes.

**Exemple d'utilisation :** le coude de votre personnage s'affaisse quand il est complètement plié. Vous sculptez un coude corrigé et le reliez à l'os du bras, pour qu'il s'applique automatiquement quand le coude se plie.

**Contrôles principaux :**
- Nouvelle Correction — choisissez la **Clé de Forme**, l'**Os Driver**, l'axe de rotation, l'angle où la forme est pleinement active et la progressivité de son apparition, puis cliquez sur **Créer un correctif**
- La liste des correctifs : cliquez sur le nom de la clé de forme d'un correctif pour le sélectionner ; **Modifier** et **Supprimer**, sous la liste, agissent sur le correctif sélectionné

**Où les trouver :** onglet BoneCraft → Peau → Correctifs (le maillage doit avoir une clé de forme de base)

---

### Outils de Courbe

**Ce qu'ils font :** des outils pour affiner les images clés et les courbes d'animation.

- **Décomposition interactive** (Breakdowner ; raccourci **Ctrl+Shift+B** dans la vue 3D) — glissez à gauche et à droite pour mêler la pose actuelle entre les images clés voisines
- **Appliquer le delta** (Déplaceur Delta ; raccourci **Ctrl+Shift+D** dans la vue 3D) — décale les os sélectionnés d'une valeur exacte dans l'espace écran ou l'espace monde
- **Capturer** et **Échanger** (Courbes en mémoire tampon) — garder une copie des courbes et alterner entre elle et vos modifications
- **Cuisson intelligente** — cuit l'animation pilotée par contraintes en images clés, en abandonnant les clés redondantes (**Tol** règle la quantité)
- **Filtre d'Euler** — corrige les retournements de rotation causés par le blocage de cardan
- Poignées Tangentes — définir le type de poignée des clés sélectionnées : **Auto**, **Vector** (vecteur), **Aligned** (alignée), **Free** (libre) ou **Auto Clamped** (auto bornée)

**Où les trouver :** onglet BoneCraft → Révision → Outils de Courbe

---

## Outils de poids

Ces outils règlent la façon dont votre maillage se déforme quand les os bougent. Les poids indiquent à chaque partie du maillage quels os suivre, et dans quelle mesure.

---

### Recalcul automatique des poids d'os

**Ce qu'il fait :** recalcule les poids d'un maillage à partir du rig existant, sans changer le maillage. Sur les maillages denses, il passe par un maillage proxy plus léger, pour ne pas échouer sans bruit.

**Contrôles principaux :** choisissez maillage cible, armature et mode Body ou Clothing. Body calcule depuis le rig existant ; Clothing transfère depuis un maillage source correctement pondéré. Réglez méthode, mélange, lissage, maximum d'os par sommet, poids minimal et sauvegarde, puis **Automatic Bone Weight Recalculation**. Les réglages précèdent le bouton. Le raccourci CATS **Smart Automatic Weights** ouvre un dialogue pour cible, armature, mode, et source en mode Clothing.

**Où le trouver :** onglet BoneCraft → Peau → Outils de Poids

---

### Miroir des poids

Cliquez d'abord sur le miroir, puis réglez axe, direction, topologie et distance dans Adjust Last Operation. **Mirror Active Weight** est aussi dans Weights → BoneCraft et la Tool Shelf Weights.

**Ce qu'il fait :** copie les poids d'un côté de votre avatar à l'autre. Indispensable pour les personnages symétriques.

**Contrôles principaux :**
- **Miroir de tous les poids** — reflète chaque groupe d'os vers son côté opposé
- **Miroir du poids actif** — reflète seulement le groupe d'os actif
- Axe de symétrie et sens du miroir (dans les deux sens, de gauche à droite, ou de droite à gauche)
- **Miroir de Topologie** — apparie les sommets par la topologie du maillage plutôt que par la position
- **Distance de Recherche** — à quelle distance deux sommets peuvent être et compter encore comme une paire (augmentez-la pour des maillages pas parfaitement symétriques)
- **Sélectionner les Non Correspondants** — sélectionne les sommets sans partenaire ; **Normaliser les Poids** ramène ensuite la somme des poids à 1.0

**Où le trouver :** onglet BoneCraft, en mode Peinture de poids → Miroir des poids

---

### Transfert de poids

**Ce qu'il fait :** copie les poids d'un maillage source vers le maillage actif. Sert à attacher des vêtements à un corps, ou à déplacer des poids d'un maillage haute résolution vers un maillage plus léger.

**Contrôles principaux :**
- Choisissez le maillage source avant le transfert.
- Après clic, méthode et filtre d'os dans Adjust Last Operation.
- **Normalize** dans Adjust Last Operation garde la somme à 1.0.
- **Transfer Weights** lance ; le résultat indique distances moyenne/maximale et **Select Problem Vertices** sélectionne les mauvaises correspondances.

**Où le trouver :** onglet BoneCraft, en mode Peinture de poids → Transfert de poids (aussi sous Peau → Outils de Poids)

---

### Tableau des poids

**Ce qu'il fait :** affiche les poids exacts du sommet sélectionné pour chaque os, pour que vous saisissiez des valeurs précises.

**Comment l'utiliser :** sélectionnez un sommet en Weight Paint ; la table liste ses os et poids. Cliquez la main d'une ligne d'os puis réglez **Weight** dans Adjust Last Operation. Add Influence utilise l'os choisi ; réglez aussi son poids après clic. **Normalize All Vertices** normalise tous les sommets sélectionnés.

**Où le trouver :** onglet BoneCraft, en mode Peinture de poids → Tableau des poids

---

### Remplissage par Inondation

**Ce qu'il fait :** règle le poids du groupe actif sur les sommets sélectionnés : **Flood to 0.0**, **Flood to 1.0**, **Flood to Custom**. Après Custom, réglez **Value** et **Normalize** dans Adjust Last Operation. Menu et étagère Weights nomment les boutons fixes Flood to Zero et Flood to One.

**Où le trouver :** onglet BoneCraft → Peau → Outils de Poids ; Weights → BoneCraft ; Tool Shelf → Weights → BoneCraft

---

### Déformer vs Contrôler

**Ce qu'il fait :** répartit les os du rig entre os de déformation (ils déplacent le maillage) et os de contrôle (l'animateur les déplace), marque les os de déformation, les renomme selon un nommage de déformation, et exporte un squelette de déformation seule.

**Où le trouver :** onglet BoneCraft, en Mode Pose → Déformer vs Contrôler

---

### Delta Mush

**Ce qu'il fait :** une déformation lissante qui réduit les pincements aux articulations. Le maillage garde sa forme au repos mais se déforme plus proprement en mouvement.

**Comment l'utiliser :** **Add Delta Mush** ajoute et lie le modificateur à la forme de repos. Réglez immédiatement **Iterations**, **Smooth Strength**, **Pin Borders**, **Only Smooth Deform** dans Adjust Last Operation. Ensuite le panneau propose **Rebind**, **Remove** et un volet Settings pour itérations, lissage et bords épinglés.

**Où le trouver :** BoneCraft → Skin → Delta Mush (Object Mode; Mesh)

---

### Enveloppe par Proximité

**Ce qu'il fait :** fait suivre à un maillage la surface d'un autre, comme une seconde peau. Utile pour les vêtements qui collent au corps.

**Comment l'utiliser :** sélectionnez le maillage cible, choisissez un autre **Driver Mesh**, puis **Bind Proximity Wrap**. Gardez l'armature pilote en pose de repos lors de la liaison. Options contient **Falloff Type** et **Max Distance** ; en 9.1.2, ces valeurs sont stockées mais ne changent pas la liaison Surface Deform. Une fois lié : **Rebind**, **Unbind**. Unbind désactive le modificateur en vue et au rendu sans le supprimer.

**Où le trouver :** BoneCraft → Skin → Proximity Wrap (Object Mode; Mesh)

---

## Contrôles de rig

Ces outils apparaissent dans l'onglet BoneCraft en Mode Pose.

---

### Changement d'espace

**Ce qu'il fait :** change l'espace qu'un os suit pendant l'animation. Une main qui tient un accessoire peut passer en un clic de « suivre le corps » à « rester immobile dans le monde ».

**Contrôles principaux :**
- **Ajouter un espace** et **Remove Space** (supprimer l'espace ; icône X sous Gérer les espaces) — les espaces qu'un os peut suivre (World, Origin ou un autre os)
- Un bouton par espace, portant son nom ; l'espace actuel est marqué ●. Cliquez sur le bouton d'un autre espace pour y faire passer l'os

**Où le trouver :** onglet BoneCraft, en Mode Pose → Changement d'espace

---

### Spline IK

**Ce qu'il fait :** fait suivre une courbe à une chaîne d'os. Sert pour les queues, tentacules, cordes, cheveux longs et colonnes qui demandent un mouvement fluide et ample.

**Comment l'utiliser :** activez l'os de départ, puis **Generate Spline IK**. Réglez **Chain Length**, **Curve Resolution**, **Stretch**, **Volume Preservation** dans Adjust Last Operation. **Remove Spline IK** retire le montage.

**Où le trouver :** onglet BoneCraft, en Mode Pose → Spline IK

---

### Dynamique de Chaîne

**Ce qu'elle fait :** un mouvement secondaire de type physique sur une chaîne d'os : les os traînent quand le parent bouge et rebondissent quand il s'arrête. Sert pour les mèches de cheveux, les queues et les accessoires.

**Comment l'utiliser :** sélectionnez la chaîne, **Add Chain Dynamics** ; réglez **Stiffness**, **Damping**, **Mass**, **Gravity Scale** dans Adjust Last Operation. Ces paramètres figurent aussi dans Settings sous l'action. Puis **Bake** et **Remove** apparaissent. Collision sphérique simplifiée : surfaces concaves parfois incorrectes.

**Où la trouver :** onglet BoneCraft, en Mode Pose → Dynamique de Chaîne

---

### Ruban

**Ce qu'il fait :** construit un ruban de Bendy Bones (des os qui se courbent et se tordent en douceur) pour les lèvres, les sourcils, les ceintures et d'autres zones souples et courbes.

**Comment l'utiliser :** sélectionnez la chaîne, **Generate Ribbon**, puis **Control Bones** et **Ribbon Width** dans Adjust Last Operation. **Remove Ribbon** retire le montage.

**Où le trouver :** onglet BoneCraft, en Mode Pose → Ruban

---

### Bibliothèque de Visèmes

**Ce qu'elle fait :** crée et gère des ensembles de visèmes (formes de bouche) reliés à des clés de forme, et génère des clés de synchronisation labiale à partir d'un texte. Pour le mappage des visèmes VRChat, utilisez VRChat Viseme Mapping ; pour générer des visèmes à partir de zéro, utilisez la section Visèmes de CATS.

**Contrôles principaux :**
- **Nouveau Jeu** et **Supprimer** — créer ou supprimer un ensemble de visèmes
- Dans chaque ensemble, un bouton par visème (icône de haut-parleur) le prévisualise
- Synchronisation Labiale — du texte vers des clés de visèmes, avec images par phonème et lissage

**Où la trouver :** CATS → Avatar Tools → Viseme Library (Armature); Lip Sync (Pose Mode)

---

### Clé Pilotée par Ensemble

**Ce qu'elle fait :** relie une valeur à une autre sans expressions Python. Posez le pilote (par exemple un os de sourcil), réglez la valeur pilotée (par exemple une clé de forme « Brow Raised ») et enregistrez le point ; BoneCraft construit la courbe du driver.

**Contrôles principaux :**
- **Os Driver** et **Attribut du Driver** — ce qui pilote
- **Os Cible** et **Attribut Cible** — ce qui est piloté
- **Définir la Valeur** et **Enregistrer le Point** — enregistrer un point sur la courbe
- **Créer un SDK** — construit le driver

**Où la trouver :** onglet BoneCraft, en Mode Pose → Clé Pilotée par Ensemble

---

### Validateur de Rig

**Ce qu'il fait :** vérifie votre rig selon un ensemble de règles et signale les problèmes : nommage, os manquants, contraintes cassées, hiérarchie, poids, drivers qui demandent Python, et les règles de Mechanisms. Les noms d'os avec des tirets (comme `DEF-upper_arm.L`) passent.

**Contrôles principaux :**
- **Exécuter la validation** — lance chaque vérification et liste les résultats
- **Export Report** (exporter le rapport) — enregistre les résultats dans un fichier

Le Tableau des tâches (onglet BoneCraft → Vue d'ensemble → Tableau des tâches) affiche une tâche du validateur quand une vérification échoue.

**Où le trouver :** onglet BoneCraft → Révision → Validateur de Rig

---

### Notes de Rig

**Ce qu'elles font :** des notes écrites attachées aux os du rig : ce que vous avez configuré, des rappels, des notes pour vos collaborateurs.

**Contrôles principaux :** **Ajouter une note**, et **Supprimer** sur chaque note. Lisez-moi du Rig affiche les notes du rig en page en lecture seule.

**Où les trouver :** onglet BoneCraft → Vue d'ensemble → Notes de Rig, et Révision → Lisez-moi du Rig

Suite : [Constructeur de Rig](06-rig-builder.md)
