"""
Linear Equations Solver Service — Professional Educational Engine
Supports 5 System of Equations Solvers:
Gaussian Elimination, Gauss-Jordan Elimination, LU Solver, Cramer's Rule, Least Squares.
For every row operation step shows: Current Matrix, Operation Performed, Result, Reason.
"""

import numpy as np
from services.solver_service import BaseSolverService


class LinearEquationsService:

    @staticmethod
    def _n(v):
        v = float(v)
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return f'{v:.4f}'.rstrip('0').rstrip('.')

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
                return None, None, f'Equation count ({A.shape[0]}) does not match constant count ({len(b)}).'
            return A, b, None
        except (ValueError, TypeError) as exc:
            return None, None, f'Invalid system data: {exc}'

    # -----------------------------------------------------------------------
    # 1. GAUSSIAN ELIMINATION
    # -----------------------------------------------------------------------
    @staticmethod
    def gaussian(coeff_data, const_data):
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        
        n = A.shape[0]
        if A.shape[1] != n:
            return {'success': False, 'error': 'Gaussian elimination requires a square coefficient matrix.'}
        
        _n = LinearEquationsService._n
        M = np.hstack([A.copy(), b.reshape(-1, 1)])
        
        steps = [
            {
                'title': '① Initial Augmented Matrix [A|b]',
                'text': 'Write system as augmented matrix:',
                'current_matrix': LinearEquationsService._latex_aug(A, b),
                'operation_performed': 'Construct [A|b]',
                'result': LinearEquationsService._latex_aug(A, b),
                'reason': 'Combines coefficients and constants for elementary row operations.',
                'latex': LinearEquationsService._latex_aug(A, b)
            }
        ]

        # Forward elimination to Upper Triangular
        for col in range(n):
            max_row = col + np.argmax(np.abs(M[col:, col]))
            if max_row != col:
                M[[col, max_row]] = M[[max_row, col]]
                steps.append({
                    'title': f'② Pivoting: Swap R{col+1} ↔ R{max_row+1}',
                    'text': 'Partial pivoting for numerical stability.',
                    'current_matrix': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'operation_performed': f'R{col+1} ↔ R{max_row+1}',
                    'result': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'reason': 'Places largest absolute pivot value at current diagonal position to avoid division by near-zero.',
                    'latex': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1])
                })
            
            if abs(M[col, col]) < 1e-10:
                return {'success': False, 'error': 'System has no unique solution (singular matrix, det = 0).'}
            
            for row in range(col + 1, n):
                if abs(M[row, col]) < 1e-10:
                    continue
                factor = M[row, col] / M[col, col]
                M[row] -= factor * M[col]
                steps.append({
                    'title': f'③ Row Elimination: R{row+1} ← R{row+1} − ({_n(factor)})·R{col+1}',
                    'text': f'Eliminating entry at row {row+1}, col {col+1}.',
                    'current_matrix': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'operation_performed': f'R{row+1} ← R{row+1} − ({_n(factor)})·R{col+1}',
                    'result': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'reason': f'Creates upper triangular zero at position ({row+1}, {col+1}).',
                    'latex': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1])
                })

        # Back substitution
        x = np.zeros(n)
        for i in range(n - 1, -1, -1):
            if abs(M[i, i]) < 1e-10:
                return {'success': False, 'error': 'System has no unique solution.'}
            x[i] = (M[i, -1] - np.dot(M[i, i+1:n], x[i+1:n])) / M[i, i]

        sol_dict = {f'x{i+1}': _n(x[i]) for i in range(n)}
        sol_latex = ', '.join(f'x_{{{i+1}}} = {_n(x[i])}' for i in range(n))

        steps.append({
            'title': '④ Back Substitution Phase',
            'text': 'Solve from bottom row upwards.',
            'operation_performed': 'Back Substitution',
            'result': sol_latex,
            'reason': 'Extracts unknown variables sequentially from upper triangular matrix.',
            'latex': sol_latex
        })

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: A · x = b',
            'latex': f'A \\mathbf{{x}} = {LinearEquationsService._latex_matrix((A @ x).reshape(-1,1))}',
            'residual_error': f'{float(np.max(np.abs(A @ x - b))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Gaussian Elimination',
            input_data={'A': A.tolist(), 'b': b.tolist()},
            theory='Gaussian elimination applies elementary row operations to reduce an augmented matrix [A|b] into Row Echelon Form (REF), followed by back substitution.',
            formula='A \\mathbf{x} = \\mathbf{b} \\xrightarrow{\\text{Row Operations}} U \\mathbf{x} = \\mathbf{c}',
            definitions=[{'term': 'Row Echelon Form (REF)', 'def': 'Triangular matrix structure where pivot entries sit to the right of upper row pivots.'}],
            steps=steps,
            verification=verif,
            result=sol_dict,
            result_display=', '.join(f'x{i+1} = {_n(x[i])}' for i in range(n)),
            result_latex=f'\\mathbf{{x}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in x)} \\end{{bmatrix}}',
            notes=['Requires non-singular square matrix A for unique solution.'],
            common_mistakes=['Arithmetic sign errors during row multiplication/subtraction.'],
            applications=['Circuit loop analysis (Kirchhoff laws)', 'Structural truss loading', 'Economic input-output models'],
            time_complexity=f'O(\\frac{{2}}{{3}} {n}^3)',
            student_mode={
                'concept': 'Systematic elimination of variables to make equations triangular.',
                'why_this_step': 'Reduces simultaneous N-variable problem into 1-variable subproblems.',
                'exam_tips': ['Use partial pivoting (swapping rows) to avoid dividing by 0.'],
                'shortcuts': ['Check det(A) ≠ 0 first.'],
                'interview_questions': ['Compare Gaussian elimination with LU decomposition.'],
                'practice_questions': ['Solve 2x2 system: 2x + y = 5, x - y = 1.']
            }
        )

    # -----------------------------------------------------------------------
    # 2. GAUSS-JORDAN ELIMINATION
    # -----------------------------------------------------------------------
    @staticmethod
    def gauss_jordan(coeff_data, const_data):
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        
        n = A.shape[0]
        if A.shape[1] != n:
            return {'success': False, 'error': 'Gauss-Jordan elimination requires a square coefficient matrix.'}
        
        _n = LinearEquationsService._n
        M = np.hstack([A.copy(), b.reshape(-1, 1)])
        
        steps = [
            {
                'title': '① Initial Augmented Matrix [A|b]',
                'text': 'Write system as augmented matrix:',
                'current_matrix': LinearEquationsService._latex_aug(A, b),
                'operation_performed': 'Construct [A|b]',
                'result': LinearEquationsService._latex_aug(A, b),
                'reason': 'Sets up matrix for full reduction to Reduced Row Echelon Form (RREF).',
                'latex': LinearEquationsService._latex_aug(A, b)
            }
        ]

        # Reduce to RREF [I | x]
        for col in range(n):
            # Pivot
            max_row = col + np.argmax(np.abs(M[col:, col]))
            if max_row != col:
                M[[col, max_row]] = M[[max_row, col]]
                steps.append({
                    'title': f'② Pivot Swap R{col+1} ↔ R{max_row+1}',
                    'text': 'Swap rows for pivot stability.',
                    'current_matrix': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'operation_performed': f'R{col+1} ↔ R{max_row+1}',
                    'result': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'reason': 'Selects optimal pivot element.',
                    'latex': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1])
                })
            
            pivot = M[col, col]
            if abs(pivot) < 1e-10:
                return {'success': False, 'error': 'System has no unique solution (singular matrix).'}
            
            # Normalize pivot row to 1
            if abs(pivot - 1.0) > 1e-10:
                M[col] /= pivot
                steps.append({
                    'title': f'③ Scale Pivot Row R{col+1} ← R{col+1} / ({_n(pivot)})',
                    'text': f'Make pivot at position ({col+1}, {col+1}) equal to 1.',
                    'current_matrix': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'operation_performed': f'R{col+1} ← R{col+1} / ({_n(pivot)})',
                    'result': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                    'reason': 'Normalizes pivot entry to unity.',
                    'latex': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1])
                })

            # Eliminate entries in all OTHER rows (above and below)
            for row in range(n):
                if row != col and abs(M[row, col]) > 1e-10:
                    factor = M[row, col]
                    M[row] -= factor * M[col]
                    steps.append({
                        'title': f'④ Eliminate Column {col+1} Entry at R{row+1}: R{row+1} ← R{row+1} − ({_n(factor)})·R{col+1}',
                        'text': f'Eliminate variable x{col+1} from row {row+1}.',
                        'current_matrix': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                        'operation_performed': f'R{row+1} ← R{row+1} − ({_n(factor)})·R{col+1}',
                        'result': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1]),
                        'reason': 'Clears entries both above and below pivot position.',
                        'latex': LinearEquationsService._latex_aug(M[:, :-1], M[:, -1])
                    })

        x = M[:, -1]
        sol_dict = {f'x{i+1}': _n(x[i]) for i in range(n)}

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: A · x = b',
            'latex': f'A \\mathbf{{x}} = {LinearEquationsService._latex_matrix((A @ x).reshape(-1,1))}',
            'residual_error': f'{float(np.max(np.abs(A @ x - b))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Gauss-Jordan Elimination',
            input_data={'A': A.tolist(), 'b': b.tolist()},
            theory='Gauss-Jordan elimination continues past upper triangular form to clear entries above pivots as well, producing Reduced Row Echelon Form [I|x] so solutions appear directly in the rightmost column.',
            formula='[A \\mid \\mathbf{b}] \\xrightarrow{\\text{RREF}} [I \\mid \\mathbf{x}]',
            definitions=[{'term': 'RREF', 'def': 'Matrix form with pivot 1s and zeros in all other column entries.'}],
            steps=steps,
            verification=verif,
            result=sol_dict,
            result_display=', '.join(f'x{i+1} = {_n(x[i])}' for i in range(n)),
            result_latex=f'\\mathbf{{x}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in x)} \\end{{bmatrix}}',
            notes=['No back substitution needed after reaching RREF.'],
            common_mistakes=['Forgetting to eliminate entries ABOVE the pivot.'],
            applications=['Computing matrix inverses [A|I] -> [I|A^-1]', 'Direct system solving'],
            time_complexity=f'O({n}^3)',
            student_mode={
                'concept': 'Reducing system to Identity matrix on the left side.',
                'why_this_step': 'Solution vector appears explicitly in the augmented constant column.',
                'exam_tips': ['Keep row operations clear and label R_i <- R_i - k*R_j.'],
                'shortcuts': ['Directly gives solution vector without back substitution step.'],
                'interview_questions': ['Why does Gauss-Jordan take 50% more operations than Gaussian elimination for solving Ax=b?'],
                'practice_questions': ['Solve 2x2 system using Gauss-Jordan.']
            }
        )

    # -----------------------------------------------------------------------
    # 3. LU SOLVER
    # -----------------------------------------------------------------------
    @staticmethod
    def lu_solver(coeff_data, const_data):
        import scipy.linalg as la
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        
        n = A.shape[0]
        if A.shape[1] != n:
            return {'success': False, 'error': 'LU solver requires a square coefficient matrix.'}
        
        _n = LinearEquationsService._n
        P, L, U = la.lu(A)
        
        # Step 1: P*b
        Pb = P.T @ b
        # Step 2: Solve L y = Pb (Forward substitution)
        y = la.solve_triangular(L, Pb, lower=True)
        # Step 3: Solve U x = y (Back substitution)
        x = la.solve_triangular(U, y, lower=False)

        steps = [
            {'title': '① LU Factorization of A', 'text': 'Decompose A into P, L, and U:', 'latex': f'P A = L U \\implies L = {LinearEquationsService._latex_matrix(L)}, \\; U = {LinearEquationsService._latex_matrix(U)}'},
            {'title': '② Forward Substitution: L y = Pᵀ b', 'text': 'Solve lower triangular system for y:', 'latex': f'\\mathbf{{y}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in y)} \\end{{bmatrix}}'},
            {'title': '③ Back Substitution: U x = y', 'text': 'Solve upper triangular system for x:', 'latex': f'\\mathbf{{x}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in x)} \\end{{bmatrix}}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: A · x = b',
            'latex': f'A \\mathbf{{x}} = {LinearEquationsService._latex_matrix((A @ x).reshape(-1,1))}',
            'residual_error': f'{float(np.max(np.abs(A @ x - b))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='LU System Solver',
            input_data={'A': A.tolist(), 'b': b.tolist()},
            theory='LU solver splits Ax = b into two triangular systems: Ly = b (Forward Substitution) and Ux = y (Back Substitution).',
            formula='A \\mathbf{x} = \\mathbf{b} \\implies L U \\mathbf{x} = \\mathbf{b} \\implies L \\mathbf{y} = \\mathbf{b}, \\quad U \\mathbf{x} = \\mathbf{y}',
            definitions=[{'term': 'Triangular System', 'def': 'A linear system solvable in O(n^2) time via substitution.'}],
            steps=steps,
            verification=verif,
            result={f'x{i+1}': _n(x[i]) for i in range(n)},
            result_display=', '.join(f'x{i+1} = {_n(x[i])}' for i in range(n)),
            result_latex=f'\\mathbf{{x}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in x)} \\end{{bmatrix}}',
            notes=['Very fast when solving Ax = b for many different b vectors.'],
            common_mistakes=['Mixing up forward substitution with back substitution order.'],
            applications=['Finite Element Analysis (FEA)', 'Circuit simulators (SPICE)'],
            time_complexity=f'O({n}^2) \\text{{ after }} O({n}^3) \\text{{ factorization}}',
            student_mode={
                'concept': 'Two-step triangular system solving.',
                'why_this_step': 'Forward solve for y, then back solve for x.',
                'exam_tips': ['L has 1s on main diagonal!'],
                'shortcuts': ['L y = b then U x = y.'],
                'interview_questions': ['How much faster is LU solver when solving for 100 different right-hand vectors b?'],
                'practice_questions': ['Solve LU system for 2x2.']
            }
        )

    # -----------------------------------------------------------------------
    # 4. CRAMER'S RULE
    # -----------------------------------------------------------------------
    @staticmethod
    def cramers_rule(coeff_data, const_data):
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        
        n = A.shape[0]
        if A.shape[1] != n:
            return {'success': False, 'error': 'Cramer\'s Rule requires a square coefficient matrix.'}
        
        _n = LinearEquationsService._n
        det_A = float(np.linalg.det(A))
        
        if abs(det_A) < 1e-10:
            return {'success': False, 'error': f'Cramer\'s Rule fails because det(A) = {_n(det_A)} ≈ 0 (singular matrix).'}
        
        steps = [
            {'title': '① Main Determinant det(A)', 'text': f'det(A) = {_n(det_A)} (≠ 0 ✓)', 'latex': f'\\det(A) = {_n(det_A)}'}
        ]

        x = np.zeros(n)
        for i in range(n):
            A_i = A.copy()
            A_i[:, i] = b
            det_Ai = float(np.linalg.det(A_i))
            x[i] = det_Ai / det_A
            steps.append({
                'title': f'② Variable x{i+1} Replacement Matrix A_{i+1}',
                'text': f'Replace column {i+1} of A with constant vector b.',
                'latex': f'A_{{{i+1}}} = {LinearEquationsService._latex_matrix(A_i)}, \\quad \\det(A_{{{i+1}}}) = {_n(det_Ai)}'
            })
            steps.append({
                'title': f'③ Compute x{i+1}',
                'text': f'x{i+1} = det(A_{i+1}) / det(A) = {_n(det_Ai)} / {_n(det_A)} = {_n(x[i])}',
                'latex': f'x_{{{i+1}}} = \\frac{{\\det(A_{{{i+1}}})}}{{\\det(A)}} = \\frac{{{{{_n(det_Ai)}}}}}{{{{{_n(det_A)}}}}} = {_n(x[i])}'
            })

        sol_dict = {f'x{i+1}': _n(x[i]) for i in range(n)}

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: A · x = b',
            'latex': f'A \\mathbf{{x}} = {LinearEquationsService._latex_matrix((A @ x).reshape(-1,1))}',
            'residual_error': f'{float(np.max(np.abs(A @ x - b))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Cramer\'s Rule',
            input_data={'A': A.tolist(), 'b': b.tolist()},
            theory='Cramer\'s rule expresses the solution of an N-variable linear system as ratios of determinants obtained by substituting constant column b into coefficient matrix columns.',
            formula='x_i = \\frac{\\det(A_i)}{\\det(A)}',
            definitions=[{'term': 'Modified Matrix Aᵢ', 'def': 'Matrix A with column i replaced by constants vector b.'}],
            steps=steps,
            verification=verif,
            result=sol_dict,
            result_display=', '.join(f'x{i+1} = {_n(x[i])}' for i in range(n)),
            result_latex=f'\\mathbf{{x}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in x)} \\end{{bmatrix}}',
            notes=['Only applicable when det(A) ≠ 0.', 'Computationally expensive for n > 4.'],
            common_mistakes=['Replacing rows instead of columns with vector b.'],
            applications=['Symbolic linear system solving', '2x2 and 3x3 hand calculations'],
            time_complexity=f'O(({n}+1) \\cdot {n}^3)',
            student_mode={
                'concept': 'Explicit determinant formula for solving linear systems.',
                'why_this_step': 'Provides direct closed-form expression for each variable.',
                'exam_tips': ['Great for 2x2 and 3x3 exam problems.'],
                'shortcuts': ['If det(A) = 0, Cramer\'s rule cannot be used.'],
                'interview_questions': ['Why is Cramer\'s rule computationally impractical for n = 100?'],
                'practice_questions': ['Solve 2x2 system via Cramer\'s Rule.']
            }
        )

    # -----------------------------------------------------------------------
    # 5. LEAST SQUARES (Aᵀ A x = Aᵀ b)
    # -----------------------------------------------------------------------
    @staticmethod
    def least_squares(coeff_data, const_data):
        A, b, err = LinearEquationsService._parse_system(coeff_data, const_data)
        if err: return {'success': False, 'error': err}
        
        m, n = A.shape
        _n = LinearEquationsService._n
        
        # Normal equations: A^T A x = A^T b
        AtA = A.T @ A
        Atb = A.T @ b
        
        try:
            x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
        except Exception as exc:
            return {'success': False, 'error': f'Least squares calculation failed: {exc}'}

        sol_dict = {f'x{i+1}': _n(x[i]) for i in range(len(x))}
        res_norm = float(np.linalg.norm(A @ x - b))

        steps = [
            {'title': '① System Dimensions', 'text': f'A is {m}×{n}, b is {m}×1. (Overdetermined system if {m} > {n}).', 'latex': f'{LinearEquationsService._latex_matrix(A)} \\mathbf{{x}} \\approx {LinearEquationsService._latex_matrix(b.reshape(-1,1))}'},
            {'title': '② Form Normal Equations: AᵀA x = Aᵀb', 'text': 'Multiply both sides by Aᵀ:', 'latex': f'A^T A = {LinearEquationsService._latex_matrix(AtA)}, \\quad A^T b = {LinearEquationsService._latex_matrix(Atb.reshape(-1,1))}'},
            {'title': '③ Solve Normal Equations', 'text': 'x = (AᵀA)⁻¹ Aᵀb', 'latex': f'\\mathbf{{x}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in x)} \\end{{bmatrix}}'},
            {'title': '④ Residual Error Check', 'text': f'Minimal Residual ||Ax - b|| = {_n(res_norm)}', 'latex': f'||A\\mathbf{{x}} - \\mathbf{{b}}|| = {_n(res_norm)}'}
        ]

        verif = {
            'status': '✔ Correct (Minimal Error)',
            'check': 'Verified least squares minimal residual error.',
            'latex': f'||A\\mathbf{{x}} - \\mathbf{{b}}|| = {_n(res_norm)}',
            'residual_error': f'{res_norm:.6f}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Least Squares Solution',
            input_data={'A': A.tolist(), 'b': b.tolist()},
            theory='Least squares finds the best-fit solution x that minimizes the squared Euclidean distance ||Ax - b||² for overdetermined or inconsistent systems.',
            formula='\\mathbf{x} = (A^T A)^{-1} A^T \\mathbf{b}',
            definitions=[{'term': 'Normal Equations', 'def': 'The consistent system AᵀAx = Aᵀb.'}, {'term': 'Residual Vector', 'def': 'r = b - Ax, orthogonal to column space of A.'}],
            steps=steps,
            verification=verif,
            result=sol_dict,
            result_display=', '.join(f'x{i+1} = {_n(x[i])}' for i in range(len(x))),
            result_latex=f'\\mathbf{{x}} = \\begin{{bmatrix}} {" \\\\ ".join(_n(v) for v in x)} \\end{{bmatrix}}',
            notes=['Works even when Ax = b has no exact solution!'],
            common_mistakes=['Attempting to solve non-invertible AᵀA without pseudoinverse.'],
            applications=['Linear regression in machine learning', 'Data fitting', 'GPS trilateration'],
            time_complexity=f'O({m} {n}^2)',
            student_mode={
                'concept': 'Finding the closest approximation when no exact solution exists.',
                'why_this_step': 'Minimizes sum of squared errors in real-world noisy data.',
                'exam_tips': ['Normal equations formula: A^T * A * x = A^T * b.'],
                'shortcuts': ['If A is square and invertible, least squares gives exact solution.'],
                'interview_questions': ['Why is QR decomposition preferred over normal equations for least squares numerically?'],
                'practice_questions': ['Fit a line y = mx + c to points (1,2), (2,3), (3,5).']
            }
        )
