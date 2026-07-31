"""
Inverse Matrix Service — Phase 4
Method: Adjoint / Classical Adjugate  →  A⁻¹ = adj(A) / det(A)
Supports 2×2 (formula), 3×3 and NxN (cofactor matrix → adjoint → inverse)
"""

import numpy as np


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
        if abs(float(v) - round(float(v))) < 1e-9:
            return str(int(round(float(v))))
        s = f'{float(v):.4f}'.rstrip('0').rstrip('.')
        return s if s not in ('', '-') else '0'

    @staticmethod
    def _latex(mat, name=None):
        rows = [' & '.join(InverseService._n(x) for x in row) for row in mat]
        body = ' \\\\ '.join(rows)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'{name} = {s}' if name else s

    @staticmethod
    def _vmatrix(mat):
        rows = [' & '.join(InverseService._n(x) for x in row) for row in mat]
        return '\\begin{vmatrix} ' + ' \\\\ '.join(rows) + ' \\end{vmatrix}'

    @staticmethod
    def _minor(A, i, j):
        return np.delete(np.delete(A, i, 0), j, 1)

    @staticmethod
    def _display(mat):
        return [[InverseService._n(x) for x in row] for row in mat.tolist()]

    # -----------------------------------------------------------------------
    # Main entry
    # -----------------------------------------------------------------------
    @staticmethod
    def calculate(matrix_data):
        A, err = InverseService.parse(matrix_data)
        if err:
            return {'success': False, 'error': err}

        n   = A.shape[0]
        det = float(np.linalg.det(A))
        _n  = InverseService._n

        if abs(det) < 1e-10:
            return {
                'success': False,
                'error': f'Matrix is singular (det = {_n(det)} ≈ 0). '
                         'No inverse exists for a singular matrix.',
                'determinant': _n(det)
            }

        # Compute cofactor matrix
        C = np.zeros_like(A)
        for i in range(n):
            for j in range(n):
                minor = InverseService._minor(A, i, j)
                C[i, j] = ((-1) ** (i + j)) * np.linalg.det(minor)

        adj = C.T                        # adjoint = transpose of cofactor matrix
        inv = adj / det                  # inverse

        steps = [
            {'title': '① Input Matrix',
             'text':  f'Square matrix A ({n}×{n})',
             'latex': InverseService._latex(A, 'A')},
            {'title': '② Compute the Determinant',
             'text':  f'det(A) = {_n(det)}  (≠ 0 ✓ — inverse exists)',
             'latex': InverseService._vmatrix(A) + f' = {_n(det)}'},
            {'title': '③ Compute Cofactor Matrix C',
             'text':  'Cᵢⱼ = (−1)^(i+j) × det(minor Mᵢⱼ)',
             'latex': f'C = {InverseService._latex(C)}'},
            {'title': '④ Compute Adjoint (adj A = Cᵀ)',
             'text':  'The adjoint is the transpose of the cofactor matrix.',
             'latex': f'\\text{{adj}}(A) = C^T = {InverseService._latex(adj)}'},
            {'title': '⑤ Compute Inverse',
             'text':  f'A⁻¹ = adj(A) / det(A) = adj(A) / {_n(det)}',
             'latex': f'A^{{-1}} = \\frac{{\\text{{adj}}(A)}}{{\\det(A)}} = '
                      f'\\frac{{1}}{{{_n(det)}}} {InverseService._latex(adj)}'},
            {'title': '⑥ Result',
             'text':  'Final inverse matrix:',
             'latex': f'A^{{-1}} = {InverseService._latex(inv)}'},
            {'title': '⑦ Verification  A · A⁻¹ = I',
             'text':  'Multiplying A by A⁻¹ should give the identity matrix.',
             'latex': f'A \\cdot A^{{-1}} = {InverseService._latex(np.round(A @ inv, 6))}'},
        ]

        return {
            'success': True,
            'operation': 'Matrix Inverse  A⁻¹',
            'determinant': _n(det),
            'cofactor': C.tolist(),
            'adjoint': adj.tolist(),
            'result': inv.tolist(),
            'result_display': InverseService._display(inv),
            'result_latex': InverseService._latex(inv),
            'steps': steps
        }
