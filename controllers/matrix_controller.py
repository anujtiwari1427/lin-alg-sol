from flask import Blueprint, render_template, request, jsonify
from services.matrix_service import MatrixService
from models.calculation import CalculationModel
from utils.validators import validate_matrix, validate_scalar

matrix_bp = Blueprint('matrix', __name__)


@matrix_bp.route('/matrix')
def matrix_page():
    return render_template('modules/matrix.html', active_module='matrix')


@matrix_bp.route('/api/matrix/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.', 'error_code': 'BAD_REQUEST'}), 400

    op = data.get('operation', '')
    matrix_a_raw = data.get('matrix_a')
    matrix_b_raw = data.get('matrix_b')
    scalar_raw   = data.get('scalar', 1)

    # Validate matrix A (always required)
    matrix_a, err = validate_matrix(matrix_a_raw, 'matrix_a')
    if err:
        return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    # Validate matrix B for binary ops
    dual_ops = {'add', 'subtract', 'multiply'}
    if op in dual_ops:
        matrix_b, err = validate_matrix(matrix_b_raw, 'matrix_b')
        if err:
            return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422
    else:
        matrix_b = matrix_b_raw

    # Validate scalar
    scalar = scalar_raw
    if op == 'scalar':
        scalar, err = validate_scalar(scalar_raw)
        if err:
            return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    ops = {
        'add':       lambda: MatrixService.addition(matrix_a, matrix_b),
        'subtract':  lambda: MatrixService.subtraction(matrix_a, matrix_b),
        'multiply':  lambda: MatrixService.multiplication(matrix_a, matrix_b),
        'scalar':    lambda: MatrixService.scalar_multiplication(matrix_a, scalar),
        'transpose': lambda: MatrixService.transpose(matrix_a),
        'trace':     lambda: MatrixService.trace(matrix_a),
        'rank':      lambda: MatrixService.rank(matrix_a),
    }

    if op not in ops:
        return jsonify({'success': False, 'error': f'Unknown operation: {op}', 'error_code': 'UNKNOWN_OP'}), 400

    try:
        result = ops[op]()
        if result.get('success'):
            CalculationModel.save(
                module='Matrix',
                operation=result.get('operation', op),
                input_data={'operation': op, 'matrix_a': matrix_a, 'matrix_b': matrix_b, 'scalar': scalar},
                result_data={'result': result.get('result_display') or result.get('result')}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': f'Calculation error: {exc}', 'error_code': 'CALCULATION_ERROR'}), 500
