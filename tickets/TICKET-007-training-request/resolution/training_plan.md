# Résolution — TICKET-007

## Problème
Le client souhaite former 150 utilisateurs (chercheurs et doctorants) à la
plateforme OKA, sans parcours structuré existant.

## Solution proposée
Parcours progressif en 3 modules de 4 heures, construit à partir des dépôts
d'extensibilité d'OKA.

### Module 1 — Bases et dashboards (4 h)
- Architecture OKA et vocabulaire (workload, job, partition, provider)
- Navigation dans les dashboards de cluster
- Lecture des métriques de charge (CPU, GPU, mémoire)
- États de jobs : COMPLETED, FAILED, TIMEOUT, OUT_OF_MEMORY

### Module 2 — Rapports et chargeback (4 h)
- Data Enhancers : enrichissement des jobs (coût, énergie, CO2)
- Colonnes réservées `Cost`, `Power`, `Energy`, `CO2` et préfixe `Cust_`
- Construction d'un rapport de consommation par compte ou département
- Interprétation des résultats et limites des modèles

### Module 3 — Alertes et HealthCheck (4 h)
- Niveaux d'alerte : OK < LOW < MEDIUM < HIGH < CRITICAL
- Contrat `HealthcheckRule` : `params_model`, `evaluate`, `_no_data_alert`
- Configuration des notifications (bridges Slack, Jira, SES, Reporting)
- Diagnostic d'une règle silencieuse (`min_jobs`, `ResultStatus`, token Bearer)

## Organisation
- Sessions de 3 h en petits groupes (15 à 20 participants)
- 1 h d'atelier pratique par module sur une instance de démonstration
- Support de cours, exercices et corrigés fournis
- Évaluation à chaud et questionnaire à froid (2 semaines)

## Preuve de résolution
Programme validé avec la cliente, planning proposé sur 3 semaines, supports
préparés à partir des fichiers réels des trois dépôts.

## Prévention
Réutiliser ce plan comme offre de formation standardisée pour les nouveaux
clients, avec adaptation du niveau et des besoins métiers.
