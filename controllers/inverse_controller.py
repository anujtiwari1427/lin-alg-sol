from flask import Blueprint, render_template, request, jsonify
from services.inverse_service import InverseService
from models.calculation import CalculationModel

inverse_bp = Blueprint('inverse', __name__)

@inverse_bp.route('/inverse')
def inverse_page():
    return render_template('modules/inverse.html', active_module='inverse')

@inverse_bp.route('/api/inverse/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.'}), 400
    matrix = data.get('matrix')
    if matrix is None:
        return jsonify({'success': False, 'error': 'matrix field is required.'}), 400
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
        return jsonify({'success': False, 'error': str(exc)}), 500
