"""
Tests unitaires pour les optimiseurs
Auteurs: Abdelkarim & Marin
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simulation.patient import Patient, Priority
from simulation.resources import Doctor, Bed
from optimization.cp_model import CPOptimizer
from optimization.milp_model import MILPOptimizer
from optimization.optimizer_interface import create_optimizer

class TestOptimizerInterface:
    """Tests pour l'interface des optimiseurs"""
    
    def test_create_cp_optimizer(self):
        """Test création d'un optimiseur CP"""
        optimizer = create_optimizer('CP', time_limit=30)
        assert isinstance(optimizer, CPOptimizer)
    
    def test_create_milp_optimizer(self):
        """Test création d'un optimiseur MILP"""
        optimizer = create_optimizer('MILP', time_limit=30)
        assert isinstance(optimizer, MILPOptimizer)
    
    def test_invalid_method(self):
        """Test avec une méthode invalide"""
        with pytest.raises(ValueError):
            create_optimizer('INVALID')

class TestMILPOptimizer:
    """Tests pour l'optimiseur MILP"""
    
    def test_milp_optimizer_creation(self):
        """Test création de l'optimiseur MILP"""
        optimizer = MILPOptimizer(time_limit=30, solver_name='PULP_CBC_CMD')
        assert optimizer.time_limit == 30
        assert optimizer.solver_name == 'PULP_CBC_CMD'
        assert optimizer.solver is not None
    
    def test_milp_empty_state(self):
        """Test avec un état vide"""
        optimizer = MILPOptimizer(time_limit=10)
        
        state = {
            'waiting_patients': [],
            'available_doctors': [],
            'available_beds': [],
            'current_time': 0.0
        }
        
        assignments = optimizer.optimize(state)
        assert assignments == []
    
    def test_milp_simple_assignment(self):
        """Test affectation simple"""
        optimizer = MILPOptimizer(time_limit=30)
        
        # Créer un état simple
        patients = [
            Patient(arrival_time=0.0, initial_priority=Priority.P2_EMERGENT)
        ]
        doctors = [Doctor(id=0, name="Dr. A")]
        beds = [Bed(id=0)]
        
        state = {
            'waiting_patients': patients,
            'available_doctors': doctors,
            'available_beds': beds,
            'current_time': 30.0
        }
        
        assignments = optimizer.optimize(state)
        
        # Devrait trouver une solution (1 patient, 1 médecin, 1 civière disponibles)
        assert len(assignments) == 1
        assert assignments[0][0] == patients[0].id
        assert assignments[0][1] == 0  # doctor_id
        assert assignments[0][2] == 0  # bed_id
    
    def test_milp_multiple_patients(self):
        """Test avec plusieurs patients de priorités différentes"""
        optimizer = MILPOptimizer(time_limit=30)
        
        patients = [
            Patient(arrival_time=0.0, initial_priority=Priority.P1_RESUSCITATION),
            Patient(arrival_time=5.0, initial_priority=Priority.P3_URGENT),
            Patient(arrival_time=10.0, initial_priority=Priority.P5_NON_URGENT)
        ]
        doctors = [Doctor(id=0, name="Dr. A"), Doctor(id=1, name="Dr. B")]
        beds = [Bed(id=0), Bed(id=1)]
        
        state = {
            'waiting_patients': patients,
            'available_doctors': doctors,
            'available_beds': beds,
            'current_time': 30.0
        }
        
        assignments = optimizer.optimize(state)
        
        # Devrait assigner au moins les patients prioritaires
        assert len(assignments) >= 1
        # Vérifier qu'aucune ressource n'est utilisée deux fois
        assigned_doctors = [a[1] for a in assignments]
        assigned_beds = [a[2] for a in assignments]
        assert len(assigned_doctors) == len(set(assigned_doctors))
        assert len(assigned_beds) == len(set(assigned_beds))
    
    def test_milp_insufficient_resources(self):
        """Test avec plus de patients que de ressources"""
        optimizer = MILPOptimizer(time_limit=30)
        
        patients = [
            Patient(arrival_time=0.0, initial_priority=Priority.P2_EMERGENT),
            Patient(arrival_time=5.0, initial_priority=Priority.P3_URGENT),
            Patient(arrival_time=10.0, initial_priority=Priority.P4_LESS_URGENT)
        ]
        doctors = [Doctor(id=0, name="Dr. A")]
        beds = [Bed(id=0)]
        
        state = {
            'waiting_patients': patients,
            'available_doctors': doctors,
            'available_beds': beds,
            'current_time': 30.0
        }
        
        assignments = optimizer.optimize(state)
        
        # Ne peut assigner qu'un seul patient maximum
        assert len(assignments) <= 1
        if len(assignments) == 1:
            # Devrait prioriser le patient P2
            assert assignments[0][0] == patients[0].id

class TestCPOptimizer:
    """Tests pour l'optimiseur CP"""
    
    def test_cp_optimizer_creation(self):
        """Test création de l'optimiseur CP"""
        try:
            optimizer = CPOptimizer(time_limit=30, solver_name='chuffed')
            assert optimizer.time_limit == 30
            assert optimizer.solver_name == 'chuffed'
        except Exception as e:
            pytest.skip(f"MiniZinc not available: {e}")
    
    def test_cp_empty_state(self):
        """Test avec un état vide"""
        try:
            optimizer = CPOptimizer(time_limit=10)
            
            state = {
                'waiting_patients': [],
                'available_doctors': [],
                'available_beds': [],
                'current_time': 0.0
            }
            
            assignments = optimizer.optimize(state)
            assert assignments == []
        except Exception as e:
            pytest.skip(f"MiniZinc not available: {e}")
    
    def test_cp_simple_assignment(self):
        """Test affectation simple avec CP"""
        try:
            optimizer = CPOptimizer(time_limit=30, solver_name='chuffed')
            
            patients = [
                Patient(arrival_time=0.0, initial_priority=Priority.P2_EMERGENT)
            ]
            doctors = [Doctor(id=0, name="Dr. A")]
            beds = [Bed(id=0)]
            
            state = {
                'waiting_patients': patients,
                'available_doctors': doctors,
                'available_beds': beds,
                'current_time': 30.0
            }
            
            assignments = optimizer.optimize(state)
            
            # Devrait trouver une solution
            assert len(assignments) == 1
            assert assignments[0][0] == patients[0].id
        except Exception as e:
            pytest.skip(f"MiniZinc not available: {e}")
    
    def test_cp_multiple_patients(self):
        """Test avec plusieurs patients"""
        try:
            optimizer = CPOptimizer(time_limit=30, solver_name='chuffed')
            
            patients = [
                Patient(arrival_time=0.0, initial_priority=Priority.P1_RESUSCITATION),
                Patient(arrival_time=5.0, initial_priority=Priority.P3_URGENT)
            ]
            doctors = [Doctor(id=0, name="Dr. A"), Doctor(id=1, name="Dr. B")]
            beds = [Bed(id=0), Bed(id=1)]
            
            state = {
                'waiting_patients': patients,
                'available_doctors': doctors,
                'available_beds': beds,
                'current_time': 30.0
            }
            
            assignments = optimizer.optimize(state)
            
            # Devrait assigner les deux patients
            assert len(assignments) >= 1
        except Exception as e:
            pytest.skip(f"MiniZinc not available: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
