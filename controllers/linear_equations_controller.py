from flask import Blueprint, render_template, request, jsonify
from services.linear_equations_service import LinearEquationsService
from models.calculation import CalculationModel

linear_equations_bp = Blueprint('linear_equations', __name__)

@linear_equations_bp.route('/linear-equations')
def linear_equations_page():
    return render_template('modules/linear_equations.html', active_module='linear_equations')

@linear_equations_bp.route('/api/linear-equations/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.'}), 400

    method = data.get('method', 'gaussian')
    coeffs = data.get('coefficients')
    consts = data.get('constants')

    if coeffs is None or consts is None:
        return jsonify({'success': False, 'error': 'coefficients and constants fields are required.'}), 400

    methods = {
        'gaussian': lambda: LinearEquationsService.gaussian(coeffs, consts),
        'cramer':   lambda: LinearEquationsService.cramer(coeffs, consts),
        'matrix':   lambda: LinearEquationsService.matrix_method(coeffs, consts),
    }

    if method not in methods:
        return jsonify({'success': False, 'error': f'Unknown method: {method}'}), 400

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
        return jsonify({'success': False, 'error': str(exc)}), 500
