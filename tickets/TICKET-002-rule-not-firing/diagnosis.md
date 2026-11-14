# Diagnostic — TICKET-002

## Cause racine
Le workload contient seulement 3 jobs sur la période évaluée, alors que le
seuil `min_jobs` par défaut de failed_jobs_rule est fixé à 10. La règle reste
silencieuse (retourne []) car l'échantillon est statistiquement trop petit pour
être fiable.

## Checklist de vérifications
- [x] Règle failed_jobs_rule.py publiée sur le workload
- [x] Nombre de jobs scannés : 3 (inférieur à min_jobs=10)
- [x] États d'échec présents : FAILED, TIMEOUT (dans _FAILED_STATES)
- [x] Règle retourne [] (liste vide) — comportement attendu par le contrat
- [x] Pas d'alerte OK explicite lorsque min_jobs n'est pas atteint

## Preuves observées
- Fichier source : ./oka_healthchecks/jobs/failed_jobs_rule.py
- Param min_jobs par défaut : 10
- Code : `if total < self.params.min_jobs: return []`
- Workload client : 3 jobs sur la période

## Impact client
Des jobs échouent (FAILED, TIMEOUT) mais aucune alerte n'est levée. Le client ne
est pas informé des problèmes sur son cluster.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : min_jobs trop élevé pour ce petit workload
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Recommandation — remonter à la R&D une alerte OK explicite
  quand min_jobs n'est pas atteint, plutôt qu'un retour [] silencieux.

**Ingénieur** : Support N2 | **Date** : 2026-10-11
