# Qualification — TICKET-003

## Client
- **Nom** : Marie Leroy
- **Organisation** : Entreprise Industrielle

## Demande
Trop d'alertes high_cost_rule, devenues du bruit. Les seuils par défaut ne
conviennent pas à un client à coûts stables.

## Composant OKA concerné
- **Famille** : false-positives
- **Composant** : HealthCheck
- **Domaine** : kpi

## Sévérité proposée
- **Niveau** : medium
- **Confiance IA** : 85%

## Qualification validée par l'ingénieur
- [x] Famille confirmée : false-positives (seuils mal calibrés)
- [x] Composant confirmé : HealthCheck, domaine kpi
- [x] Sévérité confirmée : medium (bruit d'alerte, pas d'incident de production)
- [ ] Commentaire : Calibration des seuils cost_high / cost_critical nécessaire,
  éventuellement ajout d'un min_jobs pour lisser les pics ponctuels.

**Ingénieur** : Support N1 | **Date** : 2026-10-12
