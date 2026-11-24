# Journal de session — ezCore / MeshTag (nov. 2026)

Récapitulatif chronologique du travail mené sur le projet MeshCore compagnon
(porte-clés « MeshTag », disque Ø48). Hardware KiCad, boîtier Onshape, sourcing.

---

## 1. Électronique / PCB (KiCad)

### Re-brochage du MCU (XIAO nRF52840)
Brochage retenu, pads XIAO 1→7 en face des broches Wio 6,5,4,3,2,1,11 :

| Pad MCU | Broche XIAO | Signal | Broche Wio |
|---|---|---|---|
| 1 | D0 | NSS | 6 |
| 2 | D1 | NRST | 5 |
| 3 | D2 | SCK | 4 |
| 4 | D3 | MOSI | 3 |
| 5 | D4 | MISO | 2 |
| 6 | D5 | RXEN | 1 |
| 7 | D6 | BUSY | 11 |
| 8 | D7 | **Bouton** (BTN) | — |
| 9 | D8 | LED verte | — |
| 10 | D9 | LED rouge | — |
| 11 | D10 | DIO1 | 12 |

- Inversion tardive : **bouton sur pad 8 (D7)**, **LED rouge sur pad 10 (D9)**.
- **Toutes les broches D0–D10 sont des GPIO libres** côté nRF52840 : le SPI, les
  IRQ et les GPIO se placent sur n'importe quelle broche. Un brochage non standard
  impose un **env PlatformIO + variant.h perso** (MeshCore `xiao_nrf52`), plus le
  firmware officiel tel quel.
- Un seul signal rapide : SCK. D0–D5 = AIN0..3/… (seules broches analogiques),
  D6–D10 = « low frequency I/O only ». Aucun signal du projet n'a besoin
  d'analogique précis ; le SAADC est unique et multiplexé (aucune entrée « plus
  précise »).

### Coupure batterie côté masse
`SW3` ouvre désormais **BAT−** (net `BAT_N`) vers `GND` ; `BAT+` reste sur `VBATT`.
Tout le courant passe par l'interrupteur côté masse ; piste `BAT_N` à élargir.

### NFC
NFC1/NFC2 = deux bouts d'une même bobine (pilotage différentiel). **Connecter les
deux**, pistes courtes et de même longueur, pas de plan de masse entre/dessous. Ne
pas activer `CONFIG_NFCT_PINS_AS_GPIOS` (sinon NFC HS).

### Plan de masse / antennes
- Un plan de masse est **nécessaire** (retour SPI, pics LoRa ~125 mA, référence RF).
- Keep-outs obligatoires : **sous l'antenne BLE** du XIAO et **sous la bobine NFC**.
  L'antenne LoRa (FPC/IPEX) est hors PCB, sur la paroi du boîtier.
- Coutures de masse (vias) tous les 5–8 mm, supprimer les îlots.
- Clearance netclass `Default` à passer de 0,2 → **0,3 mm** (gravure maison).

### Pastilles sous le XIAO
Batterie (19/20) et NFC (21/22) sont **sous** le module, inaccessibles au fer.
Options : plaque chauffante/air chaud par-dessous, **trous sous les pastilles**
(soudure par l'arrière), ou fils pré-soudés. SWD (15–17) non indispensables (flash
UF2 par USB).

---

## 2. Montage JLCPCB (PCBA)

### Sourcing (vérifié sur l'API pièces JLC)
JLC pose **12 composants** ; **U1 (XIAO) et U2 (Wio) exclus** (soudés main, pas DNP
pour garder le 3D).

| Réf | Composant | LCSC | MPN | Type |
|---|---|---|---|---|
| C1 | 10 µF 6,3 V X5R 0402 | C15525 | Samsung CL05A106MQ5NUNC | base |
| C2, C5 | 100 nF 16 V X7R 0402 | C1525 | Samsung CL05B104KO5NNNC | base |
| C3, C4 | 47 pF C0G 0402 (accord NFC, à confirmer au VNA) | C1567 | FH 0402CG470J500NT | base |
| R1, R2 | 470 Ω 1 % 0402 | C25117 | UNI-ROYAL 0402WGF4700TCE | base |
| D1 | LED rouge 0402 | C25503345 | XINGLIGHT XL-1005SURC | étendu |
| D2 | LED verte 0402 | C965793 | XINGLIGHT XL-1005UGC | étendu |
| SW1 | Bouton KMR2 (patte de masse) | C72443 | C&K KMR221GLFS | étendu |
| SW3 | Interrupteur 0,3 A | C221841 | C&K PCM12SMTR | étendu |
| J5 | Réceptacle pogo magnétique 4P 2,5 mm | C5126846 | Xinyangze YZT0675-20048-04025-01 | étendu, **stock 0** |

- Empreintes + STEP sourcés (Seeed officiel pour XIAO, LCSC/EasyEDA pour le reste,
  recalés sur leur WRL). Champs **LCSC/MPN/Manufacturer** dans le schéma.
- Export : `tools/export_jlc.py` **et** plugin KiCad **Fabrication Toolkit 5.3.1**
  (installé dans `~/.local/share/kicad/10.0/3rdparty/plugins`).
- Fichiers JLC : le CPL = **`positions.csv`** (Pick & Place), BOM = `bom.csv`,
  gerbers = `MeshTag.zip`. Versions sans J5 : `*_sansJ5.csv`.

### Finition PCB : **HASL** (pas ENIG)
L'ENIG était inutile : le pogo J5 est un **connecteur soudé** (contacts laiton doré
sur le connecteur), aucun frottement sur le cuivre de la carte. HASL suffit.
Estimation ~**25–35 $** / 5 cartes assemblées.

### J5 en rupture
Le réceptacle C5126846 est **stock 0**. → le sortir du BOM/CPL JLC et le souder
soi-même, ou le faire précommander par JLC.

---

## 3. Boîtier (Onshape / FeatureScript)

- Document utilisateur `ce37c786…`, Feature Studio **« MeshTag Case »**.
- Génération **paramétrique** : 5 pièces (`MeshTag Front`, `MeshTag Back`, `Button`,
  `LED Lens`, `Charge Ring`, `Slide Switch`).
- **Direction design validée (revue) : façade avant NUE** (dôme blanc-os chaud
  `#F2F1ED`), **tout le fonctionnel au dos** (recharge magnétique, bouton,
  interrupteur), **LED diffusée** sous paroi 0,45 mm (pas de trou), oreille
  porte-clés fondue, joint près de l'équateur, accent métal `#D7D7DA`.
- Galet **Ø53,7 × ~10–12 mm**. **Jeu min coque↔composant 0,34 mm** (module Wio),
  calculé sur le nuage de points réel du STEP (`enclosure/design.py`).
- **USB-C du XIAO exclu** de la géométrie (`fab/MeshTag_PCB_noUSBC.step`).
- Source + scripts : `hardware/enclosure/` (MeshTag_Case.fs, design.py, proxies.py,
  pcbpts.py, README).
- Leçons FeatureScript : filtrer les bodies via `qBodyType(...SOLID)`, extrude
  z0<z1, union via `qUnion([...])` sans `targets`, `test_feature` n'évalue que le
  **premier export**.

---

## 4. Batterie

- **Changement** : ancienne LPR604543 (ronde Ø45 × 6, 1050 mAh) → **GREPOW 553535**
  (ronde **Ø35 × 5,4 mm, 580 mAh**, réf AliExpress 1005010480898493).
- Plus petite → rentre largement dans le disque Ø48 ; **cavité boîtier à recaler**
  (Ø35 au lieu de Ø45) + **BOM/README à mettre à jour** (à faire).
- **PCM à vérifier** : les versions « cell only » n'ont pas de protection. Le XIAO
  (BQ25101) protège la **charge** mais **pas** la décharge profonde ni le
  court-circuit → **prendre la version avec PCM**. Message vendeur rédigé.

---

## 5. Liste d'achat (hors JLC, hors MCU/antenne déjà possédés)

| # | Article | Specs |
|---|---|---|
| 1 | Batterie **GREPOW 553535** | Ø35 × 5,4, 580 mAh, **avec PCM**, fils nus |
| 2 | Réceptacle pogo **femelle** 4P 2,5 mm (= J5, si soudé main) | Xinyangze YZT0675-…-01 |
| 3 | Connecteur pogo **mâle** 4P 2,5 mm (base de charge) | Xinyangze YZT0675-…-04 / YZP0048, ou kit mâle+femelle AliExpress 1005006531774076 |
| 4 | Film **ferrite 0,1 mm** | entre bobine NFC et batterie (indispensable) |

- **Attention empreinte** : l'empreinte J5 de la carte est calée sur le **Xinyangze
  YZT0675**. Un kit AliExpress générique (JCD, etc.) n'a pas de plan → à **mesurer à
  réception** (entraxe 2,5 mm, Ø pattes) avant d'ajuster l'empreinte.

---

## 6. Tâches Vikunja (projet Perso, échéance 15/11, prio haute)
1. Message au fabricant batterie : PCM ? combien de fils ?
2. Vérifier le prix PCB/PCBA sur JLCPCB (upload gerbers+BOM+CPL, HASL).

---

## Reste à faire
- [ ] Recaler la cavité du boîtier pour batterie Ø35 × 5,4.
- [ ] Mettre à jour la fiche BT1 (BOM/README) : LPR604543 → GREPOW 553535.
- [ ] Router le PCB (SPI LoRa, NFC, VBATT/BAT_N, RST) + plan de masse + vias.
- [ ] Déplacer SW3 au bord (ou garder le coulisseau au dos) ; trou porte-clés géré
      par l'oreille du boîtier (batterie sous l'ancien trou).
- [ ] Confirmer J5 : précommande JLC ou soudure main ; valider l'empreinte vs
      connecteur réellement acheté.
