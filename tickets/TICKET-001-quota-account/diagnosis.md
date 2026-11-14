# Diagnostic — TICKET-001

## Cause racine
Aucune règle de quota n'est configurée pour le compte "fusion-plasma". Le client
doit publier une règle cores_account_quota_rule.py avec les paramètres
account="fusion-plasma", quota_core_hours=10000, warn_pct=0.80, critical_pct=0.90.

## Checklist de vérifications
- [x] Règle cores_account_quota_rule.py existe dans oka_healthchecks/resources/
- [x] Contrat HealthcheckRule respecté (params_model, evaluate, _no_data_alert)
- [x] Pattern CRITICAL avant HIGH dans _resolve_alert_level
- [x] Tous les champs params ont une valeur par défaut
- [x] Le compte cible est identifiable via grouping_size suffisant

## Preuves observées
- Fichier source : ./oka_healthchecks/resources/cores_account_quota_rule.py
- Params par défaut : account="project_x", quota_core_hours=10000, warn_pct=0.80, critical_pct=0.90
- Le default "project_x" doit être remplacé par "fusion-plasma"

## Impact client
Aucune alerte de quota n'est levée pour "fusion-plasma" actuellement. Le client
ne peut pas anticiper l'épuisement de son quota de 10 000 core-hours.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : règle non configurée
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Adaptation simple des paramètres, pas de développement neuf.

**Ingénieur** : Support N1 | **Date** : 2026-10-10
