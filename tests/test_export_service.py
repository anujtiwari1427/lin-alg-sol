"""
Unit Tests for Modular Export Engine (9 Exporters)
Run with: python -m unittest discover tests
"""

import io
import json
import os
import sys
import tempfile
import unittest
import openpyxl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import Config
from services.export_service import (
    ExportService, PDFExporter, WordExporter, ExcelExporter, CSVExporter,
    JSONExporter, MarkdownExporter, LatexExporter, HTMLExporter, TextExporter
)


class TestExportEngine(unittest.TestCase):

    def setUp(self):
        self.sample_solution = {
            'success': True,
            'operation': 'Matrix Inverse A⁻¹',
            'result': [[-2.0, 1.0], [1.5, -0.5]],
            'result_display': [[-2.0, 1.0], [1.5, -0.5]],
            'result_latex': r'\begin{bmatrix} -2 & 1 \\ 1.5 & -0.5 \end{bmatrix}',
            'steps': [
                {'title': 'Compute Determinant', 'text': 'det(A) = -2', 'latex': r'\det(A) = -2', 'list': []},
                {'title': 'Compute Adjoint Matrix', 'text': 'adj(A) calculated', 'latex': r'\text{adj}(A)', 'list': []}
            ]
        }
        self.sample_question = {
            'matrix': [[1, 2], [3, 4]],
            'operation': 'Matrix Inverse A⁻¹'
        }
        self.module_name = 'Inverse Calculator'

    def test_pdf_exporter(self):
        pdf_bytes = PDFExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_word_exporter(self):
        docx_bytes = WordExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(docx_bytes, bytes)
        self.assertTrue(docx_bytes.startswith(b'PK'))

    def test_excel_exporter(self):
        xlsx_bytes = ExcelExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(xlsx_bytes, bytes)
        self.assertTrue(xlsx_bytes.startswith(b'PK'))

        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
        sheet_names = wb.sheetnames
        self.assertIn("Summary", sheet_names)
        self.assertIn("Input Matrix", sheet_names)
        self.assertIn("Step-by-Step Solution", sheet_names)
        self.assertIn("Final Answer", sheet_names)
        self.assertIn("Verification", sheet_names)

    def test_csv_exporter(self):
        csv_str = CSVExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(csv_str, str)
        self.assertIn("Linear Algebra Solver", csv_str)
        self.assertIn("Matrix Inverse", csv_str)

    def test_json_exporter(self):
        json_str = JSONExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(json_str, str)
        payload = json.loads(json_str)
        self.assertEqual(payload['application'], 'Linear Algebra Solver')
        self.assertIn('theory', payload)
        self.assertIn('formula', payload)
        self.assertIn('verification', payload)

    def test_markdown_exporter(self):
        md_str = MarkdownExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(md_str, str)
        self.assertIn("# Linear Algebra Solver", md_str)
        self.assertIn("## 1. Input Data", md_str)
        self.assertIn("## 2. Mathematical Theory", md_str)

    def test_latex_exporter(self):
        tex_str = LatexExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(tex_str, str)
        self.assertIn(r"\documentclass", tex_str)
        self.assertIn(r"\begin{document}", tex_str)

    def test_html_exporter(self):
        html_str = HTMLExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(html_str, str)
        self.assertIn("<!DOCTYPE html>", html_str)
        self.assertIn("mathjax", html_str.lower())

    def test_text_exporter(self):
        txt_str = TextExporter.export(self.sample_solution, self.module_name, self.sample_question)
        self.assertIsInstance(txt_str, str)
        self.assertIn("Linear Algebra Solver", txt_str)
        self.assertIn("[1] INPUT DATA", txt_str)


class TestExportAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_fd, cls.db_path = tempfile.mkstemp(suffix='.db')
        class ApiConfig(Config):
            TESTING = True
            DEBUG = False
            DATABASE_PATH = cls.db_path

        cls.app = create_app(ApiConfig)
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        os.close(cls.db_fd)
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_all_export_formats_via_api(self):
        formats = ['pdf', 'docx', 'xlsx', 'csv', 'json', 'md', 'tex', 'html', 'txt']
        payload = {
            'solution_data': {
                'success': True,
                'operation': 'Determinant det(A)',
                'result': 10.0,
                'result_display': 10.0,
                'result_latex': r'\det(A) = 10',
                'steps': [{'title': 'Cofactor expansion', 'text': 'det = 10'}]
            },
            'module_name': 'Determinant Calculator',
            'question_data': {'matrix': [[4, 2], [1, 3]]}
        }

        for fmt in formats:
            r = self.client.post(f'/api/export/{fmt}', json=payload)
            self.assertEqual(r.status_code, 200, f"Export endpoint for {fmt} failed with status {r.status_code}")
            self.assertTrue(len(r.data) > 0, f"Export for {fmt} returned empty data")


if __name__ == '__main__':
    unittest.main()
