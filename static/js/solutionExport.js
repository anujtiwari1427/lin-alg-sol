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

  // ─── Main render: insert formula header + export panel (steps already rendered by module) ─────
  renderDirectSolution(data, moduleName) {
    const accordion = document.getElementById('stepsAccordion');
    const downloadPanel = document.getElementById('downloadPanelContainer');

    const formula = this.getFormula(moduleName, data);

    // ── 1. Insert formula box BEFORE the stepsAccordion ────────────────
    let formulaBox = document.getElementById('solutionFormulaBox');
    if (!formulaBox && accordion) {
      formulaBox = document.createElement('div');
      formulaBox.id = 'solutionFormulaBox';
      accordion.parentNode.insertBefore(formulaBox, accordion);
    }
    if (formulaBox && formula) {
      formulaBox.innerHTML = `
        <div class="combined-single-card p-3 mb-3">
          <div class="section-label text-info mb-2"><i class="fas fa-square-root-variable me-2"></i>Governing Formula & Method</div>
          <div class="formula-box p-3 rounded-3 text-center border border-info-subtle">
            \\[ ${formula} \\]
          </div>
        </div>
      `;
    }

    // ── 2. Render export panel into #downloadPanelContainer ────────────
    if (!downloadPanel) return;
    downloadPanel.innerHTML = `
      <div class="combined-single-card p-3 p-md-4 mt-3">
        <div class="d-flex align-items-center gap-2 mb-3">
          <div class="download-icon-box"><i class="fas fa-file-export"></i></div>
          <div>
            <h6 class="fw-bold mb-0 text-primary-accent">Export Full Detailed Solution</h6>
            <p class="small text-secondary mb-0">Download formula, all computation steps &amp; result</p>
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
    const d = this.activeData;
    const title = d.operation ? `${this.activeModuleName} — ${d.operation}` : this.activeModuleName;
    const formula = this.getFormula(this.activeModuleName, d);

    // Build step HTML for PDF
    let stepsHtml = '';
    if (d.steps && d.steps.length > 0) {
      stepsHtml = d.steps.map((step, idx) => `
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:10px;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <span style="width:22px; height:22px; border-radius:50%; background:#16a34a; color:#fff; font-weight:bold; font-size:11px; display:inline-flex; align-items:center; justify-content:center;">${idx + 1}</span>
            <strong>${step.title}</strong>
          </div>
          ${step.text ? `<p style="margin:4px 0 4px 30px; font-size:13px; color:#475569;">${step.text}</p>` : ''}
          ${step.list ? `<ul style="margin:4px 0 4px 30px; font-size:12px;">${step.list.map(l => `<li>${l.replace(/<[^>]*>?/gm, '')}</li>`).join('')}</ul>` : ''}
          ${step.latex ? `<div style="margin:6px 0 0 30px; font-family:monospace; font-size:12px; color:#1e40af;">${step.latex}</div>` : ''}
        </div>
      `).join('');
    }

    // Build result
    let resultHtml = '';
    if (d.result_display) {
      resultHtml = Array.isArray(d.result_display)
        ? d.result_display.map(row => `[ ${row.join(', ')} ]`).join('<br>')
        : `${d.result_display}`;
    } else if (d.result !== undefined) {
      resultHtml = `${d.result}`;
    }
    const solObj = d.solution || d.solutions;
    if (solObj) {
      resultHtml += Object.entries(solObj).map(([k, v]) => `<strong>${k}</strong> = ${v}`).join(',  ');
    }
    if (d.eigenvalues) {
      resultHtml += d.eigenvalues.map((val, i) => {
        const vec = d.eigenvectors && d.eigenvectors[i] ? d.eigenvectors[i].join(', ') : '';
        return `λ${i+1} = ${val},  v${i+1} = [${vec}]ᵀ`;
      }).join('<br>');
    }

    const pdfDiv = document.createElement('div');
    pdfDiv.id = 'pdfExportContainer';
    pdfDiv.style.cssText = 'padding:30px; background:#fff; color:#111; font-family:system-ui,-apple-system,sans-serif;';
    pdfDiv.innerHTML = `
      <div style="border-bottom:3px solid #16a34a; padding-bottom:12px; margin-bottom:20px;">
        <h2 style="margin:0 0 4px 0; color:#16a34a; font-size:22px; font-weight:bold;">Linear Algebra Solver</h2>
        <h4 style="margin:0; color:#334155; font-size:15px;">${title}</h4>
        <p style="margin:6px 0 0; color:#94a3b8; font-size:11px;">Generated on ${new Date().toLocaleString()}</p>
      </div>

      ${formula ? `
      <div style="margin-bottom:20px;">
        <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:#0891b2; margin-bottom:6px;">1. Governing Formula & Method</div>
        <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px; padding:10px; font-family:monospace; font-size:13px; text-align:center;">${formula}</div>
      </div>` : ''}

      <div style="margin-bottom:20px;">
        <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:#d97706; margin-bottom:6px;">2. Step-by-Step Computation</div>
        ${stepsHtml || '<p style="color:#94a3b8; font-size:13px; font-style:italic;">No steps available.</p>'}
      </div>

      ${resultHtml ? `
      <div style="margin-bottom:20px;">
        <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:#16a34a; margin-bottom:6px;">3. Final Result</div>
        <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:14px; text-align:center; font-size:16px; font-weight:bold;">${resultHtml}</div>
      </div>` : ''}

      <div style="margin-top:30px; border-top:1px solid #e2e8f0; padding-top:10px; text-align:center; color:#94a3b8; font-size:10px;">
        Linear Algebra Solver — Complete Formula, Computation &amp; Result Report
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
