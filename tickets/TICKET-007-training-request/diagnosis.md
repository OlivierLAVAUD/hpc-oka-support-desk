# Diagnostic — TICKET-007

## Cause racine
Le client n'a pas encore de parcours de formation structuré pour ses 150
utilisateurs. Un programme progressif en 3 modules est nécessaire pour couvrir
les besoins des chercheurs et doctorants.

## Checklist de vérifications
- [x] Nombre d'utilisateurs : 150 (chercheurs et doctorants)
- [x] Niveaux : débutants à intermédiaires
- [x] Besoins : dashboards, rapports, alertes HealthCheck
- [x] Contenu disponible dans les 3 dépôts (oka_healthchecks, oka_dataenhancers, oka_webhooks)

## Preuves observées
- oka_healthchecks : 40 règles pour construire le module 3 (alertes)
- oka_dataenhancers : 7 enhancers pour le module 2 (rapports, chargeback)
- oka_webhooks : 4 bridges pour le module 3 (notifications)

## Impact client
Sans formation, les utilisateurs ne pourront pas exploiter pleinement OKA.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : absence de parcours de formation structuré
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Parcours en 3 modules progressifs proposé.

**Ingénieur** : Support N1 | **Date** : 2026-10-16
