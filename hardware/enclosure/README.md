# MeshTag — boîtier (Onshape / FeatureScript)

Galet type AirTag, **Ø53,7 × ~10 mm**, généré paramétriquement.

## Direction design
- **Face avant = dôme nu** (sphère R120, apex 6,7 mm) : aucune fonction sur la surface vue.
- **Tout au dos** : creux de recharge magnétique (pogo), bouton, interrupteur coulissant, anneau métal d'accent autour de la zone de charge.
- **LED** diffusée sous une paroi amincie à 0,45 mm (pas de trou traversant).
- **Oreille porte-clés** fondue dans le bord (congé), œillet Ø2,8 traversant.
- Joint près de l'équateur, rayons de bord 1,6 mm.
- Couleur : corps blanc-os chaud `#F2F1ED`, anneau de charge métal `#D7D7DA`.

## Pièces générées
`MeshTag Front`, `MeshTag Back`, `Button`, `LED Lens`, `Charge Ring`, `Slide Switch`.

## Repère (case frame)
Origine = centre de la carte, z=0 = face supérieure du PCB, +z vers l'avant.
Positions des composants extraites du STEP KiCad exporté sans l'USB-C
(`hardware/fab/MeshTag_PCB_noUSBC.step`).

## Dégagement
Jeu minimum coque ↔ composant **0,34 mm** (le point le plus serré est le module
Wio-SX1262), calculé sur le nuage de points réel du STEP — voir `design.py`.

## Scripts
- `pcbpts.py` : exporte le nuage de points des composants (repère boîtier) depuis le STEP.
- `design.py` : résout l'apex du dôme pour un jeu cible et imprime toutes les cotes.
- `proxies.py` : génère les boîtes-proxy par composant (contrôle de collision).

## Document Onshape
Feature Studio **« MeshTag Case »** :
https://cad.onshape.com/documents/ce37c7863617d0796cb32671/w/9332b5ea8f7052c2ece76ac3/e/b564788106011a73f2345a97

Pour générer les pièces : ouvrir le Part Studio (PCB importée), ajouter la
fonction **MeshTag Case** depuis la barre d'outils, OK.

## Limites connues / à finir
- Collision Onshape (`evCollision`) non rejouée de façon fiable (quotas sandbox) ;
  le jeu est prouvé analytiquement sur le maillage.
- Accostage du doigt du coulisseau sur le levier de SW3 : à vérifier en impression.
- Rayons de raccord (congés cosmétiques du joint, lissage du creux de charge) : à
  peaufiner dans la GUI Onshape si besoin.
- Le connecteur USB-C du XIAO est **exclu** de la géométrie (à dessouder).
