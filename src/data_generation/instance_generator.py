"""
Générateur d'instances pour les expériences
"""
import yaml
import numpy as np
from pathlib import Path
from typing import Dict, List
import json

class InstanceGenerator:
    """Génère des instances de test pour les expériences"""
    
    def __init__(self, config_path: str):
        """Initialise le générateur d'instances"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.hospital_type = self.config['hospital']['type']
        self.rng = np.random.RandomState(42)
    
    def generate_scenario_instance(self, scenario_name: str, method: str) -> Dict:
        """Génère une instance pour un scénario et une méthode d'optimisation donnés"""
        scenario = self.config['scenarios'][scenario_name]
        
        optimization_config = {
            'method': method,
            'interval': self.config['optimization']['interval'],
            'time_limit': self.config['optimization']['time_limit'],
            'solver': self.config['optimization']['methods'][method]['solver']
        }
        
        instance = {
            'hospital': self.config['hospital'],
            'resources': self.config['resources'].copy(),
            'patient_flow': self.config['patient_flow'].copy(),
            'optimization': optimization_config,
            'simulation': self.config['simulation'],
            'scenario': scenario
        }
        
        if 'arrival_multiplier' in scenario:
            instance['patient_flow']['arrival_rate'] *= scenario['arrival_multiplier']
        
        if 'resource_reduction' in scenario:
            for resource, value in scenario['resource_reduction'].items():
                instance['resources'][resource] = value
        
        if 'priority_shift' in scenario:
            for priority, prob in scenario['priority_shift'].items():
                instance['patient_flow']['priority_distribution'][priority] = prob
        
        return instance
    
    def save_instance(self, instance: Dict, output_path: str):
        """Sauvegarde une instance au format JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(instance, f, indent=2)
        
        print(f"Instance saved to: {output_path}")
    
    def generate_all_scenarios(self, output_dir: str):
        """Génère toutes les instances pour tous les scénarios ET toutes les méthodes"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        methods = list(self.config['optimization']['methods'].keys())
        
        count = 0
        for scenario_name in self.config['scenarios'].keys():
            for method in methods:
                instance = self.generate_scenario_instance(scenario_name, method)
                
                filename = f"{self.hospital_type}_{scenario_name}_{method}.json"
                self.save_instance(instance, output_path / filename)
                count += 1
        
