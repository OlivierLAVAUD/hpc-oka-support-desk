# Runbook — Procédures par famille de ticket

Ce runbook détaille les étapes numérotées pour chaque famille de ticket,
avec les commandes et fichiers de référence.

---

## Famille : configuration (ex: TICKET-001)

**Objectif** : Configurer une règle ou un enhancer selon les paramètres du client.

### Étapes
1. Lire le `request.md` pour identifier le compte, le quota et les seuils
2. S'inspirer du fichier source correspondant dans `oka_healthchecks/` ou `oka_dataenhancers/`
3. Adapter les `params_model` avec les valeurs du client (tous les champs ont des `default`)
4. Vérifier le pattern CRITICAL avant HIGH dans `_resolve_alert_level`
5. Vérifier `_no_data_alert` pour l'absence de données
6. Publier la règle sur le workload OKA
7. Rédiger `qualification.md`, `diagnosis.md`, `resolution/*.py`, `response.md`, `lessons.md`

### Commandes
```bash
uv run python tools/diagnostic_helper.py --family configuration --component resources
OKA_LLM=ollama uv run python tools/rule_generator.py "Alerter si le quota dépasse 80 %" --llm
make contracts     # Vérifier les contrats llms.txt et les liens d'exemples
make llm-check     # Vérifier Ollama et le modèle Qwen, si le mode LLM est utilisé
make test          # Vérifier les contrats
make lint          # Vérifier la qualité du code
```

---

## Famille : rule-not-firing (ex: TICKET-002)

**Objectif** : Comprendre pourquoi une règle ne lève aucune alerte.

### Étapes
1. Vérifier que la règle est publiée sur le workload
2. Vérifier le nombre de jobs scannés vs `min_jobs` (guard silencieux)
3. Vérifier `ResultStatus == OK` du provider
4. Si `min_jobs` non atteint : réduire le seuil ou agréger sur une période plus longue
5. Remonter à la R&D : alerte OK explicite quand `min_jobs` n'est pas atteint

### Commandes
```bash
uv run python tools/diagnostic_helper.py --family rule-not-firing --component jobs
```

---

## Famille : false-positives (ex: TICKET-003)

**Objectif** : Réduire le bruit d'alerte par recalibrage des seuils.

### Étapes
1. Analyser l'historique des coûts/métriques du client
2. Recalibrer `cost_high` / `cost_critical` (ou autres seuils)
3. Ajouter un garde-fou `min_jobs` pour lisser les pics ponctuels
4. Vérifier CRITICAL avant HIGH dans `_resolve_alert_level`
5. Tester sur une période représentative avant activation

### Commandes
```bash
uv run python tools/diagnostic_helper.py --family false-positives --component kpi
```

---

## Famille : custom-enhancer (ex: TICKET-004)

**Objectif** : Développer un Data Enhancer sur mesure.

### Étapes
1. S'inspirer de `oka_dataenhancers/costs/costs_demo.py`
2. Définir un `params_model` Pydantic avec valeurs `default`
3. Implémenter `run(self, data, **kwargs) -> pd.DataFrame`
4. Utiliser la colonne réservée `Cost` (pas de préfixe `Cust_`)
5. Utiliser `re.compile()` + `str.match()` pour les patterns de compte
6. Tester sur un DataFrame d'exemple

### Commandes
```bash
uv run python tools/diagnostic_helper.py --family custom-enhancer --component costs
```

---

## Famille : missing-data (ex: TICKET-005)

**Objectif** : Résoudre des données manquantes dans un dashboard.

### Étapes
1. Identifier la colonne manquante (ex: `ENERGY` pour CO2)
2. Vérifier si l'enhancer producteur a été exécuté en amont
3. Vérifier l'ordre d'exécution des enhancers
4. Installer les dépendances externes si besoin (pymysql, requests, entsoe-py)
5. Documenter l'ordre d'exécution dans le runbook client

### Commandes
```bash
uv run python tools/diagnostic_helper.py --family missing-data --component CO2
```

---

## Famille : notification (ex: TICKET-006)

**Objectif** : Résoudre un problème de délivrance d'alerte via webhook.

### Étapes
1. Vérifier `GET /health` du bridge (retour `{"status": "ok"}`)
2. Vérifier l'alignement du token Bearer entre OKA et le bridge
3. Vérifier les routes `POST /notify` et `GET /notify`
4. Consulter `journalctl -u <bridge>-bridge -f` pour les 401
5. Vérifier le payload OKA : `{"subject": "...", "body": "..."}`

### Commandes
```bash
curl -X POST http://localhost:5052/notify \
  -H "Authorization: Bearer <token>" \
  -d '{"subject":"Test","body":"Test body"}'
journalctl -u oka-slack-bridge -f
```

---

## Famille : remote-visualization (ex: TICKET-008)

**Objectif** : Rétablir un portail de visualisation distante 2D/3D (Linux/Windows).

### Étapes
1. Vérifier DNS, TLS, health check ALB et accès au port 443
2. Vérifier le service TurboVNC et le port noVNC en local
3. Exécuter `vglrun glxinfo -B` : le renderer doit être la GPU, pas `llvmpipe`
4. Vérifier les en-têtes WebSocket Nginx (`Upgrade`, `Connection`)
5. Aligner le timeout ALB (≥ 300 s) avec les timeouts Nginx
6. Tester une session 3D depuis Linux et Windows, puis une session inactive
7. Vérifier branding, groupes SSO et plages IP autorisées

### Commandes
```bash
uv run python tools/diagnostic_helper.py --family remote-visualization \
  --component "Portail & Visualisation"
bash tickets/TICKET-008-visualization-portal/resolution/check_remote_viz.sh
```

Côté Windows :
```powershell
.\tickets\TICKET-008-visualization-portal\resolution\Test-RemoteViz.ps1
```

---

## Famille : ccme (ex: déploiement ou mise à jour CCME)

**Objectif** : Déployer, mettre à jour ou diagnostiquer CCME avec OKA.

### Étapes
1. Vérifier la version CCME, la matrice de compatibilité OKA et la licence
2. Contrôler les prérequis Linux/Windows, comptes de service et permissions
3. Vérifier SSO/LDAP/OIDC, TLS et reverse proxy
4. Sauvegarder la base et préparer le rollback avant toute migration
5. Valider les tests de fumée et la connectivité OKA/CCME
6. Consigner les preuves et remonter les irritants à la R&D

### Commande
```bash
uv run python tools/diagnostic_helper.py --family ccme --component CCME
```

Voir `docs/ccme_deployment_checklist.md`.

---

## Famille : training (ex: TICKET-007)

**Objectif** : Construire un parcours de formation.

### Étapes
1. Évaluer le nombre d'utilisateurs et leurs niveaux
2. Définir les besoins métiers (dashboards, rapports, alertes)
3. Construire un parcours en 3 modules progressifs
4. S'appuyer sur les 3 dépôts sources pour le contenu
5. Planifier des sessions en petits groupes avec ateliers pratiques

### Commandes
```bash
uv run python tools/training_generator.py --users 150 --level "débutant à intermédiaire"
```

