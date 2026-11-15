# Qualification — TICKET-008

## Client
- **Nom** : Camille Moreau
- **Organisation** : Institut des Géosciences

## Demande
Portail de visualisation migré vers AWS : sessions 2D opérationnelles, sessions
3D en écran noir et déconnexions Windows après une minute. Demande de
personnalisation de la page de connexion et de restriction d'accès par plage IP.

## Composant OKA concerné
- **Famille** : remote-visualization
- **Composant** : Portail & Visualisation
- **Domaine** : visualization

## Sévérité proposée
- **Niveau** : high
- **Confiance IA** : 85%

## Qualification validée par l'ingénieur
- [x] Famille confirmée : incident de visualisation distante et de portail
- [x] Composant confirmé : Portail & Visualisation
- [x] Sévérité confirmée : high (3D inutilisable, 2D intermittente)
- [ ] Commentaire : Vérifier la chaîne ALB → Nginx → noVNC/TurboVNC, puis
  l'activation de VirtualGL et le délai d'inactivité ALB/WebSocket.

**Ingénieur** : Support N2 | **Date** : 2026-10-20
