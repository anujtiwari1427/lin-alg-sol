from flask import Blueprint, render_template, request, jsonify
from services.vector_service import VectorService
from models.calculation import CalculationModel

vector_bp = Blueprint('vector', __name__)

@vector_bp.route('/vector')
def vector_page():
    return render_template('modules/vector.html', active_module='vector')

@vector_bp.route('/api/vector/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.'}), 400

    op = data.get('operation', '')
    va = data.get('vector_a')
    vb = data.get('vector_b')

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
        return jsonify({'success': False, 'error': f'Unknown operation: {op}'}), 400

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
        return jsonify({'success': False, 'error': str(exc)}), 500
