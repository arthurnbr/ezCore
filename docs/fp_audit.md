# Audit des footprints — projet ezCore / MeshTag

Audit réalisé le 2026-11-13. KiCad installé : **9.0.2**. Racine des modèles 3D vérifiée :
`/usr/share/kicad/3dmodels/` (variable `${KICAD9_3DMODEL_DIR}`).

Convention : chaque chemin `.step` listé ci-dessous a été **vérifié présent** sur le disque
(`ls`), sauf mention `[FICHIER ABSENT]` ou `[NON VÉRIFIÉ]`.

Les 13 footprints `MeshTag.pretty/` ont été lus pour confronter leur géométrie réelle aux
datasheets.

---

## 1. XIAO-nRF52840-SMD

- **Dims attendues** : carte 21 × 17,8 mm (form-factor XIAO). 2 rangées de 7 pads castellated
  au pas **2,54 mm**, + pads arrière (BAT+/BAT−, NFC).
  Source : datasheet Seeed « XIAO nRF52840 » SKU 102010448 —
  https://files.seeedstudio.com/Bazaar/product_pdf/102010448.pdf
  (confirmé « Ultra Small Size : 21 x 17.8 mm » ; wiki Seeed idem).
- **Géométrie du footprint projet** : contour F.Fab = 17,8 mm (X) × 20,95 mm (Y), pads
  2,75 × 2,0 mm au pas 2,54 mm. → cohérent avec 21 × 17,8 mm (la carte réelle dépasse
  légèrement le contour copper, normal pour un module castellated). **OK.**
- **Modèle 3D** :
  - Seeed **ne publie pas** de STEP officiel propre du XIAO nRF52840 sur son dépôt de
    fichiers (pas de `.step` dans la page produit / wiki). [NON VÉRIFIÉ côté Seeed]
  - STEP tiers téléchargeable (représentation carte complète) :
    https://marathon-os.com/library/seeed-studio-xiao-nrf52840-3d-6811d9ae43b4d50b11a5916a
  - **Primitive KiCad générique de repli** : aucun modèle « XIAO » dans la lib KiCad.
    Utiliser un bloc générique ou le header SMD
    `/usr/share/kicad/3dmodels/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x07_P2.54mm_Vertical_SMD_Pin1Left.step`
    ×2 comme approximation des castellations (cosmétique uniquement).

## 2. Wio-SX1262-Module (module nu, 12 pins CMS)

- **Dims attendues** : **11,6 × 11 × 2,95 mm**, 12 pins SMT, port IPEX.
  Source : datasheet Seeed « Wio-SX1262 LoRa Module » V1.1 —
  https://files.seeedstudio.com/products/SenseCAP/Wio_SX1262/Wio-SX1262_Module_Datasheet.pdf
  (fiche produit : « 11.6mm x 11mm x 2.95mm @12 pins SMT » ; noter que certaines pages
  marchand indiquent par erreur « 6mm x 11mm »).
- **Géométrie du footprint projet** : contour silk = 11,6 × 11,0 mm
  (−5,8→5,8 × −5,5→5,5), 8 pads en haut + 4 en bas, pas **1,27 mm**, pads 0,6 × 1,4 mm.
  → cohérent avec la datasheet (Fig. 9). **OK.**
- **Modèle 3D** :
  - Seeed fournit un STEP de la **carte porteuse « Wio-SX1262 for XIAO »**
    (pas du module nu) : page produit https://www.seeedstudio.com/Wio-SX1262-for-XIAO-p-6379.html
    (section Downloads ; nom couramment cité `Wio-SX1262_for_XIAO_3D_file.step`). [NON VÉRIFIÉ URL directe]
  - STEP libre du « Wio-SX1262 for XIAO » (communauté, complet) :
    https://www.printables.com/model/1672910-cad-file-for-seeed-studio-wio-sx1262-for-xiao/files
  - **Repli primitif KiCad** : aucun modèle SX1262. Utiliser une boîte générique 11,6×11×2,95 mm
    (pas de `.step` KiCad dédié).

## 3. Pogo_4P_2.54mm (connecteur pogo / magnétique 4 pins, pas 2,54 mm)

- **Dims attendues** : footprint custom (pas de composant catalogue imposé). Pads cibles
  circulaires Ø2,0 mm, pas 2,54 mm, span −3,81→+3,81 mm (VBUS/GND/D+/D−). **OK** (c'est
  un pattern de cibles de contact, pas un boîtier).
- **Modèle 3D (primitive KiCad générique la plus proche)** — header 1×4 au pas 2,54 mm :
  `/usr/share/kicad/3dmodels/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step` ✅ présent
  (variantes aussi présentes : `PinHeader_1x04_P2.54mm_Horizontal.step`,
  `PinHeader_1x04_P2.54mm_Vertical_SMD_Pin1Left.step`,
  `PinHeader_1x04_P2.54mm_Vertical_SMD_Pin1Right.step`).
  → modèle purement cosmétique (un connecteur pogo n'est pas un header, mais pas/compte OK).

## 4. Batt_WirePads_2x (2 pastilles pour fils LiPo)

- **Dims** : 2 pads roundrect 1,6 × 2,4 mm au pas 3,6 mm (−1,8 / +1,8), BAT+/BAT−. Footprint
  custom, aucune datasheet. **OK.**
- **Modèle 3D** : **aucun requis** (simples pastilles de soudure, pas de corps).
  Placeholder suggéré si un volume est souhaité en 3D : petit cube/cylindre générique, ou
  réutiliser un modèle de fil ; sinon laisser **sans modèle 3D**.

## 5. NFC_Coil_Round (bobine PCB, net-tie cuivre)

- **Dims** : bobine 2 couches, 6 tours/couche, Ø≈13 mm, via central Ø0,6 mm. Footprint custom. **OK.**
- **Modèle 3D** : **aucun** — c'est uniquement du cuivre (pas de composant posé). Correct de
  ne référencer aucun `.step`.

## 6. Fiducial_Align_1.5mm

- **Dims** : repère d'alignement traversant, cercle silk Ø1,5 mm, trou Ø0,6 mm. Footprint custom. **OK.**
- **Modèle 3D** : **aucun** (repère de process). Correct.

---

## Footprints standards KiCad (chemin `.step` exact vérifié)

| Footprint projet | Dims attendues | Chemin 3D KiCad (vérifié) |
|---|---|---|
| **C_0402_1005Metric** | standard KiCad (0402 imperial / 1005 metric, 1,0×0,5 mm) | `/usr/share/kicad/3dmodels/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` ✅ |
| **C_0603_1608Metric** | standard KiCad (0603 imperial / 1608 metric, 1,6×0,8 mm) | `/usr/share/kicad/3dmodels/Capacitor_SMD.3dshapes/C_0603_1608Metric.step` ✅ |
| **SW_SPDT_PCM12** | C&K PCM12SMTR : corps **6,7 × 2,6 mm** (voir §switches) | `/usr/share/kicad/3dmodels/Button_Switch_SMD.3dshapes/SW_SPDT_PCM12.step` ✅ |
| **SW_Push_1P1T_NO_CK_KMR2** | C&K KMR2 : corps **4,2 × 2,8 mm**, h 1,9 mm (voir §switches) | `…/Button_Switch_SMD.3dshapes/SW_Push_1P1T_NO_CK_KMR2.step` ❌ **[FICHIER ABSENT]** |
| **TestPoint_Pad_1.0x1.0mm** | pad CMS carré 1,0 mm — standard KiCad | **aucun 3D** (le footprint standard KiCad ne référence aucun `.step`) |
| **MountingHole_3.2mm_M3** | trou Ø3,2 mm M3 — standard KiCad | **aucun 3D** (trou nu, pas de modèle ; le footprint standard n'a pas de ligne `model`) |

### ⚠️ Anomalie majeure — SW_Push_1P1T_NO_CK_KMR2
Le footprint (celui du projet **et** celui de la lib standard KiCad 9
`Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod`) référence :
`${KICAD9_3DMODEL_DIR}/Button_Switch_SMD.3dshapes/SW_Push_1P1T_NO_CK_KMR2.step`
**mais ce fichier n'existe PAS** dans `/usr/share/kicad/3dmodels/Button_Switch_SMD.3dshapes/`
(KiCad 9.0.2 — vérifié par `ls`). Référence 3D cassée.

**Replis possibles** (modèles SMD C&K réellement présents dans la lib) :
- `…/Button_Switch_SMD.3dshapes/SW_Tactile_SPST_NO_Straight_CK_PTS636Sx25SMTRLFS.step` ✅
  (autre tactile SMD C&K, géométrie proche mais plus grand) ;
- ou créer/importer un STEP KMR2 dédié (voir datasheet §switches).

### Note TestPoint / MountingHole
Confirmé : `TestPoint.3dshapes/` ne contient que des variantes Bridge / Keystone / Loop —
**aucun modèle « Pad »** (un point de test pad-only n'a pas de corps 3D, c'est normal).
`MountingEquipment.3dshapes/` ne contient aucun modèle de trou M3 3,2 mm (normal : un trou
de perçage n'est pas un composant).

---

## Confirmation dimensions des switches C&K

### KMR2 series (KMR221GLFS)
- **Dims réelles (datasheet)** : corps **4,2 ± 0,2 mm (L) × 2,8 mm (l)**, **hauteur totale 1,9 mm**
  (actuateur). Terminaux gullwing SMT, course 0,20 mm.
  ⚠️ **Correction vs l'énoncé** : l'énoncé donnait « 4,2 × 2,8 × 1,4 mm ». Le **1,4 mm** correspond
  à la hauteur jusqu'à l'épaulement, pas à la hauteur totale ; la **hauteur hors-tout est 1,9 mm**
  (le titre de la datasheet dit « 4.2 x 2.2 mm with 1.9 mm Height Actuator » — le 2,2 mm étant une
  cote interne ; l'empreinte hors-tout du boîtier est 4,2 × 2,8 mm).
- **Datasheet C&K / Littelfuse (KMR2 series)** :
  https://static.chipdip.ru/lib2/a/544/DOC068544469.pdf
  (page produit Littelfuse : https://www.littelfuse.com — série KMR2 ;
  fiche part KMR221GLFS : https://www.tme.com/.../kmr221g-lfs).

### PCM12SMTR (slide SPDT)
- **Dims réelles (datasheet)** : corps hors-tout **6,7 mm × 2,6 mm**, hauteur ≈ 1,5 mm
  (profil bas), actuateur slide, terminaux CMS pour PCB. → **conforme** à l'énoncé (6,7 × 2,6 mm).
- **Datasheet C&K / Littelfuse (PCM series)** :
  https://pdf.htelec.com/pdf/22/pcm.pdf
  (ou officielle Littelfuse :
  https://www.littelfuse.com/products/switches/slide-switches/pcm/pcm12smtr ).

---

## Synthèse (13 footprints)

| # | Footprint | Dims | Source 3D |
|---|---|---|---|
| 1 | XIAO-nRF52840-SMD | 21×17,8 mm, pas 2,54 | STEP tiers (Marathon-OS) / repli header 1x07 SMD |
| 2 | Wio-SX1262-Module | 11,6×11×2,95 mm, pas 1,27 | STEP Seeed « for XIAO » / Printables 1672910 |
| 3 | Pogo_4P_2.54mm | Ø2,0 pads, pas 2,54 | `PinHeader_1x04_P2.54mm_Vertical.step` ✅ |
| 4 | Batt_WirePads_2x | pads 1,6×2,4, pas 3,6 | aucun (pastilles) — placeholder optionnel |
| 5 | NFC_Coil_Round | Ø13 mm, 6 t/couche | aucun (cuivre) |
| 6 | Fiducial_Align_1.5mm | cercle Ø1,5, trou Ø0,6 | aucun (repère) |
| 7 | C_0402_1005Metric | standard KiCad | `Capacitor_SMD.3dshapes/C_0402_1005Metric.step` ✅ |
| 8 | C_0603_1608Metric | standard KiCad | `Capacitor_SMD.3dshapes/C_0603_1608Metric.step` ✅ |
| 9 | SW_Push_1P1T_NO_CK_KMR2 | 4,2×2,8×1,9 mm | ❌ STEP KiCad **absent** → repli PTS636 ou STEP custom |
| 10 | SW_SPDT_PCM12 | 6,7×2,6 mm | `Button_Switch_SMD.3dshapes/SW_SPDT_PCM12.step` ✅ |
| 11 | TestPoint_Pad_1.0x1.0mm | standard KiCad (pad 1,0 mm) | aucun (pad) |
| 12 | MountingHole_3.2mm_M3 | standard KiCad (Ø3,2 M3) | aucun (trou) |
| 13 | NFC_Coil_5T_2L* | bobine PCB (variante 5 tours) | aucun (cuivre) |

\* `NFC_Coil_5T_2L.kicad_mod` est également présent dans la lib (variante de bobine) — même
traitement que NFC_Coil_Round : pas de 3D.

**Action requise la plus critique** : la référence 3D de `SW_Push_1P1T_NO_CK_KMR2` pointe vers un
`.step` inexistant en KiCad 9.0.2 → corriger (pointer vers un modèle présent, ou importer un STEP
KMR2). Toutes les autres références 3D de composants (C_0402, C_0603, SW_SPDT_PCM12) sont valides,
et les footprints custom / pads / trous / bobines n'ont légitimement pas de modèle 3D.
