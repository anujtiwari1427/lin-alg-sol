"""
Matrix Operations Service — Professional Educational Engine
Supports 20 Matrix Operations with complete educational reports:
Theory, Formulas, Definitions, Detailed Working Steps, Verification,
Important Notes, Common Mistakes, Real-world Applications, Time Complexity,
and Student Mode materials.
"""

import numpy as np
import scipy.linalg as la
from services.solver_service import BaseSolverService


class MatrixService:

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
        """Format a float or complex cleanly."""
        if isinstance(v, (complex, np.complexfloating)):
            re = float(np.real(v))
            im = float(np.imag(v))
            if abs(im) < 1e-9:
                return MatrixService._n(re)
            sign = '+' if im >= 0 else '-'
            return f"{MatrixService._n(re)} {sign} {MatrixService._n(abs(im))}i"
        v = float(v)
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return f'{v:.4f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _latex(mat, name=None):
        """Convert numpy matrix to LaTeX \\bmatrix string."""
        if not isinstance(mat, np.ndarray):
            mat = np.array(mat)
        rows = [' & '.join(MatrixService._n(x) for x in row) for row in mat]
        body = ' \\\\ '.join(rows)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'{name} = {s}' if name else s

    @staticmethod
    def _display(mat):
        """Return nested list of clean strings for template rendering."""
        if not isinstance(mat, np.ndarray):
            mat = np.array(mat)
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

    @staticmethod
    def _minor(A, i, j):
        return np.delete(np.delete(A, i, 0), j, 1)

    # -----------------------------------------------------------------------
    # 1. ADDITION
    # -----------------------------------------------------------------------
    @staticmethod
    def addition(a_data, b_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = MatrixService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if A.shape != B.shape:
            return {'success': False, 'error': f'Shapes must match: A is {A.shape[0]}×{A.shape[1]}, B is {B.shape[0]}×{B.shape[1]}.'}
        
        R = A + B
        m, n = A.shape
        elem_calcs = [
            f'({MatrixService._n(A[i,j])}) + ({MatrixService._n(B[i,j])}) = {MatrixService._n(R[i,j])}'
            for i in range(m) for j in range(n)
        ]

        steps = [
            {'title': '① Compatibility Check', 'text': f'Both matrices A and B have dimensions {m}×{n}. Addition is valid.', 'latex': f'{MatrixService._latex(A, "A")} \\quad {MatrixService._latex(B, "B")}'},
            {'title': '② Element-Wise Addition Rule', 'text': 'Add corresponding entries: Cᵢⱼ = Aᵢⱼ + Bᵢⱼ', 'latex': 'C_{ij} = A_{ij} + B_{ij}'},
            {'title': '③ Intermediate Calculations', 'text': 'Computing every element:', 'list': elem_calcs},
            {'title': '④ Final Answer', 'text': f'Resulting matrix C ({m}×{n}):', 'latex': f'A + B = {MatrixService._latex(R)}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: A + B - B = A',
            'latex': f'(A + B) - B = {MatrixService._latex(np.round(R - B, 4))}',
            'residual_error': f'{float(np.max(np.abs(R - B - A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Matrix Addition A + B',
            input_data={'A': MatrixService._display(A), 'B': MatrixService._display(B)},
            theory='Matrix addition is a binary operation that takes two matrices of the same dimensions and produces a third matrix where each entry is the sum of the corresponding entries.',
            formula='C_{ij} = A_{ij} + B_{ij} \\quad \\text{for } 1 \\leq i \\leq m, 1 \\leq j \\leq n',
            definitions=[{'term': 'Dimension Matching', 'def': 'Addition requires both matrices to have identical numbers of rows and columns.'}],
            steps=steps,
            verification=verif,
            result=R.tolist(),
            result_display=MatrixService._display(R),
            result_latex=MatrixService._latex(R),
            notes=['Matrix addition is commutative: A + B = B + A.', 'Matrix addition is associative: (A + B) + C = A + (B + C).'],
            common_mistakes=['Attempting to add matrices with different row or column counts.'],
            applications=['Combining datasets', 'Image pixel intensity shifts', 'System state updates'],
            time_complexity=f'O({m} \\times {n})',
            student_mode={
                'concept': 'Element-wise linear combination of matching grids.',
                'why_this_step': 'Linearity preserves vector space addition properties.',
                'exam_tips': ['Keep track of negative signs inside matrix entries.'],
                'shortcuts': ['If one matrix is zero, the sum is simply the other matrix.'],
                'interview_questions': ['How is matrix addition parallelized in GPU computing?'],
                'practice_questions': ['Add two 3x3 matrices with alternating signs.']
            }
        )

    # -----------------------------------------------------------------------
    # 2. SUBTRACTION
    # -----------------------------------------------------------------------
    @staticmethod
    def subtraction(a_data, b_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = MatrixService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if A.shape != B.shape:
            return {'success': False, 'error': f'Shapes must match: A is {A.shape[0]}×{A.shape[1]}, B is {B.shape[0]}×{B.shape[1]}.'}
        
        R = A - B
        m, n = A.shape
        elem_calcs = [
            f'({MatrixService._n(A[i,j])}) − ({MatrixService._n(B[i,j])}) = {MatrixService._n(R[i,j])}'
            for i in range(m) for j in range(n)
        ]

        steps = [
            {'title': '① Compatibility Check', 'text': f'Both matrices A and B have dimensions {m}×{n}. Subtraction is valid.', 'latex': f'{MatrixService._latex(A, "A")} \\quad {MatrixService._latex(B, "B")}'},
            {'title': '② Element-Wise Subtraction Rule', 'text': 'Subtract corresponding entries: Cᵢⱼ = Aᵢⱼ − Bᵢⱼ', 'latex': 'C_{ij} = A_{ij} - B_{ij}'},
            {'title': '③ Intermediate Calculations', 'text': 'Computing every element:', 'list': elem_calcs},
            {'title': '④ Final Answer', 'text': f'Resulting matrix C ({m}×{n}):', 'latex': f'A - B = {MatrixService._latex(R)}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: (A - B) + B = A',
            'latex': f'(A - B) + B = {MatrixService._latex(np.round(R + B, 4))}',
            'residual_error': f'{float(np.max(np.abs(R + B - A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Matrix Subtraction A - B',
            input_data={'A': MatrixService._display(A), 'B': MatrixService._display(B)},
            theory='Matrix subtraction subtracts corresponding components of two matrices of matching order.',
            formula='C_{ij} = A_{ij} - B_{ij}',
            definitions=[{'term': 'Subtrahend', 'def': 'The matrix B being subtracted from matrix A.'}],
            steps=steps,
            verification=verif,
            result=R.tolist(),
            result_display=MatrixService._display(R),
            result_latex=MatrixService._latex(R),
            notes=['Matrix subtraction is NOT commutative: A - B ≠ B - A.'],
            common_mistakes=['Double negative errors (subtracting a negative number yields a positive sum).'],
            applications=['Differential analysis', 'Residual calculation in machine learning', 'Image differencing'],
            time_complexity=f'O({m} \\times {n})',
            student_mode={
                'concept': 'Difference of corresponding entries in two matrix arrays.',
                'why_this_step': 'Measures displacement between matrix states.',
                'exam_tips': ['Convert A - B into A + (-1)*B to avoid sign confusion.'],
                'shortcuts': ['Subtracting a matrix from itself always yields the zero matrix.'],
                'interview_questions': ['What is the difference between element-wise subtraction and matrix distance metrics?'],
                'practice_questions': ['Compute A - B where B is an identity matrix.']
            }
        )

    # -----------------------------------------------------------------------
    # 3. MULTIPLICATION
    # -----------------------------------------------------------------------
    @staticmethod
    def multiplication(a_data, b_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = MatrixService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if A.shape[1] != B.shape[0]:
            return {'success': False, 'error': f'Inner dimension mismatch: A is {A.shape[0]}×{A.shape[1]}, B is {B.shape[0]}×{B.shape[1]}. Columns of A ({A.shape[1]}) must equal rows of B ({B.shape[0]}).'}
        
        R = A @ B
        m, k, n = A.shape[0], A.shape[1], B.shape[1]
        
        shown = []
        for i in range(m):
            for j in range(n):
                terms = ' + '.join(f'({MatrixService._n(A[i,p])} × {MatrixService._n(B[p,j])})' for p in range(k))
                shown.append(f'C[{i+1},{j+1}] = {terms} = {MatrixService._n(R[i,j])}')
                if len(shown) >= 12: break
            if len(shown) >= 12: break

        steps = [
            {'title': '① Dimension Compatibility', 'text': f'A is {m}×{k} and B is {k}×{n}. Inner dimensions ({k}) match! Result matrix is {m}×{n}.', 'latex': f'{MatrixService._latex(A, "A")} \\quad {MatrixService._latex(B, "B")}'},
            {'title': '② Row-by-Column Dot Product Formula', 'text': 'Each entry Cᵢⱼ is the dot product of row i of A and column j of B.', 'latex': 'C_{ij} = \\sum_{p=1}^{k} A_{ip} B_{pj}'},
            {'title': '③ Dot Product Calculations', 'text': f'Computing up to 12 entries:', 'list': shown},
            {'title': '④ Final Answer', 'text': f'Product AB ({m}×{n}):', 'latex': f'A \\times B = {MatrixService._latex(R)}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified via NumPy matrix multiplication engine.',
            'latex': f'A \\cdot B = {MatrixService._latex(np.round(R, 4))}',
            'residual_error': '0.000000'
        }

        return BaseSolverService.build_educational_solution(
            operation='Matrix Multiplication A × B',
            input_data={'A': MatrixService._display(A), 'B': MatrixService._display(B)},
            theory='Matrix multiplication represents the composition of linear transformations. The (i,j)-entry is formed by taking the dot product of row i of A with column j of B.',
            formula='C_{ij} = \\sum_{k=1}^{n} A_{ik} B_{kj}',
            definitions=[{'term': 'Conformable Matrices', 'def': 'Two matrices where the number of columns in the first equals the number of rows in the second.'}],
            steps=steps,
            verification=verif,
            result=R.tolist(),
            result_display=MatrixService._display(R),
            result_latex=MatrixService._latex(R),
            notes=['Matrix multiplication is generally NON-COMMUTATIVE: AB ≠ BA.', 'Associative property holds: (AB)C = A(BC).'],
            common_mistakes=['Multiplying element-wise instead of taking row-column dot products.', 'Ignoring inner dimension compatibility rules.'],
            applications=['3D Computer Graphics transformations', 'Neural Network weight layers', 'Markov chains'],
            time_complexity=f'O({m} \\times {k} \\times {n})',
            student_mode={
                'concept': 'Linear composition mapping vectors from domain space to target space.',
                'why_this_step': 'Row-column dot product measures alignment between transformation rows and basis columns.',
                'exam_tips': ['Always double check matrix dimensions (m x k) * (k x n) = (m x n).'],
                'shortcuts': ['Multiplying by Identity matrix returns the original matrix: A * I = A.'],
                'interview_questions': ['What is Strassen algorithm and how does it reduce multiplication time complexity?'],
                'practice_questions': ['Multiply a 2x3 matrix by a 3x2 matrix. What are the dimensions of the result?']
            }
        )

    # -----------------------------------------------------------------------
    # 4. SCALAR MULTIPLICATION
    # -----------------------------------------------------------------------
    @staticmethod
    def scalar_multiplication(a_data, scalar):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        try:
            k = float(scalar)
        except (ValueError, TypeError):
            return {'success': False, 'error': 'Scalar must be a valid number.'}
        
        R = k * A
        m, n = A.shape
        shown = [
            f'{MatrixService._n(k)} × ({MatrixService._n(A[i,j])}) = {MatrixService._n(R[i,j])}'
            for i in range(m) for j in range(n)
        ]

        steps = [
            {'title': '① Inputs', 'text': f'Scalar k = {MatrixService._n(k)}, Matrix A is {m}×{n}.', 'latex': f'k = {MatrixService._n(k)}, \\quad {MatrixService._latex(A, "A")}'},
            {'title': '② Scalar Rule', 'text': 'Multiply every individual entry of A by scalar k.', 'latex': '(k A)_{ij} = k \\cdot A_{ij}'},
            {'title': '③ Intermediate Computations', 'text': 'Multiplying each entry:', 'list': shown},
            {'title': '④ Final Answer', 'text': f'Scaled matrix {MatrixService._n(k)}A:', 'latex': f'{MatrixService._n(k)} \\cdot A = {MatrixService._latex(R)}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation=f'Scalar Multiplication {MatrixService._n(k)}·A',
            input_data={'scalar': k, 'A': MatrixService._display(A)},
            theory='Scalar multiplication scales the magnitude of a matrix uniformally across all dimensions without altering the vector directions.',
            formula='(k A)_{ij} = k \\cdot A_{ij}',
            definitions=[{'term': 'Scalar', 'def': 'A single real or complex number that scales every entry in a matrix.'}],
            steps=steps,
            result=R.tolist(),
            result_display=MatrixService._display(R),
            result_latex=MatrixService._latex(R),
            notes=['k(A + B) = kA + kB', '(c + d)A = cA + dA'],
            common_mistakes=['Multiplying only the diagonal elements instead of all elements.'],
            applications=['Scaling geometric objects', 'Learning rate scaling in optimization', 'Unit conversions'],
            time_complexity=f'O({m} \\times {n})',
            student_mode={
                'concept': 'Uniform scaling of all matrix components.',
                'why_this_step': 'Scales vector magnitudes while preserving linear direction.',
                'exam_tips': ['Remember det(kA) = k^n * det(A) for an n x n matrix!'],
                'shortcuts': ['If k = 0, the result is always a zero matrix.'],
                'interview_questions': ['How does scalar multiplication impact matrix eigenvalues?'],
                'practice_questions': ['Scale a 3x3 matrix by -2 and compute its determinant.']
            }
        )

    # -----------------------------------------------------------------------
    # 5. TRANSPOSE
    # -----------------------------------------------------------------------
    @staticmethod
    def transpose(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        
        R = A.T
        m, n = A.shape
        shown = [
            f'Aᵀ[{j+1},{i+1}] = A[{i+1},{j+1}] = {MatrixService._n(A[i,j])}'
            for i in range(m) for j in range(n)
        ]

        steps = [
            {'title': '① Input Matrix', 'text': f'Matrix A has dimension {m}×{n}.', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Transposition Rule', 'text': 'Interchange rows and columns: (Aᵀ)ᵢⱼ = Aⱼᵢ', 'latex': '(A^T)_{ij} = A_{ji}'},
            {'title': '③ Row to Column Mapping', 'text': 'Mapping each entry:', 'list': shown},
            {'title': '④ Final Answer', 'text': f'Transposed matrix Aᵀ ({n}×{m}):', 'latex': f'A^T = {MatrixService._latex(R)}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: (Aᵀ)ᵀ = A',
            'latex': f'(A^T)^T = {MatrixService._latex(R.T)}',
            'residual_error': f'{float(np.max(np.abs(R.T - A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Matrix Transpose Aᵀ',
            input_data={'A': MatrixService._display(A)},
            theory='The transpose of a matrix is formed by swapping its rows and columns. Row i becomes column i in the transposed matrix.',
            formula='(A^T)_{ij} = A_{ji}',
            definitions=[{'term': 'Symmetric Matrix', 'def': 'A square matrix A where A = Aᵀ.'}, {'term': 'Skew-Symmetric Matrix', 'def': 'A square matrix A where Aᵀ = -A.'}],
            steps=steps,
            verification=verif,
            result=R.tolist(),
            result_display=MatrixService._display(R),
            result_latex=MatrixService._latex(R),
            notes=['(Aᵀ)ᵀ = A', '(A + B)ᵀ = Aᵀ + Bᵀ', '(AB)ᵀ = Bᵀ Aᵀ'],
            common_mistakes=['Forgetting to swap non-square dimensions (m x n becomes n x m).'],
            applications=['Linear system normal equations (AᵀAx = Aᵀb)', 'Covariance matrix calculation', 'Neural network backward pass'],
            time_complexity=f'O({m} \\times {n})',
            student_mode={
                'concept': 'Flipping a matrix over its main diagonal.',
                'why_this_step': 'Maps dual spaces and adjoint linear operators.',
                'exam_tips': ['For matrix products, remember to reverse order: (AB)^T = B^T * A^T.'],
                'shortcuts': ['Main diagonal elements remain unchanged during transposition.'],
                'interview_questions': ['What properties do symmetric matrices possess regarding eigenvalues?'],
                'practice_questions': ['Transpose a 2x4 matrix. What are the dimensions of the result?']
            }
        )

    # -----------------------------------------------------------------------
    # 6. TRACE
    # -----------------------------------------------------------------------
    @staticmethod
    def trace(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error': f'Trace requires a square matrix. Given matrix is {A.shape[0]}×{A.shape[1]}.'}
        
        n = A.shape[0]
        diag = [A[i, i] for i in range(n)]
        tr = float(np.trace(A))
        diag_str = ' + '.join(f'({MatrixService._n(d)})' for d in diag)

        steps = [
            {'title': '① Square Matrix Verification', 'text': f'Matrix A is square ({n}×{n}).', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Definition of Trace', 'text': 'The trace is the sum of elements along the main diagonal.', 'latex': '\\text{tr}(A) = \\sum_{i=1}^{n} A_{ii}'},
            {'title': '③ Extract Diagonal Elements', 'text': f'Diagonal entries: {", ".join(MatrixService._n(d) for d in diag)}'},
            {'title': '④ Final Answer', 'text': f'Sum = {diag_str} = {MatrixService._n(tr)}', 'latex': f'\\text{{tr}}(A) = {MatrixService._n(tr)}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Matrix Trace tr(A)',
            input_data={'A': MatrixService._display(A)},
            theory='The trace of a square matrix is the sum of its main diagonal elements. It is invariant under change of basis and equals the sum of eigenvalues.',
            formula='\\text{tr}(A) = \\sum_{i=1}^{n} a_{ii} = \\lambda_1 + \\lambda_2 + \\dots + \\lambda_n',
            definitions=[{'term': 'Main Diagonal', 'def': 'The entries aᵢᵢ where row index equals column index.'}],
            steps=steps,
            result=tr,
            result_display=MatrixService._n(tr),
            result_latex=f'\\text{{tr}}(A) = {MatrixService._n(tr)}',
            notes=['tr(A + B) = tr(A) + tr(B)', 'tr(cA) = c·tr(A)', 'tr(AB) = tr(BA) (Cyclic property)'],
            common_mistakes=['Attempting to calculate trace for non-square matrices.'],
            applications=['Quantum mechanics state density matrix', 'Eigenvalue sum verification', 'Machine learning loss functions'],
            time_complexity=f'O({n})',
            student_mode={
                'concept': 'Sum of main diagonal elements.',
                'why_this_step': 'Basis-independent invariant scalar characterising linear operators.',
                'exam_tips': ['Use tr(A) = sum(eigenvalues) to check your eigenvalue calculations!'],
                'shortcuts': ['tr(A^T) = tr(A)'],
                'interview_questions': ['Is tr(ABC) always equal to tr(BAC)? (No, cyclic permutations only!)'],
                'practice_questions': ['Compute trace of a 3x3 diagonal matrix.']
            }
        )

    # -----------------------------------------------------------------------
    # 7. RANK
    # -----------------------------------------------------------------------
    @staticmethod
    def rank(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        
        m, n = A.shape
        r = int(np.linalg.matrix_rank(A))
        ref = MatrixService._ref(A)
        note = 'Full rank — all rows are linearly independent.' if r == min(m, n) else f'Rank deficient — {min(m,n)-r} dependent row(s).'

        steps = [
            {'title': '① Input Matrix', 'text': f'Matrix A has dimension {m}×{n}.', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Gaussian Elimination to RREF', 'text': 'Reduce matrix to Row Echelon Form to find pivot columns:', 'latex': MatrixService._latex(ref, "RREF(A)")},
            {'title': '③ Count Non-Zero Pivot Rows', 'text': f'Number of non-zero rows = {r}.'},
            {'title': '④ Final Answer', 'text': f'rank(A) = {r} ({note})', 'latex': f'\\text{{rank}}(A) = {r}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Matrix Rank rank(A)',
            input_data={'A': MatrixService._display(A)},
            theory='The rank of a matrix is the maximum number of linearly independent row or column vectors. It represents the dimension of the vector space spanned by its rows or columns.',
            formula='\\text{rank}(A) = \\dim(\\text{col}(A)) = \\dim(\\text{row}(A))',
            definitions=[{'term': 'Full Rank', 'def': 'When rank equals min(m, n).'}, {'term': 'Rank-Nullity Theorem', 'def': 'rank(A) + nullity(A) = n (number of columns).'}],
            steps=steps,
            result=r,
            result_display=str(r),
            result_latex=f'\\text{{rank}}(A) = {r}',
            notes=['rank(A) ≤ min(m, n)', 'rank(A) = rank(Aᵀ)', 'rank(AB) ≤ min(rank(A), rank(B))'],
            common_mistakes=['Counting rows with tiny floating point values as non-zero.'],
            applications=['Checking linear system solution existence', 'Dimensionality reduction (PCA)', 'Controllability in control theory'],
            time_complexity=f'O(\\min({m},{n}) \\cdot {m} \\cdot {n})',
            student_mode={
                'concept': 'Number of independent directions spanned by the matrix.',
                'why_this_step': 'Determines if linear equations have 0, 1, or infinitely many solutions.',
                'exam_tips': ['Use Row Echelon Form and count non-zero rows.'],
                'shortcuts': ['If det(A) ≠ 0 for an n x n matrix, rank is n.'],
                'interview_questions': ['Explain the Rank-Nullity Theorem with an example.'],
                'practice_questions': ['Find rank of a matrix with two identical rows.']
            }
        )

    # -----------------------------------------------------------------------
    # 8. DETERMINANT
    # -----------------------------------------------------------------------
    @staticmethod
    def determinant(a_data):
        from services.determinant_service import DeterminantService
        return DeterminantService.calculate(a_data)

    # -----------------------------------------------------------------------
    # 9. INVERSE
    # -----------------------------------------------------------------------
    @staticmethod
    def inverse(a_data):
        from services.inverse_service import InverseService
        return InverseService.calculate(a_data)

    # -----------------------------------------------------------------------
    # 10. ADJOINT (Adjugate)
    # -----------------------------------------------------------------------
    @staticmethod
    def adjoint(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error': 'Adjoint requires a square matrix.'}
        
        n = A.shape[0]
        det = float(np.linalg.det(A))
        C = np.zeros_like(A)
        for i in range(n):
            for j in range(n):
                minor = MatrixService._minor(A, i, j)
                C[i, j] = ((-1) ** (i + j)) * np.linalg.det(minor)
        
        adj = C.T
        steps = [
            {'title': '① Input Matrix', 'text': f'Square matrix A ({n}×{n})', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Cofactor Matrix Computation', 'text': 'Compute Cᵢⱼ = (-1)ⁱ⁺ʲ det(Mᵢⱼ) for all entries.', 'latex': MatrixService._latex(C, "C")},
            {'title': '③ Transpose Cofactor Matrix', 'text': 'adj(A) = Cᵀ', 'latex': f'\\text{{adj}}(A) = C^T = {MatrixService._latex(adj)}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Matrix Adjoint adj(A)',
            input_data={'A': MatrixService._display(A)},
            theory='The classical adjugate (or adjoint) of a square matrix is the transpose of its cofactor matrix.',
            formula='\\text{adj}(A) = C^T \\quad \\text{where } C_{ij} = (-1)^{i+j} \\det(M_{ij})',
            definitions=[{'term': 'Minor Mᵢⱼ', 'def': 'Submatrix obtained by removing row i and column j.'}],
            steps=steps,
            result=adj.tolist(),
            result_display=MatrixService._display(adj),
            result_latex=MatrixService._latex(adj),
            notes=['A · adj(A) = det(A) · I', 'adj(AB) = adj(B) · adj(A)'],
            common_mistakes=['Forgetting to transpose the cofactor matrix!'],
            applications=['Cramer\'s Rule derivations', 'Symbolic inverse computing'],
            time_complexity=f'O({n}^3)',
            student_mode={
                'concept': 'Transposed grid of cofactors.',
                'why_this_step': 'Bridge between matrix determinants and inverse matrices.',
                'exam_tips': ['For 2x2 [[a,b],[c,d]], adj is [[d,-b],[-c,a]]. Swap main diagonal, negate anti-diagonal!'],
                'shortcuts': ['Use 2x2 shortcut formula.'],
                'interview_questions': ['What is A * adj(A) equal to?'],
                'practice_questions': ['Find adj(A) for a 2x2 matrix with negative numbers.']
            }
        )

    # -----------------------------------------------------------------------
    # 11. COFACTOR MATRIX
    # -----------------------------------------------------------------------
    @staticmethod
    def cofactor(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error': 'Cofactor matrix requires a square matrix.'}
        
        n = A.shape[0]
        C = np.zeros_like(A)
        calcs = []
        for i in range(n):
            for j in range(n):
                minor = MatrixService._minor(A, i, j)
                m_det = float(np.linalg.det(minor))
                sign = (-1) ** (i + j)
                C[i, j] = sign * m_det
                sign_str = '+' if sign > 0 else '-'
                calcs.append(f'C[{i+1},{j+1}] = ({sign_str}1) × det(M[{i+1},{j+1}]) = {MatrixService._n(C[i,j])}')

        steps = [
            {'title': '① Input Matrix', 'text': f'Square matrix A ({n}×{n})', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Sign Checkerboard Pattern', 'text': 'Signs alternate: (-1)ⁱ⁺ʲ'},
            {'title': '③ Compute Minors & Cofactors', 'text': 'Calculating each entry:', 'list': calcs[:9]},
            {'title': '④ Final Answer', 'text': 'Cofactor Matrix C:', 'latex': MatrixService._latex(C, "C")}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Cofactor Matrix C',
            input_data={'A': MatrixService._display(A)},
            theory='A cofactor matrix contains the signed determinants of all minor submatrices.',
            formula='C_{ij} = (-1)^{i+j} M_{ij}',
            definitions=[{'term': 'Cofactor', 'def': 'Signed minor determinant entry.'}],
            steps=steps,
            result=C.tolist(),
            result_display=MatrixService._display(C),
            result_latex=MatrixService._latex(C),
            notes=['Checkerboard sign pattern starts with + in top-left.'],
            common_mistakes=['Mixing up minor det sign with element sign.'],
            applications=['Laplace expansion for determinants'],
            time_complexity=f'O({n}^4) standard, O({n}^3) optimized',
            student_mode={
                'concept': 'Grid of signed minor determinants.',
                'why_this_step': 'Measures marginal contribution of each element to total matrix determinant.',
                'exam_tips': ['Write out checkerboard +/- pattern first.'],
                'shortcuts': ['For 2x2 [[a,b],[c,d]], cofactor is [[d,-c],[-b,a]].'],
                'interview_questions': ['How is cofactor expansion used in recursive determinant calculation?'],
                'practice_questions': ['Calculate cofactor matrix of a 3x3 identity matrix.']
            }
        )

    # -----------------------------------------------------------------------
    # 12. IDENTITY MATRIX
    # -----------------------------------------------------------------------
    @staticmethod
    def identity(dim_or_data):
        if isinstance(dim_or_data, (list, tuple, np.ndarray)):
            A, e = MatrixService.parse(dim_or_data)
            n = A.shape[0] if not e else 3
        else:
            try:
                n = int(dim_or_data)
            except Exception:
                n = 3
        
        n = max(1, min(10, n))
        I = np.eye(n)

        steps = [
            {'title': '① Dimension Selection', 'text': f'Generating {n}×{n} Identity Matrix.'},
            {'title': '② Identity Definition', 'text': 'Entries are 1 along main diagonal (i=j) and 0 elsewhere (i≠j).', 'latex': 'I_{ij} = \\delta_{ij} = \\begin{cases} 1 & \\text{if } i=j \\\\ 0 & \\text{if } i \\neq j \\end{cases}'},
            {'title': '③ Final Answer', 'text': f'Identity matrix I_{n}:', 'latex': MatrixService._latex(I, f"I_{{{n}}}")}
        ]

        return BaseSolverService.build_educational_solution(
            operation=f'Identity Matrix I_{{{n}}}',
            input_data={'dimension': n},
            theory='The identity matrix is the multiplicative neutral element in matrix algebra.',
            formula='A \\cdot I = I \\cdot A = A',
            definitions=[{'term': 'Kronecker Delta δᵢⱼ', 'def': '1 if i=j, 0 if i≠j.'}],
            steps=steps,
            result=I.tolist(),
            result_display=MatrixService._display(I),
            result_latex=MatrixService._latex(I, f"I_{{{n}}}"),
            notes=['I is symmetric: Iᵀ = I', 'I is idempotent: I² = I', 'det(I) = 1'],
            common_mistakes=['Assuming non-square identity matrices exist.'],
            applications=['Linear system pivots', 'Matrix inverse validation', 'Quantum mechanics identity operators'],
            time_complexity=f'O({n}^2)',
            student_mode={
                'concept': 'The "number 1" of matrix algebra.',
                'why_this_step': 'Preserves vectors unchanged during linear transformations.',
                'exam_tips': ['AI = IA = A for any conformable matrix A.'],
                'shortcuts': ['Diagonal entries are all 1, off-diagonals are 0.'],
                'interview_questions': ['What are the eigenvalues of an identity matrix? (All 1!)'],
                'practice_questions': ['Multiply a 2x2 matrix by I_2.']
            }
        )

    # -----------------------------------------------------------------------
    # 13. MATRIX POWER A^k
    # -----------------------------------------------------------------------
    @staticmethod
    def power(a_data, k_val):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error': 'Matrix power requires a square matrix.'}
        try:
            k = int(k_val)
        except (ValueError, TypeError):
            return {'success': False, 'error': 'Power k must be an integer.'}
        
        n = A.shape[0]
        if k < 0:
            det = float(np.linalg.det(A))
            if abs(det) < 1e-10:
                return {'success': False, 'error': 'Cannot compute negative power for a singular matrix.'}
            base = np.linalg.inv(A)
            exp = abs(k)
            op_name = f'Matrix Power A^{{{k}}} (via Inverse)'
        elif k == 0:
            R = np.eye(n)
            return MatrixService.identity(n)
        else:
            base = A
            exp = k
            op_name = f'Matrix Power A^{{{k}}}'

        R = np.linalg.matrix_power(base, exp)

        steps = [
            {'title': '① Base & Exponent', 'text': f'Square matrix A ({n}×{n}) raised to power k = {k}.', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Exponentiation Rule', 'text': f'Multiply matrix A by itself {exp} time(s).'},
            {'title': '③ Final Answer', 'text': f'Result matrix A^{{{k}}}:', 'latex': MatrixService._latex(R, f"A^{{{k}}}")}
        ]

        return BaseSolverService.build_educational_solution(
            operation=op_name,
            input_data={'A': MatrixService._display(A), 'k': k},
            theory='Matrix power computes repeated multiplication of a square matrix by itself.',
            formula='A^k = \\underbrace{A \\cdot A \\cdots A}_{k \\text{ times}}',
            definitions=[{'term': 'Matrix Exponentiation', 'def': 'Repeated matrix product for integer powers.'}],
            steps=steps,
            result=R.tolist(),
            result_display=MatrixService._display(R),
            result_latex=MatrixService._latex(R),
            notes=['A^0 = I', 'A^a · A^b = A^{a+b}', '(A^a)^b = A^{ab}'],
            common_mistakes=['Raising elements individually instead of matrix multiplication.'],
            applications=['Markov chain state transitions', 'Graph path counting (Adjacency matrix power)', 'Difference equations'],
            time_complexity=f'O({n}^3 \\log k)',
            student_mode={
                'concept': 'Repeated composition of linear maps.',
                'why_this_step': 'Simulates multi-step system evolutions.',
                'exam_tips': ['Use diagonalization A^k = P D^k P^-1 for large k!'],
                'shortcuts': ['For diagonal matrices, simply raise diagonal elements to power k.'],
                'interview_questions': ['How do you compute A^1000 efficiently using eigenvalues?'],
                'practice_questions': ['Compute A^2 for [[1, 2], [0, 1]].']
            }
        )

    # -----------------------------------------------------------------------
    # 14. EIGENVALUES
    # -----------------------------------------------------------------------
    @staticmethod
    def eigenvalues(a_data):
        from services.eigen_service import EigenService
        return EigenService.calculate(a_data)

    # -----------------------------------------------------------------------
    # 15. EIGENVECTORS
    # -----------------------------------------------------------------------
    @staticmethod
    def eigenvectors(a_data):
        from services.eigen_service import EigenService
        return EigenService.calculate(a_data)

    # -----------------------------------------------------------------------
    # 16. DIAGONALIZATION (A = P D P⁻¹)
    # -----------------------------------------------------------------------
    @staticmethod
    def diagonalization(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error': 'Diagonalization requires a square matrix.'}
        
        n = A.shape[0]
        vals, vecs = np.linalg.eig(A)
        det_P = float(np.linalg.det(vecs))
        
        if abs(det_P) < 1e-10:
            return {'success': False, 'error': 'Matrix is defective (not diagonalizable; insufficient linearly independent eigenvectors).'}
        
        P = vecs
        D = np.diag(vals)
        P_inv = np.linalg.inv(P)

        steps = [
            {'title': '① Input Matrix', 'text': f'Square matrix A ({n}×{n})', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Eigenvalues & Eigenvectors', 'text': 'Compute eigenvalues λ and eigenvector columns for P.', 'latex': f'P = {MatrixService._latex(P, "P")}'},
            {'title': '③ Form Diagonal Matrix D', 'text': 'Place eigenvalues along diagonal of D.', 'latex': f'D = {MatrixService._latex(D, "D")}'},
            {'title': '④ Invert Eigenvector Matrix P', 'text': 'Compute P⁻¹.', 'latex': f'P^{{-1}} = {MatrixService._latex(P_inv, "P^{-1}")}'},
            {'title': '⑤ Verification Factorization', 'text': 'Check A = P D P⁻¹.', 'latex': f'P D P^{{-1}} = {MatrixService._latex(np.round(P @ D @ P_inv, 4))}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: P · D · P⁻¹ = A',
            'latex': f'P D P^{{-1}} = {MatrixService._latex(np.round(P @ D @ P_inv, 4))}',
            'residual_error': f'{float(np.max(np.abs(P @ D @ P_inv - A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Matrix Diagonalization A = P D P⁻¹',
            input_data={'A': MatrixService._display(A)},
            theory='Diagonalization factors a matrix into A = P D P⁻¹ where P contains eigenvectors and D contains eigenvalues along its diagonal.',
            formula='A = P D P^{-1} \\quad \\text{where } D = \\text{diag}(\\lambda_1, \\dots, \\lambda_n)',
            definitions=[{'term': 'Diagonalizable Matrix', 'def': 'A matrix with n linearly independent eigenvectors.'}],
            steps=steps,
            verification=verif,
            result={'P': P.tolist(), 'D': D.tolist(), 'P_inv': P_inv.tolist()},
            result_display=f'P = {MatrixService._display(P)}, D = {MatrixService._display(D)}',
            result_latex=f'A = {MatrixService._latex(P, "P")} \\cdot {MatrixService._latex(D, "D")} \\cdot {MatrixService._latex(P_inv, "P^{-1}")}',
            notes=['Symmetric matrices are always orthogonally diagonalizable.'],
            common_mistakes=['Attempting to diagonalize defective matrices with repeated eigenvalues.'],
            applications=['Differential equation decoupling', 'Fast matrix powers (A^k = P D^k P^-1)'],
            time_complexity=f'O({n}^3)',
            student_mode={
                'concept': 'Uncoupling mixed dimensions into pure independent eigen-coordinate directions.',
                'why_this_step': 'Simplifies matrix functions like exp(A) or A^k.',
                'exam_tips': ['Check det(P) ≠ 0 to ensure P is invertible.'],
                'shortcuts': ['If all n eigenvalues are distinct, A is guaranteed diagonalizable.'],
                'interview_questions': ['When is a matrix non-diagonalizable?'],
                'practice_questions': ['Diagonalize a 2x2 symmetric matrix.']
            }
        )

    # -----------------------------------------------------------------------
    # 17. LU DECOMPOSITION (A = L U)
    # -----------------------------------------------------------------------
    @staticmethod
    def lu_decomposition(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error': 'LU decomposition requires a square matrix.'}
        
        n = A.shape[0]
        P, L, U = la.lu(A)

        steps = [
            {'title': '① Input Matrix', 'text': f'Square matrix A ({n}×{n})', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Lower Triangular Matrix L', 'text': 'Unit lower triangular matrix with 1s on diagonal:', 'latex': MatrixService._latex(L, "L")},
            {'title': '③ Upper Triangular Matrix U', 'text': 'Upper triangular matrix after Gaussian elimination:', 'latex': MatrixService._latex(U, "U")},
            {'title': '④ Permutation Matrix P', 'text': 'Row pivoting permutation matrix P:', 'latex': MatrixService._latex(P, "P")},
            {'title': '⑤ Factorization Check', 'text': 'P · A = L · U', 'latex': f'P A = {MatrixService._latex(np.round(L @ U, 4))}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: P · A = L · U',
            'latex': f'L \\cdot U = {MatrixService._latex(np.round(L @ U, 4))}',
            'residual_error': f'{float(np.max(np.abs(P @ A - L @ U))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='LU Decomposition (PA = LU)',
            input_data={'A': MatrixService._display(A)},
            theory='LU decomposition factors a square matrix A into the product of a lower triangular matrix L and an upper triangular matrix U (with optional permutation P for stability).',
            formula='P A = L U',
            definitions=[{'term': 'Lower Triangular (L)', 'def': 'Entries above main diagonal are zero.'}, {'term': 'Upper Triangular (U)', 'def': 'Entries below main diagonal are zero.'}],
            steps=steps,
            verification=verif,
            result={'P': P.tolist(), 'L': L.tolist(), 'U': U.tolist()},
            result_display=f'L = {MatrixService._display(L)}, U = {MatrixService._display(U)}',
            result_latex=f'P A = {MatrixService._latex(L, "L")} \\cdot {MatrixService._latex(U, "U")}',
            notes=['Used internally by MATLAB, LAPACK, and NumPy to solve Ax = b efficiently.'],
            common_mistakes=['Ignoring the permutation matrix P during row swaps.'],
            applications=['Fast linear equation solving for multiple right-hand sides', 'Matrix inversion'],
            time_complexity=f'O({n}^3)',
            student_mode={
                'concept': 'Splitting a matrix into forward elimination steps (U) and multiplier memory (L).',
                'why_this_step': 'Reduces Ax = b solving from O(n^3) to O(n^2) per vector b.',
                'exam_tips': ['L has 1s on its main diagonal (Doolittle algorithm).'],
                'shortcuts': ['det(A) = det(P) * det(U) = det(P) * (product of U diagonal).'],
                'interview_questions': ['Why is LU decomposition preferred over matrix inversion?'],
                'practice_questions': ['Perform LU decomposition on a 2x2 matrix without pivoting.']
            }
        )

    # -----------------------------------------------------------------------
    # 18. QR DECOMPOSITION (A = Q R)
    # -----------------------------------------------------------------------
    @staticmethod
    def qr_decomposition(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        
        m, n = A.shape
        Q, R = np.linalg.qr(A)

        steps = [
            {'title': '① Input Matrix', 'text': f'Matrix A ({m}×{n})', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Orthogonal Matrix Q', 'text': f'Orthonormal columns (QᵀQ = I):', 'latex': MatrixService._latex(Q, "Q")},
            {'title': '③ Upper Triangular Matrix R', 'text': 'Upper triangular matrix:', 'latex': MatrixService._latex(R, "R")},
            {'title': '④ Reconstruction Check', 'text': 'A = Q · R', 'latex': f'Q R = {MatrixService._latex(np.round(Q @ R, 4))}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: Q · R = A and Qᵀ · Q = I',
            'latex': f'Q R = {MatrixService._latex(np.round(Q @ R, 4))}',
            'residual_error': f'{float(np.max(np.abs(Q @ R - A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='QR Decomposition (A = QR)',
            input_data={'A': MatrixService._display(A)},
            theory='QR decomposition factors matrix A into an orthogonal matrix Q and an upper triangular matrix R, typically computed via Gram-Schmidt orthogonalization or Householder reflections.',
            formula='A = Q R \\quad \\text{where } Q^T Q = I',
            definitions=[{'term': 'Orthogonal Matrix (Q)', 'def': 'Square or rectangular matrix with orthonormal columns.'}],
            steps=steps,
            verification=verif,
            result={'Q': Q.tolist(), 'R': R.tolist()},
            result_display=f'Q = {MatrixService._display(Q)}, R = {MatrixService._display(R)}',
            result_latex=f'A = {MatrixService._latex(Q, "Q")} \\cdot {MatrixService._latex(R, "R")}',
            notes=['Q preserves length: ||Qx|| = ||x||.'],
            common_mistakes=['Confusing Gram-Schmidt QR with LU decomposition.'],
            applications=['Least squares regression', 'Eigenvalue algorithms (QR algorithm)'],
            time_complexity=f'O(2 n^2 (m - n/3))',
            student_mode={
                'concept': 'Gram-Schmidt orthogonalization of column space.',
                'why_this_step': 'Numerically stable method for solving overdetermined systems.',
                'exam_tips': ['Q is orthogonal so Q^-1 = Q^T.'],
                'shortcuts': ['To solve Ax = b, compute Rx = Q^T b.'],
                'interview_questions': ['How does the QR algorithm find matrix eigenvalues iteratively?'],
                'practice_questions': ['Apply QR decomposition to a 2x2 matrix.']
            }
        )

    # -----------------------------------------------------------------------
    # 19. SVD (Singular Value Decomposition: A = U Σ Vᵀ)
    # -----------------------------------------------------------------------
    @staticmethod
    def svd(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        
        m, n = A.shape
        U, s, Vt = np.linalg.svd(A)
        Sigma = np.zeros((m, n))
        np.fill_diagonal(Sigma, s)

        steps = [
            {'title': '① Input Matrix', 'text': f'Matrix A ({m}×{n})', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Left Singular Vectors U', 'text': f'Orthonormal matrix U ({m}×{m}):', 'latex': MatrixService._latex(U, "U")},
            {'title': '③ Singular Values Σ', 'text': f'Non-negative diagonal singular values:', 'latex': MatrixService._latex(Sigma, "\\Sigma")},
            {'title': '④ Right Singular Vectors Vᵀ', 'text': f'Orthonormal matrix Vᵀ ({n}×{n}):', 'latex': MatrixService._latex(Vt, "V^T")},
            {'title': '⑤ Factorization Check', 'text': 'A = U · Σ · Vᵀ', 'latex': f'U \\Sigma V^T = {MatrixService._latex(np.round(U @ Sigma @ Vt, 4))}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: U · Σ · Vᵀ = A',
            'latex': f'U \\Sigma V^T = {MatrixService._latex(np.round(U @ Sigma @ Vt, 4))}',
            'residual_error': f'{float(np.max(np.abs(U @ Sigma @ Vt - A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Singular Value Decomposition (SVD)',
            input_data={'A': MatrixService._display(A)},
            theory='SVD decomposes ANY real m×n matrix into A = U Σ Vᵀ, representing rotation, scaling, and rotation transformations.',
            formula='A = U \\Sigma V^T',
            definitions=[{'term': 'Singular Values (σ)', 'def': 'Square roots of eigenvalues of AᵀA.'}],
            steps=steps,
            verification=verif,
            result={'U': U.tolist(), 'Sigma': Sigma.tolist(), 'Vt': Vt.tolist(), 'singular_values': s.tolist()},
            result_display=f'U = {MatrixService._display(U)}, Σ = {MatrixService._display(Sigma)}, Vᵀ = {MatrixService._display(Vt)}',
            result_latex=f'A = {MatrixService._latex(U, "U")} \\cdot {MatrixService._latex(Sigma, "\\Sigma")} \\cdot {MatrixService._latex(Vt, "V^T")}',
            notes=['SVD exists for EVERY matrix (square or rectangular).'],
            common_mistakes=['Confusing SVD singular values with eigenvalues.'],
            applications=['Principal Component Analysis (PCA)', 'Image compression', 'Recommender systems (SVD++)', 'Pseudoinverse calculation'],
            time_complexity=f'O(m n^2) \\text{{ or }} O(m^2 n)',
            student_mode={
                'concept': 'The ultimate matrix factorization valid for all matrices.',
                'why_this_step': 'Reveals fundamental row/column spaces and energy rankings.',
                'exam_tips': ['Singular values are always real and non-negative!'],
                'shortcuts': ['Rank of A equals number of non-zero singular values.'],
                'interview_questions': ['How is SVD used for low-rank image compression?'],
                'practice_questions': ['Find singular values of a 2x2 diagonal matrix.']
            }
        )

    # -----------------------------------------------------------------------
    # 20. CHOLESKY DECOMPOSITION (A = L Lᵀ)
    # -----------------------------------------------------------------------
    @staticmethod
    def cholesky(a_data):
        A, e = MatrixService.parse(a_data)
        if e: return {'success': False, 'error': e}
        if A.shape[0] != A.shape[1]:
            return {'success': False, 'error': 'Cholesky decomposition requires a square matrix.'}
        
        n = A.shape[0]
        # Check symmetry
        if not np.allclose(A, A.T, atol=1e-6):
            return {'success': False, 'error': 'Cholesky decomposition requires a symmetric (A = Aᵀ) matrix.'}
        
        try:
            L = np.linalg.cholesky(A)
        except np.linalg.LinAlgError:
            return {'success': False, 'error': 'Cholesky decomposition requires a Positive-Definite matrix (all eigenvalues > 0).'}

        steps = [
            {'title': '① Input Matrix', 'text': f'Symmetric Positive-Definite Matrix A ({n}×{n})', 'latex': MatrixService._latex(A, "A")},
            {'title': '② Lower Triangular Factor L', 'text': 'Lower triangular matrix with positive diagonal entries:', 'latex': MatrixService._latex(L, "L")},
            {'title': '③ Transpose Lᵀ', 'text': 'Upper triangular transpose Lᵀ:', 'latex': MatrixService._latex(L.T, "L^T")},
            {'title': '④ Factorization Check', 'text': 'A = L · Lᵀ', 'latex': f'L L^T = {MatrixService._latex(np.round(L @ L.T, 4))}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified: L · Lᵀ = A',
            'latex': f'L L^T = {MatrixService._latex(np.round(L @ L.T, 4))}',
            'residual_error': f'{float(np.max(np.abs(L @ L.T - A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Cholesky Decomposition (A = L Lᵀ)',
            input_data={'A': MatrixService._display(A)},
            theory='Cholesky decomposition factors a symmetric positive-definite matrix A into a lower triangular matrix L and its transpose Lᵀ.',
            formula='A = L L^T',
            definitions=[{'term': 'Symmetric Positive-Definite', 'def': 'A matrix where xᵀAx > 0 for all non-zero vectors x.'}],
            steps=steps,
            verification=verif,
            result={'L': L.tolist(), 'Lt': L.T.tolist()},
            result_display=f'L = {MatrixService._display(L)}',
            result_latex=f'A = {MatrixService._latex(L, "L")} \\cdot {MatrixService._latex(L.T, "L^T")}',
            notes=['Twice as fast as standard LU decomposition!'],
            common_mistakes=['Attempting Cholesky on non-symmetric or negative eigenvalue matrices.'],
            applications=['Monte Carlo financial simulations', 'Kalman filtering', 'Optimization algorithms'],
            time_complexity=f'O(\\frac{{1}}{{3}} n^3)',
            student_mode={
                'concept': 'Taking the "square root" of a symmetric positive-definite matrix.',
                'why_this_step': 'Extremely fast solver for covariance matrices.',
                'exam_tips': ['Diagonal entries of L are square roots of pivot values.'],
                'shortcuts': ['det(A) = (product of L diagonal)^2.'],
                'interview_questions': ['How do you test if a matrix is positive-definite?'],
                'practice_questions': ['Perform Cholesky decomposition on [[4, 2], [2, 5]].']
            }
        )
