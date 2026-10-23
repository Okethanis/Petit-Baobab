"""23 oct. 2026 — l'acompte est retiré : paiement à la livraison, ou par Wave / Mobile Money avant la livraison.
   Textes (accueil, livraison, FAQ, conditions de vente, réassurance), choix de paiement et message WhatsApp. Idempotent."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def rep(old, new):
    global s
    if old not in s: return            # déjà fait
    assert s.count(old) == 1, old[:80]; s = s.replace(old, new)

rep('<p>À la livraison, par Wave ou Mobile Money, ou avec un acompte de 50 %.</p>', '<p>À la livraison, en espèces, par Wave ou Mobile Money.</p>')
rep('À la livraison, par Wave ou Mobile Money, ou avec un acompte de 50 % et le solde à la réception.</li>', 'À la livraison, en espèces, par Wave ou Mobile Money, ou à distance avant la livraison.</li>')
rep(', du montant exact de votre commande. Vous pouvez aussi verser un acompte de 50 % pour réserver votre commande et régler le solde à la livraison.</p>', ', du montant exact de votre commande.</p>')
rep(' Passé ce délai, la commande est en préparation ; un acompte déjà versé reste acquis si l\'annulation vient de vous.</p>', ' Passé ce délai, la commande est en préparation.</p>')
rep('    <details><summary>Comment fonctionne l\'acompte de 50 % ?<svg class="icon"><use href="#i-chev"/></svg></summary><p>Vous payez la moitié du total par Wave ou Mobile Money au moment de la commande, ce qui la réserve, puis le solde au livreur à la remise du colis. C\'est pratique pour les gros articles comme un lit ou une poussette.</p></details>\n', '')
rep('            <label class="choice"><input type="radio" name="pay" id="pay-deposit" value="acompte"><span><strong>Acompte de <span id="dep-pct">50</span> % par Wave ou Mobile Money, solde à la livraison</strong><small id="dep-note">Votre commande est réservée dès l\'acompte reçu. Conseillé pour les gros articles.</small></span></label>\n', '')
rep('<p>À la livraison (espèces, Wave ou Mobile Money), avant la livraison par Wave ou Mobile Money, ou par un acompte de 50 % à la commande et le solde à la livraison. Les commandes hors d\'Abidjan et les cadeaux sont payés avant le départ du colis. En cas d\'annulation de votre part après versement d\'un acompte, celui-ci peut être conservé pour couvrir les frais engagés.</p>',
    '<p>À la livraison (espèces, Wave ou Mobile Money), ou avant la livraison par Wave ou Mobile Money. Les commandes hors d\'Abidjan et les cadeaux sont payés avant le départ du colis.</p>')
rep('<span>Espèces, Wave ou Mobile Money à la livraison, paiement à distance, ou acompte et solde à la réception.</span>', '<span>Espèces, Wave ou Mobile Money à la livraison, ou paiement à distance avant la livraison.</span>')
rep("paiement à la livraison, par Wave ou Mobile Money, ou acompte de 50 %, échanges sous 48 h.'", "paiement à la livraison, par Wave ou Mobile Money, échanges sous 48 h.'")
rep("espèces acompte retour échange questions'", "espèces retour échange questions'")
rep("'<li>' + icon('check') + '<span>Espèces, Wave ou Mobile Money à la livraison, ou acompte et solde à la réception</span></li></ul>'", "'<li>' + icon('check') + '<span>Espèces, Wave ou Mobile Money à la livraison</span></li></ul>'")
# message WhatsApp et récapitulatif : plus d'option acompte
rep(" : $('#pay-deposit').checked ? 'Acompte de ' + dep.pct + ' % par Wave ou Mobile Money (' + fmt(half) + (fee.known ? '' : ' + ' + dep.pct + ' % de la livraison') + '), solde à la livraison'", '')
i = s.find("  var dep = depositFor(sub+fee.fee);\n")
if i >= 0:
    j = s.index('\n', s.index("  $('#dep-note').textContent", i)) + 1
    s = s[:i] + s[j:]
rep("  deposit: { rate: 0.5, bigRate: 0.3, bigFrom: 150000 },   // acompte 50 % en général, 30 % à partir de 150 000 FCFA (lits, packs)\n", "  deposit: null,   // acompte retiré le 23 oct. 2026 (paiement à la livraison ou avant la livraison)\n")
open(P, 'w', encoding='utf-8').write(s)
print('acompte retiré')
