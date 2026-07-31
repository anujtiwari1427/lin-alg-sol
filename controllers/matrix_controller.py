from flask import Blueprint, render_template, request, jsonify
from services.matrix_service import MatrixService
from models.calculation import CalculationModel

matrix_bp = Blueprint('matrix', __name__)

@matrix_bp.route('/matrix')
def matrix_page():
    return render_template('modules/matrix.html', active_module='matrix')

@matrix_bp.route('/api/matrix/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.'}), 400

    op       = data.get('operation', '')
    matrix_a = data.get('matrix_a')
    matrix_b = data.get('matrix_b')
    scalar   = data.get('scalar', 1)

    ops = {
        'add':      lambda: MatrixService.addition(matrix_a, matrix_b),
        'subtract': lambda: MatrixService.subtraction(matrix_a, matrix_b),
        'multiply': lambda: MatrixService.multiplication(matrix_a, matrix_b),
        'scalar':   lambda: MatrixService.scalar_multiplication(matrix_a, scalar),
        'transpose':lambda: MatrixService.transpose(matrix_a),
        'trace':    lambda: MatrixService.trace(matrix_a),
        'rank':     lambda: MatrixService.rank(matrix_a),
    }

    if op not in ops:
        return jsonify({'success': False, 'error': f'Unknown operation: {op}'}), 400

    try:
        result = ops[op]()
        if result.get('success'):
            CalculationModel.save(
                module='Matrix', operation=result.get('operation', op),
                input_data={'operation': op, 'matrix_a': matrix_a, 'matrix_b': matrix_b, 'scalar': scalar},
                result_data={'result': result.get('result_display') or result.get('result')}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': f'Calculation error: {str(exc)}'}), 500
