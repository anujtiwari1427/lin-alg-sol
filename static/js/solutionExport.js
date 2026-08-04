/* =========================================================
   SOLUTION EXPORTER — Comprehensive Multi-Format Export Engine
   Handles all 6 solvers: Matrix, Determinant, Inverse,
   Vector, Linear Equations, Eigenvalue/Eigenvector.
   Export Formats: PDF, TXT, Markdown, JSON, CSV, LaTeX, HTML, Word.
   Print: Includes Question + Solution with full formatting.
   ========================================================= */

const SolutionExporter = {
  activeData: null,
  activeModuleName: 'Linear Algebra Solution',
  activeQuestion: null,   // stores the input question data

  pendingAction: null,

  setSolution(data, moduleName, questionData) {
    this.activeData = data;
    this.activeModuleName = moduleName || 'Linear Algebra Solution';
    this.activeQuestion = questionData || null;
    try {
      this.renderDirectSolution(data, moduleName);
    } catch (e) {
      console.error('[SolutionExporter] renderDirectSolution error:', e);
    }

    if (this.pendingAction) {
      const act = this.pendingAction;
      this.pendingAction = null;
      setTimeout(() => {
        if (act === 'print') this.printSolution();
        else if (act === 'pdf') this.downloadPDF();
        else if (act === 'word') this.downloadWord();
      }, 350);
    }
  },

  // ─── Build HTML block for question/input section ──────
  buildQuestionHtml(forPrint = false) {
    const q = this.activeQuestion;
    if (!q) return '';

    const td = (v) => `<td style="padding:4px 10px;border:1px solid #cbd5e1;font-family:'Courier New',monospace;text-align:right;">${v}</td>`;
    const th = (v) => `<th style="padding:5px 10px;background:#f1f5f9;border:1px solid #e2e8f0;">${v}</th>`;

    const matrixTable = (mat, label) => {
      if (!Array.isArray(mat) || !mat.length) return '';
      const header = mat[0].map((_, j) => th(`c${j+1}`)).join('');
      const rows   = mat.map(row => `<tr>${row.map(v => td(v)).join('')}</tr>`).join('');
      return `
        <div style="margin-bottom:10px;">
          <div style="font-size:11px;font-weight:700;color:#475569;margin-bottom:4px;">${label}</div>
          <table style="border-collapse:collapse;"><thead><tr>${header}</tr></thead><tbody>${rows}</tbody></table>
        </div>`;
    };

    const vecRow = (vec, label) => {
      if (!Array.isArray(vec)) return '';
      const cells = vec.map(v => td(v)).join('');
      return `
        <div style="margin-bottom:8px;">
          <span style="font-size:11px;font-weight:700;color:#475569;">${label}:</span>
          <table style="border-collapse:collapse;display:inline-table;margin-left:8px;"><tbody><tr>${cells}</tr></tbody></table>
        </div>`;
    };

    let body = '';

    if (q.operation) {
      body += `<div style="margin-bottom:8px;"><b>Operation:</b> ${q.operation}</div>`;
    }
    if (q.method) {
      body += `<div style="margin-bottom:8px;"><b>Method:</b> ${q.method}</div>`;
    }
    if (q.matrix_a) body += matrixTable(q.matrix_a, 'Matrix A');
    if (q.matrix_b) body += matrixTable(q.matrix_b, 'Matrix B');
    if (q.matrix)   body += matrixTable(q.matrix,   'Input Matrix A');
    // scalar: only show when it is a finite number (guard against NaN)
    if (q.scalar !== undefined && q.scalar !== null && Number.isFinite(q.scalar)) {
      body += `<div style="margin-bottom:8px;"><b>Scalar k:</b> ${q.scalar}</div>`;
    }
    // vectors — support both key naming conventions
    const vu = q.vector_u || q.vector_a;
    const vv = q.vector_v || q.vector_b;
    if (vu) body += vecRow(vu, 'Vector u');
    if (vv) body += vecRow(vv, 'Vector v');
    if (q.coefficients) {
      // Linear system [A|b]
      const n = q.coefficients.length;
      const varNames = Array.from({length: n}, (_, i) => `x${i+1}`);
      const headerCells = [...varNames.map(v => th(v)), th('= b')].join('');
      const rowsHtml = q.coefficients.map((row, i) => {
        const cells = row.map(v => td(v)).join('');
        const rhs   = td(q.constants ? q.constants[i] : '?');
        return `<tr>${cells}${rhs}</tr>`;
      }).join('');
      body += `
        <div style="margin-bottom:10px;">
          <div style="font-size:11px;font-weight:700;color:#475569;margin-bottom:4px;">Augmented Matrix [A | b]</div>
          <table style="border-collapse:collapse;"><thead><tr>${headerCells}</tr></thead><tbody>${rowsHtml}</tbody></table>
        </div>`;
    }

    if (!body) return '';

    const borderColor = '#bae6fd';
    return `
      <div style="background:#f0f9ff;border:2px solid ${borderColor};border-radius:8px;padding:14px 18px;margin-bottom:18px;">
        <div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:#0891b2;margin-bottom:10px;">
          [INPUT] Question / Input Data
        </div>
        ${body}
      </div>`;
  },

  // ─── Formula lookup (LaTeX) ─────────────────────────────
  getFormula(moduleName, data) {
    const op  = (data.operation || '').toLowerCase();
    const mod = (moduleName   || '').toLowerCase();
    if (mod.includes('matrix')) {
      if (op.includes('add'))       return 'C = A + B \\quad \\text{where}\\; c_{ij} = a_{ij} + b_{ij}';
      if (op.includes('sub'))       return 'C = A - B \\quad \\text{where}\\; c_{ij} = a_{ij} - b_{ij}';
      if (op.includes('multi') && !op.includes('scalar')) return 'C_{ij} = \\sum_{k=1}^{n} A_{ik} \\cdot B_{kj}';
      if (op.includes('scalar'))    return 'B = k \\cdot A \\quad \\text{where}\\; b_{ij} = k \\cdot a_{ij}';
      if (op.includes('transpose')) return '(A^T)_{ij} = A_{ji}';
      if (op.includes('trace'))     return '\\text{tr}(A) = \\sum_{i=1}^{n} a_{ii}';
      if (op.includes('rank'))      return '\\text{rank}(A) = \\text{number of pivot rows in RREF}(A)';
      return 'C = f(A, B)';
    }
    if (mod.includes('determinant')) return '\\det(A) = \\sum_{j=1}^{n} (-1)^{1+j}\\, a_{1j}\\, \\det(M_{1j})';
    if (mod.includes('inverse'))     return 'A^{-1} = \\tfrac{1}{\\det(A)}\\,\\operatorname{adj}(A) \\quad\\text{or}\\quad [A\\mid I] \\xrightarrow{\\text{RREF}} [I\\mid A^{-1}]';
    if (mod.includes('vector')) {
      if (op.includes('dot'))       return '\\vec{u}\\cdot\\vec{v} = \\sum_{i} u_i v_i';
      if (op.includes('cross'))     return '\\vec{u}\\times\\vec{v} = \\begin{vmatrix}\\hat{i}&\\hat{j}&\\hat{k}\\\\u_1&u_2&u_3\\\\v_1&v_2&v_3\\end{vmatrix}';
      if (op.includes('magnitude')) return '\\|\\vec{v}\\| = \\sqrt{\\sum_{i} v_i^2}';
      if (op.includes('unit'))      return '\\hat{v} = \\dfrac{\\vec{v}}{\\|\\vec{v}\\|}';
      if (op.includes('add'))       return '\\vec{u}+\\vec{v} = (u_1+v_1,\\,u_2+v_2,\\,\\ldots)';
      if (op.includes('sub'))       return '\\vec{u}-\\vec{v} = (u_1-v_1,\\,u_2-v_2,\\,\\ldots)';
      return '\\vec{r} = f(\\vec{u},\\vec{v})';
    }
    if (mod.includes('linear')) return 'A\\mathbf{x}=\\mathbf{b}\\;\\Rightarrow\\;\\mathbf{x}=A^{-1}\\mathbf{b}\\quad\\text{(or Gaussian Elimination)}';
    if (mod.includes('eigen'))  return '\\det(A-\\lambda I)=0 \\quad\\text{and}\\quad (A-\\lambda I)\\mathbf{v}=\\mathbf{0}';
    return '';
  },

  // ─── Formula text (plain) ───────────────────────────────
  getFormulaPlain(moduleName, data) {
    const op  = (data.operation || '').toLowerCase();
    const mod = (moduleName   || '').toLowerCase();
    if (mod.includes('matrix')) {
      if (op.includes('add'))       return 'C = A + B  (element-wise addition)';
      if (op.includes('sub'))       return 'C = A - B  (element-wise subtraction)';
      if (op.includes('multi') && !op.includes('scalar')) return 'C[i,j] = Sum_k( A[i,k] * B[k,j] )  (matrix multiplication)';
      if (op.includes('scalar'))    return 'B = k * A  (scalar multiplication)';
      if (op.includes('transpose')) return 'A^T[i,j] = A[j,i]  (transpose)';
      if (op.includes('trace'))     return 'tr(A) = Sum of main diagonal elements';
      if (op.includes('rank'))      return 'rank(A) = number of pivot rows in RREF(A)';
      return 'Matrix operation';
    }
    if (mod.includes('determinant')) return 'det(A) = cofactor expansion along first row';
    if (mod.includes('inverse'))     return 'A^-1 = (1/det(A)) * adj(A)  OR  [A | I] --RREF--> [I | A^-1]';
    if (mod.includes('vector')) {
      if (op.includes('dot'))       return 'u . v = Sum( u_i * v_i )';
      if (op.includes('cross'))     return 'u x v = determinant of 3x3 matrix with i,j,k top row';
      if (op.includes('magnitude')) return '||v|| = sqrt( Sum( v_i^2 ) )';
      if (op.includes('unit'))      return 'v_hat = v / ||v||';
      if (op.includes('add'))       return 'u + v = (u1+v1, u2+v2, ...)';
      if (op.includes('sub'))       return 'u - v = (u1-v1, u2-v2, ...)';
      return 'Vector operation';
    }
    if (mod.includes('linear')) return 'Ax = b  =>  x = A^-1 * b  (or Gaussian Elimination)';
    if (mod.includes('eigen'))  return 'det(A - lambda*I) = 0  and  (A - lambda*I)*v = 0';
    return '';
  },

  // ─── Helpers ─────────────────────────────────────────────
  stripHtml(str) {
    return (str || '').replace(/<[^>]*>?/gm, '');
  },

  formatMatrix(matrix, pad = 8) {
    if (!Array.isArray(matrix)) return String(matrix);
    return matrix.map(row =>
      '  [ ' + (Array.isArray(row) ? row : [row]).map(v => String(v).padStart(pad)).join('  ') + ' ]'
    ).join('\n');
  },

  formatMatrixMD(matrix) {
    if (!Array.isArray(matrix)) return `\`${matrix}\``;
    const rows = matrix.map(row => Array.isArray(row) ? row : [row]);
    const cols  = rows[0].length;
    const header = '| ' + Array.from({length: cols}, (_, i) => `col ${i+1}`).join(' | ') + ' |';
    const sep    = '| ' + Array(cols).fill('---').join(' | ') + ' |';
    const body   = rows.map(row => '| ' + row.join(' | ') + ' |').join('\n');
    return `${header}\n${sep}\n${body}`;
  },

  // ─── Render formula box + export panel ───────────────────
  renderDirectSolution(data, moduleName) {
    const accordion     = document.getElementById('stepsAccordion');
    const downloadPanel = document.getElementById('downloadPanelContainer');
    const formula       = this.getFormula(moduleName, data);

    // Insert formula card before steps
    let formulaBox = document.getElementById('solutionFormulaBox');
    if (!formulaBox && accordion) {
      formulaBox = document.createElement('div');
      formulaBox.id = 'solutionFormulaBox';
      accordion.parentNode.insertBefore(formulaBox, accordion);
    }
    if (formulaBox && formula) {
      formulaBox.innerHTML = `
        <div class="combined-single-card p-3 mb-3">
          <div class="section-label text-info mb-2"><i class="fas fa-square-root-variable me-2"></i>Governing Formula &amp; Method</div>
          <div class="formula-box p-3 rounded-3 text-center border border-info-subtle">\\[ ${formula} \\]</div>
        </div>`;
    }

    // Export panel after steps
    if (!downloadPanel) return;
    downloadPanel.innerHTML = `
      <div class="combined-single-card p-3 p-md-4 mt-3">
        <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
          <div class="d-flex align-items-center gap-2">
            <div class="download-icon-box"><i class="fas fa-file-export"></i></div>
            <div>
              <h6 class="fw-bold mb-0 text-primary-accent">Export Solution</h6>
              <p class="small text-secondary mb-0">Download or copy full calculation steps and results in multiple formats</p>
            </div>
          </div>
          <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1 small">
            <i class="fas fa-check-circle me-1"></i>8 Export Formats Available
          </span>
        </div>

        <div class="row g-2 mb-3">
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadPDF()" title="Download PDF Report">
              <i class="fas fa-file-pdf text-danger fs-5 mb-1 d-block"></i><span>PDF Document</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadTXT()" title="Download Plain Text File">
              <i class="fas fa-file-lines text-info fs-5 mb-1 d-block"></i><span>Plain Text</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadMD()" title="Download Markdown Document">
              <i class="fab fa-markdown text-warning fs-5 mb-1 d-block"></i><span>Markdown</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadJSON()" title="Download JSON Data">
              <i class="fas fa-file-code text-success fs-5 mb-1 d-block"></i><span>JSON Data</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadCSV()" title="Download CSV Spreadsheet">
              <i class="fas fa-file-csv text-primary fs-5 mb-1 d-block"></i><span>CSV Table</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadLaTeX()" title="Download LaTeX Document (.tex)">
              <i class="fas fa-square-root-variable text-purple fs-5 mb-1 d-block" style="color:#a855f7;"></i><span>LaTeX (.tex)</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadHTML()" title="Download Offline HTML Report">
              <i class="fab fa-html5 text-orange fs-5 mb-1 d-block" style="color:#f97316;"></i><span>HTML Web</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadWord()" title="Download Word Document">
              <i class="fas fa-file-word fs-5 mb-1 d-block" style="color:#2b7cd3;"></i><span>Word (.doc)</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3 col-lg-2-4">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.printSolution()" title="Print Solution">
              <i class="fas fa-print text-info fs-5 mb-1 d-block"></i><span>Print</span>
            </button>
          </div>
        </div>

        <div class="pt-3 border-top border-secondary-subtle d-flex flex-wrap align-items-center justify-content-between gap-2">
          <span class="small text-secondary fw-semibold"><i class="fas fa-paste me-1"></i>Quick Clipboard Actions:</span>
          <div class="d-flex flex-wrap gap-2">
            <button type="button" class="btn btn-sm btn-secondary-custom" onclick="SolutionExporter.printSolution()">
              <i class="fas fa-print me-1 text-info"></i>Print Solution
            </button>
            <button type="button" class="btn btn-sm btn-secondary-custom" onclick="SolutionExporter.copyToClipboard()">
              <i class="fas fa-copy me-1"></i>Copy Text
            </button>
            <button type="button" class="btn btn-sm btn-secondary-custom" onclick="SolutionExporter.copyLaTeX()">
              <i class="fas fa-square-root-variable me-1"></i>Copy LaTeX
            </button>
            <button type="button" class="btn btn-sm btn-secondary-custom" onclick="SolutionExporter.copyMD()">
              <i class="fab fa-markdown me-1"></i>Copy Markdown
            </button>
          </div>
        </div>
      </div>`;
    if (window.MathJax && window.MathJax.typeset) window.MathJax.typeset();
  },

  // ═══════════════════════════════════════════════════════════
  //  TEXT EXPORT — plain text format
  // ═══════════════════════════════════════════════════════════
  buildFormattedText() {
    if (!this.activeData) return '';
    const d   = this.activeData;
    const mod = this.activeModuleName;
    const op  = d.operation || '';
    const title = op ? `${mod} — ${op}` : mod;
    const date  = new Date().toLocaleString();
    const W     = 62;
    const hr    = '='.repeat(W);
    const hr2   = '-'.repeat(W);
    const ctr   = s => s.padStart(Math.floor((W + s.length) / 2)).padEnd(W);

    let t = `${hr}\n`;
    t    += `${ctr('LINEAR ALGEBRA SOLVER')}\n`;
    t    += `${ctr('DETAILED SOLUTION REPORT')}\n`;
    t    += `${hr}\n`;
    t    += `  Solver  : ${mod}\n`;
    if (op) t += `  Operation: ${op}\n`;
    t    += `  Generated: ${date}\n`;
    t    += `${hr}\n\n`;

    // Section 1: Formula
    t += `  [1]  GOVERNING FORMULA & METHOD\n`;
    t += `  ${hr2}\n`;
    const formula = this.getFormulaPlain(mod, d);
    t += `  ${formula || title}\n\n`;

    // Section 2: Steps
    t += `  [2]  STEP-BY-STEP COMPUTATION\n`;
    t += `  ${hr2}\n`;
    if (d.steps && d.steps.length > 0) {
      d.steps.forEach((step, idx) => {
        t += `\n  Step ${idx + 1} of ${d.steps.length}: ${step.title}\n`;
        t += `  ${'·'.repeat(Math.min(step.title.length + 20, W - 4))}\n`;
        if (step.text) {
          const words = this.stripHtml(step.text).split(/\s+/);
          let line = '  ';
          words.forEach(w => {
            if ((line + w).length > W - 2) { t += line + '\n'; line = '  '; }
            line += w + ' ';
          });
          if (line.trim()) t += line.trimEnd() + '\n';
        }
        if (step.list && step.list.length > 0) {
          step.list.forEach(item => {
            t += `    ▸  ${this.stripHtml(item)}\n`;
          });
        }
        if (step.latex) {
          t += `\n    Formula:  ${step.latex}\n`;
        }
      });
      t += '\n';
    } else {
      t += '  (no computation steps available)\n\n';
    }

    // Section 3: Result
    t += `  [3]  FINAL RESULT\n`;
    t += `  ${hr2}\n`;

    if (d.result_display && Array.isArray(d.result_display) && Array.isArray(d.result_display[0])) {
      t += `\n  Result Matrix:\n${this.formatMatrix(d.result_display)}\n\n`;
    } else if (d.result_display) {
      t += `\n  Result: ${d.result_display}\n\n`;
    } else if (d.result !== undefined && d.result !== null) {
      t += `\n  Result: ${d.result}\n\n`;
    }

    const solObj = d.solution || d.solutions;
    if (solObj && typeof solObj === 'object') {
      t += `  Solution Variables:\n`;
      Object.entries(solObj).forEach(([k, v]) => {
        t += `    ${(k + ' ').padEnd(6)}=  ${v}\n`;
      });
      t += '\n';
    }

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      t += `  Eigenvalues & Eigenvectors:\n`;
      t += `  ${'  Pair'.padEnd(8)}  ${'Eigenvalue'.padEnd(20)}  Eigenvector\n`;
      t += `  ${'-'.repeat(50)}\n`;
      d.eigenvalues.forEach((val, i) => {
        const vec = d.eigenvectors && d.eigenvectors[i]
          ? '[' + d.eigenvectors[i].map(x => String(x).padStart(10)).join(',') + ']ᵀ'
          : '—';
        t += `  ${('λ' + (i + 1)).padEnd(8)}  ${String(val).padEnd(20)}  v${i + 1} = ${vec}\n`;
      });
      t += '\n';
    }

    if (d.result_latex) t += `  LaTeX:  ${d.result_latex}\n\n`;

    t += `${hr}\n`;
    t += `  Linear Algebra Solver  |  ${date}\n`;
    t += `${hr}\n`;
    return t;
  },

  // ═══════════════════════════════════════════════════════════
  //  MARKDOWN EXPORT — markdown format
  // ═══════════════════════════════════════════════════════════
  buildFormattedMD() {
    if (!this.activeData) return '';
    const d   = this.activeData;
    const mod = this.activeModuleName;
    const op  = d.operation || '';
    const title = op ? `${mod}: ${op}` : mod;
    const date  = new Date().toLocaleString();
    const formula = this.getFormula(mod, d);

    let md = `# 🔢 Linear Algebra Solver — Detailed Solution\n\n`;
    md    += `## ${title}\n\n`;
    md    += `> **Generated:** ${date}\n\n`;
    md    += `---\n\n`;

    md += `## 1. Governing Formula & Method\n\n`;
    if (formula) {
      md += `$$\n${formula}\n$$\n\n`;
    } else {
      md += `> ${title}\n\n`;
    }

    md += `---\n\n## 2. Complete Step-by-Step Computation\n\n`;
    if (d.steps && d.steps.length > 0) {
      d.steps.forEach((step, idx) => {
        md += `### Step ${idx + 1}: ${step.title}\n\n`;
        if (step.text) md += `${this.stripHtml(step.text)}\n\n`;
        if (step.list && step.list.length > 0) {
          step.list.forEach(item => { md += `- ${this.stripHtml(item)}\n`; });
          md += '\n';
        }
        if (step.latex) md += `$$\n${step.latex}\n$$\n\n`;
      });
    } else {
      md += `*No computation steps available.*\n\n`;
    }

    md += `---\n\n## 3. Final Calculated Result\n\n`;
    if (d.result_latex) {
      md += `$$\n${d.result_latex}\n$$\n\n`;
    }

    if (d.result_display && Array.isArray(d.result_display) && Array.isArray(d.result_display[0])) {
      md += `**Result Matrix:**\n\n${this.formatMatrixMD(d.result_display)}\n\n`;
    } else if (d.result_display !== undefined && d.result_display !== null) {
      md += `**Result:** \`${d.result_display}\`\n\n`;
    } else if (d.result !== undefined && d.result !== null) {
      md += `**Result:** \`${d.result}\`\n\n`;
    }

    const solObj = d.solution || d.solutions;
    if (solObj && typeof solObj === 'object') {
      md += `### Solution Variables\n\n`;
      md += `| Variable | Value |\n|---|---|\n`;
      Object.entries(solObj).forEach(([k, v]) => {
        md += `| **${k}** | \`${v}\` |\n`;
      });
      md += '\n';
    }

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      md += `### Eigenvalues & Eigenvectors\n\n`;
      md += `| Pair | Eigenvalue (λ) | Eigenvector (v) |\n|---|---|---|\n`;
      d.eigenvalues.forEach((val, i) => {
        const vec = d.eigenvectors && d.eigenvectors[i]
          ? `[${d.eigenvectors[i].join(', ')}]ᵀ`
          : '—';
        md += `| ${i + 1} | \`${val}\` | \`${vec}\` |\n`;
      });
      md += '\n';
    }

    md += `---\n\n*Generated by Linear Algebra Solver &nbsp;|&nbsp; ${date}*\n`;
    return md;
  },

  // ═══════════════════════════════════════════════════════════
  //  JSON EXPORT — structured JSON format
  // ═══════════════════════════════════════════════════════════
  buildFormattedJSON() {
    if (!this.activeData) return '{}';
    const d   = this.activeData;
    const mod = this.activeModuleName;

    const resultBlock = (() => {
      if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
        return {
          type: 'eigenpairs',
          pairs: d.eigenvalues.map((val, i) => ({
            index: i + 1,
            eigenvalue: val,
            eigenvector: d.eigenvectors ? d.eigenvectors[i] : null
          }))
        };
      }
      const solObj = d.solution || d.solutions;
      if (solObj && typeof solObj === 'object') {
        return {
          type: 'solution_variables',
          variables: solObj
        };
      }
      if (d.result_display && Array.isArray(d.result_display) && Array.isArray(d.result_display[0])) {
        return {
          type: 'matrix',
          rows: d.result_display.length,
          cols: d.result_display[0].length,
          data: d.result_display
        };
      }
      return {
        type: 'scalar',
        value: d.result_display ?? d.result ?? null,
        latex: d.result_latex ?? null
      };
    })();

    const payload = {
      metadata: {
        solver: mod,
        operation: d.operation || null,
        generated: new Date().toISOString(),
        formula_plain: this.getFormulaPlain(mod, d),
        formula_latex: this.getFormula(mod, d) || null
      },
      steps: (d.steps || []).map((step, idx) => ({
        step: idx + 1,
        title: step.title,
        explanation: step.text ? this.stripHtml(step.text) : null,
        items: step.list ? step.list.map(l => this.stripHtml(l)) : null,
        formula_latex: step.latex || null
      })),
      result: resultBlock
    };

    return JSON.stringify(payload, null, 2);
  },

  // ═══════════════════════════════════════════════════════════
  //  CSV EXPORT — tabular spreadsheet format
  // ═══════════════════════════════════════════════════════════
  buildFormattedCSV() {
    if (!this.activeData) return '';
    const d   = this.activeData;
    const mod = this.activeModuleName;
    const lines = [];

    lines.push(`"Linear Algebra Solver - ${mod}"`);
    lines.push(`"Generated","${new Date().toLocaleString()}"`);
    lines.push(`"Operation","${d.operation || ''}"`);
    lines.push('');

    // Result Matrix
    if (d.result_display && Array.isArray(d.result_display) && Array.isArray(d.result_display[0])) {
      lines.push('"Result Matrix:"');
      d.result_display.forEach(row => {
        lines.push((Array.isArray(row) ? row : [row]).map(val => `"${val}"`).join(','));
      });
      lines.push('');
    } else if (d.result_display !== undefined && d.result_display !== null) {
      lines.push(`"Result","${d.result_display}"`);
      lines.push('');
    }

    // Solution variables
    const solObj = d.solution || d.solutions;
    if (solObj && typeof solObj === 'object') {
      lines.push('"Variable","Value"');
      Object.entries(solObj).forEach(([k, v]) => {
        lines.push(`"${k}","${v}"`);
      });
      lines.push('');
    }

    // Eigenpairs
    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      lines.push('"Pair","Eigenvalue","Eigenvector"');
      d.eigenvalues.forEach((val, i) => {
        const vec = d.eigenvectors && d.eigenvectors[i]
          ? `"[${d.eigenvectors[i].join(', ')}]"`
          : '""';
        lines.push(`"λ${i + 1}","${val}",${vec}`);
      });
      lines.push('');
    }

    // Computation Steps
    if (d.steps && d.steps.length > 0) {
      lines.push('"Step","Title","Explanation"');
      d.steps.forEach((step, idx) => {
        const text = this.stripHtml(step.text || '').replace(/"/g, '""');
        lines.push(`"${idx + 1}","${step.title.replace(/"/g, '""')}","${text}"`);
      });
    }

    return lines.join('\n');
  },

  // ═══════════════════════════════════════════════════════════
  //  LaTeX DOCUMENT EXPORT — compilable .tex file
  // ═══════════════════════════════════════════════════════════
  buildFormattedLaTeXDoc() {
    if (!this.activeData) return '';
    const d   = this.activeData;
    const mod = this.activeModuleName;
    const op  = d.operation || '';
    const date = new Date().toLocaleString();
    const formula = this.getFormula(mod, d);

    let tex = `% =========================================================\n`;
    tex    += `% Linear Algebra Solution Document\n`;
    tex    += `% Generated: ${date}\n`;
    tex    += `% =========================================================\n`;
    tex    += `\\documentclass[11pt,a4paper]{article}\n`;
    tex    += `\\usepackage[utf8]{inputenc}\n`;
    tex    += `\\usepackage{amsmath,amssymb,amsfonts}\n`;
    tex    += `\\usepackage{geometry}\n`;
    tex    += `\\geometry{margin=1in}\n`;
    tex    += `\\usepackage{xcolor}\n`;
    tex    += `\\usepackage{hyperref}\n\n`;
    tex    += `\\title{\\textbf{Linear Algebra Solution Report}\\\\[0.5em]\\large ${mod}${op ? ' -- ' + op : ''}}\n`;
    tex    += `\\author{Linear Algebra Solver Engine}\n`;
    tex    += `\\date{${date}}\n\n`;
    tex    += `\\begin{document}\n\\maketitle\n\n`;

    if (formula) {
      tex += `\\section*{1. Governing Formula \\& Method}\n`;
      tex += `\\[ ${formula} \\]\n\n`;
    }

    tex += `\\section*{2. Step-by-Step Computation}\n`;
    if (d.steps && d.steps.length > 0) {
      d.steps.forEach((step, idx) => {
        tex += `\\subsection*{Step ${idx + 1}: ${step.title}}\n`;
        if (step.text) tex += `${this.stripHtml(step.text)}\\\\[0.5em]\n`;
        if (step.latex) tex += `\\[ ${step.latex} \\]\n`;
        tex += `\n`;
      });
    } else {
      tex += `No steps available.\n\n`;
    }

    tex += `\\section*{3. Final Calculated Result}\n`;
    if (d.result_latex) {
      tex += `\\[ ${d.result_latex} \\]\n`;
    } else if (d.result_display) {
      tex += `Result: \\textbf{${d.result_display}}\n`;
    }

    tex += `\n\\end{document}\n`;
    return tex;
  },

  // ═══════════════════════════════════════════════════════════
  //  PDF EXPORT — HTML for html2pdf
  // ═══════════════════════════════════════════════════════════
  buildPDFHtml() {
    if (!this.activeData) return '';
    const d   = this.activeData;
    const mod = this.activeModuleName;
    const op  = d.operation || '';
    const title = op ? `${mod} — ${op}` : mod;
    const date  = new Date().toLocaleString();
    const formula = this.getFormulaPlain(mod, d);

    const css = `
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 13px; color: #1e293b; background: #fff; }
      .page { padding: 32px 36px; }
      .hdr { border-bottom: 3px solid #16a34a; padding-bottom: 14px; margin-bottom: 22px; display: flex; justify-content: space-between; align-items: flex-end; }
      .hdr-left h1 { font-size: 20px; font-weight: 800; color: #16a34a; margin-bottom: 2px; }
      .hdr-left h2 { font-size: 13px; font-weight: 600; color: #334155; }
      .hdr-right { text-align: right; font-size: 10px; color: #94a3b8; }
      .sec-lbl { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px; padding: 4px 10px; border-radius: 4px; display: inline-block; }
      .sec-lbl.blue  { color: #0891b2; background: #f0f9ff; }
      .sec-lbl.amber { color: #b45309; background: #fffbeb; }
      .sec-lbl.green { color: #15803d; background: #f0fdf4; }
      .formula-box { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px 16px; font-family: 'Courier New', monospace; font-size: 12px; color: #0c4a6e; word-break: break-all; margin-bottom: 20px; }
      .step { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #16a34a; border-radius: 6px; padding: 12px 14px; margin-bottom: 10px; page-break-inside: avoid; }
      .step-hdr { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
      .step-num { width: 24px; height: 24px; border-radius: 50%; background: #16a34a; color: #fff; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
      .step-title { font-weight: 700; font-size: 13px; color: #0f172a; }
      .step-text { font-size: 12px; color: #475569; margin: 4px 0 4px 34px; line-height: 1.5; }
      .step-list { margin: 4px 0 4px 34px; padding-left: 16px; font-size: 12px; color: #334155; }
      .step-list li { margin-bottom: 2px; }
      .step-formula { font-family: 'Courier New', monospace; font-size: 11px; color: #1e40af; background: #eff6ff; border-radius: 4px; padding: 4px 8px; margin: 6px 0 2px 34px; word-break: break-all; }
      .result-box { background: #f0fdf4; border: 2px solid #86efac; border-radius: 10px; padding: 18px 20px; text-align: center; margin-bottom: 20px; }
      .result-value { font-size: 18px; font-weight: 800; color: #14532d; }
      .result-label { font-size: 10px; color: #15803d; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
      .mat-table { border-collapse: collapse; margin: 8px auto; font-family: 'Courier New', monospace; font-size: 12px; }
      .mat-table td { padding: 5px 12px; border: 1px solid #cbd5e1; text-align: right; }
      .sol-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
      .sol-item { background: #fff; border: 2px solid #16a34a; border-radius: 8px; padding: 8px 16px; text-align: center; min-width: 80px; }
      .sol-var  { font-size: 11px; color: #6b7280; font-weight: 600; }
      .sol-val  { font-size: 16px; font-weight: 800; color: #14532d; }
      .eigen-table { border-collapse: collapse; width: 100%; font-size: 12px; }
      .eigen-table th { background: #f1f5f9; color: #475569; font-size: 10px; text-transform: uppercase; letter-spacing: .06em; padding: 6px 10px; border: 1px solid #e2e8f0; text-align: left; }
      .eigen-table td { padding: 8px 10px; border: 1px solid #e2e8f0; font-family: 'Courier New', monospace; }
      .eigen-table tr:nth-child(even) td { background: #f8fafc; }
      .footer { margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; text-align: center; color: #94a3b8; font-size: 10px; }
      hr { border: none; border-top: 1px solid #e2e8f0; margin: 18px 0; }
    `;

    let stepsHtml = '';
    if (d.steps && d.steps.length > 0) {
      stepsHtml = d.steps.map((step, idx) => `
        <div class="step">
          <div class="step-hdr">
            <div class="step-num">${idx + 1}</div>
            <div class="step-title">${step.title}</div>
          </div>
          ${step.text ? `<div class="step-text">${this.stripHtml(step.text)}</div>` : ''}
          ${step.list && step.list.length ? `<ul class="step-list">${step.list.map(l => `<li>${this.stripHtml(l)}</li>`).join('')}</ul>` : ''}
          ${step.latex ? `<div class="step-formula">${step.latex}</div>` : ''}
        </div>
      `).join('');
    } else {
      stepsHtml = '<p style="color:#94a3b8; font-style:italic;">No computation steps recorded.</p>';
    }

    let resultHtml = '';
    const solObj = d.solution || d.solutions;

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      const rows = d.eigenvalues.map((val, i) => {
        const vec = d.eigenvectors && d.eigenvectors[i]
          ? d.eigenvectors[i].map(x => `<td>${x}</td>`).join('')
          : '<td>—</td>';
        return `<tr><td>λ${i+1} = ${val}</td>${vec}</tr>`;
      }).join('');
      const vecCols = (d.eigenvectors && d.eigenvectors[0])
        ? d.eigenvectors[0].map((_, j) => `<th>v[${j+1}]</th>`).join('')
        : '<th>Eigenvector</th>';
      resultHtml = `
        <table class="eigen-table">
          <thead><tr><th>Eigenvalue</th>${vecCols}</tr></thead>
          <tbody>${rows}</tbody>
        </table>`;
    } else if (solObj && typeof solObj === 'object') {
      const items = Object.entries(solObj).map(([k, v]) => `
        <div class="sol-item">
          <div class="sol-var">${k}</div>
          <div class="sol-val">${v}</div>
        </div>`).join('');
      resultHtml = `<div class="sol-grid">${items}</div>`;
    } else if (d.result_display && Array.isArray(d.result_display) && Array.isArray(d.result_display[0])) {
      const rows = d.result_display.map(row =>
        '<tr>' + row.map(cell => `<td>${cell}</td>`).join('') + '</tr>'
      ).join('');
      resultHtml = `<table class="mat-table">${rows}</table>`;
    } else {
      const val = d.result_display ?? d.result ?? null;
      if (val !== null) {
        resultHtml = `<div class="result-value">${val}</div>`;
      }
    }
    if (d.result_latex) {
      resultHtml += `<div style="font-family:monospace;font-size:11px;color:#64748b;margin-top:8px;">LaTeX: ${d.result_latex}</div>`;
    }

    return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
      <div class="page">
        <div class="hdr">
          <div class="hdr-left">
            <h1>&#8730; Linear Algebra Solver</h1>
            <h2>${title}</h2>
          </div>
          <div class="hdr-right">
            Detailed Solution Report<br>${date}
          </div>
        </div>

        <span class="sec-lbl blue">1 &nbsp;&#xf1de; &nbsp;Question / Input Data</span>
        ${this.buildQuestionHtml()}

        <span class="sec-lbl blue">2 &nbsp;&#xf1de; &nbsp;Governing Formula &amp; Method</span>
        <div class="formula-box">${formula || title}</div>

        <span class="sec-lbl amber">3 &nbsp;&#x2261; &nbsp;Step-by-Step Computation</span>
        <div style="margin-top:10px;">${stepsHtml}</div>

        <hr>
        <span class="sec-lbl green">4 &nbsp;&#x2714; &nbsp;Final Calculated Result</span>
        <div class="result-box" style="margin-top:10px;">
          <div class="result-label">Result</div>
          ${resultHtml}
        </div>

        <div class="footer">Linear Algebra Solver &mdash; Detailed Solution Report &mdash; ${date}</div>
      </div>
    </body></html>`;
  },

  // ─── Word/RTF Document export ──────────────────────────────
  buildWordHtml() {
    if (!this.activeData) return '';
    const d    = this.activeData;
    const mod  = this.activeModuleName;
    const op   = d.operation || '';
    const title = op ? `${mod} — ${op}` : mod;
    const date  = new Date().toLocaleString();
    const formula = this.getFormulaPlain(mod, d);

    const h2 = (t) => `<h2 style="color:#16a34a;border-bottom:2px solid #16a34a;padding-bottom:6px;">${t}</h2>`;
    const box = (content, bg='#f0f9ff', border='#bae6fd') =>
      `<div style="background:${bg};border:1.5px solid ${border};border-radius:6px;padding:12px 16px;margin-bottom:14px;">${content}</div>`;

    let stepsHtml = '';
    if (d.steps && d.steps.length > 0) {
      stepsHtml = d.steps.map((step, idx) => `
        <div style="background:#f8fafc;border-left:4px solid #16a34a;border:1px solid #e2e8f0;border-radius:5px;padding:10px 14px;margin-bottom:8px;">
          <b style="color:#0f172a;">Step ${idx+1}: ${step.title}</b><br>
          ${step.text ? `<span style="color:#475569;font-size:12px;">${this.stripHtml(step.text)}</span><br>` : ''}
          ${step.list && step.list.length ? '<ul style="margin:4px 0 4px 20px;">' + step.list.map(l => `<li style="font-size:12px;">${this.stripHtml(l)}</li>`).join('') + '</ul>' : ''}
          ${step.latex ? `<code style="font-size:11px;color:#1e40af;background:#eff6ff;padding:2px 6px;">${step.latex}</code>` : ''}
        </div>`).join('');
    } else {
      stepsHtml = '<p style="color:#888;font-style:italic;">No steps recorded.</p>';
    }

    let resultHtml = '';
    const solObj = d.solution || d.solutions;
    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      resultHtml = d.eigenvalues.map((val, i) => {
        const vec = d.eigenvectors && d.eigenvectors[i] ? `[${d.eigenvectors[i].join(', ')}]` : '';
        return `<li><b>\u03bb${i+1} = ${val}</b> &nbsp; v${i+1} = ${vec}</li>`;
      }).join('');
      resultHtml = `<ul style="font-family:monospace;">${resultHtml}</ul>`;
    } else if (solObj && typeof solObj === 'object') {
      resultHtml = Object.entries(solObj).map(([k,v]) =>
        `<b>${k}</b> = ${v}`
      ).join('&nbsp;&nbsp;&nbsp;');
    } else {
      const val = d.result_display ?? d.result ?? null;
      if (val !== null) {
        resultHtml = Array.isArray(val) && Array.isArray(val[0])
          ? '<table border="1" cellpadding="6" style="border-collapse:collapse;font-family:monospace;">' +
            val.map(row => '<tr>' + row.map(c => `<td>${c}</td>`).join('') + '</tr>').join('') +
            '</table>'
          : `<b style="font-size:18px;color:#14532d;">${val}</b>`;
      }
    }
    if (d.result_latex) resultHtml += `<br><code style="font-size:10px;color:#64748b;">${d.result_latex}</code>`;

    return `
      <html xmlns:o='urn:schemas-microsoft-com:office:office'
            xmlns:w='urn:schemas-microsoft-com:office:word'
            xmlns='http://www.w3.org/TR/REC-html40'>
      <head><meta charset="utf-8">
      <style>
        body { font-family: Calibri, sans-serif; font-size: 13px; color: #1e293b; margin: 40px; }
        h1   { font-size: 20px; color: #16a34a; }
        h2   { font-size: 15px; }
        table { border-collapse: collapse; }
        td, th { padding: 5px 10px; border: 1px solid #cbd5e1; }
        th { background: #f1f5f9; }
      </style>
      </head><body>
        <h1>&#8730; Linear Algebra Solver &mdash; Solution Report</h1>
        <p style="color:#64748b;font-size:11px;">Generated: ${date} &nbsp;|&nbsp; Solver: <b>${mod}</b>${op ? ' &nbsp;|&nbsp; Operation: <b>'+op+'</b>' : ''}</p>
        <hr style="border:1.5px solid #16a34a;">

        ${h2('1. Question / Input Data')}
        ${box(this.buildQuestionHtml() || '<p style="color:#888;">No input data captured.</p>')}

        ${h2('2. Governing Formula &amp; Method')}
        ${box(`<code>${formula || title}</code>`)}

        ${h2('3. Step-by-Step Computation')}
        ${stepsHtml}

        <hr style="border:1px solid #e2e8f0;margin:16px 0;">
        ${h2('4. Final Calculated Result')}
        ${box(resultHtml || '<p style="color:#888;">No result.</p>', '#f0fdf4', '#86efac')}

        <p style="color:#94a3b8;font-size:10px;margin-top:30px;border-top:1px solid #e2e8f0;padding-top:8px;text-align:center;">
          Linear Algebra Solver &mdash; ${date}
        </p>
      </body></html>`;
  },

  // ─── Trigger file download helper ─────────────────────────
  triggerDownload(content, filename, type = 'text/plain') {
    const blob = new Blob([content], { type: `${type};charset=utf-8` });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    if (typeof showToast === 'function') showToast(`Downloaded: ${filename}`, 'success');
  },

  safeName() {
    return this.activeModuleName.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
  },

  // ─── Export Action Trigger Methods ────────────────────────

  // Real PDF export using html2pdf.js (already loaded in base.html)
  downloadPDF() {
    if (!this.activeData) {
      const btnCalc = document.getElementById('btnCalculate');
      if (btnCalc) {
        if (typeof showToast === 'function') showToast('Calculating solution before generating PDF…', 'info');
        this.pendingAction = 'pdf';
        btnCalc.click();
        return;
      }
      if (typeof showToast === 'function') showToast('Please calculate a solution first.', 'warning');
      return;
    }

    if (typeof showToast === 'function') showToast('Generating PDF\u2026', 'info');

    // Build the print body HTML (question + formula + steps + result)
    const bodyHtml = this.buildPrintBodyHtml();

    // Create an off-screen styled container for html2pdf to render
    const pdfContainer = document.createElement('div');
    pdfContainer.id = '__pdfExportContainer';
    pdfContainer.style.cssText = [
      'position:absolute', 'top:-99999px', 'left:-99999px',
      'width:794px',          // A4 width in px at 96dpi
      'background:#ffffff',
      'font-family:Segoe UI,system-ui,sans-serif',
      'font-size:13px', 'color:#1e293b', 'line-height:1.5'
    ].join(';');

    // Inject scoped print styles so html2pdf renders correctly
    pdfContainer.innerHTML = `
      <style>
        #__pdfExportContainer .prt-page { padding: 28px 36px; }
        #__pdfExportContainer .prt-hdr { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 3px solid #16a34a; padding-bottom: 14px; margin-bottom: 20px; }
        #__pdfExportContainer .prt-hdr-title { font-size: 20px; font-weight: 800; color: #16a34a; }
        #__pdfExportContainer .prt-hdr-sub { font-size: 13px; font-weight: 600; color: #334155; }
        #__pdfExportContainer .prt-hdr-date { font-size: 10px; color: #94a3b8; text-align: right; }
        #__pdfExportContainer .prt-sec-lbl { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; padding: 4px 10px; border-radius: 4px; display: inline-block; margin-top: 16px; margin-bottom: 8px; }
        #__pdfExportContainer .prt-blue  { color: #0891b2; background: #f0f9ff; }
        #__pdfExportContainer .prt-amber { color: #b45309; background: #fffbeb; }
        #__pdfExportContainer .prt-green { color: #15803d; background: #f0fdf4; }
        #__pdfExportContainer .prt-formula { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; padding: 10px 14px; font-family: 'Courier New', monospace; font-size: 12px; color: #0c4a6e; word-break: break-all; margin-bottom: 8px; }
        #__pdfExportContainer .prt-step { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #16a34a; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; page-break-inside: avoid; }
        #__pdfExportContainer .prt-step-hdr { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
        #__pdfExportContainer .prt-step-num { width: 22px; height: 22px; border-radius: 50%; background: #16a34a; color: #fff; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        #__pdfExportContainer .prt-step-title { font-weight: 700; font-size: 13px; color: #0f172a; }
        #__pdfExportContainer .prt-step-text { font-size: 12px; color: #475569; margin: 4px 0 4px 32px; }
        #__pdfExportContainer .prt-step-list { margin: 4px 0 4px 32px; padding-left: 14px; font-size: 12px; color: #334155; }
        #__pdfExportContainer .prt-step-formula { font-family: 'Courier New', monospace; font-size: 11px; color: #1e40af; background: #eff6ff; border-radius: 4px; padding: 3px 8px; margin: 4px 0 2px 32px; word-break: break-all; }
        #__pdfExportContainer .prt-result-box { background: #f0fdf4; border: 2px solid #86efac; border-radius: 10px; padding: 16px 20px; text-align: center; margin: 8px 0 16px; page-break-inside: avoid; }
        #__pdfExportContainer .prt-result-value { font-size: 18px; font-weight: 800; color: #14532d; }
        #__pdfExportContainer .prt-result-label { font-size: 10px; color: #15803d; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
        #__pdfExportContainer .prt-mat-table { border-collapse: collapse; margin: 8px auto; font-family: 'Courier New', monospace; font-size: 12px; }
        #__pdfExportContainer .prt-mat-table td { padding: 4px 10px; border: 1px solid #cbd5e1; text-align: right; }
        #__pdfExportContainer .prt-sol-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
        #__pdfExportContainer .prt-sol-item { background: #fff; border: 2px solid #16a34a; border-radius: 8px; padding: 6px 14px; text-align: center; min-width: 70px; }
        #__pdfExportContainer .prt-sol-var { font-size: 11px; color: #6b7280; font-weight: 600; }
        #__pdfExportContainer .prt-sol-val { font-size: 15px; font-weight: 800; color: #14532d; }
        #__pdfExportContainer .prt-eigen-table { border-collapse: collapse; width: 100%; font-size: 12px; }
        #__pdfExportContainer .prt-eigen-table th { background: #f1f5f9; color: #475569; font-size: 10px; text-transform: uppercase; padding: 5px 10px; border: 1px solid #e2e8f0; }
        #__pdfExportContainer .prt-eigen-table td { padding: 7px 10px; border: 1px solid #e2e8f0; font-family: 'Courier New', monospace; }
        #__pdfExportContainer .prt-hr { border: none; border-top: 1px solid #e2e8f0; margin: 16px 0; }
        #__pdfExportContainer .prt-footer { margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 8px; text-align: center; color: #94a3b8; font-size: 10px; }
        #__pdfExportContainer .prt-close-btn { display: none !important; }
      </style>
      ${bodyHtml}`;

    document.body.appendChild(pdfContainer);

    const filename = `${this.safeName()}_solution.pdf`;
    const opt = {
      margin:       [8, 8, 8, 8],   // mm
      filename,
      image:        { type: 'jpeg', quality: 0.97 },
      html2canvas:  { scale: 2, useCORS: true, logging: false, backgroundColor: '#ffffff' },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
    };

    if (typeof html2pdf === 'undefined') {
      // Fallback: open print overlay
      document.body.removeChild(pdfContainer);
      if (typeof showToast === 'function') showToast('PDF library unavailable \u2014 using print dialog instead.', 'warning');
      this.printSolution();
      return;
    }

    html2pdf()
      .set(opt)
      .from(pdfContainer)
      .save()
      .then(() => {
        document.body.removeChild(pdfContainer);
        if (typeof showToast === 'function') showToast(`Downloaded: ${filename}`, 'success');
      })
      .catch(err => {
        console.error('[SolutionExporter] PDF error:', err);
        if (document.body.contains(pdfContainer)) document.body.removeChild(pdfContainer);
        if (typeof showToast === 'function') showToast('PDF generation failed. Try Print instead.', 'danger');
      });
  },

  downloadTXT() {
    if (!this.activeData) return;
    this.triggerDownload(this.buildFormattedText(), `${this.safeName()}_solution.txt`, 'text/plain');
  },

  downloadMD() {
    if (!this.activeData) return;
    this.triggerDownload(this.buildFormattedMD(), `${this.safeName()}_solution.md`, 'text/markdown');
  },

  downloadJSON() {
    if (!this.activeData) return;
    this.triggerDownload(this.buildFormattedJSON(), `${this.safeName()}_solution.json`, 'application/json');
  },

  downloadCSV() {
    if (!this.activeData) return;
    this.triggerDownload(this.buildFormattedCSV(), `${this.safeName()}_solution.csv`, 'text/csv');
  },

  downloadLaTeX() {
    if (!this.activeData) return;
    this.triggerDownload(this.buildFormattedLaTeXDoc(), `${this.safeName()}_solution.tex`, 'application/x-tex');
  },

  downloadHTML() {
    if (!this.activeData) return;
    this.triggerDownload(this.buildPDFHtml(), `${this.safeName()}_solution.html`, 'text/html');
  },

  downloadWord() {
    if (!this.activeData) {
      const btnCalc = document.getElementById('btnCalculate');
      if (btnCalc) {
        if (typeof showToast === 'function') showToast('Calculating solution before downloading Word doc…', 'info');
        this.pendingAction = 'word';
        btnCalc.click();
        return;
      }
      if (typeof showToast === 'function') showToast('Please calculate a solution first.', 'warning');
      return;
    }
    const content = this.buildWordHtml();
    const blob = new Blob([content], { type: 'application/msword;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `${this.safeName()}_solution.doc`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    if (typeof showToast === 'function') showToast(`Downloaded: ${this.safeName()}_solution.doc`, 'success');
  },

  // ─── Clipboard Action Methods ─────────────────────────────
  copyToClipboard() {
    if (!this.activeData) return;
    const txt = this.buildFormattedText();
    this.copyString(txt, 'Copied plain text solution to clipboard!');
  },

  copyLaTeX() {
    if (!this.activeData) return;
    const latex = this.activeData.result_latex
      ? `\\[ ${this.activeData.result_latex} \\]`
      : this.buildFormattedLaTeXDoc();
    this.copyString(latex, 'Copied LaTeX code to clipboard!');
  },

  copyMD() {
    if (!this.activeData) return;
    const md = this.buildFormattedMD();
    this.copyString(md, 'Copied Markdown solution to clipboard!');
  },

  copyString(text, successMsg) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
        .then(() => { if (typeof showToast === 'function') showToast(successMsg, 'success'); })
        .catch(() => this.fallbackCopy(text, successMsg));
    } else {
      this.fallbackCopy(text, successMsg);
    }
  },

  fallbackCopy(text, successMsg = 'Copied to clipboard!') {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    if (typeof showToast === 'function') showToast(successMsg, 'success');
  },

  downloadPDF() {
    if (!this.activeData) return;
    const htmlStr  = this.buildPDFHtml();
    const filename = `${this.safeName()}_solution.pdf`;

    if (!window.html2pdf) {
      this.triggerDownload(htmlStr, filename.replace('.pdf', '.html'), 'text/html');
      return;
    }

    const iframe = document.createElement('iframe');
    iframe.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:794px;height:1px;';
    document.body.appendChild(iframe);
    iframe.contentDocument.open();
    iframe.contentDocument.write(htmlStr);
    iframe.contentDocument.close();

    if (typeof showToast === 'function') showToast('Generating PDF document…', 'info');

    setTimeout(() => {
      html2pdf().set({
        margin: [8, 8, 8, 8],
        filename,
        image:      { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, logging: false, useCORS: true, allowTaint: true },
        jsPDF:       { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }).from(iframe.contentDocument.body).save().then(() => {
        document.body.removeChild(iframe);
        if (typeof showToast === 'function') showToast(`Downloaded: ${filename}`, 'success');
      }).catch(err => {
        console.error('PDF error:', err);
        document.body.removeChild(iframe);
        this.downloadTXT();
      });
    }, 300);
  },

  // ─── Builds print body content (no outer html/head/body tags) ────
  buildPrintBodyHtml() {
    if (!this.activeData) return '';
    const d    = this.activeData;
    const mod  = this.activeModuleName;
    const op   = d.operation || '';
    const title = op ? `${mod} — ${op}` : mod;
    const date  = new Date().toLocaleString();
    const formula = this.getFormulaPlain(mod, d);

    let stepsHtml = '';
    if (d.steps && d.steps.length > 0) {
      stepsHtml = d.steps.map((step, idx) => `
        <div class="prt-step">
          <div class="prt-step-hdr">
            <div class="prt-step-num">${idx + 1}</div>
            <div class="prt-step-title">${step.title}</div>
          </div>
          ${step.text ? `<div class="prt-step-text">${this.stripHtml(step.text)}</div>` : ''}
          ${step.list && step.list.length ? `<ul class="prt-step-list">${step.list.map(l => `<li>${this.stripHtml(l)}</li>`).join('')}</ul>` : ''}
          ${step.latex ? `<div class="prt-step-formula">${step.latex}</div>` : ''}
        </div>
      `).join('');
    } else {
      stepsHtml = '<p style="color:#666;font-style:italic;">No computation steps recorded.</p>';
    }

    let resultHtml = '';
    const solObj = d.solution || d.solutions;

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      const rows = d.eigenvalues.map((val, i) => {
        const vec = d.eigenvectors && d.eigenvectors[i]
          ? d.eigenvectors[i].map(x => `<td>${x}</td>`).join('')
          : '<td>—</td>';
        return `<tr><td>λ${i+1} = ${val}</td>${vec}</tr>`;
      }).join('');
      const vecCols = (d.eigenvectors && d.eigenvectors[0])
        ? d.eigenvectors[0].map((_, j) => `<th>v[${j+1}]</th>`).join('')
        : '<th>Eigenvector</th>';
      resultHtml = `<table class="prt-eigen-table"><thead><tr><th>Eigenvalue</th>${vecCols}</tr></thead><tbody>${rows}</tbody></table>`;
    } else if (solObj && typeof solObj === 'object') {
      const items = Object.entries(solObj).map(([k, v]) => `
        <div class="prt-sol-item"><div class="prt-sol-var">${k}</div><div class="prt-sol-val">${v}</div></div>
      `).join('');
      resultHtml = `<div class="prt-sol-grid">${items}</div>`;
    } else if (d.result_display && Array.isArray(d.result_display) && Array.isArray(d.result_display[0])) {
      const rows = d.result_display.map(row =>
        '<tr>' + row.map(cell => `<td>${cell}</td>`).join('') + '</tr>'
      ).join('');
      resultHtml = `<table class="prt-mat-table">${rows}</table>`;
    } else {
      const val = d.result_display ?? d.result ?? null;
      if (val !== null) resultHtml = `<div class="prt-result-value">${val}</div>`;
    }
    if (d.result_latex) {
      resultHtml += `<div style="font-family:monospace;font-size:11px;color:#666;margin-top:8px;">LaTeX: ${d.result_latex}</div>`;
    }

    return `
      <div class="prt-page">
        <div class="prt-hdr">
          <div>
            <div class="prt-hdr-title">Linear Algebra Solver</div>
            <div class="prt-hdr-sub">${title}</div>
          </div>
          <div class="prt-hdr-date">Detailed Solution Report<br>${date}</div>
        </div>

        <div class="prt-sec-lbl prt-blue">1 · Question / Input Data</div>
        ${this.buildQuestionHtml(true)}

        <div class="prt-sec-lbl prt-blue">2 · Governing Formula &amp; Method</div>
        <div class="prt-formula">${formula || title}</div>

        <div class="prt-sec-lbl prt-amber">3 · Step-by-Step Computation</div>
        <div style="margin-top:10px;">${stepsHtml}</div>

        <hr class="prt-hr">
        <div class="prt-sec-lbl prt-green">4 · Final Calculated Result</div>
        <div class="prt-result-box">
          <div class="prt-result-label">Result</div>
          ${resultHtml}
        </div>

        <div class="prt-footer">Linear Algebra Solver — Detailed Solution Report — ${date}</div>
      </div>`;
  },

  printSolution() {
    if (!this.activeData) {
      const btnCalc = document.getElementById('btnCalculate');
      if (btnCalc) {
        if (typeof showToast === 'function') showToast('Calculating solution before printing…', 'info');
        this.pendingAction = 'print';
        btnCalc.click();
        return;
      }
      if (typeof showToast === 'function') showToast('Please calculate a solution first before printing.', 'warning');
      return;
    }

    // Remove any previous print overlay
    const existing = document.getElementById('solutionPrintOverlay');
    if (existing) existing.remove();

    // Create overlay with scoped inline styles + body content (no nested html docs)
    const overlay = document.createElement('div');
    overlay.id = 'solutionPrintOverlay';
    overlay.innerHTML = `
      <style>
        #solutionPrintOverlay {
          display: none;
          position: fixed;
          inset: 0;
          z-index: 99999;
          background: #fff;
          overflow: auto;
          font-family: 'Segoe UI', system-ui, sans-serif;
          font-size: 13px;
          color: #1e293b;
        }
        .prt-page { padding: 32px 36px; }
        .prt-hdr { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 3px solid #16a34a; padding-bottom: 14px; margin-bottom: 22px; }
        .prt-hdr-title { font-size: 20px; font-weight: 800; color: #16a34a; }
        .prt-hdr-sub { font-size: 13px; font-weight: 600; color: #334155; }
        .prt-hdr-date { font-size: 10px; color: #94a3b8; text-align: right; }
        .prt-sec-lbl { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; padding: 4px 10px; border-radius: 4px; display: inline-block; margin-top: 18px; margin-bottom: 8px; }
        .prt-blue  { color: #0891b2; background: #f0f9ff; }
        .prt-amber { color: #b45309; background: #fffbeb; }
        .prt-green { color: #15803d; background: #f0fdf4; }
        .prt-formula { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px 16px; font-family: 'Courier New', monospace; font-size: 12px; color: #0c4a6e; word-break: break-all; margin-bottom: 10px; }
        .prt-step { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #16a34a; border-radius: 6px; padding: 12px 14px; margin-bottom: 10px; }
        .prt-step-hdr { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
        .prt-step-num { width: 24px; height: 24px; border-radius: 50%; background: #16a34a; color: #fff; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .prt-step-title { font-weight: 700; font-size: 13px; color: #0f172a; }
        .prt-step-text { font-size: 12px; color: #475569; margin: 4px 0 4px 34px; line-height: 1.5; }
        .prt-step-list { margin: 4px 0 4px 34px; padding-left: 16px; font-size: 12px; color: #334155; }
        .prt-step-list li { margin-bottom: 2px; }
        .prt-step-formula { font-family: 'Courier New', monospace; font-size: 11px; color: #1e40af; background: #eff6ff; border-radius: 4px; padding: 4px 8px; margin: 6px 0 2px 34px; word-break: break-all; }
        .prt-result-box { background: #f0fdf4; border: 2px solid #86efac; border-radius: 10px; padding: 18px 20px; text-align: center; margin: 10px 0 20px; }
        .prt-result-value { font-size: 18px; font-weight: 800; color: #14532d; }
        .prt-result-label { font-size: 10px; color: #15803d; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
        .prt-mat-table { border-collapse: collapse; margin: 8px auto; font-family: 'Courier New', monospace; font-size: 12px; }
        .prt-mat-table td { padding: 5px 12px; border: 1px solid #cbd5e1; text-align: right; }
        .prt-sol-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
        .prt-sol-item { background: #fff; border: 2px solid #16a34a; border-radius: 8px; padding: 8px 16px; text-align: center; min-width: 80px; }
        .prt-sol-var { font-size: 11px; color: #6b7280; font-weight: 600; }
        .prt-sol-val { font-size: 16px; font-weight: 800; color: #14532d; }
        .prt-eigen-table { border-collapse: collapse; width: 100%; font-size: 12px; }
        .prt-eigen-table th { background: #f1f5f9; color: #475569; font-size: 10px; text-transform: uppercase; padding: 6px 10px; border: 1px solid #e2e8f0; text-align: left; }
        .prt-eigen-table td { padding: 8px 10px; border: 1px solid #e2e8f0; font-family: 'Courier New', monospace; }
        .prt-hr { border: none; border-top: 1px solid #e2e8f0; margin: 18px 0; }
        .prt-footer { margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; text-align: center; color: #94a3b8; font-size: 10px; }
        .prt-close-btn {
          position: fixed; top: 14px; right: 20px; z-index: 100000;
          background: #ef4444; color: #fff; border: none; border-radius: 6px;
          padding: 6px 14px; font-size: 13px; font-weight: 700; cursor: pointer;
          display: flex; align-items: center; gap: 6px;
        }
        @media print {
          .prt-close-btn { display: none !important; }
          .prt-page { padding: 16px 24px; }
        }
      </style>
      <button class="prt-close-btn" onclick="document.getElementById('solutionPrintOverlay').remove()">
        ✕ Close
      </button>
      ${this.buildPrintBodyHtml()}
    `;

    document.body.appendChild(overlay);
    overlay.style.display = 'block';

    if (typeof showToast === 'function') showToast('Opening print dialog…', 'info');

    // Clean up overlay when print dialog closes
    const handleAfterPrint = () => {
      const ov = document.getElementById('solutionPrintOverlay');
      if (ov) ov.remove();
      window.removeEventListener('afterprint', handleAfterPrint);
    };
    window.addEventListener('afterprint', handleAfterPrint);

    // Trigger browser print
    setTimeout(() => {
      window.print();
    }, 350);
  }
};
