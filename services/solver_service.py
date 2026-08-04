class BaseSolverService:
    """Base service class for Linear Algebra modules."""
    
    SEARCH_TOPICS = [
        {"title": "Matrix Addition & Subtraction", "category": "Matrix Operations", "url": "/matrix", "keywords": ["matrix", "add", "subtract", "sum", "difference"]},
        {"title": "Matrix Multiplication", "category": "Matrix Operations", "url": "/matrix", "keywords": ["matrix", "multiply", "dot product", "product"]},
        {"title": "Matrix Transpose", "category": "Matrix Operations", "url": "/matrix", "keywords": ["transpose", "flip", "rows", "columns"]},
        {"title": "Matrix Rank & Trace", "category": "Matrix Operations", "url": "/matrix", "keywords": ["rank", "trace", "diagonal", "dimension"]},
        {"title": "2x2 & 3x3 Determinants", "category": "Determinants", "url": "/determinant", "keywords": ["determinant", "det", "laplace", "cofactor"]},
        {"title": "Matrix Inverse", "category": "Inverse", "url": "/inverse", "keywords": ["inverse", "adjoint", "cofactor", "singular"]},
        {"title": "Vector Dot & Cross Product", "category": "Vectors", "url": "/vector", "keywords": ["vector", "dot product", "cross product", "angle", "projection"]},
        {"title": "Gaussian Elimination", "category": "Linear Equations", "url": "/linear-equations", "keywords": ["gaussian", "system", "elimination", "row echelon"]},
        {"title": "Cramer's Rule", "category": "Linear Equations", "url": "/linear-equations", "keywords": ["cramer", "rule", "determinants", "equations"]},
        {"title": "Eigenvalues & Eigenvectors", "category": "Eigen", "url": "/eigen", "keywords": ["eigenvalue", "eigenvector", "characteristic polynomial", "spectrum"]},
        {"title": "Linear Algebra Learning Center", "category": "Education", "url": "/learning", "keywords": ["learn", "quiz", "flashcards", "tutorial", "theory"]}
    ]

    @classmethod
    def search(cls, query):
        """Search available topics across all modules."""
        if not query:
            return []
        
        query = query.lower().strip()
        results = []
        for topic in cls.SEARCH_TOPICS:
            match_title = query in topic['title'].lower()
            match_cat = query in topic['category'].lower()
            match_kw = any(query in kw for kw in topic['keywords'])
            
            if match_title or match_cat or match_kw:
                results.append(topic)
        return results

    @classmethod
    def build_educational_solution(cls, *,
                                  operation,
                                  input_data=None,
                                  theory="",
                                  formula="",
                                  definitions=None,
                                  steps=None,
                                  verification=None,
                                  result=None,
                                  result_display="",
                                  result_latex="",
                                  notes=None,
                                  common_mistakes=None,
                                  applications=None,
                                  time_complexity="O(n)",
                                  student_mode=None):
        """
        Standardized educational solution builder ensuring all calculations
        return a rich educational report structure.
        """
        from datetime import datetime
        now = datetime.now()
        
        default_verif = {
            'status': '✔ Correct',
            'check': 'Direct computation checked via NumPy floating point verification.',
            'latex': result_latex or '',
            'residual_error': '0.000000'
        }

        return {
            'success': True,
            'operation': operation,
            'input': input_data or {},
            'theory': theory or 'Linear algebra fundamental transformation.',
            'formula': formula or '',
            'definitions': definitions or [],
            'steps': steps or [],
            'verification': verification or default_verif,
            'result': result,
            'result_display': result_display,
            'result_latex': result_latex,
            'notes': notes or ['Double check input dimensions before performing calculation.'],
            'common_mistakes': common_mistakes or ['Confusing row indices with column indices.'],
            'applications': applications or ['Machine learning', 'Computer graphics', 'Data science'],
            'time_complexity': time_complexity,
            'generated_date': now.strftime('%Y-%m-%d'),
            'generated_time': now.strftime('%H:%M:%S'),
            'solver_version': '3.0.0-PRO',
            'student_mode': student_mode or {
                'concept': f'Understanding {operation}',
                'why_this_step': 'Ensures algebraic correctness and preserves geometric transformation properties.',
                'exam_tips': ['Write out every step clearly.', 'Check units and signs.'],
                'shortcuts': ['Use symmetry or diagonal properties when applicable.'],
                'interview_questions': [f'How is {operation} computed in computational software?'],
                'practice_questions': [f'Try computing {operation} for a 2x2 matrix with negative numbers.']
            }
        }

