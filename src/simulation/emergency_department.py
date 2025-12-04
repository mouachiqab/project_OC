"""
Simulation du service des urgences avec SimPy
Auteur: Marin Kerbouriou
"""
import simpy
import numpy as np
from typing import List, Dict, Callable, Optional
from collections import defaultdict

from .patient import Patient, Priority
from .resources import EmergencyResources

class EmergencyDepartment:
    """Simulation d'un service d'urgences"""
    
    def __init__(
        self,
        env: simpy.Environment,
        num_doctors: int,
        num_beds: int,
        arrival_rate: float,  # patients par heure
        optimization_interval: int = 30,  # minutes
        optimizer: Optional[Callable] = None
    ):
        """
        Initialise le service des urgences
        
        Args:
            env: Environnement SimPy
            num_doctors: Nombre de médecins
            num_beds: Nombre de civières
            arrival_rate: Taux d'arrivée (patients/heure)
            optimization_interval: Intervalle entre optimisations (minutes)
            optimizer: Fonction d'optimisation (CP ou MILP)
        """
        self.env = env
        self.arrival_rate = arrival_rate
        self.optimization_interval = optimization_interval
        self.optimizer = optimizer
        
        # Ressources
        self.resources = EmergencyResources(env, num_doctors, num_beds)
        
        # Files d'attente par priorité
        self.waiting_patients: Dict[Priority, List[Patient]] = {
            priority: [] for priority in Priority
        }
        
        # Patients en cours de traitement
        self.treating_patients: List[Patient] = []
        
        # Patients sortis
        self.discharged_patients: List[Patient] = []
        
        # Métriques
        self.metrics = defaultdict(list)
        
        # Compteurs
        self.total_arrivals = 0
        self.total_treated = 0
        self.total_deteriorations = 0
    
    def generate_priority(self) -> Priority:
        """Génère une priorité selon une distribution réaliste"""
        # Distribution basée sur statistiques québécoises
        priorities = [
            Priority.P1_RESUSCITATION,
            Priority.P2_EMERGENT,
            Priority.P3_URGENT,
            Priority.P4_LESS_URGENT,
            Priority.P5_NON_URGENT
        ]
        probabilities = [0.05, 0.15, 0.30, 0.35, 0.15]
        
        return np.random.choice(priorities, p=probabilities)
    
    def patient_arrival_process(self):
        """Processus d'arrivée des patients (Poisson)"""
        while True:
            # Temps entre arrivées (exponentiel)
            inter_arrival_time = np.random.exponential(60 / self.arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            
            # Créer un nouveau patient
            priority = self.generate_priority()
            patient = Patient(self.env.now, priority)
            
            # Ajouter à la file d'attente
            self.waiting_patients[priority].append(patient)
            self.total_arrivals += 1
            
            print(f"[{self.env.now:>6.1f}] Patient {patient.id} arrived ({priority.name})")
    
    def deterioration_process(self):
        """Processus simplifié de détérioration des patients en attente"""
        while True:
            yield self.env.timeout(30)  # Vérifier toutes les 30 minutes 
            
            # Seulement les cas critiques se détériorent
            for priority in [Priority.P3_URGENT, Priority.P2_EMERGENT]:
                for patient in list(self.waiting_patients[priority]):
                    wait_time = patient.get_wait_time(self.env.now)
                    max_wait = patient.get_max_wait_time()
                    
                    # Détérioration seulement si attente > 2x le max
                    if wait_time > max_wait * 2.0:
                        if np.random.random() < 0.15:  # 15% de chance 
                            old_priority = patient.priority
                            patient.deteriorate()
                            
                            if patient.priority != old_priority:
                                self.waiting_patients[old_priority].remove(patient)
                                self.waiting_patients[patient.priority].append(patient)
                                self.total_deteriorations += 1
    
    def optimization_process(self):
        """Processus périodique d'optimisation"""
        while True:
            yield self.env.timeout(self.optimization_interval)
            
            if self.optimizer is not None:
                state = self._get_system_state()
                
                try:
                    assignments = self.optimizer(state)
                    
                    for patient_id, doctor_id, bed_id in assignments:
                        self._assign_patient(patient_id, doctor_id, bed_id)
                        
                except Exception as e:
                    print(f"[{self.env.now:>6.1f}] Optimization error: {e}")
    
    def _get_system_state(self) -> Dict:
        """Récupère l'état actuel du système"""
        all_waiting = []
        for priority_queue in self.waiting_patients.values():
            all_waiting.extend(priority_queue)
        
        return {
            'waiting_patients': all_waiting,
            'available_doctors': self.resources.get_available_doctors(),
            'available_beds': self.resources.get_available_beds(),
            'current_time': self.env.now
        }
    
    def _assign_patient(self, patient_id: int, doctor_id: int, bed_id: int):
        """Assigne un patient à un médecin et une civière"""
        # Trouver le patient
        patient = None
        for priority_queue in self.waiting_patients.values():
            for p in priority_queue:
                if p.id == patient_id:
                    patient = p
                    priority_queue.remove(p)
                    break
            if patient:
                break
        
        if patient is None:
            return
        
        # Récupérer les ressources
        doctor = self.resources.get_doctor_by_id(doctor_id)
        bed = self.resources.get_bed_by_id(bed_id)
        
        if doctor is None or bed is None:
            return
        
        # Faire l'affectation
        patient.start_treatment(self.env.now, doctor_id, bed_id)
        doctor.assign_patient(patient_id)
        bed.assign_patient(patient_id)
        self.treating_patients.append(patient)
        
        # Lancer le processus de traitement
        self.env.process(self._treatment_process(patient))
        
        print(f"[{self.env.now:>6.1f}] Patient {patient_id} assigned to Dr.{doctor_id} & Bed{bed_id}")
    
    def _treatment_process(self, patient: Patient):
        """Traitement d'un patient"""
        yield self.env.timeout(patient.treatment_duration)
        
        # Libérer les ressources
        doctor = self.resources.get_doctor_by_id(patient.assigned_doctor)
        bed = self.resources.get_bed_by_id(patient.assigned_bed)
        
        if doctor:
            doctor.release_patient(patient.treatment_duration)
        if bed:
            bed.release_patient(patient.treatment_duration)
        
        # Terminer le traitement
        patient.end_treatment(self.env.now)
        self.treating_patients.remove(patient)
        self.discharged_patients.append(patient)
        self.total_treated += 1
        
        print(f"[{self.env.now:>6.1f}] Patient {patient.id} discharged")
    
    def collect_metrics(self):
        """Collecte périodique des métriques"""
        while True:
            yield self.env.timeout(10)
            
            total_waiting = sum(len(queue) for queue in self.waiting_patients.values())
            
            wait_times = []
            for priority_queue in self.waiting_patients.values():
                for patient in priority_queue:
                    wait_times.append(patient.get_wait_time(self.env.now))
            
            avg_wait = np.mean(wait_times) if wait_times else 0
            
            # Statistiques ressources
            resource_stats = self.resources.get_statistics()
            
            # Enregistrer les métriques
            self.metrics['time'].append(self.env.now)
            self.metrics['waiting_patients'].append(total_waiting)
            self.metrics['avg_wait_time'].append(avg_wait)
            self.metrics['treating_patients'].append(len(self.treating_patients))
            self.metrics['discharged_patients'].append(len(self.discharged_patients))
            self.metrics['doctor_utilization'].append(
                np.mean(resource_stats['doctors']['utilization_rates'])
            )
            self.metrics['bed_occupancy'].append(
                np.mean(resource_stats['beds']['occupancy_rates'])
            )
    
    def run(self, simulation_time: float):
        """Lance la simulation"""
        # Démarrer les processus
        self.env.process(self.patient_arrival_process())
        self.env.process(self.deterioration_process())
        self.env.process(self.optimization_process())
        self.env.process(self.collect_metrics())
        
        # Exécuter la simulation
        self.env.run(until=simulation_time)
        
        print(f"\n{'='*60}")
        print(f"SIMULATION COMPLETED")
        print(f"{'='*60}")
        print(f"Total arrivals: {self.total_arrivals}")
        print(f"Total treated: {self.total_treated}")
        print(f"Total deteriorations: {self.total_deteriorations}")
        print(f"Still waiting: {sum(len(q) for q in self.waiting_patients.values())}")
        
        return self.get_results()
    
    def get_results(self) -> Dict:
        """Retourne les résultats de la simulation"""
        # Convertir les patients en format sérialisable
        discharged_data = [
            {
                'id': p.id,
                'initial_priority': p.initial_priority.name,
                'final_priority': p.priority.name,
                'arrival_time': p.arrival_time,
                'start_treatment': p.state.start_treatment_time,
                'end_treatment': p.state.end_treatment_time,
                'wait_time': p.get_wait_time(p.state.start_treatment_time or self.env.now),
                'treatment_duration': p.treatment_duration
            }
            for p in self.discharged_patients
        ]
        
        return {
            'metrics': dict(self.metrics),
            'total_arrivals': self.total_arrivals,
            'total_treated': self.total_treated,
            'total_deteriorations': self.total_deteriorations,
            'discharged_patients': discharged_data,
            'resource_stats': self.resources.get_statistics()
        }
