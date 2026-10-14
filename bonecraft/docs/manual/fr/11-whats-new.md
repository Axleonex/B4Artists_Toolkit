# Nouveautés

[← Sommaire](index.md)

Les plus récentes d'abord.

## 9.2.2 — Interface actuelle

Les onglets sélectionnent un groupe. Setup Rigging, Skin, Review, Avatar Tools et Facial sont des sections à déplier dans ces onglets, pas des onglets distincts. Les chemins ci-dessous conservent les labels anglais ; leur traduction dépend du réglage Language.

- Bone Merge → BoneCraft → Setup Rigging
- Delta Mush / Proximity Wrap → BoneCraft → Skin
- Viseme Library / Lip Sync → CATS → Avatar Tools
- VRChat Viseme Mapping / Face Tracking → CATS → VRChat Tools → Facial

## 9.1.2 (octobre 2026)

- **Interrupteur Propriétés de la scène :** Préférences > Onglets a une nouvelle ligne Propriétés de la scène. Son bouton Afficher (bleu quand il est actif) affiche ou masque toutes les sections de BoneCraft dans Propriétés > onglet Scène (Constructeur de Rig, Mécanismes, CATS, VRChat, Import / Export) sans désactiver l'extension. Il est actif au départ et ne touche ni aux onglets de la vue 3D ni à l'onglet Armature.

## 9.1.1 (octobre 2026)

- **Des icônes plus claires :** chaque icône n'a plus qu'un seul sens, partout. Une soixantaine de boutons ont une icône Bforartists mieux adaptée (par exemple Appliquer toutes les transformations, Décimer, Normaliser les noms, Traduire, Fusionner, Séparer, Mélanger la pose et Synchronisation labiale), et un bouton montre la même icône dans tous les panneaux.
- **Des panneaux plus calmes :** les titres et les textes fixes n'ont plus d'icônes de thème. Les messages qui signalent un état montrent l'icône d'information, d'avertissement ou de validation.
- **Une grille d'icônes lisible :** chaque bouton des onglets Pose et Poids de la barre d'outils a sa propre icône, donc une barre étroite reste lisible.

## 9.1.0 (octobre 2026)

- **Les outils là où Bforartists met les siens :** des entrées BoneCraft dans les menus Ajouter → Armature, Pose, Poids et Objet, et un panneau de boutons BoneCraft dans les onglets Pose et Poids de la barre d'outils de Bforartists.
- **Agir d'abord, régler ensuite :** Rig rapide, Ajuster le rig déposé, les outils de poids, Ruban, Spline IK, Delta Mush et les outils d'os de CATS s'exécutent tout de suite avec les dernières valeurs utilisées ; on les règle ensuite dans le panneau Ajuster la dernière opération. Moins de fenêtres « êtes-vous sûr ».
- **Les actions d'abord, les options repliées :** les panneaux montrent d'abord leurs boutons, puis leurs réglages dans un volet replié dessous. Les réglages ressemblent à des réglages (cases à cocher, jamais des boutons), et les en-têtes de panneau n'ont pas d'icône.
- **Outils gestuels :** Placer les marqueurs du rig (cliquer sur le maillage pour placer le marqueur suivant de l'Assistant d'Auto-Rig) et Construire un mécanisme (cliquer sur une pièce pour commencer une articulation ou un lien) sont dans la barre d'outils de la vue.
- **Infobulles :** chaque opérateur et chaque option s'explique.
- **Montrer, ne pas cacher :** les sections restent visibles et disent quoi sélectionner quand le rig a disparu, l'Assistant d'Auto-Rig vient en premier dans Rig Builder, et les panneaux latéraux s'ouvrent assez larges pour être lus.
- **Corrections :** Générer Spline IK fonctionne à nouveau ; Ajouter une influence utilise l'os choisi ; les aperçus de visèmes utilisent leur jeu.

## 9.0.0 (octobre 2026)

- **Mechanisms :** une nouvelle section de l'onglet BoneCraft (et de l'onglet Scène des Propriétés) qui rigge les accessoires et les machines : Hinge, Slide, Telescope, Piston, Gear Link, Follow et Sequence, construits par étapes guidées et vérifiés avec Test. BoneCraft n'écrase jamais une retouche manuelle : vous choisissez **Keep mine** pour la garder ou **Restaurer** pour reconstruire. Voir [Mechanisms (mécanismes)](07-mechanisms.md).
- **Côtés des onglets :** chaque onglet de la vue peut se placer sur la Tool Shelf de gauche ou dans la barre latérale de droite (Préférences → Tabs → Left / Right). BoneCraft et Rig Builder commencent à gauche, CATS à droite.
- **Constructeur de Rig :** toujours dans l'onglet Scène des Propriétés, plus son propre onglet dans la vue avec une disposition compacte pour une Tool Shelf étroite. Un rig Basic Humanoid est livré dans la bibliothèque d'assets BoneCraft Rigs ; Fit Dropped Rig adapte un rig déposé depuis l'étagère d'assets.
- **Onglet CATS :** Importer / Exporter est passé dans l'onglet CATS. CATS, VRChat et Importer / Exporter sont aussi toujours dans l'onglet Scène.
- **Show Helpers :** une seule préférence affiche ou masque le texte pédagogique de BoneCraft ; le Mode Compact en est le raccourci.
- **Validateur de Rig :** les noms d'os avec des tirets passent ; les drivers n'avertissent que pour les expressions qui demandent Python ; les rigs Mechanisms sont vérifiés aussi. La tâche du validateur dans le Tableau des tâches est de nouveau signalée.
- **Nom :** l'add-on s'appelle BoneCraft.

## 8.9.x (septembre–octobre 2026)

- **8.9.6 :** toute la pièce de la robe suit les os de jupe (plus de traversée des hanches) ; correctifs des coins de bouche à mâchoire ouverte, avec lèvres collantes.
- **8.9.5 :** bascule IK/FK du coude sans saut ; détection symétrique des épaules ; les marqueurs des yeux ne s'aimantent plus ; le Control Picker montre la sélection ; coins de bouche plus ronds ; une correction de robe sur la cuisse ; clavicules de reciblage assouplies ; export en T-pose.
- **8.9.4 :** genoux plus ronds (les correctifs remplacent Preserve Volume) ; clés de contact pour les flexions profondes ; un fondu sur la jointure de l'épaule.
- **8.9.3 :** os de jupe à deux segments qui suivent les jambes et sont poussés par elles.
- **8.9.2 :** clignement par clés de forme (pas de plis de paupières) ; une ouverture de bouche ovale.
- **8.9.1 :** skinning bien plus rapide sur les maillages denses (678 000 sommets : de 232 s à 57 s) ; chaleur des os calculée via un maillage proxy plus léger au lieu d'échouer sans bruit.
- **8.9.0 :** clés de forme correctives d'articulation ; contrôles faciaux (visée des yeux, clignement, suivi des lèvres) ; vêtements qui se plient avec les articulations.
- Aussi dans la 8.9 : recalcul automatique des poids d'os, et une sélection d'atlas plus claire.

## 8.7–8.8 (septembre 2026)

- **8.8.0 :** le panneau de reciblage fonctionne sur les hôtes Blender 5 ; marqueurs des doigts placés d'après la forme de la main ; étirement IK jusqu'à la peau ; une option Preserve Volume ; une correction de liaison Delta Mush.
- **8.7.0 :** un rig de contrôle intégré ; détection des articulations par suivi des membres ; reciblage aligné sur les directions ; os de torsion.

## 8.5–8.6 (juillet 2026)

- **8.6.1–8.6.3 :** Atlas de Matériaux : diagnostics des tuiles après la cuisson ; transparence MToon vérifiée par rapport à l'alpha réel de la texture et conservée pendant la mise en atlas ; meilleur partitionnement des matériaux mixtes.
- **8.5.5–8.5.10 :** matériaux VRM / MToon : le mode alpha est respecté, l'alpha fonctionne sur les hôtes Blender 5, pas de saturation de l'émission, diagnostics en magenta et noms d'atlas sûrs.
- **8.5.4 :** le mappage humanoïde est relu correctement ; aide pour Naming Prep.
- **8.5.2–8.5.3 :** import d'un téléchargement VRoid (.zip) ; une carte de transfert pour les projets VRoid.
- **8.5.1 :** export FBX qui conserve les blend shapes.

## Versions antérieures

**8.5.0 :** Smart Combine fait désormais de `atlas_uv` l'UV0 d'export par défaut après la cuisson. La carte UV source d'avant l'atlas est retirée du maillage d'atlas généré, sauf si **Keep Source UV Maps** (garder les cartes UV source) est activé dans les réglages avancés. Les contrôles CATS / Material Combiner / dérivés d'UVToolkit sont désormais partagés avec la version Blender ouverte ; l'exclusivité B4Artists reste sur les systèmes de rigging de production, de contrôle, de reciblage/export et de publication réservés à B4Artists.

La 8.5.0 met aussi à jour le flux d'export et de validation. Les exports VRChat, VRM, MMD et Unreal exposent désormais des contrôles de dossier et de nom de fichier dans les panneaux de BoneCraft, au lieu de vous obliger à vous fier aux valeurs par défaut du navigateur de fichiers de Blender. Les exports FBX VRChat/Unity et Unreal utilisent par défaut **Embed Textures** pour faciliter l'import des matériaux, tandis que l'export VRChat laisse les maillages d'aide et de formes de contrôle hors du FBX, sauf si **Helper Meshes** est activé. Le panneau VRM inclut maintenant **Vérifier maintenant** ainsi que **Fix Humanoid Map**, qui peut réparer avant l'export un mappage d'alias humanoïde périmé, sans renommer vos os.

**8.4.5 :** Smart Combine force désormais les textures source à échantillonner l'UV d'avant l'atlas conservée pendant la cuisson, valide le maillage d'atlas généré avant de masquer les originaux, et réaffecte toutes les faces de l'atlas à l'emplacement de matériau final de l'atlas, pour éviter des morceaux de robe ou de vêtement gris ou brouillés.

**8.4.4 :** le Combinateur d'atlas de matériaux ajoute des contrôles d'inspection de qualité avant la cuisson : diagnostics de shaders/matériaux, étiquettes de rôle des textures, marqueurs de sources dupliquées/partagées, tailles forcées par matériau, préréglages d'empaquetage, cuissons facultatives en sorties Normal/Emission/Roughness, et blocages préalables de l'empaquetage des canaux Metallic/ORM tant que cette voie n'est pas vérifiée.

**8.4.3 :** le Combinateur d'atlas de matériaux inclut des méthodes d'empaquetage UV au choix dans le flux Atlas de Matériaux existant. Il comprend Smart Pack, Grid Pack, Seeded Variation, Oriented Pack, Fit 0-1 Bounds, Advanced Variation et Rotation Step, avec les détails de la méthode UV consignés dans le rapport de débogage et le registre de cuisson.

**8.4.2 :** le Combinateur d'atlas de matériaux cible désormais l'UV de l'atlas généré pendant la cuisson, tandis que les nœuds de texture source copiés lisent explicitement l'UV d'avant l'atlas. Cela corrige les résultats d'atlas cassés de robes/vêtements, causés par des textures source et un atlas cuit qui échantillonnaient des cartes UV différentes. Les lignes de matériaux et de textures sélectionnables de la 8.4.1 restent disponibles.

**7.1.3 (nettoyage des libellés de préférences) :** deux interrupteurs des préférences de l'add-on ont été renommés pour correspondre désormais à l'onglet de barre latérale qu'ils contrôlent. « VRChat Avatar Tools » s'appelle maintenant **CATS** (comme l'onglet CATS). « Task Board & Sidebar » s'appelle maintenant **Rig Builder** (comme l'onglet Rig Builder). Aucun outil n'a été retiré : seuls les libellés marche/arrêt dans Édition > Préférences > Add-ons > BoneCraft ont changé.

**7.1.1 :** BoneCraft inclut désormais les outils CATS : une suite complète d'outils de préparation de modèles, conçus pour rendre les avatars VRChat propres, optimisés et entièrement configurés. CATS a son propre onglet dans la barre latérale et utilise un système de pipeline qui vous guide à chaque fois dans le bon ordre des opérations.
