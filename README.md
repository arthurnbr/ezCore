# ezCore — porte-clés compagnon MeshCore (V2, circulaire)

Compagnon MeshCore ultra-compact en **disque Ø48 mm** (type AirTag, en plus gros)
construit autour du **Seeed XIAO nRF52840** + module LoRa **Wio-SX1262** (EU868) :
appairage BLE sans code, mise à jour OTA par application, **antenne NFC ronde
intégrée** pour l'appairage par approche, **port de charge/flash magnétique 4
points** (pogo), et batterie **1000 mAh** gérée sur la carte.

> État : PCB **générée par script** et routée (Freerouting). ERC 0/0. Quelques
> points DRC cosmétiques à finir dans KiCad (voir « Limitations connues »). Tout
> est reproductible via `hardware/tools/`.

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
    │   └── 3dmodels/
    ├── tools/
    │   ├── build_pcb.py       place les empreintes, dessine le contour, zones
    │   └── route_pcb.sh       DSN → Freerouting → import SES → zones → DRC
    └── fab/
        ├── gerbers/           Gerbers + perçage (Protel + gbrjob)
        └── BOM.csv
```

Toutes les bibliothèques (symboles, empreintes, modèle 3D) sont **copiées dans le
projet** : rien ne dépend des bibliothèques système.

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

Brochage LoRa identique à la variante MeshCore `xiao_nrf52` (pour ne pas toucher
au firmware) :

| Signal Wio-SX1262 | Broche XIAO | Net        |
|-------------------|-------------|------------|
| NSS               | D4          | LORA_NSS   |
| DIO1              | D1          | LORA_DIO1  |
| NRST              | D2          | LORA_RST   |
| BUSY              | D3          | LORA_BUSY  |
| RF_SW / RXEN      | D5          | LORA_RXEN  |
| SCK / MISO / MOSI | D8 / D9 / D10 | SPI_*    |

- **U1** XIAO nRF52840 (CMS à plat, castellations), face avant.
- **U2** module Wio-SX1262 nu (IPEX), face avant, au-dessus du XIAO.
- **AE1** bobine NFC 2 couches (net-tie NFC1/NFC2) pour l'appairage par approche.
- **C1/C2** découplage 3V3 ; **C3/C4** condensateurs d'accord NFC (face arrière).
- **SW1** bouton utilisateur ; **SW3** interrupteur de coupure batterie.
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

## Alimentation et charge

- **Batterie** : LPR604543 ronde Ø45 × 6 mm, 1050 mAh, PCM (fils soudés sur les
  pastilles `BT1` BAT+/BAT−). Le chargeur BQ25101 du XIAO charge à 50/100 mA.
- **Port pogo `J5`** (VBUS/GND/D+/D−) : charge + flash UF2 + série USB.
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
