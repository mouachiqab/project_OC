#!/usr/bin/env python3
"""
Script principal pour lancer les expériences
Auteurs: Abdelkarim & Marin
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from experiments.experiment_runner import ExperimentRunner
from data_generation.instance_generator import InstanceGenerator

def run_from_instance(instance_path: str, output_dir: str):
    """Lance une expérience depuis un fichier d'instance"""
    runner = ExperimentRunner(instance_path)
    results = runner.run_experiment()
    runner.results = results
    runner.save_results(output_dir)
    
    return results

def run_from_config(config_path: str, scenario: str, output_dir: str):
    """Lance une expérience depuis une config et un scénario"""
    # Générer l'instance
    generator = InstanceGenerator(config_path)
    instance = generator.generate_scenario_instance(scenario)
    
    # Sauvegarder temporairement
    temp_instance = Path(output_dir) / 'temp_instance.json'
    generator.save_instance(instance, str(temp_instance))
    
    # Lancer l'expérience
    results = run_from_instance(str(temp_instance), output_dir)
    
    # Nettoyer
    temp_instance.unlink()
    
    return results

def run_all_instances(instances_dir: str, output_dir: str):
    """Lance toutes les instances disponibles"""
    instances_path = Path(instances_dir)
    instance_files = list(instances_path.glob('*.json'))
    
    if not instance_files:
        print(f"No instances found in {instances_dir}")
        return
    
    print(f"Found {len(instance_files)} instances to run")

    all_results = []
    
    for instance_file in instance_files:
        print(f"\nRunning: {instance_file.name}")
        
        results = run_from_instance(str(instance_file), output_dir)
        all_results.append(results)
    

    print(f"ALL EXPERIMENTS COMPLETED")
    print(f"Total: {len(all_results)} experiments")
    print(f"Results in: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Run emergency department experiments')
    
    parser.add_argument('--instance', type=str, help='Path to instance JSON file')
    parser.add_argument('--config', type=str, help='Path to config YAML file')
    parser.add_argument('--scenario', type=str, help='Scenario name (requires --config)')
    parser.add_argument('--all', action='store_true', help='Run all instances')
    parser.add_argument('--output', type=str, default='data/results', help='Output directory')
    
    args = parser.parse_args()
    
    if args.all:
        run_all_instances('data/instances', args.output)
    elif args.instance:
        run_from_instance(args.instance, args.output)
    elif args.config and args.scenario:
        run_from_config(args.config, args.scenario, args.output)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
