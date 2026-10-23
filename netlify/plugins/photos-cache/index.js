// Garde les photos déjà préparées (.photos-cache/) d'une construction Netlify à l'autre :
// plus rapide, et une photo retirée chez le fournisseur reste disponible.
module.exports = {
  async onPreBuild({ utils }) { await utils.cache.restore('.photos-cache'); },
  async onPostBuild({ utils }) { await utils.cache.save('.photos-cache'); },
};
