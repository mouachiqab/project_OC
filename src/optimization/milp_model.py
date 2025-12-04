"""
Modèle PLNE pour l'optimisation des affectations
Auteur: Marin Kerbouriou
"""
from pulp import *
from typing import List, Dict, Tuple
import numpy as np

class MILPOptimizer:
    """Optimiseur basé sur la Programmation Linéaire en Nombres Entiers"""
    
    def __init__(self, time_limit: int = 60, solver_name: str = 'PULP_CBC_CMD'):
        """
        Args:
            time_limit: Limite de temps en secondes
            solver_name: Nom du solveur (PULP_CBC_CMD, CPLEX, GUROBI)
        """
        self.time_limit = time_limit
        self.solver_name = solver_name
        self.solver = None
        self._setup_solver()
    
    def _setup_solver(self):
        """Configure le solveur"""
        if self.solver_name == 'PULP_CBC_CMD':
            self.solver = PULP_CBC_CMD(timeLimit=self.time_limit, msg=0)
        elif self.solver_name == 'CPLEX':
            self.solver = CPLEX_CMD(timeLimit=self.time_limit, msg=0)
        elif self.solver_name == 'GUROBI':
            self.solver = GUROBI_CMD(timeLimit=self.time_limit, msg=0)
        else:
            self.solver = PULP_CBC_CMD(timeLimit=self.time_limit, msg=0)
    
    def optimize(self, state: Dict) -> List[Tuple[int, int, int]]:
        """
        Résout le problème d'affectation avec PLNE
        
        Args:
            state: État actuel du système
        """
        waiting_patients = state['waiting_patients']
        available_doctors = state['available_doctors']
        available_beds = state['available_beds']
        current_time = state['current_time']
        
        n_patients = len(waiting_patients)
        n_doctors = len(available_doctors)
        n_beds = len(available_beds)
        
        if n_patients == 0 or n_doctors == 0 or n_beds == 0:
            return []
        
        # Créer le problème
        prob = LpProblem("Emergency_Assignment", LpMinimize)
        
        #  VARIABLES DE DÉCISION 
        
        # x[i,j] = 1 si patient i assigné au médecin j
        x = {}
        for i in range(n_patients):
            for j in range(n_doctors):
                x[i, j] = LpVariable(f"x_{i}_{j}", cat='Binary')
        
        # y[i,k] = 1 si patient i assigné à la civière k
        y = {}
        for i in range(n_patients):
            for k in range(n_beds):
                y[i, k] = LpVariable(f"y_{i}_{k}", cat='Binary')
        
        # z[i] = 1 si patient i est traité
        z = {}
        for i in range(n_patients):
            z[i] = LpVariable(f"z_{i}", cat='Binary')
        
        #  CONTRAINTES 
        
        # 1. Un patient ne peut être assigné qu'à un seul médecin
        for i in range(n_patients):
            prob += lpSum([x[i, j] for j in range(n_doctors)]) <= 1, f"OneDoctor_{i}"
        
        # 2. Un médecin ne peut traiter qu'un seul patient
        for j in range(n_doctors):
            prob += lpSum([x[i, j] for i in range(n_patients)]) <= 1, f"OnePatientPerDoctor_{j}"
        
        # 3. Un patient ne peut être assigné qu'à une seule civière
        for i in range(n_patients):
            prob += lpSum([y[i, k] for k in range(n_beds)]) <= 1, f"OneBed_{i}"
        
        # 4. Une civière ne peut accueillir qu'un seul patient
        for k in range(n_beds):
            prob += lpSum([y[i, k] for i in range(n_patients)]) <= 1, f"OnePatientPerBed_{k}"
        
        # 5. Liaison : si traité, doit avoir médecin ET civière
        for i in range(n_patients):
            prob += lpSum([x[i, j] for j in range(n_doctors)]) >= z[i], f"Link_doctor_{i}"
            prob += lpSum([y[i, k] for k in range(n_beds)]) >= z[i], f"Link_bed_{i}"
            prob += z[i] <= lpSum([x[i, j] for j in range(n_doctors)]), f"Link_z_doctor_{i}"
            prob += z[i] <= lpSum([y[i, k] for k in range(n_beds)]), f"Link_z_bed_{i}"
        
        # 6. Patients critiques dépassant leur temps max DOIVENT être traités
        for i, patient in enumerate(waiting_patients):
            wait_time = patient.get_wait_time(current_time)
            max_wait = patient.get_max_wait_time()
            
            if patient.priority.value <= 2 and wait_time >= max_wait:
                prob += z[i] == 1, f"MustTreat_{i}"
        
        #  FONCTION OBJECTIF 
        
        objective_terms = []
        
        # Composante 1 : Pénalité pour patients non traités (pondérée par priorité)
        for i, patient in enumerate(waiting_patients):
            priority_weight = (6 - patient.priority.value) * 100
            objective_terms.append((1 - z[i]) * priority_weight)
        
        # Composante 2 : Pénalité pour temps d'attente des non-traités
        for i, patient in enumerate(waiting_patients):
            wait_time = patient.get_wait_time(current_time)
            objective_terms.append((1 - z[i]) * wait_time)
        
        # Composante 3 : Pénalité pour dépassement de temps max
        for i, patient in enumerate(waiting_patients):
            wait_time = patient.get_wait_time(current_time)
            max_wait = patient.get_max_wait_time()
            overtime = max(0, wait_time - max_wait)
            objective_terms.append(overtime * 50)
        
        prob += lpSum(objective_terms), "Total_Objective"
        
        #  RÉSOLUTION 
        
        try:
            prob.solve(self.solver)
            
            status = LpStatus[prob.status]
            
            if status in ['Optimal', 'Feasible']:
                # Extraire les affectations
                assignments = []
                
                for i, patient in enumerate(waiting_patients):
                    if value(z[i]) > 0.5:  # Patient traité
                        # Trouver le médecin
                        doctor_idx = None
                        for j in range(n_doctors):
                            if value(x[i, j]) > 0.5:
                                doctor_idx = j
                                break
                        
                        # Trouver la civière
                        bed_idx = None
                        for k in range(n_beds):
                            if value(y[i, k]) > 0.5:
                                bed_idx = k
                                break
                        
                        if doctor_idx is not None and bed_idx is not None:
                            actual_doctor = available_doctors[doctor_idx].id
                            actual_bed = available_beds[bed_idx].id
                            assignments.append((patient.id, actual_doctor, actual_bed))
                
                print(f"MILP Solver: {len(assignments)} assignments (objective: {value(prob.objective):.0f})")
                
                return assignments
            else:
                print(f"MILP Solver: No solution found (status: {status})")
                return []
                
        except Exception as e:
            print(f"MILP Solver error: {e}")
            return []
    
    def get_solver_stats(self, prob) -> Dict:
        """Extrait les statistiques du solveur"""
        return {
            'status': LpStatus[prob.status],
            'objective': value(prob.objective) if prob.objective else None,
            'solve_time': prob.solutionTime if hasattr(prob, 'solutionTime') else None,
            'num_variables': prob.numVariables(),
            'num_constraints': prob.numConstraints()
        }
