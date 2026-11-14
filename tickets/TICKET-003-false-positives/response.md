# Réponse client — TICKET-003

## Destinataire
Marie Leroy — Entreprise Industrielle

## Objet
Réduction des faux positifs high_cost_rule — recalibrage des seuils

## Corps du message

Bonjour Marie,

Nous faisons suite à votre demande concernant les trop nombreuses alertes
`high_cost_rule`, devenues du bruit sur votre dashboard.

### Cause identifiée
Les seuils par défaut de la règle (10 000 / 50 000) sont trop bas pour votre
volumétrie de coûts, qui se situe autour de 8 000–12 000 par période. Chaque
légère fluctuation générait une alerte. De plus, aucun garde-fou min_jobs n'était
présent pour lisser les pics ponctuels.

### Solution apportée
Nous avons recalibré la règle avec les paramètres suivants :
- Seuil HIGH : 25 000 (au lieu de 10 000)
- Seuil CRITICAL : 75 000 (au lieu de 50 000)
- Garde-fou `min_jobs` : 10 jobs minimum avant évaluation

La règle respecte le contrat OKA : `params_model` Pydantic, `_no_data_alert`,
CRITICAL vérifié avant HIGH.

### Preuve de résolution
La règle modifiée a été republiée. Les seuils sont maintenant adaptés à votre
volumétrie, et les pics ponctuels sur de petits workloads sont filtrés par le
garde-fou min_jobs.

### Prévention
Si vos coûts évoluent significativement, n'hésitez pas à nous contacter pour un
nouveau recalibrage des seuils.

### Disponibilité
Notre équipe support reste à votre disposition pour toute question complémentaire.

Cordialement,
L'équipe support UCit

---

Validé par l'ingénieur : Support N1 | Date : 2026-10-13
Bandeau BROUILLON supprimé : oui
