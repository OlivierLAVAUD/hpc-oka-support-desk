# Diagnostic — TICKET-004

## Cause racine
Aucun enhancer de coût personnalisé n'existe pour ce client. L'enhancer standard
costs_demo.py utilise des tarifs par défaut (0,02 €/CPU, 0,04 €/GPU) et un pattern
de compte "contract_fusion_.*" qui ne correspond pas aux comptes étudiants du
client ("etudiant_.*").

## Checklist de vérifications
- [x] Enhancer costs_demo.py existe dans oka_dataenhancers/costs/
- [x] Contrat DataEnhancer respecté (params_model Pydantic, run, DataFrame in place)
- [x] Colonne réservée "Cost" utilisée (pas de préfixe Cust_)
- [x] Pattern regex de compte : re.compile() + str.match() sur la colonne Account
- [x] Toutes les colonnes modifiées sont documentées

## Preuves observées
- Fichier source : ../oka_dataenhancers/costs/costs_demo.py
- Params standards : CPU_HOUR_COST=0.02, GPU_HOUR_COST=0.04, GPU_PARTITION="gpu",
  DISC_ACCOUNT_CPU_HOURS_COST=0.01, DISC_ACCOUNT=r"contract_fusion_.*"
- Colonne modifiée : Cost (via oka_constants.COST)

## Impact client
Le client ne peut pas facturer ses utilisateurs avec ses propres tarifs, et la
réduction étudiante n'est pas appliquée.

## Diagnostic validé par l'ingénieur
- [x] Cause racine confirmée : enhancer personnalisé nécessaire
- [x] Checklist complétée
- [x] Preuves documentées
- [ ] Commentaire : Développement d'un custom_cost_enhancer.py basé sur
  costs_demo.py, avec paramètres adaptés.

**Ingénieur** : Support N2 | **Date** : 2026-10-13
