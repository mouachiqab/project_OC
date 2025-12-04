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

## Exécution Complète 

### 1. Générer les instances
```bash
python scripts/generate_instances.py
```
**Résultat :** 6 fichiers JSON créés dans `data/instances/`

### 2. Lancer toutes les expériences
```bash
for instance in data/instances/*.json; do
    echo "▶ $(basename $instance)"
    python scripts/run_experiment.py --instance "$instance"
done
```

### 3. Vérifier les résultats
```bash
ls -lh data/results/
```

## Résultats Attendus

Chaque fichier `*_results.json` contient :
- **total_arrivals** : Nombre de patients arrivés
- **total_treated** : Nombre de patients traités
- **total_deteriorations** : Nombre de détériorations
- **discharged_patients** : Détails de chaque patient sorti
- **resource_stats** : Utilisation des médecins et lits

## Méthodes Comparées

- **Small/Large** : CP (Constraint Programming) avec MiniZinc/Chuffed
- **Medium** : MILP (Mixed Integer Linear Programming) avec PuLP/CBC

## Nettoyage

```bash
# Supprimer les fichiers générés
rm -f data/instances/*.json data/results/*.json
```


