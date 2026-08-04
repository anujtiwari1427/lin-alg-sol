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
    scalar_raw = data.get('scalar', 1)
    k_power = data.get('power', 2)

    if op == 'identity':
        try:
            dim = int(data.get('dimension', 3))
        except Exception:
            dim = 3
        result = MatrixService.identity(dim)
        if result.get('success'):
            CalculationModel.save(module='Matrix', operation='Identity Matrix', input_data={'dimension': dim}, result_data=result.get('result_display'), steps=result.get('steps'))
        return jsonify(result)

    # Validate matrix A
    matrix_a, err = validate_matrix(matrix_a_raw, 'matrix_a')
    if err:
        return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    # Binary ops requiring matrix B
    dual_ops = {'add', 'subtract', 'multiply'}
    if op in dual_ops:
        matrix_b, err = validate_matrix(matrix_b_raw, 'matrix_b')
        if err:
            return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422
    else:
        matrix_b = matrix_b_raw

    # Scalar validation
    scalar = scalar_raw
    if op == 'scalar':
        scalar, err = validate_scalar(scalar_raw)
        if err:
            return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    ops = {
        'add': lambda: MatrixService.addition(matrix_a, matrix_b),
        'subtract': lambda: MatrixService.subtraction(matrix_a, matrix_b),
        'multiply': lambda: MatrixService.multiplication(matrix_a, matrix_b),
        'scalar': lambda: MatrixService.scalar_multiplication(matrix_a, scalar),
        'transpose': lambda: MatrixService.transpose(matrix_a),
        'trace': lambda: MatrixService.trace(matrix_a),
        'rank': lambda: MatrixService.rank(matrix_a),
        'determinant': lambda: MatrixService.determinant(matrix_a),
        'inverse': lambda: MatrixService.inverse(matrix_a),
        'adjoint': lambda: MatrixService.adjoint(matrix_a),
        'cofactor': lambda: MatrixService.cofactor(matrix_a),
        'power': lambda: MatrixService.power(matrix_a, k_power),
        'eigenvalues': lambda: MatrixService.eigenvalues(matrix_a),
        'eigenvectors': lambda: MatrixService.eigenvectors(matrix_a),
        'diagonalization': lambda: MatrixService.diagonalization(matrix_a),
        'lu': lambda: MatrixService.lu_decomposition(matrix_a),
        'qr': lambda: MatrixService.qr_decomposition(matrix_a),
        'svd': lambda: MatrixService.svd(matrix_a),
        'cholesky': lambda: MatrixService.cholesky(matrix_a),
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
                result_data={'result': result.get('result_display') or result.get('result')},
                steps=result.get('steps')
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': f'Calculation error: {exc}', 'error_code': 'CALCULATION_ERROR'}), 500
