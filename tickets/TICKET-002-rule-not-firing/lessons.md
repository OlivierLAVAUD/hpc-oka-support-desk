# Leçons — TICKET-002

## Leçon tirée
Un retour `[]` silencieux quand `min_jobs` n'est pas atteint est trompeur pour
le client : il croit que tout va bien alors que la règle n'a tout simplement pas
assez de données. Il vaut mieux retourner une alerte `AlertLevel.OK` expliquant
que l'échantillon est insuffisant.

## Recommandation pour le client
Sur les petits workloads, réduire `min_jobs` ou agréger sur une période plus longue. Toujours vérifier le nombre de jobs scannés avant de conclure à une absence de problème.

## Guide client proposé
1. Dans l'UI OKA, ouvrir la règle failed_jobs_rule
2. Ajuster `min_jobs` à une valeur adaptée à la taille du workload
3. Vérifier que des alertes OK "insufficient sample" apparaissent quand pertinent

## Irritant produit à remonter à la R&D
Le pattern `_no_data_alert` couvre l'échec du provider, mais pas le cas où le
provider renvoie des données valides mais insuffisantes. Une alerte OK
explicite devrait être émise par le SDK quand `min_jobs` n'est pas atteint.

## Capitalisation
- [x] Ajouté à `docs/known_issues.md` : "min_jobs silencieux"
- [x] Proposition d'automatisation : vérifier min_jobs dans le diagnostic_helper
- [x] Intégré au parcours de formation (Module 3 — Alertes et HealthCheck)

**Ingénieur** : Support N2 | **Date** : 2026-10-12
