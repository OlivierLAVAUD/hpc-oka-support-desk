# Known Issues — Problèmes connus

Problèmes récurrents identifiés lors du support, avec symptôme, cause, solution
et prévention.

---

## KI-001 — min_jobs silencieux

| Champ | Valeur |
|-------|--------|
| **Symptôme** | Une règle HealthCheck ne lève aucune alerte malgré des événements |
| **Cause** | Le nombre de jobs est inférieur à `min_jobs` (défaut 10 dans la règle source ; 3 dans l'adaptation TICKET-002), la règle retourne `[]` |
| **Solution** | Réduire `min_jobs` ou agréger sur une période plus longue |
| **Prévention** | Remonter à la R&D une alerte OK explicite quand `min_jobs` n'est pas atteint |
| **Ticket** | TICKET-002 |

---

## KI-002 — ENERGY absent avant carbon_cost_RTE

| Champ | Valeur |
|-------|--------|
| **Symptôme** | Dashboard CO2 vide malgré des jobs en cours |
| **Cause** | La colonne `ENERGY` est absente car l'enhancer EAR n'a pas été exécuté en amont |
| **Solution** | Activer l'enhancer de mesure d'énergie avant `carbon_cost_RTE` |
| **Prévention** | Documenter l'ordre d'exécution des enhancers dans le runbook client |
| **Ticket** | TICKET-005 |

---

## KI-003 — Token Bearer mismatch

| Champ | Valeur |
|-------|--------|
| **Symptôme** | Bridge webhook up (/health OK) mais aucune alerte délivrée |
| **Cause** | `BRIDGE_BEARER_TOKEN` différent entre OKA et le bridge → rejets HTTP 401 |
| **Solution** | Aligner le token côté bridge et côté OKA, redémarrer le service |
| **Prévention** | Vérifier systématiquement l'alignement des tokens lors de la configuration |
| **Ticket** | TICKET-006 |

---

## KI-005 — Rendu 3D en llvmpipe

| Champ | Valeur |
|-------|--------|
| **Symptôme** | Session 3D noire ou bloquée, alors que la 2D fonctionne |
| **Cause** | Le lanceur de session n'utilise pas `vglrun` ; OpenGL bascule sur `llvmpipe` |
| **Solution** | Lancer les applications 3D avec `vglrun` et valider `vglrun glxinfo -B` |
| **Prévention** | Contrôle de pré-flight `check_remote_viz.sh` et alerte si renderer logiciel |
| **Ticket** | TICKET-008 |

---

## KI-006 — WebSocket noVNC coupé par l'ALB

| Champ | Valeur |
|-------|--------|
| **Symptôme** | Déconnexion après environ une minute, code WebSocket 1006 |
| **Cause** | Timeout ALB à 60 s et en-têtes `Upgrade`/`Connection` absents de Nginx |
| **Solution** | Timeout ALB ≥ 300 s et configuration WebSocket Nginx |
| **Prévention** | Test de session inactive et revue de configuration ALB/Nginx |
| **Ticket** | TICKET-008 |

---

## KI-004 — Seuils par défaut non adaptés

| Champ | Valeur |
|-------|--------|
| **Symptôme** | Trop d'alertes (bruit) ou pas assez |
| **Cause** | Seuils par défaut (10 000 / 50 000 pour le coût) non calibrés sur la volumétrie client |
| **Solution** | Recalibrer `cost_high` / `cost_critical` selon l'historique, ajouter `min_jobs` |
| **Prévention** | Guide de calibration des seuils dans la formation |
| **Ticket** | TICKET-003 |

