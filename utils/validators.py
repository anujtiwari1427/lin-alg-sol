"""
Input validation utilities for the Linear Algebra Solver API.
All solver endpoints call these functions before passing data to services.
"""

MAX_DIM = 10      # max rows or cols per matrix
MAX_CELLS = 64    # total element cap


def validate_matrix(data, name: str = 'matrix'):
    """
    Validate a raw JSON matrix (nested list).

    Returns:
        (data, None)   on success
        (None, error_str)  on failure
    """
    if not isinstance(data, list) or len(data) == 0:
        return None, f'{name} must be a non-empty 2-D list.'

    if not all(isinstance(row, list) for row in data):
        return None, f'{name}: every row must be a list.'

    rows = len(data)
    cols = len(data[0])

    if rows > MAX_DIM or cols > MAX_DIM:
        return None, (
            f'{name} dimensions ({rows}×{cols}) exceed the maximum '
            f'allowed ({MAX_DIM}×{MAX_DIM}).'
        )

    if rows * cols > MAX_CELLS:
        return None, f'{name} has too many elements (max {MAX_CELLS}).'

    for i, row in enumerate(data):
        if len(row) != cols:
            return None, f'{name}: row {i} has {len(row)} elements, expected {cols}.'
        for j, val in enumerate(row):
            if not isinstance(val, (int, float)):
                return None, (
                    f'{name}[{i}][{j}] must be a number, '
                    f'got {type(val).__name__!r}.'
                )
            if val != val:  # NaN check
                return None, f'{name}[{i}][{j}] is NaN.'

    return data, None


def validate_scalar(val):
    """
    Coerce *val* to float.

    Returns:
        (float, None)     on success
        (None, error_str) on failure
    """
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None, 'Scalar must be a finite number.'
    if f != f:  # NaN
        return None, 'Scalar must be a finite number (got NaN).'
    return f, None


def api_error(msg: str, code: str = 'VALIDATION_ERROR', http: int = 422):
    """Return a (jsonify-ready dict, http_status) tuple for error responses."""
    return {'success': False, 'error': msg, 'error_code': code}, http


def api_ok(payload: dict, http: int = 200):
    """Return a (jsonify-ready dict, http_status) tuple for success responses."""
    return {'success': True, **payload}, http
