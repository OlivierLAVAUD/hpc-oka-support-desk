# Qualification — TICKET-005

## Client
- **Nom** : Sophie Bernard
- **Organisation** : Centre de Calcul

## Demande
Dashboards CO2 vides malgré des jobs en cours.

## Composant OKA concerné
- **Famille** : missing-data
- **Composant** : Data Enhancer
- **Domaine** : CO2

## Sévérité proposée
- **Niveau** : high
- **Confiance IA** : 85%

## Qualification validée par l'ingénieur
- [x] Famille confirmée : missing-data (données manquantes dans le dashboard)
- [x] Composant confirmé : Data Enhancer, domaine CO2
- [x] Sévérité confirmée : high (indicateur environnemental indisponible)
- [ ] Commentaire : Hypothèse — la colonne ENERGY est absente du DataFrame car
  l'enhancer de mesure d'énergie (EAR) n'a pas été exécuté en amont.

**Ingénieur** : Support N2 | **Date** : 2026-10-14
