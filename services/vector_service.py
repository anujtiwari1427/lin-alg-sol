"""
Vector Operations Service — Phase 5
Supports: Dot Product, Cross Product, Magnitude, Unit Vector,
          Vector Projection, Angle Between Vectors, Distance
"""

import numpy as np
import math


class VectorService:

    @staticmethod
    def parse(data):
        """Parse list → numpy 1-D array. Returns (vec, error)."""
        try:
            v = np.array(data, dtype=float).flatten()
            if v.size == 0:
                return None, 'Vector cannot be empty.'
            return v, None
        except (ValueError, TypeError) as exc:
            return None, str(exc)

    @staticmethod
    def _n(v):
        if abs(float(v) - round(float(v))) < 1e-9:
            return str(int(round(float(v))))
        return f'{float(v):.6f}'.rstrip('0').rstrip('.')

    @staticmethod
    def _vec_latex(v, name=None):
        body = ' \\\\ '.join(VectorService._n(x) for x in v)
        s = f'\\begin{{bmatrix}} {body} \\end{{bmatrix}}'
        return f'\\mathbf{{{name}}} = {s}' if name else s

    @staticmethod
    def _n_list(v):
        return [VectorService._n(x) for x in v.tolist()]

    # -----------------------------------------------------------------------
    # DOT PRODUCT
    # -----------------------------------------------------------------------
    @staticmethod
    def dot_product(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': f'Vectors must have same dimension. Got {len(A)} and {len(B)}.'}
        dot = float(np.dot(A, B))
        n   = len(A)
        terms = ' + '.join(f'({VectorService._n(A[i])}×{VectorService._n(B[i])})' for i in range(n))
        return {
            'success': True, 'operation': 'Dot Product  A · B',
            'result': dot, 'result_display': VectorService._n(dot),
            'result_latex': f'\\mathbf{{A}} \\cdot \\mathbf{{B}} = {VectorService._n(dot)}',
            'steps': [
                {'title': '① Input Vectors',
                 'latex': f'{VectorService._vec_latex(A,"A")}, \\quad {VectorService._vec_latex(B,"B")}'},
                {'title': '② Formula',
                 'text':  'A·B = Σ AᵢBᵢ for each component',
                 'latex': f'\\mathbf{{A}} \\cdot \\mathbf{{B}} = \\sum_{{i=1}}^{{{n}}} A_i B_i'},
                {'title': '③ Computation',
                 'text':  f'= {terms}',
                 'latex': f'= {terms}'},
                {'title': '④ Result',
                 'text':  f'A · B = {VectorService._n(dot)}',
                 'latex': f'\\boxed{{\\mathbf{{A}} \\cdot \\mathbf{{B}} = {VectorService._n(dot)}}}'},
            ]
        }

    # -----------------------------------------------------------------------
    # CROSS PRODUCT (3D only)
    # -----------------------------------------------------------------------
    @staticmethod
    def cross_product(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != 3 or len(B) != 3:
            return {'success': False, 'error': 'Cross product is defined only for 3-D vectors.'}
        R = np.cross(A, B)
        _n = VectorService._n
        i_comp = f'({_n(A[1])}×{_n(B[2])}) - ({_n(A[2])}×{_n(B[1])}) = {_n(R[0])}'
        j_comp = f'({_n(A[2])}×{_n(B[0])}) - ({_n(A[0])}×{_n(B[2])}) = {_n(R[1])}'
        k_comp = f'({_n(A[0])}×{_n(B[1])}) - ({_n(A[1])}×{_n(B[0])}) = {_n(R[2])}'
        return {
            'success': True, 'operation': 'Cross Product  A × B',
            'result': R.tolist(), 'result_display': VectorService._n_list(R),
            'result_latex': VectorService._vec_latex(R),
            'steps': [
                {'title': '① Input Vectors',
                 'latex': f'{VectorService._vec_latex(A,"A")}, \\quad {VectorService._vec_latex(B,"B")}'},
                {'title': '② Formula  (determinant of 3×3)',
                 'text':  'A×B = |i  j  k ; A₁ A₂ A₃ ; B₁ B₂ B₃|',
                 'latex': '\\mathbf{A} \\times \\mathbf{B} = \\begin{vmatrix} \\mathbf{i} & \\mathbf{j} & \\mathbf{k} \\\\ A_1 & A_2 & A_3 \\\\ B_1 & B_2 & B_3 \\end{vmatrix}'},
                {'title': '③ i-component',  'text': i_comp,
                 'latex': f'i: {i_comp}'},
                {'title': '④ j-component',  'text': j_comp,
                 'latex': f'j: -{j_comp}'},
                {'title': '⑤ k-component',  'text': k_comp,
                 'latex': f'k: {k_comp}'},
                {'title': '⑥ Result',
                 'latex': f'\\mathbf{{A}} \\times \\mathbf{{B}} = {VectorService._vec_latex(R)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # MAGNITUDE
    # -----------------------------------------------------------------------
    @staticmethod
    def magnitude(a_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        mag  = float(np.linalg.norm(A))
        _n   = VectorService._n
        sq_terms = ' + '.join(f'({_n(x)})^2' for x in A)
        return {
            'success': True, 'operation': 'Magnitude  |A|',
            'result': mag, 'result_display': _n(mag),
            'result_latex': f'|\\mathbf{{A}}| = {_n(mag)}',
            'steps': [
                {'title': '① Input Vector',
                 'latex': VectorService._vec_latex(A, 'A')},
                {'title': '② Formula',
                 'text':  '|A| = √(A₁² + A₂² + ...)',
                 'latex': f'|\\mathbf{{A}}| = \\sqrt{{\\sum_i A_i^2}}'},
                {'title': '③ Substitution',
                 'text':  f'= √({sq_terms})',
                 'latex': f'= \\sqrt{{{sq_terms}}}'},
                {'title': '④ Result',
                 'text':  f'|A| = {_n(mag)}',
                 'latex': f'\\boxed{{|\\mathbf{{A}}| = {_n(mag)}}}'},
            ]
        }

    # -----------------------------------------------------------------------
    # UNIT VECTOR
    # -----------------------------------------------------------------------
    @staticmethod
    def unit_vector(a_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        mag = float(np.linalg.norm(A))
        if mag < 1e-12:
            return {'success': False, 'error': 'Cannot normalize a zero vector.'}
        U   = A / mag
        _n  = VectorService._n
        return {
            'success': True, 'operation': 'Unit Vector  Â',
            'result': U.tolist(), 'result_display': VectorService._n_list(U),
            'result_latex': VectorService._vec_latex(U),
            'steps': [
                {'title': '① Input Vector',   'latex': VectorService._vec_latex(A, 'A')},
                {'title': '② Magnitude',      'text':  f'|A| = {_n(mag)}',
                 'latex': f'|\\mathbf{{A}}| = {_n(mag)}'},
                {'title': '③ Formula',        'text':  'Â = A / |A|',
                 'latex': '\\hat{\\mathbf{A}} = \\frac{\\mathbf{A}}{|\\mathbf{A}|}'},
                {'title': '④ Result',
                 'text':  f'Divide each component by {_n(mag)}:',
                 'latex': f'\\hat{{\\mathbf{{A}}}} = {VectorService._vec_latex(U)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # PROJECTION of A onto B
    # -----------------------------------------------------------------------
    @staticmethod
    def projection(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have the same dimension.'}
        mag_b = float(np.linalg.norm(B))
        if mag_b < 1e-12:
            return {'success': False, 'error': 'Cannot project onto a zero vector.'}
        dot_ab = float(np.dot(A, B))
        scalar = dot_ab / (mag_b ** 2)
        proj   = scalar * B
        _n     = VectorService._n
        return {
            'success': True, 'operation': 'Projection of A onto B',
            'result': proj.tolist(), 'result_display': VectorService._n_list(proj),
            'result_latex': VectorService._vec_latex(proj),
            'steps': [
                {'title': '① Inputs',
                 'latex': f'{VectorService._vec_latex(A,"A")}, \\quad {VectorService._vec_latex(B,"B")}'},
                {'title': '② Formula',
                 'text':  'proj_B(A) = (A·B / |B|²) × B',
                 'latex': '\\text{proj}_{\\mathbf{B}}(\\mathbf{A}) = \\frac{\\mathbf{A} \\cdot \\mathbf{B}}{|\\mathbf{B}|^2} \\mathbf{B}'},
                {'title': '③ Dot Product  A·B',
                 'text':  f'A·B = {_n(dot_ab)}',
                 'latex': f'\\mathbf{{A}} \\cdot \\mathbf{{B}} = {_n(dot_ab)}'},
                {'title': '④ |B|²',
                 'text':  f'|B|² = {_n(mag_b**2)}',
                 'latex': f'|\\mathbf{{B}}|^2 = {_n(mag_b**2)}'},
                {'title': '⑤ Scalar Factor',
                 'text':  f'= {_n(dot_ab)} / {_n(mag_b**2)} = {_n(scalar)}',
                 'latex': f'\\frac{{{_n(dot_ab)}}}{{{_n(mag_b**2)}}} = {_n(scalar)}'},
                {'title': '⑥ Result',
                 'latex': f'\\text{{proj}} = {VectorService._vec_latex(proj)}'},
            ]
        }

    # -----------------------------------------------------------------------
    # ANGLE BETWEEN VECTORS
    # -----------------------------------------------------------------------
    @staticmethod
    def angle(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have the same dimension.'}
        mag_a = float(np.linalg.norm(A))
        mag_b = float(np.linalg.norm(B))
        if mag_a < 1e-12 or mag_b < 1e-12:
            return {'success': False, 'error': 'Cannot compute angle involving a zero vector.'}
        dot_ab  = float(np.dot(A, B))
        cos_val = float(np.clip(dot_ab / (mag_a * mag_b), -1.0, 1.0))
        theta_r = float(math.acos(cos_val))
        theta_d = float(math.degrees(theta_r))
        _n      = VectorService._n
        return {
            'success': True, 'operation': 'Angle Between A and B',
            'result': {'radians': theta_r, 'degrees': theta_d},
            'result_display': f'{_n(theta_d)}°  ({_n(theta_r)} rad)',
            'result_latex': f'\\theta = {_n(theta_d)}^\\circ = {_n(theta_r)}\\text{{ rad}}',
            'steps': [
                {'title': '① Inputs',
                 'latex': f'{VectorService._vec_latex(A,"A")}, \\quad {VectorService._vec_latex(B,"B")}'},
                {'title': '② Formula',
                 'text':  'θ = arccos(A·B / (|A||B|))',
                 'latex': '\\theta = \\arccos\\left(\\frac{\\mathbf{A} \\cdot \\mathbf{B}}{|\\mathbf{A}||\\mathbf{B}|}\\right)'},
                {'title': '③ Components',
                 'text':  f'A·B = {_n(dot_ab)}, |A| = {_n(mag_a)}, |B| = {_n(mag_b)}',
                 'latex': f'\\mathbf{{A}} \\cdot \\mathbf{{B}} = {_n(dot_ab)}, \\; |\\mathbf{{A}}| = {_n(mag_a)}, \\; |\\mathbf{{B}}| = {_n(mag_b)}'},
                {'title': '④ Cosine Value',
                 'text':  f'cos(θ) = {_n(dot_ab)} / ({_n(mag_a)} × {_n(mag_b)}) = {_n(cos_val)}',
                 'latex': f'\\cos\\theta = \\frac{{{_n(dot_ab)}}}{{{_n(mag_a)} \\times {_n(mag_b)}}} = {_n(cos_val)}'},
                {'title': '⑤ Result',
                 'text':  f'θ = {_n(theta_d)}°',
                 'latex': f'\\boxed{{\\theta = {_n(theta_d)}^\\circ = {_n(theta_r)}\\text{{ rad}}}}'},
            ]
        }

    # -----------------------------------------------------------------------
    # DISTANCE between two position vectors
    # -----------------------------------------------------------------------
    @staticmethod
    def distance(a_data, b_data):
        A, e = VectorService.parse(a_data)
        if e: return {'success': False, 'error': e}
        B, e = VectorService.parse(b_data)
        if e: return {'success': False, 'error': e}
        if len(A) != len(B):
            return {'success': False, 'error': 'Vectors must have the same dimension.'}
        diff = B - A
        dist = float(np.linalg.norm(diff))
        _n   = VectorService._n
        terms = ' + '.join(f'({_n(B[i])}-{_n(A[i])})^2' for i in range(len(A)))
        return {
            'success': True, 'operation': 'Distance Between A and B',
            'result': dist, 'result_display': _n(dist),
            'result_latex': f'd = {_n(dist)}',
            'steps': [
                {'title': '① Inputs',
                 'latex': f'{VectorService._vec_latex(A,"A")}, \\quad {VectorService._vec_latex(B,"B")}'},
                {'title': '② Formula',
                 'text':  'd = |B − A| = √(Σ(Bᵢ−Aᵢ)²)',
                 'latex': 'd = |\\mathbf{B} - \\mathbf{A}| = \\sqrt{\\sum_i (B_i - A_i)^2}'},
                {'title': '③ Substitution',
                 'text':  f'= √({terms})',
                 'latex': f'= \\sqrt{{{terms}}}'},
                {'title': '④ Result',
                 'text':  f'd = {_n(dist)}',
                 'latex': f'\\boxed{{d = {_n(dist)}}}'},
            ]
        }
