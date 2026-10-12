# Le pipeline CATS

[← Sommaire](index.md)

**Lisez ceci avant d'utiliser un outil CATS pour la première fois.**

Les outils CATS ne sont pas un menu d'options indépendantes : ils forment un pipeline. Chaque étape s'appuie sur la précédente. Les lancer dans le désordre produit des résultats cassés qui restent invisibles jusqu'à ce que vous soyez déjà dans VRChat, et à ce moment-là, on ne peut plus les corriger sans tout recommencer. Vous pouvez sauter une phase dont votre avatar n'a pas besoin, mais les phases que vous lancez doivent garder cet ordre.

---

## Les six phases, dans l'ordre

L'État du Pipeline de l'onglet CATS liste les phases et coche chacune quand elle est terminée :

1. **Corriger le modèle** — Nettoyer le maillage : retirer les doublons et la géométrie cassée, corriger les normales. Toutes les autres étapes en dépendent.

2. **Atlas de Matériaux** — Combiner les matériaux de l'avatar en une seule planche de texture (facultatif, pour les performances).

3. **Visèmes** — Générer les 15 formes de bouche de synchronisation labiale de VRChat à partir de vos trois formes de base (A, O, CH).

4. **Suivi Oculaire** — Configurer le mouvement des yeux de VRChat avec les os des yeux de votre avatar.

5. **Pose en Clé de Forme** — Capturer des poses ou expressions personnalisées sous forme de clés de forme.

6. **Appliquer Toutes les Transformations** — Figer toute la position, la rotation et l'échelle pour que votre avatar ait des transformations propres à l'envoi.

---

## État du Pipeline et Registre des Opérations

L'État du Pipeline affiche une ligne par phase. Quand une phase se termine, sa ligne affiche une coche. L'état est conservé dans la scène, donc il reste avec votre fichier.

Le Registre des Opérations liste chaque opération CATS lancée, la plus récente en dernier, avec son heure et son résultat : Changed (elle a modifié le modèle), Clean (rien n'avait besoin de changer) ou Failed (échec). **Copier** met le registre dans le presse-papiers (utile pour demander de l'aide) ; **Effacer** le vide.

L'ordre est un conseil, pas un verrou : un outil dont la phase précédente n'est pas faite s'exécute quand même, mais affiche un avertissement comme « Run Fix Model first for best results » (lancez d'abord Corriger le modèle pour de meilleurs résultats). Prenez cet avertissement au sérieux.

---

## Pourquoi cet ordre

Chaque phase modifie le maillage ou le squelette d'une façon dont la suivante dépend :

- **Corriger le modèle doit passer en premier** car il change le nombre de sommets, retire les doublons et corrige les normales. Tout outil qui lit la position des sommets (génération des visèmes, détection des os des yeux, capture de pose) produit de mauvais résultats sur un maillage qui a encore des sommets en double ou cassés.

- **Les visèmes avant le suivi oculaire** car tous deux modifient les clés de forme et les données d'os. Dans cet ordre, les clés de forme existent avant que les contraintes soient écrites.

- **Le suivi oculaire avant Pose en Clé de Forme** car Pose en Clé de Forme capture tout le maillage, y compris la déformation pilotée par les os. Avec les contraintes des yeux en place d'abord, la position neutre des yeux dans la forme enregistrée est juste.

- **Appliquer les transformations en dernier** car cela fige tout pour de bon. Toute géométrie non corrigée, toute clé de forme non mappée ou toute contrainte fausse est verrouillée. Après avoir appliqué les transformations, les seuls moyens de revenir à une phase précédente sont l'annulation (Ctrl+Z) ou la réimportation depuis le fichier source.

---

## Ce qui casse si vous sautez une étape

**Sauter Corriger le modèle :**
Chaque outil suivant travaille sur un maillage qui peut contenir des sommets en double à la même position. Un visème généré peut alors déplacer le sommet visible mais pas son doublon caché, si bien que dans VRChat les deux s'écartent et déchirent la bouche à chaque forme de synchronisation labiale. Le suivi oculaire peut attacher ses contraintes au maillage d'œil en double au lieu du visible, ce qui bloque les yeux dans un regard fixe. Appliquer les transformations grave ensuite toutes ces erreurs.

**Sauter les visèmes :**
Sans visèmes générés ou mappés, votre avatar n'a pas de synchronisation labiale. Si votre avatar a déjà des clés de forme de visèmes, mappez-les dans VRChat Viseme Mapping (guide 8) au lieu d'en générer de nouvelles ; l'État du Pipeline laisse alors Visèmes non coché, et c'est normal.

**Sauter le suivi oculaire :**
Votre avatar n'a pas de mouvement des yeux dans VRChat et regarde droit devant lui. C'est acceptable quand il n'a pas d'os d'yeux.

**Sauter Pose en Clé de Forme :**
Facultatif : sautez-le si vous n'avez pas d'expressions personnalisées à enregistrer.

Suite : [Outils de rig](05-rig-tools.md)
