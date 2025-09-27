# @title Generate Parameters (YAML file & Run Config)
# Colab HTML UI -> Python File Savers
from IPython.display import HTML, display
import yaml
from google.colab import output
import os
import re

# Ensure the directory exists before changing into it
if not os.path.exists("/content/boltz_data/"):
    os.makedirs("/content/boltz_data/")
os.chdir("/content/boltz_data/")

# --- START: Custom YAML Formatting (No changes needed here) ---
class IdList(list): pass

def represent_id_list(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

def str_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

class MyDumper(yaml.SafeDumper):
    pass

class QuotedString(str): pass

def quoted_str_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

MyDumper.add_representer(QuotedString, quoted_str_presenter)
MyDumper.add_representer(IdList, represent_id_list)
MyDumper.add_representer(str, str_presenter)
# --- END: Custom YAML Formatting ---

def _save_params(data):
    if not isinstance(data, dict) or 'sequences' not in data:
        return {'status': 'error', 'message': 'Invalid data structure: "sequences" key missing.'}

    sequences_fixed = []
    for entry in data['sequences']:
        if 'protein' in entry:
            ids = IdList([i.upper().replace(' ', '') for i in entry['protein'].get('id', [])])
            seq = re.sub(r'\s+', '', entry['protein'].get('sequence', '').upper())
            protein_dict = {'id': ids, 'sequence': seq}
            sequences_fixed.append({'protein': protein_dict})
        elif 'ligand' in entry:
            ids = IdList([i.upper().replace(' ', '') for i in entry['ligand'].get('id', [])])
            ligand_dict = {'id': ids}
            if 'ccd' in entry['ligand']:
                ligand_dict['ccd'] = entry['ligand']['ccd'].upper().replace(' ', '')
            if 'smiles' in entry['ligand']:
                smiles_val = entry['ligand']['smiles'].replace(' ', '')
                ligand_dict['smiles'] = QuotedString(smiles_val)
            sequences_fixed.append({'ligand': ligand_dict})

    # Reconstruct the final dictionary to be dumped in the desired order
    final_yaml_data = {'version': 1}
    final_yaml_data['sequences'] = sequences_fixed # Add sequences first
    if 'properties' in data:
        final_yaml_data['properties'] = data['properties'] # Add properties last

    filename = "params.yaml"
    try:
        with open(filename, 'w') as f:
            yaml.dump(
                final_yaml_data,
                f, Dumper=MyDumper, sort_keys=False, default_flow_style=False, indent=2
            )
        return {'status': 'ok', 'filename': filename}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def _save_run_params(data):
    try:
        filename = data.get('filename', 'run_params.txt')
        content = data.get('content', '')
        with open(filename, 'w') as f:
            f.write(content)
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

output.register_callback('save_params', _save_params)
output.register_callback('save_run_params', _save_run_params)

# HTML + JS with a Revamped UI and a second page
html = r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
<style>
    /* --- 1. THEME & GLOBAL STYLES --- */
    :root {
        --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        --primary-color: #3b82f6; --primary-hover: #2563eb;
        --danger-color: #ef4444; --danger-hover: #dc2626;
        --secondary-color: #6b7280; --secondary-hover: #4b5563;
        --success-color: #22c55e; --success-hover: #16a34a;
        --bg-light: #f9fafb; --border-color: #d1d5db;
        --text-dark: #1f2937; --text-light: #4b5563;
        --radius: 8px; --shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

    /* --- 2. LAYOUT & TYPOGRAPHY --- */
    .container { font-family: var(--font-family); color: var(--text-dark); background: #fff; padding: 24px; }
    .block {
        border: 1px solid var(--border-color); padding: 20px; margin: 16px 0; border-radius: var(--radius);
        background: #fff; box-shadow: var(--shadow); animation: fadeIn 0.4s ease-out; border-top: 4px solid var(--primary-color);
    }
    .block[data-type="ligand"] { border-top-color: #a855f7; }
    .block-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
    .title { font-weight: 600; font-size: 1.1em; color: var(--text-dark); display:flex; align-items:center; gap: 8px; }
    .row { display:flex; gap:25px; align-items:center; margin-bottom:20px; }
    .row label { width: 150px; color: var(--text-light); font-size: 0.9em; flex-shrink: 0; display: flex; align-items: center; justify-content: space-between; }
    input[type="checkbox"] { width: auto; flex: 0; height: 16px; width: 16px; cursor: pointer; }
    details { border: 1px solid var(--border-color); border-radius: var(--radius); padding: 12px; margin-top: 20px; }
    summary { font-weight: 500; cursor: pointer; }

    /* --- 3. FORMS & BUTTONS --- */
    input[type="text"], input[type="number"], textarea, select {
        flex: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px;
        font-size: 14px; color: var(--text-dark); background: var(--bg-light); transition: border-color 0.2s, box-shadow 0.2s;
    }
    input[type="text"]:focus, input[type="number"]:focus, textarea:focus, select:focus {
        outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
    }
    .btn {
        display: inline-flex; align-items: center; gap: 6px; border: none; padding: 8px 16px;
        border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;
        transition: background-color 0.2s, transform 0.1s;
    }
    .btn:active { transform: scale(0.98); }
    .btn.primary { background: var(--primary-color); color: #fff; }
    .btn.primary:hover { background: var(--primary-hover); }
    .btn.secondary { background: var(--secondary-color); color: #fff; }
    .btn.secondary:hover { background: var(--secondary-hover); }
    .btn.success { background: var(--success-color); color: #fff; }
    .btn.success:hover { background: var(--success-hover); }
    .remove-btn {background: transparent; color: var(--secondary-color); border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 1em; transition: background-color 0.2s, color 0.2s;}
    .remove-btn:hover {background-color: #fee2e2; color: var(--danger-color);}

    /* --- 4. TOOLTIPS --- */
    .tooltip-icon {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #ccc;
        border: 1px solid #ccc;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        font-size: 12px;
        line-height: 14px;
        text-align: center;
        font-style: normal;
    }
    .tooltip-icon .tooltip-text {
        visibility: hidden;
        width: 220px;
        background-color: #333;
        color: #fff;
        text-align: left;
        font-size: 0.8em;
        font-weight: 400;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 10;
        bottom: 50%;
        left: 120%;
        transform: translateY(50%);
        opacity: 0;
        transition: opacity 0.3s;
        box-shadow: var(--shadow);
    }
    .tooltip-icon:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }


    /* --- 5. CONTROLS & STATUS --- */
    .controls { margin-top: 24px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
    .status-message {
        display: flex; align-items: center; gap: 8px; padding: 8px 12px;
        border-radius: 6px; font-size: 0.9em; animation: fadeIn 0.3s;
    }
    .status-message.success { background-color: #dcfce7; color: #166534; }
    .status-message.error { background-color: #fee2e2; color: #991b1b; }
    .status-message.warning { background-color: #fef3c7; color: #92400e; }
</style>

<div class="container">
    <div id="main_params_container">
        <div id="sequences_container"></div>
        <div id="affinity_prediction_container"></div>
        <div class="controls">
            <button class="btn primary" onclick="addProtein()"><i class="fa-solid fa-dna"></i> Add Protein</button>
            <button class="btn primary" style="background-color:#a855f7;" onclick="addLigand()"><i class="fa-solid fa-puzzle-piece"></i> Add Ligand</button>
            <button class="btn secondary" onclick="clearAll()"><i class="fa-solid fa-broom"></i> Clear Added</button>
            <button class="btn secondary" id="saveBtn" onclick="saveYaml()"><i id="saveIcon" class="fa-solid fa-save"></i> <span id="saveBtnText">Save YAML</span></button>
            <button class="btn success" id="nextBtn" onclick="showRunParams()" style="display:none;"><span id="nextBtnText">Next</span> <i class="fa-solid fa-arrow-right"></i></button>
            <div id="status"></div>
        </div>
    </div>

    <div id="run_params_container" style="display:none;">
      <div class="block">
          <div class="title" style="margin-bottom: 20px;"><i class="fa-solid fa-gears"></i> Run Parameters</div>
          <div class="row">
            <label for="rp_job_name">Job Name</label>
            <input type="text" id="rp_job_name" value="" placeholder="Insulin_Peptide" required>
          </div>
          <div class="row">
            <label for="rp_use_potentials">Use Potentials <i class="tooltip-icon">?<span class="tooltip-text">Enable the use of pre-computed potentials to guide the generation process.</span></i></label>
            <input type="checkbox" id="rp_use_potentials" checked>
          </div>
          <div class="row">
            <label for="rp_override">Override <i class="tooltip-icon">?<span class="tooltip-text">If a file with the same job name already exists, this option will overwrite it.</span></i></label>
            <input type="checkbox" id="rp_override" checked>
          </div>

          <details>
              <summary>Advanced Options</summary>
              <div style="padding-top: 20px;">
                  <div class="row">
                    <label for="rp_recycling_steps">Recycling Steps <i class="tooltip-icon">?<span class="tooltip-text">Number of times to recycle the output structure back into the model for refinement.</span></i></label>
                    <input type="number" id="rp_recycling_steps" value="3" step="1" min="1">
                  </div>
                  <div class="row">
                      <label for="rp_sampling_steps">Sampling Steps <i class="tooltip-icon">?<span class="tooltip-text">Number of steps in the diffusion process. More steps can lead to higher quality but take longer.</span></i></label>
                      <input type="range" id="rp_sampling_steps" min="50" max="400" step="50" value="200" oninput="this.nextElementSibling.value = this.value">
                      <output>200</output>
                  </div>
                  <div class="row">
                    <label for="rp_diffusion_samples">Diffusion Samples <i class="tooltip-icon">?<span class="tooltip-text">Number of independent structures to generate.</span></i></label>
                    <input type="number" id="rp_diffusion_samples" value="1" step="1" min="1">
                  </div>
                  <div class="row">
                    <label for="rp_step_scale">Step Scale <i class="tooltip-icon">?<span class="tooltip-text">Controls the noise schedule during diffusion. Higher values can sometimes improve structure quality.</span></i></label>
                    <input type="number" id="rp_step_scale" value="1.638" step="0.1" min="0.1">
                  </div>
                  <div class="row">
                      <label for="rp_max_msa_seqs">Max MSA Sequences<i class="tooltip-icon">?<span class="tooltip-text">The maximum number of sequences to use from the Multiple Sequence Alignment (MSA).</span></i></label>
                      <select id="rp_max_msa_seqs">
                          <option>32</option><option>64</option><option>128</option><option>256</option><option>512</option>
                          <option>1024</option><option>2048</option><option>4096</option><option selected>8192</option>
                      </select>
                  </div>
                  <div class="row">
                    <label for="rp_subsample_msa">Subsample MSA <i class="tooltip-icon">?<span class="tooltip-text">If enabled, a smaller, random subset of the MSA will be used.</span></i></label>
                    <input type="checkbox" id="rp_subsample_msa" onchange="toggleNumSubsampled(this)">
                  </div>
                   <div class="row" id="num_subsampled_msa_row" style="display:none;">
                      <label for="rp_num_subsampled_msa">Number of Subsampled MSA <i class="tooltip-icon">?<span class="tooltip-text">The number of sequences to use when subsampling the MSA.</span></i></label>
                      <select id="rp_num_subsampled_msa">
                          <option>4</option><option>8</option><option>16</option><option>32</option><option>64</option>
                          <option>128</option><option>256</option><option>512</option><option selected>1024</option>
                      </select>
                  </div>
                  <div class="row">
                      <label for="rp_msa_pairing_strategy">MSA Pairing Strategy <i class="tooltip-icon">?<span class="tooltip-text">Strategy for pairing sequences in the MSA. 'greedy' is faster, 'complete' can be more thorough.</span></i></label>
                      <select id="rp_msa_pairing_strategy">
                          <option>greedy</option><option>complete</option>
                      </select>
                  </div>
              </div>
          </details>
      </div>
      <div class="controls">
          <button class="btn secondary" onclick="showMainParams()"><i class="fa-solid fa-arrow-left"></i> Back</button>
          <button class="btn success" onclick="saveRunParams()"><i class="fa-solid fa-check"></i> OK</button>
          <div id="run_status"></div>
      </div>
    </div>

    <template id="first_protein_template">
        <div class="block seq-block first-protein" data-type="protein">
          <div class="block-header"><div class="title"><i class="fa-solid fa-dna"></i>Protein (Primary)</div></div>
          <div class="row"><label>IDs (comma):</label><input class="p-ids" type="text" placeholder="A,B" oninput="formatIDs(this)"/></div>
          <div class="row"><label>Sequence:</label><textarea class="p-seq" rows="5" style="text-transform: uppercase;"></textarea></div>
        </div>
    </template>

    <template id="protein_template">
        <div class="block seq-block" data-type="protein">
          <div class="block-header">
            <div class="title"><i class="fa-solid fa-dna"></i>Protein</div>
            <button class="remove-btn" onclick="removeBlock(this)" title="Remove block"><i class="fa-solid fa-trash-can"></i></button>
          </div>
          <div class="row"><label>IDs (comma):</label><input class="p-ids" type="text" placeholder="C,D" oninput="formatIDs(this)"/></div>
          <div class="row"><label>Sequence:</label><textarea class="p-seq" rows="5" style="text-transform: uppercase;"></textarea></div>
        </div>
    </template>

    <template id="ligand_template">
        <div class="block seq-block" data-type="ligand">
          <div class="block-header">
            <div class="title"><i class="fa-solid fa-puzzle-piece"></i>Ligand</div>
            <button class="remove-btn" onclick="removeBlock(this)" title="Remove block"><i class="fa-solid fa-trash-can"></i></button>
          </div>
          <div class="row"><label>IDs (comma):</label><input class="l-ids" type="text" placeholder="E,F" oninput="formatIDs(this); updateLigandChainSelector();"/></div>
          <div class="row"><label>Type:</label>
            <select class="l-type" onchange="onLigandTypeChange(this)">
              <option value="ccd">CCD</option><option value="smiles">SMILES</option>
            </select>
          </div>
          <div class="row lig-value-row"><label>Value:</label><input class="l-value" style="text-transform: uppercase;" type="text" placeholder="e.g., SAH" /></div>
        </div>
    </template>
</div>

<script>
  const container = document.getElementById('sequences_container');

  function showRunParams() {
      document.getElementById('main_params_container').style.display = 'none';
      document.getElementById('run_params_container').style.display = 'block';
  }
  function showMainParams() {
      document.getElementById('run_params_container').style.display = 'none';
      document.getElementById('main_params_container').style.display = 'block';
      document.getElementById('run_status').innerHTML = '';
  }
  function toggleNumSubsampled(checkbox) {
      const row = document.getElementById('num_subsampled_msa_row');
      row.style.display = checkbox.checked ? 'flex' : 'none';
  }

  async function saveRunParams() {
      const getVal = id => document.getElementById(id).value;
      const getChecked = id => document.getElementById(id).checked;

      const content = `job_name = "${getVal('rp_job_name')}"
use_potentials = ${getChecked('rp_use_potentials')}
override = ${getChecked('rp_override')}
recycling_steps = ${getVal('rp_recycling_steps')}
sampling_steps = ${getVal('rp_sampling_steps')}
diffusion_samples = ${getVal('rp_diffusion_samples')}
step_scale = ${getVal('rp_step_scale')}
max_msa_seqs = ${getVal('rp_max_msa_seqs')}
subsample_msa = ${getChecked('rp_subsample_msa')}
num_subsampled_msa = ${getVal('rp_num_subsampled_msa')}
msa_pairing_strategy = "${getVal('rp_msa_pairing_strategy')}"`;

      const payload = { filename: 'run_params.txt', content: content.trim() };
      const runStatusEl = document.getElementById('run_status');

      try {
          const result = await google.colab.kernel.invokeFunction('save_run_params', [payload], {});
          if (result && result.status === 'ok') {
              runStatusEl.innerHTML = `<div class="status-message success"><i class="fa-solid fa-check-circle"></i> Parameters saved successfully, you can run BoltzEngine now.</div>`;
          } else {
              runStatusEl.innerHTML = `<div class="status-message error"><i class="fa-solid fa-circle-xmark"></i> <strong>Error:</strong> ${result?.message || 'Unknown error.'}</div>`;
          }
      } catch (err) {
          runStatusEl.innerHTML = `<div class="status-message error"><i class="fa-solid fa-circle-xmark"></i> <strong>Save failed:</strong> ${err.toString()}</div>`;
      }
  }

  function formatIDs(inputElement) {
    const originalValue = inputElement.value;
    const formattedValue = originalValue.replace(/[\s,]+/g, '').split('').join(',');
    inputElement.value = formattedValue.toUpperCase();
  }

  function addBlock(templateId) {
      const tpl = document.getElementById(templateId);
      const node = tpl.content.cloneNode(true);
      container.appendChild(node);
  }

  function addProtein(first=false) { addBlock(first ? 'first_protein_template' : 'protein_template'); }

  function addLigand() {
      addBlock('ligand_template');
      if (!document.getElementById('affinity-prediction-section')) {
          const affinityContainer = document.getElementById('affinity_prediction_container');
          affinityContainer.innerHTML = `
            <div id="affinity-prediction-section" class="block" style="border-top-color: var(--secondary-color); margin-bottom: 0;">
                <div class="row" style="align-items: center; margin-bottom: 12px;">
                    <input type="checkbox" id="predict_affinity_toggle" onchange="toggleAffinityOptions(this)" style="width: auto; flex: 0; height: 16px; width: 16px; cursor: pointer;">
                    <label for="predict_affinity_toggle" style="width: auto; cursor: pointer; color: var(--text-dark); font-weight: 500;">Predict Ligand Affinity</label>
                </div>
                <div id="ligand_chain_selector_container" style="display:none; margin-top: 10px;" class="row">
                    <label for="ligand_chain_id_select">Ligand Chain:</label>
                    <select id="ligand_chain_id_select"></select>
                </div>
            </div>`;
      }
  }

  function toggleAffinityOptions(checkbox) {
      const selectorContainer = document.getElementById('ligand_chain_selector_container');
      if (checkbox.checked) {
          selectorContainer.style.display = 'flex';
          updateLigandChainSelector();
      } else {
          selectorContainer.style.display = 'none';
      }
  }

  function updateLigandChainSelector() {
      const selector = document.getElementById('ligand_chain_id_select');
      if (!selector) return;
      const currentVal = selector.value;
      selector.innerHTML = '';
      const allLigandIDs = new Set();
      document.querySelectorAll('.seq-block[data-type="ligand"] .l-ids').forEach(input => {
          (input.value || '').split(',').map(s => s.trim()).filter(Boolean).forEach(id => allLigandIDs.add(id));
      });

      if (allLigandIDs.size === 0) {
          const option = document.createElement('option');
          option.textContent = 'No ligand IDs defined';
          option.value = '';
          selector.appendChild(option);
      } else {
          allLigandIDs.forEach(id => {
              const option = document.createElement('option');
              option.value = id;
              option.textContent = id;
              selector.appendChild(option);
          });
      }
      if (allLigandIDs.has(currentVal)) { selector.value = currentVal; }
  }

  function removeBlock(btn) {
      btn.closest('.seq-block')?.remove();
      if (document.querySelectorAll('.seq-block[data-type="ligand"]').length === 0) {
          document.getElementById('affinity_prediction_container').innerHTML = '';
      } else {
          updateLigandChainSelector();
      }
  }

  function clearAll() {
      container.querySelectorAll('.seq-block:not(.first-protein)').forEach(el => el.remove());
      const first = container.querySelector('.first-protein');
      if (first) {
          first.querySelectorAll('input, textarea').forEach(el => el.value = '');
      }
      document.getElementById('affinity_prediction_container').innerHTML = '';
      document.getElementById('status').innerHTML = '';
      document.getElementById('nextBtn').style.display = 'none';
  }

  function onLigandTypeChange(select) {
      const valueInput = select.closest('.seq-block').querySelector('.l-value');
      valueInput.placeholder = select.value === 'ccd' ? 'e.g., SAH' : 'e.g., CCO... (SMILES)';
  }

  function setStatus(message, type) {
      const statusEl = document.getElementById('status');
      const icon = { success: 'fa-check-circle', error: 'fa-circle-xmark', warning: 'fa-triangle-exclamation'}[type] || 'fa-circle-info';
      statusEl.innerHTML = `<div class="status-message ${type}"><i class="fa-solid ${icon}"></i> ${message}</div>`;
      document.getElementById('nextBtn').style.display = (type === 'success') ? 'inline-flex' : 'none';
  }

  async function saveYaml() {
      const saveBtn = document.getElementById('saveBtn');
      const saveIcon = document.getElementById('saveIcon');
      const saveBtnText = document.getElementById('saveBtnText');
      setStatus('Validating...', 'warning');
      const sequences = [];
      const blocks = document.querySelectorAll('.seq-block');
      const allIDs = new Set();
      let valid = true;

      for (const [idx, b] of Array.from(blocks).entries()) {
          const type = b.dataset.type;
          let currentIds = [];

          if (type === 'protein') {
              currentIds = (b.querySelector('.p-ids').value || '').split(',').map(s => s.trim()).filter(Boolean);
              const seq = b.querySelector('.p-seq').value.trim();
              if (currentIds.length === 0 || !seq) {
                  valid = false; setStatus(`<strong>Error:</strong> Protein block ${idx + 1} requires both IDs and a Sequence.`, 'error'); break;
              } else {
                  sequences.push({ protein: { id: currentIds, sequence: seq } });
              }
          } else if (type === 'ligand') {
              currentIds = (b.querySelector('.l-ids').value || '').split(',').map(s => s.trim()).filter(Boolean);
              const ltype = b.querySelector('.l-type').value;
              const lvalue = b.querySelector('.l-value').value.trim();
              if (currentIds.length === 0 || !lvalue) {
                  valid = false; setStatus(`<strong>Error:</strong> Ligand block ${idx + 1} requires both IDs and a Value.`, 'error'); break;
              } else {
                  const entry = { id: currentIds };
                  if (ltype === 'ccd') entry.ccd = lvalue; else entry.smiles = lvalue;
                  sequences.push({ ligand: entry });
              }
          }
          for (const id of currentIds) {
              if (allIDs.has(id)) {
                  valid = false; setStatus(`<strong>Error:</strong> Duplicate ID '<strong>${id}</strong>' found in block ${idx + 1}. IDs must be unique.`, 'error'); break;
              }
              allIDs.add(id);
          }
          if (!valid) break;
      }
      if (!valid) return;

      const payload = { sequences: sequences };
      const predictAffinityCheckbox = document.getElementById('predict_affinity_toggle');
      if (predictAffinityCheckbox && predictAffinityCheckbox.checked) {
          const selectedLigandId = document.getElementById('ligand_chain_id_select').value;
          if (selectedLigandId) {
              payload.properties = [{ affinity: { binder: selectedLigandId } }];
          } else {
              setStatus('<strong>Error:</strong> "Predict Ligand Affinity" is checked, but no ligand chain is selected or defined.', 'error'); return;
          }
      }

      saveBtn.disabled = true;
      saveBtnText.innerText = 'Saving...';
      saveIcon.className = 'fa-solid fa-spinner fa-spin';
      try {
          const result = await google.colab.kernel.invokeFunction('save_params', [payload], {});
          if (result && result.status === 'ok') {
              setStatus(`Parameter File Saved Successfully`, 'success');
          } else {
              setStatus(`<strong>Error:</strong> ${result?.message || 'Unknown error occurred.'}`, 'error');
          }
      } catch (err) {
          setStatus(`<strong>Save failed:</strong> ${err.toString()}`, 'error');
      } finally {
          saveBtn.disabled = false;
          saveBtnText.innerText = 'Save YAML';
          saveIcon.className = 'fa-solid fa-save';
      }
  }

  document.getElementById("rp_job_name").addEventListener("input", function() {
    this.value = this.value.replace(/\s+/g, "_");
});

  addProtein(true); // Initialize UI
</script>
"""

display(HTML(html))