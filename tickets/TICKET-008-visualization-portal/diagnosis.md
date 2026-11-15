# Diagnostic — TICKET-008

## Cause racine
Le portail lance les sessions graphiques avec TurboVNC, mais sans le wrapper
`vglrun` de VirtualGL. Les applications OpenGL (ParaView, Blender) rendent donc
en logiciel via `llvmpipe` : la session 3D reste noire ou se bloque au démarrage.

Deux facteurs aggravants expliquent les déconnexions Windows :
- le groupe cible ALB utilise le délai d'inactivité par défaut de 60 s, trop
  court pour une session de visualisation ;
- Nginx ne transmet pas les en-têtes `Upgrade` / `Connection`, ce qui interrompt
  le WebSocket noVNC au premier renouvellement.

## Checklist de vérifications
- [x] DNS et certificat TLS du portail valides
- [x] Groupe cible ALB `healthy` sur le port Nginx
- [x] Session 2D noVNC accessible sur le port 6080
- [x] `vglrun glxinfo -B` exécuté : renderer `llvmpipe`, pas de GPU
- [x] Pilote NVIDIA présent, mais VirtualGL non appelé par le lanceur de session
- [x] En-têtes WebSocket absents de la configuration Nginx
- [x] Délai d'inactivité ALB à 60 s, sessions interrompues après une minute
- [x] Journaux navigateur Windows : WebSocket fermé avec le code 1006

## Preuves observées
- `nvidia-smi` détecte une GPU NVIDIA et le pilote est à jour.
- `vglrun glxinfo -B` retourne `OpenGL renderer: llvmpipe (LLVM ...)`.
- `nginx -T` ne contient ni `proxy_set_header Upgrade` ni `Connection`.
- Attribut ALB `idle_timeout.timeout_seconds = 60`.
- `journalctl -u turbovncserver` montre des arrêts de session après 60 à 70 s.
- Console Edge/Chrome côté Windows : `WebSocket connection failed: 1006`.

## Impact client
Les chercheurs ne peuvent pas ouvrir de session 3D ; les sessions 2D se coupent
après une minute d'inactivité. Le portail est partiellement indisponible pour
les utilisateurs Windows et pour les travaux de visualisation scientifique.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : VirtualGL absent du lanceur de session
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Corriger le lanceur avec `vglrun`, activer les WebSockets
  Nginx, porter le timeout ALB à 300 s, puis valider 2D/3D sur Linux et Windows.

**Ingénieur** : Support N2 | **Date** : 2026-10-20
