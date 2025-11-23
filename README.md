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
1. **Simulation + CP** : MiniZinc/OR-Tools
2. **Simulation + MILP** : PuLP/CBC

##  Références
Voir `docs/references.md`
