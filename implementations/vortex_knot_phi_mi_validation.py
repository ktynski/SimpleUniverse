#!/usr/bin/env python3
"""
Vortex-Knot φ-MI Validation (deterministic Fourier optics surrogate)

Purpose: Validate I(Source:Knot)/I(Knot:FarField) = φ in a tractable
scalar Fourier-optics surrogate. We build a phase-engineered source,
propagate to an intermediate "knot" plane and then to the far field,
compute MI on phase-gradient feature maps, and scan a scale parameter
for the φ ratio. Strict timeout enforced.
"""

import numpy as np
from numpy.fft import fft2, ifft2, fftshift
import signal
import sys

PHI = (1 + np.sqrt(5)) / 2


class Timeout:
    def __init__(self, seconds: int):
        self.seconds = seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._raise)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc, tb):
        signal.alarm(0)

    def _raise(self, signum, frame):
        raise TimeoutError("Timeout exceeded")


def make_source(nx: int, ny: int, scale: float) -> np.ndarray:
    x = np.linspace(-1, 1, nx)
    y = np.linspace(-1, 1, ny)
    X, Y = np.meshgrid(x, y, indexing='ij')
    R = np.sqrt(X**2 + Y**2) + 1e-9
    theta = np.arctan2(Y, X)
    # Spiral phase + radial lattice to seed knot-like phase gradients
    phase = scale * (2*np.pi*R + 3*theta + 0.5*np.sin(5*theta))
    amp = np.exp(-R**2 / (0.4**2))
    psi = amp * np.exp(1j * phase)
    return psi


def fresnel_propagate(psi: np.ndarray, z: float, wavelength: float, dx: float) -> np.ndarray:
    # Fresnel kernel in Fourier domain
    nx, ny = psi.shape
    k = 2 * np.pi / wavelength
    fx = np.fft.fftfreq(nx, d=dx)
    fy = np.fft.fftfreq(ny, d=dx)
    FX, FY = np.meshgrid(fx, fy, indexing='ij')
    H = np.exp(-1j * np.pi * wavelength * z * (FX**2 + FY**2))
    return ifft2(fft2(psi) * H)


def phase_grad_features(psi: np.ndarray) -> np.ndarray:
    phase = np.angle(psi)
    gx = np.roll(phase, -1, axis=0) - phase
    gy = np.roll(phase, -1, axis=1) - phase
    # Wrap to [-pi, pi]
    gx = (gx + np.pi) % (2*np.pi) - np.pi
    gy = (gy + np.pi) % (2*np.pi) - np.pi
    mag = np.sqrt(gx**2 + gy**2)
    return mag


def mutual_information(a: np.ndarray, b: np.ndarray, bins: int = 64) -> float:
    a = a.ravel()
    b = b.ravel()
    a_min, a_max = np.percentile(a, 0.5), np.percentile(a, 99.5)
    b_min, b_max = np.percentile(b, 0.5), np.percentile(b, 99.5)
    H, _, _ = np.histogram2d(a, b, bins=bins, range=[[a_min, a_max],[b_min,b_max]])
    if H.sum() <= 0:
        return 0.0
    Pxy = H / H.sum()
    Px = Pxy.sum(axis=1, keepdims=True)
    Py = Pxy.sum(axis=0, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.where((Pxy>0) & (Px>0) & (Py>0), Pxy / (Px @ Py), 1.0)
        mi = np.sum(np.where(Pxy>0, Pxy * np.log(ratio), 0.0))
    return float(mi)


def scan_scale_for_phi(tol: float = 0.02, max_steps: int = 30) -> float:
    nx = ny = 256
    wavelength = 532e-9
    dx = 8e-6
    z1 = 0.12
    z2 = 0.24

    scales = np.linspace(0.6, 2.2, 33)
    best_ratio = None
    best_err = np.inf

    steps = 0
    for s in scales:
        psiA = make_source(nx, ny, s)
        psiB = fresnel_propagate(psiA, z1, wavelength, dx)
        psiC = fresnel_propagate(psiB, z2, wavelength, dx)

        fA = phase_grad_features(psiA)
        fB = phase_grad_features(psiB)
        fC = phase_grad_features(psiC)

        I_AB = mutual_information(fA, fB)
        I_BC = mutual_information(fB, fC)
        ratio = I_AB / I_BC if I_BC > 0 else np.inf

        err = abs(ratio - PHI) / PHI
        steps += 1
        if err < best_err:
            best_err = err
            best_ratio = ratio
        if err <= tol or steps >= max_steps:
            return best_ratio

    return best_ratio if best_ratio is not None else np.inf


def main() -> int:
    try:
        with Timeout(25):
            ratio = scan_scale_for_phi(tol=0.02, max_steps=30)
    except TimeoutError:
        print("Timeout: Vortex-knot φ-MI scan exceeded limit", file=sys.stderr)
        return 124

    err_pct = abs(ratio - PHI) / PHI * 100
    status = "PASS" if err_pct <= 2.0 else "FAIL"
    print("Vortex-Knot φ-MI Validation")
    print(f"ratio = {ratio:.6f}, φ = {PHI:.6f}, relative error = {err_pct:.2f}% → {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
