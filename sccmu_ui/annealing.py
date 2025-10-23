#!/usr/bin/env python3
"""
Temperature Annealing for SCCMU Evolution

Implements gradual β schedule from high temperature (exploration)
to low temperature (exploitation) to show emergence trajectory.

Theory.md: β = 2πφ is the equilibrium value, but we can vary it
during evolution to show the full emergence process.
"""

import numpy as np
from typing import List, Callable
from .zx_core import PHI


# Target inverse temperature (equilibrium value from theory)
BETA_TARGET = 2 * np.pi * PHI


class AnnealingSchedule:
    """
    Temperature annealing schedule for SCCMU evolution.
    
    Shows emergence trajectory by starting hot (explores widely)
    and cooling to equilibrium (settles to coherence maximum).
    """
    
    def __init__(self, 
                 schedule_type: str = "exponential",
                 total_steps: int = 200,
                 beta_initial: float = 0.1,
                 beta_final: float = None):
        """
        Args:
            schedule_type: "linear", "exponential", or "sigmoid"
            total_steps: Total number of evolution steps
            beta_initial: Starting β (high temp → exploration)
            beta_final: Final β (defaults to 2πφ from theory)
        """
        self.schedule_type = schedule_type
        self.total_steps = total_steps
        self.beta_initial = beta_initial
        self.beta_final = beta_final if beta_final is not None else BETA_TARGET
        
        self.current_step = 0
        self.current_beta = beta_initial
        
    def get_beta(self, step: int = None) -> float:
        """
        Get β at given step (or current step).
        
        Returns inverse temperature β for free energy computation.
        """
        if step is None:
            step = self.current_step
        
        if step >= self.total_steps:
            return self.beta_final
        
        # Normalized progress [0, 1]
        progress = step / self.total_steps
        
        if self.schedule_type == "linear":
            # Linear interpolation
            beta = self.beta_initial + progress * (self.beta_final - self.beta_initial)
        
        elif self.schedule_type == "exponential":
            # Exponential decay of temperature (slow then fast)
            # T = T_initial * exp(-k*t)  =>  β = β_initial * exp(k*t)
            k = np.log(self.beta_final / self.beta_initial)
            beta = self.beta_initial * np.exp(k * progress)
        
        elif self.schedule_type == "sigmoid":
            # Smooth S-curve transition
            # Maps [0,1] → [0,1] via sigmoid
            x = (progress - 0.5) * 10  # Center at 0.5, steepness 10
            sigmoid = 1.0 / (1.0 + np.exp(-x))
            beta = self.beta_initial + sigmoid * (self.beta_final - self.beta_initial)
        
        elif self.schedule_type == "power":
            # Power law: β(t) = β_i + (β_f - β_i) * t^α
            alpha = 2.0  # Quadratic
            beta = self.beta_initial + (progress ** alpha) * (self.beta_final - self.beta_initial)
        
        else:
            raise ValueError(f"Unknown schedule type: {self.schedule_type}")
        
        return float(beta)
    
    def step(self) -> float:
        """Advance one step and return current β"""
        self.current_step += 1
        self.current_beta = self.get_beta()
        return self.current_beta
    
    def temperature(self, step: int = None) -> float:
        """Get temperature T = 1/β at given step"""
        beta = self.get_beta(step)
        return 1.0 / beta if beta > 0 else float('inf')
    
    def get_schedule(self) -> np.ndarray:
        """Get full β schedule as array"""
        return np.array([self.get_beta(i) for i in range(self.total_steps + 1)])
    
    def progress(self) -> float:
        """Get progress [0, 1]"""
        return min(self.current_step / self.total_steps, 1.0)
    
    def is_complete(self) -> bool:
        """Check if annealing is complete"""
        return self.current_step >= self.total_steps
    
    def reset(self):
        """Reset to initial state"""
        self.current_step = 0
        self.current_beta = self.beta_initial


def create_annealing_schedule(schedule_type: str = "exponential",
                               total_steps: int = 200,
                               beta_initial: float = 0.1) -> AnnealingSchedule:
    """
    Create standard annealing schedule.
    
    Theory.md compliance:
    - β_final = 2πφ (equilibrium value from Axiom 3)
    - β_initial = 0.1 (high temperature for exploration)
    - Schedule shows emergence trajectory
    
    Args:
        schedule_type: "linear", "exponential", "sigmoid", "power"
        total_steps: Number of evolution steps
        beta_initial: Starting inverse temperature
    
    Returns:
        AnnealingSchedule instance
    """
    return AnnealingSchedule(
        schedule_type=schedule_type,
        total_steps=total_steps,
        beta_initial=beta_initial,
        beta_final=BETA_TARGET
    )


# Preset schedules for common use cases

def fast_annealing(steps: int = 100) -> AnnealingSchedule:
    """Fast annealing for quick visualization (100 steps)"""
    return create_annealing_schedule("exponential", steps, 0.1)


def slow_annealing(steps: int = 500) -> AnnealingSchedule:
    """Slow annealing for detailed emergence (500 steps)"""
    return create_annealing_schedule("sigmoid", steps, 0.05)


def exploration_annealing(steps: int = 300) -> AnnealingSchedule:
    """Extended exploration phase then quick convergence"""
    return create_annealing_schedule("power", steps, 0.1)


def fixed_temperature(beta: float = BETA_TARGET) -> AnnealingSchedule:
    """No annealing - fixed β (original behavior)"""
    return AnnealingSchedule("linear", 1, beta, beta)


# Analysis utilities

def analyze_schedule(schedule: AnnealingSchedule) -> dict:
    """
    Analyze annealing schedule properties.
    
    Returns statistics about temperature range, cooling rate, etc.
    """
    betas = schedule.get_schedule()
    temps = 1.0 / betas
    
    # Cooling rate (derivative approximation)
    cooling_rates = -np.diff(temps)  # -dT/dt
    
    return {
        'beta_initial': float(betas[0]),
        'beta_final': float(betas[-1]),
        'temp_initial': float(temps[0]),
        'temp_final': float(temps[-1]),
        'temp_ratio': float(temps[0] / temps[-1]),
        'max_cooling_rate': float(np.max(cooling_rates)),
        'mean_cooling_rate': float(np.mean(cooling_rates)),
        'schedule_type': schedule.schedule_type,
        'total_steps': schedule.total_steps
    }


def plot_schedule(schedule: AnnealingSchedule) -> str:
    """
    Generate ASCII plot of annealing schedule.
    
    Returns string representation for terminal display.
    """
    betas = schedule.get_schedule()
    steps = len(betas)
    
    # Normalize for plotting
    beta_min, beta_max = float(np.min(betas)), float(np.max(betas))
    normalized = (betas - beta_min) / (beta_max - beta_min) if beta_max > beta_min else betas * 0
    
    # Create ASCII plot (40 rows)
    height = 20
    width = min(steps, 80)
    
    # Downsample if needed
    if steps > width:
        indices = np.linspace(0, steps-1, width, dtype=int)
        plot_vals = normalized[indices]
    else:
        plot_vals = normalized
        width = steps
    
    lines = []
    lines.append(f"β Annealing Schedule ({schedule.schedule_type})")
    lines.append(f"{'='*width}")
    
    for row in range(height, -1, -1):
        threshold = row / height
        line = ""
        for val in plot_vals:
            if val >= threshold:
                line += "█"
            elif val >= threshold - 0.05:
                line += "▓"
            else:
                line += " "
        
        # Y-axis labels
        beta_val = beta_min + (beta_max - beta_min) * threshold
        lines.append(f"{beta_val:6.2f} │{line}│")
    
    lines.append(f"       └{'─'*width}┘")
    lines.append(f"       0{' '*(width-10)}steps{' '*(max(0, width-35))}{steps}")
    lines.append(f"\nT_initial = {1.0/betas[0]:.2f}, T_final = {1.0/betas[-1]:.2f}")
    lines.append(f"β_initial = {betas[0]:.2f}, β_final = {betas[-1]:.2f} (theory: {BETA_TARGET:.2f})")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo different schedules
    print("=" * 80)
    print("SCCMU Temperature Annealing Schedules")
    print("=" * 80)
    
    schedules = [
        ("Exponential (Fast)", fast_annealing(100)),
        ("Sigmoid (Slow)", slow_annealing(200)),
        ("Power Law (Exploration)", exploration_annealing(150)),
    ]
    
    for name, sched in schedules:
        print(f"\n{name}:")
        print("-" * 80)
        print(plot_schedule(sched))
        
        stats = analyze_schedule(sched)
        print(f"\nStats:")
        print(f"  Temperature ratio: {stats['temp_ratio']:.1f}x")
        print(f"  Max cooling rate: {stats['max_cooling_rate']:.4f}")
        print(f"  Mean cooling rate: {stats['mean_cooling_rate']:.4f}")
        print()

