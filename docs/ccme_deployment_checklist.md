# Checklist de déploiement CCME

> Checklist générique de POC. Les noms de paquets, ports, bases de données et
> paramètres exacts doivent être validés avec la documentation CCME du client
> et l'équipe produit UCit. Aucun secret ne doit figurer dans ce fichier.

## 1. Cadrage

- [ ] Version CCME cible et matrice de compatibilité OKA validées
- [ ] Environnement cible identifié : Linux, Windows, cloud ou on-premise
- [ ] Responsables client, fenêtre de changement et plan de rollback définis
- [ ] Critères d'acceptation et tests de fumée convenus
- [ ] Flux réseau, DNS, TLS, proxy et authentification documentés

## 2. Prérequis

- [ ] Comptes de service et permissions minimales créés
- [ ] Base de données, stockage et sauvegarde disponibles
- [ ] SSO/LDAP/OIDC configuré et groupes de rôles alignés
- [ ] Certificats TLS et reverse proxy validés
- [ ] Licence CCME valide et connectivité avec OKA vérifiée
- [ ] Supervision, journaux et alertes branchés

## 3. Déploiement

- [ ] Sauvegarde ou snapshot avant modification
- [ ] Paquets/artefacts vérifiés par empreinte ou signature
- [ ] Configuration CCME déployée depuis un fichier versionné
- [ ] Migrations de base exécutées et journalisées
- [ ] Services démarrés et activés au boot
- [ ] Reverse proxy et WebSocket validés si le portail CCME en dépend
- [ ] Intégration OKA testée : alertes, enhancers et webhooks

## 4. Validation

| Test | Résultat attendu |
|---|---|
| Connexion SSO administrateur | Accès au tableau de bord |
| Connexion utilisateur standard | Accès limité aux rôles prévus |
| Health check public | HTTP 200 |
| Redémarrage d'un service | Retour automatique et journal propre |
| Alerte OKA de test | Reçue dans CCME/le canal configuré |
| Requête depuis une IP non autorisée | Refusée |
| Rollback sur snapshot | Service restauré et validé |

## 5. Transfert et clôture

- [ ] Procédure d'exploitation remise au client
- [ ] Comptes, certificats et dates d'expiration documentés
- [ ] Session de formation ou de transfert de compétences réalisée
- [ ] Ticket de déploiement clôturé avec preuves et leçons
- [ ] Irritants produit remontés à la R&D via `lessons.md`
