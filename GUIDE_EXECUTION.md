# Guide d'Exécution 

## Installation 

```bash
# 1. Installer MiniZinc
brew install minizinc

# 2. Activer l'environnement virtuel
source venv/bin/activate

# 3. Vérifier les packages
pip list | grep -E "(simpy|pulp|minizinc|numpy|pandas)"
```

## Exécution Complète 🚀

### 1. Générer les instances
```bash
python scripts/generate_instances.py
```
**Résultat :** 12 fichiers JSON créés dans `data/instances/`
- 3 hôpitaux × 2 scénarios × 2 méthodes (CP et MILP)

### 2. Lancer toutes les expériences (RECOMMANDÉ)
```bash
./scripts/run_all_comparisons.sh
```
**Durée estimée :** 10-15 minutes pour les 12 instances

**OU manuellement :**
```bash
for instance in data/instances/*.json; do
    echo "▶ $(basename $instance)"
    python scripts/run_experiment.py --instance "$instance"
done
```

### 3. Comparer CP vs MILP
```bash
python scripts/compare_cp_milp.py
```
**Résultat :** Tableau comparatif avec :
- Patients traités par méthode
- Temps d'exécution
- Ratio de vitesse MILP vs CP
- Fichiers CSV générés

### 4. Visualiser les résultats
```bash
python scripts/analyze_results.py
```
**Résultat :** 4 graphiques PNG + tableau récapitulatif

## Résultats Attendus

Chaque fichier `*_results.json` contient :
- **total_arrivals** : Nombre de patients arrivés
- **total_treated** : Nombre de patients traités
- **total_deteriorations** : Nombre de détériorations
- **discharged_patients** : Détails de chaque patient sorti
- **resource_stats** : Utilisation des médecins et lits

## Instances Générées (12 au total)

Pour chaque hôpital (small, medium, large) :
- `{hospital}_baseline_CP.json` - Journée normale avec CP
- `{hospital}_baseline_MILP.json` - Journée normale avec MILP
- `{hospital}_peak_flu_CP.json` - Pic grippal avec CP
- `{hospital}_peak_flu_MILP.json` - Pic grippal avec MILP

**Objectif** : Comparer les performances de CP vs MILP sur les mêmes configurations

## Nettoyage

```bash
# Supprimer les fichiers générés
rm -f data/instances/*.json data/results/*.json
```


