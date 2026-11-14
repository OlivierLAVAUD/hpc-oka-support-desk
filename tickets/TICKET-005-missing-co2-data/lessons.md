# Leçons — TICKET-005

## Leçon tirée
Les enhancers OKA ont des dépendances entre eux : carbon_cost_RTE nécessite la
colonne ENERGY produite par un enhancer EAR en amont. L'ordre d'exécution des
enhancers est critique et doit être documenté.

## Recommandation pour le client
Documenter l'ordre d'exécution des enhancers dans le runbook. Toujours vérifier
la présence des colonnes requises avant d'exécuter un enhancer dépendant.

## Guide client proposé
1. Dans l'UI OKA → Data Enhancer → Configuration du pipeline
2. Ajouter ear_from_db.py (ou ear_from_eacct.py) en premier
3. Ajouter carbon_cost_RTE.py en second
4. Vérifier que la colonne ENERGY apparaît avant d'exécuter le calcul CO2

## Irritant produit à remonter à la R&D
Le SDK ne vérifie pas automatiquement l'ordre d'exécution ni la présence des
colonnes requises. Une validation des dépendances entre enhancers serait utile.

## Capitalisation
- [x] Ajouté à `docs/known_issues.md` : "ENERGY absent avant carbon_cost_Rte"
- [x] Proposition d'automatisation : validateur d'ordre d'exécution des enhancers
- [x] Intégré au parcours de formation (Module 2 — Rapports et chargeback)

**Ingénieur** : Support N2 | **Date** : 2026-10-15
