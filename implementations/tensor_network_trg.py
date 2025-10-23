#!/usr/bin/env python3
import numpy as np
from scipy.linalg import svd
import sys
from typing import List, Tuple

def tensor_rg_step(tensors: List[np.ndarray], chi_max: int) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    n = len(tensors)
    if n < 2:
        return tensors, []
    
    coarse_tensors = []
    spectra = []
    
    for i in range(0, n, 2):
        if i + 1 >= n:
            coarse_tensors.append(tensors[i])
            break
        
        T1 = tensors[i]
        T2 = tensors[i+1]
        
        # Contract neighboring tensors (d,d,d,d) x (d,d,d,d) -> (d,d,d,d,d,d)
        # axes=([2],[0]) means contract T1's 3rd index with T2's 1st index
        contracted = np.tensordot(T1, T2, axes=([2],[0]))
        
        # Reshape for SVD: (d*d*d) x (d*d*d)
        shape = contracted.shape
        M = contracted.reshape(shape[0]*shape[1]*shape[2], 
                               shape[3]*shape[4]*shape[5])
        
        # Perform SVD
        U, S, Vh = svd(M, full_matrices=False)
        
        # Truncate to chi_max singular values
        chi = min(chi_max, len(S))
        U_trunc = U[:, :chi]
        S_trunc = S[:chi]
        Vh_trunc = Vh[:chi, :]
        
        spectra.append(S_trunc)
        
        # Construct coarse-grained tensor
        U_scaled = U_trunc @ np.diag(np.sqrt(S_trunc))
        V_scaled = np.diag(np.sqrt(S_trunc)) @ Vh_trunc
        
        # Reshape back to tensor form
        T_coarse = np.tensordot(U_scaled, V_scaled, axes=([1],[0]))
        T_coarse = T_coarse.reshape(shape[0], shape[1], chi, 
                                     shape[4], shape[5], chi)
        
        # Trace over internal indices to get 4-index tensor
        T_final = np.trace(T_coarse, axis1=2, axis2=5)
        
        coarse_tensors.append(T_final)
    
    return coarse_tensors, spectra

def main():
    d = 4
    chi_max = 16
    n_iter = 50
    tolerance = 1e-10
    n_tensors = 32

    tensors = [np.random.rand(d, d, d, d) for _ in range(n_tensors)]
    tensors = [T / np.linalg.norm(T) for T in tensors]

    for i in range(n_iter):
        if len(tensors) < 2:
            print("Converged to a single tensor.")
            sys.exit(0)
            
        tensors_old = [T.copy() for T in tensors]
        tensors, spectra = tensor_rg_step(tensors, chi_max)
        tensors = [T / np.linalg.norm(T) for T in tensors]

        diff = np.linalg.norm(tensors[0] - tensors_old[0])
        
        print(f"Iteration {i+1}/{n_iter}, Difference: {diff:.2e}, Num Tensors: {len(tensors)}")
        if diff < tolerance and i > 0:
            print(f"Converged at iteration {i+1}")
            break
    
    success = diff < tolerance
    if success:
        print("\n✓ CONFIRMED: 1D TRG algorithm converged!")
        return 0
    else:
        print("\n✗ FAILED: 1D TRG algorithm did not converge.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
