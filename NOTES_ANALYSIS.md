# NOTES_ANALYSIS — Extraction des dépôts sources

Ce fichier prouve que le POC `oka-support-desk` s'appuie sur les trois dépôts
clonés de UCit. Toute résolution de ticket, tout outil et tout template est
conçu pour respecter les contrats et patterns extraits ci-dessous.

---

## 1. Dépôt `./oka_healthchecks` (68 règles HealthCheck, 9 domaines)

### Fichiers lus (extract complet)

| Fichier | Rôle |
|---------|------|
| `./oka_healthchecks/resources/cores_account_quota_rule.py` | Règle de quota compte (TICKET-001) |
| `./oka_healthchecks/jobs/failed_jobs_rule.py` | Règle de taux d'échec (TICKET-002) |
| `./oka_healthchecks/kpi/high_cost_rule.py` | Règle de coût KPI (TICKET-003) |
| `./oka_healthchecks/load/core_load_rule.py` | Règle de charge CPU (référence pattern) |
| `./oka_healthchecks/compatibility.json` | Version OKA 3.3.0, commit a04794b |

### Contrat `HealthcheckRule` extrait

- Chaque règle est une sous-classe de `HealthcheckRule[Params]`
- `params_model` : attribut de classe obligatoire, doit être une sous-classe de
  `pydantic.BaseModel`. Vérifié par `__init_subclass__` au moment de la définition
  de la classe (lève `TypeError` si absent ou non-BaseModel)
- `evaluate(self) -> list[Alert]` : méthode obligatoire, retourne une liste
  d'`Alert` (jamais `None`). Liste vide = aucune alerte
- `Alert` : modèle Pydantic figé avec `level` (AlertLevel), `title`, `description`,
  `reason`, `metadata`
- `AlertLevel` : `OK < LOW < MEDIUM < HIGH < CRITICAL`

### Patterns extraits (réutilisés dans le POC)

1. **`_no_data_alert`** : quand le provider renvoie un statut != `ResultStatus.OK`
   ou des données vides, retourner une alerte `AlertLevel.OK` intitulée
   `"No data - <nom>"` plutôt qu'une liste vide
2. **CRITICAL avant HIGH** : dans `_resolve_alert_level`, vérifier d'abord le
   seuil le plus sévère pour éviter une mauvaise classification
3. **`min_jobs` guard** : ne pas déclencher d'alerte si l'échantillon est trop
   petit (ex: `< 10` jobs) pour éviter les faux positifs statistiques
4. **`frozenset` pour les états** : `_FAILED_STATES = frozenset({"FAILED",
   "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"})`
5. **Providers** : `self.jobs`, `self.cluster_load`, `self.kpi`, `self.state`,
   `self.cores`, `self.congestion`, `self.waiting_time`, etc.
6. **Champs params** : chaque champ de `params_model` doit avoir une valeur `default`
   (règle exécutable sans configuration utilisateur)

---

## 2. Dépôt `./oka_dataenhancers` (8 Data Enhancers, 5 catégories)

### Fichiers lus (extract complet)

| Fichier | Rôle |
|---------|------|
| `./oka_dataenhancers/costs/costs_demo.py` | Enhancer de coût (TICKET-004) |
| `./oka_dataenhancers/CO2/carbon_cost_RTE.py` | Enhancer CO2 (TICKET-005) |
| `./oka_dataenhancers/misc/capitalize_user.py` | Enhancer de normalisation (référence) |
| `./oka_dataenhancers/llms.txt` | Contrat DataEnhancer |

### Contrat `DataEnhancer` extrait

- Chaque enhancer est une sous-classe de `DataEnhancer[Params]`
- `params_model` : attribut de classe obligatoire (Pydantic `BaseModel`)
- `run(self, data, **kwargs) -> pd.DataFrame` : modifie le DataFrame in place
- `self.params` : instance validée de `params_model`
- `self.logger` : logger namespacé à `data_enhancers.<ClassName>`

### Patterns extraits

1. **Préfixe `Cust_`** : toute colonne ajoutée dont le nom n'est pas réservé reçoit
   automatiquement le préfixe `Cust_` dans OKA (ex: `feature1` → `Cust_feature1`)
2. **Noms réservés** : `Cost`, `Power`, `Energy`, `CO2` (écrits sans préfixe,
   signification spéciale dans OKA)
3. **Pattern regex de compte** : `DISC_ACCOUNT: str = Field(default=r"contract_fusion_.*")`
   utilisé avec `re.compile()` et `str.match()`
4. **Colonnes du DataFrame** : `JobID`, `Account`, `Core_hours`, `Cost`, `Power`,
   `Energy`, `CO2`, `Cluster`, `End`, `JobName`, `Partition`, `QOS`, `Start`,
   `State`, `Submit`, `Timelimit`, `UID`
5. **Dépendances externes** : `pymysql` (EAR from DB), `requests` + `entsoe-py` (CO2),
   `pandas` (tous les enhancers)

---

## 3. Dépôt `./oka_webhooks` (4 bridges webhook : SES, Slack, Jira, Reporting)

### Fichiers lus (extract complet)

| Fichier | Rôle |
|---------|------|
| `./oka_webhooks/oka-slack-bridge/app.py` | Bridge Slack (TICKET-006) |
| `./oka_webhooks/oka-slack-bridge/.service` | Service systemd (référence) |
| `./oka_webhooks/llms.txt` | Contrat de payload webhook OKA |

### Contrat de payload OKA extrait

- POST JSON : `{"subject": "<alert title>", "body": "<alert body>"}`
- GET query : `?subject=...&body=...`
- Les deux méthodes doivent être supportées sur `/notify`
- Header optionnel : `Authorization: Bearer <token>`
- Le token est configuré dans OKA (canal webhook) et doit être validé par le bridge
  (retour 401 en cas de mismatch)

### Patterns extraits

1. **Routes** : `GET /health` (liveness, retourne `{"status": "ok"}`),
   `POST /notify` (webhook principal), `GET /notify` (fallback GET)
2. **Auth Bearer** : variable `BRIDGE_BEARER_TOKEN`, middleware `_check_auth()`
3. **Logging namespacé** : `logging.getLogger("oka-<nom>-bridge")`
4. **Déploiement** : systemd `.service` avec `gunicorn`, utilisateur `oka-bridge`,
   `EnvironmentFile=/opt/<bridge>/.env`
5. **Framework** : Flask, Python 3.13+, gestionnaire de paquets `uv`
6. **Bridges** : AWS SES (port 5050), Slack (port 5052), Jira (port 5053), Reporting (port 5054)

---

## Conclusion

Le POC `oka-support-desk` respecte scrupuleusement :
- Le contrat `HealthcheckRule` (params_model Pydantic, evaluate, _no_data_alert,
  CRITICAL avant HIGH, min_jobs)
- Le contrat `DataEnhancer` (params_model Pydantic, run, préfixe Cust_, noms réservés)
- Le contrat webhook OKA (payload {subject, body}, auth Bearer, routes /notify)
- La licence Apache 2.0 © 2026 UCit
