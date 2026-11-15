# Profil UCit — matrice de couverture du POC

Ce document relie chaque mission et chaque exigence du profil d'ingénieur
support UCit à un artefact du POC. Il distingue ce qui est **démontré par un
artefact**, ce qui est **partiel** et ce qui reste **non couvert**. Le POC ne
prétend pas remplacer une expérience réelle chez un client.

## Missions

| Mission du poste | Preuve dans le POC | Niveau |
|---|---|---|
| Installer, déployer et personnaliser la visualisation distante 2D/3D | `TICKET-008` : runbook TurboVNC/VirtualGL, configuration Nginx, scripts Linux/Windows | Démontré par procédure et scripts ; pas d'instance réelle |
| Installer et personnaliser des portails web HPC/IA | `TICKET-008` : `portal-config.example.yaml`, branding, groupes SSO, restriction IP | Démontré |
| Déployer et supporter CCME et OKA | OKA : tickets 001 à 007, règles, enhancers, bridges. CCME : `docs/ccme_deployment_checklist.md` | OKA démontré ; CCME partiel (checklist générique) |
| Investiguer, trier et résoudre les incidents N1/N2 | 8 tickets, `ticket_classifier`, `diagnostic_helper`, `docs/runbook.md` | Démontré |
| Gérer les tickets : répartition, suivi, escalade, relation client | `ticket_prioritizer`, `docs/escalation_matrix.md`, templates, réponses client | Démontré |
| Réduire la charge manuelle par l'automatisation | 8 outils, interface Gradio, scripts de pré-flight, CI | Démontré |
| Concevoir des formations et transférer les compétences | `TICKET-007`, `training_generator.py`, parcours en 3 modules | Démontré |
| Contribuer à la R&D et aux tests internes | `lessons.md`, `rnd_feedback_analyzer.py`, tests de contrat, CI | Démontré |

## Profil recherché

| Exigence | Preuve | Niveau |
|---|---|---|
| Bac +5 informatique et/ou expérience administration système/support | Portfolio structuré, méthode support, conventions de code et tests | Preuve indirecte |
| Linux et Windows | Runbook Linux, `check_remote_viz.sh`, `Test-RemoteViz.ps1`, systemd, Nginx | Démontré par scripts et procédures |
| Scripting shell, Python, PowerShell | Outils Python testés, script Bash, script PowerShell | Démontré |
| HPC, infrastructure, virtualisation, visualisation distante | OKA, AWS ALB, TurboVNC/VirtualGL, noVNC, GPU | Démontré par architecture et diagnostic |
| Sens du contact client, rigueur, autonomie, esprit d'équipe | Réponses client, HITL, checklists, revue et tests | Preuve indirecte |
| Anglais technique écrit et oral | `TICKET-008/resolution/english_summary.md` | Démontré à l'écrit |

## Parcours de lecture conseillé

1. `README.md` — vue d'ensemble et lancement de l'interface.
2. `TICKET-008-visualization-portal/` — visualisation, portail, AWS, Linux/Windows.
3. `TICKET-006-slack-not-working/` — webhook, systemd, diagnostic N2.
4. `TICKET-007-training-request/` — formation et transfert de compétences.
5. `docs/runbook.md` et `docs/escalation_matrix.md` — support N1/N2.
6. `tools/` et `tests/` — automatisation, contrats et qualité.
7. `AI_METHOD.md` — garde-fous HITL.

## Limites honnêtes

- Les tickets sont simulés : ils démontrent la méthode, pas un historique client.
- Le portail et la visualisation sont décrits et outillés, pas déployés sur une
  infrastructure réelle.
- CCME n'est couvert que par une checklist générique, faute de dépôt source ou
  d'instance dans le périmètre du POC.
- L'anglais oral ne peut pas être démontré par un dépôt ; la synthèse anglaise
  démontre l'anglais technique écrit.
