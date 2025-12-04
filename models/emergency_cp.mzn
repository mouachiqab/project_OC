% Modèle MiniZinc pour l'optimisation des urgences
% Auteur: Abdelkarim Mouachiq

include "globals.mzn";

% PARAMÈTRES


% Nombre d'entités
int: n_patients;           % Nombre de patients en attente
int: n_doctors;            % Nombre de médecins disponibles
int: n_beds;               % Nombre de civières disponibles

% Patients
array[1..n_patients] of int: priority;        % Priorité (1-5)
array[1..n_patients] of int: wait_time;       % Temps d'attente actuel
array[1..n_patients] of int: max_wait_time;   % Temps max recommandé
array[1..n_patients] of int: treatment_time;  % Durée estimée traitement

% Temps actuel
int: current_time;

% VARIABLES DE DÉCISION

% x[i] = j signifie que le patient i est assigné au médecin j (0 si non traité)
array[1..n_patients] of var 0..n_doctors: x;

% y[i] = k signifie que le patient i est assigné à la civière k (0 si non traité)
array[1..n_patients] of var 0..n_beds: y;

% z[i] = 1 si le patient i est traité dans cette décision
array[1..n_patients] of var 0..1: z;

% CONTRAINTES

% 1. Liaison entre x, y, z : si traité, doit avoir médecin ET civière
constraint forall(i in 1..n_patients)(
    z[i] = 1 <-> (x[i] > 0 /\ y[i] > 0)
);

% 2. Chaque médecin traite au plus un patient
constraint forall(j in 1..n_doctors)(
    sum(i in 1..n_patients)(x[i] = j) <= 1
);

% 3. Chaque civière accueille au plus un patient
constraint forall(k in 1..n_beds)(
    sum(i in 1..n_patients)(y[i] = k) <= 1
);

% 4. Les patients critiques (P1-P2) qui dépassent leur temps max DOIVENT être traités
constraint forall(i in 1..n_patients)(
    (priority[i] <= 2 /\ wait_time[i] >= max_wait_time[i]) -> z[i] = 1
);

% 5. Si un patient est traité, il doit avoir des ressources valides
constraint forall(i in 1..n_patients)(
    z[i] = 1 -> (x[i] >= 1 /\ x[i] <= n_doctors /\ y[i] >= 1 /\ y[i] <= n_beds)
);

% FONCTION OBJECTIF

% Composante 1: Pénalité pour patients non traités (pondérée par priorité)
var int: penalty_untreated = sum(i in 1..n_patients)(
    (1 - z[i]) * (6 - priority[i]) * 100
);

% Composante 2: Pénalité pour temps d'attente des non-traités
var int: penalty_waiting = sum(i in 1..n_patients)(
    (1 - z[i]) * wait_time[i]
);

% Composante 3: Pénalité pour dépassement de temps max
var int: penalty_overtime = sum(i in 1..n_patients)(
    if wait_time[i] > max_wait_time[i] then
        (wait_time[i] - max_wait_time[i]) * 50
    else
        0
    endif
);

% Objectif total : minimiser toutes les pénalités
var int: objective = penalty_untreated + penalty_waiting + penalty_overtime;

% Stratégie de recherche pour améliorer les performances
solve :: int_search(z, first_fail, indomain_max, complete)
      :: int_search(x, input_order, indomain_min, complete)
      :: int_search(y, input_order, indomain_min, complete)
      minimize objective;

% SORTIE

output [
    "Objective: \(objective)\n",
    "Patients treated: \(sum(z))\n",
    "Penalty untreated: \(penalty_untreated)\n",
    "Penalty waiting: \(penalty_waiting)\n",
    "Penalty overtime: \(penalty_overtime)\n",
    "\nAssignments:\n"
] ++
[
    "Patient \(i) -> Doctor \(x[i]) & Bed \(y[i]) (Priority=\(priority[i]), Wait=\(wait_time[i])min, Treated=\(z[i]))\n"
    | i in 1..n_patients where fix(z[i]) = 1
];
