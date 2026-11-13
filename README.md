# MeshTag — porte-clés compagnon MeshCore

Compagnon MeshCore ultra-compact (format porte-clés) construit autour du
**Seeed XIAO nRF52840** + module LoRa **Wio-SX1262** (EU868), avec appairage BLE
sans code, mise à jour OTA par application, antenne NFC intégrée pour l'appairage
par approche, et gestion de la batterie sur la carte.

> État : la PCB est **générée par script** et routée automatiquement. L'ERC passe
> (0/0). La DRC a quelques points cosmétiques à finir à la main dans KiCad (voir
> « Limitations connues »). Tout est reproductible via les scripts de `hardware/tools/`.

## Arborescence

```
meshtag/
├── README.md
├── docs/                     notes de conception
└── hardware/
    ├── MeshTag.kicad_pro      projet KiCad 9
    ├── MeshTag.kicad_sch      schéma (généré)
    ├── MeshTag.kicad_pcb      PCB 2 couches 26 × 52 mm (généré + routé)
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

Bobine rectangulaire 5 tours/couche, ~1,5–2 µH estimés. **La valeur exacte doit
être mesurée au NanoVNA** puis les condensateurs C3/C4 choisis entre 33 et 150 pF
(C0G 0402) pour résonner à 13,56 MHz — procédure standard (wiki Seeed XIAO NFC).

## Limitations connues (à finir dans la GUI KiCad)

- **Trou porte-clés** : laissé en cercle Edge.Cuts ; à transformer en trou NPTH
  propre (il génère quelques `copper_edge_clearance`).
- **Ratsnest bobine NFC** : la spirale est du cuivre d'empreinte (net-tie) ;
  KiCad la signale « non connectée » dans le ratsnest alors qu'elle est
  physiquement continue. À relier par un petit via/segment en GUI si besoin.
- **1 `starved_thermal`** sur une pastille GND (une seule branche thermique).
- Antenne LoRa, batterie et boîtier : voir `docs/` et la BOM de sourcing.

# ezCore
