# Réponse client — TICKET-005

## Destinataire
Sophie Bernard — Centre de Calcul

## Objet
Dashboards CO2 vides — diagnostic et résolution

## Corps du message

Bonjour Sophie,

Nous faisons suite à votre demande concernant les dashboards CO2 vides sur votre
cluster, malgré des jobs en cours.

### Cause identifiée
L'enhancer `carbon_cost_RTE.py` a besoin de la colonne `ENERGY` (consommation
énergétique mesurée en joules) pour calculer l'empreinte carbone. Cette colonne
est produite par un enhancer de mesure d'énergie (`ear_from_db.py` ou
`ear_from_eacct.py`) qui n'était pas exécuté en amont dans votre chaîne
d'exécution.

### Solution apportée
Nous avons activé l'enhancer de mesure d'énergie avant `carbon_cost_RTE` dans
votre pipeline d'enhancers, et vérifié l'ordre d'exécution :
1. `ear_from_db.py` (ou `ear_from_eacct.py`) — ajoute les colonnes ENERGY, POWER,
   MINPOWER, MAXPOWER
2. `carbon_cost_RTE.py` — calcule CARBON_FOOTPRINT et elec_cost_eur à partir de ENERGY

### Preuve de résolution
Après réexécution avec le bon ordre d'enhancers, les dashboards CO2 affichent
désormais l'empreinte carbone (kgCO2eq) et le coût électricité (€) par job.

### Prévention
Documenter l'ordre d'exécution des enhancers dans votre runbook. Toujours
vérifier la présence des colonnes d'entrée avant d'exécuter un enhancer
qui en dépend.

### Disponibilité
Notre équipe support reste à votre disposition pour toute question complémentaire.

Cordialement,
L'équipe support UCit
