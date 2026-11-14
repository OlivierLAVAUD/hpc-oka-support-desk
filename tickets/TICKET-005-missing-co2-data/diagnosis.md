# Diagnostic — TICKET-005

## Cause racine
La colonne `ENERGY` est absente du DataFrame quand carbon_cost_RTE s'exécute.
L'enhancer de mesure d'énergie (ear_from_db.py ou ear_from_eacct.py) n'a pas été
exécuté en amont dans la chaîne d'exécution des enhancers. Sans données d'énergie,
le calcul d'empreinte carbone est impossible.

## Checklist de vérifications
- [x] Enhancer carbon_cost_RTE.py présent dans oka_dataenhancers/CO2/
- [x] Colonne ENERGY requise par carbon_cost_RTE (via oka_constants.ENERGY)
- [x] Enhancer EAR (ear_from_db.py ou ear_from_eacct.py) non exécuté en amont
- [x] Ordre d'exécution des enhancers non documenté pour ce client
- [x] Dépendances externes : pymysql (EAR from DB) ou eacct CLI (EAR from eacct)

## Preuves observées
- Fichier source : ./oka_dataenhancers/CO2/carbon_cost_RTE.py
- L'enhancer lit `oka_constants.ENERGY` et calcule `elec_kwh = energy / JOULES_PER_KWH`
- Si ENERGY absente, le calcul de CARBON_FOOTPRINT ne peut pas s'effectuer

## Impact client
Les dashboards CO2 sont vides. Le client ne peut pas suivre son empreinte
carbone malgré des jobs en cours.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : colonne ENERGY absente (enchaînement d'enchancers incorrect)
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Activer l'enhancer de mesure d'énergie avant carbon_cost_RTE,
  et vérifier l'ordre d'exécution.

**Ingénieur** : Support N2 | **Date** : 2026-10-14
