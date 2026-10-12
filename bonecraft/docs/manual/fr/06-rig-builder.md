# Constructeur de Rig

[← Contenu](index.md)

## Construire un nouveau rig

Le Rig Builder crée un nouveau rig pour un personnage. Il se trouve dans son propre onglet **Rig Builder** sur l'étagère à outils de gauche (appuyez sur**T**) et dans l'onglet**Properties** de l'éditeur**Scene** lorsque Préférences → Onglets → Propriétés de la scène → Afficher est activé. Dans une étagère à outils étroite, il passe à une disposition compacte avec des étiquettes courtes. L'assistant Auto-Rig vient en premier, suivi de Quick Rig et Mannequin. Vous pouvez également démarrer l'assistant ou ajouter un Quick Rig à partir du menu Ajouter → Armature de la fenêtre.

---

### Assistant Auto-Rig

**Ce qu'il fait :** Un guide étape par étape qui place des marqueurs sur votre maillage et construit un équipement complet avec des poids à partir de ceux-ci. Le principal moyen de truquer un personnage à partir de zéro.

[Guide 1](02-guides-a.md#guide-1-amener-votre-premier-avatar-dans-vrchat) le parcourt étape par étape.

**Étapes :** Sélectionnez Maillage → Type de rig → Marqueurs de corps → Marqueurs de doigts → Marqueurs de visage → Révision → Générer

**Contrôles clés :**
- **Start Auto-Rig** ouvre l'assistant.**Back** et**Cancel** sont en haut ;**Next** se trouve au bas des étapes de maillage, de type de rig et de marqueur. La révision utilise**Generate Rig** au lieu de Next ; la dernière étape utilise**Close Wizard**
- La liste des maillages (cliquez sur votre maillage), puis le type de rig: **Body + Face**,**Body Only** ou**Face Only** (pour une armature existante)
- **Detect Markers** (dans Smart Detection) — trace les membres dans le maillage et place chaque marqueur corporel en toute confiance ;**Accept High** conserve les sûrs et**Reset Low** efface les douteux
- **Guess Markers from Mesh** et**Guess Precision** (corps),**Guess Finger Markers** (les marqueurs de doigts sont placés à partir de la forme de la main) et**Guess Face Markers**
- Détail des doigts : combien de doigts construire, de « 0 – Pas de doigts » à « 5 – Main humaine complète »
- Ligne de chaque marqueur : **Place Marker** (icône de flèche),**Confirm Marker** (coche) et**Reset Marker** (flèche circulaire) ;**Toggle Symmetry** (première icône) sur les marqueurs gauche et droit
- **Mirror L to R** et**Mirror R to L** — copiez les marqueurs confirmés sur la ligne médiane
- **Confirm All Placed** — confirme chaque marqueur placé de l'étape
- **Generate Rig** — construit la rig à partir des marqueurs confirmés ; puis, à la dernière étape,**Build Control Rig** (voir ci-dessous) et**Close Wizard**

**Qu'est-ce que Generate Rig construit :**
- Un body rig avec les segments de colonne vertébrale et de cou que vous avez choisis, ainsi que des bras et des jambes IK/FK, IK uniquement ou FK uniquement (l'option **Kinematics** )
- Os des doigts pour le nombre de doigts que vous avez choisi
- Pour **Body + Face**  : un habillage de face, avec des formes de contrôle lorsque**Generate Control Shapes** est activé
- Poids de peau à la qualité choisie. Les maillages denses sont pondérés par un maillage proxy plus léger, de sorte qu'un caractère à 678 000 sommets prend environ une minute au lieu d'échouer silencieusement.

**Build Control Rig :** l'étape de révision montre également**Twist Bones**,**Skirt Bones**,**Face Controls** et**Joint Correctives**. Generate Rig ne les applique pas. Ils appartiennent au système de contrôle du moteur (os de torsion, os de jupe qui suivent les jambes, commandes de visée et de clignement des yeux et clés de forme correctives des articulations). Après Generate Rig, la dernière étape propose**Build Control Rig**, qui construit cette rig sur l'armature générée avec les options que vous avez choisies. Cliquez dessus avant**Close Wizard**, car la fermeture réinitialise les options de l'assistant. Le panneau Control Layer (Rig Tools) apparaît uniquement sur une rig construite de cette manière.

**Où le trouver :** Rig Builder → Assistant de montage automatique

**Placez plusieurs marqueurs avec l'outil Fenêtre :** démarrez l'assistant et passez à une étape de marqueur de corps, de doigt ou de visage. En mode Objet, activez Placer des marqueurs de rig dans la barre d'outils de la fenêtre. L'en-tête de l'outil nomme le prochain marqueur non confirmé et affiche les verrous d'axe et un commutateur de miroir. Cliquez sur le maillage de l'assistant pour placer et confirmer ce marqueur. La symétrie suit les paramètres de l'assistant ; les boutons Place par marqueur fonctionnent toujours. Lorsque l'outil indique que l'étape est terminée, appuyez sur**Next** dans l'assistant. Cliquer ailleurs ne place pas de marqueur.

---

### Quick Rig (rig rapide)

**Ce qu'il fait :** Ajoute une armature prête à l'emploi en un clic : l'humanoïde de base de BoneCraft (19 os, aucun Rigify nécessaire) ou l'un des métarigs de Rigify. Plus rapide que l'assistant, moins adapté.

**Contrôles clés :**
- Le bouton Humanoïde de base et les métarigs Rigify (**Enable Rigify** en premier, si Rigify est désactivé)
- Cliquez sur un bouton d'installation pour l'ajouter immédiatement, puis ajustez l'ajustement au maillage, les poids automatiques, **Add IK/FK Controllers** et**Initial Pose** dans Ajuster la dernière opération.
- **T-Pose** et**A-Pose** — changez la pose de repos de l'installation sélectionnée
- Développez Dépannage pour **Diagnose Quick Rig (print to console)**. Avec une armature non métarig active, il affiche également**Inspect Active Rig Controls**
- Avec un métarig Rigify actif, le dépannage affiche **Generate Control Rig (active metarig)** au lieu d'Inspecter les commandes actives du rig ; il génère le système de contrôle Rigify

**La bibliothèque d'actifs BoneCraft Rigs :** l'humanoïde de base est également un atout. Faites-le glisser de l'étagère des ressources vers votre personnage. Une fois la rig déposée sélectionnée, Quick Rig affiche « Plate-forme abandonnée : adaptez-la à un maillage » : sélectionnez le**Mesh**, puis cliquez sur**Fit Dropped Rig**. Immédiatement après, utilisez**Fit Rig to Mesh** et**Parent + Auto-Weight Mesh** dans Ajuster la dernière opération pour choisir l'ajustement et la pondération. Une nouvelle opération consiste par défaut à l'ajustement et à la désactivation automatique de la pondération.

**Où le trouver :** Rig Builder → Quick Rig ; Ajouter → Armature → Quick Rig ajoute également les rigs prédéfinies

---

### Mannequin

**Ce qu'il fait :** Crée un maillage d'aperçu autour d'une rig existante afin que vous puissiez inspecter sa déformation sans avoir à terminer le maillage du personnage. Sélectionnez d'abord l'armature ou un maillage qui lui est associé. Si vous n'avez pas encore de rig, ajoutez-en un avec Quick Rig. Le mannequin n'est qu'un aperçu: remplacez-le par votre propre maille avant utilisation finale.

**Contrôles clés :**
- **Quick Mannequin** — crée un aperçu avec des valeurs par défaut fixes, remplaçant le modèle précédent pour cette rig
- **Add Mannequin** — crée un aperçu à l'aide des paramètres de scène ; il remplace par défaut un mannequin existant. Remplacer existant est en cours d'ajustement de la dernière opération après le clic
- **Regenerate** — reconstruit l'aperçu existant à l'aide de ses paramètres enregistrés
- **Remove** — supprime le maillage du mannequin et conserve l'armature
- Développez les options sous les boutons pour **Mode**,**Body Type**, densité et**Radius Scale**  ; Les options avancées à l’intérieur contiennent les échelles de région et les paramètres de sortie. Pour utiliser les paramètres de scène modifiés, cliquez à nouveau sur**Add Mannequin**

**Où le trouver :** Rig Builder → Mannequin

---

## Atelier mannequin illustré

<!-- Keep each illustrated step together and preserve the manual's print scale. -->
<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--atelier-mannequin-illustré"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--partie-a-de-lhumain-simple-au-mannequin"],[id="06-rig-builder--partie-b-mannequin-sans-rig-via-auto-rig"],[id="06-rig-builder--partie-ctest-des-poids-et-utilisation-du-ikfk"]) { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--partie-a-de-lhumain-simple-au-mannequin"],[id="06-rig-builder--partie-b-mannequin-sans-rig-via-auto-rig"],[id="06-rig-builder--partie-ctest-des-poids-et-utilisation-du-ikfk"]) + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

Suivez ces trois parties dans l'ordre : [A — Humain simple à mannequin](#partie-a-de-lhumain-simple-au-mannequin), [B — mannequin sans rig via Auto-Rig](#partie-b-mannequin-sans-rig-via-auto-rig) et [C — tester les poids et utiliser IK/FK](#partie-ctest-des-poids-et-utilisation-du-ikfk). Chaque étape numérotée possède une véritable capture d'écran de l'interface ; les chiffres rouges correspondent à la légende. Des captures d'écran ont été capturées avec la **version BoneCraft 9.1.2** dans `Bforartists 5.2.0`. La disposition des panneaux et les raccourcis du Blender peuvent différer ; les commandes nommées sont la référence.

Cet exercice produit un aperçu simple de la capsule pour apprendre le rigging. Sa tête, ses mains et son torse sont des espaces réservés et ce n'est pas un modèle de personnage fini. Commencez dans un nouveau fichier ; conservez les deux points de contrôle enregistrés afin de pouvoir répéter la conversion sans perdre le métarig d'origine.

Le référentiel comprend les deux points de contrôle dans `examples/mannequin/`  : `SimpleHuman_Mannequin.blend` est le résultat neutre de la partie A et `Mannequin_AutoRig.blend` est l'exemple terminé et posé de la partie C avec des poids corrigés.

### Partie A : De l'humain simple au mannequin

#### A1. Activer Rigify

Commencez dans une nouvelle scène. Ouvrez **Scene Properties → Rig Builder → Quick Rig**. Si les préréglages Rigify ne sont pas disponibles, cliquez sur**Enable Rigify**. Ce didacticiel utilise le métarig Rigify `Simple Human`  ;**BoneCraft Basic Humanoid (19 bones)** est un préréglage différent.

![A1 : Activer Rigify](../images/rig-builder/en/a01-enable-rigify.png)

*1 — Propriétés de la scène. 2 — Activer Rigify.*

#### A2. Ajouter un humain simple

Cliquez sur `Simple Human` sous Quick Rig. Le résultat est un métarig modifiable, pas encore un maillage. Il comporte 29 os dans cette version.

![A2 : Ajouter un humain simple](../images/rig-builder/en/a02-simple-human.png)

*1 — Préréglage humain simple.*

#### A3. Inspecter le métarig

Déplacez le pointeur dans la fenêtre et appuyez sur `Numpad 1` pour Front Orthographic. Vérifiez que tout le squelette est visible. Utilisez la molette de la souris pour le cadrer. Le nouveau métarig peut démarrer en mode Pose.

![A3 : Inspecter le métarig](../images/rig-builder/en/a03-metarig.png)

*1 — Vue de face. 2 — Squelette humain simple.*

#### A4. Revenir au mode objet

Utilisez la liste déroulante du mode d'affichage et choisissez **Object Mode**. Gardez `SimpleHumanArmature` sélectionné. Choisissez le mode objet avant de modifier la pose de repos ou de générer le mannequin.

![A4 : Revenir au mode objet](../images/rig-builder/en/a04-object-mode.png)

*1 — Liste déroulante des modes. 2 — Mode objet.*

#### A5. Utilisez une pose en T

Dans Quick Rig, cliquez sur **T-Pose**. Les bras s'étendent horizontalement. Pour un corps personnalisé, ajustez le métarig en mode édition avant de générer son aperçu ; gardez les articulations gauche et droite symétriques pour cet exercice.

![A5 : Utilisez une pose en T](../images/rig-builder/en/a05-t-pose.png)

*1 — Commande T-Pose.*

#### A6. Générer le mannequin

Développez **Mannequin → Options**. Ensemble `Mode: Universal`, `Body Type: Neutral`,**Medium** et `Radius Scale: 1.00`. Sous Avancé, conservez les échelles de région à 1,00, choisissez `Joined (non-manifold)`,**Couleur plate** et activez**Joint Smoothing**. Laissez le volume unifié désactivé. Cliquez sur**Add Mannequin** après avoir défini ces options. La capture d'écran montre le maillage de capsule résultant. Utilisez Ajouter pour les options actuelles ; Régénérer réutilise les paramètres du mannequin enregistrés.

![A6 : Générer le mannequin](../images/rig-builder/en/a06-final-settings.png)

*1 — Ajouter un mannequin. 2 — Paramètres universels et corps. 3 — Sortie et lissage joints.*

#### A7. Essayez une pose osseuse

Sélectionnez l'armature, passez à **Pose Mode** et cliquez sur l'os de l'avant-bras gauche (la gauche du personnage est à votre droite en vue de face). Faites-le légèrement pivoter avec l'outil Rotation ; le mannequin ci-joint suit. Il s'agit d'un aperçu pondéré sur le métarig. Il ne dispose pas encore des commandes d'animateur utilisées dans la partie C.

![A7 : Essayez une pose osseuse](../images/rig-builder/en/a07-select-forearm.png)

*1 — Mode Pose. 2 — Avant-bras sélectionné et son gizmo de transformation.*

#### A8. Restaurer et enregistrer l'aperçu

Avec le pointeur dans la fenêtre, sélectionnez tous les os de pose. Appuyez sur **F3**, recherchez `Clear Pose Transforms` et choisissez**Tous**. Confirmez que le mannequin revient à sa pose en T. Utilisez**File → Save As** et nommez le fichier `SimpleHuman_Mannequin.blend`. Conservez ce point de contrôle avant de continuer.

![A8 : Restaurer et enregistrer l'aperçu](../images/rig-builder/en/a09-clear-pose.png)

*1 — Effacez la recherche de transformations de pose. 2 — Tout réinitialise les os de pose sélectionnés.*

### Partie B : Mannequin sans rig via Auto-Rig

#### B1. Sélectionnez le maillage du mannequin

Continuez à partir du point de contrôle neutre dans la partie A. Passez à **Object Mode** et sélectionnez `SimpleHumanArmature_Mannequin` dans l'Outliner. Nous supprimerons délibérément son rig avant de lancer l'assistant. Enregistrez le résultat sous un nom de fichier différent pour conserver la partie A.

![B1 : Sélectionnez le maillage du mannequin](../images/rig-builder/en/b01-select-mesh.png)

*1 — Sélectionnez le maillage, pas l'armature.*

#### B2. Intégrer l'aperçu dans un maillage

Avec uniquement le mannequin sélectionné, appuyez sur **F3**, recherchez `Convert Mesh` et exécutez-le. Cela conserve la géométrie neutre visible et supprime le modificateur Armature. Faites cela avec le mannequin dans sa pose en T restaurée.

![B2 : Intégrer l'aperçu dans un maillage](../images/rig-builder/en/b02-convert-mesh.png)

*1 — Commande Convertir le maillage.*

#### B3. Effacer le parent

Appuyez sur **Alt+P** et choisissez `Clear and Keep Transformation`. Cela détache le maillage de l'ancien métarig sans le déplacer.

![B3 : Effacer le parent](../images/rig-builder/en/b03-clear-parent.png)

*1 — Effacer et conserver la transformation.*

#### B4. Retirez les anciens poids

Ouvrez **Object Data Properties → Vertex Groups**. Dans le menu déroulant de la liste, choisissez `Delete All Groups`. Ces groupes appartiennent à l'ancien métarig; l'assistant en créera de nouveaux. Cette action concerne ce maillage d'entraînement jetable.

![B4 : Retirez les anciens poids](../images/rig-builder/en/b04-clear-groups.png)

*1 — Menu Groupes de sommets. 2 — Supprimer tous les groupes.*

#### B5. Vérifiez le point de contrôle sans rig

Cachez l'ancien `SimpleHumanArmature` à l'aide de son icône en forme d'œil Outliner. Vérifiez que le mannequin reste visible, que son panneau Modificateurs n'a pas de modificateur d'armature et que sa liste de groupes de sommets est vide. Il s'agit de l'entrée du mannequin sans rig. BoneCraft 9.1.2 génère des mannequins à partir d'une armature ; détacher cet aperçu est la voie vers un maillage d’entraînement sans rigidité.

![B5 : Vérifier le point de contrôle sans plate-forme](../images/rig-builder/en/b05-rigless-check.png)

*1 — Masquer l'ancien métarig. 2 — Pile de modificateurs vide.*

#### B6. Activer l'onglet Rig Builder de la fenêtre d'affichage

Ouvrez **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Activez**Rig Builder** et choisissez**Left**. Fermez les Préférences, placez le pointeur sur la fenêtre et appuyez sur**T** si l'étagère à outils de gauche est masquée. Utilisez cet onglet de fenêtre pour le placement des marqueurs : dans l'hôte 9.1.2 testé, le démarrage de Placer un marqueur à partir des propriétés de la scène n'acceptait pas les clics dans la fenêtre.

![B6 : Activer l'onglet Rig Builder de la fenêtre d'affichage](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — Activer Rig Builder. 2 — Emplacement de l'étagère à outils gauche.*

#### B7. Démarrer le rig automatique

Une fois le mannequin sans monture sélectionné, cliquez sur **Start Auto-Rig**. La capture d'écran montre le bouton Propriétés de la scène équivalent ; la même commande se trouve en haut de l'onglet Rig Builder de la fenêtre d'affichage activé à l'étape précédente.

![B7 : Démarrer le rig automatique](../images/rig-builder/en/b06-start-wizard.png)

*1 — Démarrez le rig automatique.*

#### B8. Choisissez le maillage d'entrée

Dans `Select Mesh`, choisissez le mannequin et vérifiez la vérification du maillage sélectionné, puis cliquez sur **Next**. Ne choisissez pas de widget ou un autre objet d'aperçu.

![B8: Choisir le maillage d'entrée](../images/rig-builder/en/b07-select-input.png)

*1 — Entrée du mannequin. 2 — Suivant.*

#### B9. Choisissez un body rig avec les deux méthodes

Sélectionnez **Body Only** et `Kinematics: IK + FK`. Gardez**Generate Control Shapes** activé. Cliquez sur**Next**. Ce mannequin capsule n'a pas de topologie faciale, donc Body + Face n'est pas nécessaire.

![B9: Choisissez un body rig avec les deux méthodes](../images/rig-builder/en/b08-body-ikfk.png)

*1 — Corps uniquement. 2 — IK + FK. 3 — Suivant.*

#### B10. Détecter les premiers marqueurs corporels

Dans Marqueurs corporels, cliquez sur **Detect Markers** sous Détection intelligente. Considérez ses suppositions comme un point de départ. Gardez**Mirror Symmetry** activé pour ce mannequin symétrique. N'acceptez pas chaque supposition sans la vérifier.

![B10 : Détecter les premiers marqueurs corporels](../images/rig-builder/en/b09-detect-markers.png)

*1 — Détecter les marqueurs. 2 — Symétrie miroir.*

#### B11. Revoir les positions détectées

Vérifiez le haut de la tête, la base du cou, le bassin, les poignets et les chevilles par rapport au maillage visible. Cet aperçu segmenté produit plusieurs suppositions peu fiables. Examinez et corrigez les repères principaux et les repères de précision facultatifs avant de générer. Les étiquettes de confiance décrivent la détection originale ; une coche verte au début d'une ligne indique que le placement actuel est confirmé.

![B11 : Revoir les positions détectées](../images/rig-builder/en/b10-review-markers.png)

*1 — Résumé de la fiabilité de la détection. 2 — Rangées de marqueurs de corps.*

#### B12. Placer un poignet sur le maillage

Dans l'onglet **Rig Builder** de la fenêtre, cliquez sur la pipette**Place Marker** sur le poignet gauche, puis cliquez sur la surface du poignet dans la fenêtre. Pour un marqueur déjà confirmé, réinitialisez d’abord cette ligne pour exposer son bouton de placement. En vue de face, le poignet gauche du personnage se trouve à droite de l’écran.

![B12: Placer un poignet sur le maillage](../images/rig-builder/en/b11-place-wrist.png)

*1 — Contrôle du placement du poignet gauche. 2 — Cliquez sur la surface du poignet.*

#### B13. Vérifiez le poignet et les chevilles en miroir

Vérifiez que les deux rangées de poignets affichent désormais des coches vertes et des coordonnées X opposées. Répétez le placement pour `Ankle Left`  ; symétrie fournit la cheville droite. Placez chaque cheville au niveau de son articulation et non au niveau de l'orteil. Vérifiez la symétrie par rapport au maillage plutôt que de copier les coordonnées de l'exemple sur un personnage de taille différente.

![B13 : Vérifiez les poignets et les chevilles en miroir](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — Paire de poignets confirmée. 2 — Poignet en miroir sur la maille.*

#### B14. Affiner les épaules et les coudes

Faites défiler jusqu'à Marqueurs de précision. Réinitialisez et placez le `Shoulder Left` au niveau du pivot du haut du bras et le `Elbow Left` au niveau de l'espace du coude. Confirmez leurs partenaires en miroir. Gardez le poignet à l’extrémité de la main de l’avant-bras. Ces points déterminent la chaîne du bras, donc une épaule ou un coude deviné sur la mauvaise capsule doit être corrigé.

![B14: Affiner les épaules et les coudes](../images/rig-builder/en/b13-arm-precision.png)

*1 — Rangées de marqueurs d'épaule et de coude. 2 — Épaule. 3 — Coude.*

#### B15. Affiner les hanches et les genoux

Placez le `Hip Left` en haut de la cuisse et le `Knee Left` au niveau de l'espace cuisse/tibia. Vérifiez le côté opposé fourni par symétrie. Gardez le bassin sur la ligne médiane, entre les hanches.

![B15: Affiner les hanches et les genoux](../images/rig-builder/en/b14-leg-precision.png)

*1 — Rangées de hanches et de genoux. 2 — Surface de la hanche. 3 — Écart aux genoux.*

#### B16. Vérifiez la profondeur et les orteils sur le côté

Appuyez sur `Numpad 3` avec le pointeur sur la fenêtre. Vérifiez les points de repère dans l’orthographe droite ainsi que de face. Placez le `Toe Left` près de l'avant du pied ; vérifier son partenaire miroir. Un marqueur peut paraître correct vu de face mais être trop en avant ou en arrière du corps.

![B16 : Vérifiez la profondeur et les orteils depuis le côté](../images/rig-builder/en/b15-side-depth.png)

*1 — Orthographique droite. 2 — Rangée de marqueurs d'orteils. 3 — Surface du pied.*

#### B17. Placez les talons

Réinitialisez un talon mal deviné, puis placez le `Heel Left` près de l'arrière du pied en vue latérale. Vérifiez le talon droit. Bien que ces marqueurs soient facultatifs, les laisser à zéro a produit un avertissement de proximité dans la version testée. Les placer sur les pieds a effacé cet avertissement.

![B17: Placer les talons](../images/rig-builder/en/b16-place-heels.png)

*1 — Paire de talons confirmée. 2 — Emplacement du talon.*

#### B18. Confirmer et continuer

Examinez le dessus de la tête, la base du cou et le bassin ainsi que tous les points de repère appariés. Cliquez sur **Confirm All Placed**, puis sur**Next**. Les coches vertes à côté des noms correspondent à l'état de confirmation ; les étiquettes de confiance originales REVIEW/ADJUST peuvent rester visibles dans 9.1.2.

![B18 : Confirmer et continuer](../images/rig-builder/en/b17-confirm-markers.png)

*1 — Confirmez que tout est placé. 2 — Suivant.*

#### B19. Sautez les doigts pour ce maillage

Choisissez `0 — No Fingers` et cliquez sur **Next**. Ce mannequin a des capsules de main mais pas de géométrie des doigts. Sur un vrai maillage de main, choisissez le compte approprié et placez plutôt ses marqueurs de doigts.

![B19 : Sauter les doigts pour ce maillage](../images/rig-builder/en/b18-no-fingers.png)

*1 — Pas de doigts. 2 — Suivant.*

#### B20. Examiner et générer

Exigez **All checks passed** avant de continuer. Utilisez**IK + FK**, contrôlez les formes activées, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers` et**Game Ready** pour cet exercice. Désactivez les os de torsion, les os de jupe, la préservation du volume et les correctifs articulaires. Cliquez sur**Generate Rig**. Ces paramètres décrivent ce simple modèle de formation, et non une prescription universelle d’exportation.

![B20 : Examiner et générer](../images/rig-builder/en/b19-review-generate.png)

*1 — Vérifications des marqueurs. 2 — Paramètres de génération. 3 — Générer un rig.*

#### B21. Construire les contrôles de l'animateur

Après la génération, cliquez sur **Build Control Rig**. Generate Rig fournit le body rig et les poids ; Build Control Rig ajoute la couche de contrôle utilisée ci-dessous. Ne cliquez plus sur Quick Mannequin, le maillage d'entrée est déjà présent, même si le panneau de complétion affiche son offre de mannequin générique.

![B21 : Construire les contrôles de l'animateur](../images/rig-builder/en/b20-build-controls.png)

*1 – Construire une rig de contrôle.*

#### B22. Terminez l'assistant

Attendez le message de fin de l'installation de contrôle, puis cliquez sur **Close Wizard**. La nouvelle armature apparaît dans l'Outliner. Gardez l’ancien métarig Simple Human caché. Le nouveau gréement doit déformer le maillage; le simple fait de voir des os dans la fenêtre n'est pas une validation suffisante.

![B22 : Terminer l'assistant](../images/rig-builder/en/b21-close-wizard.png)

*1 — Le bouton Construire est désormais désactivé. 2 — Fermer l'assistant.*

### Partie C : Test des poids et utilisation du IK/FK

L'armature générée porte ce nom d'objet dans la version testée (utilisez-le dans l'Outliner et l'outil de poids) :

```text
BoneForge_Rig
```

`FK (Forward Kinematics)` **FK (cinématique directe)** transmet les rotations le long d’une hiérarchie: faites pivoter le bras, puis l’avant-bras, puis la main. Elle convient aux mouvements amples et aux membres libres. `IK (Inverse Kinematics)`**IK (cinématique inverse)** part d’une extrémité: déplacez la cible du poignet ou de la cheville et le solveur plie la chaîne pour l’atteindre. Elle convient aux pieds posés au sol et aux mains qui doivent rejoindre une surface.

|Tâche|Contrôle à utiliser|Que regarder|
|---|---|---|
|Balancer un bras|FK commandes d'épaule et de coude|Les contrôles enfants suivent leur parent|
|Placer une main|IK Cible de poignet |L'épaule et le coude se dirigent vers la cible|
|Planter un pied|IK cible de cheville pour cette jambe|Déplacez le corps pendant que la cible accessible reste en place|
|Visez une flexion du coude ou du genou|IK contrôle des pôles|Le poteau définit la direction du virage ; ce n'est pas la cible poignet/cheville|
|Changer de méthode|Les boutons IK/FK du membre|Vérifiez la pose cassée avant de saisir l'animation|

L'exercice ci-dessous compare un bras dans les deux modes. Chaque membre possède son propre interrupteur. `Bake IK / Bake FK` sont des outils de conversion d'animation; un commutateur à une seule position ne remplace pas la cuisson ou la saisie d'une animation. Voir [Couche de contrôle](05-rig-tools.md#control-layer-couche-de-contrôle-ikfk) pour les autres commandes.

#### C1. Ouvrir la couche de contrôle

Sélectionnez **armature générée**, choisissez**Pose Mode**, puis ouvrez**BoneCraft → Review → Control Layer**. Il existe un interrupteur IK/FK séparé pour chaque bras et chaque jambe. Commencez par**arm-L → FK**. La gauche et la droite font référence au personnage, donc le bras-L apparaît à votre droite en vue de face.

![C1 : Ouvrir la couche de contrôle](../images/rig-builder/en/c02-control-layer.png)

*1 — Mode Pose. 2 — Couche de contrôle et interrupteur arm-L.*

#### C2. Afficher les commandes de l'animateur

Ouvrez les **Object Data Properties → Bone Collections** de l'armature. Utilisez les étoiles Solo pour `Controls` et**FK** pour isoler leurs formes de contrôle. Activez**In Front** sous Affichage de la fenêtre lorsque les contrôles sont masqués par le maillage. Incluez ultérieurement**IK** lors de l'utilisation de cibles. Cette liste de collections natives fonctionne également si le panneau Collections BoneCraft ne parvient pas à dessiner dans cet hôte.

![C2 : Afficher les commandes de l'animateur](../images/rig-builder/en/c03-visible-controls.png)

*1 — Commandes et étoiles FK Solo. 2 — Devant.*

#### C3. Sélectionnez la commande d'avant-bras FK

En vue de face, cliquez sur le contrôle circulaire situé au coude gauche du personnage. Vérifiez que le nom de la sélection de la fenêtre est **forearm.fk-L**. Une commande d'avant-bras FK tourne autour du coude ; la sélection de la commande d'épaule ferait pivoter le haut du bras et ses enfants à la place.

![C3 : Sélectionnez la commande FK de l'avant-bras](../images/rig-builder/en/c04-select-fk.png)

*1 — Commande forearm.fk-L sélectionnée. 2 — FK est actif pour le bras-L.*

#### C4. Faire pivoter et inspecter la déformation

Faites pivoter le contrôle FK sélectionné autour du **Y** global, approximativement `−45°` pour cet exemple de vue de face. Utilisez l'outil Rotation ; dans le plan de touches Bforartists affiché,**Ctrl+E**,**Y**, tapez**-45**, puis**Enter** effectue cette rotation. Le raccourci de rotation par défaut de Blender est**R**. La capture d'écran montre délibérément le problème de poids initial: la capsule du haut du bras s'incline avec l'avant-bras. N’acceptez pas cela comme un gréement fini.

![C4: Faire pivoter et inspecter la déformation](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — Mouvement incorrect du haut du bras lors du test FK.*

#### C5. Recalculer les poids des mannequins

Si le test de pose ci-dessus échoue, passez à **Object Mode**, sélectionnez le maillage et ouvrez**BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**. Réglez le maillage sur Reweight sur le mannequin et l'armature existante sur**armature générée**. Choisissez**Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0` et `Minimum Weight: 0.001`. Gardez**Keep Weight Backup** activé, puis exécutez**Automatic Bone Weight Recalculation**. Cela a réparé l'aperçu segmenté dans la version testée.

![C5 : Recalculer les poids des mannequins](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — Maillage et armature. 2 – Chaleur osseuse. 3 — Paramètres de remplacement et sauvegarde. 4 — Recalculer.*

#### C6. Vérifier le coude FK réparé

Sélectionnez à nouveau l'armature générée et revenez à **Pose Mode**. Le haut du bras doit maintenant rester horizontal de l’épaule au coude tandis que l’avant-bras s’élève du coude. L'objet masqué `WEIGHTS_BACKUP_…` conserve les anciens poids. Testez également d'autres membres avant d'utiliser votre propre personnage dans l'animation. Un squelette généré à lui seul ne constitue pas une preuve d’un dépouillement correct.

![C6 : Vérifier le coude FK réparé](../images/rig-builder/en/c05-fk-result.png)

*1 — Le haut du bras reste en place. 2 — L'avant-bras se plie au niveau du coude.*

#### C7. Basculez le même bras vers IK

Cliquez sur **arm-L → IK**. Le commutateur accroche la cible à la pose actuelle, de sorte que le bras doit rester dans sa pose levée. Ajoutez**IK** aux collections Solo visibles si ses cibles sont masquées. Les changements de commutation qui contrôlent la chaîne ; cela ne signifie pas qu'une nouvelle animation a été enregistrée.

![C7: Basculez le même bras vers IK](../images/rig-builder/en/c06-switch-ik.png)

*1 — interrupteur bras-L IK. 2 — Pose conservée lors de la commutation.*

#### C8. Sélectionnez la cible du poignet IK

Cliquez sur la commande au poignet et vérifiez le nom de la sélection **forearm.ik-L**. Malgré son nom d'avant-bras, il s'agit de la cible finale de la chaîne de bras. Déplacez cette cible pour placer la main; le solveur change les angles d'épaule et de coude pour l'atteindre.

![C8 : Sélectionnez la cible du poignet IK](../images/rig-builder/en/c07-select-ik.png)

*1 — Cible du poignet sélectionnée. 2 — Nom de la sélection.*

#### C9. Déplacez la cible et comparez

Déplacez légèrement la cible du poignet vers l’intérieur le long du **X** global. Dans cet exemple, `−0.15 m` crée un pli visiblement différent. Dans le plan de clavier affiché, utilisez**Ctrl+W**,**X**, tapez `-0.15`, puis**Enter**, ou faites glisser la flèche X de l'outil Déplacer. Le raccourci de déplacement par défaut de Blender est**G**. Comparez le bras entier avec l'exemple FK  : les dérivations du point final et les deux segments du bras suivent. Gardez la cible à portée de main.

![C9 : Déplacez la cible et comparez](../images/rig-builder/en/c08-move-ik.png)

*1 — Point de terminaison du poignet. 2 — La chaîne répond. 3 — Exemple de mouvement X.*

#### C10. Revenez en arrière et enregistrez l'exemple

Cliquez à nouveau sur **arm-L → FK**. Les contrôles FK s'alignent sur la pose IK actuelle. Vérifiez que le maillage ne saute pas, puis utilisez**File → Save As** pour enregistrer `Mannequin_AutoRig.blend`. La capture d'écran montre l'exemple enregistré avec FK actif. Pour une copie d'entraînement neutre, conservez les quatre membres dans FK, sélectionnez tous les contrôles de pose visibles et utilisez**F3 → Clear Pose Transforms → All** comme dans la partie A ; enregistrez-le sous un nom distinct.

![C10 : Revenir en arrière et enregistrer l'exemple](../images/rig-builder/en/c10-save-complete.png)

*1 — FK à nouveau actif. 2 — Pose conservée. 3 — Nom du fichier enregistré.*

**Vérification d'achèvement :** vous avez conservé l'aperçu original du métarig, détaché un mannequin sans rig, généré un nouveau body rig et ses commandes, corrigé les poids de l'aperçu et comparé une rotation FK avec un mouvement cible IK. Conservez l'installation enregistrée comme exemple d'apprentissage ; remplacez l'aperçu par une géométrie de personnage adaptée à la production.

---

### Reciblage d'animation

Le déplacement d'une animation d'un squelette à un autre est traité dans [Outils de rig : reciblage](05-rig-tools.md#recibler).

---

## Fusion d'Os

**Ce qu'il fait :** Combine deux armatures en une seule, par exemple un body rig et un vêtement ou un hair rig, en gardant chaque poids.

[Guide 11](03-guides-b.md#guide-11-fusionner-deux-rigs) le parcourt étape par étape.

**Les trois étapes :**
1. Portée : choisissez les deux armatures et examinez en quoi elles diffèrent
2. Renommer : résolvez les conflits de noms et marquez de nouveaux os
3. Fusionner : prévisualiser, puis fusionner

**Contrôles clés :**
- **Base** — l'armature qui reste; l'autre armature s'y fond et est alors cachée
- **Analyze** — compare les deux squelettes ;**Acknowledge Scope — Proceed to Rename** ouvre l'étape 2
- **Normalize Both Armatures** — renomme les os standard des deux rigs en un seul standard de dénomination (Mixamo Prefixed, Mixamo Stripped ou personnalisé)
- **Auto-Propose Renames** — suggère des noms pour les propres os de la rig de fusion
- **Apply Rename** — renomme une entrée (une étape d'annulation) ;**Apply Batch Pattern** en renomme plusieurs avec un motif (avec `{bone}`, `{side}` et `{index}` )
- **Mark as Unique** — conserve un os en tant que nouvel os au lieu de le fusionner
- **Verify Rename — Proceed to Merge** — ouvre l'étape 3
- **Run Merge Preview** — indique ce que ferait la fusion, sans rien changer
- **Merge Armatures** — sauvegarde les deux armatures et les fusionne

**Où le trouver :** Onglet BoneCraft → Fusion osseuse

Suivant: [Mécanismes](07-mechanisms.md)
