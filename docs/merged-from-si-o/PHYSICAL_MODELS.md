# SiO Catalyst Quantum Studio Pro: Physical & Mathematical Models

This document details the scientific foundations, equations, and numerical approximations implemented in the platform's core modules.

## 1. Kinetic Engines

### 1.1 Arrhenius-Humidity Model
**Location:** `hydrolysis/page.tsx`
Calculates the rate of Si-Cl bond hydrolysis influenced by environmental humidity.
$$k(T, RH) = A \cdot \exp\left(-\frac{E_a}{RT}\right) \cdot (1 + \beta \cdot RH)$$
*   **$RH$**: Relative Humidity (0-100%)
*   **$\beta$**: Humidity sensitivity factor (~0.05)

### 1.2 Reversible Transition State Theory (ODE)
**Location:** `kinetics-simulator/page.tsx`
Solves the time-dependent concentration for a reversible reaction $A \rightleftharpoons B$.
$$\frac{d[A]}{dt} = -k_f [A] + k_r [B]$$
Where $k_f = \frac{k_B T}{h} \exp(-\frac{\Delta G^\ddagger}{RT})$ and $k_r = k_f / K_{eq}$.

## 2. Thermodynamic Distributions

### 2.1 Boltzmann Population Analysis
**Location:** `ti-poisoning/page.tsx`
Calculates the relative occupancy of various poisoned states of the Titanium center.
$$P_i = \frac{\exp(-\Delta E_i / k_B T)}{\sum_j \exp(-\Delta E_j / k_B T)}$$

## 3. Electronic Structure & Solvation

### 3.1 NBO Second-Order Perturbation
**Location:** `nbo-interaction/page.tsx`
Estimates donor-acceptor interaction energy ($E^{(2)}$) between orbitals.
$$E^{(2)} = q_i \frac{F_{ij}^2}{\epsilon_j - \epsilon_i}$$
*   **$q_i$**: Donor occupancy
*   **$F_{ij}$**: Off-diagonal Fock matrix element (Fock Coupling)
*   **$\epsilon$**: Orbital energies

### 3.2 Temperature-Dependent Solvation (Kirkwood-Onsager)
**Location:** `tea-interaction/page.tsx`
Adjusts the dielectric constant ($\epsilon$) based on temperature and computes the solvation energy shift.
$$\epsilon(T) = \epsilon_{298} \cdot \exp(-0.0025 \cdot (T - 298.15))$$
$$\Delta G_{solv} \approx -\frac{1}{2} \left( \frac{\epsilon-1}{2\epsilon+1} \right) \frac{\mu^2}{a^3}$$

## 4. Topological Analysis

### 4.1 Analytic RDG (Reduced Density Gradient)
**Location:** `qtaim-nci/page.tsx`
Simulates the RDG scalar field for identifying non-covalent interactions (NCI).
$$s(\rho) = \frac{1}{2(3\pi^2)^{1/3}} \frac{|\nabla \rho|}{\rho^{4/3}}$$
*Implemented as a distance-based analytical approximation for real-time visualization.*

## 5. Physical Constants Used
*   **Gas Constant ($R$)**: 1.987 cal/(mol·K)
*   **Boltzmann Constant ($k_B$)**: 1.3806e-23 J/K
*   **Planck Constant ($h$)**: 6.626e-34 J·s
*   **Reference Temperature**: 298.15 K
*   **Hartree to eV**: 27.2114 eV

---
**Note:** All real-time predictions for MW and Polarity in the `ai-prescreen` module use empirical descriptors derived from SMILES topology.
