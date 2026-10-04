-- Copyright (C) 2026 Jonathan f(n) Reed
-- Licensed under AGPL-3.0

import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.MeasureTheory.Integral.Bochner.Basic

variable (Q R epsilon_0 k_B T z_i : ℝ)
variable (h_eps : 0 < epsilon_0)
variable (h_T : 0 < T)

-- Geometric Coupling Constant definition
noncomputable def Gamma : ℝ := (z_i * Q * R) / epsilon_0

-- Structural Boltzmann concentration state equation definition
noncomputable def structural_concentration (C_0 mean_rho_shell : ℝ) : ℝ :=
  C_0 * Real.exp (- (Gamma Q R epsilon_0 z_i * mean_rho_shell) / (k_B * T))

theorem structural_boltzmann_form (C_0 mean_rho_shell : ℝ) :
  structural_concentration Q R epsilon_0 k_B T z_i C_0 mean_rho_shell = 
  C_0 * Real.exp (- (Gamma Q R epsilon_0 z_i * mean_rho_shell) / (k_B * T)) := by
  rfl

theorem temperature_scaling_effect (C_0 mean_rho_shell factor : ℝ) (_h_factor : 0 < factor) :
    structural_concentration Q R epsilon_0 k_B (T * factor) z_i C_0 mean_rho_shell =
    C_0 * Real.exp ((- (Gamma Q R epsilon_0 z_i * mean_rho_shell) / (k_B * T)) / factor) := by
  dsimp [structural_concentration, Gamma]
  congr 1
  ring_nf

theorem concentration_monotonic_density (C_0 rho1 rho2 : ℝ) 
    (h_dens : rho1 ≤ rho2) (h_C0 : 0 ≤ C_0) 
    (h_kb_pos : 0 < k_B) (h_t_pos : 0 < T)
    (h_gamma_pos : 0 < z_i * Q * R / epsilon_0) :
    structural_concentration Q R epsilon_0 k_B T z_i C_0 rho2 ≤ 
    structural_concentration Q R epsilon_0 k_B T z_i C_0 rho1 := by
  dsimp [structural_concentration, Gamma]
  refine mul_le_mul_of_nonneg_left ?_ h_C0
  apply Real.exp_le_exp.mpr
  have h_denom : 0 < k_B * T := mul_pos h_kb_pos h_t_pos
  apply div_le_div_of_nonneg_right _ (le_of_lt h_denom)
  nlinarith

theorem convolution_density_bound
    (kernel spatial_coords : ℝ → ℝ)
    (M : ℝ)
    (h_bound : ∀ x, |spatial_coords x| ≤ M)
    (μ : MeasureTheory.Measure ℝ)
    [MeasureTheory.IsProbabilityMeasure μ]
    (h_int : MeasureTheory.Integrable kernel μ)
    (h_meas : MeasureTheory.AEStronglyMeasurable spatial_coords μ)
    : |∫ a, spatial_coords a * kernel a ∂μ| ≤ M * ∫ a, |kernel a| ∂μ := by
  
  have h_norm : |∫ a, spatial_coords a * kernel a ∂μ| ≤ ∫ a, ‖spatial_coords a * kernel a‖ ∂μ := by
    rw [← Real.norm_eq_abs]
    exact MeasureTheory.norm_integral_le_integral_norm _
  
  have h_int_abs : MeasureTheory.Integrable (fun x => |kernel x|) μ := h_int.norm
  have h_M_nonneg : 0 ≤ M := le_trans (abs_nonneg (spatial_coords 0)) (h_bound 0)

  have h_le_plain : ∀ x, ‖spatial_coords x * kernel x‖ ≤ M * |kernel x| := by
    intro x
    rw [norm_mul, Real.norm_eq_abs]
    exact mul_le_mul_of_nonneg_right (h_bound x) (abs_nonneg (kernel x))

  have h_le_norm : ∀ x, ‖spatial_coords x * kernel x‖ ≤ ‖M * |kernel x|‖ := by
    intro x
    have h_nn : 0 ≤ M * |kernel x| := mul_nonneg h_M_nonneg (abs_nonneg (kernel x))
    have h_eq : ‖M * |kernel x|‖ = M * |kernel x| := by
      rw [Real.norm_eq_abs, abs_of_nonneg h_nn]
    rw [h_eq]
    exact h_le_plain x

  have h_int_prod : MeasureTheory.Integrable (fun x => spatial_coords x * kernel x) μ := by
    refine (h_int_abs.const_mul M).mono (h_meas.mul h_int.1) ?_
    exact Filter.Eventually.of_forall h_le_norm

  have h_mono : ∫ a, ‖spatial_coords a * kernel a‖ ∂μ ≤ ∫ a, M * |kernel a| ∂μ := by
    refine MeasureTheory.integral_mono h_int_prod.norm (h_int_abs.const_mul M) h_le_plain

  rw [MeasureTheory.integral_const_mul] at h_mono
  exact le_trans h_norm h_mono