# Diagnostic — TICKET-006

## Cause racine
Le token Bearer configuré dans le canal webhook OKA est différent de la
variable `BRIDGE_BEARER_TOKEN` du bridge Slack. Le middleware `_check_auth()`
rejette les requêtes avec un HTTP 401. Les logs du bridge (journalctl) montrent
ces rejets, mais le client n'en a pas conscience.

## Checklist de vérifications
- [x] Bridge Slack opérationnel : GET /health retourne {"status": "ok"}
- [x] Route POST /notify présente dans oka-slack-bridge/app.py
- [x] Payload OKA attendu : {"subject": "...", "body": "..."} (POST JSON ou GET query)
- [x] Middleware _check_auth() vérifie Authorization: Bearer <BRIDGE_BEARER_TOKEN>
- [x] Token Bearer côté OKA ≠ token Bearer côté bridge (mismatch)
- [x] Logs namespacés : logging.getLogger("oka-slack-bridge")

## Preuves observées
- Fichier source : ./oka_webhooks/oka-slack-bridge/app.py
- Code : `if auth != f"Bearer {BEARER_TOKEN}": return jsonify({"error": "Unauthorized"}), 401`
- Port par défaut : 5052
- Variable d'env : BRIDGE_BEARER_TOKEN

## Impact client
Aucune alerte OKA n'est transmettre sur Slack. Le client n'est pas informé des
incidents sur son cluster.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : mismatch de token Bearer
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Aligner BRIDGE_BEARER_TOKEN côté bridge et côté OKA, vérifier
  les logs du bridge (401 dans journalctl).

**Ingénieur** : Support N2 | **Date** : 2026-10-15
