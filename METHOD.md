# METHOD — Méthode de support en 5 étapes

Démarche reproductible pour traiter un ticket client OKA, inspirée des
contrats et patterns des dépôts `oka_healthchecks`, `oka_dataenhancers` et
`oka_webhooks`.

---

## Étape 1 — Qualifier

**Objectif** : Comprendre la demande du client, identifier le composant concerné
et évaluer la sévérité.

**Actions** :
1. Lire le fichier `request.md` du ticket
2. Utiliser `tools/ticket_classifier.py` pour obtenir une proposition de
   famille, sévérité, composant et confiance
3. Valider ou corriger la classification (garde-fou HITL)
4. Créer le fichier `qualification.md` résumant : client, demande, composant,
   famille, sévérité, confiance

**Livrables** : `tickets/TICKET-XXX/qualification.md`

**Garde-fous** :
- Aucune action sur la plateforme client sans qualification écrite
- La classification IA est une proposition, jamais une décision finale

---

## Étape 2 — Diagnostiquer

**Objectif** : Identifier la cause racine du problème.

**Actions** :
1. Utiliser `tools/diagnostic_helper.py --family <famille> --component <composant>`
   pour obtenir une checklist de vérifications
2. Cocher chaque item et documenter le résultat observé
3. S'appuyer sur les patterns des dépôts :
   - `min_jobs` guard (règle silencieuse sur petits échantillons)
   - `ResultStatus.OK` / données vides du provider
   - `_FAILED_STATES` (frozenset des états d'échec)
   - `BRIDGE_BEARER_TOKEN` aligné entre OKA et le bridge
   - Colonne `ENERGY` présente avant l'enhancer CO2
   - Portail/visualisation : TLS, WebSocket, TurboVNC, VirtualGL/GPU, SSO
4. Créer le fichier `diagnosis.md` avec cause racine et preuves

**Livrables** : `tickets/TICKET-XXX/diagnosis.md`

**Garde-fous** :
- Toujours vérifier `ResultStatus` avant d'utiliser un provider
- Toujours vérifier `min_jobs` avant de conclure à une absence d'alerte
- Documenter chaque vérification, même négative

---

## Étape 3 — Résoudre

**Objectif** : Produire une résolution technique conforme aux contrats OKA.

**Actions** :
1. Utiliser `tools/rule_generator.py` pour générer un squelette de règle
   HealthCheck (9 domaines OKA, providers réels) ; ajouter `--llm` ou
   `OKA_LLM=ollama` pour une suggestion locale Qwen, toujours validée avant
   usage. Pour un enhancer, s'inspirer de
   `../oka_dataenhancers/costs/costs_demo.py`
2. Contrôler le provider et la méthode dans `../oka_healthchecks/llms.txt`
   (`make contracts`), sans s'y fier aveuglément : les liens peuvent dériver
3. Vérifier les 5 patterns obligatoires (checklist affichée par l'outil) :
   - `params_model` Pydantic avec valeurs par défaut
   - `evaluate()` / `run()` conforme
   - `_no_data_alert` quand le provider échoue (convention majoritaire)
   - CRITICAL vérifié avant HIGH
   - `min_jobs` guard si applicable
4. Valider les seuils par défaut et la métrique extraite du DTO : le générateur
   produit un squelette, pas une règle publiable telle quelle
5. Pour un portail ou une visualisation, appliquer le runbook
   `TICKET-008/resolution/remote_viz_portal_runbook.md` (Linux/Windows/AWS)
6. Écrire le fichier de résolution dans `tickets/TICKET-XXX/resolution/`
7. Tester le contrat avec `tests/test_resolution_contracts.py`
**Livrables** : `tickets/TICKET-XXX/resolution/*.py`

**Garde-fous** :
- Aucun code sans `params_model` (lève `TypeError` via `__init_subclass__`)
- Pas de seuil en dur sans valeur par défaut
- Préfixe `Cust_` pour colonnes non réservées dans un enhancer

---

## Étape 4 — Répondre

**Objectif** : Rédiger la réponse client claire et structurée.

**Actions** :
1. Utiliser `tools/response_generator.py` à partir du `diagnosis.md`
2. Relire et modifier le brouillon généré (bandeau "BROUILLON")
3. Inclure : accusé, cause, solution, preuve, prévention, disponibilité
4. Créer le fichier `response.md`

**Livrables** : `tickets/TICKET-XXX/response.md`

**Garde-fous** :
- Jamais d'envoi automatique : l'humain relit et valide avant envoi
- Le bandeau BROUILLON doit être supprimé avant envoi client

---

## Étape 5 — Capitaliser

**Objectif** : Transformer la résolution en connaissance réutilisable.

**Actions** :
1. Rédiger `lessons.md` : leçon tirée, recommandation produit, guide client
2. Mettre à jour `docs/known_issues.md` si le problème est récurrent
3. Utiliser `tools/rnd_feedback_analyzer.py` pour identifier les irritants
   récurrents à remonter à la R&D
4. Proposer une automatisation via `tools/automation_identifier.py` si ROI

**Livrables** : `tickets/TICKET-XXX/lessons.md`, mise à jour `docs/known_issues.md`

**Garde-fous** :
- Chaque évolution proposée à la R&D est validée par l'ingénieur avant envoi
- La capitalisation alimente la formation future (TICKET-007)
