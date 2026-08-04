from flask import Blueprint, render_template, request, jsonify
from models.calculation import CalculationModel
from services.solver_service import BaseSolverService

main_bp = Blueprint('main', __name__)


def _dashboard_ctx():
    """Safe default context for the dashboard template."""
    try:
        recent = CalculationModel.get_recent(limit=5)
        stats  = CalculationModel.get_stats()
    except Exception:
        recent = []
        stats  = {'total_calculations': 0, 'by_module': []}
    return {'recent_history': recent, 'stats': stats, 'notice': None,
            'active_module': None, 'history': []}


@main_bp.route('/')
def landing():
    return render_template('landing.html')


@main_bp.route('/dashboard')
def dashboard():
    ctx = _dashboard_ctx()
    ctx['active_module'] = 'dashboard'
    return render_template('dashboard.html', **ctx)


@main_bp.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    results = BaseSolverService.search(q)
    return jsonify({'query': q, 'results': results, 'count': len(results)})


@main_bp.route('/history')
def history_page():
    try:
        history = CalculationModel.get_recent(limit=50)
        stats   = CalculationModel.get_stats()
    except Exception:
        history = []
        stats   = {'total_calculations': 0, 'by_module': []}
    return render_template(
        'dashboard.html',
        active_module='history', history=history,
        recent_history=history[:5], stats=stats, notice=None,
    )


@main_bp.route('/learning')
def learning_module():
    ctx = _dashboard_ctx()
    ctx.update({'active_module': 'learning',
                'notice': 'Learning Center coming in Phase 8! (Theory, Quizzes, Flashcards, Progress Tracker)'})
    return render_template('dashboard.html', **ctx)


@main_bp.route('/api/export/<format_type>', methods=['POST'])
@main_bp.route('/api/export/pdf', methods=['POST'])
def export_solution(format_type='pdf'):
    try:
        from services.export_service import ExportService
        import io
        from flask import send_file

        req = request.get_json() or {}
        solution_data = req.get('solution_data', {})
        module_name   = req.get('module_name', 'Linear Algebra Solution')
        question_data = req.get('question_data', {})

        content, mimetype, filename = ExportService.export(
            format_type, solution_data, module_name, question_data
        )

        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content

        return send_file(
            io.BytesIO(content_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


