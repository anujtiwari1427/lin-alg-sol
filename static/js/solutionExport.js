/* =========================================================
   SOLUTION EXPORTER & COMBINED DETAILED REPORT ENGINE
   Provides options to download linear algebra calculation solutions with all steps.
   Combines: Formula + Full Step-by-Step Computation + Final Result in a single detailed report.
   Formats: PDF (.pdf), Text (.txt), Markdown (.md), JSON (.json), and Clipboard.
   ========================================================= */

const SolutionExporter = {
  activeData: null,
  activeModuleName: 'Linear Algebra Solution',
  activeElementId: null,
  viewMode: 'combined', // 'combined' or 'accordion'

  setSolution(data, moduleName, containerId = 'downloadPanelContainer') {
    this.activeData = data;
    this.activeModuleName = moduleName || 'Linear Algebra Solution';
    this.activeElementId = containerId;

    this.renderCombinedSolutionCard(data, moduleName);
    this.renderDownloadPanel(containerId);
  },

  getFormula(moduleName, data) {
    const op = (data.operation || '').toLowerCase();
    const mod = (moduleName || '').toLowerCase();

    if (mod.includes('matrix')) {
      if (op.includes('add')) return 'C = A + B \\quad \\text{where } c_{ij} = a_{ij} + b_{ij}';
      if (op.includes('sub')) return 'C = A - B \\quad \\text{where } c_{ij} = a_{ij} - b_{ij}';
      if (op.includes('multi')) return 'C_{ij} = \\sum_{k=1}^{n} A_{ik} B_{kj}';
      if (op.includes('scalar')) return 'B = k \\cdot A \\quad \\text{where } b_{ij} = k \\cdot a_{ij}';
      if (op.includes('transpose')) return '(A^T)_{ij} = A_{ji}';
      if (op.includes('trace')) return '\\text{tr}(A) = \\sum_{i=1}^{n} a_{ii}';
      if (op.includes('rank')) return '\\text{rank}(A) = \\text{number of non-zero rows in RREF}(A)';
      return 'C = f(A, B)';
    }
    if (mod.includes('determinant')) {
      return '\\det(A) = \\sum_{j=1}^{n} (-1)^{1+j} a_{1j} \\det(M_{1j})';
    }
    if (mod.includes('inverse')) {
      return 'A^{-1} = \\frac{1}{\\det(A)} \\text{adj}(A) \\quad \\text{or } [A \\mid I] \\xrightarrow{\\text{RREF}} [I \\mid A^{-1}]';
    }
    if (mod.includes('vector')) {
      if (op.includes('dot')) return '\\vec{u} \\cdot \\vec{v} = \\sum_{i=1}^{n} u_i v_i';
      if (op.includes('cross')) return '\\vec{u} \\times \\vec{v} = (u_y v_z - u_z v_y,\\, u_z v_x - u_x v_z,\\, u_x v_y - u_y v_x)';
      if (op.includes('magnitude')) return '||\\vec{v}|| = \\sqrt{\\sum_{i=1}^{n} v_i^2}';
      if (op.includes('unit')) return '\\hat{v} = \\frac{\\vec{v}}{||\\vec{v}||}';
      if (op.includes('add')) return '\\vec{u} + \\vec{v} = (u_1+v_1, u_2+v_2, \\dots, u_n+v_n)';
      if (op.includes('sub')) return '\\vec{u} - \\vec{v} = (u_1-v_1, u_2-v_2, \\dots, u_n-v_n)';
      return '\\vec{r} = f(\\vec{u}, \\vec{v})';
    }
    if (mod.includes('linear')) {
      return 'A \\mathbf{x} = \\mathbf{b} \\implies \\mathbf{x} = A^{-1} \\mathbf{b} \\quad \\text{or via Gaussian Elimination } [A \\mid \\mathbf{b}]';
    }
    if (mod.includes('eigen')) {
      return '\\det(A - \\lambda I) = 0 \\quad \\text{and } (A - \\lambda I) \\mathbf{v} = \\mathbf{0}';
    }
    return '';
  },

  renderCombinedSolutionCard(data, moduleName) {
    let combinedCard = document.getElementById('combinedSolutionContainer');
    const accordion = document.getElementById('stepsAccordion');

    if (!combinedCard && accordion) {
      combinedCard = document.createElement('div');
      combinedCard.id = 'combinedSolutionContainer';
      combinedCard.className = 'mt-3 mb-4';
      accordion.parentNode.insertBefore(combinedCard, accordion);
    }

    if (!combinedCard) return;

    const formula = this.getFormula(moduleName, data);
    const title = data.operation ? `${moduleName} — ${data.operation}` : moduleName;

    // Build combined computation HTML from all steps
    let stepsCombinedHtml = '';
    if (data.steps && data.steps.length > 0) {
      stepsCombinedHtml = data.steps.map((step, idx) => `
        <div class="combined-step-block mb-3 p-3 rounded">
          <div class="fw-bold text-primary-accent mb-1"><i class="fas fa-check-circle me-2"></i>${step.title}</div>
          ${step.text ? `<p class="mb-2 text-secondary small">${step.text}</p>` : ''}
          ${step.list ? `<ul class="small font-monospace mb-2 text-light">${step.list.map(l => `<li>${l}</li>`).join('')}</ul>` : ''}
          ${step.latex ? `<div class="step-latex text-center my-2">\\[ ${step.latex} \\]</div>` : ''}
        </div>
      `).join('');
    }

    // Build result HTML
    let resultHtml = '';
    if (data.result_latex) {
      resultHtml = `\\[ ${data.result_latex} \\]`;
    } else if (data.result_display) {
      resultHtml = `<div class="fs-4 fw-bold font-monospace">${JSON.stringify(data.result_display)}</div>`;
    }

    combinedCard.innerHTML = `
      <div class="combined-single-card p-3 p-md-4">
        <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3 border-bottom border-secondary-subtle pb-2">
          <h5 class="fw-bold mb-0 text-success"><i class="fas fa-file-contract me-2"></i>Combined Detailed Solution Report</h5>
          <div class="d-flex gap-2 align-items-center">
            <button type="button" class="btn btn-sm btn-success" id="btnModeCombined" onclick="SolutionExporter.toggleViewMode('combined')">
              <i class="fas fa-align-left me-1"></i>Combined View
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" id="btnModeAccordion" onclick="SolutionExporter.toggleViewMode('accordion')">
              <i class="fas fa-list-ol me-1"></i>Accordion View
            </button>
          </div>
        </div>

        <div id="combinedViewBody">
          <!-- 1. FORMULA SECTION -->
          <div class="combined-part mb-4">
            <div class="part-header text-info fw-bold small text-uppercase mb-2"><i class="fas fa-square-root-variable me-2"></i>1. Governing Formula & Method</div>
            <div class="formula-box p-3 rounded text-center border border-info-subtle">
              ${formula ? `\\[ ${formula} \\]` : `<span class="text-muted">${title}</span>`}
            </div>
          </div>

          <!-- 2. COMPUTATION SECTION -->
          <div class="combined-part mb-4">
            <div class="part-header text-warning fw-bold small text-uppercase mb-2"><i class="fas fa-calculator me-2"></i>2. Complete Step-by-Step Computation</div>
            <div class="computation-sequence">
              ${stepsCombinedHtml || '<p class="text-muted small">No computation steps available.</p>'}
            </div>
          </div>

          <!-- 3. RESULT SECTION -->
          <div class="combined-part">
            <div class="part-header text-success fw-bold small text-uppercase mb-2"><i class="fas fa-check-double me-2"></i>3. Final Calculated Result</div>
            <div class="result-box p-3 rounded text-center border border-success-subtle bg-success-subtle">
              ${resultHtml}
            </div>
          </div>
        </div>
      </div>
    `;

    if (window.MathJax && window.MathJax.typeset) {
      window.MathJax.typeset();
    }
  },

  toggleViewMode(mode) {
    this.viewMode = mode;
    const combinedBody = document.getElementById('combinedViewBody');
    const accordion = document.getElementById('stepsAccordion');
    const btnCombined = document.getElementById('btnModeCombined');
    const btnAccordion = document.getElementById('btnModeAccordion');

    if (mode === 'combined') {
      if (combinedBody) combinedBody.style.display = 'block';
      if (accordion) accordion.style.display = 'none';
      if (btnCombined) { btnCombined.className = 'btn btn-sm btn-success'; }
      if (btnAccordion) { btnAccordion.className = 'btn btn-sm btn-outline-secondary'; }
    } else {
      if (combinedBody) combinedBody.style.display = 'none';
      if (accordion) accordion.style.display = 'block';
      if (btnCombined) { btnCombined.className = 'btn btn-sm btn-outline-secondary'; }
      if (btnAccordion) { btnAccordion.className = 'btn btn-sm btn-success'; }
    }
  },

  renderDownloadPanel(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <div class="download-options-card p-3 p-md-4 mt-4">
        <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
          <div class="d-flex align-items-center gap-2">
            <div class="download-icon-box">
              <i class="fas fa-file-export"></i>
            </div>
            <div>
              <h6 class="fw-bold mb-0 text-primary-accent">Download Combined Solution Report</h6>
              <p class="small text-secondary mb-0">Download formula, full computation & result in a single detailed file</p>
            </div>
          </div>
          <span class="badge bg-secondary-custom text-uppercase small px-2 py-1"><i class="fas fa-layer-group me-1"></i>Multi-Format</span>
        </div>

        <div class="row g-2">
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadPDF()">
              <i class="fas fa-file-pdf text-danger"></i>
              <span>PDF Document</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadTXT()">
              <i class="fas fa-file-lines text-info"></i>
              <span>Text File</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadMD()">
              <i class="fab fa-markdown text-warning"></i>
              <span>Markdown</span>
            </button>
          </div>
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-export w-100" onclick="SolutionExporter.downloadJSON()">
              <i class="fas fa-file-code text-success"></i>
              <span>JSON Data</span>
            </button>
          </div>
        </div>

        <div class="mt-3 pt-2 border-top border-secondary-subtle d-flex justify-content-end">
          <button type="button" class="btn btn-sm btn-secondary-custom" onclick="SolutionExporter.copyToClipboard()">
            <i class="fas fa-copy me-1"></i>Copy Combined Detailed Solution
          </button>
        </div>
      </div>
    `;
  },

  buildFormattedText() {
    if (!this.activeData) return '';
    const d = this.activeData;
    const title = d.operation ? `${this.activeModuleName} — ${d.operation}` : this.activeModuleName;
    const dateStr = new Date().toLocaleString();
    const formula = this.getFormula(this.activeModuleName, d);

    let txt = `=========================================================\n`;
    txt += `COMBINED DETAILED SOLUTION REPORT\n`;
    txt += `${title.toUpperCase()}\n`;
    txt += `Generated: ${dateStr}\n`;
    txt += `=========================================================\n\n`;

    txt += `[1] GOVERNING FORMULA & METHOD\n`;
    txt += `${'-'.repeat(40)}\n`;
    txt += formula ? `Formula: ${formula}\n\n` : `${title}\n\n`;

    txt += `[2] DETAILED STEP-BY-STEP COMPUTATION\n`;
    txt += `${'-'.repeat(40)}\n`;
    if (d.steps && d.steps.length > 0) {
      d.steps.forEach((step, idx) => {
        txt += `Step ${idx + 1}: ${step.title}\n`;
        if (step.text) txt += `  ${step.text}\n`;
        if (step.list && step.list.length > 0) {
          step.list.forEach(item => {
            txt += `    • ${item.replace(/<[^>]*>?/gm, '')}\n`;
          });
        }
        if (step.latex) {
          txt += `    Formula: ${step.latex}\n`;
        }
        txt += `\n`;
      });
    }

    txt += `[3] FINAL CALCULATED RESULT\n`;
    txt += `${'-'.repeat(40)}\n`;
    if (d.result_display) {
      if (Array.isArray(d.result_display)) {
        txt += d.result_display.map(row => `[ ${row.join(', ')} ]`).join('\n') + '\n';
      } else {
        txt += `${d.result_display}\n`;
      }
    } else if (d.result !== undefined) {
      txt += `${d.result}\n`;
    }
    if (d.result_latex) {
      txt += `LaTeX: ${d.result_latex}\n`;
    }

    const solObj = d.solution || d.solutions;
    if (solObj) {
      txt += `Solution Values:\n`;
      Object.entries(solObj).forEach(([k, v]) => {
        txt += `  ${k} = ${v}\n`;
      });
      txt += `\n`;
    }

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      txt += `Eigenpairs:\n`;
      d.eigenvalues.forEach((val, idx) => {
        const vec = d.eigenvectors && d.eigenvectors[idx] ? d.eigenvectors[idx].join(', ') : '';
        txt += `  λ${idx + 1} = ${val},  v${idx + 1} = [${vec}]ᵀ\n`;
      });
      txt += `\n`;
    }

    txt += `=========================================================\n`;
    txt += `Linear Algebra Solver — Combined Detailed Engine\n`;
    return txt;
  },

  buildFormattedMD() {
    if (!this.activeData) return '';
    const d = this.activeData;
    const title = d.operation ? `${this.activeModuleName}: ${d.operation}` : this.activeModuleName;
    const dateStr = new Date().toLocaleString();
    const formula = this.getFormula(this.activeModuleName, d);

    let md = `# Combined Detailed Solution Report: ${title}\n\n`;
    md += `*Generated on ${dateStr}*\n\n`;
    md += `---\n\n`;

    md += `## 1. Governing Formula & Method\n\n`;
    if (formula) {
      md += `$$\n${formula}\n$$\n\n`;
    } else {
      md += `*${title}*\n\n`;
    }

    md += `## 2. Complete Step-by-Step Computation\n\n`;
    if (d.steps && d.steps.length > 0) {
      d.steps.forEach((step, idx) => {
        md += `### Step ${idx + 1}: ${step.title}\n\n`;
        if (step.text) md += `${step.text}\n\n`;
        if (step.list && step.list.length > 0) {
          step.list.forEach(item => {
            md += `- ${item}\n`;
          });
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
      Object.entries(solObjMd).forEach(([k, v]) => {
        md += `- **${k}**: \`${v}\`\n`;
      });
      md += `\n`;
    }

    if (d.eigenvalues && Array.isArray(d.eigenvalues)) {
      md += `### Eigenpairs\n`;
      d.eigenvalues.forEach((val, idx) => {
        const vec = d.eigenvectors && d.eigenvectors[idx] ? d.eigenvectors[idx].join(', ') : '';
        md += `- **$\\lambda_${idx + 1}$**: \`${val}\`, **$v_${idx + 1}$**: \`[${vec}]ᵀ\`\n`;
      });
      md += `\n`;
    }

    return md;
  },

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
    if (typeof showToast === 'function') {
      showToast(`Downloaded ${filename}`, 'success');
    }
  },

  downloadTXT() {
    if (!this.activeData) return;
    const txt = this.buildFormattedText();
    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_combined_solution.txt`;
    this.triggerDownload(txt, filename, 'text/plain');
  },

  downloadMD() {
    if (!this.activeData) return;
    const md = this.buildFormattedMD();
    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_combined_solution.md`;
    this.triggerDownload(md, filename, 'text/markdown');
  },

  downloadJSON() {
    if (!this.activeData) return;
    const jsonPayload = {
      module: this.activeModuleName,
      formula: this.getFormula(this.activeModuleName, this.activeData),
      computation_steps: this.activeData.steps,
      result: this.activeData.result || this.activeData.result_display || this.activeData.solution || this.activeData.eigenvalues,
      raw: this.activeData
    };
    const jsonStr = JSON.stringify(jsonPayload, null, 2);
    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_combined_solution.json`;
    this.triggerDownload(jsonStr, filename, 'application/json');
  },

  copyToClipboard() {
    if (!this.activeData) return;
    const txt = this.buildFormattedText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(() => {
        if (typeof showToast === 'function') showToast('Copied combined solution report to clipboard!', 'success');
      }).catch(() => {
        this.fallbackCopy(txt);
      });
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
    if (typeof showToast === 'function') showToast('Copied combined solution report to clipboard!', 'success');
  },

  downloadPDF() {
    if (!this.activeData) return;

    // Create temporary print container with high quality styling for PDF rendering
    const pdfDiv = document.createElement('div');
    pdfDiv.id = 'pdfExportContainer';
    pdfDiv.style.cssText = 'padding: 30px; background: #ffffff; color: #111111; font-family: system-ui, -apple-system, sans-serif;';

    const title = this.activeData.operation ? `${this.activeModuleName} — ${this.activeData.operation}` : this.activeModuleName;
    const formula = this.getFormula(this.activeModuleName, this.activeData);

    const combinedBody = document.getElementById('combinedViewBody');
    const combinedHtml = combinedBody ? combinedBody.innerHTML : '';

    pdfDiv.innerHTML = `
      <div style="border-bottom: 2px solid #16a34a; padding-bottom: 12px; margin-bottom: 20px;">
        <h2 style="margin: 0 0 6px 0; color: #16a34a; font-size: 24px; font-weight: bold;">Linear Algebra Solver</h2>
        <h4 style="margin: 0; color: #334155; font-size: 16px; font-weight: 600;">Combined Solution Report: ${title}</h4>
        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">Generated on ${new Date().toLocaleString()}</p>
      </div>

      ${combinedHtml ? `<div style="color: #0f172a;">${combinedHtml}</div>` : ''}

      <div style="margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; text-align: center; color: #94a3b8; font-size: 11px;">
        Linear Algebra Solver — Formula, Computation & Result Combined Report
      </div>
    `;

    document.body.appendChild(pdfDiv);

    const filename = `${this.activeModuleName.toLowerCase().replace(/\s+/g, '_')}_combined_solution.pdf`;

    if (window.html2pdf) {
      const opt = {
        margin: [10, 10, 10, 10],
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, logging: false, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };

      if (typeof showToast === 'function') showToast('Generating PDF combined report...', 'info');

      html2pdf().set(opt).from(pdfDiv).save().then(() => {
        document.body.removeChild(pdfDiv);
        if (typeof showToast === 'function') showToast(`Downloaded ${filename}`, 'success');
      }).catch(err => {
        console.error('PDF export error:', err);
        document.body.removeChild(pdfDiv);
        this.downloadTXT();
      });
    } else {
      document.body.removeChild(pdfDiv);
      this.downloadTXT();
    }
  }
};
