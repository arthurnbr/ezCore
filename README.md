# ezCore — porte-clés compagnon MeshCore (V3, circulaire, UX)

Compagnon MeshCore ultra-compact en **disque Ø48 mm** (type AirTag) autour du
**Seeed XIAO nRF52840** + module LoRa **Wio-SX1262** (EU868) : appairage BLE sans
code, mise à jour OTA par application, **antenne NFC ronde intégrée**, **LED
bi-couleur** de retour utilisateur, **port de charge/flash magnétique 4 points**
(pogo), et batterie **1050 mAh** au dos du boîtier.

> État : schéma ERC 0/0, PCB placée UX + routée (Freerouting). Quelques points DRC
> à finir dans KiCad. Tout est reproductible via `hardware/tools/`.

## Disposition UX (V3)

Placement pensé usage, carte propre et symétrique :

- **Pogo magnétique `J5` en haut** (VBUS/GND/D+/D−, type chargeur de montre) :
  charge + flash UF2 + série USB.
- **Bouton `SW1` + LED bi-couleur `D1`/`D2` à gauche** (90° du pogo) : retour
  visuel type AirPods (rouge = charge, vert = prêt, orange = transition). Pilotée
  par D9 (rouge) / D8 (vert) du XIAO via `R1`/`R2` (série).
- **Ports de debug SWD `TP1-TP4` sous le bouton** (RST / SWDIO / SWCLK / GND).
- **Interrupteur ON/OFF `SW3` à droite** (coupe la batterie).
- **XIAO `U1` + bobine NFC + Wio `U2` au centre**, pour un routage court.
- **Languette porte-clés en bas** (opposée au pogo) : contour avec repère de
  perçage en sérigraphie — tu perces toi-même, pas de trou dans le cuivre.
- **Repères de calage recto-verso** : traits de sérigraphie N/E/O en bord (plus de
  trous FID).

## Nouveautés V2 (vs V1 rectangulaire 26 × 52)

- **Forme circulaire Ø48 mm** + oreille porte-clés dédiée (trou NPTH, plus à
  travers la carte).
- **Module Wio-SX1262** placé en bord de disque, IPEX vers le pourtour :
  l'**antenne LoRa FPC s'enroule sur la paroi intérieure** du boîtier (~270°),
  à l'opposé de l'oreille et de l'antenne BLE du XIAO.
- **Port pogo 4 points** (`J5` = VBUS / GND / D+ / D−) : charge **et** flash UF2
  **et** série USB par le même connecteur magnétique, sans ouvrir le boîtier.
- **USB-C du XIAO non exposé** ; peut être **dessoudé** pour gagner de la place
  (le pogo fournit VBUS + D+/D− → le bootloader UF2 et l'OTA marchent quand même).
- **Batterie LPR604543** ronde Ø45 × 6 mm, 1050 mAh, PCM (keep-out circulaire sous
  la PCB).
- **Bobine NFC ronde** (Ø28, net-tie) centrée sous le XIAO.
- **Pas de pull-up SPI** : confirmé par le schéma Seeed de la carte d'extension
  (ses 3 résistances servent au connecteur 30-pin, à la LED et au bouton — pas au
  bus SPI du SX1262). Seul un **100 nF** (`C5`) de découplage est ajouté au VCC
  du module.

## Arborescence

```
meshtag/
├── README.md
├── docs/                     notes de conception
└── hardware/
    ├── MeshTag.kicad_pro      projet KiCad 9
    ├── MeshTag.kicad_sch      schéma (généré)
    ├── MeshTag.kicad_pcb      PCB 2 couches, disque Ø48 mm (généré + routé)
    ├── MeshTag.net            netlist exportée
    ├── MeshTag.kicad_dru      règles DRC (exemption net-tie bobine NFC)
    ├── sym-lib-table          → lib/MeshTag.kicad_sym (locale)
    ├── fp-lib-table           → lib/MeshTag.pretty (locale)
    ├── lib/
    │   ├── MeshTag.kicad_sym  TOUS les symboles (projet autonome)
    │   ├── MeshTag.pretty/    TOUTES les empreintes (projet autonome)
    │   └── 3dmodels/          modèles 3D STEP (constructeur / LCSC, alignés)
    ├── tools/
    │   ├── gen_sch.py         génère le schéma lisible (blocs + stubs + notes + champs BOM)
    │   ├── build_pcb.py       place les empreintes, dessine le contour, zones
    │   ├── route_pcb.sh       DSN → Freerouting → import SES → zones → DRC
    │   └── export_jlc.py      fichiers JLCPCB PCBA (gerbers zip, BOM, CPL)
    └── fab/
        ├── jlc/               MeshTag_gerbers.zip + MeshTag_BOM_JLC.csv + MeshTag_CPL_JLC.csv
        ├── gerbers/           Gerbers + perçage (Protel + gbrjob)
        ├── schematic.png      rendu du schéma
        ├── render_3d_top.png  rendu 3D
        └── BOM.csv            BOM complète (valeurs, LCSC, MPN, fabricant)
```

Toutes les bibliothèques (symboles, empreintes, **modèles 3D**) sont **copiées
dans le projet** (`${KIPRJMOD}/lib/3dmodels`) : rien ne dépend des bibliothèques
système. Provenance des modèles 3D :

| Empreinte | Modèle 3D | Source |
|---|---|---|
| `XIAO-nRF52840-SMD` | `XIAO-nRF52840-SMD.step` | STEP officiel Seeed (« XIAO-nRF52840 v3 », Printables Seeed Studio), recalé sur les pads 19–22 (écart < 0,01 mm) ; empreinte identique à la lib KiCad officielle Seeed `OPL_Kicad_Library` |
| `Wio-SX1262-Module` | `Wio-SX1262-Module.step` | LCSC/EasyEDA C55348741, recalé sur le WRL EasyEDA (écart 0,03 mm) ; pads identiques à EasyEDA à ±0,02 mm |
| `MagPogo_4P_P2.50mm_YZT0675` | `MagPogo_4P_P2.50mm_YZT0675.step` | LCSC/EasyEDA C5126846, recalé ; empreinte = EasyEDA + plan constructeur |
| `SW_Push_1P1T-SH_NO_CK_KMR2xxG` | idem `.step` | lib KiCad officielle (KMR2 avec patte de masse, cf. fiche C&K) |
| `SW_SPDT_PCM12` | idem `.step` | lib KiCad officielle (C&K PCM12) |
| `C_0402_1005Metric`, `R_0402` | idem `.step` | lib KiCad officielle |
| `LED_0402_Red_XL-1005SURC` / `LED_0402_Green_XL-1005UGC` | idem `.step` | LCSC/EasyEDA C25503345 / C965793, recalés |

Les empreintes sans 3D (bobine NFC, pastilles batterie, fiducials, test points)
sont du cuivre/pads, sans pièce physique.

Pour régénérer le schéma : `python3 tools/gen_sch.py` (ERC 0/0).

## Fabrication JLCPCB (PCBA)

```bash
cd hardware && python3 tools/export_jlc.py   # → fab/jlc/
```

JLC pose les **12 composants CMS/THT** du tableau ci-dessous ; **U1 (XIAO) et U2
(Wio-SX1262) sont DNP** (marqués « Do Not Populate », hors BOM/CPL) et soudés à la
main. Les champs `LCSC` / `MPN` / `Manufacturer` sont dans le schéma.

| Réf | Valeur | LCSC | MPN | Type JLC |
|---|---|---|---|---|
| C1 | 10 µF 6,3 V X5R 0402 | C15525 | Samsung CL05A106MQ5NUNC | base |
| C2, C5 | 100 nF 16 V X7R 0402 | C1525 | Samsung CL05B104KO5NNNC | base |
| C3, C4 | 47 pF 50 V C0G 0402 (accord NFC, à confirmer au VNA) | C1567 | FH 0402CG470J500NT | base |
| R1, R2 | 470 Ω 1 % 0402 | C25117 | UNI-ROYAL 0402WGF4700TCE | base |
| D1 | LED rouge 0402 | C25503345 | XINGLIGHT XL-1005SURC | étendu |
| D2 | LED verte 0402 | C965793 | XINGLIGHT XL-1005UGC | étendu |
| SW1 | bouton KMR2 2 N | C72443 | C&K KMR221GLFS | étendu |
| SW3 | interrupteur coulissant 0,3 A | C221841 | C&K PCM12SMTR | étendu |
| J5 | réceptacle pogo magnétique 4P pas 2,5 mm | C5126846 | Xinyangze YZT0675-20048-04025-01 | étendu |

## Régénérer le PCB

```bash
cd hardware
export KIPRJMOD="$PWD"
kicad-cli sch export netlist --format kicadsexpr -o MeshTag.net MeshTag.kicad_sch
python3 tools/build_pcb.py        # place + contour + zoneinfo
bash   tools/route_pcb.sh         # autoroute + zones + DRC
```

Dépendances : KiCad 9 (`kicad-cli`, module `pcbnew`), Freerouting 2.5
(`FREEROUTING_JAR`, défaut `/tmp/tools/freerouting.jar`) exécuté avec un JRE ≥ 23
(`JAVA25`, défaut `/usr/lib/jvm/java-25-openjdk-amd64/bin/java`).

## Architecture électrique

Brochage choisi pour le routage (XIAO pads 1→7 en face des broches Wio
6,5,4,3,2,1,11). **Diffère de la variante MeshCore `xiao_nrf52`** : il faut un env
PlatformIO dédié (flags `P_LORA_*`, `SX126X_RXEN`, `PIN_USER_BTN`, `P_LORA_TX_LED`,
I2C désactivé) et une copie de `variant.h` (`PIN_SPI_*` y sont codés en dur).

| Signal          | Broche Wio | Pad XIAO | Broche XIAO | GPIO nRF | Net       |
|-----------------|------------|----------|-------------|----------|-----------|
| NSS             | 6          | 1        | D0          | P0.02    | LORA_NSS  |
| NRST            | 5          | 2        | D1          | P0.03    | LORA_RST  |
| SCK             | 4          | 3        | D2          | P0.28    | SPI_SCK   |
| MOSI            | 3          | 4        | D3          | P0.29    | SPI_MOSI  |
| MISO            | 2          | 5        | D4          | P0.04    | SPI_MISO  |
| RF_SW / RXEN    | 1          | 6        | D5          | P0.05    | LORA_RXEN |
| BUSY            | 11         | 7        | D6          | P1.11    | LORA_BUSY |
| DIO1            | 12         | 11       | D10         | P1.15    | LORA_DIO1 |
| Bouton `SW1`    | —          | 8        | D7          | P1.12    | BTN       |
| LED verte       | —          | 9        | D8          | P1.13    | via R2    |
| LED rouge       | —          | 10       | D9          | P1.14    | via R1    |

- **U1** XIAO nRF52840 (CMS à plat, castellations), face avant.
- **U2** module Wio-SX1262 nu (IPEX), face avant, au-dessus du XIAO.
- **AE1** bobine NFC 2 couches (net-tie NFC1/NFC2) pour l'appairage par approche.
- **C1/C2** découplage 3V3, **C3/C4** accord NFC, **C5** découplage Wio — tous en
  **0402** (petits). **D1/D2** LED bi-couleur 0402 + **R1/R2** résistances 0402.
  Tous les symboles ont leur **footprint assigné** (mise à jour schéma → PCB OK).
- **SW1** bouton utilisateur ; **SW3** interrupteur de coupure batterie **côté
  masse** : BAT+ reste sur `VBATT`, SW3 relie/coupe BAT− (`BAT_N`) de `GND`.
- **BT1** pastilles fils LiPo 1S ; **TP1-4** RST_MCU / SWDIO / SWCLK / GND.
- Plan de masse coulé sur les deux faces (zone médiane).
- **Keep-out antenne BLE** : pas de cuivre sous l'antenne 2,4 GHz intégrée du XIAO.
- **Keep-out bobine NFC** : pas de plan de masse dans la bande basse.

L'**antenne LoRa** n'est pas sur la PCB : elle se branche sur l'IPEX du module
Wio (FPC 868 MHz, voir `docs/`).

## Accord de la bobine NFC

Bobine **ronde** 6 tours/couche (Ø15 mm), ~1,5–2 µH estimés, centrée sous le XIAO.
**La valeur exacte doit être mesurée au NanoVNA** puis les condensateurs C3/C4
choisis entre 33 et 150 pF (C0G 0402) pour résonner à 13,56 MHz — procédure
standard (wiki Seeed XIAO NFC).

## Alimentation, charge et empilage (stack)

**Tous les composants sont sur la face AVANT** (gravure simple face pour les
pièces). La face avant porte aussi la **bobine NFC** (surface de tap). La
**batterie occupe seule l'arrière**, dans le boîtier.

```
[ téléphone ]
  bobine NFC          face AVANT du PCB (cuivre vers le téléphone)
  PCB  (XIAO, Wio, pogo, switch, bouton, caps, TP sur l'avant)
  --- film ferrite 0,1 mm ---   <-- indispensable pour le NFC
  BATTERIE Ø45 1050 mAh         collée au dos, dans le boîtier
[ dos du boîtier ]
```

- **Batterie** : LPR604543 ronde Ø45 × 6 mm, 1050 mAh, PCM ; fils soudés sur les
  pastilles `BT1` (BAT+/BAT−). Elle n'a **pas** de modèle 3D sur la PCB (ce n'est
  pas un composant CMS). Le chargeur BQ25101 du XIAO charge à 50/100 mA.
- **Film ferrite 0,1 mm** entre la bobine et la batterie : **obligatoire**. Le PCB
  (FR4) est transparent au champ magnétique et ne protège pas ; sans ferrite,
  l'enveloppe aluminium de la batterie absorbe le champ et tue le NFC. ~2 €.
- **Port pogo magnétique `J5`** (Xinyangze YZT0675, 4P pas 2,50 mm, contacts plats +
  2 aimants) : VBUS/GND/D+/D− → charge + flash UF2 + série USB. Le câble doit être
  un **mâle à ressorts 4P au pas de 2,5 mm** avec le **même ordre de broches** et
  des aimants de polarité opposée (sinon VBUS/GND s'inversent).
- **USB-C du XIAO** non exposé ; dessoudage optionnel pour gagner de la hauteur.
  Les pogo D+/D− se câblent alors sur les pads USB du XIAO (`TP5`/`TP6`).

## État du routage (à finir dans la GUI KiCad)

Le disque est **placé** (0 conflit de pastilles), les plans GND coulés, mais
l'auto-routeur ne boucle pas tout sur 2 couches à cette densité. **~13 liaisons
courtes restent à tirer à la main** (SPI LoRa U1↔U2, NFC, VBATT, RST) — ~15 min
dans KiCad, en passant par la face arrière là où le plan GND laisse la place.

## Limitations connues (à finir dans la GUI KiCad)

- **~13 nets non routés** (voir ci-dessus) : SPI LoRa, NFC1/NFC2, VBATT, RST_MCU.
- **Ratsnest bobine NFC** : la spirale est du cuivre d'empreinte (net-tie) ;
  KiCad peut la signaler « non connectée » alors qu'elle est physiquement continue.
- **`solder_mask_bridge`** entre pastilles castellées serrées du XIAO : cosmétique,
  accepté par les fabricants (ponts de masque tolérés sur ce module).
- Antenne LoRa, batterie et boîtier : voir `docs/bom_v2.md`.

## Fabrication maison (photogravure UV, double face)

Règles de conception adaptées à la **photogravure UV maison**, pas à un fab pro :

| Paramètre | Valeur |
|---|---|
| Couches | 2 (F.Cu + B.Cu uniquement) |
| Largeur de piste | **0,3 mm** |
| Isolation | **0,3 mm** |
| Vias | **⌀1,0 mm pad / perçage 0,6 mm** — métallisés à la main (rivet ou fil soudé des deux côtés) |
| Calage recto-verso | 3 repères `FID1/2/3` (trous ⌀0,6) en triangle : percer puis aligner les deux films dessus |

**Procédure vias maison** : chaque via se perce à 0,6 mm puis se métallise avec un
rivet à œillet ou un bout de fil soudé sur les deux faces. Il faut donc router en
gardant les vias **hors des composants** (soudables des deux côtés).

> ⚠️ **Via central de la bobine NFC** : il tombe sous le XIAO. Le riveter/souder
> **avant** de poser le XIAO, ou déplacer la bobine `AE1` dans la zone libre en bas
> du disque si l'accès est requis après assemblage.

# ezCore
