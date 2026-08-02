from flask import Blueprint, render_template, request, jsonify
from services.inverse_service import InverseService
from models.calculation import CalculationModel
from utils.validators import validate_matrix

inverse_bp = Blueprint('inverse', __name__)


@inverse_bp.route('/inverse')
def inverse_page():
    return render_template('modules/inverse.html', active_module='inverse')


@inverse_bp.route('/api/inverse/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.', 'error_code': 'BAD_REQUEST'}), 400

    matrix_raw = data.get('matrix')
    matrix, err = validate_matrix(matrix_raw, 'matrix')
    if err:
        return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    try:
        result = InverseService.calculate(matrix)
        if result.get('success'):
            CalculationModel.save(
                module='Inverse', operation='A⁻¹',
                input_data={'matrix': matrix},
                result_data={'inverse': result.get('result_display')}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc), 'error_code': 'CALCULATION_ERROR'}), 500
