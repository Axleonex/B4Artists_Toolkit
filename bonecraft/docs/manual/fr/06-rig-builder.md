# Constructeur de Rig

[← Sommaire](index.md)

Pour une démonstration commentée des deux types de rigs, voir le [parcours IK/FK et son fichier d'exercice](https://github.com/Axleonex/B4Artists_Toolkit/blob/main/bonecraft/docs/tutorials/ikfk-beginner.md).

## Construire un nouveau rig

Le Constructeur de Rig crée un nouveau rig pour un personnage. Il se trouve dans son propre onglet **Rig Builder** sur la Tool Shelf de gauche (touche **T**), et  dans l'onglet **Scène** de l'éditeur **Propriétés**. Dans une Tool Shelf étroite, il passe à une disposition compacte avec des libellés courts. Les panneaux Scène sont visibles quand Preferences → Tabs → Scene Properties → Show est activé. Masquer un onglet de la vue 3D ne masque pas cette copie. Auto-Rig Wizard vient en premier, puis Quick Rig et Mannequin. Le menu Add → Armature de la vue 3D permet aussi de démarrer l'assistant ou d'ajouter un Quick Rig.

---

### Assistant Auto-Rig

**Ce qu'il fait :** un guide pas à pas qui place des marqueurs sur votre maillage et construit à partir d'eux un rig avec ses poids. C'est la façon principale de rigger un personnage à partir de zéro.

Le [guide 1](02-guides-a.md#guide-1--amener-votre-premier-avatar-dans-vrchat) le parcourt étape par étape.

**Étapes :** Sélection du maillage → Type de rig → Marqueurs du corps → Marqueurs des doigts → Marqueurs du visage → Vérification → Génération

**Contrôles principaux :**
- **Start Auto-Rig** ouvre l'assistant. **Back** et **Cancel** sont en haut ; **Next** est en bas des étapes de maillage, type de rig et marqueurs. Review propose **Generate Rig** à la place de Next ; la dernière étape propose **Close Wizard**
- La liste des maillages (cliquez sur votre maillage), puis le type de rig : **Body + Face** (corps et visage), **Body Only** (corps seul) ou **Face Only** (visage seul, pour une armature existante)
- **Detect Markers** (détecter les marqueurs ; dans Smart Detection) — suit les membres dans le maillage et place chaque marqueur du corps avec un indice de confiance ; **Accept High** (accepter la confiance élevée) garde les sûrs et **Reset Low** (réinitialiser la faible confiance) efface les douteux
- **Deviner les marqueurs depuis le maillage** et **Deviner la précision** (corps), **Deviner les marqueurs de doigts** (les marqueurs des doigts sont placés d'après la forme de la main) et **Deviner les marqueurs faciaux**
- Détail des Doigts — le nombre de doigts à construire, de « 0 — No Fingers » à « 5 — Full Human Hand »
- La ligne de chaque marqueur : **Place Marker** (placer le marqueur ; icône de flèche), **Confirm Marker** (confirmer le marqueur ; coche) et **Reset Marker** (réinitialiser le marqueur ; flèche circulaire) ; **Toggle Symmetry** (basculer la symétrie ; première icône) sur les marqueurs gauches et droits
- **Mirror L to R** (refléter de gauche à droite) et **Mirror R to L** (refléter de droite à gauche) — copient les marqueurs confirmés de part et d'autre de l'axe central
- **Confirmer tous placés** — confirme chaque marqueur placé de l'étape
- **Générer le rig** — construit le rig à partir des marqueurs confirmés ; puis, à la dernière étape, **Construire le rig de contrôle** (voir plus bas) et **Fermer l'assistant**

**Ce que construit Générer le rig :**
- Un rig de corps avec les segments de colonne et de cou choisis, et des bras et jambes IK/FK, IK seul ou FK seul (l'option **Cinématique**)
- Les os des doigts pour le nombre de doigts choisi
- Pour **Body + Face** : un rig facial, avec des formes de contrôle quand **Générer des formes de contrôle** est activé
- Les poids de peau à la qualité choisie. Les maillages denses sont pondérés via un maillage proxy plus léger, si bien qu'un personnage de 678 000 sommets prend environ une minute au lieu d'échouer sans bruit.

**Construire le rig de contrôle :** l'étape de vérification affiche aussi **Twist Bones** (os de torsion), **Skirt Bones** (os de jupe), **Face Controls** (contrôles faciaux) et **Joint Correctives** (correctifs d'articulation). Générer le rig ne les applique pas. Ils appartiennent au rig de contrôle pour les moteurs (os de torsion, os de jupe qui suivent les jambes, contrôles de visée des yeux et de clignement, et clés de forme correctives d'articulation). Après Générer le rig, la dernière étape propose **Construire le rig de contrôle**, qui construit ce rig sur l'armature générée avec les options choisies. Cliquez dessus avant **Fermer l'assistant**, car fermer l'assistant remet ses options à zéro. Le panneau Control Layer (Outils de rig) n'apparaît que sur un rig construit ainsi.

**Où le trouver :** Rig Builder → Assistant Auto-Rig

---

**Placer plusieurs marqueurs dans la vue 3D :** démarrez l'assistant et atteignez une étape de marqueurs corporels, de doigts ou faciaux. En Object Mode, activez Place Rig Markers dans la barre d'outils. Son en-tête indique le prochain marqueur non confirmé, les verrouillages d'axes et la symétrie. Cliquez sur le maillage de l'assistant pour placer et confirmer le marqueur. La symétrie suit les réglages de l'assistant ; les boutons Place individuels restent utilisables. Quand l'étape est terminée, cliquez sur **Next**. Un clic ailleurs ne place aucun marqueur.

---

### Quick Rig (rig rapide)

**Ce qu'il fait :** ajoute en un clic une armature prête : Basic Humanoid de BoneCraft (19 os, sans Rigify) ou un métarig Rigify. Plus rapide que l'assistant, moins personnalisé.

**Contrôles principaux :**
- Basic Humanoid et les métarigs Rigify (**Enable Rigify** d'abord si désactivé).
- Cliquez pour ajouter immédiatement, puis réglez adaptation au maillage, poids automatiques, **Add IK/FK Controllers** et **Initial Pose** dans Adjust Last Operation.
- **T-Pose** et **A-Pose** changent la pose de repos du rig sélectionné.
- Troubleshooting propose **Diagnose Quick Rig (print to console)** ; pour une armature autre qu'un métarig, aussi **Inspect Active Rig Controls**.
- Pour un métarig Rigify actif, **Generate Control Rig (active metarig)** remplace Inspect Active Rig Controls et génère le rig de contrôle Rigify.

**Catalogue de départ BoneCraft Rigs :** les neuf rigs fournis partagent le catalogue **Starter Rigs** de l'étagère native d'assets en bas. Ouvrez le menu des catalogues à gauche, choisissez **All** pour les bibliothèques et activez une fois **Starter Rigs** pour ajouter son onglet. Sélectionnez-le pour parcourir les rigs. **Add → Armature → Starter Rig Catalog** ouvre le sélecteur qui gère les dépendances, l'adaptation et l'ajout.

Basic Humanoid n'a pas besoin de Rigify. Les autres vignettes portent **Rigify**. Si Rigify est inactif, choisir ou déposer un de ces rigs propose **Enable Rigify & Add Rig** et Cancel. Accepter active Rigify installé et ajoute le rig choisi ; annuler n'ajoute rien. Quick Rig permet aussi d'activer Rigify ; le menu contextuel d'asset du sélecteur propose Enable Rigify si nécessaire. Les commandes de départ en haut à gauche de la vue 3D ont été retirées en 9.2.5. Une dépendance absente ou un préréglage indisponible dans votre version produit une explication sans ajouter de remplacement.

Cliquez sur une vignette ou glissez-la dans la vue 3D. Avec un maillage sélectionné, le rig s'y adapte ; poids et génération de commandes sont désactivés au départ. Réglez-les ensuite dans **Adjust Last Operation**. Sans maillage sélectionné, sélectionnez le nouveau rig, choisissez le **Mesh** dans Quick Rig, puis **Fit Dropped Rig**. L'adaptation change l'échelle et la position du squelette : vérifiez et corrigez les articulations avant les commandes ou les poids. Déposer hors de la vue 3D, Esc ou clic droit annule sans rien ajouter.

**Où le trouver :** Rig Builder → Quick Rig ; Add → Armature → Quick Rig ajoute aussi ces rigs.

---

### Mannequin

**Ce qu'il fait :** construit un maillage d'aperçu autour d'un rig existant pour examiner les déformations sans personnage final. Sélectionnez d'abord l'armature ou un maillage qui lui est parenté. Sans rig, ajoutez-en un avec Quick Rig. Remplacez cet aperçu par votre propre maillage avant l'utilisation finale.

**Contrôles principaux :**
- **Quick Mannequin** utilise des valeurs fixes et remplace l'ancien mannequin de ce rig.
- **Add Mannequin** utilise les réglages de scène et remplace le mannequin existant par défaut. Replace Existing est dans Adjust Last Operation après le clic.
- **Regenerate** reconstruit l'aperçu selon ses réglages sauvegardés.
- **Remove** supprime le mannequin en conservant l'armature.
- Options sous les boutons contient **Mode**, **Body Type**, densité et **Radius Scale** ; Advanced contient échelles régionales et sortie. Après modification des réglages de scène, recliquez sur **Add Mannequin**.

**Où le trouver :** Rig Builder → Mannequin

---

## Atelier illustré du mannequin

<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--atelier-illustré-du-mannequin"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--partie-"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--partie-"] + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

Suivez dans l'ordre [A — Simple Human vers mannequin](#partie-a--simple-human-vers-mannequin), [B — mannequin sans rig avec Auto-Rig](#partie-b--mannequin-sans-rig-avec-auto-rig) et [C — vérifier les poids et utiliser IK/FK](#partie-c--vérifier-les-poids-et-utiliser-ikfk). Chaque étape numérotée comporte une capture réelle ; les chiffres rouges correspondent à la légende. Captures réalisées avec **BoneCraft 9.1.2** dans `Bforartists 5.2.0`. Les panneaux et raccourcis de Blender peuvent différer : les noms des commandes font référence.

Cet exercice crée un aperçu en capsules pour apprendre le rigging. Tête, mains et torse sont provisoires, pas un personnage fini. Commencez dans un nouveau fichier et conservez les deux sauvegardes pour répéter la conversion sans perdre le métarig initial.

Les deux sauvegardes sont dans `examples/mannequin/` : `SimpleHuman_Mannequin.blend` contient le résultat neutre de A ; `Mannequin_AutoRig.blend` contient l'exemple terminé et posé de C, avec ses poids corrigés.

### Partie A : Simple Human vers mannequin



#### A1. Activer Rigify

Dans une nouvelle scène, ouvrez **Scene Properties → Rig Builder → Quick Rig**. Si les préréglages Rigify sont indisponibles, cliquez sur **Enable Rigify**. Cet atelier utilise le métarig Rigify `Simple Human` ; **BoneCraft Basic Humanoid (19 bones)** est un autre préréglage.

![A1. Activer Rigify](../images/rig-builder/en/a01-enable-rigify.png)

*1 — Scene Properties. 2 — Enable Rigify.*

#### A2. Ajouter Simple Human

Cliquez sur `Simple Human` sous Quick Rig : vous obtenez un métarig modifiable, pas encore un maillage. Cette version comporte 29 os.

![A2. Ajouter Simple Human](../images/rig-builder/en/a02-simple-human.png)

*1 — Préréglage Simple Human.*

#### A3. Examiner le métarig

Placez le pointeur dans la vue 3D et appuyez sur `Numpad 1` pour la vue orthographique de face. Vérifiez que tout le squelette est visible ; ajustez le cadrage avec la molette. Le métarig peut démarrer en Pose Mode.

![A3. Examiner le métarig](../images/rig-builder/en/a03-metarig.png)

*1 — Vue de face. 2 — Squelette Simple Human.*

#### A4. Revenir en Object Mode

Dans le menu des modes de la vue 3D, choisissez **Object Mode**. Gardez `SimpleHumanArmature` sélectionné. Revenez dans ce mode avant de modifier la pose de repos ou de générer le mannequin.

![A4. Revenir en Object Mode](../images/rig-builder/en/a04-object-mode.png)

*1 — Menu des modes. 2 — Object Mode.*

#### A5. Utiliser une pose en T

Dans Quick Rig, cliquez sur **T-Pose** : les bras s'étendent horizontalement. Pour un corps personnalisé, ajustez d'abord le métarig en Edit Mode ; gardez les articulations symétriques pour cet exercice.

![A5. Utiliser une pose en T](../images/rig-builder/en/a05-t-pose.png)

*1 — Commande T-Pose.*

#### A6. Générer le mannequin

Dépliez **Mannequin → Options**. Choisissez `Mode: Universal`, `Body Type: Neutral`, **Medium** et `Radius Scale: 1.00`. Dans Advanced, laissez les échelles régionales à 1.00 ; choisissez `Joined (non-manifold)`, **Flat colour** et **Joint Smoothing**. Laissez Unified Volume désactivé. Cliquez ensuite sur **Add Mannequin**. La capture montre le résultat en capsules. Add utilise les options actuelles ; Regenerate reprend les réglages sauvegardés du mannequin.

![A6. Générer le mannequin](../images/rig-builder/en/a06-final-settings.png)

*1 — Add Mannequin. 2 — Universal et réglages du corps. 3 — Sortie Joined et lissage.*

#### A7. Essayer une pose d'os

Sélectionnez l'armature, passez en **Pose Mode** et cliquez sur l'avant-bras gauche du personnage (à votre droite en vue de face). Faites-le légèrement tourner avec Rotate : le mannequin suit. Cet aperçu pondéré utilise le métarig ; il ne possède pas encore les commandes d'animation de C.

![A7. Essayer une pose d'os](../images/rig-builder/en/a07-select-forearm.png)

*1 — Pose Mode. 2 — Avant-bras sélectionné et gizmo de transformation.*

#### A8. Restaurer et sauvegarder l'aperçu

Pointeur dans la vue 3D, sélectionnez tous les os de pose. Avec **F3**, cherchez `Clear Pose Transforms` et choisissez **All**. Vérifiez le retour en T-pose. Faites **File → Save As** sous `SimpleHuman_Mannequin.blend` et conservez cette sauvegarde.

![A8. Restaurer et sauvegarder l'aperçu](../images/rig-builder/en/a09-clear-pose.png)

*1 — Recherche Clear Pose Transforms. 2 — All réinitialise les os de pose sélectionnés.*

### Partie B : mannequin sans rig avec Auto-Rig



#### B1. Sélectionner le maillage du mannequin

Reprenez la sauvegarde neutre de A. En **Object Mode**, sélectionnez `SimpleHumanArmature_Mannequin` dans l'Outliner. Nous allons retirer volontairement son rig avant l'assistant. Sauvegardez sous un autre nom pour préserver A.

![B1. Sélectionner le maillage du mannequin](../images/rig-builder/en/b01-select-mesh.png)

*1 — Sélectionnez le maillage, pas l'armature.*

#### B2. Convertir l'aperçu en maillage

Seul le mannequin étant sélectionné, cherchez `Convert Mesh` avec **F3** et exécutez la commande. Elle conserve la géométrie neutre visible et retire le modificateur Armature. Le mannequin doit avoir retrouvé sa T-pose.

![B2. Convertir l'aperçu en maillage](../images/rig-builder/en/b02-convert-mesh.png)

*1 — Commande Convert Mesh.*

#### B3. Retirer le parent

Appuyez sur **Alt+P**, puis choisissez `Clear and Keep Transformation`. Le maillage se détache de l'ancien métarig sans bouger.

![B3. Retirer le parent](../images/rig-builder/en/b03-clear-parent.png)

*1 — Clear and Keep Transformation.*

#### B4. Supprimer les anciens poids

Ouvrez **Object Data Properties → Vertex Groups**. Dans le menu de la liste, choisissez `Delete All Groups`. Ces groupes appartiennent à l'ancien métarig ; l'assistant en créera de nouveaux. Réservez cette suppression à ce maillage d'entraînement jetable.

![B4. Supprimer les anciens poids](../images/rig-builder/en/b04-clear-groups.png)

*1 — Menu Vertex Groups. 2 — Delete All Groups.*

#### B5. Vérifier le mannequin sans rig

Masquez `SimpleHumanArmature` avec l'œil de l'Outliner. Le mannequin doit rester visible, sans modificateur Armature ni groupe de sommets. C'est l'entrée sans rig. BoneCraft 9.1.2 produit les mannequins à partir d'une armature ; détacher cet aperçu fournit le maillage d'exercice sans rig.

![B5. Vérifier le mannequin sans rig](../images/rig-builder/en/b05-rigless-check.png)

*1 — Masquez l'ancien métarig. 2 — Pile de modificateurs vide.*

#### B6. Afficher l'onglet Rig Builder dans la vue 3D

Ouvrez **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Activez **Rig Builder**, choisissez **Left** et fermez Preferences. Pointeur dans la vue 3D, appuyez sur **T** si la Tool Shelf gauche est masquée. Placez les marqueurs depuis cet onglet : dans l'hôte 9.1.2 testé, Place Marker lancé depuis Scene Properties n'acceptait pas les clics dans la vue 3D.

![B6. Afficher l'onglet Rig Builder dans la vue 3D](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — Activez Rig Builder. 2 — Placement dans la Tool Shelf gauche.*

#### B7. Démarrer Auto-Rig

Le mannequin sans rig étant sélectionné, cliquez sur **Start Auto-Rig**. La capture montre le bouton équivalent de Scene Properties ; la même commande figure en haut de l'onglet Rig Builder activé précédemment.

![B7. Démarrer Auto-Rig](../images/rig-builder/en/b06-start-wizard.png)

*1 — Start Auto-Rig.*

#### B8. Choisir le maillage d'entrée

Dans `Select Mesh`, choisissez le mannequin et vérifiez la confirmation de sélection, puis **Next**. Ne choisissez pas un widget ou un autre aperçu.

![B8. Choisir le maillage d'entrée](../images/rig-builder/en/b07-select-input.png)

*1 — Mannequin d'entrée. 2 — Next.*

#### B9. Choisir un corps avec les deux méthodes

Choisissez **Body Only** et `Kinematics: IK + FK`. Gardez **Generate Control Shapes** activé, puis **Next**. Ce mannequin en capsules n'a pas de topologie faciale : Body + Face est inutile.

![B9. Choisir un corps avec les deux méthodes](../images/rig-builder/en/b08-body-ikfk.png)

*1 — Body Only. 2 — IK + FK. 3 — Next.*

#### B10. Détecter les premiers marqueurs corporels

Dans Body Markers, cliquez sur **Detect Markers** sous Smart Detection. Ces estimations sont un point de départ. Gardez **Mirror Symmetry** activé pour ce mannequin symétrique ; vérifiez chaque estimation avant de l'accepter.

![B10. Détecter les premiers marqueurs corporels](../images/rig-builder/en/b09-detect-markers.png)

*1 — Detect Markers. 2 — Mirror Symmetry.*

#### B11. Examiner les positions détectées

Vérifiez sommet de la tête, base du cou, bassin, poignets et chevilles sur le maillage. Cet aperçu segmenté entraîne plusieurs estimations peu fiables. Corrigez les repères principaux et ceux de précision facultatifs avant la génération. Les indices de confiance concernent la détection initiale ; la coche verte au début de la ligne confirme le placement actuel.

![B11. Examiner les positions détectées](../images/rig-builder/en/b10-review-markers.png)

*1 — Résumé des indices de confiance. 2 — Lignes des marqueurs corporels.*

#### B12. Placer un poignet sur le maillage

Dans l'onglet **Rig Builder** de la vue 3D, cliquez sur la pipette **Place Marker** de Wrist Left, puis sur la surface du poignet. Si le marqueur est déjà confirmé, réinitialisez d'abord sa ligne pour retrouver le bouton de placement. En vue de face, le poignet gauche du personnage est à droite de l'écran.

![B12. Placer un poignet sur le maillage](../images/rig-builder/en/b11-place-wrist.png)

*1 — Placement Wrist Left. 2 — Cliquez sur la surface du poignet.*

#### B13. Vérifier le poignet symétrique et les chevilles

Les deux poignets doivent avoir une coche verte et des coordonnées X opposées. Recommencez pour `Ankle Left` ; la symétrie place Ankle Right. Placez les chevilles à l'articulation, pas aux orteils. Vérifiez sur le maillage sans recopier les coordonnées d'exemple sur un personnage d'une autre taille.

![B13. Vérifier le poignet symétrique et les chevilles](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — Paire de poignets confirmée. 2 — Poignet symétrique sur le maillage.*

#### B14. Affiner épaules et coudes

Dans Precision Markers, réinitialisez et placez `Shoulder Left` au pivot du bras, puis `Elbow Left` dans l'espace du coude. Confirmez leurs partenaires symétriques. Le poignet reste à l'extrémité de l'avant-bras côté main. Ces points définissent la chaîne du bras : corrigez toute estimation sur une mauvaise capsule.

![B14. Affiner épaules et coudes](../images/rig-builder/en/b13-arm-precision.png)

*1 — Lignes épaule et coude. 2 — Épaule. 3 — Coude.*

#### B15. Affiner hanches et genoux

Placez `Hip Left` en haut de la cuisse et `Knee Left` entre cuisse et tibia. Vérifiez les partenaires symétriques. Gardez le bassin sur l'axe central, entre les hanches.

![B15. Affiner hanches et genoux](../images/rig-builder/en/b14-leg-precision.png)

*1 — Lignes hanche et genou. 2 — Surface de la hanche. 3 — Espace du genou.*

#### B16. Vérifier profondeur et orteils de profil

Pointeur dans la vue 3D, appuyez sur `Numpad 3`. Vérifiez les repères en vue orthographique droite, en plus de la face. Placez `Toe Left` près de l'avant du pied et vérifiez son partenaire symétrique. Un marqueur correct de face peut être trop avancé ou reculé.

![B16. Vérifier profondeur et orteils de profil](../images/rig-builder/en/b15-side-depth.png)

*1 — Vue orthographique droite. 2 — Ligne d'orteil. 3 — Surface du pied.*

#### B17. Placer les talons

Réinitialisez le talon mal estimé, puis placez `Heel Left` près de l'arrière du pied en vue de profil. Vérifiez Heel Right. Bien que facultatifs, ces marqueurs laissés à zéro déclenchaient un avertissement de proximité dans la version testée ; les placer sur les pieds l'a supprimé.

![B17. Placer les talons](../images/rig-builder/en/b16-place-heels.png)

*1 — Paire de talons confirmée. 2 — Position du talon.*

#### B18. Confirmer et continuer

Revérifiez sommet de tête, base du cou, bassin et tous les repères appariés. Cliquez sur **Confirm All Placed**, puis **Next**. Les coches vertes indiquent la confirmation ; les anciennes étiquettes REVIEW/ADJUST peuvent rester visibles en 9.1.2.

![B18. Confirmer et continuer](../images/rig-builder/en/b17-confirm-markers.png)

*1 — Confirm All Placed. 2 — Next.*

#### B19. Ignorer les doigts sur ce maillage

Choisissez `0 — No Fingers`, puis **Next**. Ce mannequin a des capsules de mains sans géométrie de doigts. Sur une vraie main, choisissez le nombre approprié et placez les marqueurs.

![B19. Ignorer les doigts sur ce maillage](../images/rig-builder/en/b18-no-fingers.png)

*1 — No Fingers. 2 — Next.*

#### B20. Vérifier et générer

Attendez **All checks passed**. Pour cet exercice : **IK + FK**, formes de contrôle activées, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers`, **Game Ready**. Désactivez Twist Bones, Skirt Bones, Preserve Volume et Joint Correctives. Cliquez sur **Generate Rig**. Ces réglages conviennent à ce mannequin d'apprentissage, pas à tous les exports.

![B20. Vérifier et générer](../images/rig-builder/en/b19-review-generate.png)

*1 — Vérification des marqueurs. 2 — Réglages de génération. 3 — Generate Rig.*

#### B21. Construire les commandes d'animation

Après génération, cliquez sur **Build Control Rig**. Generate Rig fournit corps et poids ; Build Control Rig ajoute la couche de commandes utilisée ci-dessous. Ne recliquez pas sur Quick Mannequin : le maillage d'entrée existe déjà, même si le panneau final propose un mannequin.

![B21. Construire les commandes d'animation](../images/rig-builder/en/b20-build-controls.png)

*1 — Build Control Rig.*

#### B22. Terminer l'assistant

Attendez le message de fin du rig de contrôle, puis **Close Wizard**. La nouvelle armature apparaît dans l'Outliner. Gardez l'ancien métarig Simple Human masqué. Le nouveau rig doit déformer le maillage : voir des os ne suffit pas.

![B22. Terminer l'assistant](../images/rig-builder/en/b21-close-wizard.png)

*1 — Bouton de construction désormais désactivé. 2 — Close Wizard.*

### Partie C : vérifier les poids et utiliser IK/FK

Dans la version testée, le nom d'objet de l'armature générée est le suivant (à utiliser dans l'Outliner et l'outil de poids) :

```text
BoneForge_Rig
```

`FK (Forward Kinematics)`, cinématique directe : les rotations suivent la hiérarchie, bras puis avant-bras puis main. Adaptée aux mouvements amples et libres. `IK (Inverse Kinematics)`, cinématique inverse : déplacez une cible de poignet ou cheville, le solveur plie la chaîne pour l'atteindre. Adaptée aux pieds ancrés et aux mains sur une surface.

| Tâche | Commande | À vérifier |
|---|---|---|
| Balancer un bras | Épaule et coude FK | Les enfants suivent leur parent |
| Placer une main | Cible de poignet IK | Épaule et coude visent la cible |
| Ancrer un pied | Cible de cheville IK de cette jambe | Bougez le corps sans déplacer la cible accessible |
| Orienter coude ou genou | Pôle IK | Le pôle fixe la direction de flexion, pas la position de poignet/cheville |
| Changer de méthode | Boutons IK/FK du membre | Vérifiez la pose alignée avant d'insérer des clés |

Nous comparons un bras dans les deux modes. Chaque membre a son propre commutateur. `Bake IK / Bake FK` convertit l'animation ; changer une pose ne remplace pas la cuisson ou les clés d'animation. Voir [Couche de contrôle](05-rig-tools.md#control-layer-couche-de-contrôle-ikfk).

#### C1. Ouvrir la couche de contrôle

Sélectionnez **l'armature générée**, passez en **Pose Mode** et ouvrez **BoneCraft → Review → Control Layer**. Chaque bras et jambe dispose de son commutateur IK/FK. Commencez par **arm-L → FK**. Les côtés sont ceux du personnage : arm-L est à votre droite de face.

![C1. Ouvrir la couche de contrôle](../images/rig-builder/en/c02-control-layer.png)

*1 — Pose Mode. 2 — Control Layer et commutateur arm-L.*

#### C2. Afficher les commandes d'animation

Ouvrez **Object Data Properties → Bone Collections** de l'armature. Les étoiles Solo de `Controls` et **FK** isolent leurs formes. Activez **In Front** sous Viewport Display si le maillage les masque. Ajoutez ensuite **IK** pour les cibles. Cette liste native fonctionne aussi si le panneau Collections de BoneCraft ne s'affiche pas dans cet hôte.

![C2. Afficher les commandes d'animation](../images/rig-builder/en/c03-visible-controls.png)

*1 — Étoiles Solo Controls et FK. 2 — In Front.*

#### C3. Sélectionner la commande FK de l'avant-bras

De face, cliquez sur le cercle du coude gauche du personnage. Vérifiez le nom **forearm.fk-L**. Cette commande tourne autour du coude ; celle de l'épaule tournerait le bras et ses enfants.

![C3. Sélectionner la commande FK de l'avant-bras](../images/rig-builder/en/c04-select-fk.png)

*1 — Commande forearm.fk-L sélectionnée. 2 — FK actif pour arm-L.*

#### C4. Tourner et examiner la déformation

Tournez la commande FK autour de **Y** global d'environ `−45°` dans cet exemple de face. Utilisez Rotate ; avec le clavier Bforartists illustré : **Ctrl+E**, **Y**, saisissez **-45**, puis **Enter**. Le raccourci Blender par défaut est **R**. La capture montre volontairement le défaut initial : la capsule du bras s'incline avec l'avant-bras. Ce rig n'est pas terminé.

![C4. Tourner et examiner la déformation](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — Mouvement incorrect du bras pendant le test FK.*

#### C5. Recalculer les poids du mannequin

Si le test échoue, passez en **Object Mode**, sélectionnez le maillage, puis **BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**. Mesh to Reweight : mannequin ; Existing Armature : **armature générée**. Choisissez **Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0`, `Minimum Weight: 0.001`. Gardez **Keep Weight Backup** activé, puis lancez **Automatic Bone Weight Recalculation**. Cela a réparé l'aperçu segmenté dans la version testée.

![C5. Recalculer les poids du mannequin](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — Maillage et armature. 2 — Bone Heat. 3 — Remplacement et sauvegarde. 4 — Recalcul.*

#### C6. Vérifier la flexion FK corrigée

Resélectionnez l'armature générée, puis **Pose Mode**. Le bras doit rester horizontal de l'épaule au coude, tandis que l'avant-bras monte depuis le coude. L'objet masqué `WEIGHTS_BACKUP_…` conserve les anciens poids. Testez aussi les autres membres avant d'animer votre personnage : un squelette généré ne prouve pas la qualité des poids.

![C6. Vérifier la flexion FK corrigée](../images/rig-builder/en/c05-fk-result.png)

*1 — Le bras reste en place. 2 — L'avant-bras plie au coude.*

#### C7. Passer le même bras en IK

Cliquez sur **arm-L → IK** : la cible s'aligne sur la pose actuelle, le bras doit rester levé. Ajoutez **IK** aux collections Solo visibles si les cibles sont masquées. Le changement sélectionne les commandes motrices ; il n'enregistre pas d'animation.

![C7. Passer le même bras en IK](../images/rig-builder/en/c06-switch-ik.png)

*1 — Commutateur arm-L IK. 2 — Pose conservée.*

#### C8. Sélectionner la cible IK du poignet

Cliquez sur la commande du poignet et vérifiez **forearm.ik-L**. Malgré son nom d'avant-bras, c'est la cible terminale du bras. Déplacez-la pour placer la main : le solveur ajuste épaule et coude.

![C8. Sélectionner la cible IK du poignet](../images/rig-builder/en/c07-select-ik.png)

*1 — Cible du poignet sélectionnée. 2 — Nom de sélection.*

#### C9. Déplacer la cible et comparer

Déplacez légèrement le poignet vers l'intérieur sur **X** global. Ici, `−0.15 m` change nettement la flexion. Clavier illustré : **Ctrl+W**, **X**, `-0.15`, **Enter**, ou flèche X de Move. Le raccourci Blender par défaut est **G**. Comparez au FK : l'extrémité mène, les deux segments suivent. Gardez la cible à portée du bras.

![C9. Déplacer la cible et comparer](../images/rig-builder/en/c08-move-ik.png)

*1 — Extrémité au poignet. 2 — Réaction de la chaîne. 3 — Déplacement X d'exemple.*

#### C10. Revenir en FK et sauvegarder

Cliquez sur **arm-L → FK** : les commandes FK s'alignent sur la pose IK. Vérifiez l'absence de saut du maillage, puis **File → Save As** sous `Mannequin_AutoRig.blend`. La capture montre l'exemple sauvegardé en FK. Pour une copie neutre, mettez les quatre membres en FK, sélectionnez toutes les commandes de pose visibles, puis **F3 → Clear Pose Transforms → All**, comme en A ; sauvegardez sous un autre nom.

![C10. Revenir en FK et sauvegarder](../images/rig-builder/en/c10-save-complete.png)

*1 — FK de nouveau actif. 2 — Pose conservée. 3 — Nom du fichier.*

**Vérification finale :** aperçu du métarig original conservé, mannequin sans rig détaché, nouveau corps et commandes générés, poids corrigés et rotation FK comparée au déplacement d'une cible IK. Gardez ce rig comme exemple ; remplacez l'aperçu par une géométrie de personnage adaptée à la production.

---

### Reciblage d'animation

Le transfert d'une animation d'un squelette à un autre est traité dans [Outils de rig : Recibler](05-rig-tools.md#recibler).

---

## Fusion d'Os

**Ce qu'elle fait :** combine deux armatures en une seule (par exemple un rig de corps et un rig de vêtement ou de cheveux) en gardant tous les poids.

Le [guide 11](03-guides-b.md#guide-11--fusionner-deux-rigs) la parcourt étape par étape.

**Les trois stades :**
1. Périmètre — choisir les deux armatures et examiner leurs différences
2. Renommage — résoudre les conflits de noms et marquer les nouveaux os
3. Fusion — prévisualiser, puis fusionner

**Contrôles principaux :**
- **Base** — l'armature qui reste ; l'autre fusionne dedans puis est masquée
- **Analyze** (analyser) — compare les deux squelettes ; **Acknowledge Scope — Proceed to Rename** (valider le périmètre — passer au renommage) ouvre le stade 2
- **Normalize Both Armatures** (normaliser les deux armatures) — renomme les os standard des deux rigs selon une même norme de nommage (Mixamo Prefixed, Mixamo Stripped ou personnalisée)
- **Auto-Propose Renames** (proposer des renommages automatiquement) — suggère des noms pour les os propres au rig fusionné
- **Apply Rename** (appliquer le renommage) — renomme une entrée (une étape d'annulation) ; **Apply Batch Pattern** (appliquer un motif par lot) en renomme beaucoup avec un motif (avec `{bone}`, `{side}` et `{index}`)
- **Mark as Unique** (marquer comme unique) — garde un os comme nouvel os au lieu de le fusionner
- **Verify Rename — Proceed to Merge** (vérifier le renommage — passer à la fusion) — ouvre le stade 3
- **Run Merge Preview** (lancer l'aperçu de fusion) — indique ce que ferait la fusion, sans rien modifier
- **Fusionner les Armatures** — sauvegarde les deux armatures et les fusionne

**Où la trouver :** BoneCraft → Setup Rigging → Bone Merge

Suite : [Mechanisms (mécanismes)](07-mechanisms.md)
