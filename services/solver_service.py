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
