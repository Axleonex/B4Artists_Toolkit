# Constructeur de Rig

[← Sommaire](index.md)

## Construire un nouveau rig

Le Constructeur de Rig crée un nouveau rig pour un personnage. Il se trouve dans son propre onglet **Rig Builder** sur la Tool Shelf de gauche (touche **T**), et toujours dans l'onglet **Scène** de l'éditeur **Propriétés**. Dans une Tool Shelf étroite, il passe à une disposition compacte avec des libellés courts.

---

### Assistant Auto-Rig

**Ce qu'il fait :** un guide pas à pas qui place des marqueurs sur votre maillage et construit à partir d'eux un rig avec ses poids. C'est la façon principale de rigger un personnage à partir de zéro.

Le [guide 1](02-guides-a.md#guide-1--amener-votre-premier-avatar-dans-vrchat) le parcourt étape par étape.

**Étapes :** Sélection du maillage → Type de rig → Marqueurs du corps → Marqueurs des doigts → Marqueurs du visage → Vérification → Génération

**Contrôles principaux :**
- **Démarrer l'auto-rig**, et **Retour**, **Annuler** et **Suivant** en haut et en bas de chaque étape
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

### Quick Rig (rig rapide)

**Ce qu'il fait :** ajoute en un clic une armature toute prête : le Basic Humanoid de BoneCraft (19 os, sans Rigify) ou l'un des métarigs de Rigify. Plus rapide que l'assistant, moins ajusté.

**Contrôles principaux :**
- Le bouton Basic Humanoid, et les métarigs Rigify (**Activer Rigify** d'abord, si Rigify est désactivé)
- Options pour le prochain clic : **Adapter le Rig au Maillage Actif**, poids automatiques, **Ajouter des Contrôleurs IK/FK** et **Pose Initiale**
- **T-Pose** et **Pose A** — changer la pose de repos du rig sélectionné
- **Inspecter les contrôles du rig actif** et **Diagnostiquer le Rig Rapide (afficher dans la console)** — vérifier ce qui a été construit
- **Générer le rig de contrôle (métarig actif)** — avec un métarig Rigify actif, génère son rig de contrôle Rigify

**La bibliothèque d'assets BoneCraft Rigs :** le Basic Humanoid est aussi un asset. Faites-le glisser depuis l'étagère d'assets sur votre personnage. Le rig déposé étant sélectionné, Quick Rig affiche « Dropped rig: fit it to a mesh » (rig déposé : adaptez-le à un maillage) : choisissez le **Mesh** (maillage), indiquez s'il faut l'adapter et le pondérer, puis cliquez sur **Fit Dropped Rig** (adapter le rig déposé).

**Où le trouver :** Rig Builder → Quick Rig

---

### Mannequin

**Ce qu'il fait :** construit une figure humaine simple avec un rig, comme doublure quand vous n'avez pas encore de modèle. C'est seulement un aperçu : remplacez-le par votre propre maillage avant l'usage final.

**Contrôles principaux :**
- **Mannequin rapide** — en construit un aux proportions par défaut
- **Ajouter un mannequin** — en construit un avec les réglages ci-dessous
- **Régénérer** et **Supprimer** — le reconstruire avec de nouveaux réglages, ou le supprimer avec son rig
- **Mode**, **Type de corps** et **Échelle de rayon**, avec d'autres réglages sous Avancé

**Où le trouver :** Rig Builder → Mannequin

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

**Où la trouver :** onglet BoneCraft → Fusion d'Os

Suite : [Mechanisms (mécanismes)](07-mechanisms.md)
