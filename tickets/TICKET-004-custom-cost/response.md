# Réponse client — TICKET-004

## Destinataire
Pierre Martin — Université

## Objet
Data Enhancer de coût personnalisé avec réduction étudiante

## Corps du message

Bonjour Pierre,

Nous faisons suite à votre demande concernant un calcul de coût avec tarifs
personnalisés et réduction pour les comptes étudiants.

### Cause identifiée
L'enhancer standard `costs_demo.py` utilise des tarifs par défaut (0,02 €/CPU,
0,04 €/GPU) et un pattern de compte "contract_fusion_.*" qui ne correspond pas
à vos comptes étudiants ("etudiant_.*").

### Solution apportée
Nous avons développé un enhancer `custom_cost_enhancer.py` avec les paramètres
suivants :
- Tarif CPU : 0,015 €/heure-core
- Tarif GPU : 0,035 €/heure-GPU (partition "gpu")
- Réduction étudiante : 0,0075 €/heure-core sur comptes "etudiant_*"

L'enhancer respecte le contrat OKA DataEnhancer :
- `params_model` Pydantic avec valeurs par défaut
- `run(self, data, **kwargs) -> pd.DataFrame` modifiant le DataFrame in place
- Colonne réservée "Cost" utilisée (pas de préfixe Cust_)
- Pattern de compte avec `re.compile()` et `str.match()`

### Preuve de résolution
L'enhancer est prêt à être importé dans OKA. Il ajoutera une colonne "Cost"
à chaque job, avec les tarifs et la réduction étudiante appliqués.

### Prévention
Tous les champs ont des valeurs par défaut : l'enhancer fonctionne sans
configuration utilisateur. Vous pouvez ajuster les tarifs via l'interface OKA
si nécessaire.

### Disponibilité
Notre équipe support reste à votre disposition pour toute question complémentaire.

Cordialement,
L'équipe support UCit

---

Validé par l'ingénieur : Support N2 | Date : 2026-10-14
Bandeau BROUILLON supprimé : oui
