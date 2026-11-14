# Leçons — TICKET-003

## Leçon tirée
Les seuils par défaut des règles OKA sont des points de départ, pas des valeurs
optimales pour tous les clients. Un recalibrage selon l'historique du client est
souvent nécessaire. L'ajout d'un garde-fou min_jobs permet de lisser les pics
ponctuels sans masquer les vrais problèmes.

## Recommandation pour le client
Proposer un guide de calibration des seuils dans la formation : analyser
l'historique des coûts, définir des seuils HIGH/CRITICAL adaptés, tester sur
une période représentative avant mise en production.

## Guide client proposé
1. Exporter l'historique des coûts depuis OKA (30 jours minimum)
2. Calculer le coût moyen et l'écart-type
3. Définir HIGH à moyenne + 1 écart-type, CRITICAL à moyenne + 2 écarts-types
4. Tester en mode "dry run" avant activation

## Irritant produit à remonter à la R&D
Aucun — le recalibrage est une opération de support standard.

## Capitalisation
- [ ] Pas d'ajout à known_issues.md
- [x] Proposition d'automatisation : assistant de calibration des seuils basé sur l'historique
- [x] Intégré au parcours de formation (Module 3 — Alertes et HealthCheck)

**Ingénieur** : Support N1 | **Date** : 2026-10-13
