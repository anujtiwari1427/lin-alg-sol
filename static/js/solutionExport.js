/* =========================================================
   SOLUTION EXPORTER — DIRECT DETAILED VIEW + EXPORT ENGINE
   Shows Formula + All Steps (directly visible, no dropdown) + Result,
   with export options (PDF, TXT, MD, JSON, Clipboard) placed after.
   ========================================================= */

const SolutionExporter = {
  activeData: null,
  activeModuleName: 'Linear Algebra Solution',

  setSolution(data, moduleName) {
    this.activeData = data;
    this.activeModuleName = moduleName || 'Linear Algebra Solution';
    this.renderDirectSolution(data, moduleName);
  },

  // ─── Formula lookup per module + operation ─────────────────────────
  getFormula(moduleName, data) {
    const op = (data.operation || '').toLowerCase();
    const mod = (moduleName || '').toLowerCase();

    if (mod.includes('matrix')) {
      if (op.includes('add')) return 'C = A + B \\quad \\text{where } c_{ij} = a_{ij} + b_{ij}';
      if (op.includes('sub')) return 'C = A - B \\quad \\text{where } c_{ij} = a_{ij} - b_{ij}';
      if (op.includes('multi') && !op.includes('scalar')) return 'C_{ij} = \\sum_{k=1}^{n} A_{ik} \\cdot B_{kj}';
      if (op.includes('scalar')) return 'B = k \\cdot A \\quad \\text{where } b_{ij} = k \\cdot a_{ij}';
      if (op.includes('transpose')) return '(A^T)_{ij} = A_{ji}';
      if (op.includes('trace')) return '\\text{tr}(A) = \\sum_{i=1}^{n} a_{ii}';
      if (op.includes('rank')) return '\\text{rank}(A) = \\text{number of non-zero rows in RREF}(A)';
      return 'C = f(A, B)';
    }
    if (mod.includes('determinant')) {
      return '\\det(A) = \\sum_{j=1}^{n} (-1)^{1+j}\\; a_{1j}\\; \\det(M_{1j})';
    }
    if (mod.includes('inverse')) {
      return 'A^{-1} = \\frac{1}{\\det(A)}\\,\\text{adj}(A) \\quad \\text{or}\\; [A \\mid I] \\xrightarrow{\\text{RREF}} [I \\mid A^{-1}]';
    }
    if (mod.includes('vector')) {
      if (op.includes('dot')) return '\\vec{u} \\cdot \\vec{v} = \\sum_{i=1}^{n} u_i v_i';
      if (op.includes('cross')) return '\\vec{u} \\times \\vec{v} = \\begin{vmatrix} \\hat{i} & \\hat{j} & \\hat{k} \\\\ u_1 & u_2 & u_3 \\\\ v_1 & v_2 & v_3 \\end{vmatrix}';
      if (op.includes('magnitude')) return '\\|\\vec{v}\\| = \\sqrt{\\sum_{i=1}^{n} v_i^2}';
      if (op.includes('unit')) return '\\hat{v} = \\frac{\\vec{v}}{\\|\\vec{v}\\|}';
      if (op.includes('add')) return '\\vec{u} + \\vec{v} = (u_1+v_1,\\; u_2+v_2,\\; \\dots,\\; u_n+v_n)';
      if (op.includes('sub')) return '\\vec{u} - \\vec{v} = (u_1-v_1,\\; u_2-v_2,\\; \\dots,\\; u_n-v_n)';
      return '\\vec{r} = f(\\vec{u}, \\vec{v})';
    }
    if (mod.includes('linear')) {
      return 'A\\mathbf{x} = \\mathbf{b} \\;\\implies\\; \\mathbf{x} = A^{-1}\\mathbf{b} \\quad \\text{or via Gaussian Elimination}\\; [A \\mid \\mathbf{b}]';
    }
    if (mod.includes('eigen')) {
      return '\\det(A - \\lambda I) = 0 \\quad \\text{and}\\quad (A - \\lambda I)\\mathbf{v} = \\mathbf{0}';
    }
    return '';
  },

  // ─── Main render: direct view (no dropdown) + export at bottom ─────
  renderDirectSolution(data, moduleName) {
    const accordion = document.getElementById('stepsAccordion');
    const downloadPanel = document.getElementById('downloadPanelContainer');

    // Hide the old accordion and its heading
    if (accordion) {
      accordion.style.display = 'none';
      // Also hide the h6 heading right before it
      const prevSibling = accordion.previousElementSibling;
      if (prevSibling && prevSibling.tagName === 'H6') {
        prevSibling.style.display = 'none';
      }
    }
    // Hide the separate download panel container (we embed export inside the card)
    if (downloadPanel) {
      downloadPanel.style.display = 'none';
    }

    // Create or reuse the combined container
    let container = document.getElementById('directSolutionContainer');
    if (!container && accordion) {
      container = document.createElement('div');
      container.id = 'directSolutionContainer';
      accordion.parentNode.insertBefore(container, accordion);
    }
    if (!container) return;

    const formula = this.getFormula(moduleName, data);
    const title = data.operation ? `${moduleName} — ${data.operation}` : moduleName;

    // ── Build steps HTML (all directly visible, no dropdown) ──────────
    let stepsHtml = '';
    if (data.steps && data.steps.length > 0) {
      stepsHtml = data.steps.map((step, idx) => `
        <div class="direct-step-block rounded-3 p-3 mb-3">
          <div class="d-flex align-items-start gap-2 mb-2">
            <span class="step-num-badge">${idx + 1}</span>
            <span class="fw-bold text-primary-accent">${step.title}</span>
          </div>
          ${step.text ? `<p class="mb-2 text-secondary small ps-4">${step.text}</p>` : ''}
          ${step.list ? `<ul class="small font-monospace mb-2 ps-4">${step.list.map(l => `<li>${l}</li>`).join('')}</ul>` : ''}
          ${step.latex ? `<div class="step-latex text-center my-2">\\[ ${step.latex} \\]</div>` : ''}
        </div>
      `).join('');
    }

    // ── Build solution values (for linear equations) ─────────────────
    let solutionValuesHtml = '';
    const solObj = data.solution || data.solutions;
    if (solObj) {
      solutionValuesHtml = `
        <div class="d-flex flex-wrap gap-2 mb-3">
          ${Object.entries(solObj).map(([k, v]) => `
            <div class="solution-var">
              <div class="var-name">${k}</div>
              <div class="var-val">${v}</div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // ── Build eigenpairs (for eigen) ─────────────────────────────────
    let eigenHtml = '';
    if (data.eigenvalues && Array.isArray(data.eigenvalues)) {
      eigenHtml = data.eigenvalues.map((val, idx) => {
        const vec = data.eigenvectors && data.eigenvectors[idx] ? data.eigenvectors[idx].join(', ') : '';
        return `
          <div class="eigen-pair-card mb-2">
            <div class="eigen-val-header">λ${idx + 1} = ${val}</div>
            <div class="eigen-vec-body">v${idx + 1} = [${vec}]ᵀ</div>
          </div>
        `;
      }).join('');
    }

    // ── Build result LaTeX ───────────────────────────────────────────
    let resultHtml = '';
    if (data.result_latex) {
      resultHtml = `\\[ ${data.result_latex} \\]`;
    } else if (data.result_display) {
      resultHtml = `<div class="fs-4 fw-bold font-monospace text-primary-accent">${JSON.stringify(data.result_display)}</div>`;
    }

    // ── Render the full direct card ──────────────────────────────────
    container.innerHTML = `
      <div class="combined-single-card p-3 p-md-4 mt-3">

        <!-- ▸ SECTION 1 — Formula & Method -->
        <div class="mb-4">
          <div class="section-label text-info"><i class="fas fa-square-root-variable me-2"></i>Governing Formula & Method</div>
          <div class="formula-box p-3 rounded-3 text-center border border-info-subtle mt-2">
            ${formula ? `\\[ ${formula} \\]` : `<span class="text-muted fst-italic">${title}</span>`}
          </div>
        </div>

        <!-- ▸ SECTION 2 — All Steps (directly visible) -->
        <div class="mb-4">
          <div class="section-label text-warning"><i class="fas fa-calculator me-2"></i>Complete Step-by-Step Computation</div>
          <div class="mt-2">
            ${stepsHtml || '<p class="text-muted small fst-italic">No computation steps available.</p>'}
          </div>
        </div>

        <!-- ▸ SECTION 3 — Final Result -->
        <div class="mb-4">
          <div class="section-label text-success"><i class="fas fa-check-double me-2"></i>Final Calculated Result</div>
          <div class="result-highlight-box p-3 rounded-3 text-center mt-2">
            ${eigenHtml}
            ${solutionValuesHtml}
            ${resultHtml}
          </div>
        </div>

        <!-- ▸ SECTION 4 — Export Options -->
        <div class="export-section pt-3 mt-3 border-top border-secondary-subtle">
          <div class="d-flex align-items-center gap-2 mb-3">
            <div class="download-icon-box"><i class="fas fa-file-export"></i></div>
            <div>
              <h6 class="fw-bold mb-0 text-primary-accent">Export Full Detailed Solution</h6>
              <p class="small text-secondary mb-0">Download the complete formula, computation & result report</p>
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
        </div>
      </div>
    `;

    if (window.MathJax && window.MathJax.typeset) {
      window.MathJax.typeset();
    }
  },

  // ─── Text export builder ───────────────────────────────────────────
  buildFormattedText() {
    if (!this.activeData) return '';
    const d = this.activeData;
    const title = d.operation ? `${this.activeModuleName} — ${d.operation}` : this.activeModuleName;
    const dateStr = new Date().toLocaleString();
    const formula = this.getFormula(this.activeModuleName, d);

    let txt = `=========================================================\n`;
    txt += `DETAILED SOLUTION REPORT\n`;
    txt += `${title.toUpperCase()}\n`;
    txt += `Generated: ${dateStr}\n`;
    txt += `=========================================================\n\n`;

    txt += `[1] GOVERNING FORMULA & METHOD\n`;
    txt += `${'-'.repeat(50)}\n`;
    txt += formula ? `  ${formula}\n\n` : `  ${title}\n\n`;

    txt += `[2] COMPLETE STEP-BY-STEP COMPUTATION\n`;
    txt += `${'-'.repeat(50)}\n`;
    if (d.steps && d.steps.length > 0) {
      d.steps.forEach((step, idx) => {
        txt += `  Step ${idx + 1}: ${step.title}\n`;
        if (step.text) txt += `    ${step.text}\n`;
        if (step.list && step.list.length > 0) {
          step.list.forEach(item => {
            txt += `      • ${item.replace(/<[^>]*>?/gm, '')}\n`;
          });
        }
        if (step.latex) {
          txt += `      LaTeX: ${step.latex}\n`;
        }
        txt += `\n`;
      });
    } else {
      txt += `  (no computation steps)\n\n`;
    }

    txt += `[3] FINAL CALCULATED RESULT\n`;
    txt += `${'-'.repeat(50)}\n`;
    if (d.result_display) {
      if (Array.isArray(d.result_display)) {
        txt += d.result_display.map(row => `  [ ${row.join(', ')} ]`).join('\n') + '\n';
      } else {
        txt += `  ${d.result_display}\n`;
      }
    } else if (d.result !== undefined) {
      txt += `  ${d.result}\n`;
    }
    if (d.result_latex) {
      txt += `  LaTeX: ${d.result_latex}\n`;
    }
    txt += `\n`;

    const solObj = d.solution || d.solutions;
    if (solObj) {
      txt += `  Solution Values:\n`;
      Object.entries(solObj).forEach(([k, v]) => {
        txt += `    ${k} = ${v}\n`;
      });
      txt += `\n`;
    }

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      txt += `  Eigenpairs:\n`;
      d.eigenvalues.forEach((val, idx) => {
        const vec = d.eigenvectors && d.eigenvectors[idx] ? d.eigenvectors[idx].join(', ') : '';
        txt += `    λ${idx + 1} = ${val},  v${idx + 1} = [${vec}]ᵀ\n`;
      });
      txt += `\n`;
    }

    txt += `=========================================================\n`;
    txt += `Linear Algebra Solver — Detailed Solution Engine\n`;
    return txt;
  },

  // ─── Markdown export builder ───────────────────────────────────────
  buildFormattedMD() {
    if (!this.activeData) return '';
    const d = this.activeData;
    const title = d.operation ? `${this.activeModuleName}: ${d.operation}` : this.activeModuleName;
    const dateStr = new Date().toLocaleString();
    const formula = this.getFormula(this.activeModuleName, d);

    let md = `# Detailed Solution Report — ${title}\n\n`;
    md += `> Generated on ${dateStr}\n\n---\n\n`;

    md += `## 1. Governing Formula & Method\n\n`;
    md += formula ? `$$\n${formula}\n$$\n\n` : `*${title}*\n\n`;

    md += `## 2. Complete Step-by-Step Computation\n\n`;
    if (d.steps && d.steps.length > 0) {
      d.steps.forEach((step, idx) => {
        md += `### Step ${idx + 1}: ${step.title}\n\n`;
        if (step.text) md += `${step.text}\n\n`;
        if (step.list && step.list.length > 0) {
          step.list.forEach(item => { md += `- ${item}\n`; });
          md += `\n`;
        }
        if (step.latex) {
          md += `$$\n${step.latex}\n$$\n\n`;
        }
      });
    }

    md += `## 3. Final Calculated Result\n\n`;
    if (d.result_latex) {
      md += `$$\n${d.result_latex}\n$$\n\n`;
    } else if (d.result_display) {
      md += `\`\`\`\n${JSON.stringify(d.result_display, null, 2)}\n\`\`\`\n\n`;
    }

    const solObjMd = d.solution || d.solutions;
    if (solObjMd) {
      md += `### Solution Values\n`;
      Object.entries(solObjMd).forEach(([k, v]) => { md += `- **${k}**: \`${v}\`\n`; });
      md += `\n`;
    }

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      md += `### Eigenpairs\n`;
      d.eigenvalues.forEach((val, idx) => {
        const vec = d.eigenvectors && d.eigenvectors[idx] ? d.eigenvectors[idx].join(', ') : '';
        md += `- **λ${idx + 1}** = \`${val}\`,  **v${idx + 1}** = \`[${vec}]ᵀ\`\n`;
      });
      md += `\n`;
    }

    return md;
  },

  // ─── Download helpers ──────────────────────────────────────────────
  triggerDownload(content, filename, type = 'text/plain') {
    const blob = new Blob([content], { type: `${type};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    if (typeof showToast === 'function') showToast(`Downloaded ${filename}`, 'success');
  },

  downloadTXT() {
    if (!this.activeData) return;
    const txt = this.buildFormattedText();
    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_solution.txt`;
    this.triggerDownload(txt, filename, 'text/plain');
  },

  downloadMD() {
    if (!this.activeData) return;
    const md = this.buildFormattedMD();
    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_solution.md`;
    this.triggerDownload(md, filename, 'text/markdown');
  },

  downloadJSON() {
    if (!this.activeData) return;
    const payload = {
      module: this.activeModuleName,
      formula: this.getFormula(this.activeModuleName, this.activeData),
      computation_steps: this.activeData.steps,
      result: this.activeData.result || this.activeData.result_display || this.activeData.solution || this.activeData.eigenvalues,
      raw: this.activeData
    };
    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_solution.json`;
    this.triggerDownload(JSON.stringify(payload, null, 2), filename, 'application/json');
  },

  copyToClipboard() {
    if (!this.activeData) return;
    const txt = this.buildFormattedText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(() => {
        if (typeof showToast === 'function') showToast('Copied full solution to clipboard!', 'success');
      }).catch(() => this.fallbackCopy(txt));
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
    const title = this.activeData.operation
      ? `${this.activeModuleName} — ${this.activeData.operation}`
      : this.activeModuleName;

    // Clone the visible combined card for PDF rendering
    const sourceCard = document.getElementById('directSolutionContainer');
    if (!sourceCard) { this.downloadTXT(); return; }

    const pdfDiv = document.createElement('div');
    pdfDiv.id = 'pdfExportContainer';
    pdfDiv.style.cssText = 'padding: 30px; background: #fff; color: #111; font-family: system-ui, -apple-system, sans-serif;';

    // Clone inner HTML but strip the export section
    const clone = sourceCard.cloneNode(true);
    const exportSection = clone.querySelector('.export-section');
    if (exportSection) exportSection.remove();

    pdfDiv.innerHTML = `
      <div style="border-bottom: 3px solid #16a34a; padding-bottom: 12px; margin-bottom: 24px;">
        <h2 style="margin:0 0 4px 0; color:#16a34a; font-size:22px; font-weight:bold;">Linear Algebra Solver</h2>
        <h4 style="margin:0; color:#334155; font-size:15px;">${title}</h4>
        <p style="margin:6px 0 0 0; color:#94a3b8; font-size:11px;">Generated on ${new Date().toLocaleString()}</p>
      </div>
      ${clone.innerHTML}
      <div style="margin-top:30px; border-top:1px solid #e2e8f0; padding-top:10px; text-align:center; color:#94a3b8; font-size:10px;">
        Linear Algebra Solver — Complete Formula, Computation & Result Report
      </div>
    `;

    document.body.appendChild(pdfDiv);
    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_solution.pdf`;

    if (window.html2pdf) {
      if (typeof showToast === 'function') showToast('Generating PDF…', 'info');
      html2pdf().set({
        margin: [10, 10, 10, 10],
        filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, logging: false, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }).from(pdfDiv).save().then(() => {
        document.body.removeChild(pdfDiv);
        if (typeof showToast === 'function') showToast(`Downloaded ${filename}`, 'success');
      }).catch(err => {
        console.error('PDF error:', err);
        document.body.removeChild(pdfDiv);
        this.downloadTXT();
      });
    } else {
      document.body.removeChild(pdfDiv);
      this.downloadTXT();
    }
  }
};
