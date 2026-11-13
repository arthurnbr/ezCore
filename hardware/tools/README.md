# Outils de génération

- `build_pcb.py` : place les 14 empreintes (par centre de corps), dessine le
  contour arrondi + trou porte-clés, écrit le keep-out bobine NFC, et prépare les
  zones. `finalize` (appelé par le script de routage) ajoute le keep-out antenne
  BLE + les plans de masse puis remplit les zones.
- `route_pcb.sh` : exporte le DSN, lance Freerouting, réimporte la session,
  finalise les zones, lance la DRC.

Freerouting 2.5 nécessite un JRE >= 23. Récupérer le jar :
https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar
et pointer `FREEROUTING_JAR` dessus (ou le poser dans ce dossier).
