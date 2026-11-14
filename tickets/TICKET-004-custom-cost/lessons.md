# Leçons — TICKET-004

## Leçon tirée
Un Data Enhancer personnalisé se construit facilement en s'inspirant de
costs_demo.py. Les points clés : utiliser la colonne réservée "Cost" (sans
préfixe Cust_), définir un params_model Pydantic avec defaults, et utiliser
`re.compile()` + `str.match()` pour les patterns de compte.

## Recommandation pour le client
Fournir un template d'enhancer paramétrable aux clients pour qu'ils puissent
adapter les tarifs eux-mêmes sans intervention du support.

## Guide client proposé
1. Copier le template custom_cost_enhancer.py
2. Modifier les valeurs par défaut dans `CustomCostEnhancerParams`
3. Importer le fichier dans l'UI OKA → Data Enhancer
4. Tester sur un workload représentatif

## Irritant produit à remonter à la R&D
Aucun — le contrat DataEnhancer est clair et bien documenté.

## Capitalisation
- [ ] Pas d'ajout à known_issues.md
- [x] Proposition d'automatisation : générateur d'enhancer de coût via rule_generator.py
- [x] Intégré au parcours de formation (Module 2 — Rapports et chargeback)

**Ingénieur** : Support N2 | **Date** : 2026-10-14
