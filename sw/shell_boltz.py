# Copyright (C) 2026 Jonathan f(n) Reed
# Licensed under AGPL-3.0

import numpy as np

# ==========================================
# 1. CORE ENGINE (SI UNITS)
# ==========================================

EPSILON_0 = 8.854187817e-12  # Vacuum permittivity (F/m)
E_CHARGE  = 1.602176634e-19  # Elementary charge (C)
K_B       = 1.380649e-23     # Boltzmann constant (J/K)

class ShellBoltzSolver:
    def __init__(self, max_density_bound: float = 5.0):
        # Verified upper bound for the dimensionless structural density field
        self.max_density_bound = max_density_bound

    def compute_gamma(self, z_i: int, q_shell_effective: float, r_shell: float) -> float:
        """
        Computes the Geometric Coupling Constant (Gamma):
        Gamma = (z_i * e * Q_shell_effective * R) / epsilon_0
        """
        return (z_i * E_CHARGE * q_shell_effective * r_shell) / EPSILON_0

    def compute_structural_boltzmann(
        self, 
        c_0: float, 
        gamma: float, 
        rho_s_shell: np.ndarray, 
        temp: float
    ) -> np.ndarray:
        """
        Computes the Structural Boltzmann Distribution using exact thermal scaling:
        c_i(r) = C_0 * exp(-(Gamma * <rho_s>) / (k_B * T * R_scale))
        """
        if np.any(rho_s_shell > self.max_density_bound):
            raise ValueError(
                f"Stability Warning: Local structural density field exceeds the verified "
                f"bound (M = {self.max_density_bound}). Simulation unstable; "
                f"potential physical phase-transition or void collapse detected."
            )

        characteristic_length = 2.5e-10  # 2.5 Angstroms coordination radius (m)
        
        exponent = -(gamma * rho_s_shell) / (K_B * temp * characteristic_length)
        return c_0 * np.exp(exponent)

    def solve_deposition_threshold(
        self, 
        c_0: float, 
        gamma: float, 
        temp: float, 
        threshold_concentration: float
    ) -> float:
        """Calculates critical structural density threshold for metal plating."""
        if threshold_concentration >= c_0:
            return 0.0
        characteristic_length = 2.5e-10
        return -(K_B * temp * characteristic_length / gamma) * np.log(threshold_concentration / c_0)