"""
Matrix Operations Service — Phase 2
Supports: Addition, Subtraction, Multiplication, Scalar Multiplication,
          Transpose, Trace, Rank (all with step-by-step explanations)
"""

import numpy as np


class MatrixService:

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def parse(data):
        """Parse nested-list → numpy float64 matrix. Returns (matrix, error)."""
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
        """Format a float cleanly (no trailing zeros)."""
        if abs(float(v) - round(float(v))) < 1e-9:
            return str(int(round(float(v))))
        return f'{float(v):.4f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex(mat, name=None):
        """Convert numpy matrix to LaTeX \\bmatrix string."""
        rows = [' & '.join(MatrixService._n(x) for x in row) for row in mat]
        body = ' \\\\ '.join(rows)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'{name} = {s}' if name else s

    @staticmethod
    def _display(mat):
        """Return nested list of clean strings for template rendering."""
        return [[MatrixService._n(x) for x in row] for row in mat.tolist()]

    @staticmethod
    def _ref(A):
        """Reduced row-echelon form for rank display (returns copy)."""
        M = A.astype(float).copy()
        m, n = M.shape
        pivot_row = 0
        for col in range(n):
            if pivot_row >= m:
                break
            # Find best pivot
            best = max(range(pivot_row, m), key=lambda r: abs(M[r, col]))
            if abs(M[best, col]) < 1e-10:
                continue
            M[[pivot_row, best]] = M[[best, pivot_row]]
            M[pivot_row] /= M[pivot_row, col]
            for r in range(m):
                if r != pivot_row:
                    M[r] -= M[r, col] * M[pivot_row]
            pivot_row += 1
        M[np.abs(M) < 1e-10] = 0
        return M

    # -----------------------------------------------------------------------
    # ADDITION
    # -----------------------------------------------------------------------
    @staticmethod
    def addition(a_data, b_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = MatrixService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if A.shape != B.shape:
            return {'success': False, 'error':
                    f'Shapes must match: A is {A.shape[0]}×{A.shape[1]}, '
                    f'B is {B.shape[0]}×{B.shape[1]}.'}
        R = A + B
        m, n = A.shape
        elem_calcs = []
        for i in range(m):
            for j in range(n):
                elem_calcs.append(f'({MatrixService._n(A[i,j])}) + ({MatrixService._n(B[i,j])}) = {MatrixService._n(R[i,j])}')

        return {
            'success': True,
            'operation': 'Matrix Addition  A + B',
            'result': R.tolist(),
            'result_display': MatrixService._display(R),
            'result_latex': MatrixService._latex(R),
            'steps': [
                {'title': '① Compatibility Check',
                 'text':  f'Both A and B are {m}×{n}. ✓ Addition is valid.',
                 'latex': f'{MatrixService._latex(A, "A")} \\qquad {MatrixService._latex(B, "B")}'},
                {'title': '② Rule',
                 'text':  'Corresponding elements are added: (A+B)ᵢⱼ = Aᵢⱼ + Bᵢⱼ',
                 'latex': '(A+B)_{ij} = A_{ij} + B_{ij}'},
                {'title': '③ Element Calculations',
                 'text':  'Computing each position:',
                 'list':  elem_calcs},
                {'title': '④ Result',
                 'text':  'Final answer:',
                 'latex': f'A + B = {MatrixService._latex(R)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # SUBTRACTION
    # -----------------------------------------------------------------------
    @staticmethod
    def subtraction(a_data, b_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = MatrixService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if A.shape != B.shape:
            return {'success': False, 'error':
                    f'Shapes must match: A is {A.shape[0]}×{A.shape[1]}, '
                    f'B is {B.shape[0]}×{B.shape[1]}.'}
        R = A - B
        m, n = A.shape
        elem_calcs = [
            f'({MatrixService._n(A[i,j])}) − ({MatrixService._n(B[i,j])}) = {MatrixService._n(R[i,j])}'
            for i in range(m) for j in range(n)
        ]
        return {
            'success': True,
            'operation': 'Matrix Subtraction  A − B',
            'result': R.tolist(),
            'result_display': MatrixService._display(R),
            'result_latex': MatrixService._latex(R),
            'steps': [
                {'title': '① Compatibility Check',
                 'text':  f'Both A and B are {m}×{n}. ✓ Subtraction is valid.',
                 'latex': f'{MatrixService._latex(A,"A")} \\qquad {MatrixService._latex(B,"B")}'},
                {'title': '② Rule',
                 'text':  '(A−B)ᵢⱼ = Aᵢⱼ − Bᵢⱼ',
                 'latex': '(A-B)_{ij} = A_{ij} - B_{ij}'},
                {'title': '③ Element Calculations',
                 'text':  'Computing each position:',
                 'list':  elem_calcs},
                {'title': '④ Result',
                 'text':  'Final answer:',
                 'latex': f'A - B = {MatrixService._latex(R)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # MULTIPLICATION
    # -----------------------------------------------------------------------
    @staticmethod
    def multiplication(a_data, b_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = MatrixService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if A.shape[1] != B.shape[0]:
            return {'success': False, 'error':
                    f'Cols of A ({A.shape[1]}) must equal rows of B ({B.shape[0]}).'}
        R = A @ B
        m, k, n = A.shape[0], A.shape[1], B.shape[1]
        # Show all element dot-products (capped at 9 for readability)
        shown = []
        for i in range(m):
            for j in range(n):
                terms = ' + '.join(
                    f'{MatrixService._n(A[i,p])}×{MatrixService._n(B[p,j])}'
                    for p in range(k))
                shown.append(f'R[{i+1}][{j+1}] = {terms} = {MatrixService._n(R[i,j])}')
                if len(shown) >= 9:
                    break
            if len(shown) >= 9:
                break

        return {
            'success': True,
            'operation': 'Matrix Multiplication  A × B',
            'result': R.tolist(),
            'result_display': MatrixService._display(R),
            'result_latex': MatrixService._latex(R),
            'steps': [
                {'title': '① Compatibility Check',
                 'text':  f'A is {m}×{k}, B is {k}×{n}. ✓ Inner dimensions match ({k}). Result is {m}×{n}.',
                 'latex': f'{MatrixService._latex(A,"A")} \\qquad {MatrixService._latex(B,"B")}'},
                {'title': '② Dot-Product Rule',
                 'text':  'Each element of AB = dot product of a row of A with a column of B.',
                 'latex': f'(AB)_{{ij}} = \\sum_{{p=1}}^{{{k}}} A_{{ip}} \\cdot B_{{pj}}'},
                {'title': '③ Element Calculations',
                 'text':  f'Showing first {len(shown)} elements:',
                 'list':  shown},
                {'title': '④ Result',
                 'text':  f'Product A×B ({m}×{n}):',
                 'latex': f'A \\times B = {MatrixService._latex(R)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # SCALAR MULTIPLICATION
    # -----------------------------------------------------------------------
    @staticmethod
    def scalar_multiplication(a_data, scalar):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        try:
            k = float(scalar)
        except (ValueError, TypeError):
            return {'success': False, 'error': 'Scalar must be a number.'}
        R = k * A
        m, n = A.shape
        shown = [
            f'{MatrixService._n(k)} × {MatrixService._n(A[i,j])} = {MatrixService._n(R[i,j])}'
            for i in range(m) for j in range(n)
        ]
        return {
            'success': True,
            'operation': f'Scalar Multiplication  {MatrixService._n(k)}·A',
            'result': R.tolist(),
            'result_display': MatrixService._display(R),
            'result_latex': MatrixService._latex(R),
            'steps': [
                {'title': '① Inputs',
                 'text':  f'Scalar k = {MatrixService._n(k)}, Matrix A is {m}×{n}',
                 'latex': f'k={MatrixService._n(k)}, \\quad {MatrixService._latex(A,"A")}'},
                {'title': '② Rule',
                 'text':  'Every element is multiplied by k',
                 'latex': f'(kA)_{{ij}} = {MatrixService._n(k)} \\cdot A_{{ij}}'},
                {'title': '③ Element Calculations',
                 'text':  'Computing each position:',
                 'list':  shown},
                {'title': '④ Result',
                 'text':  'Final answer:',
                 'latex': f'{MatrixService._n(k)} \\cdot A = {MatrixService._latex(R)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # TRANSPOSE
    # -----------------------------------------------------------------------
    @staticmethod
    def transpose(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        R = A.T
        m, n = A.shape
        shown = [
            f'Aᵀ[{j+1}][{i+1}] = A[{i+1}][{j+1}] = {MatrixService._n(A[i,j])}'
            for i in range(m) for j in range(n)
        ]
        return {
            'success': True,
            'operation': 'Matrix Transpose  Aᵀ',
            'result': R.tolist(),
            'result_display': MatrixService._display(R),
            'result_latex': MatrixService._latex(R),
            'steps': [
                {'title': '① Input',
                 'text':  f'A is {m}×{n}',
                 'latex': MatrixService._latex(A, 'A')},
                {'title': '② Transpose Rule',
                 'text':  'Rows become columns and columns become rows: (Aᵀ)ᵢⱼ = Aⱼᵢ',
                 'latex': '(A^T)_{ij} = A_{ji}'},
                {'title': '③ Element Mapping',
                 'text':  'Each element mapped:',
                 'list':  shown},
                {'title': '④ Result',
                 'text':  f'Transpose Aᵀ is {n}×{m}:',
                 'latex': f'A^T = {MatrixService._latex(R)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # TRACE
    # -----------------------------------------------------------------------
    @staticmethod
    def trace(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error':
                    f'Trace requires a square matrix. Got {A.shape[0]}×{A.shape[1]}.'}
        n = A.shape[0]
        diag = [A[i, i] for i in range(n)]
        tr   = float(np.trace(A))
        diag_str = ' + '.join(MatrixService._n(d) for d in diag)
        return {
            'success': True,
            'operation': 'Matrix Trace  tr(A)',
            'result': tr,
            'result_display': MatrixService._n(tr),
            'result_latex': f'\\text{{tr}}(A) = {MatrixService._n(tr)}',
            'steps': [
                {'title': '① Input Matrix',
                 'text':  f'Square matrix A ({n}×{n})',
                 'latex': MatrixService._latex(A, 'A')},
                {'title': '② Definition',
                 'text':  'The trace is the sum of all main-diagonal elements.',
                 'latex': f'\\text{{tr}}(A) = \\sum_{{i=1}}^{{{n}}} A_{{ii}}'},
                {'title': '③ Diagonal Elements',
                 'text':  ', '.join(f'A[{i+1}][{i+1}]={MatrixService._n(diag[i])}' for i in range(n)),
                 'latex': f'\\text{{diag}} = ({", ".join(MatrixService._n(d) for d in diag)})'},
                {'title': '④ Result',
                 'text':  f'{diag_str} = {MatrixService._n(tr)}',
                 'latex': f'\\text{{tr}}(A) = {diag_str} = {MatrixService._n(tr)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # RANK
    # -----------------------------------------------------------------------
    @staticmethod
    def rank(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        m, n = A.shape
        r    = int(np.linalg.matrix_rank(A))
        ref  = MatrixService._ref(A.copy())
        note = ('Full rank — all rows are linearly independent.'
                if r == min(m, n) else
                f'Rank-deficient — {min(m,n)-r} linearly dependent row(s) detected.')
        return {
            'success': True,
            'operation': 'Matrix Rank',
            'result': r,
            'result_display': str(r),
            'result_latex': f'\\text{{rank}}(A) = {r}',
            'steps': [
                {'title': '① Input Matrix',
                 'text':  f'Matrix A is {m}×{n}',
                 'latex': MatrixService._latex(A, 'A')},
                {'title': '② Row Echelon Form',
                 'text':  'Apply Gaussian elimination:',
                 'latex': f'\\text{{REF}}(A) = {MatrixService._latex(ref)}'},
                {'title': '③ Count Non-Zero Rows',
                 'text':  f'Non-zero rows in REF = {r}  →  rank(A) = {r}',
                 'latex': f'\\text{{rank}}(A) = {r}'},
                {'title': '④ Interpretation',
                 'text':  note,
                 'latex': f'\\text{{rank}}(A) = {r} \\leq \\min({m},{n}) = {min(m,n)}'},
            ]
        }
