# Qualification — TICKET-006

## Client
- **Nom** : Lucas Petit
- **Organisation** : Startup IA

## Demande
Bridge Slack up, /health OK, mais aucune alerte reçue sur le canal Slack.

## Composant OKA concerné
- **Famille** : notification
- **Composant** : Webhook Bridge
- **Domaine** : webhook

## Sévérité proposée
- **Niveau** : high
- **Confiance IA** : 80%

## Qualification validée par l'ingénieur
- [x] Famille confirmée : notification (webhook non délivré)
- [x] Composant confirmé : Webhook Bridge, domaine webhook
- [x] Sévérité confirmée : high (alertes non transmises au client)
- [ ] Commentaire : Hypothèse — token Bearer différent entre OKA et le bridge,
  entraînant des rejets 401 non visibles côté client.

**Ingénieur** : Support N2 | **Date** : 2026-10-15
