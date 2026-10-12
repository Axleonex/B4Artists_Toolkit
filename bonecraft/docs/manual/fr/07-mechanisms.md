# Mechanisms (mécanismes)

[← Contenu](index.md)

## Ce que fait Mechanisms

Les mécanismes transforment les pièces à surface dure en une rig mécanique fonctionnelle : charnières,
diapositives, télescopes, pistons, engrenages, suiveurs et transformations entières jouées
par un curseur. Il construit des structures et des contraintes Blender ordinaires, afin que vous puissiez voir
et changez tout ce qu'il fait, et le rig fonctionne dans Blender sans scripts.
Les moteurs reçoivent les os `DEF-`. Exportation du mouvement du mécanisme cuit vers les moteurs
vient plus tard (voir Limites de cette version).

BoneCraft expédie les outils, pas une arme. Vous apportez les pièces.

Un exemple fonctionnel complet, avec une capture d'écran pour chaque étape, est [Tutoriel : Crescent Rose avec mécanismes](12-crescent-rose.md).

Mots utilisés dans les panneaux et dans cette page :

|Mot|Signification|
|---|---|
|*Partie*|Une pièce qui se déplace comme un seul bloc solide : un objet ou un morceau lâche d'un maillage. Une partie peut rouler sur une autre partie.|
|*Joint*|Comment une pièce peut se déplacer : Charnière (tourne), Glissière (se déplace), Télescope (étend les segments imbriqués).|
|*Lien*|Ce qui déplace une pièce pour vous : Piston, Gear Link, Follow.|
|*Poignée*|L'os que vous faites glisser dans la fenêtre. Chaque joint en possède un. Sa valeur est également un curseur dans le panneau.|
|*Séquence*|Une transformation jouée par un curseur, faite d'étapes.|
|*Formulaire*|Un ensemble enregistré de valeurs de poignée et de séquence, telles que « Stowed » ou « Rifle ».|

## Où il se trouve

- **BoneCraft tab → Mechanisms** dans la vue 3D. L'onglet BoneCraft est activé
l'étagère à outils de gauche (appuyez sur **T**), sauf si vous l'avez déplacée vers la barre latérale droite
(**N**) dans Préférences. Il se situe entre Skin et Review. Cela montre quand un maillage
est actif (pour démarrer une plate-forme) ou lorsqu'une armature avec des mécanismes est active ; sinon
il explique quoi sélectionner.
- **Properties editor → Scene tab → Mechanisms**, juste après Rig Builder. C'est
affiché lorsque Préférences → Onglets → Propriétés de la scène → Afficher est activé. Avec rien
utilisable sélectionné, il affiche une ligne : "Sélectionnez un maillage
pour démarrer, ou une armature avec des mécanismes. Basculement de l'onglet de la fenêtre BoneCraft
off ne le supprime pas. Le commutateur Propriétés de la scène masque uniquement la copie de la scène.
Le commutateur d'outil `mechanisms` (**Préférences → Modules complémentaires → BoneCraft → Outils**)
supprime l'outil de chaque emplacement.
Les sections de l'onglet Scène commencent par être réduites, cliquez donc sur **Mechanisms** pour les développer.
- **Object menu → Mechanisms** donne des raccourcis pour ajouter des pièces, des joints et des liens,
et pour tester le mouvement.
- **Viewport toolbar → Build Mechanism** démarre une liaison ou un lien guidé à partir d'un
cliquez sur une pièce, en mode Objet ou en mode Pose. Ajoutez d'abord les pièces, puis sélectionnez
le mécanisme ou l'une de ses pièces et choisissez le type dans l'en-tête de l'outil.

À l'intérieur des mécanismes, il y a quatre sous-sections : **1. Parts**,**2. Articulations et
Liens**,**3. Séquences** et**4. Contrôles**. Ils apparaissent une fois le rig
pièces. Avant cela, vous ne voyez que **Add Parts from Selection**.

Chaque bouton est une étape d’annulation. Si une build échoue, tout ce qu'elle a modifié est mis en place
retour et le panneau montre la raison.

## Pièces

1. Sélectionnez les objets de la pièce (ou un maillage composé de pièces détachées) en mode Objet.
2. Cliquez sur **Add Parts from Selection**.
 - Plusieurs objets: une pièce par objet. Chaque objet est parent de celui de sa partie
os et reste là où il est.
 - Une maille avec des pièces détachées: une pièce par pièce. Chaque pièce obtient un sommet
groupe pour son os et le maillage reçoit un modificateur Armature.
 - La première fois, BoneCraft fabrique le rig (une armature) pour vous.
3. Sélectionnez une pièce dans la liste pour la modifier.

Pour chaque partie:

- **Monte sur :** choisissez la partie avec laquelle celui-ci se déplace. Une partie enfant suit sa
partie mère. "le gréement" signifie qu'il repose sur la racine du gréement.
- **Size** définit la longueur de l'os, qui définit la taille de la poignée.
- **Edit Pivot** place un marqueur sur la pièce. Faites-le glisser là où la pièce doit
tournez ou faites glisser, puis cliquez sur **Apply Pivot**. Les os de la pièce s'y déplacent
et l'objet reste en place.
- **Apply Transforms** apparaît lorsqu'une partie d'objet a une rotation non appliquée ou
échelle. Cliquez dessus. Les transformations non appliquées inclinent les axes.
- Le bouton **X** supprime la pièce. Il refuse alors qu'un joint, un lien ou autre
une partie l'utilise et les nomme.
- **Merge for VRChat** (deux parties d'objet ou plus) joint les parties d'objet dans
un maillage avec un groupe de sommets par ancien objet et un modificateur Armature.
Faites cela en dernier. Les parties jointes deviennent des parties détachées de ce maillage. Il
supprime chaque groupe de sommets nommé d'après un os de cette armature (autre que
l'os `DEF-` de la pièce), fusionnez donc uniquement les pièces qui sont adaptées à l'os `DEF-` de la pièce).
mécanisme seul.

Vous pouvez renommer l'objet d'une pièce: les pièces sont étiquetées sur leurs objets, donc la pièce
retrouve son objet. Une copie de l'objet (Maj+D) ne reprend pas le
partie. Si l'objet d'une pièce est supprimé, la pièce affiche "La pièce '<nom>' est manquante".
avec **Reassign** et**Delete**. D’autres mécanismes continuent de fonctionner.

- **Reassign** utilise le maillage que vous avez sélectionné. Il refuse un non-maillage, et il
refuse un objet qu'une autre partie de l'objet utilise déjà. Pièces détachées d'un
le maillage peut partager ce maillage.
- **Delete** supprime la pièce (voir Modification ci-dessous pour savoir lorsqu'elle est refusée).

## Articulations et liens, un exemple de chaque

Ajoutez un joint avec **Add Joint**, un lien avec**Add Link**. Chaque choix démarre un
construction guidée. Ils fonctionnent depuis l'onglet de la fenêtre et depuis la scène de l'éditeur de propriétés.
onglet ; à partir de l'onglet Scène, le guide utilise la plus grande fenêtre 3D de l'écran.
Vous pouvez également activer le mécanisme de construction dans la barre d'outils de la fenêtre, choisir l'assemblage
ou tapez un lien dans l'en-tête de l'outil, puis cliquez sur sa première partie. Ce clic démarre le
même guide et fournit son premier choix. Continuez avec les choix des pics et des axes
demandé dans la fenêtre ; les menus Ajouter une articulation et Ajouter un lien restent disponibles.

Règles courtes pour chaque construction guidée :

- Cliquez sur les pièces dans la fenêtre. Les pièces cliquées obtiennent un contour et un numéro.
- Lorsqu'une étape nécessite un axe, appuyez sur **X**,**Y** ou**Z**, ou**A** pour aligner sur
la sélection. **Align to Selection** est destiné aux charnières angulaires. Il faut le maillage de la pièce
pour être toujours en mode édition avec un bord ou une face sélectionné lorsque vous appuyez sur **A**,
et le guide ignore **Tab**. Entrez donc en mode édition sur le maillage de la pièce et
sélectionnez d'abord une arête ou une face. Restez en mode édition, démarrez **Ajouter un joint →
Charnière**, cliquez sur la pièce, appuyez sur**A**. Si rien d’utile n’est sélectionné le guide
vous le dit et vous pouvez appuyer sur une autre touche.
- La dernière étape donne un aperçu du mécanisme se déplaçant en boucle. **Enter** le conserve.
**Esc** le supprime.
- L'en-tête et la barre d'état affichent une phrase complète pour chaque étape. Avec spectacle
Les assistants s'en vont, ils montrent une courte étiquette.

Chaque ligne de la liste Joints et liens comporte quatre boutons d'icône : **Test** (lire
triangle), **Edit** (crayon, affiche les paramètres),**Detach** (chaîne cassée) et
**Delete** (X).

Après la construction, l'élément sélectionné dans la liste affiche uniquement les paramètres de son
type utilise.

### Hinge (charnière)

Charnière à lame, 0°…90° :

1. Ajoutez des pièces de la sélection avec une pièce lame.
2. **Add Joint → Hinge**. Cliquez sur la lame. Appuyez sur**X**. Appuyez sur**Enter**.
3. Vous obtenez une poignée en demi-cercle, `CTRL-Blade`, et une *charnière à lame* dans le
liste. Réglez **Min** 0 et**Max** 90 (° pour une charnière).
4. Essayez-le : faites glisser la poignée en demi-cercle. Il s'arrête à 90°. **Set Min** et
**Set Max** copie la pose actuelle de la poignée dans les limites.

Une limite inférieure à un tour complet doit rester entre −180°…180°. Des limites telles que
170°…190° sont refusés avec un message. Une portée d'un tour complet ou plus (pour
exemple −180°…180°) tourne librement sans limite.

### Slide (glissière)

Glissière du baril, 0…0,3 :

1. **Add Joint → Slide**. Cliquez sur la partie Baril. Appuyez sur**Y**. Appuyez sur**Enter**.
2. Vous obtenez une poignée de flèche. Réglez **Min** 0 et**Max** 0,3 (unités de scène).
3. Essayez-le : faites glisser la flèche. Le canon glisse et s'arrête à 0,3.

### Telescope (télescope)

Mât à trois segments:

1. Fabriquez la base et les trois segments.
2. **Add Joint → Telescope**. Cliquez sur la base. Cliquez sur chaque segment de la base
vers l'extérieur. Appuyez sur **Enter**. Appuyez sur la touche d'axe. Appuyez sur**Enter** pour le conserver.
3. Vous obtenez une poignée de flèche sur la base. **Length** est le trajet total ;
**Shares (empty = even)** le divise entre les segments. Pour essayer le personnalisé
partages, définissez d'abord **Length** sur 1, puis tapez `0.5, 0.25, 0.25`. Les actions
doit s'additionner à la longueur, de sorte que la pointe parcourt toute la longueur. Une faute de frappe (pour
exemple `0.5, abc` ) est refusé avec le même message en clair: les partages
doit être composé de nombres, un par segment, dont la somme correspond à la longueur.
4. Essayez-le : faites glisser la flèche. Les trois segments s'étendent par leurs actions.
**Set Max** définit la longueur à partir de la pose de la poignée.

### Piston

Ascenseur: vérin sur le châssis, tige sur le bras.

1. Donnez d'abord une charnière au bras et réglez le bras pour qu'il monte sur le cadre.
2. **Add Link → Piston**. Cliquez sur la partie cylindre (sur le cadre). Cliquez sur la tige
partie (sur le bras).
3. Vous obtenez un piston sans poignée. Chaque partie pointe vers l'attache de l'autre
point. **Stretch** (en option) étire la tige, pour les ressorts et les câbles.
4. Essayez-le : déplacez la poignée du bras. Le piston suit. Si rien ne bouge le
Piston pour l'instant, la version fonctionne mais n'a pas d'aperçu et **Test** le dit.

### Gear Link (lien d'engrenage)

Engrenages 20:40 :

1. Les deux parties ont d’abord besoin d’un joint. La partie motrice a besoin d'une charnière. Pour l'équipement et
Courroie, la partie entraînée a besoin d'une charnière ; pour Rack, il faut une diapositive.
2. **Add Link → Gear Link**. Cliquez sur la partie motrice. Cliquez sur la pièce entraînée.
3. Dans ses paramètres, définissez **Source Teeth** 20 et**Target Teeth** 40 (ou tapez un
**Ratio** ).**Kind** est un engrenage, une courroie ou une crémaillère.**Reverse** inverse la direction.
4. Essayez-le : allumez la source. Avec **Kind** Gear, la cible tourne de −0,5× jusqu'à
(+0,5× avec ceinture). Une vitesse s'inverse
direction, une courroie la maintient et une crémaillère transforme la rotation en glissière (distance
par radian = **Ratio** ×**Pinion Radius** ).

La façon dont BoneCraft le construit dépend de la plage de la charnière source :

- Sous un tour complet: une contrainte Transformation. Il suit tout ce qui bouge
la source, Séquences incluses.
- Un tour complet ou plus : un pilote qui n'a pas besoin de Python. La cible tourne pour toujours
avec la source. Il suit uniquement les poignées et les engrenages. Le Rig Validator prévient
lorsqu'une séquence ou un suivi serait perdu.

### Follow (suiveur)

La lame 0 à 90° soulève le couvercle 0 à 40° :

1. Les deux parties nécessitent une charnière ou une glissière. Une charnière source a besoin de limites sous un
tour complet ; une source à rotation libre est refusée.
2. **Add Link → Follow**. Cliquez sur la partie principale (Lame). Cliquez sur ce qui suit
partie (Couverture).
3. Les gammes commencent par la gamme complète de chaque joint. Ensemble **Source Range**
0…90 et **Target Range** 0…40. Passé l’une ou l’autre extrémité, la cible tient.
4. Essayez-le : déplacez la poignée de la lame. La couverture suit.
5. Cochez **Curve** pour remodeler le mappage dans l'éditeur graphique. BoneCraft jamais
écrase votre courbe (voir Modification ci-dessous).

### Sequence (séquence)

Enregistrez les étapes pour plier une arme :

1. Dans **3. Sequences**, cliquez sur**Add Sequence**. Cela fait une poignée de curseur
`CTRL-SEQ-<name>`.
2. Cliquez sur **Move Slider to End**. Le curseur saute jusqu'à sa fin (1) et le bouton
devient Record Step suivi du numéro de l’étape suivante.
3. Posez les poignées des joints pour la première étape. Cliquez sur Enregistrer l'étape 1.
Chaque poignée déplacée devient un pas avec sa valeur cible, et le
les poignées reviennent à zéro.
4. Répétez les étapes 2 et 3 pour plus d'étapes. Chaque nouvelle étape prend le quart suivant du
curseur par défaut.
5. Réglez **Target**, la facilité (Linéaire, Ease In, Ease Out, Ease In Out, Snap),
**Start** et**End** pour chaque étape. Hors de sa tranche une marche tient son bout
valeur. Plusieurs Séquences peuvent se cumuler.
6. Cliquez sur **Test**  : le curseur joue 0 → 1 → 0.

À côté du bouton d'enregistrement pas à pas et de **Test**, la séquence sélectionnée porte**Detach**
(chaîne cassée) et **Delete** (X). Une Séquence tenue (par exemple un pas dont
courbe que vous avez remodelée) affiche son message et un bouton **Restore**. Restaurer
régénère les étapes de l'enregistrement. Keep mine n'est pas offert pour une Séquence.

## Test

**Test** (le bouton de lecture dans la liste et dans 3. Séquences) en balaie un
mécanisme sur toute sa gamme et son dos. Il n'écrit aucune clé et met la pose
de retour quand ça se termine. Appuyez sur **Esc** pour l'arrêter plus tôt ; la pose est rétablie alors
aussi. Pour un Gear Link ou Follow, il balaie la source. Pour un piston, il balaie le
articulation qui le déplace. Surveillez les pièces qui entrent en conflit ; BoneCraft ne détecte pas
collisions.

## Formes

Dans **4. Controls**  :

- Chaque jointure et séquence possède un curseur. C'est le canal propre à la poignée, donc
faire glisser la poignée et utiliser le curseur sont la même chose.
- **Save Form** enregistre chaque valeur de poignée et de curseur de séquence sous un nom.
Renommez-le dans la liste.
- **Go to Form** définit chaque contrôle sur les valeurs enregistrées.
- **Go and Key** fait de même et insère également des clés sur l'image actuelle.
- Le **X** à côté de la liste supprime un formulaire.

## Ce que construit BoneCraft

Pour chaque partie:

|Os|Emploi|Visible|
|---|---|---|
|`CTRL-<part>` |La poignée. Sa valeur est le curseur du panneau. Seuls la charnière, la glissière et le télescope n'en font qu'un.|Oui|
|`MCH-<part>` |Ajoute le handle et chaque lien, puis applique les limites.|Caché|
|`DEF-<part>` |Copies `MCH-<part>`. Le maillage y est lié. Les moteurs reçoivent cet os.|Caché|

Les os se trouvent dans les collections `Mechanism Controls`, `Mechanism MCH` et
`Mechanism DEF`. Une pièce sans articulation ne comporte que des os `MCH-` et `DEF-`. Un
La poignée du télescope est `CTRL-<telescope name>`. Une séquence est
`CTRL-SEQ-<name>`. Un piston ajoute les os `MCH-<part>-aim` et `MCH-<part>-target`
pour chacune de ses deux parties.

Les contraintes sur `MCH-<part>` viennent toujours dans le même ordre: Copier les transformations
de la poignée, puis la contribution de chaque maillon, puis la limite de rotation de l'articulation
ou Limiter l'emplacement. `DEF-<part>` possède une transformation de copie de `MCH-<part>`.

Tout ce que BoneCraft construit est étiqueté avec son enregistrement : les noms de contraintes commencent
avec `BC·<id>·<role>`, et les os portent les propriétés `bc_mech_id` et
`bc_mech_role`. BoneCraft trouve ses os par étiquette et non par nom, vous pouvez donc
renommer n'importe quel os. Une reconstruction le retrouve et ne crée aucun doublon.

Lorsque l'option Afficher les aides est activée, chaque liaison et lien comporte une note **How this works**. Il
répertorie les contraintes par nom, indique ce que chacune fait et possède un **Select**
(une icône en forme de flèche) pour inspecter l’os.

Vos propres contraintes, pilotes et os ne sont jamais touchés. Une contrainte que vous ajoutez
à un os MCH reste inférieur à celui de BoneCraft après une reconstruction.

## Modifications et retouches manuelles

- **Modifications de valeurs** (limites, ratio, plages, timing, facilité, apparence de la poignée) mettent à jour le
contraintes existantes en place. Il n'y a pas de reconstruction.
- **Modifications structurelles** (un**Kind** de Gear Link, un**Curve** de Follow, un
Piston **Stretch** ) remplace les contraintes de ce mécanisme et reconstruit uniquement
ce mécanisme.
- **Modifié manuellement.** Si vous modifiez une contrainte BoneCraft (par exemple un
Limite), le message du mécanisme se termine par "(modifié à la main)". BoneCraft n'écrase jamais
cela en silence. Choisissez :
 - **Keep mine** copie vos valeurs dans l'enregistrement. Il refuse ce qu'il ne peut pas
relisez et dites d'utiliser Restaurer ou Détacher.
 - **Restore** supprime votre modification et reconstruit à partir de l'enregistrement.
- Un mécanisme maintenu maintient également tous les mécanismes qui utilisent ses os, jusqu'à ce que vous
régler ça.
- Une courbe remodelée est la même. Si vous remodelez une courbe de suivi (**Curve**
cochée) dans l'éditeur graphique puis modifiez une valeur qui la remplacerait,
comme sa portée cible, le message du suivi se termine par "(modifié à la main)". **Keep mine**
garde votre courbe. **Restore** le régénère.
- Une séquence en attente affiche son message et **Restore** dans**3. Sequences**, avec
**Detach** et**Delete** à côté. Keep mine n’est pas proposé pour les séquences.
- **Detach** (bouton chaîne brisée) supprime l'enregistrement et les tags mais conserve les os et
contraintes comme votre propre plate-forme faite à la main. Détacher et Supprimer refusent tous deux un enregistrement
qu'un autre enregistrement utilise et nommez les utilisateurs.
- **Delete** (bouton X) supprime l'enregistrement et tout ce que BoneCraft a construit pour celui-ci.
- Une boucle de lien est refusée avant que quoi que ce soit ne soit construit, et la boucle est nommée, par exemple
exemple "La charnière de la lame → Suivi du couvercle → La charnière de la lame ferait une boucle."

Le Rig Validator et le Task Board signalent les boucles de liaison, les pièces manquantes, le DEF
les os déplacés de l'extérieur de leur mécanisme, les pilotes qui ont besoin de Python et Gear
Liens qui perdent une séquence ou un suivi. Le contrôle de dénomination du validateur accepte
tirets (`CTRL-`, `MCH-`, `DEF-` ), et la vérification de ses pilotes avertit uniquement sur
expressions qui nécessitent Python, donc une rig Mechanisms propre ne montre aucune validation
erreurs - seul le seul avertissement concernant l'os `root` décrit dans Limites de cette version.

## Show Helpers (afficher les aides)

**Show Helpers** est une préférence pour tous les BoneCraft  :**Préférences →
Modules complémentaires → BoneCraft → Aides**. Désactivé cache le texte pédagogique partout : le quoi/quand
lignes, les notes **How this works** et les phrases guidées complètes (celles
deviennent des étiquettes courtes). Les étapes elles-mêmes, les listes, les tests, les avertissements et
Les info-bulles de survol de Blender restent toujours.

Le bouton VRChat **Compact Mode** est son raccourci: Mode Compact activé signifie Afficher
Les secours sont partis.

## Limites de cette version

- Les mécanismes Click Turn, Track et Linkage viennent plus tard.
- L'exportation du moteur du mouvement du mécanisme cuit intervient plus tard, après la main du bureau
vérifier. En attendant, les os `DEF-` sont les os à exporter.
- BoneCraft ne détecte pas les collisions. Utilisez Test et regardez.
- Un Gear Link à rotation libre suit uniquement les poignées et les engrenages.
- L'os `root` du rig n'est dans aucune collection d'os, donc le Rig Validator's
Le contrôle des collections en avertit et le tableau des tâches affiche "Rig validation
avertissements (1)".

Suivant: [VRChat Outils](08-vrchat.md)
