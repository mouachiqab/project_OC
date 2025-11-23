"""
Générateur d'instances pour les expériences
Auteurs: Abdelkarim & Marin
"""
import yaml
import numpy as np
from pathlib import Path
from typing import Dict, List
import json

class InstanceGenerator:
    """Génère des instances de test pour les expériences"""
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: Chemin vers le fichier de configuration YAML
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.hospital_type = self.config['hospital']['type']
        self.rng = np.random.RandomState(42)  # Pour reproductibilité
    
    def generate_scenario_instance(self, scenario_name: str) -> Dict:
        """
        Génère une instance pour un scénario donné
        
        Args:
            scenario_name: Nom du scénario (baseline, peak_flu, etc.)
        
        Returns:
            Dictionnaire avec les paramètres de l'instance
        """
        scenario = self.config['scenarios'][scenario_name]
        
        instance = {
            'hospital': self.config['hospital'],
            'resources': self.config['resources'].copy(),
            'patient_flow': self.config['patient_flow'].copy(),
            'optimization': self.config['optimization'],
            'simulation': self.config['simulation'],
            'scenario': scenario
        }
        
        # Appliquer les modifications du scénario
        if 'arrival_multiplier' in scenario:
            instance['patient_flow']['arrival_rate'] *= scenario['arrival_multiplier']
        
        if 'resource_reduction' in scenario:
            for resource, value in scenario['resource_reduction'].items():
                instance['resources'][resource] = value
        
        if 'priority_shift' in scenario:
            # Ajuster la distribution des priorités
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
        """Génère toutes les instances pour tous les scénarios"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for scenario_name in self.config['scenarios'].keys():
            instance = self.generate_scenario_instance(scenario_name)
            
            filename = f"{self.hospital_type}_{scenario_name}.json"
            self.save_instance(instance, output_path / filename)
        
        print(f"Generated {len(self.config['scenarios'])} instances for {self.hospital_type}")
