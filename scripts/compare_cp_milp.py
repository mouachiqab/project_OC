#!/usr/bin/env python3
"""
Script de comparaison directe CP vs MILP
Auteurs: Abdelkarim & Marin

Analyse les résultats et génère un tableau comparatif
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
import pandas as pd

def load_results(results_dir: str = 'data/results'):
    """Charge tous les résultats"""
    results_path = Path(results_dir)
    results = []
    
    for json_file in results_path.glob('*_results.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            print(f"Erreur lecture {json_file}: {e}")
    
    return results

def extract_comparison_data(results):
    """Extrait les données pour la comparaison"""
    data = []
    
    for result in results:
        instance_name = result['instance_name']
        
        # Parser le nom: {hospital}_{scenario}_{method}
        parts = instance_name.split('_')
        if len(parts) >= 3:
            hospital = parts[0]
            scenario = parts[1]
            method = parts[2]
        else:
            continue
        
        summary = result.get('summary', {})
        
        data.append({
            'Hôpital': hospital.upper(),
            'Scénario': scenario.replace('_', ' ').title(),
            'Méthode': method,
            'Patients Arrivés': f"{summary.get('avg_arrivals', 0):.1f}",
            'Patients Traités': f"{summary.get('avg_treated', 0):.1f}",
            'Détériorations': f"{summary.get('avg_deteriorations', 0):.1f}",
            'Temps Exec (s)': f"{summary.get('avg_elapsed_time', 0):.2f}",
            'Répétitions': result.get('num_replications', 0)
        })
    
    return data

def create_comparison_table(data):
    """Crée un tableau de comparaison"""
    df = pd.DataFrame(data)
    
    # Trier par hôpital, scénario, méthode
    df = df.sort_values(['Hôpital', 'Scénario', 'Méthode'])
    
    return df

def calculate_improvements(df):
    """Calcule les améliorations CP vs MILP"""
    improvements = []
    
    hospitals = df['Hôpital'].unique()
    scenarios = df['Scénario'].unique()
    
    for hospital in hospitals:
        for scenario in scenarios:
            subset = df[(df['Hôpital'] == hospital) & (df['Scénario'] == scenario)]
            
            if len(subset) != 2:
                continue
            
            cp_row = subset[subset['Méthode'] == 'CP']
            milp_row = subset[subset['Méthode'] == 'MILP']
            
            if len(cp_row) == 0 or len(milp_row) == 0:
                continue
            
            cp_treated = float(cp_row['Patients Traités'].values[0])
            milp_treated = float(milp_row['Patients Traités'].values[0])
            
            cp_time = float(cp_row['Temps Exec (s)'].values[0])
            milp_time = float(milp_row['Temps Exec (s)'].values[0])
            
            # Calcul des différences
            treated_diff = milp_treated - cp_treated
            treated_pct = (treated_diff / cp_treated * 100) if cp_treated > 0 else 0
            
            time_diff = milp_time - cp_time
            time_ratio = (cp_time / milp_time) if milp_time > 0 else 0
            
            improvements.append({
                'Hôpital': hospital,
                'Scénario': scenario,
                'CP Traités': cp_treated,
                'MILP Traités': milp_treated,
                'Différence': f"{treated_diff:+.1f}",
                'Amélioration (%)': f"{treated_pct:+.1f}%",
                'CP Temps (s)': f"{cp_time:.2f}",
                'MILP Temps (s)': f"{milp_time:.2f}",
                'Ratio Vitesse': f"{time_ratio:.1f}x"
            })
    
    return pd.DataFrame(improvements)

def main():
    print("=" * 80)
    print("COMPARAISON CP vs MILP")
    print("=" * 80)
    print()
    
    # Charger les résultats
    results = load_results()
    
    if not results:
        print("❌ Aucun résultat trouvé dans data/results/")
        print("   Lancez d'abord: ./scripts/run_all_comparisons.sh")
        sys.exit(1)
    
    print(f"✅ {len(results)} résultats chargés")
    print()
    
    # Extraire les données
    data = extract_comparison_data(results)
    df = create_comparison_table(data)
    
    # Afficher le tableau complet
    print("📊 TABLEAU COMPLET DES RÉSULTATS")
    print("-" * 80)
    print(df.to_string(index=False))
    print()
    
    # Sauvegarder en CSV
    output_csv = Path('data/results/comparison_cp_milp.csv')
    df.to_csv(output_csv, index=False)
    print(f"💾 Tableau sauvegardé: {output_csv}")
    print()
    
    # Calculer les améliorations
    if len(data) >= 2:
        improvements_df = calculate_improvements(df)
        
        if not improvements_df.empty:
            print("📈 ANALYSE COMPARATIVE (MILP vs CP)")
            print("-" * 80)
            print(improvements_df.to_string(index=False))
            print()
            
            # Sauvegarder
            improvements_csv = Path('data/results/improvements_analysis.csv')
            improvements_df.to_csv(improvements_csv, index=False)
            print(f"💾 Analyse sauvegardée: {improvements_csv}")
            print()
    
    # Résumé global
    print("🎯 RÉSUMÉ GLOBAL")
    print("-" * 80)
    
    cp_results = df[df['Méthode'] == 'CP']
    milp_results = df[df['Méthode'] == 'MILP']
    
    if not cp_results.empty and not milp_results.empty:
        avg_cp_time = cp_results['Temps Exec (s)'].apply(lambda x: float(x)).mean()
        avg_milp_time = milp_results['Temps Exec (s)'].apply(lambda x: float(x)).mean()
        
        print(f"CP   - Temps moyen: {avg_cp_time:.2f}s")
        print(f"MILP - Temps moyen: {avg_milp_time:.2f}s")
        print(f"MILP est {avg_cp_time/avg_milp_time:.1f}× plus rapide en moyenne")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
