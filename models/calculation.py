import json
import numpy as np
from database.db import get_db_connection
from config import Config


class NpEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle NumPy scalar types and arrays."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class CalculationModel:
    """Data Access Object for calculation history records."""

    _db_path = None

    @classmethod
    def _get_path(cls):
        return cls._db_path or Config.DATABASE_PATH

    @classmethod
    def save(cls, module, operation, input_data, result_data, steps=None):
        conn = get_db_connection(cls._get_path())
        try:
            input_str = json.dumps(input_data, cls=NpEncoder) if isinstance(input_data, (dict, list)) else str(input_data)
            result_str = json.dumps(result_data, cls=NpEncoder) if isinstance(result_data, (dict, list)) else str(result_data)
            steps_str = json.dumps(steps, cls=NpEncoder) if steps else None

            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO calculation_history
                    (module, operation, input_data, result_data, steps_json)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (module, operation, input_str, result_str, steps_str)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def get_recent(cls, limit=10):
        conn = get_db_connection(cls._get_path())
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM calculation_history ORDER BY created_at DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        results = []
        for row in rows:
            item = dict(row)
            for field in ('input_data', 'result_data'):
                try:
                    item[field] = json.loads(item[field])
                except (json.JSONDecodeError, TypeError):
                    pass
            if item.get('steps_json'):
                try:
                    item['steps_json'] = json.loads(item['steps_json'])
                except (json.JSONDecodeError, TypeError):
                    pass
            results.append(item)
        return results

    @classmethod
    def get_stats(cls):
        conn = get_db_connection(cls._get_path())
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) AS total FROM calculation_history')
            total = cursor.fetchone()['total']

            cursor.execute('''
                SELECT module, COUNT(*) AS count
                FROM calculation_history
                GROUP BY module
                ORDER BY count DESC
            ''')
            by_module = [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

        return {
            'total_calculations': total,
            'by_module': by_module
        }

    @classmethod
    def get_weekly_counts(cls):
        """
        Return a 7-element list [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
        counting calculations in the past 7 days.
        SQLite's %w: 0=Sunday … 6=Saturday.
        """
        conn = get_db_connection(cls._get_path())
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%w', created_at) AS dow, COUNT(*) AS cnt
                FROM calculation_history
                WHERE created_at >= date('now', '-6 days')
                GROUP BY dow
            """)
            rows = {r['dow']: r['cnt'] for r in cursor.fetchall()}
        finally:
            conn.close()
        # Remap SQLite %w (0=Sun) → Mon-indexed list
        return [rows.get(str((i + 1) % 7), 0) for i in range(7)]

    @classmethod
    def delete_all(cls):
        conn = get_db_connection(cls._get_path())
        try:
            conn.execute('DELETE FROM calculation_history')
            conn.commit()
        finally:
            conn.close()
