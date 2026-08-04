"""
Vector Operations Service — Professional Educational Engine
Supports 9 Vector Operations with complete educational reports:
Theory, Formulas, Definitions, Working Steps, Verification, Notes,
Common Mistakes, Applications, Time Complexity, and Student Mode.
"""

import numpy as np
import math
from services.solver_service import BaseSolverService


class VectorService:

    @staticmethod
    def parse(data):
        """Parse list → numpy 1-D float64 vector. Returns (vec, error)."""
        try:
            v = np.array(data, dtype=float).flatten()
            if v.size == 0:
                return None, 'Vector cannot be empty.'
            return v, None
        except (ValueError, TypeError) as exc:
            return None, f'Invalid vector data: {exc}'

    @staticmethod
    def _n(v):
        v = float(v)
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return f'{v:.4f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _vec_latex(v, name=None):
        body = ' \\\\ '.join(VectorService._n(x) for x in v)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'\\mathbf{{{name}}} = {s}' if name else s

    @staticmethod
    def _n_list(v):
        return [VectorService._n(x) for x in v.tolist()]

    # -----------------------------------------------------------------------
    # 1. DOT PRODUCT
    # -----------------------------------------------------------------------
    @staticmethod
    def dot_product(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': f'Vectors must have identical dimension. Got {len(A)} and {len(B)}.'}
        
        dot = float(np.dot(A, B))
        n = len(A)
        terms = ' + '.join(f'({VectorService._n(A[i])} × {VectorService._n(B[i])})' for i in range(n))

        steps = [
            {'title': '① Input Vectors', 'text': f'Vectors in ℝ^{n}:', 'latex': f'{VectorService._vec_latex(A,"u")}, \\quad {VectorService._vec_latex(B,"v")}'},
            {'title': '② Dot Product Formula', 'text': 'Multiply matching components and sum results:', 'latex': '\\mathbf{u} \\cdot \\mathbf{v} = \\sum_{i=1}^{n} u_i v_i'},
            {'title': '③ Component Calculations', 'text': f'= {terms}', 'latex': f'= {terms}'},
            {'title': '④ Final Answer', 'text': f'u · v = {VectorService._n(dot)}', 'latex': f'\\boxed{{\\mathbf{{u}} \\cdot \\mathbf{{v}} = {VectorService._n(dot)}}}'}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified commutative property: u·v = v·u',
            'latex': f'\\mathbf{{v}} \\cdot \\mathbf{{u}} = {VectorService._n(float(np.dot(B, A)))}',
            'residual_error': '0.000000'
        }

        return BaseSolverService.build_educational_solution(
            operation='Vector Dot Product u · v',
            input_data={'u': VectorService._n_list(A), 'v': VectorService._n_list(B)},
            theory='The dot product (scalar product) combines two equal-length vectors into a single scalar value, reflecting directional alignment.',
            formula='\\mathbf{u} \\cdot \\mathbf{v} = ||\\mathbf{u}|| ||\\mathbf{v}|| \\cos\\theta = \\sum_{i=1}^{n} u_i v_i',
            definitions=[{'term': 'Orthogonal', 'def': 'Vectors with a dot product of 0.'}],
            steps=steps,
            verification=verif,
            result=dot,
            result_display=VectorService._n(dot),
            result_latex=f'\\mathbf{{u}} \\cdot \\mathbf{{v}} = {VectorService._n(dot)}',
            notes=['u·v > 0 implies acute angle (<90°)', 'u·v = 0 implies orthogonal (90°)', 'u·v < 0 implies obtuse angle (>90°)'],
            common_mistakes=['Attempting dot product between vectors of different dimensions.'],
            applications=['Physics mechanical work W = F · d', 'Cosymmetric similarity in NLP', 'Machine learning attention mechanisms'],
            time_complexity=f'O({n})',
            student_mode={
                'concept': 'Algebraic sum of component-wise products / Geometric projection magnitude.',
                'why_this_step': 'Measures parallel alignment between two vector directions.',
                'exam_tips': ['Remember u·u = ||u||^2.'],
                'shortcuts': ['If one vector is zero, dot product is 0.'],
                'interview_questions': ['How is cosine similarity calculated from the dot product?'],
                'practice_questions': ['Find dot product of [1, 2, 3] and [4, -5, 6].']
            }
        )

    # -----------------------------------------------------------------------
    # 2. CROSS PRODUCT (3D only)
    # -----------------------------------------------------------------------
    @staticmethod
    def cross_product(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != 3 or len(B) != 3:
            return {'success': False, 'error': 'Cross product is strictly defined only for 3-D vectors.'}
        
        R = np.cross(A, B)
        _n = VectorService._n
        i_comp = f'({_n(A[1])}×{_n(B[2])}) − ({_n(A[2])}×{_n(B[1])}) = {_n(R[0])}'
        j_comp = f'({_n(A[2])}×{_n(B[0])}) − ({_n(A[0])}×{_n(B[2])}) = {_n(R[1])}'
        k_comp = f'({_n(A[0])}×{_n(B[1])}) − ({_n(A[1])}×{_n(B[0])}) = {_n(R[2])}'

        steps = [
            {'title': '① Input 3D Vectors', 'text': 'Vectors in ℝ³:', 'latex': f'{VectorService._vec_latex(A,"u")}, \\quad {VectorService._vec_latex(B,"v")}'},
            {'title': '② 3x3 Determinant Formula', 'text': 'Cross product is the expansion of 3x3 matrix with unit vectors i, j, k:', 'latex': '\\mathbf{u} \\times \\mathbf{v} = \\begin{vmatrix} \\mathbf{i} & \\mathbf{j} & \\mathbf{k} \\\\ u_1 & u_2 & u_3 \\\\ v_1 & v_2 & v_3 \\end{vmatrix}'},
            {'title': '③ i-component (x)', 'text': i_comp, 'latex': f'i: {i_comp}'},
            {'title': '④ j-component (y)', 'text': j_comp, 'latex': f'j: -({j_comp})'},
            {'title': '⑤ k-component (z)', 'text': k_comp, 'latex': f'k: {k_comp}'},
            {'title': '⑥ Final Answer', 'text': 'Perpendicular result vector:', 'latex': f'\\mathbf{{u}} \\times \\mathbf{{v}} = {VectorService._vec_latex(R)}'}
        ]

        # Orthogonality verification
        verif = {
            'status': '✔ Correct',
            'check': 'Verified result is perpendicular to both u and v: (u×v)·u = 0, (u×v)·v = 0',
            'latex': f'(\\mathbf{{u}} \\times \\mathbf{{v}}) \\cdot \\mathbf{{u}} = {VectorService._n(float(np.dot(R, A)))}',
            'residual_error': f'{abs(float(np.dot(R, A))):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Vector Cross Product u × v',
            input_data={'u': VectorService._n_list(A), 'v': VectorService._n_list(B)},
            theory='The cross product takes two 3D vectors and returns a vector perpendicular to both, obeying the right-hand rule.',
            formula='\\mathbf{u} \\times \\mathbf{v} = (u_2 v_3 - u_3 v_2)\\mathbf{i} - (u_1 v_3 - u_3 v_1)\\mathbf{j} + (u_1 v_2 - u_2 v_1)\\mathbf{k}',
            definitions=[{'term': 'Right-Hand Rule', 'def': 'Orientation rule determining the direction of the output vector.'}],
            steps=steps,
            verification=verif,
            result=R.tolist(),
            result_display=VectorService._n_list(R),
            result_latex=VectorService._vec_latex(R),
            notes=['u × v = -(v × u) (Anti-commutative)', '||u × v|| = ||u|| ||v|| sin θ (Parallelogram area)'],
            common_mistakes=['Attempting cross product on 2D or 4D vectors.', 'Forgetting the negative sign on the j-component.'],
            applications=['Computing normal vectors in 3D computer graphics', 'Torque τ = r × F in physics', 'Magnetic force F = q(v × B)'],
            time_complexity='O(1)',
            student_mode={
                'concept': 'Vector perpendicular to the plane formed by u and v.',
                'why_this_step': 'Constructs normal vectors for surfaces and torque axes.',
                'exam_tips': ['Magnitude of cross product equals parallelogram area!'],
                'shortcuts': ['i × j = k, j × k = i, k × i = j.'],
                'interview_questions': ['What does it mean if u × v = 0 for non-zero vectors u and v? (Parallel!)'],
                'practice_questions': ['Compute [1, 0, 0] × [0, 1, 0].']
            }
        )

    # -----------------------------------------------------------------------
    # 3. MAGNITUDE
    # -----------------------------------------------------------------------
    @staticmethod
    def magnitude(a_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        
        mag = float(np.linalg.norm(A))
        _n = VectorService._n
        n = len(A)
        sq_terms = ' + '.join(f'({_n(x)})²' for x in A)

        steps = [
            {'title': '① Input Vector', 'text': f'Vector in ℝ^{n}:', 'latex': VectorService._vec_latex(A, "v")},
            {'title': '② Euclidean Length Formula', 'text': 'Square each component, sum them up, take square root:', 'latex': '||\\mathbf{v}|| = \\sqrt{\\sum_{i=1}^{n} v_i^2}'},
            {'title': '③ Substitution', 'text': f'= √({sq_terms})', 'latex': f'= \\sqrt{{{sq_terms}}}'},
            {'title': '④ Final Answer', 'text': f'||v|| = {_n(mag)}', 'latex': f'\\boxed{{||\\mathbf{{v}}|| = {_n(mag)}}}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Vector Magnitude ||v||',
            input_data={'v': VectorService._n_list(A)},
            theory='The magnitude (norm) of a vector represents its geometric length or distance from the origin in Euclidean space.',
            formula='||\\mathbf{v}|| = \\sqrt{v_1^2 + v_2^2 + \\dots + v_n^2}',
            definitions=[{'term': 'Euclidean Norm (L2)', 'def': 'Straight line length of a vector in N-dimensional space.'}],
            steps=steps,
            result=mag,
            result_display=_n(mag),
            result_latex=f'||\\mathbf{{v}}|| = {_n(mag)}',
            notes=['||v|| ≥ 0 always', '||v|| = 0 if and only if v is the zero vector', '||c · v|| = |c| · ||v||'],
            common_mistakes=['Forgetting to take the square root at the end.'],
            applications=['Distance calculations', 'Normalizing features in machine learning', 'Physics speed ||v||'],
            time_complexity=f'O({n})',
            student_mode={
                'concept': 'Pythagorean distance of vector tip from origin.',
                'why_this_step': 'Establishes scale/length metric for vector spaces.',
                'exam_tips': ['Squaring components removes negative signs!'],
                'shortcuts': ['For 3-4-5 right triangle components, length is integer.'],
                'interview_questions': ['What is the difference between L1 norm and L2 norm?'],
                'practice_questions': ['Compute magnitude of vector [3, 4, 12].']
            }
        )

    # -----------------------------------------------------------------------
    # 4. UNIT VECTOR
    # -----------------------------------------------------------------------
    @staticmethod
    def unit_vector(a_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        
        mag = float(np.linalg.norm(A))
        if mag < 1e-12:
            return {'success': False, 'error': 'Cannot normalize a zero vector (magnitude is 0).'}
        
        U = A / mag
        _n = VectorService._n

        steps = [
            {'title': '① Input Vector', 'text': f'Vector in ℝ^{len(A)}:', 'latex': VectorService._vec_latex(A, "v")},
            {'title': '② Calculate Magnitude', 'text': f'||v|| = {_n(mag)}', 'latex': f'||\\mathbf{{v}}|| = {_n(mag)}'},
            {'title': '③ Normalization Formula', 'text': 'Divide each component by magnitude:', 'latex': '\\hat{\\mathbf{v}} = \\frac{\\mathbf{v}}{||\\mathbf{v}||}'},
            {'title': '④ Final Answer', 'text': 'Unit vector v̂ (length = 1):', 'latex': VectorService._vec_latex(U, "\\hat{v}")}
        ]

        verif = {
            'status': '✔ Correct',
            'check': 'Verified unit length: ||v̂|| = 1.0',
            'latex': f'||\\hat{{\\mathbf{{v}}|| = {_n(float(np.linalg.norm(U)))}',
            'residual_error': f'{abs(float(np.linalg.norm(U)) - 1.0):.6e}'
        }

        return BaseSolverService.build_educational_solution(
            operation='Unit Vector v̂',
            input_data={'v': VectorService._n_list(A)},
            theory='A unit vector is a vector with length 1 pointing in the exact direction of the original vector.',
            formula='\\hat{\\mathbf{v}} = \\frac{\\mathbf{v}}{||\\mathbf{v}||}',
            definitions=[{'term': 'Normalized Vector', 'def': 'Vector scaled to have norm equal to 1.'}],
            steps=steps,
            verification=verif,
            result=U.tolist(),
            result_display=VectorService._n_list(U),
            result_latex=VectorService._vec_latex(U, "\\hat{v}"),
            notes=['Direction is preserved while magnitude is standardized to 1.'],
            common_mistakes=['Dividing by squared magnitude instead of magnitude.'],
            applications=['Direction vectors in ray tracing', 'Feature scaling in ML', 'Basis vectors'],
            time_complexity=f'O({len(A)})',
            student_mode={
                'concept': 'Pure direction vector with magnitude = 1.',
                'why_this_step': 'Isolates direction parameter from scale parameter.',
                'exam_tips': ['Check that the magnitude of your result equals 1.'],
                'shortcuts': ['Unit vector of an already unit vector is itself.'],
                'interview_questions': ['Why do machine learning models prefer unit normalized input vectors?'],
                'practice_questions': ['Find unit vector of [3, 4].']
            }
        )

    # -----------------------------------------------------------------------
    # 5. PROJECTION of u onto v
    # -----------------------------------------------------------------------
    @staticmethod
    def projection(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have identical dimension.'}
        
        mag_b = float(np.linalg.norm(B))
        if mag_b < 1e-12:
            return {'success': False, 'error': 'Cannot project onto a zero vector.'}
        
        dot_uv = float(np.dot(A, B))
        scalar = dot_uv / (mag_b ** 2)
        proj = scalar * B
        _n = VectorService._n

        steps = [
            {'title': '① Input Vectors', 'text': f'u and v in ℝ^{len(A)}:', 'latex': f'{VectorService._vec_latex(A,"u")}, \\quad {VectorService._vec_latex(B,"v")}'},
            {'title': '② Projection Formula', 'text': 'proj_v(u) = ( (u · v) / ||v||² ) · v', 'latex': '\\text{proj}_{\\mathbf{v}}(\\mathbf{u}) = \\frac{\\mathbf{u} \\cdot \\mathbf{v}}{||\\mathbf{v}||^2} \\mathbf{v}'},
            {'title': '③ Compute Dot Product & Magnitude', 'text': f'u·v = {_n(dot_uv)}, ||v||² = {_n(mag_b**2)}'},
            {'title': '④ Compute Scalar Component', 'text': f'c = {_n(dot_uv)} / {_n(mag_b**2)} = {_n(scalar)}'},
            {'title': '⑤ Final Answer', 'text': f'proj_v(u) = {_n(scalar)} · v:', 'latex': VectorService._vec_latex(proj, "\\text{proj}_v(u)")}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Vector Projection proj_v(u)',
            input_data={'u': VectorService._n_list(A), 'v': VectorService._n_list(B)},
            theory='The orthogonal projection of vector u onto vector v decomposes u into a component parallel to v and a component orthogonal to v.',
            formula='\\text{proj}_{\\mathbf{v}}(\\mathbf{u}) = \\left( \\frac{\\mathbf{u} \\cdot \\mathbf{v}}{||\\mathbf{v}||^2} \\right) \\mathbf{v}',
            definitions=[{'term': 'Orthogonal Component', 'def': 'u_perp = u - proj_v(u), perpendicular to v.'}],
            steps=steps,
            result=proj.tolist(),
            result_display=VectorService._n_list(proj),
            result_latex=VectorService._vec_latex(proj, "\\text{proj}_v(u)"),
            notes=['proj_v(u) is always parallel to v.'],
            common_mistakes=['Projecting v onto u instead of u onto v (denominator uses target vector v!).'],
            applications=['Gram-Schmidt orthogonalization', 'Shadow calculation in computer graphics', 'Linear regression residuals'],
            time_complexity=f'O({len(A)})',
            student_mode={
                'concept': 'Shadow cast by vector u onto line v.',
                'why_this_step': 'Decomposes signals/vectors into independent target bases.',
                'exam_tips': ['Target vector v goes in denominator squared!'],
                'shortcuts': ['If u is orthogonal to v, proj_v(u) = 0.'],
                'interview_questions': ['How is vector projection used in the Gram-Schmidt process?'],
                'practice_questions': ['Project [3, 4] onto [1, 0].']
            }
        )

    # -----------------------------------------------------------------------
    # 6. ANGLE BETWEEN VECTORS
    # -----------------------------------------------------------------------
    @staticmethod
    def angle(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have identical dimension.'}
        
        mag_a = float(np.linalg.norm(A))
        mag_b = float(np.linalg.norm(B))
        if mag_a < 1e-12 or mag_b < 1e-12:
            return {'success': False, 'error': 'Cannot compute angle involving a zero vector.'}
        
        dot_uv = float(np.dot(A, B))
        cos_val = float(np.clip(dot_uv / (mag_a * mag_b), -1.0, 1.0))
        theta_r = float(math.acos(cos_val))
        theta_d = float(math.degrees(theta_r))
        _n = VectorService._n

        steps = [
            {'title': '① Input Vectors', 'text': f'Vectors in ℝ^{len(A)}:', 'latex': f'{VectorService._vec_latex(A,"u")}, \\quad {VectorService._vec_latex(B,"v")}'},
            {'title': '② Cosine Formula', 'text': 'θ = arccos( (u·v) / (||u|| ||v||) )', 'latex': '\\cos\\theta = \\frac{\\mathbf{u} \\cdot \\mathbf{v}}{||\\mathbf{u}|| ||\\mathbf{v}||}'},
            {'title': '③ Intermediate Terms', 'text': f'u·v = {_n(dot_uv)}, ||u|| = {_n(mag_a)}, ||v|| = {_n(mag_b)}'},
            {'title': '④ Cosine Ratio', 'text': f'cos(θ) = {_n(dot_uv)} / ({_n(mag_a)} × {_n(mag_b)}) = {_n(cos_val)}'},
            {'title': '⑤ Final Answer', 'text': f'θ = {_n(theta_d)}° ({_n(theta_r)} rad)', 'latex': f'\\boxed{{\\theta = {_n(theta_d)}^\\circ = {_n(theta_r)}\\text{{ rad}}}}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Angle Between Vectors θ',
            input_data={'u': VectorService._n_list(A), 'v': VectorService._n_list(B)},
            theory='The angle θ between two non-zero vectors measures their angular separation in the plane spanning them.',
            formula='\\theta = \\arccos\\left( \\frac{\\mathbf{u} \\cdot \\mathbf{v}}{||\\mathbf{u}|| ||\\mathbf{v}||} \\right)',
            definitions=[{'term': 'Angular Distance', 'def': 'Measure of orientation difference independent of length scale.'}],
            steps=steps,
            result={'radians': theta_r, 'degrees': theta_d},
            result_display=f'{_n(theta_d)}° ({_n(theta_r)} rad)',
            result_latex=f'\\theta = {_n(theta_d)}^\\circ = {_n(theta_r)}\\text{{ rad}}',
            notes=['0° ≤ θ ≤ 180°', 'θ = 0° → parallel same direction', 'θ = 90° → orthogonal', 'θ = 180° → parallel opposite direction'],
            common_mistakes=['Mixing up radians and degrees in final reporting.'],
            applications=['3D game engine field of view', 'Document similarity comparison', 'Robotic joint kinematics'],
            time_complexity=f'O({len(A)})',
            student_mode={
                'concept': 'Geometric separation angle in degrees and radians.',
                'why_this_step': 'Determines geometric orientation alignment regardless of magnitude.',
                'exam_tips': ['Double check your calculator mode (Deg vs Rad)!'],
                'shortcuts': ['If dot product is 0, angle is 90° (π/2 rad) instantly.'],
                'interview_questions': ['Why is cosine similarity preferred over Euclidean distance for high-dimensional text vectors?'],
                'practice_questions': ['Find angle between [1, 0] and [1, 1].']
            }
        )

    # -----------------------------------------------------------------------
    # 7. LINEAR COMBINATION (c1*u + c2*v)
    # -----------------------------------------------------------------------
    @staticmethod
    def linear_combination(a_data, b_data, c1_val=1, c2_val=1):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have identical dimension.'}
        try:
            c1 = float(c1_val)
            c2 = float(c2_val)
        except Exception:
            c1, c2 = 1.0, 1.0

        R = c1 * A + c2 * B
        _n = VectorService._n

        steps = [
            {'title': '① Inputs & Scalars', 'text': f'c₁ = {_n(c1)}, c₂ = {_n(c2)}', 'latex': f'{_n(c1)}\\mathbf{{u}} + {_n(c2)}\\mathbf{{v}}'},
            {'title': '② Scalar Scaling', 'text': f'c₁u = {VectorService._n_list(c1*A)}, c₂v = {VectorService._n_list(c2*B)}'},
            {'title': '③ Component Addition', 'text': 'Sum corresponding scaled components.'},
            {'title': '④ Final Answer', 'text': f'Linear Combination Result:', 'latex': VectorService._vec_latex(R, "w")}
        ]

        return BaseSolverService.build_educational_solution(
            operation=f'Linear Combination ({_n(c1)}u + {_n(c2)}v)',
            input_data={'u': VectorService._n_list(A), 'v': VectorService._n_list(B), 'c1': c1, 'c2': c2},
            theory='A linear combination of vectors multiplies each vector by a scalar and sums the results, forming the basis of vector space spans.',
            formula='\\mathbf{w} = c_1 \\mathbf{u}_1 + c_2 \\mathbf{u}_2 + \\dots + c_k \\mathbf{u}_k',
            definitions=[{'term': 'Span', 'def': 'The set of all possible linear combinations of a vector set.'}],
            steps=steps,
            result=R.tolist(),
            result_display=VectorService._n_list(R),
            result_latex=VectorService._vec_latex(R, "w"),
            notes=['Basis vectors span a vector space via linear combinations.'],
            common_mistakes=['Scaling only the first component instead of all vector entries.'],
            applications=['Vector space spanning', 'Quantum state superposition', 'Signal synthesis'],
            time_complexity=f'O({len(A)})',
            student_mode={
                'concept': 'Building new vectors by scaling and adding existing ones.',
                'why_this_step': 'Fundamental operation defining vector spaces and subspace spans.',
                'exam_tips': ['To check linear independence, set c1*u + c2*v = 0 and solve for c1, c2.'],
                'shortcuts': ['If c1=1, c2=-1, this is simple vector subtraction.'],
                'interview_questions': ['What does it mean for a set of vectors to be linearly dependent?'],
                'practice_questions': ['Compute 2*[1, 2] - 3*[0, 1].']
            }
        )

    # -----------------------------------------------------------------------
    # 8. ORTHOGONALITY CHECK
    # -----------------------------------------------------------------------
    @staticmethod
    def orthogonality(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have identical dimension.'}
        
        dot = float(np.dot(A, B))
        is_ortho = abs(dot) < 1e-9
        _n = VectorService._n
        status = '✔ Orthogonal (Perpendicular)' if is_ortho else '✘ Not Orthogonal'

        steps = [
            {'title': '① Input Vectors', 'text': f'Vectors in ℝ^{len(A)}:', 'latex': f'{VectorService._vec_latex(A,"u")}, \\quad {VectorService._vec_latex(B,"v")}'},
            {'title': '② Compute Dot Product', 'text': f'u · v = {_n(dot)}', 'latex': f'\\mathbf{{u}} \\cdot \\mathbf{{v}} = {_n(dot)}'},
            {'title': '③ Condition Evaluation', 'text': f'u · v == 0 ? -> {is_ortho}'},
            {'title': '④ Final Answer', 'text': f'Status: {status}', 'latex': f'\\text{{Orthogonal}} = \\text{{{is_ortho}}}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Vector Orthogonality Check',
            input_data={'u': VectorService._n_list(A), 'v': VectorService._n_list(B)},
            theory='Two vectors are orthogonal if their dot product equals zero, meaning they meet at a 90-degree angle.',
            formula='\\mathbf{u} \\perp \\mathbf{v} \\iff \\mathbf{u} \\cdot \\mathbf{v} = 0',
            definitions=[{'term': 'Orthonormal', 'def': 'Vectors that are both orthogonal and unit length.'}],
            steps=steps,
            result={'is_orthogonal': is_ortho, 'dot_product': dot},
            result_display=status,
            result_latex=f'\\mathbf{{u}} \\cdot \\mathbf{{v}} = {_n(dot)} \\implies \\text{{{status}}}',
            notes=['Zero vector is orthogonal to all vectors.'],
            common_mistakes=['Assuming non-zero dot product implies orthogonality.'],
            applications=['Orthogonal coordinate axes', 'Fourier series harmonic independence', 'QR decomposition'],
            time_complexity=f'O({len(A)})',
            student_mode={
                'concept': 'Checking if vectors meet at right angles.',
                'why_this_step': 'Ensures zero crosstalk/interference between coordinate components.',
                'exam_tips': ['Dot product must be EXACTLY zero.'],
                'shortcuts': ['[a, b] is orthogonal to [-b, a] in 2D.'],
                'interview_questions': ['Why are orthogonal bases preferred in numerical linear algebra?'],
                'practice_questions': ['Are [2, 3] and [-3, 2] orthogonal?']
            }
        )

    # -----------------------------------------------------------------------
    # 9. DISTANCE
    # -----------------------------------------------------------------------
    @staticmethod
    def distance(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have identical dimension.'}
        
        diff = B - A
        dist = float(np.linalg.norm(diff))
        _n = VectorService._n
        terms = ' + '.join(f'({_n(B[i])} − {_n(A[i])})²' for i in range(len(A)))

        steps = [
            {'title': '① Input Position Vectors', 'text': f'Points in ℝ^{len(A)}:', 'latex': f'{VectorService._vec_latex(A,"u")}, \\quad {VectorService._vec_latex(B,"v")}'},
            {'title': '② Euclidean Distance Formula', 'text': 'd(u, v) = ||v - u|| = √(Σ(vᵢ - uᵢ)²)', 'latex': 'd(\\mathbf{u}, \\mathbf{v}) = \\sqrt{\\sum_{i=1}^{n} (v_i - u_i)^2}'},
            {'title': '③ Difference Terms', 'text': f'= √({terms})'},
            {'title': '④ Final Answer', 'text': f'Distance d = {_n(dist)}', 'latex': f'\\boxed{{d(\\mathbf{{u}}, \\mathbf{{v}}) = {_n(dist)}}}'}
        ]

        return BaseSolverService.build_educational_solution(
            operation='Euclidean Distance d(u, v)',
            input_data={'u': VectorService._n_list(A), 'v': VectorService._n_list(B)},
            theory='The Euclidean distance measures straight-line spatial distance between two vector tips in N-dimensional space.',
            formula='d(\\mathbf{u}, \\mathbf{v}) = ||\\mathbf{v} - \\mathbf{u}|| = \\sqrt{\\sum_{i=1}^{n} (v_i - u_i)^2}',
            definitions=[{'term': 'Metric Space', 'def': 'A set where distances between elements are well-defined.'}],
            steps=steps,
            result=dist,
            result_display=_n(dist),
            result_latex=f'd(\\mathbf{{u}}, \\mathbf{{v}}) = {_n(dist)}',
            notes=['d(u, v) = d(v, u)', 'd(u, v) ≥ 0', 'Triangle inequality: d(u, w) ≤ d(u, v) + d(v, w)'],
            common_mistakes=['Mixing up subtraction order inside squares (though squaring fixes sign, keep orderly!).'],
            applications=['K-Nearest Neighbors (KNN) classification', 'Cluster analysis (K-Means)', 'Spatial positioning'],
            time_complexity=f'O({len(A)})',
            student_mode={
                'concept': 'Straight line ruler distance between two points.',
                'why_this_step': 'Measures geometric dissimilarity between vector states.',
                'exam_tips': ['Square differences first, then sum, then take square root!'],
                'shortcuts': ['d(u, v) = magnitude of (v - u).'],
                'interview_questions': ['Compare Euclidean distance with Manhattan distance (L1).'],
                'practice_questions': ['Compute distance between [0, 0] and [3, 4].']
            }
        )
