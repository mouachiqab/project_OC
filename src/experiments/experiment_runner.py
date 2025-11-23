"""
Lancer les expériences pour les simulations
Auteurs: Abdelkarim & Marin
"""
import simpy
import json
import time
from pathlib import Path
from typing import Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from simulation.emergency_department import EmergencyDepartment
from optimization.optimizer_interface import create_optimizer

class ExperimentRunner:
    """Gère l'exécution des expériences de simulation"""
    
    def __init__(self, instance_path: str):
        """
        Args:
            instance_path: Chemin vers le fichier JSON de l'instance
        """
        with open(instance_path, 'r') as f:
            self.instance = json.load(f)
        
        self.instance_name = Path(instance_path).stem
        self.results = {}
    
    def run_single_replication(self, replication_id: int) -> Dict:
        """
        Exécute une seule réplication de la simulation
        
        Args:
            replication_id: Numéro de la réplication
        
        Returns:
            Résultats de la simulation
        """
        print(f"\nReplication {replication_id + 1}...")
        print("-" * 40)
        
        # Créer l'environnement SimPy
        env = simpy.Environment()
        
        # Créer l'optimiseur
        opt_config = self.instance['optimization']
        optimizer = create_optimizer(
            method=opt_config['method'],
            time_limit=opt_config['time_limit'],
            solver_name=opt_config.get('solver', 'chuffed' if opt_config['method'] == 'CP' else 'PULP_CBC_CMD')
        )
        
        # Créer le service des urgences
        resources = self.instance['resources']
        patient_flow = self.instance['patient_flow']
        
        ed = EmergencyDepartment(
            env=env,
            num_doctors=resources['num_doctors'],
            num_beds=resources['num_beds'],
            arrival_rate=patient_flow['arrival_rate'] / 24,  # Convertir en patients/heure
            optimization_interval=opt_config['interval'],
            optimizer=optimizer.optimize
        )
        
        # Lancer la simulation
        start_time = time.time()
        simulation_duration = self.instance['simulation']['duration']
        
        results = ed.run(simulation_duration)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Ajouter les métadonnées
        results['replication_id'] = replication_id
        results['elapsed_time'] = elapsed_time
        results['instance_name'] = self.instance_name
        
        print(f"Replication {replication_id + 1} completed in {elapsed_time:.2f}s")
        
        return results
    
    def run_experiment(self) -> Dict:
        """
        Exécute toutes les répétitions de l'expérience
        
        Returns:
            Résultats agrégés de toutes les répétitions
        """
        num_replications = self.instance['simulation']['replications']
        
        print(f"RUNNING EXPERIMENT: {self.instance_name}")
        print(f"Hospital: {self.instance['hospital']['name']}")
        print(f"Scenario: {self.instance['scenario']['name']}")
        print(f"Method: {self.instance['optimization']['method']}")
        print(f"Replications: {num_replications}")
        
        all_results = []
        
        for rep_id in range(num_replications):
            rep_results = self.run_single_replication(rep_id)
            all_results.append(rep_results)
        
        # Agréger les résultats
        aggregated_results = self._aggregate_results(all_results)
        
        return aggregated_results
    
    def _aggregate_results(self, results_list: list) -> Dict:
        """Agrège les résultats de toutes les répétitions"""
        import numpy as np
        
        aggregated = {
            'instance_name': self.instance_name,
            'hospital': self.instance['hospital'],
            'scenario': self.instance['scenario'],
            'optimization': self.instance['optimization'],
            'num_replications': len(results_list),
            'replications': results_list,
            'summary': {}
        }
        
        # Calculer les moyennes et écarts-types
        arrivals = [r['total_arrivals'] for r in results_list]
        treated = [r['total_treated'] for r in results_list]
        deteriorations = [r['total_deteriorations'] for r in results_list]
        elapsed_times = [r['elapsed_time'] for r in results_list]
        
        aggregated['summary'] = {
            'avg_arrivals': np.mean(arrivals),
            'avg_treated': np.mean(treated),
            'avg_deteriorations': np.mean(deteriorations),
            'avg_elapsed_time': np.mean(elapsed_times),
            'std_treated': np.std(treated),
        }
        
        return aggregated
    
    def save_results(self, output_dir: str):
        """Sauvegarde les résultats"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_file = output_path / f"{self.instance_name}_results.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
