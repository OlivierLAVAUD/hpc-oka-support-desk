# oka-support-desk — POC Ingénieur Support UCit

POC d’un poste d’**Ingénieur Support UCit** sur la plateforme **OKA**
(analytique et supervision HPC). Il simule un portefeuille de **8 tickets
clients** traités avec une méthode reproductible, **8 outils IA + HITL** et une
**interface Gradio** pour les manipuler. Il couvre aussi les portails, la
visualisation distante 2D/3D, Linux/Windows, AWS et l’anglais technique écrit.

L’IA prépare, l’ingénieur valide : aucune action n’est appliquée automatiquement
sur une plateforme client.

---

## Sommaire

1. [Contexte](#1-contexte)
2. [Démarrage rapide](#2-démarrage-rapide)
3. [L’interface Gradio](#3-linterface-gradio)
4. [Ce que contient le POC](#4-ce-que-contient-le-poc)
5. [Les 8 tickets](#5-les-8-tickets)
6. [Méthode et approche IA + HITL](#6-méthode-et-approche-ia--hitl)
7. [Ce que cela démontre](#7-ce-que-cela-démontre)
8. [Tests et CI](#8-tests-et-ci)
9. [Limites assumées](#9-limites-assumées)
10. [Références](#10-références)

---

## 1. Contexte

Poste visé : **Ingénieur Support** — UCit (Montpellier)

Produit : **OKA** — plateforme Data Science pour environnements HPC

https://oka.how | https://doc.oka.how

Le POC démontre la capacité à :

- lire et comprendre les dépôts d’extensibilité d’OKA ;
- qualifier, diagnostiquer et résoudre des tickets clients ;
- respecter les contrats `HealthcheckRule`, `DataEnhancer` et webhook ;
- capitaliser via une méthode et des outils réutilisables ;
- garder l’humain dans la boucle à chaque étape.

### Couverture du profil UCit

| Mission du poste | Preuve dans le POC |
|---|---|
| Visualisation distante 2D/3D et portails HPC/IA | `TICKET-008` : runbook TurboVNC/VirtualGL, Nginx, AWS ALB, branding et restriction IP |
| Support CCME et OKA | OKA : tickets 001 à 007 ; CCME : `docs/ccme_deployment_checklist.md` (partiel) |
| Incidents N1/N2, gestion et escalade | 8 tickets, `ticket_classifier`, `diagnostic_helper`, `ticket_prioritizer`, `docs/escalation_matrix.md` |
| Automatisation, formation, R&D et tests | 8 outils, interface Gradio, `TICKET-007`, `rnd_feedback_analyzer`, `tests/` et CI |

La matrice complète, avec les limites honnêtes, est dans
[`docs/profile_alignment.md`](docs/profile_alignment.md).

---

## 2. Démarrage rapide

**Prérequis** : Python 3.11+ et [uv](https://docs.astral.sh/uv/).

```bash
# Installer les dépendances (pydantic, gradio, pytest, ruff)
make install

# Lancer l’interface Gradio
make ui
```

L’interface est disponible sur **http://127.0.0.1:7860**.

Pour l’exposer sur une autre interface réseau :

```bash
GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7860 make ui
```

Autres commandes utiles :

```bash
make lint    # ruff sur les outils, tests, tickets et app.py
make test    # pytest
make demo    # démo CLI rapide de trois outils
```

Le CLI reste disponible comme fallback :

```bash
uv run python interface_cli.py
```

---

## 3. L’interface Gradio

`app.py` expose les 8 outils dans **8 onglets** et affiche systématiquement le
bandeau HITL ainsi que le journal de sortie de l’outil.

| Onglet | Outil exposé | Entrée | Sortie |
|---|---|---|---|
| Accueil & tickets | `ticket_prioritizer.py` + lecteur de tickets | Ticket ou portefeuille complet | Livrables du ticket, tableau de priorisation |
| Profil & preuves | `docs/profile_alignment.md` | — | Matrice missions/preuves et limites |
| 1 · Qualifier | `ticket_classifier.py` | Demande collée ou `request.md` | JSON famille, sévérité, composant, confiance |
| 2 · Diagnostiquer | `diagnostic_helper.py` | Famille + composant | Checklist Markdown de vérifications |
| 3 · Répondre | `response_generator.py` | Contenu d’un `diagnosis.md` | Brouillon de réponse avec bandeau BROUILLON |
| 4 · Générer une règle | `rule_generator.py` | Demande en français, domaine, nom | Code `HealthcheckRule` + checklist des 5 patterns |
| 5 · Former | `training_generator.py` | Nombre d’utilisateurs, niveau, besoins | Parcours en 3 modules |
| 6 · Capitaliser | `automation_identifier.py`, `rnd_feedback_analyzer.py` | `lessons.md` des tickets | Automatisations par ROI, irritants R&D |

### Parcours de démonstration conseillé

1. **Accueil & tickets** → sélectionner `TICKET-001-quota-account` et parcourir ses livrables.
2. **Profil & preuves** → lire la matrice de couverture du poste UCit.
3. **1 · Qualifier** → coller la demande de TICKET-001 ou charger son `request.md`.
4. **2 · Diagnostiquer** → choisir `notification` / `Webhook Bridge` ou `remote-visualization` / `Portail & Visualisation`.
5. **3 · Répondre** → coller le diagnostic de TICKET-006 ou TICKET-008 et générer un brouillon.
6. **4 · Générer une règle** → demander « Alerter si le taux d’échec des jobs dépasse 10 % ».
7. **5 · Former** → générer un parcours pour 150 utilisateurs de niveau intermédiaire.
8. **6 · Capitaliser** → afficher les automatisations et les irritants extraits des `lessons.md`.

L’interface est **locale et sans authentification**. Pour un usage exposé, ajouter
un reverse proxy et un contrôle d’accès.

---

## 4. Ce que contient le POC

```text
oka-support-desk/
├── README.md               # Ce fichier
├── METHOD.md               # Méthode de support en 5 étapes
├── AI_METHOD.md            # Approche IA + HITL
├── NOTES_ANALYSIS.md       # Preuve d’extraction des 3 dépôts
├── app.py                  # Interface Gradio (IA + HITL)
├── interface_cli.py        # Fallback CLI
├── pyproject.toml          # Dépendances Python
├── uv.lock                 # Versions verrouillées
├── Makefile                # make install / lint / test / demo / ui
├── LICENSE / NOTICE        # Apache 2.0 © 2026 UCit
├── .github/workflows/ci.yml # CI GitHub Actions (ruff + pytest)
├── templates/              # 4 templates de ticket
├── tickets/                # 8 tickets clients, 8 résolutions
├── tools/                  # 8 outils IA + HITL
├── docs/                   # Runbook, known issues, escalade, profil, CCME
└── tests/                  # Contrats, outils, interface Gradio
```

### Dépôts sources analysés

| Dépôt | Éléments | Fichiers clés |
|---|---|---|
| `oka_healthchecks` | 68 règles HealthCheck, 9 domaines | `resources/cores_account_quota_rule.py`, `jobs/failed_jobs_rule.py`, `kpi/high_cost_rule.py`, `load/core_load_rule.py` |
| `oka_dataenhancers` | 8 Data Enhancers, 5 catégories | `costs/costs_demo.py`, `CO2/carbon_cost_RTE.py` |
| `oka_webhooks` | 4 bridges webhook (SES, Slack, Jira, Reporting) | `oka-slack-bridge/app.py`, `oka-slack-bridge/.service` |

Les trois dépôts sont sous licence Apache 2.0, version `2026.10.0`, testés
contre **OKA 3.3.0**. Les chiffres réels sont **68 règles** et **8 enhancers**
(et non 40 / 7 comme dans l’énoncé initial).

---

## 5. Les 8 tickets

| Ticket | Client | Composant | Résolution |
|---|---|---|---|
| TICKET-001 | Ahmed Benali — Institut de Recherche | HealthCheck / resources | `cores_account_quota_rule.py` |
| TICKET-002 | Jean Dupont — Labo Example | HealthCheck / jobs | `failed_jobs_rule.py` |
| TICKET-003 | Marie Leroy — Entreprise Industrielle | HealthCheck / kpi | `high_cost_rule.py` |
| TICKET-004 | Pierre Martin — Université | Data Enhancer / costs | `custom_cost_enhancer.py` |
| TICKET-005 | Sophie Bernard — Centre de Calcul | Data Enhancer / CO2 | `resolution.txt` |
| TICKET-006 | Lucas Petit — Startup IA | Webhook Bridge | `resolution.txt` |
| TICKET-007 | Nathalie Rousseau — École d’Ingénieurs | Formation | `training_plan.md` |
| TICKET-008 | Camille Moreau — Institut des Géosciences | Portail & Visualisation | Runbook, Nginx, scripts Linux/Windows |

Chaque ticket contient `request.md`, `qualification.md`, `diagnosis.md`,
`resolution/`, `response.md` et `lessons.md`.

---

## 6. Méthode et approche IA + HITL

`METHOD.md` détaille les cinq étapes : **qualifier → diagnostiquer → résoudre →
répondre → capitaliser**, avec pour chacune l’objectif, les actions, les
livrables et les garde-fous.

`AI_METHOD.md` décrit l’architecture IA + HITL et les trois garde-fous :

1. **Aucune action automatique** : l’humain valide avant toute action client.
2. **Traçabilité** : chaque sortie est affichée ou écrite dans un fichier révisable.
3. **Transparence** : chaque outil affiche un avertissement HITL.

Les outils utilisent une heuristique déterministe, sans dépendance cloud. Un LLM
local via Ollama reste optionnel.

---

## 7. Ce que cela démontre

| Mission | Preuve dans le POC |
|---|---|
| Comprendre `HealthcheckRule` | `cores_account_quota_rule.py` : `params_model`, `evaluate`, `_no_data_alert`, CRITICAL avant HIGH ; `failed_jobs_rule.py` : `_FAILED_STATES`, `min_jobs` |
| Comprendre `DataEnhancer` | `custom_cost_enhancer.py` : `params_model`, `run`, colonne `Cost`, préfixe `Cust_`, regex de compte |
| Comprendre le payload webhook | `TICKET-006` : `{subject, body}`, Bearer token, routes `/health` et `/notify` |
| Visualisation distante et portail | `TICKET-008` : TurboVNC, VirtualGL, noVNC, Nginx, ALB AWS, branding et restriction IP |
| Linux, Windows, shell et PowerShell | `check_remote_viz.sh`, `Test-RemoteViz.ps1`, systemd, Nginx |
| CCME et OKA | OKA : tickets 001 à 007 ; CCME : `docs/ccme_deployment_checklist.md` |
| Anglais technique écrit | `TICKET-008/resolution/english_summary.md` |
| Appliquer les patterns UCit | `frozenset`, `_FAILED_STATES`, `_no_data_alert`, `min_jobs`, CRITICAL avant HIGH |
| Méthode reproductible | `METHOD.md` et les 8 tickets |
| IA + HITL | `app.py` et les 8 outils, avec journal et validation humaine |
| Tests de contrat | 41 tests : compilation, AST, `TypeError` sans `params_model`, outils, interface |

---

## 8. Tests et CI

```bash
make test
```

La suite couvre :

- `test_classifier.py` : les 9 familles de tickets, dont portail/visualisation et CCME ;
- `test_diagnostic_helper.py` : checklist non vide pour toutes les familles et composants ;
- `test_resolution_contracts.py` : compilation, AST, contrat `params_model`,
  `TypeError` à la définition d’une règle sans `params_model`, contrat enhancer ;
- `test_tools.py` : exécution des 8 outils, HITL, génération de règle compilable,
  profil de formation, colonnes de priorisation ;
- `test_gradio_app.py` : construction de l’interface, onglet Profil, rendu des
  livrables et coloration des scripts Bash/PowerShell/Nginx.

**41 tests passent** avec `make test`. La CI GitHub Actions exécute `uv sync`,
`ruff` puis `pytest` sur chaque push et pull request.

---

## 9. Limites assumées

- **Pas d’instance OKA réelle** : les règles sont compilées et vérifiées
  statiquement, pas exécutées contre la plateforme.
- **Pas de SDK OKA fourni** : le test de contrat utilise un stub minimal pour
  vérifier le `TypeError` et la présence de `params_model`.
- **Pas de LLM obligatoire** : fallback heuristique déterministe, Ollama optionnel.
- **Enhancer TICKET-004** : validé statiquement ; `pandas` n’est pas une
  dépendance runtime du POC.
- **Interface Gradio locale** : sans authentification, à ne pas exposer
  publiquement sans reverse proxy et contrôle d’accès.
- **8 tickets simulés** : ils démontrent la méthode, pas un historique réel.
- **Portail et visualisation non déployés** : le runbook et les scripts sont
  fournis, mais aucune infrastructure AWS/GPU réelle n’est attachée au POC.
- **CCME partiel** : checklist générique uniquement, faute de dépôt ou d’instance
  CCME dans le périmètre.
- **Anglais oral non démontrable** : l’anglais technique écrit est couvert par
  la synthèse de TICKET-008.

---

## 10. Références

- Dépôts sources : `../oka_healthchecks`, `../oka_dataenhancers`, `../oka_webhooks`
- Matrice profil : [`docs/profile_alignment.md`](docs/profile_alignment.md)
- Documentation OKA : https://doc.oka.how
- Plateforme OKA : https://oka.how
- UCit : https://ucit.fr
- Dépôt du POC : `git@ssh.bitbucket.org:lavaud_olivier/hpc-oka-support-desk.git`
