# Optimisation des Urgences au Québec

Projet de recherche opérationnelle comparant deux méthodes d'optimisation (Programmation par Contraintes et Programmation Linéaire en Nombres Entiers) pour l'affectation des ressources dans les services d'urgence hospitaliers québécois.

## Équipe

- Abdelkarim Mouachiq 
- Marin Kerboriou 

Université Laval - Automne 2025

## Objectif

Réduire les temps d'attente et maximiser le nombre de patients traités dans les services d'urgence en optimisant l'affectation des médecins et des civières. Le projet compare les performances de deux approches d'optimisation sur trois tailles d'hôpitaux et deux scénarios de charge.

## Architecture du Projet

```
project_OC/
├── config/              # Configurations des hôpitaux (small, medium, large)
├── data/
│   ├── instances/       # Instances générées pour les expériences
│   └── results/         # Résultats des simulations et graphiques
├── models/              # Modèle MiniZinc pour la programmation par contraintes
├── src/
│   ├── data_generation/ # Génération d'instances expérimentales
│   ├── experiments/     # Orchestration des expériences
│   ├── optimization/    # Modèles CP et MILP
│   ├── simulation/      # Simulation SimPy du service d'urgence
│   └── visualization/   # Génération de graphiques et analyses
└── scripts/             # Scripts d'exécution et d'analyse
```

## Installation

### Prérequis

- Python 3.11 ou supérieur
- MiniZinc 2.8+ (pour la programmation par contraintes)
- CBC solver (inclus avec PuLP pour la programmation linéaire)

### Installation de Python et des dépendances

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Installation de MiniZinc

Télécharger et installer MiniZinc depuis: https://www.minizinc.org/software.html

## Utilisation

### Génération des instances expérimentales

```bash
python scripts/generate_instances.py
```

Cela génère 12 instances (3 hôpitaux × 2 scénarios × 2 méthodes) dans `data/instances/`.

### Lancement des expériences

Pour lancer toutes les expériences (12 scénarios avec 5 réplications chacun):

```bash
./scripts/run_all_comparisons.sh
```

Les résultats sont sauvegardés dans `data/results/`.

Pour lancer une expérience spécifique:

```bash
python scripts/run_experiment.py --instance data/instances/medium_baseline_CP.json
```

### Analyse des résultats

Générer les tableaux comparatifs et les graphiques:

```bash
python scripts/compare_cp_milp.py
python scripts/analyze_results.py
```

Les graphiques sont sauvegardés dans `data/results/plots/`:
- `cp_vs_milp_comparison.png` - Comparaison des patients traités et temps d'exécution
- `resource_utilization.png` - Utilisation des médecins et civières
- `scenario_comparison.png` - Impact des scénarios baseline vs pic grippal
- `waiting_times_evolution.png` - Évolution des temps d'attente au cours de la simulation

## Méthodologie

### Configurations d'hôpitaux

Trois tailles d'hôpitaux sont modélisées:

- **Petit hôpital**: 3 médecins, 25 civières, 40 patients/jour
- **Hôpital moyen**: 6 médecins, 50 civières, 120 patients/jour
- **Grand hôpital (CHU)**: 12 médecins, 120 civières, 250 patients/jour

### Scénarios

- **Baseline**: Journée normale (taux d'arrivée standard)
- **Pic grippal**: Augmentation de 30% des arrivées avec davantage de cas urgents

### Méthodes d'optimisation

**1. Programmation par Contraintes (CP)**
- Solveur: Chuffed (via MiniZinc)
- Modèle: `models/emergency_cp.mzn`
- Optimise l'affectation en considérant les priorités et les temps d'attente

**2. Programmation Linéaire en Nombres Entiers (MILP)**
- Solveur: CBC (via PuLP)
- Modèle: `src/optimization/milp_model.py`
- Formulation linéaire avec variables binaires pour les affectations

### Simulation

La simulation utilise SimPy pour modéliser le flux de patients:
- Arrivées selon un processus de Poisson
- 5 niveaux de priorité 
- Temps de traitement variables selon la priorité
- Détérioration possible si temps d'attente dépasse le seuil
- Optimisation toutes les 30 minutes (période d'intervention)

### Validation

Chaque scénario est exécuté avec 5 réplications pour tenir compte de la variance stochastique. Les métriques collectées incluent:
- Nombre de patients traités
- Temps d'attente moyens
- Nombre de détériorations
- Taux d'utilisation des ressources
- Temps d'exécution des optimisations



