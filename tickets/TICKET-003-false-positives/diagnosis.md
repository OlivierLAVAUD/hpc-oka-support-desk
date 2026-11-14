# Diagnostic — TICKET-003

## Cause racine
Les seuils par défaut de high_cost_rule (cost_high=10 000, cost_critical=50 000)
sont trop bas pour la volumétrie du client. Chaque dépassement génère une alerte,
créant du bruit. De plus, aucun garde-fou min_jobs n'est présent pour lisser les
pics ponctuels.

## Checklist de vérifications
- [x] Règle high_cost_rule.py publiée sur le workload
- [x] Seuils par défaut : cost_high=10 000, cost_critical=50 000
- [x] Coûts du client : stables, autour de 8 000–12 000 par période
- [x] Pas de garde-fou min_jobs dans la règle actuelle
- [x] Pattern CRITICAL avant HIGH respecté dans _resolve_alert_level

## Preuves observées
- Fichier source : ./oka_healthchecks/kpi/high_cost_rule.py
- Code : `if total_cost >= self.params.cost_critical: ... elif total_cost >= self.params.cost_high: ...`
- Aucun paramètre min_jobs dans la classe Params

## Impact client
Alertes fréquentes non pertinentes (bruit), risque de désensibilisation du client
aux alertes réelles.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : seuils trop bas + pas de min_jobs guard
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Recalibrer cost_high et cost_critical selon l'historique du
  client, et ajouter un min_jobs pour lisser.

**Ingénieur** : Support N1 | **Date** : 2026-10-12
