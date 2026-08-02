from flask import Blueprint, render_template, request, jsonify
from services.vector_service import VectorService
from models.calculation import CalculationModel

vector_bp = Blueprint('vector', __name__)


def _validate_vector(data, name):
    """Validate a raw vector (flat list of numbers, max 10 elements)."""
    if not isinstance(data, list) or len(data) == 0:
        return None, f'{name} must be a non-empty list of numbers.'
    if len(data) > 10:
        return None, f'{name} has {len(data)} elements; max allowed is 10.'
    for i, v in enumerate(data):
        if not isinstance(v, (int, float)):
            return None, f'{name}[{i}] must be a number, got {type(v).__name__!r}.'
    return data, None


@vector_bp.route('/vector')
def vector_page():
    return render_template('modules/vector.html', active_module='vector')


@vector_bp.route('/api/vector/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.', 'error_code': 'BAD_REQUEST'}), 400

    op = data.get('operation', '')
    va_raw = data.get('vector_a')
    vb_raw = data.get('vector_b')

    va, err = _validate_vector(va_raw, 'vector_a')
    if err:
        return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    dual_ops = {'dot', 'cross', 'projection', 'angle', 'distance'}
    vb = vb_raw
    if op in dual_ops:
        vb, err = _validate_vector(vb_raw, 'vector_b')
        if err:
            return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    ops = {
        'dot':        lambda: VectorService.dot_product(va, vb),
        'cross':      lambda: VectorService.cross_product(va, vb),
        'magnitude':  lambda: VectorService.magnitude(va),
        'unit':       lambda: VectorService.unit_vector(va),
        'projection': lambda: VectorService.projection(va, vb),
        'angle':      lambda: VectorService.angle(va, vb),
        'distance':   lambda: VectorService.distance(va, vb),
    }

    if op not in ops:
        return jsonify({'success': False, 'error': f'Unknown operation: {op}', 'error_code': 'UNKNOWN_OP'}), 400

    try:
        result = ops[op]()
        if result.get('success'):
            CalculationModel.save(
                module='Vector', operation=result.get('operation', op),
                input_data={'operation': op, 'vector_a': va, 'vector_b': vb},
                result_data={'result': str(result.get('result_display'))}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc), 'error_code': 'CALCULATION_ERROR'}), 500
