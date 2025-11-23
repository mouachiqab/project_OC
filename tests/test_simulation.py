"""
Tests unitaires pour les modules de simulation
Auteurs: Abdelkarim & Marin
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simulation.patient import Patient, Priority, PatientState
from simulation.resources import Doctor, Bed, EmergencyResources
import simpy

class TestPatient:
    """Tests pour la classe Patient"""
    
    def test_patient_creation(self):
        """Test création d'un patient"""
        patient = Patient(arrival_time=0.0, initial_priority=Priority.P3_URGENT)
        
        assert patient.id > 0
        assert patient.arrival_time == 0.0
        assert patient.priority == Priority.P3_URGENT
        assert patient.initial_priority == Priority.P3_URGENT
        assert patient.treatment_duration > 0
    
    def test_max_wait_time(self):
        """Test des temps d'attente maximum selon priorité"""
        priorities_and_times = [
            (Priority.P1_RESUSCITATION, 0),
            (Priority.P2_EMERGENT, 15),
            (Priority.P3_URGENT, 30),
            (Priority.P4_LESS_URGENT, 60),
            (Priority.P5_NON_URGENT, 120)
        ]
        
        for priority, expected_time in priorities_and_times:
            patient = Patient(0.0, priority)
            assert patient.get_max_wait_time() == expected_time
    
    def test_wait_time_calculation(self):
        """Test calcul du temps d'attente"""
        patient = Patient(arrival_time=10.0, initial_priority=Priority.P3_URGENT)
        
        # Sans traitement démarré
        wait_time = patient.get_wait_time(current_time=40.0)
        assert wait_time == 30.0
        
        # Avec traitement démarré
        patient.start_treatment(current_time=40.0, doctor_id=1, bed_id=1)
        wait_time = patient.get_wait_time(current_time=50.0)
        assert wait_time == 30.0  # Temps entre arrivée et début traitement
    
    def test_deterioration(self):
        """Test de la détérioration de l'état"""
        patient = Patient(arrival_time=0.0, initial_priority=Priority.P5_NON_URGENT)
        
        original_priority = patient.priority
        patient.deteriorate()
        
        assert patient.priority.value == original_priority.value - 1
        assert patient.priority == Priority.P4_LESS_URGENT
        
        # Test qu'on ne peut pas détériorer en dessous de P1
        patient_p1 = Patient(0.0, Priority.P1_RESUSCITATION)
        patient_p1.deteriorate()
        assert patient_p1.priority == Priority.P1_RESUSCITATION

class TestResources:
    """Tests pour la gestion des ressources"""
    
    def test_doctor_creation(self):
        """Test création d'un médecin"""
        doctor = Doctor(id=1, name="Dr. Smith")
        
        assert doctor.id == 1
        assert doctor.name == "Dr. Smith"
        assert doctor.is_available == True
        assert doctor.current_patient is None
        assert doctor.total_patients_treated == 0
    
    def test_doctor_assignment(self):
        """Test affectation d'un patient à un médecin"""
        doctor = Doctor(id=1, name="Dr. Smith")
        
        doctor.assign_patient(patient_id=101)
        
        assert doctor.is_available == False
        assert doctor.current_patient == 101
        assert doctor.total_patients_treated == 1
    
    def test_doctor_release(self):
        """Test libération d'un médecin"""
        doctor = Doctor(id=1, name="Dr. Smith")
        doctor.assign_patient(patient_id=101)
        
        doctor.release_patient(treatment_time=45.0)
        
        assert doctor.is_available == True
        assert doctor.current_patient is None
        assert doctor.total_treatment_time == 45.0
    
    def test_bed_operations(self):
        """Test des opérations sur les civières"""
        bed = Bed(id=1)
        
        assert bed.is_available == True
        
        bed.assign_patient(patient_id=101)
        assert bed.is_available == False
        assert bed.current_patient == 101
        
        bed.release_patient(occupancy_time=120.0)
        assert bed.is_available == True
        assert bed.total_occupancy_time == 120.0
    
    def test_emergency_resources(self):
        """Test de la gestion centralisée des ressources"""
        env = simpy.Environment()
        resources = EmergencyResources(env, num_doctors=3, num_beds=10)
        
        assert len(resources.doctors) == 3
        assert len(resources.beds) == 10
        assert len(resources.get_available_doctors()) == 3
        assert len(resources.get_available_beds()) == 10
        
        # Simuler une affectation
        doctors = resources.get_available_doctors()
        doctors[0].assign_patient(101)
        
        assert len(resources.get_available_doctors()) == 2

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
