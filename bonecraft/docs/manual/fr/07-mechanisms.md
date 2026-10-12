# Mechanisms (mécanismes)

[← Sommaire](index.md)

## Ce que fait Mechanisms

Mechanisms transforme des pièces hard-surface en un rig mécanique fonctionnel : charnières, glissières, télescopes, pistons, engrenages, suiveurs et transformations entières jouées par un seul curseur. Il construit des os et des contraintes Blender ordinaires, donc vous pouvez voir et modifier tout ce qu'il crée, et le rig fonctionne dans Blender sans scripts. Les moteurs de jeu reçoivent les os `DEF-`. L'export vers les moteurs du mouvement cuit des mécanismes viendra plus tard (voir Limites de cette version).

BoneCraft fournit les outils, pas une arme. Les pièces, c'est vous qui les apportez.

Les mots utilisés dans les panneaux et dans cette page :

| Mot | Sens |
|---|---|
| *Pièce* (Part) | Un élément qui bouge comme un bloc solide : un objet, ou un morceau détaché d'un maillage. Une pièce peut être portée par une autre pièce. |
| *Articulation* (Joint) | Comment une pièce peut bouger : Hinge (tourne), Slide (se déplace), Telescope (déploie des segments emboîtés). |
| *Lien* (Link) | Ce qui déplace une pièce à votre place : Piston, Gear Link, Follow. |
| *Poignée* (Handle) | L'os que vous faites glisser dans la vue. Chaque articulation en a une. Sa valeur est aussi un curseur dans le panneau. |
| *Séquence* (Sequence) | Une transformation jouée par un seul curseur, faite d'étapes. |
| *Forme* (Form) | Un ensemble enregistré de valeurs de poignées et de séquences, comme « Stowed » (rangé) ou « Rifle » (fusil). |

## Où il se trouve

- **Onglet BoneCraft → Mechanisms** dans la vue 3D. L'onglet BoneCraft est sur la Tool Shelf de gauche (touche **T**), sauf si vous l'avez déplacé dans la barre latérale de droite (**N**) dans les Préférences. Il se place entre Peau et Révision. Il s'affiche quand un maillage est actif (pour commencer un rig) ou quand une armature avec des mécanismes est active.
- **Éditeur Propriétés → onglet Scène → Mechanisms**, juste après le Constructeur de Rig. Il y est toujours. Sans rien d'utilisable sélectionné, il affiche une ligne : « Select a mesh to start, or an armature with mechanisms. » (sélectionnez un maillage pour commencer, ou une armature avec des mécanismes). Désactiver l'onglet BoneCraft de la vue ne le retire pas. Seul l'interrupteur d'outil `mechanisms` (**Préférences → Add-ons → BoneCraft → Outils**) le retire, avec la copie de la vue. Les sections de l'onglet Scène sont repliées au départ : cliquez sur **Mechanisms** pour le déplier.

Dans Mechanisms, il y a quatre sous-sections : **1. Parts** (pièces), **2. Joints & Links** (articulations et liens), **3. Sequences** (séquences) et **4. Controls** (contrôles). Elles apparaissent dès que le rig a des pièces. Avant cela, vous ne voyez que **Add Parts from Selection** (ajouter des pièces depuis la sélection).

Chaque bouton est une étape d'annulation. Si une construction échoue, tout ce qu'elle a changé est remis en place et le panneau affiche la raison.

## Pièces

1. Sélectionnez les objets des pièces (ou un maillage fait de morceaux détachés) en Mode Objet.
2. Cliquez sur **Add Parts from Selection**.
   - Plusieurs objets : une pièce par objet. Chaque objet est parenté à l'os de sa pièce et reste où il est.
   - Un maillage avec des morceaux détachés : une pièce par morceau. Chaque morceau reçoit un groupe de sommets pour son os et le maillage reçoit un modificateur Armature.
   - La première fois, BoneCraft crée le rig (une armature) pour vous.
3. Sélectionnez une pièce dans la liste pour la modifier.

Pour chaque pièce :

- **Rides on:** (portée par) : choisissez la pièce avec laquelle celle-ci se déplace. Une pièce enfant suit sa pièce parente. « the rig » signifie qu'elle est portée par la racine du rig.
- **Size** (taille) règle la longueur de l'os, qui règle la taille de la poignée.
- **Edit Pivot** (modifier le pivot) place un marqueur sur la pièce. Faites-le glisser là où la pièce doit tourner ou glisser, puis cliquez sur **Apply Pivot** (appliquer le pivot). Les os de la pièce s'y déplacent et l'objet reste en place.
- **Apply Transforms** (appliquer les transformations) apparaît quand une pièce objet a une rotation ou une échelle non appliquée. Cliquez dessus. Des transformations non appliquées inclinent les axes.
- Le bouton **X** retire la pièce. Il refuse tant qu'une articulation, un lien ou une autre pièce l'utilise, et les nomme.
- **Merge for VRChat** (fusionner pour VRChat ; deux pièces objets ou plus) joint les pièces objets en un seul maillage, avec un groupe de sommets par ancien objet et un modificateur Armature. Faites-le en dernier. Les pièces jointes deviennent des morceaux détachés de ce maillage unique. Il supprime chaque groupe de sommets portant le nom d'un os de cette armature (sauf l'os `DEF-` propre à la pièce), donc ne fusionnez que des pièces riggées sur le seul rig de mécanismes.

Vous pouvez renommer l'objet d'une pièce : les pièces sont marquées sur leurs objets, donc la pièce retrouve son objet. Une copie de l'objet (Maj+D) ne reprend pas la pièce. Si l'objet d'une pièce est supprimé, la pièce affiche « Part '<name>' is missing » (la pièce '<name>' est manquante) avec **Reassign** (réattribuer) et **Supprimer**. Les autres mécanismes continuent de fonctionner.

- **Reassign** utilise le maillage que vous avez sélectionné. Il refuse ce qui n'est pas un maillage, et refuse un objet déjà utilisé par une autre pièce objet. Les morceaux détachés d'un même maillage peuvent partager ce maillage.
- **Supprimer** retire la pièce (voir Modifications et retouches manuelles plus bas pour les cas de refus).

## Articulations et liens, un exemple de chaque

Ajoutez une articulation avec **Add Joint** (ajouter une articulation), un lien avec **Add Link** (ajouter un lien). Chaque choix lance une construction guidée. Elles fonctionnent depuis l'onglet de la vue et depuis l'onglet Scène de l'éditeur Propriétés ; depuis l'onglet Scène, le guide utilise la plus grande vue 3D de l'écran. Règles courtes pour toute construction guidée :

- Cliquez sur les pièces dans la vue. Les pièces cliquées reçoivent un contour et un numéro.
- Quand une étape demande un axe, appuyez sur **X**, **Y** ou **Z**, ou sur **A** pour l'aligner sur la sélection. **Align to Selection** (aligner sur la sélection) sert aux charnières inclinées. Il faut que le maillage de la pièce soit encore en Mode Édition avec une arête ou une face sélectionnée quand vous appuyez sur **A**, et le guide ignore **Tab**. Passez donc d'abord en Mode Édition sur le maillage de la pièce et sélectionnez une arête ou une face. Restez en Mode Édition, lancez **Add Joint → Hinge**, cliquez sur la pièce, appuyez sur **A**. Si rien d'utilisable n'est sélectionné, le guide vous le dit et vous pouvez appuyer sur une autre touche.
- La dernière étape prévisualise le mécanisme en boucle. **Entrée** le garde. **Échap** le retire.
- L'en-tête et la barre d'état affichent une phrase complète pour chaque étape. Avec Show Helpers (afficher les aides) désactivé, ils affichent un libellé court.

Chaque ligne de la liste Joints & Links a quatre boutons à icône : **Test** (triangle de lecture), **Modifier** (crayon, affiche les réglages), **Detach** (détacher ; chaîne brisée) et **Supprimer** (X).

Après la construction, l'élément sélectionné dans la liste n'affiche que les réglages utilisés par son type.

### Hinge (charnière)

Hinge de lame, 0°…90° :

1. Add Parts from Selection avec une pièce Blade (lame).
2. **Add Joint → Hinge**. Cliquez sur Blade. Appuyez sur **X**. Appuyez sur **Entrée**.
3. Vous obtenez une poignée en demi-cercle, `CTRL-Blade`, et une *Blade Hinge* dans la liste. Réglez **Min** sur 0 et **Max** sur 90 (en ° pour une Hinge).
4. Essayez : faites glisser la poignée en demi-cercle. Elle s'arrête à 90°. **Set Min** (définir le min) et **Set Max** (définir le max) copient la pose actuelle de la poignée dans les limites.

Une limite inférieure à un tour complet doit rester dans −180°…180°. Des limites comme 170°…190° sont refusées avec un message. Une plage d'un tour complet ou plus (par exemple −180°…180°) tourne librement sans limite.

### Slide (glissière)

Slide de canon, 0…0.3 :

1. **Add Joint → Slide**. Cliquez sur la pièce Barrel (canon). Appuyez sur **Y**. Appuyez sur **Entrée**.
2. Vous obtenez une poignée en flèche. Réglez **Min** sur 0 et **Max** sur 0.3 (unités de la scène).
3. Essayez : faites glisser la flèche. Le canon glisse et s'arrête à 0.3.

### Telescope (télescope)

Mât à trois segments :

1. Créez la base et trois pièces de segment.
2. **Add Joint → Telescope**. Cliquez sur la base. Cliquez sur chaque segment, de la base vers l'extérieur. Appuyez sur **Entrée**. Appuyez sur la touche d'axe. Appuyez sur **Entrée** pour garder.
3. Vous obtenez une seule poignée en flèche sur la base. **Length** (longueur) est la course totale ; **Shares (empty = even)** (parts ; vide = égales) la répartit entre les segments. Pour essayer des parts personnalisées, réglez d'abord **Length** sur 1, puis tapez `0.5, 0.25, 0.25`. La somme des parts doit égaler la Length, pour que le bout parcoure toute la longueur. Une faute de frappe (par exemple `0.5, abc`) est refusée avec le même message simple : les parts doivent être des nombres, un par segment, dont la somme égale la Length.
4. Essayez : faites glisser l'unique flèche. Les trois segments se déploient selon leurs parts. **Set Max** règle la Length d'après la pose de la poignée.

### Piston

Élévateur : cylindre sur le châssis, tige sur le bras.

1. Donnez d'abord une Hinge au bras, et faites porter le bras par le châssis.
2. **Add Link → Piston**. Cliquez sur la pièce cylindre (sur le châssis). Cliquez sur la pièce tige (sur le bras).
3. Vous obtenez un Piston sans poignée. Chaque pièce pointe vers le point d'attache de l'autre. **Étirer** (facultatif) étire la tige, pour les ressorts et les câbles.
4. Essayez : bougez la poignée du bras. Le piston suit. Si rien ne fait encore bouger le Piston, la construction fonctionne mais sans aperçu, et **Test** l'indique.

### Gear Link (lien d'engrenage)

Engrenage 20:40 :

1. Les deux pièces ont d'abord besoin d'une articulation. La pièce menante a besoin d'une Hinge. Pour Gear et Belt, la pièce menée a besoin d'une Hinge ; pour Rack, d'une Slide.
2. **Add Link → Gear Link**. Cliquez sur la pièce menante. Cliquez sur la pièce menée.
3. Dans ses réglages, mettez **Source Teeth** (dents de la source) à 20 et **Target Teeth** (dents de la cible) à 40 (ou tapez un **Ratio**). **Kind** (type) vaut Gear, Belt ou Rack. **Reverse** (inverser) inverse le sens.
4. Essayez : tournez la source. Avec **Kind** sur Gear, la cible tourne de −0.5× autant (+0.5× avec Belt). Un Gear inverse le sens, un Belt le garde, et un Rack transforme la rotation en glissement (distance par radian = **Ratio** × **Pinion Radius** (rayon du pignon)).

La façon dont BoneCraft le construit dépend de la plage de la Hinge source :

- Moins d'un tour complet : une contrainte Transformation. Elle suit tout ce qui fait bouger la source, séquences comprises.
- Un tour complet ou plus : un driver qui n'a pas besoin de Python. La cible tourne indéfiniment avec la source. Elle ne suit que les poignées et les engrenages. Le Validateur de Rig avertit quand une séquence ou un Follow serait perdu.

### Follow (suiveur)

Blade 0–90° soulève Cover (couvercle) 0–40° :

1. Les deux pièces ont besoin d'une Hinge ou d'une Slide. Une Hinge source a besoin de limites inférieures à un tour complet ; une source en rotation libre est refusée.
2. **Add Link → Follow**. Cliquez sur la pièce qui mène (Blade). Cliquez sur la pièce qui suit (Cover).
3. Les plages commencent à la plage complète de chaque articulation. Réglez **Source Range** (plage source) sur 0…90 et **Target Range** (plage cible) sur 0…40. Au-delà de l'une ou l'autre extrémité, la cible reste immobile.
4. Essayez : bougez la poignée de Blade. Cover suit.
5. Cochez **Curve** (courbe) pour remodeler la correspondance dans l'éditeur de graphe. BoneCraft n'écrase jamais votre courbe (voir Modifications et retouches manuelles plus bas).

### Sequence (séquence)

Capture Step pour replier une arme :

1. Dans **3. Sequences**, cliquez sur **Add Sequence** (ajouter une séquence). Cela crée une poignée de curseur `CTRL-SEQ-<name>`.
2. Cliquez sur **Capture Step** (capturer une étape). Le curseur saute à sa fin (1).
3. Posez les poignées des articulations pour la première étape. Cliquez de nouveau sur **Capture Step**. Chaque poignée qui a bougé devient une étape avec sa valeur cible, et les poignées reviennent à zéro.
4. Répétez l'étape 3 pour d'autres étapes. Chaque nouvelle étape prend par défaut le quart suivant du curseur.
5. Réglez la **Cible**, l'accélération (Linear, Ease In, Ease Out, Ease In Out, Snap), **Démarrer** et **End** (fin) de chaque étape. En dehors de sa tranche, une étape garde sa valeur de fin. Plusieurs séquences peuvent s'empiler.
6. Cliquez sur **Test** : le curseur joue 0 → 1 → 0.

À côté de **Capture Step** et **Test**, la séquence sélectionnée a **Detach** (chaîne brisée) et **Supprimer** (X). Une séquence en attente (par exemple une étape dont vous avez remodelé la courbe) affiche son message et un bouton **Restaurer**. Restaurer régénère les étapes à partir de l'enregistrement. Keep mine (garder la mienne) n'est pas proposé pour une séquence.

## Test

**Test** (le bouton de lecture dans la liste, et dans 3. Sequences) fait parcourir à un mécanisme toute sa plage, aller et retour. Il n'écrit aucune clé et remet la pose en place à la fin. Appuyez sur **Échap** pour l'arrêter plus tôt ; la pose est alors restaurée aussi. Pour un Gear Link ou un Follow, il fait bouger la source. Pour un Piston, il fait bouger l'articulation qui l'entraîne. Surveillez les pièces qui se heurtent ; BoneCraft ne détecte pas les collisions.

## Formes

Dans **4. Controls** :

- Chaque articulation et chaque séquence a un curseur. C'est le canal propre de la poignée, donc faire glisser la poignée et utiliser le curseur reviennent au même.
- **Save Form** (enregistrer la forme) enregistre la valeur de chaque poignée et de chaque curseur de séquence sous un nom. Renommez-la dans la liste.
- **Go to Form** (aller à la forme) règle chaque contrôle sur les valeurs enregistrées.
- **Go and Key** (aller et poser une clé) fait de même et insère aussi des clés à l'image actuelle.
- Le **X** à côté de la liste retire une forme.

## Ce que construit BoneCraft

Pour chaque pièce :

| Os | Rôle | Visible |
|---|---|---|
| `CTRL-<part>` | La poignée. Sa valeur est le curseur du panneau. Seules Hinge, Slide et Telescope en créent une. | Oui |
| `MCH-<part>` | Additionne la poignée et chaque lien, puis applique les limites. | Masqué |
| `DEF-<part>` | Copie `MCH-<part>`. Le maillage y est lié. Les moteurs reçoivent cet os. | Masqué |

Les os sont dans les collections `Mechanism Controls`, `Mechanism MCH` et `Mechanism DEF`. Une pièce sans articulation n'a que des os `MCH-` et `DEF-`. La poignée d'un Telescope est `CTRL-<telescope name>`. Celle d'une séquence est `CTRL-SEQ-<name>`. Un Piston ajoute des os `MCH-<part>-aim` et `MCH-<part>-target` pour chacune de ses deux pièces.

Les contraintes de `MCH-<part>` viennent toujours dans le même ordre : Copier les transformations depuis la poignée, puis la contribution de chaque lien, puis la Limite de rotation ou la Limite de position de l'articulation. `DEF-<part>` a une seule Copie des transformations depuis `MCH-<part>`.

Tout ce que construit BoneCraft est marqué avec son enregistrement : les noms de contraintes commencent par `BC·<id>·<role>`, et les os portent les propriétés `bc_mech_id` et `bc_mech_role`. BoneCraft trouve ses os par marque, pas par nom, donc vous pouvez renommer n'importe quel os. Une reconstruction le retrouve et ne crée pas de doublon.

Avec Show Helpers activé, chaque articulation et chaque lien a une note **How this works** (comment ça marche). Elle liste les contraintes par nom, dit ce que fait chacune, et a un bouton **Sélectionner** (icône de flèche) pour inspecter l'os.

Vos propres contraintes, drivers et os ne sont jamais touchés. Une contrainte que vous ajoutez à un os MCH reste sous celles de BoneCraft après une reconstruction.

## Modifications et retouches manuelles

- Les **Value edits** (modifications de valeurs : limites, ratio, plages, minutage, accélération, aspect de la poignée) mettent à jour les contraintes existantes sur place. Il n'y a pas de reconstruction.
- Les **Structural edits** (modifications de structure : le **Kind** d'un Gear Link, la **Curve** d'un Follow, l'**Étirer** d'un Piston) remplacent les contraintes de ce mécanisme et ne reconstruisent que lui.
- **Changed by hand.** (modifié à la main) Si vous modifiez une contrainte de BoneCraft (par exemple une Limite), le message du mécanisme se termine par « (changed by hand) ». BoneCraft ne l'écrase jamais sans rien dire. Choisissez :
  - **Keep mine** (garder la mienne) copie vos valeurs dans l'enregistrement. Il refuse ce qu'il ne peut pas relire, et dit d'utiliser Restaurer ou Detach.
  - **Restaurer** jette votre modification et reconstruit à partir de l'enregistrement.
- Un mécanisme en attente met aussi en attente chaque mécanisme qui utilise ses os, jusqu'à ce que vous le régliez.
- Une courbe remodelée, c'est pareil. Si vous remodelez la courbe d'un Follow (**Curve** cochée) dans l'éditeur de graphe puis changez une valeur qui la remplacerait, comme sa Target Range, le message du Follow se termine par « (changed by hand) ». **Keep mine** garde votre courbe. **Restaurer** la régénère.
- Une séquence en attente affiche son message et **Restaurer** dans **3. Sequences**, avec **Detach** et **Supprimer** à côté. Keep mine n'est pas proposé pour les séquences.
- **Detach** (bouton chaîne brisée) supprime l'enregistrement et les marques mais garde les os et les contraintes comme votre propre rig fait main. Detach et Supprimer refusent tous deux un enregistrement qu'un autre enregistrement utilise, et nomment les utilisateurs.
- **Supprimer** (bouton X) retire l'enregistrement et tout ce que BoneCraft a construit pour lui.
- Une boucle de liens est refusée avant toute construction, et la boucle est nommée, par exemple « Blade Hinge → Cover Follow → Blade Hinge would loop. » (formerait une boucle)

Le Validateur de Rig et le Tableau des tâches signalent les boucles de liens, les pièces manquantes, les os DEF déplacés depuis l'extérieur de leur mécanisme, les drivers qui demandent Python, et les Gear Links qui perdent une séquence ou un Follow. La vérification de nommage du validateur accepte les tirets (`CTRL-`, `MCH-`, `DEF-`), et sa vérification des drivers n'avertit que pour les expressions qui demandent Python, donc un rig Mechanisms propre n'affiche aucune erreur de validation : seulement l'avertissement unique sur l'os `root` décrit dans Limites de cette version.

## Show Helpers (afficher les aides)

**Show Helpers** est une seule préférence pour tout BoneCraft : **Préférences → Add-ons → BoneCraft → Helpers**. Désactivée, elle masque partout le texte pédagogique : les lignes quoi / quand, les notes **How this works** et les phrases complètes des étapes guidées (qui deviennent des libellés courts). Les étapes elles-mêmes, les listes, Test, les avertissements et les infobulles de survol de Blender restent toujours.

Le bouton **Mode Compact** de VRChat en est le raccourci : Mode Compact activé signifie Show Helpers désactivé.

## Limites de cette version

- Les mécanismes Click Turn, Track et Linkage viendront plus tard.
- L'export vers les moteurs du mouvement cuit des mécanismes viendra plus tard, après la vérification manuelle sur ordinateur. D'ici là, les os `DEF-` sont les os à exporter.
- BoneCraft ne détecte pas les collisions. Utilisez Test et regardez.
- Un Gear Link en rotation libre ne suit que les poignées et les engrenages.
- L'os `root` du rig n'est dans aucune collection d'os, donc la vérification des collections du Validateur de Rig l'avertit et le Tableau des tâches affiche « Rig validation warnings (1) » (avertissements de validation du rig (1)).

Suite : [Outils VRChat](08-vrchat.md)
