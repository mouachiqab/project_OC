# Optimisation des Urgences Québécoises

##  Objectif
Optimiser l'affectation des ressources dans les urgences pour réduire les temps d'attente.

##  Équipe
- **Abdelkarim Mouachiq** (537 396 376)
- **Marin Kerbouriou** (537 396 202)

##  Architecture
```
project_OC/
├── config/           # Configurations des hôpitaux
├── data/            # Données et résultats
├── src/             # Code source
│   ├── simulation/  # Simulation SimPy
│   ├── optimization/# Modèles CP et MILP
│   └── ...
├── models/          # Modèles MiniZinc
└── scripts/         # Scripts d'exécution
```

##  Installation

### Prérequis
- Python 3.11+
- MiniZinc 2.8+
- CBC solver

### Installation des dépendances
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

##  Utilisation
```bash
# Générer des instances
python scripts/generate_instances.py

# Lancer une expérience
python scripts/run_experiment.py --config config/small_hospital.yaml
```

##  Approches
**Objectif** : Comparer deux méthodes d'optimisation sur les mêmes instances

1. **CP (Constraint Programming)** : MiniZinc avec solveur Chuffed
2. **MILP (Mixed Integer Linear Programming)** : PuLP avec solveur CBC

Chaque configuration d'hôpital est testée avec **les deux méthodes** pour comparer :
- Nombre de patients traités
- Temps d'exécution
- Qualité des affectations

##  Références
Voir `docs/references.md`
