# Réponse client — TICKET-008

## Destinataire
Camille Moreau — Institut des Géosciences

## Objet
Portail de visualisation — rétablissement des sessions 3D et stabilité des sessions 2D

## Corps du message

Bonjour Camille,

Nous faisons suite à votre signalement concernant les sessions 3D de votre
portail de visualisation migré vers AWS.

### Cause identifiée
Les sessions graphiques étaient lancées avec TurboVNC, mais sans le wrapper
`vglrun` de VirtualGL. Les applications OpenGL utilisaient donc le rendu
logiciel `llvmpipe`, ce qui provoquait un écran noir ou un blocage au démarrage
des sessions 3D.

Deux réglages aggravants ont également été identifiés : le délai d'inactivité
du groupe cible ALB était limité à 60 secondes, et Nginx ne relayait pas
correctement les en-têtes WebSocket utilisés par noVNC. D'où les déconnexions
après une minute, notamment depuis Windows.

### Solution apportée
1. Modification du lanceur de session pour exécuter les applications 3D avec
   `vglrun` et vérification du renderer OpenGL.
2. Mise à jour de la configuration Nginx avec les en-têtes `Upgrade` et
   `Connection`, ainsi qu'un timeout de proxy adapté aux sessions longues.
3. Passage du délai d'inactivité ALB de 60 à 300 secondes.
4. Personnalisation de la page de connexion (logo, couleurs, message d'accueil)
   et restriction d'accès aux plages IP du laboratoire.
5. Ajout d'un contrôle de santé Linux et d'un script de vérification Windows
   pour les futures migrations.

### Preuve de résolution
Après application, une session 3D ParaView a été ouverte simultanément depuis
un poste Linux et un poste Windows. Le renderer OpenGL affiche bien la GPU
NVIDIA, les sessions restent actives au-delà de cinq minutes et la page de
connexion personnalisée est accessible uniquement depuis les plages autorisées.

### Prévention
- Le script `check_remote_viz.sh` vérifie GPU, VirtualGL, TurboVNC, Nginx et
  santé du portail avant chaque mise en production.
- Le script `Test-RemoteViz.ps1` contrôle DNS, TLS, port 443, santé HTTP et
  pilote graphique côté Windows.
- La procédure de migration est documentée dans le runbook du portail.

### Disponibilité
Notre équipe reste à votre disposition pour valider les accès des différents
laboratoires et ajuster les plages IP si nécessaire.

Cordialement,
L'équipe support UCit

---

Validé par l'ingénieur : Support N2 | Date : 2026-10-21
Bandeau BROUILLON supprimé : oui
