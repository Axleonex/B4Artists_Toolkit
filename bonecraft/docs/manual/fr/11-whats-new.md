# Nouveautés

[← Contenu](index.md)

Le plus récent en premier.

## 9.1.2 (octobre 2026)

- **Commutateur Propriétés de la scène :** Préférences > Onglets comporte une nouvelle ligne Propriétés de la scène. Son bouton Afficher (bleu lorsqu'il est activé) affiche ou masque toutes les sections de BoneCraft dans l'onglet Propriétés > Scène (Rig Builder, Mécanismes, CATS, Outils Avatar, Outils VRChat, Importer/Exporter) sans désactiver le module complémentaire. Il démarre et laisse les onglets de la fenêtre et l'onglet Armature seuls. Voir [Où sont les choses](01-start.md#où-trouver-chaque-chose).

## 9.1.1 (octobre 2026)

- **Icônes plus claires :** chaque icône signifie désormais une chose partout. Environ 60 boutons ont une icône Bforartists mieux adaptée (par exemple Appliquer toutes les transformations, Décimer, Normaliser les noms, Traduire, Fusionner, Séparer, Mélanger la pose et Synchroniser les lèvres), et un bouton affiche la même icône dans chaque panneau.
- **Panneaux plus calmes :** les titres et le texte fixe ne comportent plus d'icônes de sujet. Les indices qui signalent un état affichent l'icône d'information, d'avertissement ou de vérification.
- **Grille d'icônes lisible :** chaque bouton des onglets Étagère à outils Pose et Poids a sa propre icône, de sorte qu'une étagère étroite reste lisible.

## 9.1.0 (octobre 2026)

- **Outils dans lesquels Bforartists met les siens :** Entrées BoneCraft dans les menus Ajouter → Armature, Pose, Poids et Objet, et un panneau de boutons BoneCraft dans les onglets de l'étagère à outils Pose et Poids de Bforartists.
- **Agissez d'abord, réglez après :** Quick Rig, Fit Dropped Rig, les outils de poids, Ribbon, Spline IK, Delta Mush et les outils d'os CATS fonctionnent en même temps avec les valeurs que vous avez utilisées en dernier lieu ; vous les réglez ensuite dans le panneau Ajuster la dernière opération. Moins de pop-ups « êtes-vous sûr ».
- **Les actions en premier, les options repliées :** plusieurs panneaux affichent leurs boutons en premier et les paramètres facultatifs dans un pli en dessous. Les entrées requises restent avant l'action, tout comme les commutateurs de nettoyage de Fix Model. Les paramètres ressemblent à des paramètres (cases à cocher, jamais boutons) et les en-têtes de panneau n'ont pas d'icônes.
- **Outils gestuels :** Placer les marqueurs de rig (cliquez sur le maillage pour placer le prochain marqueur de l'assistant de rig automatique) et le mécanisme de construction (cliquez sur une pièce pour démarrer une jointure ou un lien) se trouvent dans la barre d'outils de la fenêtre.
- **Sections Avatar :** Avatar Tools contient la cartographie humanoïde, les cheveux, les visèmes et l'exportation. La section distincte VRChat Tools regroupe les utilitaires Performance, Clothing et Naming. Les guides utilisent ces noms de panneaux actuels.
- **Info-bulles :** chaque opérateur et chaque option s'explique.
- **Afficher, ne pas masquer :** les sections restent visibles et indiquent ce qu'il faut sélectionner lorsque l'installation est partie, l'assistant d'installation automatique apparaît en premier dans Rig Builder et les étagères commencent suffisamment larges pour être lues.
- **Fixes:** Générer une spline IK fonctionne à nouveau ; Ajouter une influence utilise l'os choisi ; les aperçus de visèmes utilisent leur ensemble.

## 9.0.0 (octobre 2026)

- **Mécanismes :** une nouvelle section de l'onglet BoneCraft (et de l'onglet Propriétés de la scène) qui configure les accessoires et les machines : charnière, glissière, télescope, piston, maillon d'engrenage, suivi et séquence, construits avec des étapes guidées et vérifiés avec Test. BoneCraft n'écrase jamais une modification manuelle : vous choisissez**Keep mine** pour la conserver ou**Restore** pour la reconstruire. Voir [Mécanismes](07-mechanisms.md).
- **Exemple de fichier :** `examples/crescent-rose/` contient le Crescent Rose équipé de mécanismes (faux, fusil et formes compactes), et le [chapitre 12](12-crescent-rose.md) du manuel le construit étape par étape.
- **Côtés des onglets :** chaque onglet de la fenêtre d'affichage peut se trouver sur l'étagère à outils de gauche ou sur la barre latérale droite (Préférences → Onglets → Gauche/Droite). BoneCraft et Rig Builder démarrent à gauche, CATS à droite.
- **Rig Builder :** toujours dans l'onglet Propriétés de la scène, plus son propre onglet de fenêtre avec une disposition compacte pour une étagère à outils étroite. Une rig humanoïde de base est livrée dans la bibliothèque d'actifs BoneCraft Rigs ; Ajuster l'équipement abandonné s'adapte à un équipement déposé depuis l'étagère des ressources.
- **Onglet CATS  :** Import/Export déplacé dans l'onglet CATS. CATS, VRChat et Import/Export sont également toujours dans l'onglet Scène.
- **Afficher les assistants :** une préférence affiche ou masque le texte pédagogique de BoneCraft  ; Le mode compact est son raccourci.
- **Rig Validator :** les noms d'os avec des traits d'union passent ; les pilotes avertissent uniquement pour les expressions qui nécessitent Python ; Les mécanismes de montage sont également vérifiés. La tâche de validation du Task Board fait à nouveau rapport.
- **Nom :** le module complémentaire s'appelle BoneCraft.

## 8.9.x (septembre–octobre 2026)

- **8.9.6 :** toute la pièce de la robe suit les os de la jupe (pas de coupe des hanches) ; correcteurs de coins ouverts avec lèvres collantes.
- **8.9.5 :** Interrupteur coudé IK/FK sans bruit; détection d'épaule symétrique; les marqueurs oculaires ne s'enclenchent plus ; le sélecteur de contrôle affiche la sélection ; coins de bouche plus arrondis; une correction de la robe sur la cuisse ; clavicules reciblées détendues; Exportation de pose en T.
- **8.9.4 :** genoux plus ronds (les correctifs remplacent Preserve Volume) ; clés de contact pour les virages profonds ; un mélange de coutures d'épaule.
- **8.9.3 :** Os de la jupe à deux segments qui suivent et sont poussés par les jambes.
- **8.9.2 :** clignote avec les touches de forme (pas de pliage du couvercle) ; une ouverture de bouche ovale.
- **8.9.1 :** skinning beaucoup plus rapide sur des maillages denses (678 000 sommets : 232 s à 57 s) ; la chaleur des os à travers un maillage proxy plus léger au lieu d'échouer silencieusement.
- **8.9.0 :** clés de forme correctives conjointes ; commandes du visage (visée des yeux, clignement des yeux, suivi des lèvres) ; vêtements qui se plient avec les articulations.
- Également dans la version 8.9 : recalcul automatique du poids des os et sélection plus claire de l'atlas.

## 8.7–8.8 (septembre 2026)

- **8.8.0 :** le panneau de reciblage fonctionne sur les hôtes Blender 5 ; des marqueurs de doigts placés à partir de la forme de la main ; IK s'étire sur la peau ; une option Préserver le volume ; un correctif de liaison Delta Mush.
- **8.7.0 :** une rig de contrôle intégrée ; détection des articulations tracées par les membres ; reciblage adapté à la direction ; tordre les os.

## 8.5–8.6 (juillet 2026)

- **8.6.1–8.6.3 :** Atlas des matériaux : diagnostic des carreaux après cuisson ; Transparence MToon vérifiée par rapport à la texture alpha réelle et conservée pendant l'atlas ; meilleur cloisonnement des matériaux mixtes.
- **8.5.5–8.5.10 :** Matériaux VRM / MToon : le mode alpha est respecté, alpha fonctionne sur les hôtes Blender 5, aucune éruption d'émission, diagnostics magenta et noms d'atlas sécurisés.
- **8.5.4 :** la cartographie humanoïde est relue correctement ; Conseils pour la préparation du nom.
- **8.5.2–8.5.3 :** importez un téléchargement VRoid (.zip) ; une carte de transfert de projet VRoid.
- **8.5.1 :** Exportation FBX qui conserve les formes de mélange.

## Versions antérieures

**8.5.0 :** Smart Combine fait désormais de `atlas_uv` l'UV0 d'exportation par défaut après la cuisson. La carte UV source pré-atlas est supprimée du maillage d'atlas généré, sauf si**Keep Source UV Maps** est activé dans les paramètres avancés. Les contrôles dérivés de CATS / Material Combiner / UVToolkit sont désormais partagés avec la version ouverte Blender  ; L'exclusivité de B4Artists reste sur les systèmes de montage de production, de contrôle, de reciblage/exportation et de publication réservés à B4Artists.

La version 8.5.0 met également à jour le workflow d'exportation et de validation. Les exportations VRChat, VRM, MMD et Unreal exposent désormais les contrôles de dossier et de nom de fichier dans les panneaux BoneCraft au lieu de vous obliger à vous fier uniquement aux paramètres par défaut du navigateur de fichiers de Blender. Les exportations VRChat /Unity et Unreal FBX sont exportées par défaut vers **Embed Textures** pour faciliter l'importation de matériaux, tandis que l'exportation VRChat maintient les maillages de forme d'assistance/de contrôle hors du FBX à moins que**Helper Meshes** ne soit activé. Le panneau VRM comprend désormais**Lint Now** plus**Fix Humanoid Map**, qui peuvent réparer le mappage d'alias humanoïde obsolète avant l'exportation sans renommer vos os.

**8.4.5 :** Smart Combine force désormais les textures sources à échantillonner les UV pré-atlas préservés pendant la cuisson, valide le maillage de l'atlas généré avant de masquer les originaux et réinitialise toutes les faces de l'atlas sur l'emplacement de matériau de l'atlas final pour éviter les morceaux de robe/vêtements gris ou brouillés.

**8.4.4 :** Le Material Atlas Combiner ajoute des contrôles d'inspection de parité qualité avant la cuisson : diagnostics de shader/matériau, étiquettes de rôle de texture, marqueurs sources en double/partagés, remplacements de taille par matériau, préréglages de compression, cuissons de sortie normales/émissions/rugosité en option et bloqueurs de contrôle en amont pour le conditionnement des canaux métalliques/ORM jusqu'à ce que ce chemin soit vérifié.

**8.4.3 :** Le Material Atlas Combiner inclut des méthodes d'emballage UV sélectionnables dans le flux de travail Material Atlas existant. Il comprend Smart Pack, Grid Pack, Seeded Variation, Oriented Pack, Fit 0-1 Bounds, Advanced Variation et Rotation Step, avec les détails de la méthode UV enregistrés dans le rapport de débogage et le registre de cuisson.

**8.4.2 :** Le Material Atlas Combiner cible désormais les UV de l'atlas générés pendant la cuisson, tandis que les nœuds de texture source copiés lisent explicitement les UV du pré-atlas. Cela corrige les résultats cassés de l'atlas des robes/vêtements causés par les textures sources et l'atlas cuit échantillonnant différentes cartes UV. Les lignes de matériaux et de textures sélectionnables de 8.4.1 restent disponibles.

**7.1.3 (nettoyage des étiquettes de préférence) :** Deux options de préférence de module complémentaire ont été renommées afin qu'elles correspondent désormais à l'onglet de la barre latérale qu'elles contrôlent. "VRChat Avatar Tools" s'intitule désormais**CATS** (correspond à l'onglet de la barre latérale CATS ). « Tableau des tâches et barre latérale » s'intitule désormais**Rig Builder** (correspond à l'onglet de la barre latérale de Rig Builder). Aucun outil n'a été supprimé - seules les étiquettes d'activation/désactivation dans Édition > Préférences > Modules complémentaires > BoneCraft ont été modifiées.

**7.1.1 :** BoneCraft inclut désormais les outils CATS, une suite complète d'outils de préparation de modèles spécialement conçus pour nettoyer, optimiser et entièrement configurer les avatars VRChat. CATS réside dans son propre onglet de barre latérale et utilise un système de pipeline qui vous guide à chaque fois dans le bon ordre des opérations.

Suivant: [Tutoriel : Crescent Rose avec mécanismes](12-crescent-rose.md)
