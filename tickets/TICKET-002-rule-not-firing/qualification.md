# Qualification — TICKET-002

## Client
- **Nom** : Jean Dupont
- **Organisation** : Labo Example

## Demande
La règle failed_jobs_rule publiée mais aucune alerte n'est levée, alors que
nous savons que des jobs échouent sur le cluster.

## Composant OKA concerné
- **Famille** : rule-not-firing
- **Composant** : HealthCheck
- **Domaine** : jobs

## Sévérité proposée
- **Niveau** : high
- **Confiance IA** : 90%

## Qualification validée par l'ingénieur
- [x] Famille confirmée : rule-not-firing (règle présente mais silencieuse)
- [x] Composant confirmé : HealthCheck, domaine jobs
- [x] Sévérité confirmée : high (risque de ne pas détecter des échecs de jobs)
- [ ] Commentaire : Hypothèse principale — le workload contient trop peu de jobs
  pour dépasser le seuil min_jobs par défaut (10).

**Ingénieur** : Support N2 | **Date** : 2026-10-11
