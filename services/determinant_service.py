"""
Determinant Service — Phase 3
Supports: 2×2 (formula), 3×3 (cofactor expansion), NxN (LU + cofactor steps)
"""

import numpy as np


class DeterminantService:

    @staticmethod
    def parse(data):
        try:
            A = np.array(data, dtype=float)
            if A.ndim != 2 or A.shape[0] != A.shape[1]:
                return None, 'Determinant requires a square matrix.'
            return A, None
        except (ValueError, TypeError) as exc:
            return None, str(exc)

    @staticmethod
    def _n(v):
        if abs(float(v) - round(float(v))) < 1e-9:
            return str(int(round(float(v))))
        return f'{float(v):.6f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex(mat):
        rows = [' & '.join(DeterminantService._n(x) for x in row) for row in mat]
        return '\\begin{bmatrix} ' + ' \\\\ '.join(rows) + ' \\end{bmatrix}'

    @staticmethod
    def _det_latex(mat):
        """Determinant notation |...|"""
        rows = [' & '.join(DeterminantService._n(x) for x in row) for row in mat]
        return '\\begin{vmatrix} ' + ' \\\\ '.join(rows) + ' \\end{vmatrix}'

    @staticmethod
    def _minor(A, row, col):
        return np.delete(np.delete(A, row, 0), col, 1)

    @staticmethod
    def calculate(matrix_data):
        A, err = DeterminantService.parse(matrix_data)
        if err:
            return {'success': False, 'error': err}
        n = A.shape[0]

        if n == 1:
            det = float(A[0, 0])
            return {
                'success': True, 'result': det,
                'result_display': DeterminantService._n(det),
                'result_latex': f'\\det(A) = {DeterminantService._n(det)}',
                'steps': [
                    {'title': '① 1×1 Determinant',
                     'text': 'det of a 1×1 matrix is just the single element.',
                     'latex': f'\\det(A) = {DeterminantService._n(det)}'}
                ]
            }

        if n == 2:
            return DeterminantService._det2x2(A)
        if n == 3:
            return DeterminantService._det3x3(A)
        return DeterminantService._detNxN(A)

    # -----------------------------------------------------------------------
    # 2×2
    # -----------------------------------------------------------------------
    @staticmethod
    def _det2x2(A):
        a, b = A[0, 0], A[0, 1]
        c, d = A[1, 0], A[1, 1]
        det  = float(a * d - b * c)
        _n   = DeterminantService._n
        return {
            'success': True,
            'result': det,
            'result_display': _n(det),
            'result_latex': f'\\det(A) = {_n(det)}',
            'steps': [
                {'title': '① Write the Matrix',
                 'text':  '2×2 determinant formula: det = ad − bc',
                 'latex': DeterminantService._det_latex(A)},
                {'title': '② Apply Formula',
                 'text':  'det(A) = ad − bc',
                 'latex': f'\\det(A) = ({_n(a)})({_n(d)}) - ({_n(b)})({_n(c)})'},
                {'title': '③ Compute',
                 'text':  f'{_n(a*d)} − ({_n(b*c)}) = {_n(det)}',
                 'latex': f'\\det(A) = {_n(a*d)} - ({_n(b*c)}) = {_n(det)}'},
                {'title': '④ Result',
                 'text':  f'det(A) = {_n(det)}',
                 'latex': f'\\boxed{{\\det(A) = {_n(det)}}}'},
            ]
        }

    # -----------------------------------------------------------------------
    # 3×3 (Sarrus + cofactor expansion for steps)
    # -----------------------------------------------------------------------
    @staticmethod
    def _det3x3(A):
        _n = DeterminantService._n
        # Cofactor expansion along row 0
        steps = []
        det   = float(np.linalg.det(A))

        steps.append({'title': '① Write the Matrix',
                       'text':  'Compute using cofactor expansion along the first row.',
                       'latex': DeterminantService._det_latex(A)})

        expansion_terms = []
        for j in range(3):
            sign  = (-1) ** j
            minor = DeterminantService._minor(A, 0, j)
            m_det = float(minor[0,0]*minor[1,1] - minor[0,1]*minor[1,0])
            term  = sign * A[0, j] * m_det
            sign_str = '+' if sign > 0 else '-'
            expansion_terms.append(
                f'{sign_str}{_n(A[0,j])} \\cdot {DeterminantService._det_latex(minor)}'
            )
            steps.append({'title': f'② Cofactor C₁{j+1}  (sign={sign_str}1)',
                           'text':  f'Element A[1][{j+1}]={_n(A[0,j])}, minor:',
                           'latex': f'C_{{1{j+1}}} = ({sign_str}1) \\cdot {_n(A[0,j])} '
                                    f'\\cdot {DeterminantService._det_latex(minor)} = {_n(term)}'})

        steps.append({'title': '③ Sum of Cofactor Terms',
                       'text':  'det(A) = sum of all cofactor terms',
                       'latex': f'\\det(A) = {" ".join(expansion_terms)}'})

        steps.append({'title': '④ Result',
                       'text':  f'det(A) = {_n(det)}',
                       'latex': f'\\boxed{{\\det(A) = {_n(det)}}}'})

        return {
            'success': True,
            'result': det,
            'result_display': _n(det),
            'result_latex': f'\\det(A) = {_n(det)}',
            'steps': steps
        }

    # -----------------------------------------------------------------------
    # NxN using numpy + Gaussian elimination explanation
    # -----------------------------------------------------------------------
    @staticmethod
    def _detNxN(A):
        _n  = DeterminantService._n
        n   = A.shape[0]
        det = float(np.linalg.det(A))
        # Show LU pivots explanation
        # We'll do a manual Gaussian elimination to show row ops
        M   = A.astype(float).copy()
        sign_count = 0
        product_diag = []
        elim_steps = []

        for col in range(n):
            # Find pivot
            pivot_row = None
            for row in range(col, n):
                if abs(M[row, col]) > 1e-12:
                    pivot_row = row
                    break
            if pivot_row is None:
                break
            if pivot_row != col:
                M[[col, pivot_row]] = M[[pivot_row, col]]
                sign_count += 1
                elim_steps.append(f'R{col+1} ↔ R{pivot_row+1}  (sign changes, ×−1)')
            for row in range(col + 1, n):
                if abs(M[row, col]) < 1e-12:
                    continue
                factor = M[row, col] / M[col, col]
                M[row] -= factor * M[col]
                elim_steps.append(f'R{row+1} ← R{row+1} − ({_n(factor)})·R{col+1}')

        diag_product = np.prod([M[i, i] for i in range(n)])
        sign_val = (-1) ** sign_count

        steps = [
            {'title': '① Input Matrix',
             'text':  f'{n}×{n} matrix — using Gaussian elimination to triangularize.',
             'latex': DeterminantService._det_latex(A)},
            {'title': '② Row Operations',
             'text':  'Apply elimination (sign changes tracked for row swaps):',
             'list':  elim_steps if elim_steps else ['No row swaps needed.']},
            {'title': '③ Upper Triangular Form',
             'text':  'After elimination, det = (sign) × product of diagonal:',
             'latex': DeterminantService._det_latex(M)},
            {'title': '④ Result',
             'text':  f'det = (−1)^{sign_count} × {" × ".join(_n(M[i,i]) for i in range(n))} = {_n(det)}',
             'latex': f'\\boxed{{\\det(A) = {_n(det)}}}'},
        ]
        return {
            'success': True,
            'result': det,
            'result_display': _n(det),
            'result_latex': f'\\det(A) = {_n(det)}',
            'steps': steps
        }
