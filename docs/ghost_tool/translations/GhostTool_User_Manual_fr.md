# Ghost Tool 4.3.1 : guide d'utilisation

Traduction du [guide anglais 4.3.1](../GhostTool_User_Manual.md). Les noms anglais des commandes sont conservés pour retrouver les boutons dans Bforartists. Cette traduction n'a pas fait l'objet d'une révision linguistique professionnelle.

Ghost Tool pour Bforartists affiche des maillages fantômes, des trajectoires et des repères de mouvement modifiables. Ce guide de la version 4.3.1 décrit la barre d'outils directe de la vue, les nombres distincts Before/Ahead, les réglages accessibles par appui prolongé, le déplacement répété des repères et la restauration actualisée des repères d'instantanés.

Ce guide accompagne le [ZIP d'installation de Ghost Tool 4.3.1](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Une mise à jour du dépôt ne met pas automatiquement à jour l'extension installée : installez le nouveau ZIP et redémarrez Bforartists. Consultez les [notes de version](../releases/4.3.1/RELEASE-NOTES.md) et le [relevé du paquet](../releases/4.3.1/package-receipt.json) pour connaître la version et la somme de contrôle.

## Installer et retrouver Ghost Tool

Téléchargez `b4_ghost_tool_v4.3.1.zip`, puis installez-le via Edit > Preferences > Add-ons > Install from Disk. Activez Ghost Tool et redémarrez Bforartists après avoir remplacé une version installée. Vérifiez que Preferences indique 4.3.1. Un ancien ZIP installe toujours sa version d'origine.

Ghost Tool utilise par défaut Top Toolbar, dans la ligne native Tool Settings de la vue 3D. Lorsque les en-têtes sont en haut, cette ligne apparaît juste sous l'en-tête principal et suit son alignement. Preferences propose aussi Right Sidebar (N) et Left Tool Shelf (T). Les anciens choix enregistrés Top Header migrent vers la barre visible ; cette préférence s'appelle désormais Top Toolbar.

Les commandes natives d'outil et de mode restent disponibles. Une vue étroite ou divisée conserve tous les outils Ghost dans le même ordre. Faites glisser la ligne horizontalement avec le bouton central de la souris pour atteindre les outils hors écran. Si les commandes sont masquées, choisissez View > Show Ghost Toolbar. Enregistrez normalement les préférences pour conserver l'affichage choisi.

## Démarrage rapide : examiner une cible animée

Sélectionnez un objet animé ou un os de pose et activez la première icône de fantôme. Cliquez sur Ghosts pour afficher les aperçus de maillage et réglez Before et Ahead séparément. Choisissez Wire ou Solid pour leur apparence. Maintenez Ghosts pour choisir un échantillonnage par pas d'images ou par images clés, puis régler l'opacité, l'atténuation ou In Front.

Cliquez sur Paths pour afficher une trajectoire. En l'absence de cible de trajectoire, l'action peut ajouter la cible animée sélectionnée. Utilisez Add Selected Path pour ajouter une autre cible, ou Follow Selection pour suivre la sélection courante. Activez Markers Display pour faire apparaître les points modifiables d'une trajectoire ajoutée à la liste.

Cliquez sur Drag, puis sélectionnez et déplacez des repères dans la vue 3D. Validez un déplacement, puis choisissez un autre repère sans relancer Drag. Cliquez de nouveau sur Drag ou appuyez sur Escape pour quitter le mode. Avant de modifier le mouvement, maintenez Drag pour choisir l'effet du relâchement sur l'animation.

## Lire la barre supérieure de gauche à droite

**Ghost Tool :** la première icône active ou désactive l'ensemble de l'outil. Elle est distincte du bouton Ghosts qui affiche les maillages. La désactivation arrête aussi les modes d'édition des repères et poignées. Maintenez-la pour Update Meshes While Scrubbing, Update Markers While Scrubbing et Freeze Updates.

**Ghosts :** cliquez pour afficher ou masquer les maillages fantômes. Les nombres Before et Ahead possèdent chacun des boutons moins et plus. Wire Ghosts et Solid Ghosts sélectionnent explicitement le style. Masquer les maillages conserve ce style ; choisir un style n'est pas une commande de visibilité.

**Paths :** affiche ou masque les trajectoires. Ses propres nombres Before et Ahead sont suivis de Add Selected Path et Follow Selection. Les cibles ajoutées restent présentes quand vous sélectionnez un autre objet ou os. Follow Selection ajoute un aperçu de la sélection courante. Une cible de trajectoire et un repère épinglé pour l'édition sont deux notions différentes.

**Drag :** lance le mode persistant Drag Markers. **Pin :** demande de sélectionner un repère pour l'épingler ou le libérer. **Markers Display :** le bouton en losange immédiatement à droite de Pin affiche ou masque les repères modifiables des trajectoires. Les info-bulles portent le nom de chaque outil.

**Arc Style :** un simple clic ouvre directement Solid, Speed Colored et Fade. Ce réglage concerne l'arc de mouvement Ghost, pas le style Wire ou Solid des maillages. Paths possède son propre Line Style dans son menu d'appui prolongé. **Spacing Ticks :** affiche ou masque les indicateurs d'espacement ; maintenez ce bouton pour Acceleration Indicators.

**Settings :** ouvre les commandes avancées de génération de repères, cibles, plages, édition, comparaison, physique et apparence. Generate et Clear ne sont plus répétés sous forme d'icônes indépendantes dans la ligne supérieure. Ces opérations restent disponibles dans les commandes avancées.

## Régler les nombres Before et Ahead

Deux nombres accompagnent Ghosts et deux autres Paths. Le premier, Before, compte les échantillons antérieurs à l'image courante. Le second, Ahead, compte les échantillons ultérieurs. Ce sont des nombres indépendants, pas un réglage unique de densité. Modifiez directement un nombre ou utilisez ses boutons moins et plus dans la barre supérieure. Zéro désactive les échantillons de ce côté.

Les nombres indiquent combien d'échantillons demander ; l'échantillonnage détermine leurs positions. Avec la tête de lecture à l'image 20, Ghosts Before 3, Ahead 2 et un pas de 2, les échantillons demandés sont 18, 16 et 14 avant, puis 22 et 24 après, selon les limites de plage et l'animation disponible. La pose de l'image courante n'est pas comptée parmi eux.

By Keyframe utilise les clés d'animation de la cible plutôt que des images régulièrement espacées. Son intervalle peut sauter des clés. Modifier les nombres de Paths sélectionne la fenêtre fondée sur le nombre d'échantillons autour de la tête de lecture. Les plages d'images avancées restent accessibles dans Settings et suivent leurs propres règles.

## Maintenir un outil pour ouvrir ses réglages

Un clic ordinaire exécute l'action principale. Maintenez un bouton compatible pour ouvrir ses paramètres. Arc Style fait exception : un clic ouvre immédiatement ses trois choix. Settings ouvre aussi son panneau avancé avec un clic normal.

**Maintenir Ghosts :** choisissez le pas d'images ou les images clés. Le premier mode expose Every (Frames) ; 1 échantillonne chaque image. Le second expose Keyframe Interval, avec un intervalle personnalisé. Les réglages d'apparence sont Opacity, In Front et Fade.

**Maintenir Paths :** choisissez l'échantillonnage et son intervalle en images ou en clés. Line Style, Frame Numbers et Bezier Handles règlent l'affichage. Activez Bezier Handles pour examiner ou modifier les poignées des courbes.

**Maintenir Markers Display :** modifiez l'échantillonnage partagé avec Motion Paths, affichez les points d'images clés et les numéros d'images des repères. Ce menu est dans la barre supérieure. Les repères n'ont pas de troisième mode d'échantillonnage indépendant : changer ce réglage modifie aussi celui de Paths.

**Maintenir Drag :** réglez When Released, Curve Shape ou Smooth Neighbours selon le mode, Nearby Frame Reach et Falloff. **Maintenir Pin :** consultez les instructions ou choisissez Unpin All Markers. **Maintenir Follow Selection :** réglez Highlight Active Path. **Maintenir Spacing Ticks :** choisissez Acceleration Indicators.

## Utiliser la barre inférieure de la Timeline

La bande Ghost compacte se trouve sur la même ligne que les commandes natives de la Timeline. Ce n'est pas une deuxième ligne personnalisée sous sa barre d'outils. La mise à jour documentaire 4.3.1 ne redessine pas cette bande.

Son ordre est : activation générale ; affichage des maillages Ghosts ; nombres de maillages avant/après ; Wire et Solid ; Drag Markers ; losange des repères modifiables ; affichage Paths ; nombres de trajectoire avant/après. Dans chaque paire, l'ordre est le même que dans la barre supérieure : avant, puis après.

Maintenez Ghosts ou Paths dans la Timeline pour Frame by Frame, By Keyframe, les intervalles et l'affichage. More Ghost Settings ouvre les options complètes. Le losange inférieur est un interrupteur direct ; son menu distinct se trouve sur Markers Display dans la barre supérieure. Les instantanés se trouvent dans Compare, via les réglages avancés, pas dans la bande inférieure.

## Déplacer plusieurs repères successivement

Activez Ghost Tool et affichez les repères modifiables d'une cible animée. Drag arme le sélecteur ; la barre d'état demande de cliquer sur un repère dans la vue 3D. Un clic dans le vide le laisse en attente : rapprochez-vous d'un repère visible. Après validation d'un déplacement, Drag reste actif pour le suivant. Tous les boutons Drag Markers partagent ce mode.

Cliquez de nouveau sur Drag ou appuyez sur Escape pour l'arrêter. Escape pendant un déplacement annule ce déplacement et restaure ses courbes et positions initiales. Les déplacements déjà validés sont des modifications distinctes ; annulez-les avec Undo. Désactiver l'outil, perdre une cible, changer de fichier ou d'état d'historique, ou désactiver l'extension termine ou annule aussi les sessions concernées.

Le déplacement des poignées de trajectoire possède également un mode d'attente persistant. Affichez Bezier Handles, lancez leur outil de déplacement et sélectionnez successivement des poignées visibles. Shift+G reste disponible. Alt bascule l'alignement des poignées pendant le déplacement. Escape annule le déplacement de poignée en cours et quitte le mode.

## Choisir un mouvement lisse ou anguleux

Maintenez Drag et examinez When Released. Reshape Handles modifie les poignées de Bézier existantes pour faire passer la courbe par le point déplacé, sans ajouter de clé. Curve Shape propose Free, Locked et Smooth : Free libère le réglage des poignées ; Locked conserve leurs angles ; Smooth redistribue leur influence sur le segment.

Insert Keyframe écrit une véritable clé à l'image du repère. Smooth Neighbours peut lisser les poignées des clés voisines après cette insertion. Nearby Frame Reach et Falloff déterminent la participation des images proches à la sculpture du mouvement.

La ligne visible dépend aussi de la densité d'échantillonnage. Des points très espacés produisent une ligne grossière même si l'animation sous-jacente est courbe. Réduisez le pas pour examiner le résultat. Un angle net peut venir de l'interpolation, des poignées ou du mode d'édition ; augmenter seulement les points d'affichage ne change pas la forme de la courbe d'animation.

## Épingler des repères et gérer les cibles de trajectoire

Cliquez sur Pin, puis sur un repère visible pour l'épingler ou le libérer. Pin est une sélection ponctuelle, pas le mode persistant Drag : relancez-le pour un autre repère. Vous pouvez épingler plusieurs repères, pas seulement un seul. Ils restent fixes pendant le remodelage et un rafraîchissement conserve les enregistrements épinglés correspondants. Maintenez Pin et choisissez Unpin All Markers pour tous les libérer.

Ajouter une cible de trajectoire conserve l'objet ou l'os dans la liste ; cela ne fige pas tous ses échantillons d'animation. Follow Selection modifie l'aperçu de sélection tandis que les cibles explicitement ajoutées restent. Gérez celles-ci dans la liste de Paths sous Settings. Markers Display commande les points modifiables des trajectoires ajoutées ; Keyframe Dots est une aide d'affichage distincte.

## Mises à jour en direct et édition native

Live Update Markers et Live Update Skin sont désactivés par défaut ; les scènes existantes conservent leurs valeurs enregistrées. Lorsqu'ils sont désactivés, déplacer la tête de lecture conserve le dernier aperçu actualisé. Utilisez les options sous l'icône principale pour changer ce comportement. Freeze Updates suspend aussi les rafraîchissements automatiques.

Pendant les déplacements, rotations, changements d'échelle et manipulations natives des gizmos, Ghost conserve l'aperçu au lieu de parcourir les images. Après validation ou annulation, il attend la stabilisation des modifications puis actualise les fantômes existants. Auto-key peut rester activé ; sinon, insérez la clé voulue après validation de la pose. Generate dans les commandes avancées régénère explicitement les repères si nécessaire.

Les commandes avancées conservent Marker Targets, les sources d'onion skin, la plage, la subdivision et l'apparence. La visibilité des repères et peaux mis en cache affiche ou masque leurs aperçus sans les reconstruire. Clear All Ghosts supprime repères et onion skins ; utilisez plutôt la visibilité pour simplement les masquer. Les repères masqués ne peuvent être ni cliqués ni sélectionnés par rectangle.

## Enregistrer, comparer et restaurer des instantanés

Ouvrez Compare via Settings. Avant Save Snapshot, choisissez la portée : Active Object / Selected Bones, Selected Path, canaux des repères sélectionnés ou portée explicite de scène. Vérifiez la cible affichée. Les instantanés conservent échantillons figés et clés/poignées capturées. Ils sont enregistrés dans la scène et survivent à sa réouverture ainsi qu'à la désactivation/réactivation de l'extension.

Hide/Show modifie la surimpression d'un instantané sans changer l'animation. Save Variant crée une variante indépendante avec son origine enregistrée ; supprimer le parent préserve la variante. À dix instantanés conservés, supprimez-en un avant d'en ajouter un autre. Capture, variantes, liaison, visibilité, suppression et restauration participent à Undo/Redo natif.

Restore vérifie l'identité de la scène, de l'objet, de l'action, du slot, de l'os et du canal avant écriture. Il restaure les courbes et repères capturés dans la portée de l'instantané puis actualise l'affichage, même si les mises à jour en direct sont arrêtées ou gelées. Il ne restaure ni objets sans rapport ni modificateurs arbitraires d'Action. Les anciens instantanés d'échantillons seuls restaurent les valeurs adaptées lorsque les courbes peuvent être remodelées.

Une cible remplacée exige une liaison volontaire. Les slots d'action partagés sont refusés : rendez d'abord l'animation indépendante. Bind to Active Target accepte un objet d'origine et ses canaux d'os nommés par référence. Une référence importée multi-objets reste visible et non liée, sans être réduite à une cible. Les renommages d'os sont suivis. Après réouverture, l'identité de canal identifie la courbe ; pendant un geste, une courbe remplacée ne reçoit pas l'annulation destinée à l'originale.

## Transférer des instantanés et utiliser les outils avancés

Exportez les instantanés en JSON pour transférer les données de comparaison. L'import valide et fusionne les enregistrements, remappe les identifiants en collision et rejette de façon atomique les versions non prises en charge ou le dépassement de capacité. Les références importées ou anciennes restent visibles, mais leur restauration exige une liaison explicite : JSON ne prouve pas l'identité de l'objet d'origine. Un import qui échoue préserve les enregistrements de scène existants illisibles.

Edit Motion conserve les préréglages et réglages personnalisés d'easing. Draw to Keys transforme le plus long trait d'annotation en trajectoire de position ; les tirets transversaux indiquent les clés. Sa boîte de dialogue conserve la cible sélectionnée. Physics Feel, Look, Compare et les autres outils avancés restent accessibles par Settings et les emplacements alternatifs de barre latérale ou d'étagère.

## Dépannage et remarques de version

Si rien n'apparaît, vérifiez la première icône Ghost, l'animation de la cible, l'activation de l'affichage voulu et des nombres supérieurs à zéro. Si les points modifiables manquent, ajoutez la cible à Paths et activez Markers Display. Davantage de points visibles peuvent nécessiter un pas réduit ou un autre intervalle de clés. L'échantillonnage des repères suit celui de Paths.

Si la barre manque, choisissez Top Toolbar dans les préférences et View > Show Ghost Toolbar. Si elle est tronquée dans une vue divisée, faites défiler la ligne horizontalement. Les préférences de largeur de l'étagère gauche restent disponibles ; leur vérification complète de largeur/échelle était inachevée en 4.2.11. Cette version ne prétend donc pas corriger tous ces cas.

L'implémentation des outils directs a passé 188 vérifications ciblées en arrière-plan avant cette mise à jour de version/documentation : interface, édition, trajectoires, instantanés, démarrage, emplacement et cache. Ces résultats concernent cette implémentation précédemment vérifiée. L'archive 4.3.1 a aussi été contrôlée pour l'intégrité ZIP, la version et la correspondance exacte du code source ; cette étape de packaging ne revendique aucun nouveau test fonctionnel. Signalez la cible, l'opération et l'étape en échec dans le [suivi des problèmes](https://github.com/Axleonex/B4Artists_Toolkit/issues).
