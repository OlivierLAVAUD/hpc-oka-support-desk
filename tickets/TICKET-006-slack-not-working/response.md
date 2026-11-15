# Réponse client — TICKET-006

## Destinataire
Lucas Petit — Startup IA

## Objet
Bridge Slack — alertes non reçues, résolution du token Bearer

## Corps du message

Bonjour Lucas,

Nous faisons suite à votre signalement : votre bridge Slack est opérationnel
(`/health` retourne OK), mais aucune alerte n'est reçue sur votre canal.

### Cause identifiée
Le token Bearer configuré dans le canal webhook OKA est différent de la variable
`BRIDGE_BEARER_TOKEN` de votre bridge Slack. Le middleware d'authentification
rejette chaque requête d'OKA avec une erreur HTTP 401 (non autorisé). Les alertes
sont donc bloquées avant d'atteindre Slack.

### Solution apportée
1. Récupération du token configuré dans le canal webhook OKA
2. Mise à jour de `BRIDGE_BEARER_TOKEN` dans le fichier `.env` du bridge
3. Redémarrage du service systemd `oka-slack-bridge`
4. Vérification dans `journalctl -u oka-slack-bridge -f` : plus de 401

### Preuve de résolution
Après alignement des tokens, une alerte de test envoyée depuis OKA a été reçue
correctement sur votre canal Slack. Le bridge fonctionne désormais en bout en bout.

### Prévention
- Vérifier systématiquement l'alignement des tokens Bearer entre OKA et le bridge
  lors de toute configuration
- Surveiller les logs du bridge (`journalctl -u oka-slack-bridge -f`) pour
  détecter les rejets 401

### Disponibilité
Notre équipe support reste à votre disposition pour toute question complémentaire.

Cordialement,
L'équipe support UCit

---

Validé par l'ingénieur : Support N2 | Date : 2026-10-16
Bandeau BROUILLON supprimé : oui
