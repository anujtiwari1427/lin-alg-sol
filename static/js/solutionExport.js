/* =========================================================
   SOLUTION EXPORTER  — Well-Formatted Export Engine
   Handles all 6 solvers: Matrix, Determinant, Inverse,
   Vector, Linear Equations, Eigenvalue/Eigenvector.
   Exports: PDF, TXT, Markdown, JSON, Clipboard.
   ========================================================= */

const SolutionExporter = {
  activeData: null,
  activeModuleName: 'Linear Algebra Solution',

  setSolution(data, moduleName) {
    this.activeData = data;
    this.activeModuleName = moduleName || 'Linear Algebra Solution';
    this.renderDirectSolution(data, moduleName);
  },

  // ─── Formula lookup ──────────────────────────────────────
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

  // ─── Formula text (plain, for TXT/clipboard) ─────────────
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
    const accordion   = document.getElementById('stepsAccordion');
    const downloadPanel = document.getElementById('downloadPanelContainer');
    const formula = this.getFormula(moduleName, data);

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
        <div class="d-flex align-items-center gap-2 mb-3">
          <div class="download-icon-box"><i class="fas fa-file-export"></i></div>
          <div>
            <h6 class="fw-bold mb-0 text-primary-accent">Export Full Detailed Solution</h6>
            <p class="small text-secondary mb-0">Well-formatted export of formula, all steps &amp; result</p>
          </div>
        </div>
        <div class="row g-2">
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadPDF()">
              <i class="fas fa-file-pdf text-danger"></i><span>PDF</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadTXT()">
              <i class="fas fa-file-lines text-info"></i><span>Text</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadMD()">
              <i class="fab fa-markdown text-warning"></i><span>Markdown</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadJSON()">
              <i class="fas fa-file-code text-success"></i><span>JSON</span>
            </button>
          </div>
        </div>
        <div class="mt-3 d-flex justify-content-end">
          <button type="button" class="btn btn-sm btn-secondary-custom" onclick="SolutionExporter.copyToClipboard()">
            <i class="fas fa-copy me-1"></i>Copy Full Solution
          </button>
        </div>
      </div>`;
    if (window.MathJax && window.MathJax.typeset) window.MathJax.typeset();
  },

  // ═══════════════════════════════════════════════════════════
  //  TEXT EXPORT — well-aligned plain text
  // ═══════════════════════════════════════════════════════════
  buildFormattedText() {
    if (!this.activeData) return '';
    const d   = this.activeData;
    const mod = this.activeModuleName;
    const op  = d.operation || '';
    const title = op ? `${mod} — ${op}` : mod;
    const date  = new Date().toLocaleString();
    const W     = 62;  // page width
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

    // ── Section 1: Formula ──────────────────────────────────
    t += `  [1]  GOVERNING FORMULA & METHOD\n`;
    t += `  ${hr2}\n`;
    const formula = this.getFormulaPlain(mod, d);
    t += `  ${formula || title}\n\n`;

    // ── Section 2: Steps ────────────────────────────────────
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

    // ── Section 3: Result ───────────────────────────────────
    t += `  [3]  FINAL RESULT\n`;
    t += `  ${hr2}\n`;

    // Matrix result
    if (d.result_display && Array.isArray(d.result_display) && Array.isArray(d.result_display[0])) {
      t += `\n  Result Matrix:\n${this.formatMatrix(d.result_display)}\n\n`;
    } else if (d.result_display) {
      t += `\n  Result: ${d.result_display}\n\n`;
    } else if (d.result !== undefined && d.result !== null) {
      t += `\n  Result: ${d.result}\n\n`;
    }

    // Solution variables (linear equations)
    const solObj = d.solution || d.solutions;
    if (solObj && typeof solObj === 'object') {
      t += `  Solution Variables:\n`;
      Object.entries(solObj).forEach(([k, v]) => {
        t += `    ${(k + ' ').padEnd(6)}=  ${v}\n`;
      });
      t += '\n';
    }

    // Eigenpairs
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
  //  MARKDOWN EXPORT — GitHub-flavored markdown
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

    // Section 1: Formula
    md += `## 1. Governing Formula & Method\n\n`;
    if (formula) {
      md += `$$\n${formula}\n$$\n\n`;
    } else {
      md += `> ${title}\n\n`;
    }

    // Section 2: Steps
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

    // Section 3: Result
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

    // Solution variables
    const solObj = d.solution || d.solutions;
    if (solObj && typeof solObj === 'object') {
      md += `### Solution Variables\n\n`;
      md += `| Variable | Value |\n|---|---|\n`;
      Object.entries(solObj).forEach(([k, v]) => {
        md += `| **${k}** | \`${v}\` |\n`;
      });
      md += '\n';
    }

    // Eigenpairs
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
  //  JSON EXPORT — structured, human-readable
  // ═══════════════════════════════════════════════════════════
  buildFormattedJSON() {
    if (!this.activeData) return '{}';
    const d   = this.activeData;
    const mod = this.activeModuleName;

    // Structured result object per solver type
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
  //  PDF EXPORT — polished HTML → html2pdf
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
      /* Header */
      .hdr { border-bottom: 3px solid #16a34a; padding-bottom: 14px; margin-bottom: 22px; display: flex; justify-content: space-between; align-items: flex-end; }
      .hdr-left h1 { font-size: 20px; font-weight: 800; color: #16a34a; margin-bottom: 2px; }
      .hdr-left h2 { font-size: 13px; font-weight: 600; color: #334155; }
      .hdr-right { text-align: right; font-size: 10px; color: #94a3b8; }
      /* Section headers */
      .sec-lbl { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px; padding: 4px 10px; border-radius: 4px; display: inline-block; }
      .sec-lbl.blue  { color: #0891b2; background: #f0f9ff; }
      .sec-lbl.amber { color: #b45309; background: #fffbeb; }
      .sec-lbl.green { color: #15803d; background: #f0fdf4; }
      /* Formula box */
      .formula-box { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px 16px; font-family: 'Courier New', monospace; font-size: 12px; color: #0c4a6e; word-break: break-all; margin-bottom: 20px; }
      /* Steps */
      .step { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #16a34a; border-radius: 6px; padding: 12px 14px; margin-bottom: 10px; page-break-inside: avoid; }
      .step-hdr { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
      .step-num { width: 24px; height: 24px; border-radius: 50%; background: #16a34a; color: #fff; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
      .step-title { font-weight: 700; font-size: 13px; color: #0f172a; }
      .step-text { font-size: 12px; color: #475569; margin: 4px 0 4px 34px; line-height: 1.5; }
      .step-list { margin: 4px 0 4px 34px; padding-left: 16px; font-size: 12px; color: #334155; }
      .step-list li { margin-bottom: 2px; }
      .step-formula { font-family: 'Courier New', monospace; font-size: 11px; color: #1e40af; background: #eff6ff; border-radius: 4px; padding: 4px 8px; margin: 6px 0 2px 34px; word-break: break-all; }
      /* Result */
      .result-box { background: #f0fdf4; border: 2px solid #86efac; border-radius: 10px; padding: 18px 20px; text-align: center; margin-bottom: 20px; }
      .result-value { font-size: 18px; font-weight: 800; color: #14532d; }
      .result-label { font-size: 10px; color: #15803d; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
      /* Matrix table */
      .mat-table { border-collapse: collapse; margin: 8px auto; font-family: 'Courier New', monospace; font-size: 12px; }
      .mat-table td { padding: 5px 12px; border: 1px solid #cbd5e1; text-align: right; }
      /* Solution vars */
      .sol-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
      .sol-item { background: #fff; border: 2px solid #16a34a; border-radius: 8px; padding: 8px 16px; text-align: center; min-width: 80px; }
      .sol-var  { font-size: 11px; color: #6b7280; font-weight: 600; }
      .sol-val  { font-size: 16px; font-weight: 800; color: #14532d; }
      /* Eigen table */
      .eigen-table { border-collapse: collapse; width: 100%; font-size: 12px; }
      .eigen-table th { background: #f1f5f9; color: #475569; font-size: 10px; text-transform: uppercase; letter-spacing: .06em; padding: 6px 10px; border: 1px solid #e2e8f0; text-align: left; }
      .eigen-table td { padding: 8px 10px; border: 1px solid #e2e8f0; font-family: 'Courier New', monospace; }
      .eigen-table tr:nth-child(even) td { background: #f8fafc; }
      /* Footer */
      .footer { margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; text-align: center; color: #94a3b8; font-size: 10px; }
      hr { border: none; border-top: 1px solid #e2e8f0; margin: 18px 0; }
    `;

    // Build steps HTML
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

    // Build result HTML
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

        <span class="sec-lbl blue">1 &nbsp;&#xf1de; &nbsp;Governing Formula &amp; Method</span>
        <div class="formula-box">${formula || title}</div>

        <span class="sec-lbl amber">2 &nbsp;&#x2261; &nbsp;Step-by-Step Computation</span>
        <div style="margin-top:10px;">${stepsHtml}</div>

        <hr>
        <span class="sec-lbl green">3 &nbsp;&#x2714; &nbsp;Final Calculated Result</span>
        <div class="result-box" style="margin-top:10px;">
          <div class="result-label">Result</div>
          ${resultHtml}
        </div>

        <div class="footer">Linear Algebra Solver &mdash; Detailed Solution Report &mdash; ${date}</div>
      </div>
    </body></html>`;
  },

  // ─── Download helpers ─────────────────────────────────────
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

  copyToClipboard() {
    if (!this.activeData) return;
    const txt = this.buildFormattedText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt)
        .then(() => { if (typeof showToast === 'function') showToast('Copied full solution to clipboard!', 'success'); })
        .catch(() => this.fallbackCopy(txt));
    } else {
      this.fallbackCopy(txt);
    }
  },

  fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    if (typeof showToast === 'function') showToast('Copied full solution to clipboard!', 'success');
  },

  downloadPDF() {
    if (!this.activeData) return;
    const htmlStr  = this.buildPDFHtml();
    const filename = `${this.safeName()}_solution.pdf`;

    if (!window.html2pdf) {
      // Fallback: download as HTML file
      this.triggerDownload(htmlStr, filename.replace('.pdf', '.html'), 'text/html');
      return;
    }

    // Create hidden iframe to render the standalone HTML doc
    const iframe = document.createElement('iframe');
    iframe.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:794px;height:1px;';
    document.body.appendChild(iframe);
    iframe.contentDocument.open();
    iframe.contentDocument.write(htmlStr);
    iframe.contentDocument.close();

    if (typeof showToast === 'function') showToast('Generating PDF…', 'info');

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
  }
};
