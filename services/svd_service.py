"""
SVD (Singular Value Decomposition) Service
Computes A = U·Σ·Vᵀ with full step-by-step LaTeX proofs.
"""
import numpy as np


class SVDService:

    # ------------------------------------------------------------------
    # Internal helpers
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
        rows = [' & '.join(SVDService._n(x) for x in row) for row in mat]
        body = ' \\\\ '.join(rows)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'{name} = {s}' if name else s

    @staticmethod
    def _display(mat):
        return [[SVDService._n(x) for x in row] for row in mat.tolist()]

    # ------------------------------------------------------------------
    # Main decomposition
    # ------------------------------------------------------------------

    @staticmethod
    def decompose(matrix_data):
        A, err = SVDService._parse(matrix_data)
        if err:
            return {'success': False, 'error': err}

        m, n = A.shape

        try:
            U, S, Vt = np.linalg.svd(A, full_matrices=False)
        except Exception as exc:
            return {'success': False, 'error': f'SVD computation failed: {exc}'}

        Sigma = np.diag(S)

        # Clean near-zero values
        U[np.abs(U) < 1e-10]      = 0
        Sigma[np.abs(Sigma) < 1e-10] = 0
        Vt[np.abs(Vt) < 1e-10]    = 0

        rank      = int(np.sum(S > 1e-10))
        condition = float(S[0] / S[-1]) if S[-1] > 1e-10 else float('inf')

        sv_str = ', '.join(f'σ{i+1} = {SVDService._n(s)}' for i, s in enumerate(S))

        # Verify  A ≈ U·Σ·Vᵀ
        reconstructed = U @ Sigma @ Vt
        residual = float(np.max(np.abs(A - reconstructed)))

        steps = [
            {
                'title': '① Input Matrix A',
                'text':  f'Rectangular matrix A is {m}×{n}.',
                'latex': SVDService._latex(A, 'A')
            },
            {
                'title': '② Left Singular Vectors U',
                'text':  (f'Columns of U are orthonormal eigenvectors of AAᵀ ({m}×{m}). '
                          'They describe the "input" directions.'),
                'latex': SVDService._latex(U, 'U')
            },
            {
                'title': '③ Singular Values Σ (diagonal)',
                'text':  f'{sv_str}. Singular values are always ≥ 0 and sorted in descending order.',
                'latex': SVDService._latex(Sigma, '\\Sigma')
            },
            {
                'title': '④ Right Singular Vectors Vᵀ',
                'text':  (f'Rows of Vᵀ are orthonormal eigenvectors of AᵀA ({n}×{n}). '
                          'They describe the "output" directions.'),
                'latex': SVDService._latex(Vt, 'V^T')
            },
            {
                'title': '⑤ Key Properties',
                'text':  (f'Rank = {rank}  |  '
                          f'Condition number κ(A) = σ₁/σ_r = {SVDService._n(condition)}  |  '
                          f'Frobenius norm ‖A‖_F = {SVDService._n(float(np.linalg.norm(A, "fro")))}'),
                'latex': (f'\\text{{rank}}(A) = {rank},\\quad '
                          f'\\kappa(A) = {SVDService._n(condition)},\\quad '
                          f'\\|A\\|_F = {SVDService._n(float(np.linalg.norm(A, "fro")))}')
            },
            {
                'title': '⑥ Verification  A ≈ UΣVᵀ',
                'text':  f'Maximum reconstruction error ‖A − UΣVᵀ‖∞ = {residual:.2e}  {"✓ Valid" if residual < 1e-8 else "⚠ Check inputs"}',
                'latex': SVDService._latex(reconstructed, 'U\\Sigma V^T')
            },
        ]

        return {
            'success':          True,
            'operation':        'SVD  A = UΣVᵀ',
            'm':                m,
            'n':                n,
            'rank':             rank,
            'condition_number': condition if condition != float('inf') else 'inf',
            'singular_values':  [SVDService._n(s) for s in S],
            'U_display':        SVDService._display(U),
            'Sigma_display':    SVDService._display(Sigma),
            'Vt_display':       SVDService._display(Vt),
            'U_latex':          SVDService._latex(U, 'U'),
            'Sigma_latex':      SVDService._latex(Sigma, '\\Sigma'),
            'Vt_latex':         SVDService._latex(Vt, 'V^T'),
            'steps':            steps,
        }
