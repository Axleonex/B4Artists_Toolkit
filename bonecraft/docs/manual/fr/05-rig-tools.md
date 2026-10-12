# Outils de rig

[← Contenu](index.md)

Ce chapitre couvre en détail les outils de rigging, d'animation et de poids du BoneCraft. Utilisez-le lorsque vous souhaitez comprendre une fonctionnalité plus en profondeur ou lorsque les guides ne couvrent pas votre situation exacte.

Chaque entrée indique ce que fait l'outil, quand vous l'utiliserez, ses principales commandes et où le trouver. La ligne « Où le trouver » de chaque entrée indique le mode nécessaire pour l'utiliser : par exemple, les commandes de rig en mode Pose, le miroir de poids et le transfert de poids en mode Weight Paint et le Delta Mush en mode objet. Certaines sections restent visibles avec un message indiquant ce qu'il faut sélectionner lorsque leurs outils ne peuvent pas s'exécuter.

Dans la version 9.1, de nombreux outils s'exécutent simultanément et placent leurs options dans le panneau Ajuster la dernière opération. Modifiez ces options immédiatement après le clic, avant d'exécuter une autre opération. Les menus Pose → BoneCraft et Poids → BoneCraft, ainsi que les panneaux de boutons BoneCraft dans les onglets de l'étagère à outils Pose et Poids de Bforartists, offrent des raccourcis vers les opérations courantes. [Commencer](01-start.md#où-trouver-chaque-chose) répertorie ces points d'accès.

---

## Outils d'interface de rig

Ces outils vous aident à gérer l'aspect visuel du travail avec les armatures : quels os sont visibles, comment ils sont organisés et un accès rapide.

---

### Collections d'os

**Ce qu'il fait :** Affiche les collections d'os de votre squelette sous forme de lignes. Cliquez sur le nom d'une collection pour sélectionner ses os ; l'icône en forme d'œil l'affiche ou le masque.

> Une collection d'os est un groupe nommé d'os — par exemple « Contrôles IK », « Os du visage » et « Os de déformation ». Le fait de masquer une collection masque ces os dans la fenêtre, afin que vous puissiez vous concentrer sur une partie de l'ossature.

**Contrôles clés :**
- Chaque ligne : la couleur d'accentuation, **Toggle Collection Visibility** (icône en forme d'œil), le nom de la collection (sélectionne ses os),**Solo Collection** et**Rename Collection Display**, qui définit un nom d'affichage personnalisé pour la ligne. Passez la souris sur un bouton contenant uniquement une icône pour l'identifier grâce à son info-bulle
- **Show All Collections** et**Hide All Collections** (icônes yeux ouverts et fermés au-dessus de la liste) — tout en même temps
- Sections : regroupez plusieurs collections sous un en-tête pliable.

**Où le trouver :** Onglet BoneCraft → Révision → Collections

---

### Signets de Visibilité

**Ce qu'il fait :** Enregistre les collections d'os visibles, afin que vous puissiez basculer simultanément entre les vues enregistrées.

**Exemple d'utilisation :** Vous configurez une vue avec uniquement les os du visage pour le travail d'expression et vous l'enregistrez sous "Visage uniquement". Ensuite, vous montrez tout pour la peinture au poids et vous l'enregistrez sous "Full Rig". Maintenant, un clic permet de basculer entre eux.

**Contrôles clés :** chaque emplacement est une ligne.
- Le nom du signet — cliquez dessus pour appliquer la vue enregistrée
- **Save Bookmark** — enregistre la visibilité actuelle dans l'emplacement ; survolez son icône pour voir l'info-bulle
- L'échantillon de couleur - code couleur le signet
- **Clear Bookmark** et**Remove Bookmark** (icônes de fermeture) : videz l'emplacement ou supprimez un emplacement ajouté
- **Add Bookmark** — ajoute un emplacement

**Signets par défaut :** Bras FK, corps IK, visage uniquement, rig complète

**Où le trouver :** Onglet BoneCraft → Révision → Collections → Signets de visibilité

---

### Panneau rapide par raccourci

**Ce qu'il fait :** Ouvre le panneau de configuration de BoneCraft (collections et signets) sous forme de fenêtre contextuelle là où se trouve votre curseur.

**Comment utiliser :** Appuyez sur**Ctrl+Shift+R** dans la fenêtre 3D. Cliquez en dehors de la fenêtre contextuelle pour la fermer.

**Où le trouver :** le raccourci**Ctrl+Maj+R** dans la fenêtre 3D (il n'a pas de panneau propre)

---

## Outils d'animation

---

### Bibliothèque de Poses

**Ce qu'il fait :** Stocke les poses nommées avec des vignettes que vous pouvez appliquer à votre rig en un seul clic.

**Contrôles clés :**
- **Save** — stocke les positions actuelles des os sous forme de pose nommée, avec une vignette de la fenêtre d'affichage
- **Apply** — accroche les os à la pose enregistrée
- **Blend** — applique la pose à force partielle, mélangée à la position actuelle
- **Mirror** — applique la pose inversée de gauche à droite
- **Delete**,**Rename** et**Category** — gèrent la liste ;**Filter** affiche une catégorie
- **Export** et**Import**  : enregistrer ou charger à partir d'un fichier `.bfpose`

Le mélange s'applique immédiatement. Définissez l'intensité du mélange dans Ajuster la dernière opération après avoir cliqué dessus.

**Où le trouver :** Onglet BoneCraft → Révision → Bibliothèque de poses

---

### Control Picker (sélecteur de contrôles)

**Ce qu'il fait :** Une carte cliquable des commandes de votre rig. Cliquez sur une forme pour sélectionner son os ; le sélecteur met en évidence ce qui est sélectionné.

**Contrôles clés :**
- **Generate Picker** — crée la mise en page à partir de votre rig
- **Edit Layout** — déplacez, redimensionnez et ré-étiquetez les contrôles (**Move Picker Control**,**Resize Picker Control** et**Relabel Picker Control** apparaissent sous forme d'icônes sur la ligne de chaque contrôle) et**Snap** dans une grille ;**Rebuild Layout** le reconstruit
- **Mirror Selection** — sélectionne les commandes en miroir
- **Pop-up Picker** — ouvre le sélecteur dans une fenêtre flottante, qui contient également**Add Selection Set**

**Où le trouver :** Onglet BoneCraft → Révision → Sélecteur de contrôle

---

### Control Layer (couche de contrôle, IK/FK)

Pour une comparaison pratique illustrée, suivez [Testez les poids et utilisez IK/FK](06-rig-builder.md#partie-ctest-des-poids-et-utilisation-du-ikfk).

**Ce qu'il fait :** L'animateur contrôle les membres d'un rig fabriqué par**Build Control Rig**  : basculez un membre entre IK et FK sans que le membre saute, et intégrez l'un dans l'autre sur une plage d'images.

**Contrôles clés :**
- **IK** et**FK**  : changez de membre et placez les nouvelles commandes à l'endroit où se trouve le membre, afin que le coude ou le genou ne saute pas.
- **Bake IK** et**Bake FK**: convertissez l'animation sur une plage d'images en IK ou en FK
- **Pole Follow**,**Pin** et**Lock-Free**, et**Global Rig Scale**, qui conserve les verrous protégés

**Où le trouver :** Onglet BoneCraft → Révision → Couche de contrôle (avec une rig réalisée par**Build Control Rig** sélectionnée ; voir [Constructeur de plates-formes](06-rig-builder.md) )

---

### Outils Rigify

**Ce qu'il fait :** Détecte une rig de contrôle Rigify et connecte le panneau de collecte, les signets et les curseurs de propriétés de BoneCraft aux contrôles standard de Rigify.

> Rigify est le système intégré de Bforartists pour générer des rigs prêtes pour l'animation. Si vous avez construit votre rig avec Rigify, cela connecte l'interface utilisateur de BoneCraft aux commandes IK/FK de Rigify.

**Contrôles clés :**
- **Auto-Enhance** — configure les panneaux BoneCraft pour l'installation Rigify sélectionnée
- **Re-run Enhancement** – les reconstruit à partir de zéro
- **Enable Rigify** est dans Quick Rig ; développez son volet de dépannage pour**Generate Control Rig (active metarig)** (voir [Constructeur de plates-formes](06-rig-builder.md) )
- Propriétés Rigify — les curseurs IK/FK, d'étirement, d'espace parent et de suivi de la tête/du cou de la rig

**Où le trouver :** Onglet BoneCraft → Configuration du gréement → Outils Rigify (et section Propriétés Rigify )

---

### Recibler

**Ce qu'il fait :** Déplace l'animation d'un squelette à un autre, par exemple un clip de capture de mouvement sur votre avatar. Les os sont assortis par leur nom et par leur direction, de sorte que les membres conservent leur orientation ; les clavicules sont légèrement assorties afin que les épaules ne tournent pas trop.

**Contrôles clés :**
- **Import Clip** et**Browse Library**: chargez un clip ou définissez un dossier de bibliothèque ; cliquez sur le nom d'un clip pour le sélectionner
- **Auto-Match Bones** (la coche sur la ligne d'un clip) — associe les os source et cible (la liste Bone Mapping du panneau affiche les paires)
- **Preview** et**Stop Preview** — essayez le résultat
- **Apply** — place le clip sur votre rig

**Où le trouver :** Onglet BoneCraft → Configurer le gréement → Retarget

---

### Clés de forme correctives

**Ce qu'il fait :** Des touches de forme qui s'activent lorsqu'un os atteint un angle, pour corriger le pincement ou l'effondrement dans des poses extrêmes.

**Exemple d'utilisation :** Le coude de votre personnage s'effondre lorsqu'il est complètement plié. Vous sculptez un coude corrigé et le reliez à l'os du bras pour qu'il s'applique automatiquement lorsque le coude se plie.

**Contrôles clés :**
- Nouveau correctif : choisissez le **Shape Key**, le**Driver Bone**, l'axe de rotation, l'angle auquel la forme est entièrement activée et la progression progressive de son fondu, puis**Create Corrective**.
- La liste des correctifs: cliquez sur le nom de la clé de forme d'un correctif pour le sélectionner; **Edit** et**Delete** sous la liste agissent sur celui sélectionné

L'édition démarre à partir des valeurs actuelles du correctif. Modifiez son angle et son atténuation dans Ajuster la dernière opération après avoir cliqué dessus.

**Où le trouver :** Onglet BoneCraft → Peau → Correctifs (le maillage a besoin d'une clé de forme de base)

---

### Outils de Courbe

**Ce qu'il fait :** Outils de raffinement de l'animation pour les images clés et les courbes.

- **Interactive Breakdown** (Répartition ; raccourci**Ctrl+Maj+B** dans la fenêtre 3D) : faites glisser vers la gauche et la droite pour mélanger la pose actuelle entre les images clés les plus proches.
- **Apply Delta** (Delta Mover ; raccourci**Ctrl+Shift+D** dans la fenêtre 3D) — déplace les os sélectionnés d'un décalage exact dans l'espace de l'écran ou dans l'espace mondial.
- **Capture** et**Swap** (courbes tampon) : conservez une copie des courbes et échangez-la avec vos modifications.
- **Smart Bake** — crée une animation basée sur des contraintes sur les clés, en supprimant les clés redondantes (**Tol** définit la quantité)
- **Euler Filter** — corrige les retournements de rotation causés par le verrouillage du cardan
- Poignées tangentes — définissez les types de poignées sur les clés sélectionnées : **Auto**,**Vector**,**Aligned**,**Free** ou**Auto Clamped**.

**Où le trouver :** Onglet BoneCraft → Révision → Outils graphiques

---

## Outils de poids

Ces outils contrôlent la façon dont votre maillage se déforme lorsque les os bougent. Les poids indiquent à chaque partie de votre maillage quels os suivre et dans quelle mesure.

---

### Recalcul automatique des poids d'os

**Ce qu'il fait :** Recalcule les poids d'un maillage à partir de l'installation existante, sans modifier le maillage. Sur les maillages denses, il fonctionne via un maillage proxy plus léger, de sorte qu'il n'échoue pas silencieusement.

**Contrôles clés :** choisissez le maillage et l'armature cibles, puis le mode Corps ou Vêtements. Le corps calcule les poids à partir de l'installation existante ; Les vêtements les transfèrent à partir d'un maillage source correctement pondéré. Définissez la méthode, le mélange et le lissage, le nombre maximum d'influences d'os par sommet, un poids minimum et s'il faut conserver une sauvegarde, puis exécutez**Automatic Bone Weight Recalculation**. Ces paramètres se trouvent au-dessus du bouton. Le raccourci CATS,**Smart Automatic Weights**, ouvre une boîte de dialogue pour le maillage cible, l'armature et le mode, ainsi que le maillage source en mode Vêtements.

**Où le trouver :** Onglet BoneCraft → Skin → Outils de poids

---

### Miroir des poids

**Ce qu'il fait :** Copie les poids d'un côté de votre avatar à l'autre. Indispensable pour les personnages symétriques.

**Contrôles clés :**
- **Mirror All Weights** — reflète chaque groupe d'os sur son côté opposé
- **Mirror Active Weight** — reflète uniquement le groupe d'os actif
- Axe de symétrie et direction du miroir (dans les deux sens, de gauche à droite ou de droite à gauche)
- **Topology Mirror** — associe les sommets par topologie de maillage au lieu de position
- **Search Distance** — quelle distance peuvent avoir deux sommets tout en comptant comme une paire (augmentez-le pour les maillages qui ne sont pas parfaitement symétriques)
- **Select Unmatched** — sélectionne les sommets sans partenaire ;**Normalize Weights** fait ensuite la somme des poids à 1,0

Cliquez d’abord sur un bouton miroir, puis définissez l’axe, la direction, le mode topologique et la distance de recherche dans Ajuster la dernière opération. **Mirror Active Weight** se trouve également dans Poids → BoneCraft et dans l'onglet Étagère à outils de poids.

**Où le trouver :** Onglet BoneCraft, en mode Weight Paint → Weight Mirror

---

### Transfert de poids

**Ce qu'il fait :** Copie les poids d'un maillage source vers le maillage actif. Utilisé pour attacher des vêtements à un corps ou pour déplacer des poids d'un maillage haute résolution vers un maillage inférieur.

**Contrôles clés :**
- Choisissez le maillage source avant de transférer
- Après le clic, définissez la méthode de transfert et le filtre osseux dans Ajuster la dernière opération.
- **Normalize** dans Ajuster la dernière opération : maintient la somme des poids à 1,0
- **Transfer Weights** — l'exécute ; le résultat montre la distance moyenne et maximale, et**Select Problem Vertices** sélectionne les sommets qui correspondent mal

**Où le trouver :** Onglet BoneCraft, en mode Weight Paint → Weight Transfer (également sous Skin → Weight Tools)

---

### Tableau des poids

**Ce qu'il fait :** Affiche les poids exacts du sommet sélectionné pour chaque os et vous permet de définir une valeur précise.

**Comment utiliser :** Sélectionnez un sommet en mode Weight Paint ; le tableau répertorie ses os et ses poids. Cliquez sur l'icône en forme de main sur la rangée d'un os, puis définissez**Weight** dans Ajuster la dernière opération. Ajouter une influence utilise l'os que vous choisissez ; définissez également son nouveau poids dans Ajuster la dernière opération. Avec plusieurs sommets sélectionnés,**Normalize All Vertices** les normalise tous.

**Où le trouver :** Onglet BoneCraft, en mode Weight Paint → Tableau des poids

---

### Remplissage par Inondation

**Ce qu'il fait :** Définit le poids du groupe actif sur les sommets sélectionnés en un seul clic :**Flood to 0.0**,**Flood to 1.0** ou**Flood to Custom**. Après Flood sur Custom, définissez**Value** et**Normalize** dans Ajuster la dernière opération. Le menu et l'étagère Poids appellent les boutons à valeur fixe Flood to Zero et Flood to One.

**Où le trouver :** Onglet BoneCraft → Skin → Outils de poids ; également Poids → BoneCraft et étagère à outils → Poids → BoneCraft

---

### Déformer vs Contrôler

**Ce qu'il fait :** trie les os de la rig en os déformés (ils déplacent le maillage) et os de contrôle (l'animateur les déplace), étiquette les os déformés, les renomme en un nom de déformation et exporte un squelette uniquement déformé.

**Où le trouver :** Onglet BoneCraft, en mode Pose → Déformation vs Contrôle

---

### Delta Mush

**Ce qu'il fait :** Une déformation lissante qui réduit le pincement au niveau des articulations. Le maillage conserve sa forme au repos mais se déforme plus nettement en mouvement.

**Comment utiliser :** Cliquez sur**Add Delta Mush** pour ajouter le modificateur et le lier à la forme restante. Immédiatement après, définissez**Iterations**,**Smooth Strength**,**Pin Borders** et**Only Smooth Deform** dans Ajuster la dernière opération. Une fois le modificateur existant, le panneau affiche**Rebind** et**Remove**, avec un pli Paramètres contenant les itérations du modificateur, la force de lissage et les commandes d'épinglage des bordures.

**Où le trouver :** Onglet BoneCraft, en Mode Objet avec un maillage sélectionné → Delta Mush

---

### Enveloppe par Proximité

**Ce qu'il fait :** Fait en sorte qu'un maillage suive la surface d'un autre, comme une seconde peau. Utile pour les vêtements qui épousent le corps.

**Comment utiliser :** sélectionnez le maillage cible, choisissez un autre**Driver Mesh**, puis cliquez sur**Bind Proximity Wrap**. Maintenez l'armature du conducteur dans sa position de repos lors de la liaison. Le volet Options situé sous le bouton répertorie**Falloff Type** et**Max Distance**  ; dans la version 9.1.2, ces valeurs sont stockées avec la configuration mais ne modifient pas sa liaison Surface Deform. Une fois relié, le panneau affiche**Rebind** et**Unbind**. Dissocier désactive le modificateur dans la fenêtre et le rendu ; cela ne le supprime pas.

**Où le trouver :** Onglet BoneCraft, en Mode Objet avec un maillage sélectionné → Enveloppement de proximité

---

## Contrôles de rig

Ces outils apparaissent dans l'onglet BoneCraft en mode Pose.

---

### Changement d'espace

**Ce qu'il fait :** Modifie l'espace qu'un os suit pendant l'animation. Une main tenant un accessoire peut passer de suivre le corps à rester immobile dans le monde en un seul clic.

**Contrôles clés :**
- **Add Space** et**Remove Space** (icône X sous Gérer les espaces) — les espaces qu'un os peut suivre (Monde, Origine ou un autre os)
- Un bouton par espace, nommé d'après celui-ci ; l'espace actuel est marqué ●. Cliquez sur le bouton d'un autre espace pour y basculer l'os

**Où le trouver :** Onglet BoneCraft, en mode Pose → Space Switch

---

### Spline IK

**Ce qu'il fait :** Fait suivre une courbe à une chaîne d'os. Utilisé pour les queues, les tentacules, les cordes, les cheveux longs et les épines qui nécessitent un mouvement fluide et rapide.

**Comment utiliser :** Activez l'os de départ, puis cliquez sur**Generate Spline IK**. Réglez**Chain Length**,**Curve Resolution**,**Stretch** et**Volume Preservation** dans Ajuster la dernière opération.**Remove Spline IK** supprime la configuration.

**Où le trouver :** Onglet BoneCraft, en mode Pose → Spline IK

---

### Dynamique de Chaîne

**Ce qu'il fait :** Mouvement secondaire de type physique sur une chaîne osseuse : les os sont à la traîne lorsque le parent bouge et rebondissent lorsqu'il s'arrête. Utilisé pour les mèches de cheveux, les queues et les accessoires.

**Comment utiliser :** sélectionnez la chaîne d'os et cliquez sur**Add Chain Dynamics**. Réglez**Stiffness**,**Damping**,**Mass** et**Gravity Scale** dans Ajuster la dernière opération. Le panneau répertorie également les paramètres dans un dossier Paramètres sous l'action. Une fois que la dynamique existe, elle affiche**Bake** et**Remove**. Collision utilise une forme de sphère simplifiée, de sorte que les surfaces concaves peuvent ne pas entrer en collision correctement.

**Où le trouver :** Onglet BoneCraft, en mode Pose → Chain Dynamics

---

### Ruban

**Ce qu'il fait :** Crée un ruban de Bendy Bones — des os qui se courbent et se tordent en douceur — pour les lèvres, les sourcils, les ceintures et autres zones légèrement incurvées.

**Comment utiliser :** Sélectionnez la chaîne osseuse et cliquez sur**Generate Ribbon**, puis définissez**Control Bones** et**Ribbon Width** dans Ajuster la dernière opération.**Remove Ribbon** supprime la configuration.

**Où le trouver :** Onglet BoneCraft, en mode Pose → Ruban

---

### Bibliothèque de Visèmes

**Ce qu'il fait :** Crée et gère des ensembles de visèmes (formes de bouche) liés aux clés de forme et génère des clés de synchronisation labiale à partir du texte. Pour la cartographie des visèmes VRChat, utilisez la cartographie des visèmes VRChat  ; pour générer des visèmes à partir de zéro, utilisez la section CATS Visèmes.

**Contrôles clés :**
- **New Set** et**Delete** — créent ou suppriment un ensemble de visèmes
- Dans chaque ensemble, un bouton par visème (avec une icône de haut-parleur) le prévisualise
- Lip Sync : texte sur touches de visème, avec images par phonème et lissage

**Où le trouver :** Onglet BoneCraft, avec une armature sélectionnée → Bibliothèque Viseme

---

### Clé Pilotée par Ensemble

**Ce qu'il fait :** Lie une valeur à une autre sans expressions Python. Posez le pilote (par exemple un os du sourcil), définissez la valeur pilotée (par exemple une clé de forme "Brow Raised") et enregistrez le point ; BoneCraft construit la courbe du pilote.

**Contrôles clés :**
- **Driver Bone** et**Driver Attribute** — ce qui motive
- **Target Bone** et**Target Attribute** — ce qui est piloté
- **Set Value** et**Record Point** — enregistrent un point sur la courbe
- **Create SDK** — construit le pilote

**Où le trouver :** Onglet BoneCraft, en mode Pose → Définir la clé pilotée

---

### Validateur de Rig

**Ce qu'il fait :** vérifie votre rig par rapport à un ensemble de règles et signale les problèmes : dénomination, os manquants, contraintes brisées, hiérarchie, poids, pilotes nécessitant Python et règles des mécanismes. Les noms d'os avec des tirets (tels que `DEF-upper_arm.L` ) sont transmis.

**Contrôles clés :**
- **Run Validation** — exécute chaque vérification et répertorie les résultats
- **Export Report** — enregistre les résultats dans un fichier

Le Tableau des tâches (onglet BoneCraft → Présentation → Tableau des tâches) affiche une tâche de validateur lorsqu'une vérification échoue.

**Où le trouver :** Onglet BoneCraft → Révision → Rig Validator

---

### Notes de Rig

**Ce qu'il fait :** Notes écrites attachées aux os de la rig : ce que vous avez configuré, des rappels, des notes pour les collaborateurs.

**Contrôles clés :** **Add Note** et**Remove** sur chaque note. Rig Readme affiche les notes de la rig sous forme de page en lecture seule.

**Où le trouver :** Onglet BoneCraft → Présentation → Notes sur l'installation et révision → Lisez-moi sur l'installation

Suivant: [Constructeur de plates-formes](06-rig-builder.md)
