from flask import Blueprint, render_template, request, jsonify
from services.linear_equations_service import LinearEquationsService
from models.calculation import CalculationModel
from utils.validators import validate_matrix

linear_equations_bp = Blueprint('linear_equations', __name__)


@linear_equations_bp.route('/linear-equations')
def linear_equations_page():
    return render_template('modules/linear_equations.html', active_module='linear_equations')


@linear_equations_bp.route('/api/linear-equations/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.', 'error_code': 'BAD_REQUEST'}), 400

    method = data.get('method', 'gaussian')
    coeffs_raw = data.get('coefficients')
    consts_raw = data.get('constants')

    coeffs, err = validate_matrix(coeffs_raw, 'coefficients')
    if err:
        return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    if not isinstance(consts_raw, list) or len(consts_raw) == 0:
        return jsonify({'success': False, 'error': 'constants must be a non-empty list.', 'error_code': 'VALIDATION_ERROR'}), 422
    for i, v in enumerate(consts_raw):
        if not isinstance(v, (int, float)):
            return jsonify({'success': False, 'error': f'constants[{i}] must be a number.', 'error_code': 'VALIDATION_ERROR'}), 422
    consts = consts_raw

    methods = {
        'gaussian': lambda: LinearEquationsService.gaussian(coeffs, consts),
        'cramer':   lambda: LinearEquationsService.cramer(coeffs, consts),
        'matrix':   lambda: LinearEquationsService.matrix_method(coeffs, consts),
    }

    if method not in methods:
        return jsonify({'success': False, 'error': f'Unknown method: {method}', 'error_code': 'UNKNOWN_OP'}), 400

    try:
        result = methods[method]()
        if result.get('success'):
            CalculationModel.save(
                module='Linear Equations', operation=result.get('method', method),
                input_data={'method': method, 'coefficients': coeffs, 'constants': consts},
                result_data={'solution': result.get('solution')}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc), 'error_code': 'CALCULATION_ERROR'}), 500
