# Ghost Tool 4.3.1 - Guide d'utilisation

Traduction automatique de l’édition anglaise 4.3.1, sans certification professionnelle. Les noms des commandes restent en anglais pour correspondre à l’interface. [Source anglaise](../../GhostTool_User_Manual.md).

Ghost Tool pour Bforartists affiche des maillages fantômes, des trajectoires et des marqueurs de mouvement modifiables. La version 4.3.1 intègre à ce guide la barre d'outils directe de la vue 3D, les nombres Before/Ahead séparés, les paramètres accessibles par appui long, le déplacement continu des marqueurs et la restauration actualisée des marqueurs d'instantané.

Ce guide accompagne le [ZIP d'installation Ghost Tool 4.3.1](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Mettre à jour les sources du dépôt ne met pas automatiquement à jour l'extension installée : installez le nouveau ZIP et redémarrez Bforartists. Consultez les [notes de version](../../releases/4.3.1/RELEASE-NOTES.md) et le [reçu du paquet](../../releases/4.3.1/package-receipt.json) pour sa version et sa somme de contrôle.

## Installer et trouver Ghost Tool

Téléchargez `b4_ghost_tool_v4.3.1.zip` et installez-le via Edit > Preferences > Add-ons > Install from Disk. Activez Ghost Tool et redémarrez Bforartists après le remplacement d'une version installée. Vérifiez que Preferences indique 4.3.1. Un ancien ZIP installe toujours sa version d'origine.

Par défaut, Ghost Tool utilise Top Toolbar dans la ligne native Tool Settings de la vue 3D. Avec les en-têtes natifs en haut, cette ligne se trouve juste sous l'en-tête principal et suit son alignement. Les préférences proposent aussi Right Sidebar (N) et Left Tool Shelf (T). L'ancien choix enregistré Top Header migre vers la barre visible ; la préférence s'appelle désormais Top Toolbar.

Les commandes natives d'outil et de mode restent accessibles. Dans les vues étroites ou divisées, tous les outils Ghost conservent leur ordre ; faites glisser horizontalement la ligne avec le bouton central de la souris pour atteindre les commandes hors champ. Si elles sont masquées, choisissez View > Show Ghost Toolbar. Enregistrez normalement les préférences pour conserver l'affichage.

## Démarrage rapide : examiner une cible animée

Sélectionnez un objet animé ou un os en mode Pose et activez la première icône de fantôme. Cliquez sur Ghosts pour afficher les aperçus des maillages ; réglez Before et Ahead séparément. Choisissez Wire ou Solid pour leur apparence. Maintenez Ghosts enfoncé pour choisir l'échantillonnage par pas d'images ou par images clés et régler Opacity, Fade ou In Front.

Cliquez sur Paths pour afficher une trajectoire. Si aucune cible de trajectoire n'existe, cette action peut ajouter la cible animée sélectionnée. Utilisez Add Selected Path pour une autre cible, ou Follow Selection pour un aperçu suivant la sélection. Activez Markers Display pour afficher les points modifiables d'une trajectoire conservée dans la liste.

Cliquez sur Drag, puis sélectionnez et déplacez les marqueurs dans la vue 3D. Validez un déplacement et sélectionnez un autre marqueur sans relancer Drag. Cliquez à nouveau sur Drag ou appuyez sur Escape pour quitter. Avant de modifier, maintenez Drag enfoncé pour choisir l'effet du relâchement sur l'animation.

## Lire la barre supérieure de gauche à droite

**Ghost Tool :** la première icône active ou désactive l'ensemble de l'outil, indépendamment du bouton d'affichage des maillages Ghosts. La désactivation arrête aussi les modes d'édition des marqueurs et des poignées. Maintenez l'icône enfoncée pour Update Meshes While Scrubbing, Update Markers While Scrubbing et Freeze Updates.

**Ghosts :** cliquez pour afficher ou masquer les maillages fantômes. Les champs Before et Ahead adjacents ont chacun des boutons moins et plus. Wire Ghosts et Solid Ghosts sélectionnent explicitement le style. Masquer les maillages conserve le style choisi ; sélectionner un style ne remplace pas la commande de visibilité.

**Paths :** affiche ou masque les trajectoires. Ses propres champs Before et Ahead sont suivis de Add Selected Path et Follow Selection. Les cibles ajoutées restent présentes lorsque vous sélectionnez un autre objet ou os. Follow Selection ajoute un aperçu pour la sélection courante. Les cibles de trajectoire et les marqueurs d'édition épinglés sont deux notions distinctes.

**Drag :** lance le mode continu Drag Markers. **Pin :** lance la sélection d'un marqueur à épingler ou désépingler. **Markers Display :** le losange immédiatement à droite de Pin affiche ou masque les marqueurs de trajectoire modifiables. Les infobulles donnent le nom des outils.

**Arc Style :** un simple clic ouvre directement Solid, Speed Colored et Fade. Ce réglage contrôle l'arc de mouvement des fantômes, pas le style Wire/Solid des maillages. Les trajectoires ont leur propre Line Style dans leur menu d'appui long. **Spacing Ticks :** active les repères d'espacement ; maintenez le bouton pour Acceleration Indicators.

**Settings :** ouvre les commandes avancées de génération des marqueurs, cibles, plages, édition, comparaison, physique et apparence. Generate et Clear ne sont plus répétés comme icônes autonomes dans la barre supérieure ; ils restent accessibles dans les commandes avancées.

## Régler les nombres Before et Ahead

Ghosts et Paths ont chacun deux nombres. Le premier, Before, demande des échantillons avant l'image courante ; le second, Ahead, après celle-ci. Ce sont des nombres indépendants, pas une densité globale. Modifiez directement un nombre ou utilisez moins/plus dans la barre supérieure. Zéro désactive les échantillons du côté concerné.

Le nombre indique combien d'échantillons demander ; l'échantillonnage détermine leur emplacement. À l'image 20, Ghosts Before 3, Ahead 2 et un pas de 2 demandent les images précédentes 18, 16, 14 et suivantes 22, 24, sous réserve de l'animation disponible et des limites de plage. La pose à la tête de lecture ne fait pas partie de ces échantillons.

By Keyframe utilise les clés d'animation de la cible plutôt que des images régulièrement espacées ; son intervalle peut sauter des clés. Modifier les nombres de Paths sélectionne la fenêtre fondée sur ces nombres autour de la tête de lecture. Les modes avancés de plage d'images restent accessibles dans Settings avec leurs propres règles.

## Maintenir un outil pour accéder aux paramètres

Un clic ordinaire exécute l'action principale. Un appui prolongé sur un bouton compatible ouvre ses paramètres. Arc Style fait exception : un clic ouvre immédiatement ses trois choix. Settings ouvre son panneau avancé par un clic normal.

**Appui long sur Ghosts :** choisissez l'échantillonnage par pas d'images ou par images clés. Le premier affiche Every (Frames) : 1 signifie chaque image. Le second affiche Keyframe Interval, avec un intervalle personnalisé possible. Opacity, In Front et Fade règlent l'apparence.

**Appui long sur Paths :** choisissez l'échantillonnage et son intervalle d'images ou de clés. Line Style, Frame Numbers et Bezier Handles règlent l'affichage. Activez Bezier Handles pour examiner ou modifier les poignées des courbes.

**Appui long sur Markers Display :** modifiez l'échantillonnage partagé avec Motion Paths, affichez les points des images clés et activez les numéros d'images des marqueurs. Ce menu est disponible dans la barre supérieure. Il n'existe pas de troisième mode d'échantillonnage indépendant pour les marqueurs : une modification ici change aussi Paths.

**Appui long sur Drag :** réglez When Released, Curve Shape ou Smooth Neighbours selon le mode, Nearby Frame Reach et Falloff. **Sur Pin :** consultez les instructions ou choisissez Unpin All Markers. **Sur Follow Selection :** réglez Highlight Active Path. **Sur Spacing Ticks :** choisissez Acceleration Indicators.

## Utiliser la barre inférieure de la Timeline

La bande compacte Ghost se trouve sur la même ligne que les boutons natifs de la Timeline, sans seconde ligne personnalisée en dessous. La mise à jour documentaire 4.3.1 ne remanie pas cette bande.

Son ordre est : activation générale ; affichage des maillages Ghosts ; nombres de maillages avant et après ; Wire et Solid ; Drag Markers ; losange des marqueurs modifiables ; affichage Paths ; nombres de trajectoire avant et après. Chaque paire suit le même ordre antérieur/postérieur que la barre supérieure.

Maintenez Ghosts ou Paths dans la Timeline pour Frame by Frame, By Keyframe, les intervalles et les paramètres d'affichage. More Ghost Settings ouvre les options complètes. Le losange inférieur bascule directement les marqueurs ; son menu d'appui long distinct se trouve sur Markers Display dans la barre supérieure. Les instantanés sont accessibles via Compare dans les paramètres avancés, pas par un bouton inférieur.

## Déplacer plusieurs marqueurs à la suite

Activez Ghost Tool et affichez les marqueurs modifiables d'une cible animée. Drag prépare la sélection ; le texte d'état demande de cliquer sur un marqueur dans la vue 3D. Un clic dans une zone vide laisse la sélection en attente : rapprochez-vous d'un marqueur visible. Après validation d'un déplacement, Drag reste actif. Tous les boutons lançant Drag Markers partagent ce mode.

Cliquez à nouveau sur Drag ou appuyez sur Escape pour arrêter. Pendant un déplacement, Escape annule ce déplacement et rétablit les courbes et positions d'origine. Les déplacements déjà validés restent des modifications séparées ; utilisez Undo pour les annuler. Désactiver l'outil, perdre une cible, changer de fichier ou d'historique, ou arrêter l'extension termine ou annule aussi les sessions concernées.

Le déplacement des poignées de trajectoire offre également une attente continue. Affichez Bezier Handles, lancez leur déplacement et sélectionnez successivement les poignées visibles. Shift+G reste disponible. Alt bascule le comportement des poignées alignées pendant un déplacement. Escape annule le déplacement en cours et quitte le mode.

## Choisir des modifications douces ou anguleuses

Maintenez Drag et consultez When Released. Reshape Handles modifie les poignées de Bézier existantes pour faire passer la courbe par l'échantillon déplacé sans ajouter de clé. Curve Shape propose Free, Locked et Smooth : Free autorise des ajustements libres, Locked préserve les angles et Smooth redistribue l'influence des poignées sur le segment.

Insert Keyframe écrit une vraie clé à l'image du marqueur. Smooth Neighbours peut lisser les poignées des clés voisines après cette insertion. Nearby Frame Reach et Falloff règlent la participation des images environnantes à la sculpture.

La ligne visible dépend aussi de la densité des échantillons. Des échantillons espacés produisent une ligne grossière même si l'animation sous-jacente est courbe. Réduisez le pas pour examiner le résultat. Un angle peut provenir de l'interpolation, des poignées ou du mode d'édition ; ajouter seulement des échantillons d'affichage ne modifie pas la courbe d'animation.

## Épingler les marqueurs et gérer les cibles de trajectoire

Cliquez sur Pin, puis sur un marqueur visible pour basculer son épinglage. Pin sélectionne une seule fois ; ce n'est pas le mode continu Drag. Relancez-le pour un autre marqueur. Plusieurs marqueurs peuvent être épinglés. Ils restent fixes pendant le remodelage, et l'actualisation préserve les enregistrements épinglés correspondants. Maintenez Pin et choisissez Unpin All Markers pour les libérer ensemble.

Ajouter une cible conserve l'objet ou l'os dans la liste des trajectoires sans figer tous ses échantillons d'animation. Follow Selection change l'aperçu de sélection tout en conservant les cibles ajoutées explicitement. Gérez ces cibles dans la liste de Settings. Markers Display affiche les points modifiables des trajectoires conservées ; Keyframe Dots est une aide d'affichage distincte.

## Actualisation en direct et édition native

Live Update Markers et Live Update Skin sont désactivés par défaut ; les scènes existantes gardent leurs valeurs enregistrées. Sans ces options, parcourir les images conserve le dernier aperçu actualisé. Modifiez ce comportement via les options sous l'icône générale. Freeze Updates suspend aussi les actualisations automatiques.

Pendant les déplacements, rotations, changements d'échelle et gestes de gizmo natifs, Ghost conserve le dernier aperçu au lieu de parcourir les images d'animation. Après validation ou annulation, il attend la stabilisation des modifications puis actualise les fantômes existants. Auto-key peut rester actif ; sans lui, insérez la clé voulue après validation de la pose. Generate, dans les commandes avancées des marqueurs, permet une régénération explicite.

Les commandes avancées conservent Marker Targets, les sources de pelure d'oignon, les plages, la subdivision et l'apparence. La visibilité des marqueurs et peaux en cache affiche ou masque les aperçus existants sans les reconstruire. Clear All Ghosts supprime les marqueurs et les pelures d'oignon ; utilisez les commandes de visibilité pour seulement les masquer. Les marqueurs masqués ne peuvent être sélectionnés ni par clic ni par rectangle.

## Enregistrer, comparer et restaurer des instantanés

Ouvrez Compare via Settings. Avant Save Snapshot, choisissez la portée : Active Object / Selected Bones, Selected Path, canaux des marqueurs sélectionnés ou scène explicite. Vérifiez la cible indiquée. Les instantanés conservent les échantillons figés et les clés/poignées capturées ; ils restent dans la scène après enregistrement/réouverture ou désactivation/réactivation de l'extension.

Hide/Show change la superposition sans modifier l'animation. Save Variant crée une variante indépendante avec son origine enregistrée ; supprimer le parent préserve la variante. À dix instantanés conservés, supprimez les enregistrements inutiles avant d'en ajouter. Capture, variantes, liaison, visibilité, suppression et restauration participent à Undo/Redo natif.

Restore valide l'identité de la scène, de l'objet, de l'action, du slot, de l'os et du canal avant d'écrire. Il restaure les courbes et enregistrements de marqueurs dans la portée capturée puis actualise l'affichage, même si les mises à jour sont désactivées ou figées. Il ne restaure ni les objets sans rapport ni les modificateurs Action arbitraires. Les anciennes références contenant seulement des échantillons restaurent les valeurs adaptées là où les courbes peuvent être remodelées.

Une cible remplacée exige une liaison explicite. Les slots d'action partagés sont refusés : rendez d'abord l'animation indépendante, à utilisateur unique. Bind to Active Target accepte un objet d'origine et ses canaux d'os nommés par référence. Les références importées à plusieurs objets restent visibles et non liées, sans être rabattues sur une seule cible. Les renommages d'os sont suivis. Après réouverture, l'identité du canal identifie la courbe ; pendant un geste, une courbe remplacée ne reçoit pas les écritures d'annulation destinées à l'originale.

## Transférer les instantanés et utiliser les outils avancés

Exportez les instantanés en JSON pour transférer les données de comparaison. L'import valide et fusionne les enregistrements, remappe les collisions d'identifiants et rejette atomiquement les versions non prises en charge ou les dépassements de capacité. Les références importées et anciennes restent visibles, mais exigent une liaison explicite pour restaurer : JSON ne prouve pas l'identité de l'objet d'origine. Un échec d'import préserve les enregistrements de scène existants illisibles.

Edit Motion conserve les préréglages et réglages personnalisés d'accélération. Draw to Keys convertit le plus long trait d'annotation en trajectoire de position ; les traits transversaux identifient les clés. Sa boîte de dialogue conserve la cible sélectionnée. Physics Feel, Look, Compare et les autres outils avancés restent accessibles via Settings et les emplacements alternatifs de barre latérale/étagère.

## Dépannage et notes de version

Si rien n'apparaît, vérifiez l'activation de la première icône, l'animation de la cible, l'affichage concerné et des nombres supérieurs à zéro. Pour les points modifiables absents, ajoutez la cible à Paths et activez Markers Display. Davantage d'échantillons peuvent nécessiter un pas plus petit ou un autre intervalle de clés. Les marqueurs suivent l'échantillonnage de Paths.

Si la barre manque, choisissez Top Toolbar dans les préférences Ghost puis View > Show Ghost Toolbar. Si elle est tronquée dans une vue divisée, faites défiler horizontalement la ligne native. Les préférences de largeur de l'étagère gauche restent disponibles ; leur vérification complète selon largeur/échelle était inachevée en 4.2.11. Cette version ne promet donc pas la correction de tous ces cas.

L'implémentation des outils directs a reçu 188 vérifications ciblées en arrière-plan avant cette mise à jour de version/documentation : interface, édition, trajectoires, instantanés, démarrage, emplacement et affichage en cache. Ces résultats concernent l'implémentation déjà testée. L'archive 4.3.1 a fait l'objet de contrôles séparés d'intégrité ZIP, de métadonnées et de correspondance octet par octet des sources ; ce conditionnement ne revendique aucune nouvelle exécution de tests fonctionnels. Dans le [suivi des problèmes](https://github.com/Axleonex/B4Artists_Toolkit/issues), indiquez la cible, l'opération et l'étape qui échoue.
