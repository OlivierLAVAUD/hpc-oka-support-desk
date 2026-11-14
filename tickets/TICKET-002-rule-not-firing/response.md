# Réponse client — TICKET-002

## Destinataire
Jean Dupont — Labo Example

## Objet
Règle failed_jobs_rule silencieuse — diagnostic et résolution

## Corps du message

Bonjour Jean,

Nous faisons suite à votre signalement : la règle `failed_jobs_rule` ne
levait aucune alerte malgré des échecs de jobs observés sur votre cluster.

### Cause identifiée
Votre workload ne contient que 3 jobs sur la période évaluée. La règle applique
un garde-fou `min_jobs` (seuil minimal de 10 jobs par défaut) pour éviter les
faux positifs statistiques sur des échantillons trop petits. En dessous de ce
seuil, la règle reste volontairement silencieuse.

### Solution apportée
Nous avons adapté la règle avec un seuil `min_jobs` réduit à 3, et ajouté une
alerte de niveau OK explicite lorsque l'échantillon est insuffisant (au lieu de
retourner silencieusement une liste vide). Vous serez désormais informé, même
sur un petit workload, que la règle n'a pas assez de données pour conclure.

### Preuve de résolution
La règle modifiée a été republiée sur votre workload. Elle :
- Déclenche HIGH à 10 % de taux d'échec, CRITICAL à 30 %
- Reste silencieuse en dessous de 3 jobs (avec une alerte OK informative)
- Respecte le contrat OKA : `params_model`, `evaluate`, CRITICAL avant HIGH

### Prévention
Surveillez le nombre de jobs sur vos workloads. Si un workload reste très petit,
considérez l'agrégation sur une période plus longue.

### Disponibilité
Notre équipe support reste à votre disposition pour toute question complémentaire.

Cordialement,
L'équipe support UCit

---

Validé par l'ingénieur : Support N2 | Date : 2026-10-12
Bandeau BROUILLON supprimé : oui
