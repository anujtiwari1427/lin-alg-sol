"""
Linear Equations Solver Service — Phase 6
Methods: Gaussian Elimination, Cramer's Rule, Matrix (Inverse) Method
Supports 2-variable and 3-variable systems (NxN for Gaussian/Matrix methods)
"""

import numpy as np


class LinearEquationsService:

    @staticmethod
    def _n(v):
        if abs(float(v) - round(float(v))) < 1e-9:
            return str(int(round(float(v))))
        return f'{float(v):.6f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex_matrix(mat):
        rows = [' & '.join(LinearEquationsService._n(x) for x in row) for row in mat]
        return '\\begin{bmatrix} ' + ' \\\\ '.join(rows) + ' \\end{bmatrix}'

    @staticmethod
    def _latex_aug(A, b):
        rows = []
        for i in range(len(A)):
            r = [LinearEquationsService._n(x) for x in A[i]] + ['|', LinearEquationsService._n(b[i])]
            rows.append(' & '.join(r[:len(A[i])]) + ' & ' + r[-1])
        return '\\left[\\begin{array}{' + 'c' * len(A[0]) + '|c} ' + ' \\\\ '.join(rows) + ' \\end{array}\\right]'

    @staticmethod
    def _parse_system(coeff_data, const_data):
        try:
            A = np.array(coeff_data, dtype=float)
            b = np.array(const_data, dtype=float).flatten()
            if A.ndim != 2:
                return None, None, 'Coefficient matrix must be 2-D.'
            if A.shape[0] != len(b):
                return None, None, 'Number of equations must match number of constants.'
            return A, b, None
        except (ValueError, TypeError) as exc:
            return None, None, str(exc)

    # -----------------------------------------------------------------------
    # GAUSSIAN ELIMINATION
    # -----------------------------------------------------------------------
    @staticmethod
    def gaussian(coeff_data, const_data):
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        n = A.shape[0]
        if A.shape[1] != n:
            return {'success': False, 'error': 'Gaussian elimination requires a square coefficient matrix.'}

        _n    = LinearEquationsService._n
        M     = np.hstack([A.copy(), b.reshape(-1, 1)])
        steps = [
            {'title': '① Augmented Matrix [A|b]',
             'text':  'Write the system as an augmented matrix:',
             'latex': LinearEquationsService._latex_aug(A, b)}
        ]

        # Forward elimination
        for col in range(n):
            # Partial pivot
            max_row = col + np.argmax(np.abs(M[col:, col]))
            if max_row != col:
                M[[col, max_row]] = M[[max_row, col]]
                steps.append({'title': f'② Row Swap  R{col+1} ↔ R{max_row+1}',
                               'text':  'Swap to place largest pivot element at top.',
                               'latex': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1])})
            if abs(M[col, col]) < 1e-12:
                return {'success': False, 'error': 'System has no unique solution (singular matrix).'}
            for row in range(col + 1, n):
                if abs(M[row, col]) < 1e-12:
                    continue
                factor = M[row, col] / M[col, col]
                M[row] -= factor * M[col]
                steps.append({'title': f'③ Eliminate: R{row+1} ← R{row+1} − ({_n(factor)})·R{col+1}',
                               'text':  f'Eliminate variable x{col+1} from row {row+1}.',
                               'latex': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1])})

        # Back substitution
        x = np.zeros(n)
        for i in range(n - 1, -1, -1):
            if abs(M[i, i]) < 1e-12:
                return {'success': False, 'error': 'System has no unique solution.'}
            x[i] = (M[i, -1] - np.dot(M[i, i+1:n], x[i+1:n])) / M[i, i]

        sol = {f'x{i+1}': _n(x[i]) for i in range(n)}
        sol_latex = ', '.join(f'x_{{{i+1}}} = {_n(x[i])}' for i in range(n))
        steps.append({'title': '④ Back Substitution',
                       'text':  'Solve from last equation upwards.',
                       'latex': sol_latex})
        steps.append({'title': '⑤ Solution',
                       'text':  ' | '.join(f'x{i+1} = {_n(x[i])}' for i in range(n)),
                       'latex': f'\\boxed{{{sol_latex}}}'})

        return {
            'success': True, 'method': 'Gaussian Elimination',
            'solution': sol, 'solution_vector': x.tolist(),
            'result_latex': sol_latex, 'steps': steps
        }

    # -----------------------------------------------------------------------
    # CRAMER'S RULE
    # -----------------------------------------------------------------------
    @staticmethod
    def cramer(coeff_data, const_data):
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        n = A.shape[0]
        if A.shape[1] != n:
            return {'success': False, 'error': "Cramer's Rule requires a square coefficient matrix."}
        if n > 4:
            return {'success': False, 'error': "Cramer's Rule is practical only for small systems (≤4 variables). Use Gaussian for larger systems."}

        _n  = LinearEquationsService._n
        det_A = float(np.linalg.det(A))

        steps = [
            {'title': '① Coefficient Matrix & Constants',
             'latex': f'A = {LinearEquationsService._latex_matrix(A)}, \\quad b = {LinearEquationsService._latex_matrix(b.reshape(-1,1))}'},
            {'title': '② det(A)',
             'text':  f'det(A) = {_n(det_A)}',
             'latex': f'\\det(A) = {_n(det_A)}'},
        ]

        if abs(det_A) < 1e-12:
            return {'success': False, 'error': f"Cramer's Rule: det(A) = {_n(det_A)} ≈ 0. System has no unique solution."}

        x = []
        for i in range(n):
            Ai = A.copy()
            Ai[:, i] = b
            det_Ai = float(np.linalg.det(Ai))
            xi     = det_Ai / det_A
            x.append(xi)
            steps.append({
                'title': f'③ x{i+1} = det(A{i+1}) / det(A)',
                'text':  f'Replace column {i+1} of A with b to form A{i+1}. det(A{i+1}) = {_n(det_Ai)}',
                'latex': f'x_{{{i+1}}} = \\frac{{\\det(A_{{{i+1}}})}}{{\\det(A)}} = \\frac{{{_n(det_Ai)}}}{{{_n(det_A)}}} = {_n(xi)}'
            })

        sol       = {f'x{i+1}': _n(x[i]) for i in range(n)}
        sol_latex = ', '.join(f'x_{{{i+1}}} = {_n(x[i])}' for i in range(n))
        steps.append({'title': '④ Solution',
                       'text':  ' | '.join(f'x{i+1} = {_n(x[i])}' for i in range(n)),
                       'latex': f'\\boxed{{{sol_latex}}}'})

        return {
            'success': True, 'method': "Cramer's Rule",
            'solution': sol, 'solution_vector': x,
            'result_latex': sol_latex, 'steps': steps
        }

    # -----------------------------------------------------------------------
    # MATRIX (INVERSE) METHOD  x = A⁻¹ b
    # -----------------------------------------------------------------------
    @staticmethod
    def matrix_method(coeff_data, const_data):
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        n = A.shape[0]
        if A.shape[1] != n:
            return {'success': False, 'error': 'Matrix method requires a square coefficient matrix.'}

        _n    = LinearEquationsService._n
        det_A = float(np.linalg.det(A))

        if abs(det_A) < 1e-12:
            return {'success': False, 'error': f'Matrix method: A is singular (det = {_n(det_A)}). Cannot find A⁻¹.'}

        A_inv = np.linalg.inv(A)
        x     = A_inv @ b
        sol       = {f'x{i+1}': _n(x[i]) for i in range(n)}
        sol_latex = ', '.join(f'x_{{{i+1}}} = {_n(x[i])}' for i in range(n))

        steps = [
            {'title': '① System in Matrix Form  Ax = b',
             'latex': f'{LinearEquationsService._latex_matrix(A)} \\cdot x = {LinearEquationsService._latex_matrix(b.reshape(-1,1))}'},
            {'title': '② Compute A⁻¹',
             'text':  f'det(A) = {_n(det_A)} ≠ 0 ✓',
             'latex': f'A^{{-1}} = {LinearEquationsService._latex_matrix(A_inv)}'},
            {'title': '③ Solve  x = A⁻¹ · b',
             'text':  'Multiply both sides on the left by A⁻¹',
             'latex': f'x = A^{{-1}} b = {LinearEquationsService._latex_matrix(A_inv)} {LinearEquationsService._latex_matrix(b.reshape(-1,1))}'},
            {'title': '④ Solution',
             'text':  ' | '.join(f'x{i+1} = {_n(x[i])}' for i in range(n)),
             'latex': f'\\boxed{{{sol_latex}}}'},
        ]

        return {
            'success': True, 'method': 'Matrix (Inverse) Method',
            'solution': sol, 'solution_vector': x.tolist(),
            'result_latex': sol_latex, 'steps': steps
        }
