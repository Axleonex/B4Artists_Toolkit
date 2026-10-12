# Le pipeline CATS

[← Contenu](index.md)

**Lisez ceci avant d'utiliser un outil CATS pour la première fois.**

Les outils CATS ne sont pas un menu d'options indépendantes: ils constituent un pipeline. Chaque étape s’appuie sur la précédente. Les exécuter dans le désordre produit des résultats cassés qui restent invisibles jusqu'à ce que vous soyez déjà dans VRChat, et ils ne peuvent alors pas être corrigés sans recommencer. Vous pouvez sauter une phase dont votre avatar n'a pas besoin, mais les phases que vous exécutez doivent conserver cet ordre.

---

## Les six phases, dans l'ordre

L'état du pipeline de l'onglet CATS répertorie les phases et coche chacune d'entre elles une fois terminée :

1. **Fix Model** — Nettoyez le maillage : supprimez les doublons et la géométrie cassée, corrigez les normales. Toutes les autres étapes dépendent de celle-ci.

2. **Material Atlas** — Combinez les matériaux de l'avatar en une seule feuille de texture (facultatif, pour les performances).

3. **Visemes** — Générez les 15 formes de bouche lip-sync VRChat à partir de vos trois formes de base (A, O, CH).

4. **Eye Tracking** — Configurez le mouvement des yeux de VRChat avec les os des yeux de votre avatar.

5. **Pose to Shape Key** — Capturez des poses ou des expressions personnalisées sous forme de clés de forme.

6. **Apply All Transforms** — Gelez toutes les positions, rotations et échelles afin que votre avatar dispose de transformations propres à télécharger.

---

## État du Pipeline et Registre des Opérations

L'état du pipeline affiche une ligne par phase. Lorsqu'une phase se termine, sa ligne affiche une coche. Le statut est conservé dans la scène, il reste donc avec votre fichier.

Le registre des opérations répertorie chaque opération CATS que vous avez exécutée, la plus récente en dernier, avec son heure et son résultat : modifié (le modèle a été modifié), nettoyé (rien à modifier) ou échoué. **Copy** met le registre dans le presse-papiers (utile lorsque vous demandez de l'aide) ;**Clear** le vide.

L'ordre est un conseil, pas un verrou : un outil dont la phase précédente n'est pas terminée s'exécute toujours, mais affiche un avertissement tel que "Exécutez d'abord le modèle de correction pour de meilleurs résultats". Prenez l'avertissement au sérieux.

---

## Pourquoi cet ordre

Chaque phase modifie le maillage ou le squelette d'une manière dont la suivante dépend :

- **Fix Model doit être le premier** car il modifie le nombre de sommets, supprime les doublons et corrige les normales. Tout outil qui lit les positions des sommets (génération de visèmes, détection des os de l'œil, capture de pose) produit des résultats erronés sur un maillage qui comporte encore des sommets en double ou cassés.

- **Visémes avant Eye Tracking** car les deux modifient la clé de forme et les données osseuses. Dans cet ordre, les clés de forme existent avant que les contraintes ne soient écrites.

- **Suivi oculaire avant Pose to Shape**, car Pose to Shape capture l'intégralité du maillage, y compris la déformation provoquée par les os. Avec les contraintes oculaires en place en premier, la position neutre de l'œil dans la forme enregistrée est correcte.

- **Appliquer les transformations en dernier** car cela gèle tout pour de bon. Toute géométrie non corrigée, clés de forme non mappées ou contraintes incorrectes sont verrouillées. Après avoir appliqué les transformations, les seuls moyens de revenir à une phase antérieure sont d'annuler (Ctrl+Z) ou de réimporter à partir du fichier source.

---

## Ce qui casse si vous sautez une étape

**Ignorer le modèle de correction :**
Chaque outil ultérieur fonctionne sur un maillage qui peut contenir des sommets en double à la même position. Un visème généré peut alors déplacer le sommet visible mais pas sa copie cachée, donc dans VRChat, les deux se séparent et déchirent la bouche à chaque forme de synchronisation labiale. Le suivi oculaire peut attacher ses contraintes au maillage oculaire en double au lieu de celui visible, verrouillant les yeux dans un regard fixe. Apply Transforms intègre ensuite toutes ces erreurs.

**Passer les visèmes :**
Sans visèmes générés ou cartographiés, votre avatar n'a pas de synchronisation labiale. Si votre avatar possède déjà des clés de forme de visème, mappez-les dans VRChat Viseme Mapping (Guide 8) au lieu d'en générer de nouvelles ; L'état du pipeline affiche alors Visemes non coché, ce qui est très bien.

** Ignorer le suivi oculaire :**
Votre avatar n'a aucun mouvement oculaire dans VRChat et regarde droit devant lui. C'est acceptable lorsqu'il n'a pas d'os oculaire.

**Passer la pose à la forme :**
Facultatif : ignorez-le si vous n'avez aucune expression personnalisée à enregistrer.

Suivant: [Outils de plate-forme](05-rig-tools.md)
