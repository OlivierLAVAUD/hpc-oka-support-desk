# Qualification — TICKET-001

## Client
- **Nom** : Ahmed Benali
- **Organisation** : Institut de Recherche

## Demande
Alertes de consommation de core-hours pour le compte "fusion-plasma" :
- HIGH à 80 % d'un quota de 10 000 core-hours
- CRITICAL à 90 % du même quota

## Composant OKA concerné
- **Famille** : configuration
- **Composant** : HealthCheck
- **Domaine** : resources

## Sévérité proposée
- **Niveau** : medium
- **Confiance IA** : 95%

## Qualification validée par l'ingénieur
- [x] Famille confirmée : configuration d'une règle de quota existante
- [x] Composant confirmé : HealthCheck, domaine resources
- [x] Sévérité confirmée : medium (pas d'incident en cours, demande de configuration)
- [ ] Commentaire : Règle cores_account_quota_rule.py déjà disponible dans le dépôt oka_healthchecks, il suffit de l'adapter avec les paramètres du client.

**Ingénieur** : Support N1 | **Date** : 2026-10-10
