# ezCore — Recherche batterie, dimensionnement, autonomie (session 2026-11)

Dump de la conversation de travail sur le choix de batterie AliExpress, le
calcul d'épaisseur du boîtier et l'estimation d'autonomie MeshCore.

---

## 1. Besoin initial

Trouver une batterie sympa pour le projet (disque Ø48/50 mm type AirTag autour du
XIAO nRF52840 + Wio-SX1262). Achat unitaire → AliExpress (seul endroit pour du
particulier). Descriptions mauvaises : specs et dimensions à retrouver à la main.

Lien de départ fourni :
<https://fr.aliexpress.com/item/1005010480898493.html> (GREPOW 553535).

Contrainte : **ignorer tout ce qui est livré en janvier**.

Cible d'origine du README : **LPR604543 ronde Ø45 × 6 mm, 1050 mAh, PCM**
(le BOM mentionnait encore une EREMIT 502030 250 mAh).

---

## 2. Résultat de la navigation AliExpress

Les cellules **rondes** sont rares sur Ali (surtout des pièces de rechange de
montres, Ø≈35 mm, 450–600 mAh). **Aucune ronde Ø45 1050 mAh** disponible.
Beaucoup d'annonces livrées le 13 janvier → écartées.

Attention : l'« aperçu IA » du lien de départ annonçait 1300 mAh ; **l'étiquette
réelle sur la photo dit 580 mAh / 2,146 Wh**.

### Annonces livrées avant janvier (fin nov. → déc.)

| # | Pile | Dim. (L×l×ép, mm) | Capacité | Prix + port | Livraison | Lien |
|---|---|---|---|---|---|---|
| 1 | GREPOW 553535 ronde | Ø35 × 5,5 | 580 mAh | 11,69 + 9,42 = **21,11 €** | 30 nov – 8 déc | <https://fr.aliexpress.com/item/1005010480898493.html> |
| 2 | **603030 carrée, PH2.0** | 30 × 30 × 6 | 600 mAh | 5,19 + 4,88 = **10,07 €** | 30 nov – 8 déc | <https://fr.aliexpress.com/item/1005010795423538.html> |
| 3 | 803030 carrée | 30 × 30 × 8 | 700 mAh | 6,59 + 5,98 = **12,57 €** | 30 nov – 8 déc | <https://fr.aliexpress.com/item/1005007481321117.html> |
| 4 | Samsung EB-BR800ABU | n.c., rect. coin coupé | 600 mAh, 3,88 V | 12,89 + 3,99 = **16,88 €** | 30 nov – 8 déc | <https://fr.aliexpress.com/item/1005009645834601.html> |
| 5 | Huawei HB532729ECW | ≈27 × 29 × 5,3, rect. | 455 mAh, 3,82 V | 10,49 + 3,99 = **14,48 €** | 30 nov – 8 déc | <https://fr.aliexpress.com/item/1005011922589974.html> |

### Recommandations

- **Ronde → n°1** : seule ronde livrable avant janvier. 5,5 mm, ~580 mAh, nappe
  souple (souder des fils sur les pastilles). Port > prix de la pile.
- **Meilleur rapport q/p → n°2** : 30×30×6, fils + PH2.0 standard, 10 € livrée,
  vendeur 96 %. Gabarit de pile à passer en carré.
- **n°3** : +100 mAh mais 8 mm d'épaisseur.
- **Éviter n°4 et n°5** : cellules « haute tension » (charge 4,4 V) ; le BQ25101
  du XIAO s'arrête à 4,2 V → ~10 % de capacité perdue, dimensions/forme mal
  définies, PCM non vérifié.

### Écartées (livraison 13 janvier)

Rondes 443535/403535 (Finow), 483535 550 mAh (Zeblaze), Garmin Fenix 5,
802535 700 mAh, 603035 700 mAh.

---

## 3. Dimensionnement (calculé depuis le KiCad + modèles 3D)

### Carte

- **Contour réel : Ø50 mm** (le README dit Ø48).
- **Épaisseur PCB : 1,0 mm.**
- Impossible de rétrécir sans re-placer : Wio, LED et R déjà à ~24 mm du centre.

| Pièce (face avant) | Hauteur |
|---|---|
| USB-C XIAO | 3,3 mm |
| Wio-SX1262 | 2,96 mm |
| Pogo | 2,8 mm |
| Bouton | 1,9 mm |

Composants avant : **3,0 mm** si USB-C dessoudé, 3,3 mm sinon.

### Épaisseur totale

Empilage : composants (3,0) + PCB (1,0) + ferrite (0,15) + pile.
Boîtier : toit 0,8 + jeu 0,2 + gonflement 0,3 + fond 0,8.

| Pile | Ép. pile | Carte nue | Avec boîtier PLA | Capacité |
|---|---|---|---|---|
| GREPOW 553535 ronde | 5,5 | **9,6 mm** | **11,7 mm** | 580 mAh |
| 603030 carrée | 6,0 | 10,1 mm | **12,2 mm** | 600 mAh |
| 803030 carrée | 8,0 | 12,1 mm | 14,2 mm | 700 mAh |
| LPR604543 (prévue) | 6,0 | 10,1 mm | 12,2 mm | 1050 mAh |

(+0,3 mm partout si USB-C conservé.)

### Diamètre

- Carte nue : **Ø50 mm**.
- Avec boîtier : **~Ø53–54 mm** (50 + 2×0,3 jeu + 2×1,2 paroi) ; +~0,5 mm si
  antenne LoRa contre la paroi. Oreille porte-clés en plus. Ouverture paroi pour
  le pogo (zone jusqu'à 26 mm du centre).
- **Cible réaliste : palet ~Ø54 × 12 mm**, ~27 cm³, ~7 g PLA + 10–12 g pile.

### Obstacles sous la carte

- **Pogo** : descend 2 mm sous la carte, à 20,0–20,4 mm du centre (diag. haut-droite).
- **Trou porte-clés** : traverse à 19–24 mm du centre (diag. haut-gauche).
- Ronde Ø35 : va à 17,5 mm → ne touche rien.
- Carrée 30×30 : **à poser en losange (45°)**, sinon les coins (21,2 mm) tombent
  sur le pogo et le trou.
- **⚠️ LPR604543 Ø45 ne passe pas** : va à 22,5 mm → bouche le trou et bute sur le
  pogo. Nécessiterait +2 mm d'épaisseur ou déplacer pogo + trou.

---

## 4. Autonomie

Companion MeshCore = écoute radio permanente → la **RX LoRa domine**.
Mesures publiées (XIAO nRF52 / RAK4631, au câble batterie, PR #2286) :
**9,3 mA** sans économie, **6,5 mA** avec (BLE connecté).

TX : 20 msg/j × ~80 o × 0,8 s @125 mA ≈ **0,7 mAh/j** (négligeable vs ~156 mAh/j RX).

Hypothèses : ~90 % capacité utile (coupure ~3,0 V), LED éteintes, TX inclus.

| Pile | Mode économie (6,6 mA) | Sans (9,4 mA) |
|---|---|---|
| 553535, 580 mAh | **≈ 3,3 j** | 2,3 j |
| 603030, 600 mAh | **≈ 3,4 j** | 2,4 j |
| 803030, 700 mAh | ≈ 4,0 j | 2,8 j |
| LPR604543, 1050 mAh | ≈ 6,0 j | 4,2 j |

Baisse de 10–20 % par froid / après ~100 cycles ; LED allumée = +3–5 mA/LED
(R = 470 Ω). Recharge XIAO ≤ 100 mA → 6–7 h pour 600 mAh.

Non mesuré : conso propre de la carte (bobine NFC, pont diviseur) → à vérifier au PPK2.
Dim. 553535 déduites de la réf + photo, pas d'une datasheet.

---

## 5. Économie d'énergie : couper/alléger l'écoute

### Ce que les nœuds gardent en mémoire

| Nœud | Mémoire | Source |
|---|---|---|
| Relais (`simple_repeater`) | file d'envoi immédiate seulement, rien pour un absent | `curr_tx_queue_len` |
| Room server | **oui** : 32 msg non lus, renvoyés jusqu'à ACK | `MAX_UNSYNCED_POSTS 32`, `pushPostToClient` |
| Companion (le tien) | file de 16 msg module↔téléphone (BLE, pas radio) | `OFFLINE_QUEUE_SIZE 16` |
| Message privé | expéditeur réessaie qq s puis abandonne | `calcDirectTimeoutMillisFor` |
| Message de canal | diffusé une fois, sans ACK ni retry | — |

→ Couper l'écoute par périodes **perd** les messages privés et de canal reçus
pendant la coupure ; seul un room server rejoue plus tard.

### Meilleure approche : écoute du préambule (duty-cycle RX)

Préambule EU = **32 symboles** (`preambleLengthForSF` ≤ SF8). Le SX1262 sait dormir
et se réveiller brièvement pour détecter le début de trame : RadioLib fournit
`startReceiveDutyCycleAuto()`, **mais MeshCore ne l'utilise pas** (`startReceive()`
continu).

Calcul RadioLib (SF8 / 62,5 kHz) :
- symbole = 2⁸/62500 = **4,1 ms**
- sommeil = (32 − 2×8) = **65,5 ms**
- réveil = max(35,3 ; 9×4,1) = **36,9 ms**
- → radio active **~36 %** du temps, sans rater de trame (en théorie).

### Autonomie estimée (pile 603030, 540 mAh utiles)

| Mode | Courant moyen | Autonomie | Pertes |
|---|---|---|---|
| Écoute continue (actuel) | 6,5 mA | ≈ 3,4 j | aucune |
| **Duty-cycle préambule** | ≈ 3,6 mA | **≈ 6 j** (5,5–7) | théoriquement aucune |
| Écoute 1 min / 10 min | ≈ 2,4 mA | ≈ 9 j | presque tout hors room server |
| Les deux | ≈ 2,1 mA | ≈ 10 j | idem |

Une fois la RX économe, c'est le **reste de la carte (~1,9 mA)** qui domine
(BLE 15–30 ms, régulateur XIAO, pont diviseur batterie).

### Modifs firmware (variante ezCore)

1. `CustomSX1262` : `startReceive(INF)` → `startReceiveDutyCycleAuto(32, 8)` si
   mode économie.
2. Désactiver ce qui suppose l'écoute continue : mesure du bruit de fond
   (`getCurrentRSSI()` dans `RadioLibWrapper::loop`), CAD avant TX.
3. Vérifier la gestion `_preambleMillis` avec ce mode.

Risques : suppose que les autres nœuds émettent bien 32 symboles (16 → raté,
RadioLib repasse en continu) ; pertes réelles à mesurer sur le terrain ; courants
calculés, pas mesurés (→ PPK2). Aucune modif côté carte nécessaire.

---

## 6. Liens batterie (rappel)

- **603030 carrée** 30×30×6, 600 mAh, PH2.0, ~10 € livrée :
  <https://fr.aliexpress.com/item/1005010795423538.html>
- **GREPOW 553535 ronde** Ø35×5,5, 580 mAh, ~21 € livrée :
  <https://fr.aliexpress.com/item/1005010480898493.html>

Livraison annoncée : 30 nov – 8 déc.

---

## 7. À mettre à jour si on abandonne la LPR604543

- README : capacité (1050 → ~600 mAh) et Ø45 → pile 30×30 ou Ø35.
- Gabarit de pile sous le PCB (carré en losange, ou rond Ø35).
