"""
Visualisation des résultats d'expériences
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict
import pandas as pd

# Style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

class ResultsPlotter:
    """Génère des visualisations des résultats d'expériences"""
    
    def __init__(self, results_dir: str):
        """
        Args:
            results_dir: Répertoire contenant les fichiers de résultats JSON
        """
        self.results_dir = Path(results_dir)
        self.results = self._load_all_results()
    
    def _load_all_results(self) -> List[Dict]:
        """Charge tous les fichiers de résultats"""
        results = []
        
        for json_file in self.results_dir.glob('*_results.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    results.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        print(f"Loaded {len(results)} result files")
        return results
    
    def plot_waiting_times_evolution(self, output_path: str = None):
        """Graphique : évolution des temps d'attente au cours de la simulation"""
        fig, axes = plt.subplots(3, 2, figsize=(16, 18))
        fig.suptitle('Évolution des Temps d\'Attente par Type d\'Hôpital', fontsize=16, fontweight='bold')
        
        hospital_types = ['small', 'medium', 'large']
        scenarios = ['baseline', 'peak_flu']
        
        plot_idx = 0
        for hospital_type in hospital_types:
            for scenario in scenarios:
                ax = axes[plot_idx // 2, plot_idx % 2]
                
                # Filtrer les résultats
                matching = [r for r in self.results 
                           if hospital_type in r['instance_name'] 
                           and scenario in r['instance_name']]
                
                if not matching:
                    plot_idx += 1
                    continue
                
                for result in matching:
                    method = result['optimization']['method']
                    
                    # Moyenner les répétitions
                    all_wait_times = []
                    common_times = None
                    
                    for replication in result['replications']:
                        metrics = replication['metrics']
                        if common_times is None:
                            common_times = metrics['time']
                        all_wait_times.append(metrics['avg_wait_time'])
                    
                    # Calculer la moyenne des répétitions
                    avg_wait_times = np.mean(all_wait_times, axis=0)
                    
                    # Couleurs fixes: CP=bleu, MILP=rouge
                    color = '#3498db' if method == 'CP' else '#e74c3c'
                    marker = 'o' if method == 'CP' else 's'
                    
                    label = f"{method}"
                    ax.plot(common_times, avg_wait_times, linewidth=2, label=label, 
                           color=color, marker=marker, markersize=4, markevery=5)
                
                ax.set_xlabel('Temps de simulation (minutes)', fontweight='bold')
                ax.set_ylabel('Temps d\'attente moyen (minutes)', fontweight='bold')
                ax.set_title(f'{hospital_type.title()} - {scenario.replace("_", " ").title()}', fontsize=12)
                ax.legend(loc='best')
                ax.grid(True, alpha=0.3)
                
                plot_idx += 1
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot: {output_path}")
        else:
            plt.show()
    
    def plot_comparison_cp_vs_milp(self, output_path: str = None):
        """Graphique : comparaison CP vs MILP"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Comparaison CP vs MILP', fontsize=16, fontweight='bold')
        
        metrics_to_compare = [
            ('avg_treated', 'Patients Traités (moyenne)'),
            ('avg_deteriorations', 'Détériorations (moyenne)'),
            ('avg_elapsed_time', 'Temps d\'Exécution (secondes)')
        ]
        
        for idx, (metric, title) in enumerate(metrics_to_compare):
            ax = axes[idx]
            
            # Créer un dictionnaire pour aligner correctement CP et MILP
            data_by_instance = {}
            
            for result in self.results:
                method = result['optimization']['method']
                value = result['summary'].get(metric, 0)
                instance_name = result['instance_name']
                
                # Créer une clé unique pour l'instance (sans la méthode)
                instance_key = '_'.join(instance_name.split('_')[:-1])
                
                if instance_key not in data_by_instance:
                    data_by_instance[instance_key] = {'CP': 0, 'MILP': 0}
                
                data_by_instance[instance_key][method] = value
            
            # Trier par taille d'hôpital et scénario
            hospital_order = {'small': 0, 'medium': 1, 'large': 2}
            scenario_order = {'baseline': 0, 'peak': 1}
            
            sorted_instances = sorted(
                data_by_instance.keys(),
                key=lambda x: (
                    hospital_order.get(x.split('_')[0], 999),
                    scenario_order.get(x.split('_')[1], 999)
                )
            )
            
            # Extraire les valeurs alignées
            cp_values = [data_by_instance[inst]['CP'] for inst in sorted_instances]
            milp_values = [data_by_instance[inst]['MILP'] for inst in sorted_instances]
            
            # Créer labels lisibles
            labels = []
            for inst in sorted_instances:
                parts = inst.split('_')
                hosp = parts[0][:3].capitalize()
                scen = parts[1][:4].capitalize()
                labels.append(f"{hosp}-{scen}")
            
            # Tracer
            x = np.arange(len(labels))
            width = 0.35
            
            ax.bar(x - width/2, cp_values, width, label='CP', color='#3498db')
            ax.bar(x + width/2, milp_values, width, label='MILP', color='#e74c3c')
            
            ax.set_xlabel('Instance', fontweight='bold')
            ax.set_ylabel(metric.replace('_', ' ').title(), fontweight='bold')
            ax.set_title(title)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot: {output_path}")
        else:
            plt.show()
    
    def plot_resource_utilization(self, output_path: str = None):
        """Graphique : utilisation des ressources"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Utilisation des Ressources', fontsize=16, fontweight='bold')
        
        # Dictionnaire pour organiser les données
        data_dict = {}
        
        for result in self.results:
            if 'baseline' not in result['instance_name']:
                continue
            
            # Calculer la moyenne sur toutes les réplications
            doc_utils = []
            bed_utils = []
            
            for replication in result['replications']:
                resource_stats = replication['resource_stats']
                doc_utils.append(float(np.mean(resource_stats['doctors']['utilization_rates'])))
                
                # Pour les civières, calculer seulement sur celles utilisées (> 0)
                bed_rates = resource_stats['beds']['occupancy_rates']
                used_beds = [rate for rate in bed_rates if rate > 0]
                bed_util_avg = np.mean(used_beds) if used_beds else 0
                bed_utils.append(float(bed_util_avg))
            
            hospital_type = result['hospital']['type']
            method = result['optimization']['method']
            
            key = f"{hospital_type}_{method}"
            data_dict[key] = {
                'doctor_util': np.mean(doc_utils),
                'bed_util': np.mean(bed_utils),
                'hospital': hospital_type,
                'method': method
            }
        
        # Trier les données : small, medium, large, puis CP avant MILP
        hospital_order = {'small': 0, 'medium': 1, 'large': 2}
        method_order = {'CP': 0, 'MILP': 1}
        
        sorted_keys = sorted(
            data_dict.keys(),
            key=lambda x: (
                hospital_order.get(data_dict[x]['hospital'], 999),
                method_order.get(data_dict[x]['method'], 999)
            )
        )
        
        # Extraire les données triées
        doctor_util = []
        bed_util = []
        instance_labels = []
        colors_doc = []
        colors_bed = []
        
        for key in sorted_keys:
            data = data_dict[key]
            doctor_util.append(data['doctor_util'])
            bed_util.append(data['bed_util'])
            
            hosp = data['hospital'][:3].capitalize()
            method = data['method']
            instance_labels.append(f"{hosp}-{method}")
            
            # Couleurs : CP=bleu, MILP=rouge
            color = '#3498db' if method == 'CP' else '#e74c3c'
            colors_doc.append(color)
            colors_bed.append(color)
        
        # Graphique médecins
        ax1 = axes[0]
        ax1.barh(instance_labels, doctor_util, color=colors_doc)
        ax1.set_xlabel('Taux d\'Utilisation (%)', fontweight='bold')
        ax1.set_title('Utilisation des Médecins')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Graphique civières
        ax2 = axes[1]
        ax2.barh(instance_labels, bed_util, color=colors_bed)
        ax2.set_xlabel('Taux d\'Occupation (%)', fontweight='bold')
        ax2.set_title('Occupation des Civières (utilisees)')
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot: {output_path}")
        else:
            plt.show()
    
    def plot_scenario_comparison(self, output_path: str = None):
        """Graphique : comparaison des scénarios"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Créer un DataFrame pour faciliter le tracé
        data = []
        
        for result in self.results:
            hospital_type = result['hospital']['type']
            scenario = result['scenario']['name']
            method = result['optimization']['method']
            avg_treated = result['summary']['avg_treated']
            
            data.append({
                'Hospital': hospital_type,
                'Scenario': scenario,
                'Method': method,
                'Patients_Treated': avg_treated
            })
        
        df = pd.DataFrame(data)
        
        # Pivot pour le graphique
        pivot = df.pivot_table(
            values='Patients_Treated',
            index=['Hospital', 'Scenario'],
            columns='Method',
            aggfunc='mean'
        )
        
        pivot.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c'])
        
        ax.set_xlabel('Hôpital - Scénario', fontweight='bold')
        ax.set_ylabel('Patients Traités (moyenne)', fontweight='bold')
        ax.set_title('Comparaison des Performances par Scénario', fontsize=14, fontweight='bold')
        ax.legend(title='Méthode')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot: {output_path}")
        else:
            plt.show()
    
    def generate_all_plots(self, output_dir: str = 'data/results/plots'):
        """Génère tous les graphiques"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        plots = [
            ('waiting_times_evolution', self.plot_waiting_times_evolution),
            ('cp_vs_milp_comparison', self.plot_comparison_cp_vs_milp),
            ('resource_utilization', self.plot_resource_utilization),
            ('scenario_comparison', self.plot_scenario_comparison)
        ]
        
        for name, plot_func in plots:
            print(f"\nGenerating: {name}...")
            try:
                plot_func(output_path / f"{name}.png")
            except Exception as e:
                print(f"Error generating {name}: {e}")
        

    
    def generate_summary_table(self, output_path: str = None):
        """Génère un tableau récapitulatif des résultats"""
        summary_data = []
        
        for result in self.results:
            summary_data.append({
                'Instance': result['instance_name'],
                'Hospital': result['hospital']['type'],
                'Scenario': result['scenario']['name'],
                'Method': result['optimization']['method'],
                'Avg_Arrivals': result['summary']['avg_arrivals'],
                'Avg_Treated': result['summary']['avg_treated'],
                'Avg_Deteriorations': result['summary']['avg_deteriorations'],
                'Avg_Time(s)': f"{result['summary']['avg_elapsed_time']:.2f}",
                'Std_Treated': f"{result['summary']['std_treated']:.2f}"
            })
        
        df = pd.DataFrame(summary_data)
        
        if output_path:
            df.to_csv(output_path, index=False)
            print(f"Summary table saved to: {output_path}")
        

        print(df.to_string(index=False))
        
        return df
