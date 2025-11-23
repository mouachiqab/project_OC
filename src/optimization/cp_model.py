"""
Interface Python pour le modèle CP MiniZinc
Auteur: Abdelkarim Mouachiq
"""
from minizinc import Instance, Model, Solver
from typing import List, Dict, Tuple, Optional
import numpy as np
from pathlib import Path

class CPOptimizer:
    """Optimiseur basé sur la Programmation par Contraintes"""
    
    def __init__(self, time_limit: int = 60, solver_name: str = 'chuffed'):
        """
        Args:
            time_limit: Limite de temps en secondes
            solver_name: Nom du solveur (chuffed, gecode, etc.)
        """
        self.time_limit = time_limit
        self.solver_name = solver_name
        self.model_path = Path(__file__).parent.parent.parent / 'models' / 'emergency_cp.mzn'
        
        # Charger le modèle MiniZinc
        try:
            self.model = Model(str(self.model_path))
            self.solver = Solver.lookup(solver_name)
        except Exception as e:
            print(f"Error loading MiniZinc model: {e}")
            self.model = None
            self.solver = None
    
    def optimize(self, state: Dict) -> List[Tuple[int, int, int]]:
        """
        Résout le problème d'affectation avec CP
        
        Args:
            state: État actuel du système
                - waiting_patients: Liste des patients en attente
                - available_doctors: Liste des médecins disponibles
                - available_beds: Liste des civières disponibles
                - current_time: Temps actuel
        
        Returns:
            Liste de tuples (patient_id, doctor_id, bed_id)
        """
        if self.model is None or self.solver is None:
            return []
        
        waiting_patients = state['waiting_patients']
        available_doctors = state['available_doctors']
        available_beds = state['available_beds']
        current_time = state['current_time']
        
        n_patients = len(waiting_patients)
        n_doctors = len(available_doctors)
        n_beds = len(available_beds)
        
        if n_patients == 0 or n_doctors == 0 or n_beds == 0:
            return []
        
        # Préparer les données pour MiniZinc
        priority_values = [p.priority.value for p in waiting_patients]
        wait_times = [int(p.get_wait_time(current_time)) for p in waiting_patients]
        max_wait_times = [int(p.get_max_wait_time()) for p in waiting_patients]
        treatment_times = [int(p.treatment_duration) for p in waiting_patients]
        
        try:
            # Créer une instance du modèle
            instance = Instance(self.solver, self.model)
            
            # Assigner les paramètres
            instance['n_patients'] = n_patients
            instance['n_doctors'] = n_doctors
            instance['n_beds'] = n_beds
            instance['priority'] = priority_values
            instance['wait_time'] = wait_times
            instance['max_wait_time'] = max_wait_times
            instance['treatment_time'] = treatment_times
            instance['current_time'] = int(current_time)
            
            # Résoudre avec timeout
            result = instance.solve(timeout=self.time_limit)
            
            if result.solution is not None:
                # Extraire les affectations
                x = result['x']  # Affectations médecins
                y = result['y']  # Affectations civières
                z = result['z']  # Patients traités
                
                assignments = []
                for i in range(n_patients):
                    if z[i] == 1:  # Patient traité
                        patient = waiting_patients[i]
                        doctor_idx = x[i] - 1  
                        bed_idx = y[i] - 1
                        
                        if 0 <= doctor_idx < n_doctors and 0 <= bed_idx < n_beds:
                            actual_doctor = available_doctors[doctor_idx].id
                            actual_bed = available_beds[bed_idx].id
                            assignments.append((patient.id, actual_doctor, actual_bed))
                
                print(f"CP Solver: Found solution with {len(assignments)} assignments")
                print(f"  Objective: {result['objective']}")
                print(f"  Solve time: {result.statistics.get('time', 'N/A')}s")
                
                return assignments
            else:
                print(f"CP Solver: No solution found")
                return []
                
        except Exception as e:
            print(f"CP Solver error: {e}")
            return []
    
    def get_solver_stats(self, result) -> Dict:
        """Extrait les statistiques du solveur"""
        if result.solution is None:
            return {'status': 'UNSATISFIABLE'}
        
        return {
            'status': result.status.name,
            'objective': result.get('objective', None),
            'solve_time': result.statistics.get('time', None),
            'nodes': result.statistics.get('nodes', None),
            'failures': result.statistics.get('failures', None),
        }
