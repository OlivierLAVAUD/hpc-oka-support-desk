# Leçons — TICKET-008

## Leçon tirée
Une migration de portail de visualisation peut réussir les tests 2D tout en
laissant la 3D inutilisable : noVNC et TurboVNC peuvent démarrer, mais sans
VirtualGL le rendu OpenGL bascule silencieusement sur `llvmpipe`. Les WebSockets
et le timeout ALB sont deux points de contrôle distincts à tester avant la mise
en production.

## Recommandation pour le client
Exécuter la checklist de pré-flight avant chaque changement d'image, de pilote
GPU ou de règle ALB. Tester une session 3D depuis Linux et Windows, pas
uniquement la page de connexion.

## Guide client proposé
1. Vérifier `nvidia-smi` et `vglrun glxinfo -B` sur le nœud de visualisation.
2. Contrôler `systemctl status turbovncserver` et le port 6080 en local.
3. Vérifier les en-têtes WebSocket Nginx et le timeout ALB (≥ 300 s).
4. Lancer `check_remote_viz.sh` côté Linux et `Test-RemoteViz.ps1` côté Windows.
5. Ouvrir une session 3D, la laisser inactive plus de deux minutes, puis vérifier
   qu'elle reste connectée.

## Irritant produit à remonter à la R&D
Le portail ne signale pas que le rendu est logiciel : il devrait exposer le
renderer OpenGL dans l'interface d'administration et bloquer une session 3D si
`llvmpipe` est détecté. Une alerte de pré-flight éviterait une migration
silencieusement dégradée.

## Capitalisation
- [x] Ajouté à `docs/known_issues.md` : renderer logiciel et WebSocket ALB
- [x] Proposition d'automatisation : `check_remote_viz.sh` et `Test-RemoteViz.ps1`
- [x] Intégré au parcours de formation (Module 1 — architecture et accès)
- [x] Ajouté au runbook `docs/runbook.md` (famille remote-visualization)
- [x] Synthèse technique anglaise : `resolution/english_summary.md`

**Ingénieur** : Support N2 | **Date** : 2026-10-21
