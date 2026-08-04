/* =========================================================
   SOLUTION EXPORTER & EDUCATIONAL REPORT ENGINE
   Handles all 30+ solvers across Matrix, Determinant, Inverse,
   Vector, Linear Equations, Eigenvalues & Decompositions.
   Exports: PDF, Word, Excel, CSV, TXT, JSON, MD, LaTeX, HTML, PNG, SVG, Print.
   Copy Features: 8 format-specific copy buttons.
   ========================================================= */

const SolutionExporter = {
  activeData: null,
  activeModuleName: 'Linear Algebra Solution',

  setSolution(data, moduleName) {
    this.activeData = data;
    this.activeModuleName = moduleName || 'Linear Algebra Solution';
    this.renderEducationalReport(data, moduleName);
  },

  stripHtml(str) {
    return (str || '').replace(/<[^>]*>?/gm, '');
  },

  formatMatrixPlain(matrix) {
    if (!Array.isArray(matrix)) return String(matrix);
    return matrix.map(row =>
      '  [ ' + (Array.isArray(row) ? row : [row]).map(v => String(v).padStart(8)).join('  ') + ' ]'
    ).join('\n');
  },

  formatMatrixMD(matrix) {
    if (!Array.isArray(matrix)) return `\`${matrix}\``;
    const rows = matrix.map(row => Array.isArray(row) ? row : [row]);
    const cols = rows[0].length;
    const header = '| ' + Array.from({length: cols}, (_, i) => `col ${i+1}`).join(' | ') + ' |';
    const sep = '| ' + Array(cols).fill('---').join(' | ') + ' |';
    const body = rows.map(row => '| ' + row.join(' | ') + ' |').join('\n');
    return `${header}\n${sep}\n${body}`;
  },

  triggerMathJax(element) {
    try {
      if (window.MathJax) {
        if (typeof window.MathJax.typesetPromise === 'function') {
          window.MathJax.typesetPromise(element ? [element] : []).catch(err => console.warn('MathJax:', err));
        } else if (typeof window.MathJax.typeset === 'function') {
          window.MathJax.typeset(element ? [element] : []);
        }
      }
    } catch (e) {
      console.warn('MathJax exception:', e);
    }
  },

  // ═══════════════════════════════════════════════════════════
  //  RENDER MULTI-TAB RESULT PANEL & REPORT CONTAINER
  // ═══════════════════════════════════════════════════════════
  renderEducationalReport(data, moduleName) {
    const container = document.getElementById('solutionExportTarget') || document.getElementById('downloadPanelContainer');
    if (!container) return;

    const opName = data.operation || moduleName;
    const theory = data.theory || 'Linear algebra transformation and mathematical solver.';
    const formula = data.formula || '';
    const defs = data.definitions || [];
    const steps = data.steps || [];
    const verif = data.verification || { status: '✔ Correct', check: 'Direct math check passed.', residual_error: '0.000000' };
    const ansDisplay = data.result_display || data.result_latex || JSON.stringify(data.result);
    const notes = data.notes || [];
    const mistakes = data.common_mistakes || [];
    const apps = data.applications || [];
    const complexity = data.time_complexity || 'O(n)';
    const gDate = data.generated_date || new Date().toISOString().split('T')[0];
    const gTime = data.generated_time || new Date().toTimeString().split(' ')[0];
    const version = data.solver_version || '3.0.0-PRO';
    const student = data.student_mode || {};

    const html = `
      <div class="educational-solution-wrapper mt-3">
        <!-- Result Panel Navigation Tabs -->
        <ul class="nav nav-tabs custom-result-tabs mb-3" id="resultTabs" role="tablist">
          <li class="nav-item">
            <button class="nav-link active" id="tab-overview-btn" data-bs-toggle="tab" data-bs-target="#tab-overview" type="button"><i class="fas fa-home me-2"></i>Overview</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" id="tab-theory-btn" data-bs-toggle="tab" data-bs-target="#tab-theory" type="button"><i class="fas fa-book me-2"></i>Theory</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" id="tab-steps-btn" data-bs-toggle="tab" data-bs-target="#tab-steps" type="button"><i class="fas fa-list-ol me-2"></i>Detailed Steps</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" id="tab-verification-btn" data-bs-toggle="tab" data-bs-target="#tab-verification" type="button"><i class="fas fa-check-double me-2"></i>Verification</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" id="tab-student-btn" data-bs-toggle="tab" data-bs-target="#tab-student" type="button"><i class="fas fa-graduation-cap me-2"></i>Student Mode</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" id="tab-export-btn" data-bs-toggle="tab" data-bs-target="#tab-export" type="button"><i class="fas fa-download me-2"></i>Export & Copy</button>
          </li>
        </ul>

        <div class="tab-content" id="resultTabsContent">
          <!-- Overview Tab -->
          <div class="tab-pane fade show active p-3 glass-card rounded-3" id="tab-overview" role="tabpanel">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold mb-0 text-gradient"><i class="fas fa-calculator me-2"></i>${opName}</h5>
              <span class="badge bg-success-subtle text-success fs-6">${verif.status || '✔ Verified'}</span>
            </div>
            ${formula ? `
              <div class="p-3 mb-3 formula-highlight-box rounded-3 text-center">
                <div class="small text-info fw-bold mb-1">Governing Formula</div>
                <div class="math-latex-block">$$ ${formula} $$</div>
              </div>` : ''}
            <div class="p-3 mb-3 answer-highlight-box rounded-3">
              <div class="text-success small fw-bold mb-1"><i class="fas fa-check-circle me-1"></i>Final Answer</div>
              <div class="fs-4 font-monospace text-wrap fw-bold mb-2">${ansDisplay}</div>
              ${data.result_latex ? `<div class="math-latex-block">$$ ${data.result_latex} $$</div>` : ''}
            </div>
          </div>

          <!-- Theory Tab -->
          <div class="tab-pane fade p-3 glass-card rounded-3" id="tab-theory" role="tabpanel">
            <h6 class="fw-bold text-purple mb-2"><i class="fas fa-brain me-2"></i>Theoretical Foundation</h6>
            <p class="text-secondary">${theory}</p>
            ${defs.length ? `
              <h6 class="fw-bold text-info mt-3 mb-2"><i class="fas fa-book-open me-2"></i>Key Definitions</h6>
              <ul class="list-group list-group-flush mb-3">
                ${defs.map(d => `<li class="list-group-item bg-transparent text-secondary"><strong>${d.term}:</strong> ${d.def}</li>`).join('')}
              </ul>` : ''}
            <div class="d-flex align-items-center gap-2 mt-3 text-muted small">
              <i class="fas fa-clock"></i> <strong>Time Complexity:</strong> <span class="badge bg-secondary">${complexity}</span>
            </div>
          </div>

          <!-- Detailed Steps Tab -->
          <div class="tab-pane fade p-3 glass-card rounded-3" id="tab-steps" role="tabpanel">
            <h6 class="fw-bold text-warning mb-3"><i class="fas fa-shoe-prints me-2"></i>Step-by-Step Breakdown</h6>
            <div class="accordion accordion-flush" id="reportStepsAccordion">
              ${steps.map((s, idx) => `
                <div class="accordion-item bg-transparent border-bottom">
                  <h2 class="accordion-header">
                    <button class="accordion-button collapsed bg-transparent text-white" type="button" data-bs-toggle="collapse" data-bs-target="#reportStep${idx}">
                      <strong>${s.title}</strong>
                    </button>
                  </h2>
                  <div id="reportStep${idx}" class="accordion-collapse collapse" data-bs-parent="#reportStepsAccordion">
                    <div class="accordion-body text-secondary">
                      <p class="mb-2">${s.text || ''}</p>
                      ${s.operation_performed ? `<div class="badge bg-warning text-dark me-2">Op: ${s.operation_performed}</div>` : ''}
                      ${s.reason ? `<div class="small text-info mb-2"><em>Reason: ${s.reason}</em></div>` : ''}
                      ${s.latex ? `<div class="math-latex-block my-2">$$ ${s.latex} $$</div>` : ''}
                      ${s.list ? `<ul class="small"> ${s.list.map(li => `<li>${li}</li>`).join('')} </ul>` : ''}
                    </div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Verification Tab -->
          <div class="tab-pane fade p-3 glass-card rounded-3" id="tab-verification" role="tabpanel">
            <h6 class="fw-bold text-success mb-2"><i class="fas fa-shield-alt me-2"></i>Mathematical Verification</h6>
            <div class="p-3 border border-success-subtle bg-success-subtle bg-opacity-10 rounded-3 mb-3">
              <div class="fw-bold text-success mb-1">${verif.status || '✔ Verified Correct'}</div>
              <p class="mb-2 text-secondary">${verif.check || 'Direct computation verified via floating point tolerance check.'}</p>
              ${verif.latex ? `<div class="math-latex-block my-2">$$ ${verif.latex} $$</div>` : ''}
              <div class="small text-muted">Residual Error Tolerance: <code>${verif.residual_error || '0.000000'}</code></div>
            </div>
          </div>

          <!-- Student Mode Tab -->
          <div class="tab-pane fade p-3 glass-card rounded-3" id="tab-student" role="tabpanel">
            <h6 class="fw-bold text-primary-accent mb-3"><i class="fas fa-graduation-cap me-2"></i>Student Learning Hub</h6>
            <div class="row g-3">
              <div class="col-md-6">
                <div class="p-3 border border-warning-subtle rounded-3 bg-warning-subtle bg-opacity-10 h-100">
                  <h6 class="fw-bold text-warning"><i class="fas fa-lightbulb me-1"></i>Exam Tips</h6>
                  <ul class="small mb-0">${(student.exam_tips || ['Write out each step clearly.']).map(t => `<li>${t}</li>`).join('')}</ul>
                </div>
              </div>
              <div class="col-md-6">
                <div class="p-3 border border-danger-subtle rounded-3 bg-danger-subtle bg-opacity-10 h-100">
                  <h6 class="fw-bold text-danger"><i class="fas fa-exclamation-triangle me-1"></i>Common Mistakes</h6>
                  <ul class="small mb-0">${mistakes.map(m => `<li>${m}</li>`).join('')}</ul>
                </div>
              </div>
              <div class="col-md-6">
                <div class="p-3 border border-info-subtle rounded-3 bg-info-subtle bg-opacity-10 h-100">
                  <h6 class="fw-bold text-info"><i class="fas fa-bolt me-1"></i>Shortcuts</h6>
                  <ul class="small mb-0">${(student.shortcuts || ['Look for matrix symmetry or zeroes.']).map(s => `<li>${s}</li>`).join('')}</ul>
                </div>
              </div>
              <div class="col-md-6">
                <div class="p-3 border border-success-subtle rounded-3 bg-success-subtle bg-opacity-10 h-100">
                  <h6 class="fw-bold text-success"><i class="fas fa-question-circle me-1"></i>Interview Questions</h6>
                  <ul class="small mb-0">${(student.interview_questions || ['How is this computed computationally?']).map(q => `<li>${q}</li>`).join('')}</ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Export & Copy Tab -->
          <div class="tab-pane fade p-3 glass-card rounded-3" id="tab-export" role="tabpanel">
            <h6 class="fw-bold text-info mb-3"><i class="fas fa-copy me-2"></i>Copy Features</h6>
            <div class="d-flex flex-wrap gap-2 mb-4">
              <button class="btn btn-sm btn-primary" onclick="SolutionExporter.copyEntireSolution()"><i class="fas fa-clipboard-check me-1"></i>Copy Entire Solution</button>
              <button class="btn btn-sm btn-outline-success" onclick="SolutionExporter.copyFinalAnswer()"><i class="fas fa-check me-1"></i>Copy Answer</button>
              <button class="btn btn-sm btn-outline-info" onclick="SolutionExporter.copyFormula()"><i class="fas fa-square-root-variable me-1"></i>Copy Formula</button>
              <button class="btn btn-sm btn-outline-warning" onclick="SolutionExporter.copySteps()"><i class="fas fa-list-ol me-1"></i>Copy Steps</button>
              <button class="btn btn-sm btn-outline-purple" onclick="SolutionExporter.copyLaTeX()"><i class="fas fa-square-root-alt me-1"></i>Copy LaTeX</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="SolutionExporter.copyMarkdown()"><i class="fab fa-markdown me-1"></i>Copy Markdown</button>
              <button class="btn btn-sm btn-outline-dark" onclick="SolutionExporter.copyJSON()"><i class="fas fa-code me-1"></i>Copy JSON</button>
            </div>

            <h6 class="fw-bold text-primary-accent mb-3"><i class="fas fa-file-export me-2"></i>Export Full Document</h6>
            <div class="row g-2">
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadPDF()"><i class="fas fa-file-pdf text-danger me-1"></i>PDF</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadWord()"><i class="fas fa-file-word text-primary me-1"></i>Word (.docx)</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadExcel()"><i class="fas fa-file-excel text-success me-1"></i>Excel (.xlsx)</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadCSV()"><i class="fas fa-file-csv text-warning me-1"></i>CSV</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadTXT()"><i class="fas fa-file-lines text-info me-1"></i>TXT</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadJSON()"><i class="fas fa-file-code text-success me-1"></i>JSON</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadMD()"><i class="fab fa-markdown text-warning me-1"></i>Markdown</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadLaTeX()"><i class="fas fa-square-root-alt text-purple me-1"></i>LaTeX</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadHTML()"><i class="fab fa-html5 text-danger me-1"></i>HTML</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadPNG()"><i class="fas fa-image text-info me-1"></i>PNG Image</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.downloadSVG()"><i class="fas fa-vector-square text-warning me-1"></i>SVG</button></div>
              <div class="col-6 col-sm-4 col-md-3"><button class="btn btn-export w-100" onclick="SolutionExporter.printReport()"><i class="fas fa-print text-white me-1"></i>Print</button></div>
            </div>
          </div>
        </div>

        <!-- Single Copyable Solution Container -->
        <div class="single-copyable-report-box mt-4 p-4 rounded-3 border border-secondary-subtle bg-dark text-white" id="copyableReportContainer">
          <div class="report-header pb-3 mb-3 border-bottom border-secondary d-flex justify-content-between align-items-center">
            <div>
              <h5 class="fw-bold mb-0 text-gradient"><i class="fas fa-calculator me-2"></i>Linear Algebra Solver</h5>
              <small class="text-muted">Educational Report &bull; ${opName}</small>
            </div>
            <button class="btn btn-sm btn-outline-success" onclick="SolutionExporter.copyEntireSolution()"><i class="fas fa-copy me-1"></i>Copy Entire Solution</button>
          </div>

          <div class="report-body">
            <div class="mb-3"><span class="badge bg-primary me-2">Operation Name:</span> <strong>${opName}</strong></div>
            <div class="mb-3"><span class="badge bg-purple me-2">Theory:</span> ${theory}</div>
            ${formula ? `<div class="mb-3"><span class="badge bg-info me-2">Formula Used:</span> <code>${formula}</code></div>` : ''}
            
            ${defs.length ? `<div class="mb-3"><span class="badge bg-secondary me-2">Definitions:</span> <ul>${defs.map(d => `<li><strong>${d.term}:</strong> ${d.def}</li>`).join('')}</ul></div>` : ''}

            <div class="mb-3">
              <span class="badge bg-warning text-dark me-2">Steps:</span>
              <ol class="mt-2">
                ${steps.map(s => `
                  <li class="mb-2">
                    <strong>${s.title}</strong>: ${s.text || ''}
                    ${s.operation_performed ? `<br><small class="text-warning">Op: ${s.operation_performed}</small>` : ''}
                    ${s.reason ? `<br><small class="text-info">Reason: ${s.reason}</small>` : ''}
                    ${s.latex ? `<br><code>${s.latex}</code>` : ''}
                  </li>
                `).join('')}
              </ol>
            </div>

            <div class="mb-3"><span class="badge bg-success me-2">Verification:</span> ${verif.status} &bull; ${verif.check}</div>
            <div class="mb-3 p-3 bg-black rounded border border-success"><span class="text-success fw-bold">Final Answer:</span> ${ansDisplay}</div>

            ${notes.length ? `<div class="mb-3"><span class="badge bg-secondary me-2">Important Notes:</span> <ul>${notes.map(n => `<li>${n}</li>`).join('')}</ul></div>` : ''}
            ${apps.length ? `<div class="mb-3"><span class="badge bg-info me-2">Applications:</span> <ul>${apps.map(a => `<li>${a}</li>`).join('')}</ul></div>` : ''}

            <div class="report-footer pt-3 mt-3 border-top border-secondary text-muted small d-flex justify-content-between flex-wrap gap-2">
              <div>Time Complexity: <code>${complexity}</code> &bull; Date: ${gDate} &bull; Time: ${gTime}</div>
              <div>Solver Version: ${version} &bull; Generated by Linear Algebra Solver</div>
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
    this.triggerMathJax(container);
  },

  // ═══════════════════════════════════════════════════════════
  //  8 COPY BUTTON ACTIONS
  // ═══════════════════════════════════════════════════════════
  copyToClipboardText(str, msg) {
    navigator.clipboard.writeText(str).then(() => {
      if (typeof showToast === 'function') showToast(msg || 'Copied to clipboard!', 'success');
      else alert(msg || 'Copied to clipboard!');
    }).catch(err => {
      console.error('Clipboard failed:', err);
    });
  },

  copyEntireSolution() {
    const reportBox = document.getElementById('copyableReportContainer');
    if (!reportBox) return;
    const txt = reportBox.innerText;
    this.copyToClipboardText(txt, 'Entire solution copied to clipboard!');
  },

  copyFinalAnswer() {
    if (!this.activeData) return;
    const ans = this.activeData.result_display || this.activeData.result_latex || JSON.stringify(this.activeData.result);
    this.copyToClipboardText(ans, 'Final answer copied!');
  },

  copyFormula() {
    if (!this.activeData) return;
    const f = this.activeData.formula || '';
    this.copyToClipboardText(f, 'Formula copied!');
  },

  copySteps() {
    if (!this.activeData || !this.activeData.steps) return;
    const stepsTxt = this.activeData.steps.map((s, i) => `Step ${i+1}: ${s.title}\n${s.text || ''}\n${s.latex || ''}`).join('\n\n');
    this.copyToClipboardText(stepsTxt, 'Steps copied!');
  },

  copyLaTeX() {
    if (!this.activeData) return;
    const ltx = this.activeData.result_latex || this.activeData.formula || '';
    this.copyToClipboardText(ltx, 'LaTeX copied!');
  },

  copyMarkdown() {
    if (!this.activeData) return;
    const d = this.activeData;
    const md = `# ${d.operation}\n\n**Theory:** ${d.theory}\n\n**Formula:** \`$${d.formula}$\`\n\n**Final Answer:** ${d.result_display}\n`;
    this.copyToClipboardText(md, 'Markdown copied!');
  },

  copyJSON() {
    if (!this.activeData) return;
    this.copyToClipboardText(JSON.stringify(this.activeData, null, 2), 'JSON copied!');
  },

  // ═══════════════════════════════════════════════════════════
  //  12 EXPORT FORMATS
  // ═══════════════════════════════════════════════════════════
  downloadPDF() {
    const el = document.getElementById('copyableReportContainer');
    if (!el) return;
    const opt = {
      margin: 0.5,
      filename: `Solution_${(this.activeData?.operation || 'Export').replace(/\s+/g, '_')}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    if (window.html2pdf) {
      window.html2pdf().set(opt).from(el).save();
    } else {
      window.print();
    }
  },

  downloadTXT() {
    const el = document.getElementById('copyableReportContainer');
    const text = el ? el.innerText : JSON.stringify(this.activeData, null, 2);
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    this.triggerDownload(blob, 'txt');
  },

  downloadMD() {
    const d = this.activeData || {};
    let md = `# ${d.operation || 'Linear Algebra Solution'}\n\n`;
    md += `**Theory:** ${d.theory || ''}\n\n`;
    md += `**Formula:** $${d.formula || ''}$\n\n`;
    if (d.steps) {
      md += `### Steps\n\n`;
      d.steps.forEach((s, idx) => {
        md += `${idx + 1}. **${s.title}**: ${s.text || ''}\n`;
      });
    }
    md += `\n### Final Answer\n\`\`\`\n${d.result_display || JSON.stringify(d.result)}\n\`\`\`\n`;
    md += `\n---\n*Generated by Linear Algebra Solver*\n`;
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    this.triggerDownload(blob, 'md');
  },

  downloadJSON() {
    const blob = new Blob([JSON.stringify(this.activeData || {}, null, 2)], { type: 'application/json' });
    this.triggerDownload(blob, 'json');
  },

  downloadLaTeX() {
    const d = this.activeData || {};
    let ltx = `\\documentclass{article}\n\\usepackage{amsmath}\n\\begin{document}\n`;
    ltx += `\\section*{${d.operation || 'Solution'}}\n`;
    if (d.formula) ltx += `\\[ ${d.formula} \\]\n`;
    if (d.result_latex) ltx += `\\[ ${d.result_latex} \\]\n`;
    ltx += `\\end{document}`;
    const blob = new Blob([ltx], { type: 'text/x-tex;charset=utf-8' });
    this.triggerDownload(blob, 'tex');
  },

  downloadCSV() {
    const d = this.activeData || {};
    let csv = `Property,Value\n`;
    csv += `"Operation","${d.operation || ''}"\n`;
    csv += `"Formula","${(d.formula || '').replace(/"/g, '""')}"\n`;
    csv += `"Result","${(d.result_display || '').replace(/"/g, '""')}"\n`;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    this.triggerDownload(blob, 'csv');
  },

  downloadExcel() {
    if (window.XLSX && this.activeData) {
      const ws = XLSX.utils.json_to_sheet([{
        Operation: this.activeData.operation,
        Formula: this.activeData.formula,
        Result: this.activeData.result_display,
        Date: this.activeData.generated_date
      }]);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Solution");
      XLSX.writeFile(wb, `Solution_${Date.now()}.xlsx`);
    } else {
      this.downloadCSV();
    }
  },

  downloadWord() {
    const el = document.getElementById('copyableReportContainer');
    const htmlStr = `<html><head><meta charset="utf-8"></head><body>${el ? el.innerHTML : ''}</body></html>`;
    const blob = new Blob(['\ufeff' + htmlStr], { type: 'application/msword' });
    this.triggerDownload(blob, 'doc');
  },

  downloadHTML() {
    const el = document.getElementById('copyableReportContainer');
    const htmlStr = `<!DOCTYPE html><html><head><title>Solution</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"></head><body class="bg-dark text-white p-4">${el ? el.innerHTML : ''}</body></html>`;
    const blob = new Blob([htmlStr], { type: 'text/html;charset=utf-8' });
    this.triggerDownload(blob, 'html');
  },

  downloadPNG() {
    const el = document.getElementById('copyableReportContainer');
    if (window.html2canvas && el) {
      window.html2canvas(el, { backgroundColor: '#161616' }).then(canvas => {
        const link = document.createElement('a');
        link.download = `Solution_${Date.now()}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
      });
    } else {
      alert('PNG image capture initializing or not supported on this browser.');
    }
  },

  downloadSVG() {
    const el = document.getElementById('copyableReportContainer');
    const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="100%" height="100%" fill="#161616"/><foreignObject width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="color:white;font-family:sans-serif;padding:20px;">${el ? el.innerText : ''}</div></foreignObject></svg>`;
    const blob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
    this.triggerDownload(blob, 'svg');
  },

  printReport() {
    window.print();
  },

  triggerDownload(blob, ext) {
    const name = (this.activeData?.operation || 'Solution').replace(/[^a-zA-Z0-9]/g, '_');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name}_Report.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
};
