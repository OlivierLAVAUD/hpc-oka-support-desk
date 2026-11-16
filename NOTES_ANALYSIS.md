# NOTES_ANALYSIS — Extraction des dépôts sources

Ce fichier prouve que le POC `oka-support-desk` s'appuie sur les trois dépôts
clonés de UCit. Toute résolution de ticket, tout outil et tout template est
conçu pour respecter les contrats et patterns extraits ci-dessous.

---

## 1. Dépôt `../oka_healthchecks` (68 règles HealthCheck, 9 domaines)

### Fichiers lus (extract complet)

| Fichier | Rôle |
|---------|------|
| `../oka_healthchecks/resources/cores_account_quota_rule.py` | Règle de quota compte (TICKET-001) |
| `../oka_healthchecks/jobs/failed_jobs_rule.py` | Règle de taux d'échec (TICKET-002) |
| `../oka_healthchecks/kpi/high_cost_rule.py` | Règle de coût KPI (TICKET-003) |
| `../oka_healthchecks/load/core_load_rule.py` | Règle de charge CPU (référence pattern) |
| `../oka_healthchecks/compatibility.json` | Version OKA 3.3.0, commit a04794b |

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
   `"No data - <nom>"` plutôt qu'une liste vide. Présent dans **64 des 68
   règles** ; les 4 règles `jobs/` ne l'utilisent pas, c'est donc une convention
   forte mais pas une obligation du SDK.
2. **CRITICAL avant HIGH** : dans `_resolve_alert_level`, vérifier d'abord le
   seuil le plus sévère pour éviter une mauvaise classification. Vérifié dans
   les **55 règles** qui implémentent cette méthode.
3. **`min_jobs` guard** : ne pas déclencher d'alerte si l'échantillon est trop
   petit (ex: `< 10` jobs) pour éviter les faux positifs statistiques. Présent
   dans **24 règles**.
4. **`frozenset` pour les états** : `_FAILED_STATES = frozenset({"FAILED",
   "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"})`
   (`jobs/failed_jobs_rule.py`) et `_FAILURE_STATES` à base de `JobState`
   (`state/job_failure_rate_rule.py`).
5. **Providers** : `self.jobs`, `self.cluster_load`, `self.kpi`, `self.state`,
   `self.cores`, `self.congestion`, `self.slowdown`, `self.consumers`,
   `self.concurrent_users`, etc.
6. **Champs params** : chaque champ de `params_model` a une valeur `default`
   dans les 68 règles healthcheck, ce qui permet de les exécuter sans
   configuration utilisateur.

---

## 2. Dépôt `../oka_dataenhancers` (8 Data Enhancers, 5 catégories)

### Fichiers lus (extract complet)

| Fichier | Rôle |
|---------|------|
| `../oka_dataenhancers/costs/costs_demo.py` | Enhancer de coût (TICKET-004) |
| `../oka_dataenhancers/CO2/carbon_cost_RTE.py` | Enhancer CO2 (TICKET-005) |
| `../oka_dataenhancers/misc/capitalize_user.py` | Enhancer de normalisation (référence) |
| `../oka_dataenhancers/llms.txt` | Contrat DataEnhancer |

### Contrat `DataEnhancer` extrait

- Chaque enhancer est une sous-classe de `DataEnhancer[Params]`
- `params_model` : attribut de classe obligatoire (Pydantic `BaseModel`)
- `run(self, data, **kwargs) -> pd.DataFrame` : modifie le DataFrame in place
- `self.params` : instance validée de `params_model`
- `self.logger` : logger namespacé à `data_enhancers.<ClassName>`

Nuance : `llms.txt` recommande une valeur `default` pour chaque champ, et c'est
le cas partout sauf `EAR/ear_from_db.py`, où `user` et `password` sont requis
(seuls 2 champs sans défaut sur les 8 enhancers).

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

## 3. Dépôt `../oka_webhooks` (4 bridges webhook : SES, Slack, Jira, Reporting)

### Fichiers lus (extract complet)

| Fichier | Rôle |
|---------|------|
| `../oka_webhooks/oka-slack-bridge/app.py` | Bridge Slack (TICKET-006) |
| `../oka_webhooks/oka-slack-bridge/oka-slack-bridge.service` | Service systemd (référence) |
| `../oka_webhooks/llms.txt` | Contrat de payload webhook OKA |

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
4. **Déploiement** : systemd `oka-<nom>-bridge.service` avec `gunicorn`,
   utilisateur `oka-bridge`, `EnvironmentFile=/opt/<bridge>/.env`
5. **Framework** : Flask, Python 3.13+, gestionnaire de paquets `uv`
6. **Bridges** : AWS SES (port 5050), Slack (port 5052), Jira (port 5053), Reporting (port 5054)

---

## 4. Générateur de règle (`tools/rule_generator.py`)

Le générateur ne fait pas d'analyse de code : il combine un template figé du
contrat `HealthcheckRule` avec des heuristiques lexicales (domaine, seuils,
nom). En revanche, chaque domaine pointe désormais vers un **provider et une
méthode réellement présents** dans `../oka_healthchecks`, avec la bonne
signature et la bonne extraction de métrique.

| Domaine | Provider / méthode | Source de référence | Métrique |
|---|---|---|---|
| `jobs` | `self.jobs.scan_jobs()` | `jobs/failed_jobs_rule.py` | taux d'échec (0-1) |
| `kpi` | `self.kpi.get_cost_metrics()` | `kpi/high_cost_rule.py` | coût total (absolu) |
| `load` | `self.cluster_load.get_core_load()` | `load/core_load_rule.py` | taux d'utilisation (0-1) |
| `resources` | `self.cores.get_grouped_distribution()` | `resources/cores_account_quota_rule.py` | ratio quota (0-1) |
| `congestion` | `self.congestion.get_congestion_metrics()` | `congestion/congestion_rule.py` | % d'utilisation (0-100) |
| `state` | `self.state.get_jobs_status()` | `state/job_failure_rate_rule.py` | taux d'échec (0-1) |
| `throughput` | `self.slowdown.get_slowdown_stats()` | `throughput/slowdown_high_slowdown.py` | slowdown médian (absolu) |
| `consumers` | `self.consumers.get_group_aggregation()` | `consumers/core_hours_high_group_dominance.py` | part du groupe dominant (0-1) |
| `concurrent_users` | `self.concurrent_users.get_running_and_waiting_users()` | `concurrent_users/peak_concurrent_users.py` | pic d'utilisateurs (absolu) |

Le template gère trois familles de seuils : `ratio` (0-1), `percent` (0-100) et
`absolute` (valeur métier). Les seuils par défaut viennent des règles sources ;
un pourcentage présent dans la demande est converti selon le type. Le code
généré reste un **squelette** : il compile et respecte le contrat de surface,
mais les seuils et la sémantique métier doivent être validés par l'ingénieur
avant publication.

### 4.1 Contrats `llms.txt` et dérives constatées

Les trois dépôts publient aussi un `llms.txt` destiné aux assistants de code :
398 lignes pour `oka_healthchecks`, 87 pour `oka_dataenhancers`, 45 pour
`oka_webhooks`. Ces fichiers ne sont ni importés ni appliqués par OKA : ils
servent de contexte de génération et de point de comparaison.

Le POC les exploite de deux façons :

- `tools/contract_context.py` découpe les sections, extrait les providers
  (`self.<nom>`), les exemples listés et les liens cassés ; `make contracts`
  affiche le rapport ;
- `tests/test_llms_contract.py` vérifie que chaque domaine du générateur pointe
  vers un provider documenté et une méthode réellement présente dans le fichier
  source correspondant.

Dérives relevées dans `../oka_healthchecks/llms.txt` :

- `load/high_core_utilization_rule.py` est listé mais le fichier réel est
  `load/core_load_rule.py` ;
- `scheduler_config/partition_scheduler_limits_rule.py` est listé mais le
  répertoire n'existe pas ;
- les imports du squelette (`applications.healthcheck.core.base`,
  `applications.healthcheck.core.alerts`, `ait.enums`) diffèrent de ceux des
  règles réelles (`applications.healthcheck.core`, `applications.ait.enums`) ;
- `get_group_aggregation` et `get_running_and_waiting_users` ne figurent pas
  dans les signatures « Optional », alors que les règles sources les utilisent.

Conclusion pratique : `llms.txt` est un bon accélérateur et un bon oracle de
revue, mais la vérité reste le SDK, les exemples qui compilent et
`compatibility.json`.

### 4.2 Mode LLM local optionnel

Le générateur peut appeler Ollama (`qwen2.5-coder:7b` par défaut) via
`tools/llm_client.py`, avec `--llm` ou `OKA_LLM=ollama`. Le modèle ne produit
pas de code libre : il retourne un JSON avec domaine, nom, seuils et
justification. Les validateurs vérifient le domaine, l'ordre et les bornes des
seuils, puis le template déterministe génère la règle. Ollama absent ou sortie
invalide → fallback heuristique.

---

## Conclusion

Le POC `oka-support-desk` est fidèle aux sources pour :
- le contrat `HealthcheckRule` (params_model Pydantic, evaluate, `_no_data_alert`
  dans 64/68 règles, CRITICAL avant HIGH dans 55/55 `_resolve_alert_level`,
  `min_jobs`) ;
- le contrat `DataEnhancer` (params_model Pydantic, run, préfixe `Cust_`, noms
  réservés, colonne `Cost` dans `costs_demo.py`) ;
- le contrat webhook OKA (payload `{subject, body}`, auth Bearer, routes
  `/health` et `/notify`) ;
- la licence Apache 2.0 © 2026 UCit.

Le générateur de règle est un template à heuristiques, pas un analyseur de code :
ses provider/méthodes sont alignés sur les 9 domaines sources, mais les seuils
et l'extraction fine des DTO restent à valider au cas par cas.
