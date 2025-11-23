#!/usr/bin/env python3
"""
Script pour générer toutes les instances d'expérimentation
Auteurs: Abdelkarim & Marin
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_generation.instance_generator import InstanceGenerator

def main():
    """Génère toutes les instances"""
    
    config_dir = Path(__file__).parent.parent / 'config'
    output_dir = Path(__file__).parent.parent / 'data' / 'instances'
    
    # Configurations à traiter
    configs = [
        'small_hospital.yaml',
        'medium_hospital.yaml',
        'large_hospital.yaml'
    ]
    
    print("="*60)
    print("GENERATING EXPERIMENTAL INSTANCES")
    print("="*60)
    
    for config_file in configs:
        config_path = config_dir / config_file
        
        if not config_path.exists():
            print(f"Warning: {config_file} not found, skipping...")
            continue
        
        print(f"\nProcessing: {config_file}")
        
        generator = InstanceGenerator(str(config_path))
        generator.generate_all_scenarios(str(output_dir))

    print("GENERATION COMPLETE")
    print(f"Instances saved in: {output_dir}")

if __name__ == '__main__':
    main()
