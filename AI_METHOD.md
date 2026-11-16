# AI_METHOD — Approche IA + HITL (Human In The Loop)

## Architecture

Les outils du dossier `tools/` sont des scripts Python exécutables. Chaque outil
utilise par défaut une **heuristique déterministe** documentée comme fallback.
Un **LLM local optionnel via Ollama** (`qwen2.5-coder:7b`) peut être activé pour
la génération de règle ; aucune dépendance cloud n'est requise.

## Mode LLM local optionnel

Le mode est désactivé par défaut. Il s'active avec `--llm` ou `OKA_LLM=ollama`.

```bash
ollama serve
ollama pull qwen2.5-coder:7b
make llm-check
OKA_LLM=ollama uv run python tools/rule_generator.py \
  "Alerter si le taux d'échec des jobs dépasse 10 %" --llm
```

Le client `tools/llm_client.py` appelle `/api/chat` avec `temperature=0`, un
format JSON et un timeout de 60 s. Le modèle propose uniquement :

- le domaine ;
- le nom de règle ;
- `warn_threshold` et `critical_threshold` ;
- une justification courte.

Le template et les validateurs restent maîtres : domaine connu, seuils ordonnés
et bornés selon `ratio`/`percent`/`absolute`, provider vérifié dans `llms.txt`.
Le domaine est d'abord détecté par mots-clés métier ; le LLM n'arbitre que si
aucun mot-clé ne correspond. Les nombres explicites de la demande priment sur le
LLM, les seuils sont normalisés si le modèle change d'échelle (0,8 vs 80 %), et
une proposition trop éloignée des défauts du domaine (facteur 2) est rejetée.
Toute erreur ou sortie invalide déclenche le fallback heuristique. Timeout par
défaut : 60 s (`OKA_LLM_TIMEOUT`).

## Interface Gradio

`app.py` expose les 8 outils dans une interface unique, avec un onglet par
étape de la méthode (qualifier, diagnostiquer, répondre, générer une règle,
former, capitaliser), un onglet « Profil & preuves » et les livrables des
8 tickets. L'interface affiche le bandeau HITL, le journal de sortie de chaque
outil et les scripts Linux/Windows du ticket 008. Elle ne déclenche aucune
action sur la plateforme OKA : elle prépare des propositions.

## Les 3 garde-fous

| Garde-fou | Description |
|-----------|-------------|
| 1. Aucune action automatique | Aucun outil ne modifie la plateforme client sans validation humaine explicite |
| 2. Traçabilité | Chaque sortie d'outil est affichée ou écrite dans un fichier révisable par l'ingénieur |
| 3. Transparence | Chaque outil affiche un avertissement HITL avant toute utilisation |

## Limites

- Hallucinations possibles d'un LLM local : toujours relire la sortie
- Pas de décision autonome : l'ingénieur reste le seul décideur
- Fallback heuristique : moins précis qu'un LLM mais déterministe et auditable
- Ollama local uniquement : pas de cloud, pas de secrets dans les prompts
- `rule_generator.py` produit un squelette à partir d'un template et d'heuristiques :
  les providers sont alignés sur `oka_healthchecks`, mais les seuils et la
  sémantique métier doivent être validés règle par règle

## Rôle de l'humain à chaque étape

| Outil | Ce que l'IA prépare | Ce que l'humain valide |
|-------|--------------------|----------------------|
| `ticket_classifier.py` | Famille, sévérité, composant, confiance | Classification finale |
| `diagnostic_helper.py` | Checklist de vérifications | Résultats des vérifications, cause racine |
| `response_generator.py` | Brouillon de réponse client | Version finale envoyée au client |
| `rule_generator.py` | Squelette `HealthcheckRule` pour 9 domaines OKA, providers réels, seuils pré-remplis, contrôle du provider dans `llms.txt` | Vérification des seuils, de la métrique et publication sur la plateforme |
| `ticket_prioritizer.py` | Ordre de priorité proposé | Ordre de traitement retenu |
| `automation_identifier.py` | Liste d'automatisations par ROI | Automatisations à implémenter |
| `training_generator.py` | Parcours de formation | Contenu adapté au client |
| `rnd_feedback_analyzer.py` | Irritants récurrents | Évolutions à remonter à la R&D |

## Garde-fous contractuels

- `tools/contract_context.py` lit les `llms.txt` publics des dépôts OKA et
  produit un rapport de dérive (`make contracts`).
- `rule_generator.py` indique si le provider du domaine est bien documenté dans
  `oka_healthchecks/llms.txt` ; ce contrôle reste informatif et ne remplace pas
  la validation humaine.
- `tests/test_llms_contract.py` compare les providers/méthodes du générateur aux
  dépôts sources et signale les liens d’exemples cassés. Les tests sont ignorés
  si les dépôts `../oka_*` ne sont pas présents.
- Les `llms.txt` ne sont pas une source de vérité : le SDK, les exemples qui
  compilent et `compatibility.json` priment.

## Exemple d'avertissement HITL (affiché par chaque outil)

```
╔═══════════════════════════════════════════════════════════════╗
║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║
║  Cette sortie est une proposition, pas une décision finale.   ║
║  Relire, modifier si nécessaire, et valider avant toute usage.║
╚═══════════════════════════════════════════════════════════════╝
```
