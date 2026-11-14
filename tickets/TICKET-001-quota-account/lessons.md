# Leçons — TICKET-001

## Leçon tirée
La règle de quota existe déjà dans le dépôt oka_healthchecks ; le rôle du support
est de l'adapter aux paramètres du client (nom du compte, quota, seuils) plutôt
que de développer une règle neuf. Il faut systématiquement remplacer le default
placeholder "project_x" par le nom de compte réel.

## Recommandation pour le client
Documenter la démarche de configuration : identifier le compte cible, choisir le
quota, définir les seuils HIGH/CRITICAL, publier la règle via l'UI OKA.

## Guide client proposé
1. Ouvrir l'UI OKA → HealthCheck → + Nouvelle règle
2. Coller le code de cores_account_quota_rule.py
3. Modifier `account` par le nom de votre compte
4. Ajuster `quota_core_hours`, `warn_pct`, `critical_pct`
5. Enregistrer et activer sur votre workload

## Irritant produit à remonter à la R&D
Aucun — la règle existe et fonctionne correctement.

## Capitalisation
- [x] Pas d'ajout à known_issues.md (pas de problème récurrent)
- [x] Proposition d'automatisation : template de publication de règle de quota
- [x] Intégré au parcours de formation (Module 3 — Alertes et HealthCheck)

**Ingénieur** : Support N1 | **Date** : 2026-10-11
