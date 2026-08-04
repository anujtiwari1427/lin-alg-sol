"""
PDF Export Service using ReportLab
Generates clean, professional PDF reports for matrix, determinant,
eigen, vector, inverse, and linear equations solutions.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


class PDFService:

    @staticmethod
    def generate_pdf(solution_data, module_name, question_data=None):
        """
        Generate a binary PDF buffer containing the complete solution report.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#16a34a')
        )

        sub_style = ParagraphStyle(
            'DocSub',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#334155')
        )

        date_style = ParagraphStyle(
            'DocDate',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#94a3b8')
        )

        sec_style = ParagraphStyle(
            'DocSec',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#0891b2'),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1e293b')
        )

        step_title_style = ParagraphStyle(
            'StepTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#0f172a')
        )

        result_val_style = ParagraphStyle(
            'ResultVal',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#14532d')
        )

        story = []

        # Header
        op = solution_data.get('operation', '') if solution_data else ''
        title_text = f"{module_name} — {op}" if op else module_name

        header_table_data = [
            [
                Paragraph("<b>Linear Algebra Solver</b>", title_style),
                Paragraph("Detailed Solution Report", date_style)
            ],
            [
                Paragraph(f"<b>{title_text}</b>", sub_style),
                Paragraph("", date_style)
            ]
        ]
        header_table = Table(header_table_data, colWidths=[360, 180])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#16a34a'), spaceAfter=12, spaceBefore=6))

        # 1. Question / Input Data Section
        if question_data:
            story.append(Paragraph("1. Question / Input Data", sec_style))
            q_elements = []
            if question_data.get('matrix_a'):
                q_elements.append("<b>Matrix A:</b> " + str(question_data['matrix_a']))
            if question_data.get('matrix_b'):
                q_elements.append("<b>Matrix B:</b> " + str(question_data['matrix_b']))
            if question_data.get('matrix'):
                q_elements.append("<b>Input Matrix:</b> " + str(question_data['matrix']))
            if question_data.get('coefficients'):
                q_elements.append("<b>Coefficients [A]:</b> " + str(question_data['coefficients']))
                if question_data.get('constants'):
                    q_elements.append("<b>Constants [b]:</b> " + str(question_data['constants']))

            q_text = "<br/>".join(q_elements) if q_elements else "Input data provided."
            story.append(Paragraph(q_text, body_style))
            story.append(Spacer(1, 8))

        # 2. Governing Formula
        story.append(Paragraph("2. Governing Formula & Method", sec_style))
        story.append(Paragraph(f"Method / Formula: <i>{title_text}</i>", body_style))
        story.append(Spacer(1, 8))

        # 3. Step-by-Step Computation
        story.append(Paragraph("3. Step-by-Step Computation", sec_style))
        steps = solution_data.get('steps', []) if solution_data else []
        if steps:
            for idx, step in enumerate(steps, 1):
                st_title = step.get('title', '')
                st_text  = step.get('text', '')
                st_latex = step.get('latex', '')
                st_list  = step.get('list', [])

                step_block = f"<b>Step {idx}: {st_title}</b>"
                if st_text:
                    step_block += f"<br/>{st_text}"
                if st_list:
                    step_block += "<br/>• " + "<br/>• ".join(st_list)
                if st_latex:
                    step_block += f"<br/><code>{st_latex}</code>"

                story.append(Paragraph(step_block, body_style))
                story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("No detailed steps recorded.", body_style))

        # 4. Final Calculated Result
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=8, spaceBefore=8))
        story.append(Paragraph("4. Final Calculated Result", sec_style))

        sol_val = solution_data.get('result_display') or solution_data.get('result') or solution_data.get('solution') or solution_data.get('solutions') if solution_data else None
        res_str = str(sol_val) if sol_val is not None else "Result computed."

        res_table = Table([[Paragraph(f"<b>Result:</b> {res_str}", result_val_style)]], colWidths=[540])
        res_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#86efac')),
            ('PADDING', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(res_table)

        # Footer space
        story.append(Spacer(1, 20))
        story.append(Paragraph("<font color='#94a3b8' size=8>Linear Algebra Solver — Detailed Report</font>", ParagraphStyle('Ftr', parent=body_style, alignment=TA_CENTER)))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
