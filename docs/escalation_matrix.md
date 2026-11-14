# Escalation Matrix — Matrice d'escalade

| Situation | Escalader ? | Destinataire | Délai |
|-----------|-------------|--------------|-------|
| Règle de quota standard à configurer | Non | Support N1 | Immédiat |
| Règle silencieuse (min_jobs) | Non | Support N2 | < 4h |
| Faux positifs (seuils) | Non | Support N1 | < 8h |
| Enhancer personnalisé à développer | Non | Support N2 | < 2j |
| Données manquantes (chaîne d'enhancers) | Oui si dépendance externe | Support N2 / R&D | < 4h |
| Token Bearer mismatch | Non | Support N2 | < 2h |
| Bug dans le SDK OKA | Oui | R&D | < 24h |
| Demande de formation | Non | Support N1 | < 1j |
| Demande de fonctionnalité produit | Oui | Product | < 1s |
| Incident de production (cluster down) | Oui | N2 + R&D | Immédiat |

**Niveaux** :
- **N1** : Support de premier niveau (configuration, formation, questions courantes)
- **N2** : Support de second niveau (diagnostic, développement d'enhancers/rules, dépannage)
- **R&D** : Recherche et développement (bugs SDK, évolutions produit)
- **Product** : Équipe produit (demandes de fonctionnalités)
