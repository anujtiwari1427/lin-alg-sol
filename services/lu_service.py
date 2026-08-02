"""
LU Decomposition Service
Computes PA = LU factorisation using scipy and generates full step-by-step proofs.
"""
import numpy as np
from scipy.linalg import lu


class LUService:

    # ------------------------------------------------------------------
    # Internal helpers (mirrors MatrixService conventions)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(data):
        try:
            arr = np.array(data, dtype=float)
            if arr.ndim != 2:
                return None, 'Input must be a 2-D matrix.'
            if arr.size == 0:
                return None, 'Matrix cannot be empty.'
            return arr, None
        except (ValueError, TypeError) as exc:
            return None, f'Invalid matrix data: {exc}'

    @staticmethod
    def _n(v):
        if abs(float(v) - round(float(v))) < 1e-9:
            return str(int(round(float(v))))
        return f'{float(v):.4f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex(mat, name=None):
        rows = [' & '.join(LUService._n(x) for x in row) for row in mat]
        body = ' \\\\ '.join(rows)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'{name} = {s}' if name else s

    @staticmethod
    def _display(mat):
        return [[LUService._n(x) for x in row] for row in mat.tolist()]

    # ------------------------------------------------------------------
    # Main decomposition
    # ------------------------------------------------------------------

    @staticmethod
    def decompose(matrix_data):
        A, err = LUService._parse(matrix_data)
        if err:
            return {'success': False, 'error': err}

        if A.shape[0] != A.shape[1]:
            return {
                'success': False,
                'error': f'LU decomposition requires a square matrix. Got {A.shape[0]}×{A.shape[1]}.'
            }

        n = A.shape[0]

        try:
            P, L, U = lu(A)         # scipy: P·A = L·U
        except Exception as exc:
            return {'success': False, 'error': f'LU computation failed: {exc}'}

        # Clean near-zero values
        P[np.abs(P) < 1e-10] = 0
        L[np.abs(L) < 1e-10] = 0
        U[np.abs(U) < 1e-10] = 0

        # Verify
        PA   = P @ A
        LU_  = L @ U
        residual = float(np.max(np.abs(PA - LU_)))

        # Count row swaps encoded in P
        swaps = int(round(n - np.trace(P))) // 2

        steps = [
            {
                'title': '① Input Matrix A',
                'text':  f'Square matrix A is {n}×{n}.',
                'latex': LUService._latex(A, 'A')
            },
            {
                'title': '② Permutation Matrix P',
                'text':  (f'P encodes {swaps} row swap(s) to avoid zero pivots. '
                          'PA reorders rows of A so Gaussian elimination stays numerically stable.'),
                'latex': LUService._latex(P, 'P')
            },
            {
                'title': '③ Lower-Triangular L',
                'text':  'All diagonal entries are 1. Below-diagonal entries are the Gaussian elimination multipliers.',
                'latex': LUService._latex(L, 'L')
            },
            {
                'title': '④ Upper-Triangular U',
                'text':  'Row echelon form of PA. Pivot positions are on the diagonal.',
                'latex': LUService._latex(U, 'U')
            },
            {
                'title': '⑤ Verification  PA = LU',
                'text':  f'Maximum residual ‖PA − LU‖∞ = {residual:.2e}  {"✓ Valid" if residual < 1e-8 else "⚠ Check inputs"}',
                'latex': f'PA = {LUService._latex(PA)} \\approx LU = {LUService._latex(LU_)}'
            },
        ]

        return {
            'success':    True,
            'operation':  'LU Decomposition  PA = LU',
            'n':          n,
            'L':          L.tolist(),
            'U':          U.tolist(),
            'P':          P.tolist(),
            'L_display':  LUService._display(L),
            'U_display':  LUService._display(U),
            'P_display':  LUService._display(P),
            'L_latex':    LUService._latex(L, 'L'),
            'U_latex':    LUService._latex(U, 'U'),
            'P_latex':    LUService._latex(P, 'P'),
            'residual':   residual,
            'steps':      steps,
        }
