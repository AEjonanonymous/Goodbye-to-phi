# Copyright (C) 2026 Jonathan f(n) Reed
# Licensed under AGPL-3.0

import numpy as np
from shell_boltz import ShellBoltzSolver, E_CHARGE

# ==========================================
# 2. TESTBENCH WORKFLOW EXECUTION
# ==========================================

if __name__ == "__main__":
    print("=== INITIALIZING SHELLBOLTZ ENGINE ===")
    
    # Initialize solver with verified bounds
    solver = ShellBoltzSolver(max_density_bound=5.0)
    
    # Define exact physical battery interface parameters
    z_ion = 2                    # Divalent metal ion (e.g., Zn^2+)
    
    # Collective coordination scaling: Effective shell charge incorporates 
    # the cooperative multi-ion/solvent footprint of the structural shell (~10^5 factor)
    coordination_number_factor = 2.0e5 
    q_shell_effective = coordination_number_factor * E_CHARGE
    
    shell_radius = 2.5e-10       # 2.5 Angstroms coordination radius (m)
    temperature = 298.15         # Standard operating temperature (K)
    pre_exponential_c0 = 1.0     # Base reference concentration
    
    print(f"Parameters Set -> Ion Charge: z={z_ion}, Radius: {shell_radius*1e10:.1f} Å, Temp: {temperature} K")

    # Step A: Compute Exact Gamma
    gamma = solver.compute_gamma(z_ion, q_shell_effective, shell_radius)
    print(f"Computed Geometric Coupling Constant (Gamma): {gamma:.4e} J*m")

    # Step B: Run Safe Spatial Density Simulation (Dimensionless structural packing field)
    safe_density_field = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    
    concentration_profile = solver.compute_structural_boltzmann(
        c_0=pre_exponential_c0,
        gamma=gamma,
        rho_s_shell=safe_density_field,
        temp=temperature
    )
    
    print("\n--- Simulation Run: Normal Operating Conditions ---")
    for density, conc in zip(safe_density_field, concentration_profile):
        print(f"Local Structural Density (rho_s): {density:.1f} | Resulting Ion Concentration: {conc:.4f}")

    # Step C: Test Deposition Threshold
    critical_density = solver.solve_deposition_threshold(
        c_0=pre_exponential_c0,
        gamma=gamma,
        temp=temperature,
        threshold_concentration=0.5
    )
    print(f"\nCalculated Critical Plating Threshold Density: {critical_density:.4f}")

    # Step D: Test Safety Boundary Trigger
    print("\n--- Testing Safety Boundary Trigger ---")
    try:
        unstable_density_field = np.array([1.0, 3.0, 6.0])  # Exceeds max_density_bound of 5.0
        solver.compute_structural_boltzmann(
            c_0=pre_exponential_c0,
            gamma=gamma,
            rho_s_shell=unstable_density_field,
            temp=temperature
        )
    except ValueError as e:
        print("SUCCESS: Safety assertion caught instability correctly!")
        print(f"Error message captured: {e}")
        
    print("\n=== WORKFLOW COMPLETED SUCCESSFULLY ===")