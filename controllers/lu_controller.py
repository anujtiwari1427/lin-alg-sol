from flask import Blueprint, render_template, request, jsonify
from services.lu_service import LUService
from models.calculation import CalculationModel
from utils.validators import validate_matrix

lu_bp = Blueprint('lu', __name__)


@lu_bp.route('/lu')
def lu_page():
    return render_template('modules/lu.html', active_module='lu')


@lu_bp.route('/api/lu/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.', 'error_code': 'BAD_REQUEST'}), 400

    matrix_raw = data.get('matrix')
    matrix, err = validate_matrix(matrix_raw, 'matrix')
    if err:
        return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    try:
        result = LUService.decompose(matrix)
        if result.get('success'):
            CalculationModel.save(
                module='LU', operation='PA = LU',
                input_data={'matrix': matrix},
                result_data={'L': result.get('L_display'), 'U': result.get('U_display')}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc), 'error_code': 'CALCULATION_ERROR'}), 500
