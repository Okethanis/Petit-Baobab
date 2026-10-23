# Petit Baobab — site de puériculture en ligne (Abidjan)

Boutique en ligne qui présente ~597 articles et conclut les ventes sur **WhatsApp** (pas de paiement en ligne, pas de serveur, pas de base de données). Site statique, en français.

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
- `netlify.toml` ne reconstruit QUE si `petit-baobab.html`, `build.js`, `images`, `static` ou `vendor` changent. Un commit qui ne touche que `admin/`, `brand/`, `CLAUDE.md` ne coûte rien.
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
- **Validation** : sur l'aperçu (PR, branche `photos-lits`), la page `/verification-photos/` montre avant/après pour chaque article avec une case à décocher et un bouton « Copier les numéros refusés ». Rien ne part en production sans le « publie » de Hanis.
- Recherche par image Alibaba sans téléchargement : dans le navigateur, injecter l'image (`raw.githubusercontent.com/Okethanis/Petit-Baobab/main/images/<id>.webp`, éventuellement recadrée) dans `input[name=image-search-upload]` ; l'adresse HD d'une vignette = adresse sans le suffixe `_NNNxNNN.jpg`. La recherche par texte déclenche un CAPTCHA (ne jamais le résoudre) ; la recherche par image passe avec le compte de Hanis connecté.
- Suivi : tableau de bord « Photos du catalogue » (artefact claude.ai, jeu de données `progression`).

## À faire (au 23 oct. 2026)

- Remplacer les **tarifs de livraison** par commune (dans `CONFIG.zones`) par les vrais tarifs.
- Remplacer l'**adresse e-mail** fictive (`CONFIG.email`) par la vraie.
- Fiches dont la photo ne correspond pas au nom (à corriger avec Hanis) : 6005 (photo = support de baignoire), 7686 (photo = armoire à fleurs), hk305 (photo = couffin), x300 (photo = trotteur), d900 (photo = poussette), 9172 (photo = boîtes doseuses ALGO), 2314 (photo = étagère poussin), 7276-1 (photo = coffret biberons EVANI), zy-360 (photo = brosse à biberon), x-10 (photo = bassin de toilette), MS-4, HT681, x-n-2 (réf. « 袜子 »). **103-100-60-40 : l'ancienne photo affiche un prix en yuans** (à remplacer en priorité).
- **30 articles affichent une référence en chinois** (champ `ref`), parfois avec des quantités par coloris issues des packing lists (ex. « 米30 灰50 兰20 ») ; certains `id` en contiennent aussi (1688-30-50-20, 9-80-20-50, hh727-…, 5100-…). À remplacer par des références propres (proposé à Hanis le 23 oct. 2026). Contrôle : chercher `[　-鿿]` dans `PRODUCTS`.
- Nom de domaine souhaité : `petit-baobab.com`.
