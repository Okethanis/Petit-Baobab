# Petit Baobab — site de puériculture en ligne (Abidjan)

Boutique en ligne qui présente ~516 articles visibles (597 fiches dont 81 cachées) et conclut les ventes sur **WhatsApp** (pas de paiement en ligne, pas de serveur, pas de base de données). Site statique, en français.

## Comment c'est construit

- **`petit-baobab.html`** : LE fichier source unique. Il contient tout — styles (`<style>`), scripts (`<script>`), les réglages (`var CONFIG`), les adresses des pages (`var ROUTES`), et le catalogue (`var PRODUCTS`, une ligne par article).
- **`build.js`** : génère le dossier `site/` (une vraie page par adresse, 404, sitemap, robots, en-têtes de sécurité `_headers`). Commande : `node build.js`.
- **`images/`** : photos des articles en WebP (avec filigrane « Petit Baobab »).
- **`static/`** : fichiers publiés tels quels (favicons, image de partage).
- **`brand/`** : scripts Python/JS qui modifient `petit-baobab.html` de façon idempotente (police, boutons, pied de page, pages, images de packs…). Chacun se relance sans dupliquer.
- **`admin/`** : la page « Catalogue » (modifier prix/fiches) et le « Tableau de bord » (registre des commandes). Ce sont des artefacts claude.ai séparés, PAS publiés sur le site. Générés par `make-admin.js` / `make-dashboard.js`. Non versionnés (voir `.gitignore`).

## Pour voir le site en local

```
node build.js
cd site && python3 -m http.server 8000   # puis ouvrir http://localhost:8000
```

## Mise en ligne (ATTENTION aux crédits)

- Hébergé sur **Netlify** (plan gratuit : **300 crédits/mois**, cycle du 22 au 21). Chaque mise en ligne du site = **15 crédits**. Le site est coupé si on atteint 300.
- Déploiement automatique : `git push` sur la branche `main` du dépôt `Okethanis/Petit-Baobab` → Netlify reconstruit.
- `netlify.toml` ne reconstruit QUE si `petit-baobab.html`, `build.js`, `images`, `static`, `amenageur`, `photos` ou `vendor` changent. Un commit qui ne touche que `admin/`, `brand/`, `CLAUDE.md` ne coûte rien.
- **Travailler sur une branche et ouvrir une Pull Request** donne un aperçu gratuit (`deploy-preview-N--petit-baobab.netlify.app`) sans dépenser de crédits. Ne fusionner dans `main` que quand c'est validé.
- Envisager **Cloudflare Pages** (gratuit, sans crédits) avant le lancement public (TikTok, pub).

## Conventions

- Tout en français. Un seul bouton orange par page. Prix « 54 500 FCFA » avec espace fine.
- Aucune donnée sensible publiée : pas de prix d'achat, pas de packing list, pas d'adresse.
- Vérifier après chaque modif du script : `node -e "..."` pour contrôler que les `<script>` sont valides, et `node build.js` sans erreur.

## Remplacer une photo floue

- `python3 -I admin/photo.py <source> <id> --propose <dossier>` : prépare une proposition (carré 1000 px, fond blanc, marges rognées, filigrane) sans toucher au site ; sans `--propose`, remplace `images/<id>.webp`.
- Trouver la source : recherche par image sur Alibaba (la plus efficace pour nos fournisseurs) ou Google Lens. Ne garder qu'une photo du **même modèle et de la même couleur** ; ne jamais effacer le logo ou le filigrane d'un autre.
- Beaucoup de nos lits viennent d'**Anhui Cool Baby (酷豆丁 = « KDD »)**, boutique `ahcoolbaby.en.alibaba.com`, modèles nommés « B271 », « B2261 », « B4401 », « F3501 »… Leurs photos portent le logo Cool Baby (accepté par Hanis le 23 oct. 2026).
- Photos des articles à refaire : 234 font moins de 600 px (148 moins de 400 px). Lot 1 (lits) fait le 23 oct. 2026 : 271, P271, P3501, 2261, 4401 ; puis, en autre coloris : KDD185, C316A, 608. Non trouvés : YSJ560, YSJ570, 2201, 4402, 2151, 265B, TM799, 9655B, 5704 (2201 et YSJ560/570 existent avec un décor différent, non retenus).
- Hanis accepte une photo du même modèle dans une autre couleur. Dans ce cas on fait des **versions par couleur** : champ `colors:[['Rose','images/x.webp'], ['Blanc','images/x-blanc.webp', 'note facultative']]` sur l'article (première couleur = vignette ; on garde l'ancienne photo comme version de la vraie couleur). Code dans `brand/couleurs.py` (liste `COLORS` en bas) ; la couleur choisie part dans le panier (clé `id~Couleur`) et le message WhatsApp.
- **Ne plus télécharger de photos sur le Mac de Hanis** (fenêtres « Enregistrer sous » à fermer à la main : il ne veut plus de tâches manuelles). Méthode depuis le 23 oct. 2026 : on note seulement les adresses des photos dans **`photos/sources.json`** (`{id: {urls:[jusqu'à 4], statut:'trouve'|'couleur'|'doute', note, fiche}}`). C'est **Netlify qui télécharge et prépare** les photos au moment du build (`admin/photos-fetch.js`, avec `sharp` : marges blanches rognées, carré 1000 px, filigrane) : `images/<id>.webp` (principale), `<id>-2/-3/-4.webp` (galerie de la fiche, `brand/galerie.py`), `images/galerie.json`. Cache entre builds : plugin `netlify/plugins/photos-cache`.
- **En ligne (production)**, `photos-fetch.js` ne prend que les photos « même article » (`trouve`) et « autre couleur » (`couleur`) ; les « à vérifier » (`doute`) restent sur l'aperçu tant que Hanis ne les a pas validées. En ligne, les photos déjà préparées sont **reprises de l'aperçu n° 2** (`PHOTOS_FROM`, par défaut `deploy-preview-2--petit-baobab.netlify.app`) : la mise en ligne du 23 oct. 2026 a pris 34 s (502 photos reprises). Chaque construction a une limite de temps (8 min sur l'aperçu, 14 min en ligne) : le reste est préparé à la construction suivante. Netlify ne construit qu'un site à la fois : éviter les aperçus en double.
- **Validation** : sur l'aperçu (PR, branche `photos-lits`), la page `/verification-photos/` montre avant/après pour chaque article avec une case à décocher et un bouton « Copier les numéros refusés ». Rien ne part en production sans le « publie » de Hanis.
- Recherche par image Alibaba sans téléchargement : dans le navigateur, injecter l'image (`raw.githubusercontent.com/Okethanis/Petit-Baobab/main/images/<id>.webp`, éventuellement recadrée) dans `input[name=image-search-upload]` ; l'adresse HD d'une vignette = adresse sans le suffixe `_NNNxNNN.jpg`. La recherche par texte déclenche un CAPTCHA (ne jamais le résoudre) ; la recherche par image passe avec le compte de Hanis connecté.
- Suivi : tableau de bord « Photos du catalogue » (artefact claude.ai, jeu de données `progression`).
- **Aucun texte chinois sur les photos** (demande de Hanis, 23 oct. 2026). Sur l'aperçu, `admin/photos-ocr.py` (RapidOCR, lancé par `netlify.toml` hors production) lit chaque nouvelle photo HD et écrit `/verification-photos/ocr.json` + une étiquette rouge « Texte chinois » sur la page de vérification ; on retire alors l'adresse fautive de `photos/sources.json`. Photos du dépôt sans version HD : recadrées ou retouchées à la main (étiquette effacée), jamais un logo de marque.
- Doublons (même article sous plusieurs codes ou prix) : **effacés le 23 oct. 2026** sur demande de Hanis (`brand/doublons.py`) : 55 fiches en `hidden:true` (rien de supprimé), prix = le plus haut du groupe, packs repointés ; 11 modèles « autre couleur » regroupés en une fiche avec choix de couleur (`brand/couleurs.py`). 08113 reste à part (prix différent). Anciens codes → fiche gardée dans `brand/alias.json` → `ID_ALIAS` (partagé avec `brand/ids-propres.py`). Ordre : `ids-propres.py` → `doublons.py` → `couleurs.py` → `node admin/packs.js` → `node build.js`. Suivi des groupes : artefact claude.ai « Doublons du catalogue ».

## Aménageur de chambre 3D (page /amenageur/)

- Le client entre les mesures de la chambre, place des meubles de la boutique sur un plan et en 3D (alertes porte, chevauchement, fenêtre, hauteur), puis commande toute la chambre sur WhatsApp (code de plan qui rouvre le même plan).
- Deux pièces (24 oct. 2026, demande de Hanis) : onglets « Chambre de bébé » et « Chambre des parents » (si bébé dort chez les parents). Dans la chambre des parents, le lit des parents (140, 160 ou 180 cm, « Déjà chez vous », jamais compté dans le total) est posé d'office ; on y ajoute berceau, lit cododo, table à langer… Chaque pièce garde son plan (`localStorage` `pb-amenageur-v1` et `pb-amenageur-v1-parents`) ; le message WhatsApp liste les pièces utilisées.
- Les mesures de la pièce sont repliées : une ligne de résumé (« 4 × 3,5 m · porte : mur du bas… ») et le bouton « Personnaliser les dimensions » qui ouvre le formulaire (demande de Hanis : la zone prenait trop de place sur l'écran).
- Codes de plan : « PB1-… » = chambre de bébé seule (anciens codes, toujours acceptés) ; « PB2-… » = les deux pièces. Le lit des parents est codé 900 + taille (hors catalogue).
- Sources : `amenageur/page.html` (l'outil, repères `/*CATALOG*/`, `/*WA*/`, `/*WA_DISPLAY*/`) et `amenageur/meubles.json` (14 meubles : code du site, couleur montrée, dimensions en cm, `approx` = dimensions non vérifiées, modèle 3D). **L'ordre de `meubles.json` ne doit jamais changer** (les codes PB1/PB2 enregistrent la position) : ajouter à la fin.
- `build.js` écrit `site/amenageur/index.html` : nom, référence, prix et photo viennent de `PRODUCTS` (toujours ceux du site), numéro WhatsApp de `CONFIG`. Un article absent ou masqué fait échouer le build (message clair).
- `static/amenageur/` : `three.min.js` (r128, hébergé chez nous : la politique de sécurité du site bloque les CDN), film du bloc « Voir comment ça marche » (`demo-amenageur.mp4`/`.webm`, `preload="none"`) et son affiche.
- Liens : onglet « Chambre 3D » dans le menu (ordinateur et téléphone), encart sur l'accueil, pastille « Chambre en 3D » du haut d'accueil et lien sur les fiches lits, berceaux, lits parapluie, parcs, tables à langer et mobilier (`brand/amenageur-liens.py`), sans deuxième bouton orange.
- Sur le Mac de Hanis (`~/Documents/Petit-Baobab`), `build.js` copie `static/` fichier par fichier (`copyTree`) : `fs.cpSync` échoue (EACCES) sur ce dossier.
- Film de présentation (50 s, 1080 × 1920) : sources dans l'artefact claude.ai de l'aménageur (`sources/film/`), refait le 23 oct. 2026 avec les photos HD ; copie sur le Mac de Hanis : `~/Documents/Film-amenageur-Petit-Baobab/`.

## Mises en ligne

- 23 oct. 2026, 22 h 27 : photos HD sûres, doublons effacés, codes renommés, aménageur 3D, haut d'accueil « pour qui + services », numéro 01 52 35 81 22 (main@d1839a0).

## À faire (au 23 oct. 2026)

- Remplacer les **tarifs de livraison** par commune (dans `CONFIG.zones`) par les vrais tarifs.
- Remplacer l'**adresse e-mail** fictive (`CONFIG.email`) par la vraie.
- Fiches dont la photo ne correspond pas au nom (à corriger avec Hanis) : 6005 (photo = support de baignoire), 7686 (photo = armoire à fleurs), hk305 (photo = couffin), x300 (photo = trotteur), d900 (photo = poussette), 9172 (photo = boîtes doseuses ALGO), 2314 (photo = étagère poussin), 7276-1 (photo = coffret biberons EVANI), zy-360 (photo = brosse à biberon), x-10 (photo = bassin de toilette), MS-4, HT681, x-n-2, 7276-2 « Lingettes » (photo = coffret biberons Dr Gym). L'ancienne photo de 103 (ex-103-100-60-40) affichait un prix en yuans : remplacée par la photo HD (aperçu).
- Références en chinois : **supprimées le 23 oct. 2026** à la demande de Hanis (`brand/refs-propres.py` : 29 retirées, « 香槟-BW365 » devenue « BW365 »). Un article sans `ref` n'affiche simplement pas de ligne « Réf. ». Ne jamais remettre de chinois ni de quantités de packing list dans `PRODUCTS` (contrôle : chercher `[　-鿿＀-￯]`). Codes d'articles (`id`) contenant des quantités de packing list : **renommés le 23 oct. 2026** (`brand/ids-propres.py` : 28 codes, ex. « bjj-601-grey-20-khaki-20 » → « bjj-601 », photos et `photos/sources.json` renommés). Les fiches n'ont pas d'adresse propre ; les anciens codes restent reconnus via `ID_ALIAS` (paniers, listes de naissance `?l=`, favoris déjà enregistrés sont convertis au chargement). Ne jamais créer de nouvel `id` avec des quantités.
- Nom de domaine souhaité : `petit-baobab.com`.
