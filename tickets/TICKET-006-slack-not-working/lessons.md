# Leçons — TICKET-006

## Leçon tirée
Un mismatch de token Bearer entre OKA et le bridge bloque silencieusement les
alertes. Le middleware retourne 401, mais sans vérification des logs du bridge,
le client n'a aucune visibilité. Il faut systématiquement ajouter une vérification
de token dans le diagnostic des problèmes de notification.

## Recommandation pour le client
Documenter la procédure d'alignement des tokens Bearer entre OKA et chaque bridge.
Surveiller les logs du bridge en cas de silence des alertes.

## Guide client proposé
1. Dans OKA → Notifications → Webhook channels, noter le token Bearer
2. Dans le fichier `.env` du bridge, définir `BRIDGE_BEARER_TOKEN` avec la même valeur
3. Redémarrer le service systemd
4. Tester avec un curl sur POST /notify
5. Vérifier `journalctl -u <bridge>-bridge -f` en cas de problème

## Irritant produit à remonter à la R&D
Le bridge ne renvoie pas d'erreur explicite au client quand le token mismatch.
Une alerte OK ou une notification de "webhook non délivré" serait utile.

## Capitalisation
- [x] Ajouté à `docs/known_issues.md` : "token Bearer différent OKA vs bridge"
- [x] Proposition d'automatisation : vérification de token dans diagnostic_helper.py
- [x] Intégré au parcours de formation (Module 3 — Alertes et HealthCheck)

**Ingénieur** : Support N2 | **Date** : 2026-10-16
