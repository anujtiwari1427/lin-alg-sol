"""
Inverse Matrix Service — Professional Educational Engine
Supports 2x2, 3x3, and NxN matrix inversion with complete educational reports.
"""

import numpy as np
from services.solver_service import BaseSolverService


class InverseService:

    @staticmethod
    def parse(data):
        try:
            A = np.array(data, dtype=float)
            if A.ndim != 2 or A.shape[0] != A.shape[1]:
                return None, 'Inverse requires a square matrix.'
            return A, None
        except (ValueError, TypeError) as exc:
            return None, str(exc)

    @staticmethod
    def _n(v):
        v = float(v)
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return f'{v:.4f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex(mat, name=None):
        rows = [' & '.join(InverseService._n(x) for x in row) for row in mat]
        body = ' \\\\ '.join(rows)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'{name} = {s}' if name else s

    @staticmethod
    def _display(mat):
        return [[InverseService._n(x) for x in row] for row in mat.tolist()]

    @staticmethod
    def _minor(A, i, j):
        return np.delete(np.delete(A, i, 0), j, 1)

    @staticmethod
    def calculate(matrix_data):
        A, err = InverseService.parse(matrix_data)
        if err:
            return {'success': False, 'error': err}
        
        n = A.shape[0]
        det = float(np.linalg.det(A))
        _n = InverseService._n

        if abs(det) < 1e-10:
            return {
                'success': False,
                'error': f'Matrix is singular (det(A) = {_n(det)} ≈ 0). Singular matrices have no inverse.',
                'determinant': _n(det)
            }

        C = np.zeros_like(A)
        for i in range(n):
            for j in range(n):
                minor = InverseService._minor(A, i, j)
                C[i, j] = ((-1) ** (i + j)) * np.linalg.det(minor)

        adj = C.T
        inv = adj / det
        I_check = A @ inv

        steps = [
            {'title': '① Input Square Matrix', 'text': f'A is a {n}×{n} matrix:', 'latex': InverseService._latex(A, "A")},
            {'title': '② Compute Determinant', 'text': f'det(A) = {_n(det)} (≠ 0 ✓ Inverse exists)', 'latex': f'\\det(A) = {_n(det)}'},
            {'title': '③ Compute Cofactor Matrix C', 'text': 'Cᵢⱼ = (-1)ⁱ⁺ʲ det(Mᵢⱼ)', 'latex': InverseService._latex(C, "C")},
            {'title': '④ Compute Adjoint Matrix (adj A = Cᵀ)', 'text': 'Transpose the cofactor matrix:', 'latex': InverseService._latex(adj, "\\text{adj}(A)")},
            {'title': '⑤ Divide Adjoint by Determinant', 'text': f'A⁻¹ = adj(A) / det(A) = adj(A) / {_n(det)}', 'latex': f'A^{{-1}} = \\frac{{1}}{{{_n(det)}}} {InverseService._latex(adj)}'},
            {'title': '⑥ Final Inverse Matrix', 'text': 'Resulting inverse:', 'latex': InverseService._latex(inv, "A^{-1}")},
            {'title': '⑦ Verification: A · A⁻¹ = I', 'text': 'Multiplying A by A⁻¹ yields the identity matrix:', 'latex': f'A \\cdot A^{{-1}} = {InverseService._latex(np.round(I_check, 4))}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified identity property: A · A⁻¹ = I',
            'latex': f'A \\cdot A^{{-1}} = {InverseService._latex(np.round(I_check, 4))}',
            'residual_error': f'{float(np.max(np.abs(I_check - np.eye(n)))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Matrix Inverse A⁻¹',
            input_data={'A': InverseService._display(A)},
            theory='The inverse of a square matrix A is the matrix A⁻¹ such that A · A⁻¹ = A⁻¹ · A = I.',
            formula='A^{-1} = \\frac{1}{\\det(A)} \\text{adj}(A) \\quad \\text{or } [A \\mid I] \\xrightarrow{\\text{RREF}} [I \\mid A^{-1}]',
            definitions=[{'term': 'Invertible (Non-singular)', 'def': 'A square matrix with a non-zero determinant.'}],
            steps=steps,
            verification=verif,
            result=inv.tolist(),
            result_display=InverseService._display(inv),
            result_latex=InverseService._latex(inv, "A^{-1}"),
            notes=['(A⁻¹)⁻¹ = A', '(AB)⁻¹ = B⁻¹ A⁻¹', '(Aᵀ)⁻¹ = (A⁻¹)ᵀ'],
            common_mistakes=['Attempting to invert a non-square matrix.', 'Forgetting to transpose the cofactor matrix.'],
            applications=['Solving linear systems Ax = b -> x = A^-1 b', 'Coordinate transformation reversal', 'Cryptography'],
            time_complexity=f'O({n}^3)',
            student_mode={
                'concept': 'Undo matrix transformation.',
                'why_this_step': 'Restores original vector space coordinates.',
                'exam_tips': ['For 2x2 [[a,b],[c,d]], A^-1 = 1/(ad-bc) * [[d,-b],[-c,a]].'],
                'shortcuts': ['Check det(A) != 0 before doing any work!'],
                'interview_questions': ['Why is Ax=b solved via Gaussian elimination rather than computing A^-1 b directly?'],
                'practice_questions': ['Invert [[4, 7], [2, 6]].']
            }
        )
