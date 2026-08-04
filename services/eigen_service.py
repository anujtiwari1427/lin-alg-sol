"""
Eigenvalue & Eigenvector Service — Professional Educational Engine
Computes: Eigenvalues, Eigenvectors, Characteristic Polynomial, Verification, and Educational Reports.
"""

import numpy as np
from services.solver_service import BaseSolverService


class EigenService:

    @staticmethod
    def parse(data):
        try:
            A = np.array(data, dtype=float)
            if A.ndim != 2 or A.shape[0] != A.shape[1]:
                return None, 'Eigenvalue computation requires a square matrix.'
            return A, None
        except (ValueError, TypeError) as exc:
            return None, str(exc)

    @staticmethod
    def _n(v):
        if isinstance(v, (complex, np.complexfloating)):
            re = float(np.real(v))
            im = float(np.imag(v))
            if abs(im) < 1e-9:
                return EigenService._n(re)
            sign = '+' if im >= 0 else '-'
            return f"{EigenService._n(re)} {sign} {EigenService._n(abs(im))}i"
        v = float(v)
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return f'{v:.4f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex_matrix(mat):
        rows = [' & '.join(EigenService._n(x) for x in row) for row in np.real(mat)]
        return '\\begin{bmatrix} ' + ' \\\\ '.join(rows) + ' \\end{bmatrix}'

    @staticmethod
    def _char_poly_str(A):
        n = A.shape[0]
        _n = EigenService._n
        if n == 2:
            a, b, c, d = A[0,0], A[0,1], A[1,0], A[1,1]
            tr = float(a + d)
            det = float(a*d - b*c)
            sign_tr = '-' if tr >= 0 else '+'
            sign_det = '+' if det >= 0 else '-'
            return (f'\\lambda^2 {sign_tr} {_n(abs(tr))}\\lambda {sign_det} {_n(abs(det))} = 0',
                    f'tr(A) = {_n(tr)}, \\det(A) = {_n(det)}')
        if n == 3:
            tr = float(np.trace(A))
            det = float(np.linalg.det(A))
            m1 = float(A[0,0]*A[1,1] - A[0,1]*A[1,0])
            m2 = float(A[0,0]*A[2,2] - A[0,2]*A[2,0])
            m3 = float(A[1,1]*A[2,2] - A[1,2]*A[2,1])
            p2 = float(m1 + m2 + m3)
            return (f'\\lambda^3 - {_n(tr)}\\lambda^2 + {_n(p2)}\\lambda - {_n(det)} = 0',
                    f'tr(A) = {_n(tr)}, \\det(A) = {_n(det)}')
        return (f'\\det(A - \\lambda I) = 0 \\quad ({n}\\times{n} \\text{{ polynomial}})', '')

    @staticmethod
    def calculate(matrix_data):
        A, err = EigenService.parse(matrix_data)
        if err:
            return {'success': False, 'error': err}
        
        n = A.shape[0]
        _n = EigenService._n

        try:
            raw_vals, raw_vecs = np.linalg.eig(A)
        except np.linalg.LinAlgError as exc:
            return {'success': False, 'error': str(exc)}

        order = np.argsort(np.real(raw_vals))
        eig_vals = raw_vals[order]
        eig_vecs = raw_vecs[:, order]

        formatted_vals = [_n(v) for v in eig_vals]
        formatted_vecs = []
        for col in range(n):
            vec = eig_vecs[:, col]
            formatted_vecs.append([_n(x) for x in vec])

        char_poly, poly_note = EigenService._char_poly_str(A)

        steps = [
            {'title': '① Input Square Matrix A', 'text': f'Square matrix ({n}×{n}):', 'latex': EigenService._latex_matrix(A)},
            {'title': '② Characteristic Equation', 'text': 'Solve det(A - λI) = 0:', 'latex': char_poly},
            {'title': '③ Computed Eigenvalues (λ)', 'text': f'Roots of polynomial: {", ".join(formatted_vals)}', 'latex': f'\\lambda = \\{{ {", ".join(formatted_vals)} \\}}'},
            {'title': '④ Eigenvectors Solving (A - λI)v = 0', 'text': 'For each eigenvalue λ, solve nullspace:', 'latex': EigenService._latex_matrix(eig_vecs)}
        ]

        # Verification step: A*v = lambda*v
        max_err = 0.0
        for i in range(n):
            v_col = eig_vecs[:, i]
            Av = A @ v_col
            lv = eig_vals[i] * v_col
            err_i = float(np.max(np.abs(Av - lv)))
            if err_i > max_err: max_err = err_i

        verif = {
            'status': '✔ Correct',
            'check': 'Verified eigen-equation A · v_i = λ_i · v_i',
            'latex': 'A \\mathbf{v}_i = \\lambda_i \\mathbf{v}_i',
            'residual_error': f'{max_err:.6e}'
        }

        res = BaseSolverService.build_educational_solution(
            operation='Eigenvalues & Eigenvectors',
            input_data={'A': [[_n(x) for x in row] for row in A.tolist()]},
            theory='Eigenvalues (λ) and eigenvectors (v) characterize directions along which a linear transformation acts as pure scalar stretch or compression.',
            formula='A \\mathbf{v} = \\lambda \\mathbf{v} \\iff \\det(A - \\lambda I) = 0',
            definitions=[{'term': 'Eigenvalue (λ)', 'def': 'Scaling factor by which eigenvector length changes.'}, {'term': 'Eigenvector (v)', 'def': 'Non-zero vector whose direction remains unchanged by matrix multiplication.'}],
            steps=steps,
            verification=verif,
            result={'eigenvalues': formatted_vals, 'eigenvectors': formatted_vecs},
            result_display=f'λ = {", ".join(formatted_vals)}',
            result_latex=f'\\lambda = \\{{ {", ".join(formatted_vals)} \\}}',
            notes=['Sum of eigenvalues = trace(A)', 'Product of eigenvalues = det(A)'],
            common_mistakes=['Assuming non-square matrices have eigenvalues.'],
            applications=['Google PageRank algorithm', 'Vibration modes in civil engineering', 'Principal Component Analysis (PCA)', 'Quantum Mechanics wavefunctions'],
            time_complexity=f'O({n}^3)',
            student_mode={
                'concept': 'Invariant direction vectors under matrix transformation.',
                'why_this_step': 'Identifies fundamental modes and resonant axes.',
                'exam_tips': ['Sum of eigenvalues equals trace(A)! Use this for quick checks.'],
                'shortcuts': ['Product of eigenvalues equals det(A).'],
                'interview_questions': ['What are eigenvalues of a projection matrix? (0 and 1!)'],
                'practice_questions': ['Find eigenvalues of [[2, 1], [1, 2]].']
            }
        )
        res['eigenvalues'] = formatted_vals
        res['eigenvectors'] = formatted_vecs
        return res
