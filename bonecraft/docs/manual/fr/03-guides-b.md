# Guides 8–13

[← Sommaire](index.md)

## Guide 8 : configurer la synchronisation labiale

`CATS → VRChat Tools → Facial`

> **Durée :** environ 10 à 20 minutes
> **Résultat :** la bouche de votre avatar qui bouge correctement quand vous parlez dans VRChat

**Avant de commencer, vérifiez ces points :**
- [ ] Le maillage de la tête de votre avatar a des clés de forme de bouche (aussi appelées blend shapes ou morph targets : les différentes positions de la bouche pour parler)
- [ ] Vous savez à peu près comment s'appellent les clés de forme (regardez la liste Clés de forme dans les propriétés Données de l'objet du maillage)

> Visème = une forme de bouche pour un son. `aa` est le son « ah », `O` le son « oh », et ainsi de suite. VRChat utilise 15 visèmes pour animer la synchronisation labiale de votre avatar.
>
> Clé de forme (blend shape) = une version enregistrée de votre maillage dans une autre position. Votre clé de forme bouche ouverte, c'est votre maillage avec la bouche ouverte.

---

### Étape 1 — Ouvrir VRChat Viseme Mapping

Dans l'onglet **CATS → VRChat Tools → Facial** → VRChat Viseme Mapping.

---

### Étape 2 — Mapper automatiquement les visèmes

Cliquez sur **Mapper tous les visèmes automatiquement**. BoneCraft lit les clés de forme de votre maillage et les associe par leur nom aux 15 emplacements de visèmes de VRChat.

**Ce que vous devriez voir :** la liste des visèmes, la plupart des emplacements affichant une clé de forme mappée.

---

### Étape 3 — Remplir les emplacements manquants

Un emplacement sans clé de forme affiche « (unmapped) » (non mappé). Cliquez sur le bouton d'un emplacement pour ouvrir une liste de recherche des clés de forme du maillage, et choisissez la plus proche (tapez pour filtrer la liste). Choisissez « (unmapped) » pour vider un emplacement. Correspondances courantes :

| Visème VRChat | Son | Clé de forme à chercher |
|---|---|---|
| `aa` | « ah » | mouth_open, A, aa |
| `O` | « oh » | mouth_o, OH, oh |
| `CH` | « tch » / « ch » | mouth_ch, CH |
| `PP` | lèvres fermées (P, B, M) | mouth_m, MM, lips_together |
| `SS` | « sss » / « zzz » | mouth_s, SS |

**Aucune clé de forme de visème ?** Si la bouche a au moins trois formes de base (A, O et CH), la section **Visèmes** de l'onglet CATS crée les 15 à partir d'elles. Sans aucune forme de bouche, créez d'abord ces trois-là. Voir le [guide 13, phase 2](#phase-2--génération-des-visèmes).

---

### Étape 4 — Vérifier une forme de bouche

Pour voir une forme de bouche mappée, réglez la valeur de sa clé de forme sur 1.0 dans la liste Clés de forme du maillage (Propriétés → Données de l'objet), puis remettez-la à 0.

---

### Étape 5 — Suivi facial (facultatif)

Sous la liste des visèmes, **Suivi Facial (SteamVR)** prépare des formes d'expression pour le matériel de suivi facial. C'est facultatif : la plupart des utilisateurs n'en ont pas besoin.

**Ce que cela débloque :** la bouche de votre avatar bouge quand vous parlez dans VRChat. Les expressions s'appuient sur les clés de forme que vous venez de mapper.

---

## Guide 9 : améliorer les performances de votre avatar

`CATS → VRChat Tools → Check Performance`

> **Durée :** environ 15 à 25 minutes
> **Résultat :** un meilleur rang de performance VRChat et un chargement plus rapide pour les autres joueurs

**Avant de commencer, vérifiez ces points :**
- [ ] Votre avatar est terminé (riggé, habillé, synchronisation labiale configurée)
- [ ] Vous connaissez votre rang cible (Good ou Excellent pour la plupart des utilisateurs)

> Rang de performance = l'évaluation par VRChat de l'exigence de votre avatar. Les avatars Very Poor peuvent être masqués par les autres joueurs. Les avatars Good et Excellent se chargent vite et sont toujours affichés.

---

### Étape 1 — Vérifier le rang actuel

Dans l'onglet **CATS**, dépliez **VRChat Tools** → **Vérifier les Performances**. Cliquez sur **Calculate Performance Rank** (calculer le rang de performance). BoneCraft affiche le rang global et le détail (polygones, maillages skinnés, emplacements de matériaux, os, PhysBones et contacts), avec l'écart de chacun par rapport au niveau suivant.

---

### Étape 2 — Nettoyer

L'Optimiseur VRChat de la même section liste des corrections sûres. Le **Mode Hypothétique** est activé au départ : chaque correction indique ce qu'elle changerait sans rien modifier. Décochez-le, car les corrections ne font que rendre compte tant qu'il est actif, et lancez les corrections voulues :

1. **Supprimer les Os de Poids Zéro** — supprime les os qui ne déplacent aucune partie du maillage
2. **Fusionner les maillages de même matériau** — joint les maillages qui partagent un matériau
3. **Supprimer les Clés de Forme Non Utilisées** — supprime les clés de forme que rien n'utilise
4. **Supprimer les Groupes de Sommets Non Utilisés** — retire les groupes de poids vides

---

### Étape 3 — Réduire le nombre de polygones (si nécessaire)

Si le nombre de polygones est trop élevé, utilisez la Décimation VRChat de la même section avec le maillage sélectionné : réglez le ratio cible (0.5 divise les polygones par deux, 0.8 en retire 20 %), cliquez sur **Aperçu** pour voir le résultat, et sur **Appliquer** pour le garder. Les clés de forme sont protégées pendant la décimation.

> Commencez à 0.8 et descendez : de petites réductions changent rarement l'apparence de l'avatar mais peuvent beaucoup améliorer les performances.

---

### Étape 4 — Fusionner les matériaux (facultatif)

Si votre avatar utilise beaucoup de matériaux, combinez-les en une seule planche de texture (un atlas). Dans l'onglet **CATS** → **CATS** → **Atlas de Matériaux** :

1. Cliquez sur **Analyze** (analyser) pour voir vos matériaux et textures. Choisissez ceux à inclure.
2. Cliquez sur **Smart Combine Materials** (combinaison intelligente des matériaux) (ou **Cuire l'atlas** pour une cuisson simple). BoneCraft cuit l'atlas et fait pointer chaque maillage vers lui ; une sauvegarde des originaux est conservée.
3. Cliquez sur **Accepter — Supprimer la sauvegarde** pour garder le résultat, ou sur **Revenir — Restaurer les Originaux** pour revenir en arrière.

[Outils CATS : Combinateur d'atlas de matériaux](09-cats.md#combinateur-datlas-de-matériaux) explique chaque réglage.

---

### Étape 5 — Vérifier de nouveau le rang

Cliquez de nouveau sur **Calculate Performance Rank** pour voir l'amélioration.

**Ce que cela débloque :** un meilleur rang signifie que plus de joueurs voient votre avatar. Un avatar Good ou Excellent se charge vite, utilise moins le GPU, et est montré par défaut aux autres joueurs.

---

## Guide 10 : enregistrer et réutiliser des poses

`BoneCraft → Review → Pose Library`

> **Durée :** environ 5 à 10 minutes
> **Résultat :** une bibliothèque de poses enregistrées que vous appliquez en un clic

**Avant de commencer, vérifiez ces points :**
- [ ] Votre avatar a un squelette terminé
- [ ] Vous êtes en **Mode Pose** (sélectionnez l'armature et appuyez sur Ctrl+Tab, ou utilisez le menu déroulant des modes en haut à gauche de la vue)

---

### Étape 1 — Ouvrir la bibliothèque de poses

Dans l'onglet **BoneCraft** de la Tool Shelf de gauche, dépliez **Révision** → **Bibliothèque de Poses**.

---

### Étape 2 — Poser votre avatar

Déplacez les os dans la position à garder : faites pivoter les bras, inclinez la tête. Toute combinaison de positions d'os est une pose.

---

### Étape 3 — Enregistrer la pose

Cliquez sur **Sauvegarder** et donnez un nom à la pose (par exemple « Peace Sign » ou « Thinking »). **Catégorie** la range dans un groupe comme « Greetings » ; le **Filtre** en haut affiche une catégorie à la fois. Une vignette de la vue est capturée avec la pose.

---

### Étape 4 — Appliquer une pose enregistrée

Sélectionnez une pose et cliquez sur **Appliquer**.

- **Mélanger** — applique la pose avec une intensité partielle, pour mélanger deux poses
- **Miroir** — applique la pose inversée de gauche à droite

**Renommer** et **Supprimer** gèrent la liste.

---

### Étape 5 — Exporter et importer des poses

**Exporter** enregistre votre bibliothèque de poses dans un fichier `.bfpose` que vous pouvez garder avec le projet ou partager. **Importer** charge des poses depuis un fichier `.bfpose`.

**Ce que cela débloque :** une bibliothèque de poses personnelle, réutilisable d'un projet à l'autre, à mélanger pour des clés d'animation ou à partager avec d'autres utilisateurs de BoneCraft.

---

## Guide 11 : fusionner deux rigs

`BoneCraft → Setup Rigging → Bone Merge`

> **Durée :** environ 25 à 40 minutes selon la complexité
> **Résultat :** deux squelettes combinés en un seul, avec tous les poids conservés

**Avant de commencer, vérifiez ces points :**
- [ ] L'avatar de base et le second rig (un rig de vêtement ou d'accessoire) sont dans le même fichier
- [ ] Les deux sont riggés et ont des poids

> Fusion de rigs = absorber un squelette dans un autre, pour obtenir un seul squelette combiné. Utile quand un rig de corps et un rig de cheveux ou de tenue doivent n'en faire qu'un.

---

### Étape 1 — Ouvrir Fusion d'Os

Dans l'onglet **BoneCraft → Setup Rigging**, dépliez la section **Fusion d'Os**. Elle fonctionne en trois stades ; chacun s'ouvre quand le précédent est terminé.

---

### Étape 2 — Stade 1 : périmètre

Choisissez l'armature **Base** (le squelette du corps, qui reste) et l'armature qui fusionne dedans (le rig de vêtement ou de cheveux, ajouté à la base puis masqué). Cliquez sur **Analyze** (analyser).

BoneCraft compare les deux squelettes et liste :
- ✓ Matched (correspondants) — os présents des deux côtés et alignés
- \+ Source only (source seulement) — os du rig fusionné sans correspondance dans la base
- − Target only (cible seulement) — os de la base que le rig fusionné n'a pas

Quand vous avez lu la liste, cliquez sur **Acknowledge Scope — Proceed to Rename** (valider le périmètre — passer au renommage).

---

### Étape 3 — Stade 2 : renommage

Pour chaque os « source seulement », décidez ce qu'il est :

- Donnez-lui le nom de l'os de base qu'il représente, et cliquez sur **Apply Rename** (appliquer le renommage)
- Cliquez sur **Mark as Unique** (marquer comme unique) si c'est un nouvel os sans équivalent (il est ajouté à la base tel quel)

**Normalize Both Armatures** (normaliser les deux armatures) renomme les os standard (colonne, bras, jambes, etc.) que BoneCraft reconnaît dans les deux rigs. **Auto-Propose Renames** (proposer des renommages automatiquement) suggère des noms pour le reste d'après la position de chaque os ; **Apply Batch Pattern** (appliquer un motif par lot) renomme de nombreux os avec un seul motif.

Quand chaque os « source seulement » est réglé, cliquez sur **Verify Rename — Proceed to Merge** (vérifier le renommage — passer à la fusion).

---

### Étape 4 — Stade 3 : fusion

Cliquez d'abord sur **Run Merge Preview** (lancer l'aperçu de fusion) : il indique ce que la fusion va faire, sans rien modifier.

Quand le rapport semble correct, cliquez sur **Fusionner les Armatures**. BoneCraft sauvegarde les deux armatures, puis les combine.

**Ce que vous devriez voir :** une seule armature contenant tous les os des deux squelettes, avec chaque maillage pondéré sur elle.

**Ce que cela débloque :** un seul rig, plus facile à exporter et à modifier. Indispensable pour tout avatar avec des rigs de vêtements ou d'accessoires séparés.

---

## Guide 12 : résoudre les problèmes d'envoi

> **Durée :** environ 5 à 15 minutes selon le problème

**Avant de commencer :** trouvez votre problème dans la liste ci-dessous et allez à cette section.

---

### « Échec de l'envoi — os non reconnus »

Vos os ont des noms que VRChat ne comprend pas. → [Guide 4 : corriger les noms d'os de votre avatar](02-guides-a.md#guide-4--corriger-les-noms-dos-de-votre-avatar)

---

### « L'avatar est en T-pose / ne bouge pas avec moi dans VRChat »

Le mappage humanoïde manque ou est faux. → [Guide 5 : mapper votre avatar sur le système corporel de VRChat](02-guides-a.md#guide-5--mapper-votre-avatar-sur-le-système-corporel-de-vrchat)

---

### « Le maillage se déforme bizarrement / la peau s'étire mal »

Les poids des os doivent être ajustés. → Voir le transfert de poids et le miroir de poids dans [Outils de rig](05-rig-tools.md), ou lancez **Smart Automatic Weights** (poids automatiques intelligents) dans l'onglet CATS.

---

### « Les cheveux traversent la tête »

Les colliders de cheveux manquent ou sont trop petits. → [Guide 6 : ajouter la physique des cheveux](02-guides-a.md#guide-6--ajouter-la-physique-des-cheveux), étape 5.

---

### « L'avatar est en performance Very Poor et bloqué par les autres joueurs »

→ [Guide 9 : améliorer les performances de votre avatar](#guide-9--améliorer-les-performances-de-votre-avatar)

---

### « La synchronisation labiale ne marche pas »

Les visèmes ne sont pas mappés correctement. → [Guide 8 : configurer la synchronisation labiale](#guide-8--configurer-la-synchronisation-labiale)

---

### « Le validateur de rig affiche des erreurs »

Dans l'onglet **BoneCraft**, dépliez **Révision** → **Validateur de Rig** et cliquez sur **Exécuter la validation**. Chaque résultat nomme le problème et l'os ; suivez sa suggestion, ou consultez l'[Index des solutions rapides](10-reference.md#index-des-solutions-rapides). **Export Report** (exporter le rapport) enregistre les résultats dans un fichier.

---

### « L'import VRM ne marche pas »

L'add-on VRM n'est peut-être pas installé. → [Guide 2](02-guides-a.md#guide-2--amener-un-avatar-vroid-dans-vrchat), étape 1.

---

### « L'import MMD ne marche pas »

L'add-on mmd_tools n'est peut-être pas installé. → [Guide 3](02-guides-a.md#guide-3--amener-un-avatar-mmd-dans-vrchat), étape 1.

---

## Guide 13 : préparer votre avatar pour VRChat avec CATS

> **Durée :** environ 20 à 35 minutes pour un passage complet du pipeline
> **Résultat :** un avatar propre et optimisé, avec synchronisation labiale, suivi oculaire et transformations correctes, prêt à être envoyé sur VRChat

**Avant de commencer, lisez d'abord ceci :**

Les outils CATS suivent un pipeline : chaque phase doit être faite dans l'ordre. L'État du Pipeline de l'onglet CATS coche chaque phase terminée (Corriger le modèle, Atlas de Matériaux, Visèmes, Suivi Oculaire, Pose en Clé de Forme, Appliquer les transformations), et le Registre des Opérations liste chaque opération CATS lancée. Un outil dont la phase précédente n'est pas faite s'exécute quand même, mais affiche un avertissement comme « Run Fix Model first for best results » (lancez d'abord Corriger le modèle pour de meilleurs résultats).

**Commencez toujours par Corriger le modèle. À chaque fois. Sans exception.**

Lisez [Le pipeline CATS](04-cats-pipeline.md) avant de continuer, si ce n'est pas déjà fait.

**Avant de commencer, vérifiez ces points :**
- [ ] Votre avatar est importé et visible dans la vue 3D
- [ ] L'onglet CATS est ouvert dans la barre latérale de droite (appuyez sur N si la barre est masquée)
- [ ] Votre avatar est sélectionné (cliquez dessus dans la vue ou dans l'outliner)

---

### Phase 1 — Corriger le modèle

Corriger le modèle est la base obligatoire de tout le reste dans CATS. Lancez-le en premier, même si votre modèle semble correct : il retire des problèmes cachés qui, sinon, casseraient sans bruit les outils suivants.

**Ce que fait Corriger le modèle** (chaque partie peut être désactivée dans ses options) :
- Applique les modificateurs
- Supprime les sommets en double et la géométrie isolée (triangles qui flottent loin du corps)
- Recalcule les normales (les directions qui décident quel côté du maillage est vers l'extérieur)
- Supprime les groupes de sommets vides et les os de poids zéro
- Supprime les contraintes et les corps rigides que VRChat ne peut pas utiliser

**Étapes :**
1. Dans l'onglet **CATS**, dépliez **CATS** → **Corriger le modèle**
2. Vérifiez que le maillage de votre avatar est sélectionné
3. Cliquez sur **Corriger le modèle** et attendez ; pour les gros maillages, cela prend quelques secondes
4. Vérifiez que l'État du Pipeline affiche une coche (✓) pour Corriger le modèle

**Ce que vous devriez voir :** votre avatar a le même aspect ou un aspect un peu plus propre. L'État du Pipeline coche Corriger le modèle, et le Registre des Opérations liste le passage.

> **Si votre modèle disparaît ou semble retourné après Corriger le modèle :** les normales du maillage étaient inversées. Sélectionnez le maillage, passez en Mode Édition (Tab), sélectionnez tout (A), puis utilisez Maillage > Normales > Inverser. Relancez ensuite Corriger le modèle.

---

### Phase 2 — Génération des visèmes

À lancer après : Corriger le modèle ✓

La section Visèmes crée les 15 formes de bouche de synchronisation labiale de VRChat à partir de trois formes de base que vous avez déjà. Si votre avatar a déjà des clés de forme de visèmes complètes, vous pouvez sauter cette phase, mais vérifiez-les dans VRChat Viseme Mapping (guide 8).

VRChat a besoin de 15 formes de bouche (visèmes) pour animer les lèvres de votre avatar quand vous parlez. La plupart des avatars n'ont que quelques formes de bouche de base. CATS combine vos formes de base pour créer le reste.

Les trois formes de base :
- **Forme A** — bouche grande ouverte (la forme « ah »)
- **Forme O** — bouche arrondie (la forme « oh »)
- **Forme CH** — bouche entrouverte, dents visibles (la forme « tch » / « ch »)

**Étapes :**
1. Dans l'onglet **CATS**, dépliez **CATS** → **Visèmes**
2. Cliquez sur **Détection Automatique** pour remplir les trois formes, ou choisissez-les vous-même (pour des clés nommées comme `mouth_open`, `vrc.v_O` ou `mouth_wide`, prenez la plus proche)
3. Cliquez sur **Générer les Visèmes**
4. CATS crée 15 clés de forme avec les noms de VRChat (`vrc.v_aa`, `vrc.v_O`, `vrc.v_CH`, etc.)
5. Vérifiez que l'État du Pipeline affiche Visèmes ✓

**Ce que vous devriez voir :** 15 nouvelles clés de forme dans la liste Clés de forme du maillage (Propriétés → Données de l'objet → Clés de forme).

> **Si votre avatar n'a aucune clé de forme de bouche :** créez vous-même au moins A, O et CH (sculptez-les ou modifiez-les comme clés de forme) avant que CATS puisse générer le reste. Voir l'entrée Clé de forme du glossaire.

---

### Phase 3 — Suivi Oculaire

À lancer après : Corriger le modèle ✓

Le suivi oculaire configure les os des yeux de votre avatar pour le suivi oculaire intégré de VRChat, afin que les yeux bougent naturellement et regardent les autres joueurs.

**Ce qu'il fait :**
- Trouve les os de l'œil gauche et de l'œil droit
- Les nomme comme VRChat l'exige (`LeftEye` et `RightEye`)
- Ajoute les contraintes de rotation dont VRChat a besoin pour bouger les yeux
- Limite la rotation des yeux à une amplitude naturelle (haut, bas et côtés)

Sans Corriger le modèle d'abord, la détection des yeux peut s'accrocher à des sommets en double restants au lieu des vrais yeux, et placer les contraintes au mauvais endroit : les avatars arrivent dans VRChat avec les deux yeux bloqués vers le bas.

**Étapes :**
1. Dans l'onglet **CATS**, dépliez **CATS** → **Suivi Oculaire**
2. Cliquez sur **Détection Automatique** ; CATS cherche les os dont le nom ou la position correspond à des os d'yeux
3. Vérifiez les champs **Œil Gauche** et **Œil Droit** ; choisissez vous-même les os s'ils sont faux
4. Réglez la **Limite Supérieure**, la **Limite Inférieure** et la **Limite Latérale** si besoin
5. Cliquez sur **Créer le Suivi Oculaire**
6. Vérifiez que l'État du Pipeline affiche Suivi Oculaire ✓

**Ce que vous devriez voir :** les deux os des yeux renommés, avec des contraintes de rotation dans le panneau Contraintes d'os.

> **Si CATS ne trouve pas d'os d'yeux :** votre squelette n'en a peut-être pas. Certains formats (surtout les anciens modèles MMD) clignent avec des clés de forme plutôt qu'avec des os. Sautez cette phase : VRChat se rabat sur l'animation des yeux par clés de forme quand il n'y a pas d'os d'yeux.

---

### Phase 4 — Pose en Clé de Forme

À lancer après : Corriger le modèle ✓

Pose en Clé de Forme transforme la pose actuelle de votre avatar en clé de forme. Utilisez-la pour capturer des expressions personnalisées ou des poses de repos pour le menu d'expressions de VRChat.

Sans Corriger le modèle d'abord, l'ordre des sommets peut encore contenir des trous laissés par les doublons supprimés, et la clé de forme capture une géométrie déformée : des clés de forme qui font exploser le maillage vers l'extérieur quand elles sont déclenchées dans VRChat.

**Étapes :**
1. Posez votre avatar en Mode Pose (sélectionnez l'armature, appuyez sur Ctrl+Tab)
2. Déplacez les os dans l'expression ou la position à capturer
3. Revenez en Mode Objet (Ctrl+Tab de nouveau)
4. Dans l'onglet **CATS**, dépliez **CATS** → **Pose et Clés de Forme**
5. Cliquez sur **Pose en Clé de Forme** et nommez la nouvelle clé de forme
6. Vérifiez que l'État du Pipeline affiche Pose en Clé de Forme ✓

**Ce que vous devriez voir :** une nouvelle clé de forme dans la liste du maillage. Réglez sa valeur à 1.0 pour vérifier qu'elle montre la pose.

> **Clé de Forme en Basis :** l'outil compagnon fait l'inverse : il cuit une clé de forme dans la forme de repos neutre du maillage. Utilisez-le pour fixer une pose de repos corrigée. Lancez-le lui aussi après Corriger le modèle.

---

### Phase 5 — Appliquer les transformations

À lancer après : toutes les phases précédentes dont vous avez besoin

La dernière phase. Appliquer les transformations fige toute la position, la rotation et l'échelle dans le maillage et le squelette, pour que tout se lise avec des valeurs propres (position 0,0,0 / rotation 0°,0°,0° / échelle 1.0). Le SDK VRChat a besoin de transformations propres : une échelle non appliquée, en particulier, fait apparaître les avatars à la mauvaise taille ou avec une physique qui se comporte mal.

Appliquer les transformations avant les phases précédentes cuit définitivement leurs problèmes dans le maillage : des avatars qui semblent corrects dans Bforartists mais apparaissent dans VRChat à une fraction de leur taille.

**Les outils de Transformations et FBT :**
- **Appliquer Toutes les Transformations** — applique la position, la rotation et l'échelle au maillage et à l'armature ensemble
- **Corriger le FBT** — une correction de transformation pour les configurations Full Body Tracking (déplace l'os racine au niveau du sol)
- **Supprimer le FBT** — retire de nouveau cette correction

**Étapes :**
1. Vérifiez que les phases dont votre avatar a besoin sont cochées dans l'État du Pipeline (Atlas de Matériaux et Pose en Clé de Forme sont facultatifs, et Visèmes reste non coché si vous avez mappé des visèmes existants)
2. Dans l'onglet **CATS**, dépliez **CATS** → **Transformations et FBT**
3. Cliquez sur **Appliquer Toutes les Transformations**
4. Vérifiez que l'État du Pipeline affiche Appliquer les transformations ✓
5. Exportez votre avatar (VRChat → Exporter vers VRChat, guide 1 étape 9)

**Ce que vous devriez voir :** Appliquer les transformations coché, après les phases dont vous aviez besoin. Votre avatar est prêt pour le VRChat Creator Companion.

---

**Ce que cela débloque :** un avatar entièrement traité, avec une géométrie propre, les 15 visèmes, le suivi oculaire (quand il a des os d'yeux), les expressions personnalisées que vous avez créées et des transformations propres : tout ce qu'il faut pour qu'un envoi sur VRChat fonctionne du premier coup.

Suite : [Le pipeline CATS](04-cats-pipeline.md)
