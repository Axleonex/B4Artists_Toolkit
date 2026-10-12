# Guides 8–13

[← Contenu](index.md)

## Guide 8: configurer la synchronisation labiale

> **Durée :** Environ 10 à 20 minutes
> **Résultat :** La bouche de votre avatar bouge correctement lorsque vous parlez en VRChat

**Avant de commencer, vérifiez ceci :**
- [] Le maillage de la tête de votre avatar comporte des clés de forme de bouche (également appelées formes de mélange ou cibles de morphing – les différentes positions de la bouche pour parler)
- [] Vous savez à peu près comment sont nommées les clés de forme (regardez dans la liste Clés de forme des propriétés de données d'objet du maillage)

> Visème = une forme de bouche pour un son. `aa` est le son « ahh », `O` le son « ohh », et ainsi de suite. VRChat utilise 15 visèmes pour piloter la synchronisation labiale de votre avatar.
>
> Clé de forme (forme de mélange) = une version enregistrée de votre maillage dans une autre position. Votre clé de forme bouche ouverte est votre maillage avec la bouche ouverte.

---

### Étape 1 — Ouvrir VRChat Viseme Mapping

Dans l'onglet **CATS** de la barre latérale droite, développez**Avatar Tools** →**VRChat Viseme Mapping**.

---

### Étape 2 — Mapper automatiquement les visèmes

Cliquez sur **Auto-Map All Visemes**. BoneCraft lit les clés de forme de votre maillage et les associe par leur nom aux 15 emplacements de visème de VRChat.

**Ce que vous devriez voir :** La liste des visèmes, avec la plupart des emplacements affichant une clé de forme mappée.

---

### Étape 3 — Remplir les emplacements manquants

Un emplacement sans clé de forme affiche "(non mappé)". Cliquez sur le bouton d'un emplacement pour ouvrir une liste de recherche des clés de forme de votre maillage et choisissez la plus proche (tapez pour filtrer la liste). Choisissez "(non mappé)" pour libérer un emplacement. Correspondances courantes :

|VRChat visème|À quoi ça ressemble|Clé de forme à rechercher|
|---|---|---|
|`aa` |"ahh"|bouche_ouverte, A, aa|
|`O` |"ohh"|bouche_o, OH, oh|
|`CH` |"ch" / "sh"|bouche_ch, CH|
|`PP` |lèvres ensemble (P, B, M)|bouche_m, MM, lèvres_ensemble|
|`SS` |"sss" / "zzz"|bouche_s, SS|

**Aucune clé de forme de visème ?** Si la bouche a au moins trois formes de base (A, O et CH), la section**Visemes** de l'onglet CATS crée les 15 à partir d'elles. Sans aucune forme de bouche, faites ces trois-là en premier. Voir [Guide 13, Phase 2](#phase-2--génération-des-visèmes).

---

### Étape 4 — Vérifier une forme de bouche

Pour voir une forme de bouche mappée, définissez la valeur de sa clé de forme sur 1,0 dans la liste Clés de forme du maillage (Propriétés → Données d'objet), puis remettez-la à 0.

---

### Étape 5 — Suivi facial (facultatif)

Sous la liste des visèmes, **Face Tracking (SteamVR)** prépare les formes d'expression pour le matériel de suivi du visage. C'est facultatif: la plupart des utilisateurs n'en ont pas besoin.

**Ce que cela débloque :** La bouche de votre avatar bouge lorsque vous parlez dans VRChat. Les expressions s'appuient sur les clés de forme que vous venez de mapper.

---

## Guide 9: améliorer les performances de votre avatar

> **Durée :** Environ 15 à 25 minutes
> **Résultat :** Un meilleur classement des performances VRChat et un chargement plus rapide pour les autres joueurs

**Avant de commencer, vérifiez ceci :**
- [] Votre avatar est complet (gréé, habillé, configuration de synchronisation labiale)
- [] Vous connaissez votre classement cible (Bon ou Excellent pour la plupart des utilisateurs)

> Classement des performances = note de VRChat sur l'exigence de votre avatar. Les avatars très médiocres peuvent être cachés par d'autres joueurs. Les avatars Bon et Excellent se chargent rapidement et sont toujours affichés.

---

### Étape 1 — Vérifier le rang actuel

Dans l'onglet **CATS**, développez**VRChat Tools** et recherchez son groupe Performance. Cliquez sur**Calculate Performance Rank**. BoneCraft affiche le classement global et une répartition (polygones, maillages skinnés, emplacements de matériaux, os, PhysBones et contacts) avec la distance de chacun par rapport au niveau suivant.

---

### Étape 2 — Nettoyer

L'optimiseur VRChat dans la même section répertorie les correctifs sûrs. **What-If Mode** est activé au début : chaque correctif indique ce qu'il changerait sans rien changer. Décochez-la, car les correctifs ne sont signalés que lorsqu'il est activé, et exécutez les correctifs souhaités :

1. **Remove Zero-Weight Bones** — supprime les os qui ne déplacent aucune partie du maillage
2. **Merge Same-Material Meshes** — joint les maillages qui partagent un matériau
3. **Remove Unused Shape Keys** — supprime les clés de forme que rien n'utilise
4. **Remove Unused Vertex Groups** — supprime les groupes de poids vides

---

### Étape 3 — Réduire le nombre de polygones (si nécessaire)

Si le nombre de polygones est trop élevé, utilisez la décimation VRChat dans la même section avec le maillage sélectionné : définissez le rapport cible (0,5 réduit de moitié les polygones, 0,8 supprime 20 %), cliquez sur **Preview** pour voir le résultat et sur**Apply** pour le conserver. Les clés de forme sont protégées lors de la décimation.

> Commencez à 0,8 et travaillez vers le bas: de petites réductions modifient rarement l'apparence de l'avatar mais peuvent améliorer considérablement les performances.

---

### Étape 4 — Fusionner les matériaux (facultatif)

Si votre avatar utilise de nombreux matériaux, combinez-les en une seule feuille de texture (un atlas). Dans l'onglet **CATS** →**CATS** →**Material Atlas**:

1. Cliquez sur **Analyze** pour voir vos matériaux et textures. Choisissez lesquels inclure.
2. Cliquez sur **Smart Combine Materials** (ou**Bake Atlas** pour une cuisson nature). BoneCraft prépare l'atlas et pointe chaque maillage vers lui ; une sauvegarde des originaux est conservée.
3. Cliquez sur **Accept — Delete Backup** pour conserver le résultat, ou sur**Revert — Restore Originals** pour revenir en arrière.

[Outils CATS  : Combineur Atlas de matériaux](09-cats.md#combinateur-datlas-de-matériaux) explique chaque paramètre.

---

### Étape 5 — Vérifier de nouveau le rang

Cliquez à nouveau sur **Calculate Performance Rank** pour voir l'amélioration.

**Ce que cela débloque :** Un meilleur classement signifie que davantage de joueurs voient votre avatar. Un avatar Bon ou Excellent se charge rapidement, utilise moins de GPU et est présenté par défaut aux autres joueurs.

---

## Guide 10: enregistrer et réutiliser des poses

> **Durée :** Environ 5 à 10 minutes
> **Résultat :** Une bibliothèque enregistrée de poses que vous pouvez appliquer en un seul clic

**Avant de commencer, vérifiez ceci :**
- [] Votre avatar a un squelette fini
- [] Vous êtes dans **Pose Mode** (sélectionnez l'armature et appuyez sur Ctrl+Tab, ou utilisez la liste déroulante des modes en haut à gauche de la fenêtre)

---

### Étape 1 — Ouvrir la bibliothèque de poses

Dans l'onglet **BoneCraft** sur l'étagère à outils de gauche, développez**Review** →**Pose Library**.

---

### Étape 2 — Poser votre avatar

Déplacez les os dans la position que vous souhaitez conserver: faites pivoter les bras, inclinez la tête – toute combinaison de positions des os est une pose.

---

### Étape 3 — Enregistrer la pose

Cliquez sur **Save** et donnez un nom à la pose (par exemple « Signe de paix » ou « Pensée »).**Category** le classe dans un groupe tel que « Salutations » ; le**Filter** en haut affiche une catégorie à la fois. Une vignette de la fenêtre est capturée avec la pose.

---

### Étape 4 — Appliquer une pose enregistrée

Sélectionnez une pose et cliquez sur **Apply**.

- **Blend** — applique la pose à force partielle, pour mélanger deux poses
- **Mirror** — applique la pose inversée de gauche à droite

**Rename** et**Delete** gèrent la liste.

---

### Étape 5 — Exporter et importer des poses

**Export** enregistre votre bibliothèque de poses dans un fichier `.bfpose` que vous pouvez conserver avec le projet ou partager.**Import** charge les poses à partir d'un fichier `.bfpose`.

**Ce que cela débloque :** Une bibliothèque de poses personnelle que vous pouvez réutiliser dans plusieurs projets, mélanger pour des clés d'animation ou partager avec d'autres utilisateurs de BoneCraft.

---

## Guide 11: fusionner deux rigs

> **Durée :** Environ 25 à 40 minutes selon la complexité
> **Résultat :** Deux squelettes combinés en un seul, avec tous les poids conservés

**Avant de commencer, vérifiez ceci :**
- [] L'avatar de base et le deuxième rig (un vêtement ou un accessoire) sont dans le même fichier
- [] Les deux sont gréés et lestés

> Rig merge = absorber un squelette dans un autre, vous vous retrouvez donc avec un squelette combiné. Utile lorsqu'un body rig et un hair ou une tenue doivent ne faire qu'un.

---

### Étape 1 — Ouvrir Fusion d'Os

Dans l'onglet **BoneCraft**, développez la section**Bone Merge**. Cela fonctionne en trois étapes ; chacun s'ouvre lorsque celui qui le précède est terminé.

---

### Étape 2 — Stade 1: périmètre

Choisissez l'armature **Base** (le squelette du corps qui reste) et l'armature qui s'y fond (le vêtement ou la coiffure, qui est ajouté à la base puis caché). Cliquez sur**Analyze**.

BoneCraft compare les deux squelettes et répertorie :
- ✓ Correspondants : os qui existent dans les deux et s'alignent
- \+ Source uniquement — os du rig fusionné sans correspondance dans la base
- − Cible uniquement – les os de base que la rig de fusion n'a pas

Lorsque vous avez lu la liste, cliquez sur **Acknowledge Scope — Proceed to Rename**.

---

### Étape 3 — Stade 2: renommage

Pour chaque os source uniquement, décidez de quoi il s’agit :

- Donnez-lui le nom de l'os de base qu'il représente et cliquez sur **Apply Rename**
- Cliquez sur **Mark as Unique** s'il s'agit d'un nouvel os sans équivalent (il est ajouté à la base tel quel)

**Normalize Both Armatures** renomme les os standard (colonne vertébrale, bras, jambes, etc.) que BoneCraft reconnaît dans les deux rigs.**Auto-Propose Renames** suggère des noms pour le reste à partir de la position de chaque os ;**Apply Batch Pattern** renomme de nombreux os avec un seul motif.

Lorsque chaque os source uniquement est résolu, cliquez sur **Verify Rename — Proceed to Merge**.

---

### Étape 4 — Stade 3: fusion

Cliquez d'abord sur **Run Merge Preview**  : il indique ce que fera la fusion sans rien changer.

Lorsque le rapport semble correct, cliquez sur **Merge Armatures**. BoneCraft sauvegarde les deux armatures, puis les combine.

**Ce que vous devriez voir :** Une armature contenant tous les os des deux squelettes, avec chaque maille pondérée dessus.

**Ce que cela débloque :** Une rig unique plus facile à exporter et à modifier. Nécessaire pour tout avatar avec des vêtements ou des accessoires séparés.

---

## Guide 12: résoudre les problèmes d'envoi

> **Durée :** Environ 5 à 15 minutes selon le problème

**Avant de commencer :** Recherchez votre problème dans la liste ci-dessous et accédez à cette section.

---

### « Échec de l'envoi — os non reconnus »

Vos os portent des noms que VRChat ne comprend pas. → [Guider 4 : Corrigez les noms d'os de votre avatar](02-guides-a.md#guide-4-corriger-les-noms-dos-de-votre-avatar)

---

### « L'avatar est en T-pose / ne bouge pas avec moi dans VRChat »

La cartographie humanoïde est manquante ou erronée. → [Guide 5 : Mappez votre avatar sur le système corporel de VRChat](02-guides-a.md#guide-5-mapper-votre-avatar-sur-le-système-corporel-de-vrchat)

---

### « Le maillage se déforme bizarrement / la peau s'étire mal »

Les poids des os doivent être ajustés. → Voir Transfert de poids et Miroir de poids dans [Outils de plate-forme](05-rig-tools.md), ou exécutez **Smart Automatic Weights** dans l'onglet CATS.

---

### « Les cheveux traversent la tête »

Les collisionneurs de cheveux sont manquants ou trop petits. → [Guide 6 : Ajouter la physique des cheveux](02-guides-a.md#guide-6-ajouter-la-physique-des-cheveux), étape 5.

---

### « L'avatar est en performance Very Poor et bloqué par les autres joueurs »

→ [Guide 9 : Améliorez les performances de votre avatar](#guide-9-améliorer-les-performances-de-votre-avatar)

---

### « La synchronisation labiale ne marche pas »

Les visèmes ne sont pas cartographiés correctement. → [Guider 8 : Configurer la synchronisation labiale](#guide-8-configurer-la-synchronisation-labiale)

---

### « Le validateur de rig affiche des erreurs »

Dans l'onglet **BoneCraft**, développez**Review** →**Rig Validator** et cliquez sur**Run Validation**. Chaque résultat nomme le problème et l'os; suivez sa suggestion ou vérifiez le [Index des solutions rapides](10-reference.md#index-des-solutions-rapides).**Export Report** enregistre les résultats dans un fichier.

---

### « L'import VRM ne marche pas »

Le module complémentaire VRM n’est peut-être pas installé. → [Guider 2](02-guides-a.md#guide-2-amener-un-avatar-vroid-dans-vrchat), étape 1.

---

### « L'import MMD ne marche pas »

Le module complémentaire mmd_tools n'est peut-être pas installé. → [Guider 3](02-guides-a.md#guide-3-amener-un-avatar-mmd-dans-vrchat), étape 1.

---

## Guide 13: préparer votre avatar pour VRChat avec CATS

> **Durée :** Environ 20 à 35 minutes pour une exécution complète du pipeline
> **Résultat :** Un avatar épuré et optimisé avec synchronisation labiale, suivi oculaire et transformations correctes — prêt pour le téléchargement VRChat

**Avant de commencer, lisez ceci en premier :**

Les outils CATS suivent un pipeline: chaque phase doit être réalisée dans l'ordre. L'état du pipeline de l'onglet CATS affiche une coche pour chaque phase que vous avez effectuée (Corriger le modèle, Atlas des matériaux, Visèmes, Suivi oculaire, Pose à la forme, Appliquer les transformations) et le Registre des opérations répertorie chaque opération CATS que vous avez exécutée. Un outil dont la phase précédente n'est pas terminée s'exécute toujours, mais affiche un avertissement tel que « Exécutez d'abord le modèle de correction pour de meilleurs résultats ».

** Commencez toujours par Fix Model. À chaque fois. Sans exception.**

Lisez [Le pipeline CATS](04-cats-pipeline.md) avant de continuer, si ce n'est pas déjà fait.

**Avant de commencer, vérifiez ceci :**
- [] Votre avatar est importé et visible dans la fenêtre 3D
- [] L'onglet CATS est ouvert dans la barre latérale droite (appuyez sur N si la barre latérale est masquée)
- [] Votre avatar est sélectionné (cliquez dessus dans la fenêtre ou dans l'aperçu)

---

### Phase 1 — Corriger le modèle

Fix Model est la base obligatoire pour tout le reste dans CATS. Exécutez-le en premier, même si votre modèle semble correct : il supprime les problèmes cachés qui, autrement, interrompraient silencieusement les outils suivants.

**Ce que fait Fix Model** (chaque partie peut être désactivée dans ses options) :
- Applique des modificateurs
- Supprime les sommets en double et la géométrie lâche (triangles flottant loin du corps)
- Recalcule les normales (les directions qui décident quel côté du maillage est tourné vers l'extérieur)
- Supprime les groupes de sommets vides et les os de poids nul
- Supprime les contraintes et les corps rigides que VRChat ne peut pas utiliser

**Étapes :**
1. Dans l'onglet **CATS**, développez**CATS** →**Fix Model**
2. Assurez-vous que le maillage de votre avatar est sélectionné
3. Cliquez sur **Fix Model** et attendez — pour les grands maillages, cela prend quelques secondes
4. Vérifiez que l'état du pipeline affiche une coche ( ✓) pour le modèle de correction.

**Ce que vous devriez voir :** Votre avatar est identique ou légèrement plus propre. L'état du pipeline vérifie le modèle de correction et le grand livre des opérations répertorie l'exécution.

> **Si votre modèle disparaît ou semble à l'envers après la correction du modèle :** les normales du maillage ont été inversées. Sélectionnez le maillage, entrez en mode édition (onglet), sélectionnez tout (A), puis utilisez Maillage > Normales > Retourner. Ensuite, exécutez à nouveau Fix Model.

---

### Phase 2 — Génération des visèmes

Courir après : corriger le modèle ✓

La section Visemes crée les 15 formes de bouche lip-sync VRChat à partir de trois formes de base que vous possédez déjà. Si votre avatar dispose déjà de clés de forme de visème complètes, vous pouvez ignorer cette phase, mais vérifiez-les dans VRChat Viseme Mapping (Guide 8).

VRChat a besoin de 15 formes de bouche (visèmes) pour diriger les lèvres de votre avatar lorsque vous parlez. La plupart des avatars n’ont que quelques formes de bouche de base. CATS combine vos formes de base pour faire le reste.

Les trois formes de base:
- **A Shape** — bouche grande ouverte (la forme « ahh »)
- **O Shape** — bouche arrondie (la forme « ohh »)
- **CH Shape** — bouche ouverte étroite avec des dents visibles (la forme « ch » / « sh »)

**Étapes :**
1. Dans l'onglet **CATS**, développez**CATS** →**Visemes**
2. Cliquez sur **Auto-Detect** pour remplir les trois formes, ou choisissez-les vous-même (pour les clés nommées comme `mouth_open`, `vrc.v_O` ou `mouth_wide`, choisissez la correspondance la plus proche).
3. Cliquez sur **Generate Visemes**
4. CATS crée 15 clés de forme avec les noms de VRChat (`vrc.v_aa`, `vrc.v_O`, `vrc.v_CH` et ainsi de suite)
5. Vérifiez que l'état du pipeline affiche Visèmes ✓

**Ce que vous devriez voir :** 15 nouvelles clés de forme dans la liste des clés de forme du maillage (Propriétés → Données d'objet → Clés de forme).

> **Si votre avatar n'a aucune clé de forme de bouche :** créez vous-même au moins A, O et CH (sculptez-les ou modifiez-les en tant que clés de forme) avant que CATS puisse générer le reste. Voir l'entrée du glossaire pour la clé de forme.

---

### Phase 3 — Suivi Oculaire

Courir après : corriger le modèle ✓

Eye Tracking configure les os des yeux de votre avatar pour le suivi oculaire intégré du VRChat, afin que les yeux bougent naturellement et regardent les autres joueurs.

**Ce qu'il fait :**
- Trouve les os des yeux gauche et droit
- Les nomme comme VRChat requis (`LeftEye` et `RightEye` )
- Ajoute les contraintes de rotation dont VRChat a besoin pour déplacer les yeux
- Limite la rotation des yeux à une plage naturelle (vers le haut, le bas et sur le côté)

Sans corriger le modèle au préalable, la détection des yeux peut se verrouiller sur les sommets en double restants au lieu des yeux réels et placer les contraintes au mauvais endroit – les avatars arrivent dans VRChat avec les deux yeux coincés vers le bas.

**Étapes :**
1. Dans l'onglet **CATS**, développez**CATS** →**Eye Tracking**
2. Cliquez sur **Auto-Detect** — CATS recherche les os dont les noms ou les positions correspondent aux os de l'œil.
3. Vérifiez les champs **Left Eye** et**Right Eye**  ; ramasser les os vous-même s'ils sont faux
4. Réglez les **Up Limit**,**Down Limit** et**Side Limit** si nécessaire
5. Cliquez sur **Create Eye Tracking**
6. Vérifiez que l'état du pipeline affiche Eye Tracking ✓

**Ce que vous devriez voir :** Les deux os de l'œil ont été renommés, avec des contraintes de rotation dans le panneau Contraintes osseuses.

> **Si CATS ne trouve pas d'os oculaires :** votre squelette n'en a peut-être pas. Certains formats (en particulier les anciens modèles MMD ) clignotent avec des clés de forme au lieu d'os. Ignorer cette phase : VRChat revient à l'animation oculaire à clé de forme lorsqu'il n'y a pas d'os oculaires.

---

### Phase 4 — Pose en Clé de Forme

Courir après : corriger le modèle ✓

Pose to Shape Key transforme la pose actuelle de votre avatar en clé de forme. Utilisez-le pour capturer des expressions personnalisées ou des poses de repos pour le menu d'expressions de VRChat.

Sans corriger le modèle au préalable, l'ordre des sommets peut toujours contenir des espaces provenant des doublons supprimés, de sorte que la clé de forme capture la géométrie déformée - des clés de forme qui font exploser le maillage vers l'extérieur lorsqu'elles sont déclenchées dans VRChat.

**Étapes :**
1. Posez votre avatar en mode Pose (sélectionnez l'armature, appuyez sur Ctrl+Tab)
2. Déplacez les os dans l'expression ou la position que vous souhaitez capturer
3. Revenir en mode objet (Ctrl+Tab à nouveau)
4. Dans l'onglet **CATS**, développez**CATS** →**Pose & Shape Keys**
5. Cliquez sur **Pose to Shape Key** et nommez la nouvelle clé de forme
6. Vérifiez que l'état du pipeline indique Pose à la forme ✓

**Ce que vous devriez voir :** Une nouvelle clé de forme dans la liste des maillages. Définissez sa valeur sur 1,0 pour vérifier qu'il affiche la pose.

> **Clé de forme de base :** l'outil compagnon fait le contraire : il intègre une clé de forme dans la forme restante neutre du maillage. Utilisez-le pour verrouiller une pose de repos corrigée. Exécutez-le également après Fix Model.

---

### Phase 5 — Appliquer les transformations

Courir après : chaque phase antérieure dont vous avez besoin

La dernière phase. Appliquer des transformations gèle toutes les positions, rotations et échelles dans le maillage et le squelette, de sorte que tout se lit comme des valeurs propres (position 0,0,0 / rotation 0°,0°,0° / échelle 1,0). Le SDK VRChat nécessite des transformations propres: une échelle non appliquée en particulier fait apparaître les avatars à la mauvaise taille ou avec une physique qui se comporte mal.

L'application des transformations avant les phases précédentes intègre définitivement leurs problèmes dans le maillage - des avatars qui semblent corrects dans Bforartists mais apparaissent à une fraction de leur hauteur dans VRChat.

**Les outils de Transforms & FBT :**
- **Apply All Transforms** — applique la position, la rotation et l'échelle au maillage et à l'armature ensemble
- **Fix FBT** — une correction de transformation pour les configurations de suivi complet du corps (déplace l'os racine au niveau du sol)
- **Remove FBT** — supprime à nouveau cette correction

**Étapes :**
1. Confirmez que les phases dont votre avatar a besoin sont cochées dans l'état du pipeline (Atlas des matériaux et Pose en forme sont facultatifs, et Visèmes reste décoché lorsque vous avez mappé des visèmes existants à la place).
2. Dans l'onglet **CATS**, développez**CATS** →**Transforms & FBT**
3. Cliquez sur **Apply All Transforms**
4. Vérifiez que l'état du pipeline affiche Appliquer les transformations ✓
5. Exportez votre avatar (VRChat → Exporter vers VRChat, Guide 1 Étape 9)

**Ce que vous devriez voir :** Cochée Appliquer les transformations, après les phases dont vous aviez besoin. Votre avatar est prêt pour le compagnon créateur VRChat.

---

**Ce que cela débloque :** Un avatar entièrement traité avec une géométrie épurée, les 15 visèmes, un suivi oculaire (lorsqu'il comporte des os oculaires), toutes les expressions personnalisées que vous avez créées et des transformations nettes : tout ce dont un téléchargement VRChat a besoin pour fonctionner du premier coup.

Suivant: [Le pipeline CATS](04-cats-pipeline.md)
