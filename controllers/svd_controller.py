from flask import Blueprint, render_template, request, jsonify
from services.svd_service import SVDService
from models.calculation import CalculationModel
from utils.validators import validate_matrix

svd_bp = Blueprint('svd', __name__)


@svd_bp.route('/svd')
def svd_page():
    return render_template('modules/svd.html', active_module='svd')


@svd_bp.route('/api/svd/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.', 'error_code': 'BAD_REQUEST'}), 400

    matrix_raw = data.get('matrix')
    matrix, err = validate_matrix(matrix_raw, 'matrix')
    if err:
        return jsonify({'success': False, 'error': err, 'error_code': 'VALIDATION_ERROR'}), 422

    try:
        result = SVDService.decompose(matrix)
        if result.get('success'):
            CalculationModel.save(
                module='SVD', operation='A = UΣVᵀ',
                input_data={'matrix': matrix},
                result_data={
                    'rank': result.get('rank'),
                    'singular_values': result.get('singular_values')
                }
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc), 'error_code': 'CALCULATION_ERROR'}), 500
