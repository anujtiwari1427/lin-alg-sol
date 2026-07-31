from flask import Blueprint, render_template, request, jsonify
from services.determinant_service import DeterminantService
from models.calculation import CalculationModel

determinant_bp = Blueprint('determinant', __name__)

@determinant_bp.route('/determinant')
def determinant_page():
    return render_template('modules/determinant.html', active_module='determinant')

@determinant_bp.route('/api/determinant/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.'}), 400
    matrix = data.get('matrix')
    if matrix is None:
        return jsonify({'success': False, 'error': 'matrix field is required.'}), 400
    try:
        result = DeterminantService.calculate(matrix)
        if result.get('success'):
            CalculationModel.save(
                module='Determinant', operation='det(A)',
                input_data={'matrix': matrix},
                result_data={'determinant': result.get('result_display')}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500
