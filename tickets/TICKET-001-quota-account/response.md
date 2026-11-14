# Réponse client — TICKET-001

## Destinataire
Ahmed Benali — Institut de Recherche

## Objet
Configuration de votre règle de quota de core-hours (compte "fusion-plasma")

## Corps du message

Bonjour Ahmed,

Nous faisons suite à votre demande concernant la mise en place d'alertes sur la
consommation de core-hours pour le compte "fusion-plasma".

### Cause identifiée
Aucune règle de quota n'était configurée pour votre compte. OKA dispose d'une
règle standard `cores_account_quota_rule.py` qu'il suffit de paramétrer.

### Solution apportée
Nous avons publié une règle de santé avec les paramètres suivants :
- Compte surveillé : `fusion-plasma`
- Quota : 10 000 core-hours
- Seuil HIGH (alerte) : 80 % (8 000 core-hours)
- Seuil CRITICAL (alerte critique) : 90 % (9 000 core-hours)

La règle respecte le contrat OKA : `params_model` Pydantic, `_no_data_alert`
en cas d'absence de données, et vérification de CRITICAL avant HIGH.

### Preuve de résolution
La règle est active sur votre workload. Vous recevrez une alerte HIGH dès que
la consommation atteint 8 000 core-hours, et CRITICAL à 9 000 core-hours.

### Prévention
Surveillez les alertes dans le dashboard OKA. Si vous modifiez votre quota,
pensez à mettre à jour la règle correspondante.

### Disponibilité
Notre équipe support reste à votre disposition pour toute question complémentaire.

Cordialement,
L'équipe support UCit

---

Validé par l'ingénieur : Support N1 | Date : 2026-10-11
Bandeau BROUILLON supprimé : oui
