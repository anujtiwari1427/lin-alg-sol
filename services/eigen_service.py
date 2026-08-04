"""
Eigenvalue & Eigenvector Service — Phase 7
Computes: Eigenvalues, Eigenvectors, Characteristic Polynomial, Verification
"""

import numpy as np


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
        v = float(np.real(v)) if np.iscomplex(v) else float(v)
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return f'{v:.6f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex_matrix(mat):
        rows = [' & '.join(EigenService._n(x) for x in row) for row in np.real(mat)]
        return '\\begin{bmatrix} ' + ' \\\\ '.join(rows) + ' \\end{bmatrix}'

    @staticmethod
    def _char_poly_str(A):
        """Build a human-readable characteristic polynomial string for 2x2 and 3x3."""
        n   = A.shape[0]
        _n  = EigenService._n
        if n == 2:
            a, b = A[0,0], A[0,1]
            c, d = A[1,0], A[1,1]
            tr   = float(a + d)
            det  = float(a*d - b*c)
            # λ² - tr(A)λ + det(A) = 0
            s_tr  = _n(abs(tr))
            s_det = _n(abs(det))
            sign_tr  = '-' if tr >= 0 else '+'
            sign_det = '+' if det >= 0 else '-'
            return (f'\\lambda^2 {sign_tr} {s_tr}\\lambda {sign_det} {s_det} = 0',
                    f'tr(A)={_n(tr)}, det(A)={_n(det)}')
        if n == 3:
            tr  = float(np.trace(A))
            det = float(np.linalg.det(A))
            # Sum of 2x2 principal minors
            m1  = float(A[0,0]*A[1,1] - A[0,1]*A[1,0])
            m2  = float(A[0,0]*A[2,2] - A[0,2]*A[2,0])
            m3  = float(A[1,1]*A[2,2] - A[1,2]*A[2,1])
            p2  = float(m1 + m2 + m3)
            return (f'\\lambda^3 - {_n(tr)}\\lambda^2 + {_n(p2)}\\lambda - {_n(det)} = 0',
                    f'tr(A)={_n(tr)}, det(A)={_n(det)}')
        return (f'\\det(A - \\lambda I) = 0  \\quad (\\text{{{n}}}\\times\\text{{{n}}} \\text{{ polynomial}})', '')

    @staticmethod
    def calculate(matrix_data):
        A, err = EigenService.parse(matrix_data)
        if err:
            return {'success': False, 'error': err}
        n   = A.shape[0]
        _n  = EigenService._n

        try:
            raw_vals, raw_vecs = np.linalg.eig(A)
        except np.linalg.LinAlgError as exc:
            return {'success': False, 'error': str(exc)}

        # Sort by real part of eigenvalue for deterministic output
        order     = np.argsort(np.real(raw_vals))
        eig_vals  = raw_vals[order]
        eig_vecs  = raw_vecs[:, order]

        # Format eigenvalues (handle complex)
        def fmt_val(v):
            re = float(np.real(v))
            im = float(np.imag(v))
            if abs(im) < 1e-9:
                return _n(re)
            sign = '+' if im >= 0 else '-'
            return f'{_n(re)} {sign} {_n(abs(im))}i'

        formatted_vals = [fmt_val(v) for v in eig_vals]
        formatted_vecs = []
        for col in range(n):
            vec = eig_vecs[:, col]
            formatted_vecs.append([_n(float(np.real(x))) for x in vec])

        # Characteristic polynomial info
        char_poly, poly_note = EigenService._char_poly_str(A)

        # Verification: Av = λv for each pair
        verif_steps = []
        for i in range(n):
            lam = eig_vals[i]
            v   = eig_vecs[:, i]
            Av  = A @ np.real(v)
            lv  = float(np.real(lam)) * np.real(v)
            ok  = np.allclose(Av, lv, atol=1e-6)
            verif_steps.append(
                f'λ{i+1}={fmt_val(lam)}: A·v{i+1} ≈ λ{i+1}·v{i+1}  {"✓" if ok else "✗"}'
            )

        # I matrix
        I_latex = EigenService._latex_matrix(np.eye(n))

        steps = [
            {'title': '① Input Matrix',
             'text':  f'{n}×{n} matrix A',
             'latex': EigenService._latex_matrix(A)},
            {'title': '② Characteristic Equation',
             'text':  'Find values λ where det(A − λI) = 0',
             'latex': f'\\det(A - \\lambda I) = 0'},
            {'title': '③ Characteristic Polynomial',
             'text':  poly_note,
             'latex': char_poly},
            {'title': '④ Eigenvalues  (roots of polynomial)',
             'text':  ', '.join(f'λ{i+1} = {fmt_val(eig_vals[i])}' for i in range(n)),
             'latex': '  \\quad  '.join(f'\\lambda_{{{i+1}}} = {fmt_val(eig_vals[i])}' for i in range(n))},
            {'title': '⑤ Eigenvectors  (null-space of A − λᵢI)',
             'text':  'For each λᵢ solve (A − λᵢI)v = 0',
             'latex': '  \\quad  '.join(
                 f'\\mathbf{{v}}_{{{i+1}}} = ' +
                 '\\begin{bmatrix} ' +
                 ' \\\\ '.join(_n(float(np.real(eig_vecs[r, i]))) for r in range(n)) +
                 ' \\end{bmatrix}'
                 for i in range(n)
             )},
            {'title': '⑥ Verification  Av = λv',
             'text':  'Confirming each eigenpair:',
             'list':  verif_steps},
        ]

        return {
            'success': True,
            'operation': 'Eigenvalues & Eigenvectors',
            'eigenvalues': formatted_vals,
            'eigenvectors': formatted_vecs,
            'char_poly': char_poly,
            'result_latex': '\\lambda \\in \\{' + ', '.join(formatted_vals) + '\\}',
            'steps': steps
        }
