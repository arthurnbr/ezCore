# MeshTag — Sourcing BOM (prototypes FR/EU, relevé du 2026-11-13)

Les prix et URL ci-dessous viennent de pages consultées le 2026-11-13, ou d'extraits de résultats de recherche quand c'est indiqué. Tout ce qui n'a pas été vérifié directement est marqué **[NON VÉRIFIÉ]**. Pour la conversion, j'ai pris **1 USD ≈ 0,86 €** **[NON VÉRIFIÉ]** : c'est une hypothèse, pas un taux relevé.

## 0. Kit Meshtastic 102010710 : état de soudure (question 1)

| Point | Constat | Source |
|---|---|---|
| Contenu du kit | « XIAO nRF52840 x1, Wio-SX1262 extension board x1, LoRa antenna x1 » ; prix 13,49 $ HT, en stock | https://jp.seeedstudio.com/XIAO-nRF52840-Wio-SX1262-Kit-for-Meshtastic-p-6400.html · https://www.seeedstudio.com/XIAO-nRF52840-Wio-SX1262-Kit-for-Meshtastic-p-6400.html |
| Module Wio-SX1262 sur l'adaptateur « Wio-SX1262 for XIAO » (113010003) | **Oui, le module est soudé en usine** sur l'adaptateur. La photo produit montre le module CMS avec son IPEX sur la carte, qui porte des **connecteurs femelles** 2×7. La page indique « Pin headers for plug-and-play… no soldering needed ». | https://www.seeedstudio.com/Wio-SX1262-for-XIAO-p-6379.html · photo `3-102010710-nrf52840_wio-sx1262-kit_1.jpg` |
| XIAO du kit : headers pré-soudés ? | **Très probablement oui.** Botland répond à un client : « These two modules are already connected via gold-pin headers, so there is no need to solder them ». Sur la photo du kit, les castellations du XIAO sont garnies de soudure, comme sur une carte à broches mâles. Ce n'est pas écrit noir sur blanc par Seeed : **[INFERENCE]**. | https://botland.store/lora-lorawan/26528-xiao-nrf52840-wio-sx1262-kit-for-meshtastic-lorabluetooth-seeedstudio-102010710-5904422387815.html |
| Conséquence | Le kit ne convient **pas** à un montage CMS à plat sur notre PCB : le XIAO a des broches et le SX1262 est déjà soudé sur sa carte fille. Il faut acheter séparément le **XIAO 102010448 sans broches** et le **module nu 114993390**. À noter : XIAO 9,90 $ + module 4,29 $ = 14,19 $, contre 13,49 $ pour le kit, donc presque le même prix. | — |
| Référence à éviter | **102010631**, la version « Pre-Soldered » (broches déjà soudées) | https://www.gotronic.fr/art-carte-xiao-nrf52840-soude-47616.htm |

## 1. Tableau BOM

| Réf | Fonction | MPN exact | Specs clés / dimensions | Fournisseur(s) + URL | Prix unitaire (2026-11) | Stock | Alternative |
|---|---|---|---|---|---|---|---|
| **U1** | MCU BLE/NFC (XIAO) | Seeed **102010448** (XIAO nRF52840, non-Sense, non-Plus) | 21 × 17,8 mm, CMS à castellations, rien en face arrière. Livré **broches non soudées** : « Seeed Studio XIAO nRF52840 (pin not included) x1, 7 Pin Header x2 » | Seeed : https://www.seeedstudio.com/Seeed-XIAO-BLE-nRF52840-p-5201.html | 9,90 $ HT (option « Un-Soldered ») | non indiqué | — |
| | | | | Gotronic (FR) : https://www.gotronic.fr/art-carte-xiao-ble-nrf52840-34718.htm | **15,20 € TTC** (12,67 € HT) | En stock | |
| | | | | DigiKey : https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/102010448/16652893 | 10,38 $ (qté 1) | 2 096 | |
| | | | | Mouser : https://www.mouser.com/en/ProductDetail/Seeed-Studio/102010448?qs=Znm5pLBrcAJ5g%252BWAkitg4w%3D%3D | 10,38 $ (extrait de recherche ; page bloquée en anti-bot) | [NON VÉRIFIÉ] | |
| | | | | Farnell BE : https://be.farnell.com/en-BE/seeed-studio/102010448/xiao-board-arm-arduino-board/dp/4060351 (réf. 4060351) | [NON VÉRIFIÉ] (HTTP 403) | [NON VÉRIFIÉ] | |
| | | | | Kubii : aucune fiche trouvée | — | — | TME (fiche SEEED-102010448 vue en recherche) [NON VÉRIFIÉ] |
| **U2** | Radio LoRa SX1262 | Seeed **114993390** (Wio-SX1262, IPEX, bande) | 11,6 × 11 × 2,95 mm, 12 broches CMS, TCXO, 22 dBm, **TX 125 mA @22 dBm**, veille 1,62 µA ; antenne « IPEX port or SMT pin, default IPEX » | Seeed : https://www.seeedstudio.com/Wio-SX1262-Wireless-Module-p-5981.html | **4,29 $ HT** | En stock | **113991436** « Wio-SX1262-N », **sans IPEX, RF sur broche CMS**, 4,29 $ : https://www.seeedstudio.com/Wio-SX1262-Wireless-Module-without-IPEX-Tape-Reel-p-6417.html. **Oui, la variante RF sur broche CMS se commande** (DigiKey 113991436 vu en recherche). |
| | | | | DigiKey : https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/114993390/25835823 | 5,95 $ (bande coupée, qté 1) | **0, réappro de 1 000 attendue le 18-01-2027** | OpenELAB (vu en recherche) [NON VÉRIFIÉ] |
| **AE1** | Antenne FPC 868 MHz, câble U.FL | **The Antenna Company AC61005-100UF** (recommandée) | **24,85 × 24,85 × 0,25 mm**, câble 1,13 mm de **100 mm**, MHF1/U.FL, 868 MHz : efficacité 66 %, VSWR 1,6, adhésif 3M 467MP | DigiKey : https://www.digikey.com/en/products/detail/the-antenna-company/AC61005-100UF/29427033 · fiche technique : https://www.antennacompany.com/wp-content/uploads/datasheet/AC61005-ds.pdf | **2,70 $** (2,33 $ par 10) | 1 843 | **Molex 211140-0100** : 38 × 10 × 0,1 mm, câble 100 mm, efficacité >55 % @868, TME 1,20–1,97 $, stock 408 : https://www.tme.eu/en/details/2111400100/rf-antennas/molex/211140-0100 |
| **BT1** | Pouch LiPo 1S avec PCM | **EREMIT 502030 250 mAh** (recommandée : tient dans 25 × 35 mm) | 30 × 20 × 5 mm, ≥250 mAh, **0,5C = 125 mA en continu, >1C en pic**, PCM (surcharge >4,25 V, décharge profonde <3 V, court-circuit, >2C), certifiée IEC62133-2. Connecteur JST-PH 2,0 à couper. | Eremit (DE) : https://www.eremit.de/p/eremit-3-7v-250mah-lipo-akku-502030 | **3,59 € TTC** | Auf Lager | voir le tableau BT1 ci-dessous |
| **SW1, SW2** | Bouton utilisateur / reset | **C&K KMR221GLFS** | 4,2 × 2,8 × 1,4 mm (bouton de 1,9 mm), SPST-NO, 2 N, 50 mA/32 V, CMS | TME : https://www.tme.com/us/en-us/details/kmr221glfs/microswitches-tact/c-k/kmr221g-lfs | 0,32–0,49 $ | 14 151 d'après les données de la fiche (l'affichage HTML dit 0, incohérent) | Future Electronics (vu en recherche) [NON VÉRIFIÉ] |
| **SW3** | Interrupteur coupure batterie | **C&K PCM12SMTR** | SPDT ON-ON, **0,3 A/6 V**, 6,7 × 2,6 × 1,4 mm, CMS | TME : https://www.tme.eu/ie/en/details/pcm12smtr/slide-switches/c-k | **0,63–0,93 €** | 6 652 | SHOU HAN **MSK12C02** (LCSC C431540), dès 0,0305 $, stock 164 070 : https://www.lcsc.com/product-detail/Slide-Switches_SHOU-HAN-MSK12C02_C431540.html. **Attention : 50 mA nominal**, voir les notes. |
| **C1** | Découplage 10 µF | **Murata GRM188R61A106KE69D** | 0603, X5R, 10 V, ±10 % | TME : https://www.tme.eu/en/details/grm188r61a106ke69d/mlcc-smd-capacitors/murata/ | 0,0081–0,12 $ | **0 chez TME (« hardly available »)** | Samsung CL10A106KP8NNNC (10 µF 0603 X5R 10 V) [NON VÉRIFIÉ], ou n'importe quel 10 µF 0603 X5R ≥10 V en stock |
| **C2** | Découplage 100 nF | **Murata GRM155R71C104KA88D** | 0402, X7R, 16 V | TME (via Findchips) : https://www.findchips.com/search/GRM155R71C104KA88D | 0,0023–0,04 $ | TME 240 290 | Mouser (vu en recherche, stock 6,8 M) |
| **C3/C4** | Accord NFC, C0G 50 V 0402 | **GRM1555C1H330JA01D** (33 pF), **GRM1555C1H390JA01D** (39 pF), **GRM1555C1H470JA01D** (47 pF), **GRM1555C1H560JA01D** (56 pF), **GRM1555C1H680JA01D** (68 pF) | 0402 (1,0 × 0,5 mm), C0G, 50 V, ±5 % (J) | 39 pF chez TME : https://www.findchips.com/search/GRM1555C1H390JA01D · 47 pF : https://www.digikey.com/en/products/detail/murata-electronics/GRM1555C1H470JA01D/3693853 · 68 pF : https://www.digikey.com/en/products/detail/murata-electronics/GRM1555C1H680JA01D/3175195 | 39 pF : 0,004–0,09 $ (TME) ; autres valeurs [NON VÉRIFIÉ], même ordre de grandeur | 39 pF : TME 12 698 | Toute série C0G 0402 50 V (ex. Samsung CL05C) [NON VÉRIFIÉ] |
| **PCB** | 2 couches, 24 × 45 mm, 1,0 mm, ENIG, 5 pcs | — | — | voir le tableau PCB ci-dessous | ≈ 20–25 $ chez JLC [estimation] | — | Aisler (DE) |
| Outil | Profileur de puissance | Nordic **NRF-PPK2** | — | Farnell IE/BE (extrait) : https://ie.farnell.com/nordic-semiconductor/nrf-ppk2/power-profiler-kit-ii/dp/3595499 ; Mouser HR (extrait) : https://hr.mouser.com/ProductDetail/Nordic-Semiconductor/nRF-PPK2?qs=hd1VzrDQEGilgnS3iQ3EVw%3D%3D | **83,58 € HT** (Farnell), 83,57 € (Mouser) | [NON VÉRIFIÉ] | Adafruit 5048, 99,95 $ |
| Outil | VNA (antenne + NFC) | **NanoVNA-H4** (Hugen, HW 4.3) | 10 kHz–1,5 GHz, 4", batterie 1 950 mAh, kit SOL fourni | SDRstore (EU) : https://www.sdrstore.eu/test-and-measurement/spectrum-analyzer/nanovna-h4-10khz-1-5ghz-portable-vector-network-analyzer-vna-for-mf-hf-vhf-uhf-shf | **106,48 €** | In stock | Eleshop NL (original Hugen) : https://www.eleshop.nl/nanovna-h4.html (prix non extrait) |
| Outil | Pont LCR USB | — | — | — | **Pas nécessaire** | — | Le NanoVNA mesure directement les 33–68 pF et la bobine NFC à 13,56 MHz |

## 2. Comparatif des antennes (AE1) : boîtier ~28 × 50 × 12 mm

| Antenne | Dimensions (mm) | Câble | Eff./gain @868 | Tient dans 28 × 50 ? | Prix relevé | Source |
|---|---|---|---|---|---|---|
| **AC61005-100UF** | **24,85 × 24,85 × 0,25** | 100 mm (pas de variante 50 mm) | 66 %, crête 2,5 dBi | **Oui** | 2,70 $ DigiKey | fiche technique AC61005 + DigiKey |
| Molex 211140-0100 | **38 × 10 × 0,1** | 100 mm | >55 %, crête 0,3 dBi | **Oui** (le plus étroit) | 1,20–1,97 $ TME | https://fccid.co/api/files/s1/mcq_xblpx_testreport_7677365_ad0de19a7c.pdf |
| Linx/TE ANT-8/9-FPC-UFL-100 | 39 × 15 × 0,2 | 100 mm | **15 %**, moy. −8,4 dBi | Oui, mais performance faible | Farnell 4,10–4,52 $ (Findchips) | https://resources.ampheo.com/static/datasheets/linx-technologies/ant-8-9-fpc-ufl-100.pdf |
| Antenna Co. AC61003 | 55,5 × 16,2 × 0,25 | **50**/100/150/200 mm | 69 % | **Non** (55,5 > 50) | prix non relevé | https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/9024/AC61003-ds.pdf |
| Taoglas FXP890.07.0100C | 62,2 × 20 × 1,6 | 100 mm | 49,7 % | **Non** | 4,88 $ DigiKey (stock 95) | https://www.taoglas.com/datasheets/FXP890.07.0100C.pdf |
| Molex 105262-0001 | 79 × 10 × 0,1 | 100 mm | crête 0,4 dBi, > −3 dB eff. | **Non** | 2,10–3,11 $ TME (stock 0) | https://www.tme.eu/en/details/1052620001/rf-antennas/molex/105262-0001/ |
| Siretta Echo 36B | 110 × 21 × 0,2 | 100 mm (Ø 0,81) | 75,5 % | **Non** | prix non relevé | https://www.siretta.com/wp-content/uploads/2026/09/Echo-36B-Datasheet-Rev-1.0.pdf |

**Recommandation : AC61005-100UF.** C'est la seule antenne qui est à la fois compacte et efficace (66 %). Elle se colle à plat sous la grande face (28 × 50) du boîtier, en face du PCB, avec un câble de 100 mm à lover. Si la place manque en largeur, prendre le Molex 211140-0100 (38 × 10 mm, efficacité >55 %). Aucune des antennes compatibles n'existe en 50 mm de câble ; seule l'AC61003 a une version 50 mm, et elle est trop longue.

## 3. Comparatif batteries (BT1) : ≤ 25 × 35 mm, 4–5 mm, PCM, ≥0,5C

| Pack | Dim. (mm) | Capacité | Décharge | Respecte ≤25 × 35 × 5 ? | Prix / source |
|---|---|---|---|---|---|
| **EREMIT 502030** | 30 × 20 × 5 | 250 mAh | 125 mA continu (0,5C), >1C en pic | **Oui** | 3,59 € TTC, stock DE : https://www.eremit.de/p/eremit-3-7v-250mah-lipo-akku-502030 |
| EEMB LP402535 | 25,5 × 36 × 4,3 | 320 mAh (min 300) | PCM complet | Dépasse de 0,5 × 1 mm | Amazon EEMB B08215N9R8 (vu en recherche, prix [NON VÉRIFIÉ]) ; fiche : https://eemb.store/products/lp402535 |
| LiPol Battery LP502535 | **35 × 25 × 5,0**, fils AWG28 de 50 mm, sans connecteur | 400 mAh | 0,5–1C | **Oui** | Expédition depuis la Chine, 99 $ de port : https://www.lipolbattery.com/Lithium-Ion-Polymer-Battery-LP502535.html |
| Gotronic PR502535 | 36 × 26 × 5,2 | 400 mAh | PCM, débit max [NON VÉRIFIÉ] | Légèrement trop grand | 7,60 € TTC, stock FR : https://www.gotronic.fr/art-accu-lipo-3-7-vcc-400-mah-pr502535-5812.htm |
| BerryBase PKCell LP-552035 | 35,5 × 20 × 5,5 | 350 mAh | **3C max** | Épaisseur 5,5 mm | https://www.berrybase.de/en/product-datasheet/019234a40e637392ba257f8ee97e49e3/create (prix [NON VÉRIFIÉ]) |
| Adafruit 2750 | 36 × 19,6 × 5,2 | 350 mAh | PCM, coupure à 3,0 V | Légèrement trop grand | 6,95 $ : https://www.adafruit.com/product/2750 |

Pas de fiche 402535, 502535 ou 452535 trouvée chez Eremit au 2026-11-13 (liste consultée : https://www.eremit.de/c/3-7v-lipo-akkus). Akkuplus et Conrad n'ont pas été vérifiés.

## 4. PCB et pochoir (5 pcs, 2 couches, 24 × 45 mm, 1,0 mm, ENIG)

| Fab | Données relevées | Estimation pour notre carte |
|---|---|---|
| **JLCPCB** | 100 × 100 / 2 couches / 10 pcs : HASL 5,00 $, **ENIG 23,80 $** ; épaisseurs 0,8 à 1,6 mm sans surcoût ; 5 pcs à 2 $ en promo JLCONE (relevé du 23-08-2026, https://comparepcb.com/articles/six-fields-set-your-pcb-price). Surcoûts « petites cartes » : ébavurage de 0,02 $/pcs si un côté mesure 1,5–3 cm (notre 24 mm est concerné), plus une majoration en livraison « Single PCB » si un côté ≤ 3 cm (https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra). **Pochoir ≤ 100 × 100 mm : 3 $** (https://jlcpcb.com/resources/small-stencil). | ≈ **20–25 $ de PCB + 3 $ de pochoir**, port en sus [estimation, devis non simulé] |
| PCBWay | 2 couches 100 × 100 : 5 $ les 10 pcs ; finition « Immersion gold » proposée, épaisseur 1,0 mm proposée (https://www.pcbway.com/pcb_prototype/2_Layer_pcb/100x100mm.html) | Surcoût ENIG et pochoir **[NON VÉRIFIÉ]** |
| Aisler (DE) | 2 couches ENIG Budget : job fee 12 € + 0,097 €/cm² × qté, par multiples de 3 ; pochoir : 5 € + 0,095 €/cm² (https://community.aisler.net/t/our-simple-pricing/102) | 10,8 cm², 6 pcs : 12 + 10,8 × 0,097 × 6 = **18,29 € HT** ; pochoir **6,03 € HT**. Le tarif publié est pour du 1,6 mm ; le 1,0 mm reste **[NON VÉRIFIÉ]**. |

## 5. Coût estimé

Les prix sont unitaires, en € (USD convertis à 0,86 [NON VÉRIFIÉ]). Je n'ai pas pu chiffrer précisément le port, j'ai mis un forfait estimé.

| Poste | 1 prototype | 5 prototypes |
|---|---|---|
| U1 XIAO 102010448 (Gotronic, 15,20 € TTC) | 15,20 | 76,00 |
| U2 Wio-SX1262 114993390 (Seeed, 4,29 $) | 3,69 | 18,45 |
| AE1 AC61005-100UF (2,70 $) | 2,32 | 11,60 |
| BT1 EREMIT 502030 | 3,59 | 17,95 |
| SW1 + SW2 KMR221GLFS (2 × 0,49 $) | 0,84 | 4,20 |
| SW3 PCM12SMTR (0,93 €) | 0,93 | 4,65 |
| C1 + C2 | 0,13 | 0,65 |
| Assortiment C3/C4 (10 pièces de chaque valeur × 5 valeurs, ~0,09 $) | 3,87 | 3,87 |
| PCB JLC 5 pcs ENIG + pochoir (~28 $, lot unique) | 24,00 | 24,00 |
| Port cumulé Seeed + Gotronic + Eremit + TME/DigiKey + JLC | ~30 [NON VÉRIFIÉ] | ~35 [NON VÉRIFIÉ] |
| **Total hors outils** | **≈ 85 €** | **≈ 200 €** (≈ 40 €/proto) |
| Outils optionnels : PPK2 83,58 € + NanoVNA-H4 106,48 € | +190 € | +190 € |

En prenant le XIAO chez Seeed (9,90 $ ≈ 8,51 €) au lieu de Gotronic, on économise environ 6,7 €/unité, mais le port depuis Seeed n'a pas été vérifié.

## Notes

1. **SW3 et MSK12C02** : le MSK12C02 n'est donné que pour **50 mA** sur LCSC. Or la batterie fournit environ 125 mA en émission LoRa, plus jusqu'à 100 mA de charge. Je recommande donc de garder le **PCM12SMTR (0,3 A)**. Le MSK12C02 ne sert que si l'interrupteur coupe une ligne de commande et pas le courant batterie.
2. **C1 GRM188R61A106KE69D** : épuisé chez TME. Il faut vérifier Mouser/DigiKey au moment de la commande ou passer à un équivalent 10 µF 0603 X5R 10 V.
3. **U2 chez DigiKey** : rupture jusqu'au 18-01-2027. Il faut commander chez Seeed directement (en stock à 4,29 $).
4. **Wio-SX1262-N (113991436)** : variante sans IPEX, RF sur broche CMS, même prix. À retenir seulement si on route la RF sur le PCB vers un connecteur U.FL ; avec AE1 câblée, garder le 114993390.
5. **Batterie** : le chargeur BQ25101 du XIAO charge en 50 ou 100 mA, ce qui reste ≤ 0,5C pour 250 mAh et convient. Penser à couper le JST-PH et à souder les fils sur les pastilles BAT+/− du XIAO ou du PCB.
6. **Accès aux pages** : Mouser (anti-bot) et Farnell (HTTP 403) ont bloqué les lectures directes. Leurs prix proviennent uniquement d'extraits de recherche. Kubii, Akkuplus et Conrad n'ont rien donné d'exploitable.
