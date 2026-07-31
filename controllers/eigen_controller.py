from flask import Blueprint, render_template, request, jsonify
from services.eigen_service import EigenService
from models.calculation import CalculationModel

eigen_bp = Blueprint('eigen', __name__)

@eigen_bp.route('/eigen')
def eigen_page():
    return render_template('modules/eigen.html', active_module='eigen')

@eigen_bp.route('/api/eigen/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON body.'}), 400
    matrix = data.get('matrix')
    if matrix is None:
        return jsonify({'success': False, 'error': 'matrix field is required.'}), 400
    try:
        result = EigenService.calculate(matrix)
        if result.get('success'):
            CalculationModel.save(
                module='Eigen', operation='Eigenvalues & Eigenvectors',
                input_data={'matrix': matrix},
                result_data={'eigenvalues': result.get('eigenvalues')}
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500
