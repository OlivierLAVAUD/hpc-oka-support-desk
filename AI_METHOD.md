# AI_METHOD — Approche IA + HITL (Human In The Loop)

## Architecture

Les outils du dossier `tools/` sont des scripts Python exécutables. Chaque outil
peut s'appuyer sur un LLM local (Ollama) si disponible, mais utilise par défaut
une \*\*heuristique déterministe\*\* documentée comme fallback. Aucune dépendance
cloud n'est requise.

## Les 3 garde-fous

| Garde-fou | Description |
|-----------|-------------|
| 1. Aucune action automatique | Aucun outil ne modifie la plateforme client sans validation humaine explicite |
| 2. Traçabilité | Chaque sortie d'outil est écrite dans un fichier markdown révisable par l'ingénieur |
| 3. Transparence | Chaque outil affiche un avertissement HITL avant toute utilisation |

## Limites

- Hallucinations possibles d'un LLM local : toujours relire la sortie
- Pas de décision autonome : l'ingénieur reste le seul décideur
- Fallback heuristique : moins précis qu'un LLM mais déterministe et auditable

## Rôle de l'humain à chaque étape

| Outil | Ce que l'IA prépare | Ce que l'humain valide |
|-------|--------------------|----------------------|
| `ticket_classifier.py` | Famille, sévérité, composant, confiance | Classification finale |
| `diagnostic_helper.py` | Checklist de vérifications | Résultats des vérifications, cause racine |
| `response_generator.py` | Brouillon de réponse client | Version finale envoyée au client |
| `rule_generator.py` | Code de règle/enhancer conforme OKA | Publication sur la plateforme |
| `ticket_prioritizer.py` | Ordre de priorité proposé | Ordre de traitement retenu |
| `automation_identifier.py` | Liste d'automatisations par ROI | Automatisations à implémenter |
| `training_generator.py` | Parcours de formation | Contenu adapté au client |
| `rnd_feedback_analyzer.py` | Irritants récurrents | Évolutions à remonter à la R&D |

## Exemple d'avertissement HITL (affiché par chaque outil)

```
╔═══════════════════════════════════════════════════════════════╗
║  AVERTISSEMENT HITL — À VALIDER PAR L'INGÉNIEUR SUPPORT      ║
║  Cette sortie est une proposition, pas une décision finale.   ║
║  Relire, modifier si nécessaire, et valider avant toute usage.║
╚═══════════════════════════════════════════════════════════════╝
```
