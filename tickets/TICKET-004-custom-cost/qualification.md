# Qualification — TICKET-004

## Client
- **Nom** : Pierre Martin
- **Organisation** : Université

## Demande
Data Enhancer personnalisé pour calcul de coût avec :
- Tarif CPU : 0,015 €/heure-core
- Tarif GPU : 0,035 €/heure-GPU
- Réduction étudiante : 0,0075 €/heure-core sur comptes "etudiant_*".

## Composant OKA concerné
- **Famille** : custom-enhancer
- **Composant** : Data Enhancer
- **Domaine** : costs

## Sévérité proposée
- **Niveau** : medium
- **Confiance IA** : 90%

## Qualification validée par l'ingénieur
- [x] Famille confirmée : custom-enhancer (développement d'un enhancer sur mesure)
- [x] Composant confirmé : Data Enhancer, domaine costs
- [x] Sévérité confirmée : medium (nouvelle fonctionnalité, pas d'incident)
- [ ] Commentaire : S'inspirer de costs_demo.py pour la structure, adapter les
  paramètres et le pattern de compte avec regex.

**Ingénieur** : Support N2 | **Date** : 2026-10-13
