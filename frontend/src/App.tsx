import { useState, useEffect } from 'react';
import MonacoEditor from '@monaco-editor/react';
import { Play, ShieldAlert, Cpu, Layers, FileDown, FileCode } from 'lucide-react';

import { compileCode, getHardwareProfiles } from './api';
import type { CompileResponse, HardwareProfile } from './types';
import { TokensView } from './components/TokensView';
import { ASTView } from './components/ASTView';
import { IRView } from './components/IRView';
import { OptimizationLog } from './components/OptimizationLog';
import { AssemblyView } from './components/AssemblyView';
import { MetricsPanel } from './components/MetricsPanel';
import { CFGView } from './components/CFGView';
import { AssemblyDiffView } from './components/AssemblyDiffView';
import { TimingsPanel } from './components/TimingsPanel';

const INITIAL_CODE = `int main() {
    int a = 10;
    int b = a + 5;
    int c = b * 2;
    int d = 100 * 2;
    
    // Dead code check
    int dead_var = 50;
    
    return c + d;
}`;

export default function App() {
  const [code, setCode] = useState(INITIAL_CODE);
  const [hardware, setHardware] = useState<HardwareProfile[]>([]);
  const [selectedTarget, setSelectedTarget] = useState('arm_cortex_m4');
  const [activeTab, setActiveTab] = useState<'tokens' | 'ast' | 'ir' | 'log' | 'assembly' | 'metrics' | 'cfg' | 'diff' | 'timings'>('metrics');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompileResponse | null>(null);

  // Optimization passes activation toggles
  const [passes, setPasses] = useState({
    constant_folding: true,
    constant_propagation: true,
    dead_code: true,
    cse: true,
    algebraic: true,
    strength_reduction: true,
    loop_optimization: true
  });

  useEffect(() => {
    getHardwareProfiles()
      .then(setHardware)
      .catch(console.error);
  }, []);

  const handleCompile = async () => {
    setLoading(true);
    try {
      const data = await compileCode(code, selectedTarget, passes);
      setResult(data);
      if (data.success) {
        // Automatically switch tabs depending on success/state
        setActiveTab('metrics');
      } else {
        setActiveTab('tokens');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = () => {
    if (!result) return;
    
    const targetInfo = hardware.find(h => h.id === selectedTarget);
    const dateStr = new Date().toISOString();

    const markdownReport = `# Code Optimization Framework — Compilation Report
Generated: ${dateStr}
Target Profile: ${targetInfo ? targetInfo.name : selectedTarget} (${targetInfo?.architecture}, ${targetInfo?.word_size})

---

## 1. Executive Performance Summary

| Resource Metric | Unoptimized (O0) | Optimized | Improvement |
| :--- | :---: | :---: | :---: |
| **Instruction Count** | ${result.metrics_before.instruction_count} | ${result.metrics_after.instruction_count} | ${(((result.metrics_before.instruction_count - result.metrics_after.instruction_count) / (result.metrics_before.instruction_count || 1)) * 100).toFixed(1)}% |
| **Estimated CPU Cycles** | ${result.metrics_before.estimated_cycles} | ${result.metrics_after.estimated_cycles} | ${(((result.metrics_before.estimated_cycles - result.metrics_after.estimated_cycles) / (result.metrics_before.estimated_cycles || 1)) * 100).toFixed(1)}% |
| **Code Size (Flash)** | ${result.metrics_before.code_size_bytes} B | ${result.metrics_after.code_size_bytes} B | ${(((result.metrics_before.code_size_bytes - result.metrics_after.code_size_bytes) / (result.metrics_before.code_size_bytes || 1)) * 100).toFixed(1)}% |
| **Stack Memory Usage** | ${result.metrics_before.stack_usage_bytes} B | ${result.metrics_after.stack_usage_bytes} B | ${(((result.metrics_before.stack_usage_bytes - result.metrics_after.stack_usage_bytes) / (result.metrics_before.stack_usage_bytes || 1)) * 100).toFixed(1)}% |
| **Memory Accesses** | ${result.metrics_before.memory_accesses} | ${result.metrics_after.memory_accesses} | ${(((result.metrics_before.memory_accesses - result.metrics_after.memory_accesses) / (result.metrics_before.memory_accesses || 1)) * 100).toFixed(1)}% |
| **Power Cost Score** | ${result.metrics_before.estimated_power_cost} | ${result.metrics_after.estimated_power_cost} | ${(((result.metrics_before.estimated_power_cost - result.metrics_after.estimated_power_cost) / (result.metrics_before.estimated_power_cost || 1)) * 100).toFixed(1)}% |

---

## 2. Optimizer Transformation Log

Total Transformations Applied: ${result.optimization_log.length}

${result.optimization_log.map((log, i) => `### Step ${i + 1}: ${log.pass}
- **Reason:** ${log.reason}
- **Before:** \`${log.before || '(empty)'}\`
- **After:** \`${log.after || '(deleted)'}\`
`).join('\n')}

---

## 3. Register Allocation Summary

- **Total Spills to Stack:** ${result.register_allocation.spill_count}
- **Register Pool Utilization:** ${result.register_allocation.utilization} registers used

### Physical Register Mapping
${Object.entries(result.register_allocation.mapping).map(([v, r]) => `- \`${v}\` → \`${r}\``).join('\n') || 'None'}

---

## 4. Source Input Code
\`\`\`c
${code}
\`\`\`

---

## 5. Generated Assembly Output (${targetInfo?.architecture || 'ARM'})
\`\`\`asm
${result.assembly}
\`\`\`
`;

    const blob = new Blob([markdownReport], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `compiler_report_${selectedTarget}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadTAC = () => {
    if (!result) return;
    const tacContent = `; =========================================================
; Three-Address Code (TAC) Intermediate Representation
; Target: ${selectedTarget}
; =========================================================

; --- [RAW INTERMEDIATE REPRESENTATION (O0)] ---
${result.ir_before}

; =========================================================
; --- [OPTIMIZED INTERMEDIATE REPRESENTATION] ---
; =========================================================
${result.ir_after}
`;
    const blob = new Blob([tacContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `intermediate_representation_${selectedTarget}.tac`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-mono text-sm antialiased">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-5 py-3.5 flex justify-between items-center select-none">
        <div className="flex items-center space-x-3">
          <Cpu className="text-sky-400 w-5 h-5" />
          <span className="font-bold tracking-tight text-slate-200 uppercase">Code Optimization Framework</span>
          <span className="text-[10px] bg-slate-800 text-slate-400 border border-slate-700/80 px-2 py-0.5 rounded-full">Embedded</span>
        </div>
        
        {/* Hardware & Target Selector */}
        <div className="flex items-center space-x-3">
          <label className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Profile:</label>
          <select 
            value={selectedTarget}
            onChange={(e) => setSelectedTarget(e.target.value)}
            className="bg-slate-950 border border-slate-800 hover:border-slate-700 text-xs text-sky-400 font-bold rounded py-1 px-2.5 focus:outline-none focus:border-sky-500"
          >
            {hardware.map(p => (
              <option key={p.id} value={p.id}>{p.name} ({p.architecture})</option>
            ))}
          </select>
          
          <button
            onClick={handleCompile}
            disabled={loading}
            className="bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-slate-950 font-bold py-1 px-4 rounded text-xs transition-colors flex items-center space-x-1.5"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{loading ? "COMPILING..." : "COMPILE"}</span>
          </button>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 grid grid-cols-5 overflow-hidden">
        {/* Left Controls/Explorer Panel */}
        <div className="col-span-1 border-r border-slate-900 bg-slate-950 p-4 space-y-5 flex flex-col justify-between select-none">
          <div className="space-y-4">
            <div className="border-b border-slate-900 pb-2">
              <span className="text-xs text-slate-500 font-bold tracking-wider uppercase">Optimizer Passes</span>
            </div>
            
            <div className="space-y-2.5 text-xs text-slate-400 font-sans">
              {Object.keys(passes).map((passKey) => (
                <label key={passKey} className="flex items-center space-x-2.5 cursor-pointer hover:text-slate-200">
                  <input 
                    type="checkbox"
                    checked={(passes as any)[passKey]}
                    onChange={(e) => setPasses({ ...passes, [passKey]: e.target.checked })}
                    className="rounded border-slate-800 bg-slate-950 text-sky-600 focus:ring-sky-500"
                  />
                  <span className="capitalize">{passKey.replace('_', ' ')}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t border-slate-900">
            <div className="text-[10px] text-slate-600 uppercase tracking-widest">Active Target Info</div>
            {hardware.find(h => h.id === selectedTarget) && (
              <div className="bg-slate-900/40 border border-slate-800/80 p-2.5 rounded text-[11px] space-y-1 text-slate-400">
                <div>Registers: <span className="text-slate-200">{hardware.find(h => h.id === selectedTarget)?.registers}</span></div>
                <div>Word size: <span className="text-slate-200">{hardware.find(h => h.id === selectedTarget)?.word_size}</span></div>
                <div>RAM: <span className="text-slate-200">{hardware.find(h => h.id === selectedTarget)?.ram}</span></div>
                <div>Flash: <span className="text-slate-200">{hardware.find(h => h.id === selectedTarget)?.flash}</span></div>
              </div>
            )}
            
            {result && (
              <div className="space-y-2">
                <button 
                  onClick={handleDownloadReport}
                  className="w-full border border-sky-800/80 hover:border-sky-500 text-sky-300 bg-sky-950/40 hover:bg-sky-900/60 py-1.5 rounded transition-all text-xs flex justify-center items-center space-x-1.5 font-semibold"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  <span>Download Report (.md)</span>
                </button>
                <button 
                  onClick={handleDownloadTAC}
                  className="w-full border border-emerald-800/80 hover:border-emerald-500 text-emerald-300 bg-emerald-950/40 hover:bg-emerald-900/60 py-1.5 rounded transition-all text-xs flex justify-center items-center space-x-1.5 font-semibold"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  <span>Download IR (.tac)</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Center Source Editor */}
        <div className="col-span-2 border-r border-slate-900 flex flex-col">
          <div className="bg-slate-900/30 px-4 py-2 border-b border-slate-900 flex items-center justify-between text-xs text-slate-500 font-semibold select-none">
            <span className="flex items-center space-x-1"><FileCode className="w-3.5 h-3.5 text-sky-500" /> <span>main.c</span></span>
            <span>C (Embedded Dialect)</span>
          </div>
          <div className="flex-1 min-h-[400px]">
            <MonacoEditor
              height="100%"
              language="c"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 12,
                fontFamily: 'ui-monospace, monospace',
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
              }}
            />
          </div>
        </div>

        {/* Right Output Viewer */}
        <div className="col-span-2 bg-slate-950 flex flex-col">
          {/* Output Navigation Tab header — row 1 */}
          <div className="bg-slate-900/30 border-b border-slate-900 flex text-xs select-none flex-wrap">
            {(['metrics', 'assembly', 'diff', 'ir', 'log', 'cfg', 'timings', 'ast', 'tokens'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-2 border-r border-slate-900 transition-colors uppercase font-bold tracking-tight text-[10px] ${
                  activeTab === tab ? 'bg-slate-950 text-sky-400 border-t-2 border-t-sky-500' : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {tab === 'log' ? 'Opt. Log'
                  : tab === 'diff' ? 'Asm Diff'
                  : tab === 'cfg' ? 'CFG'
                  : tab === 'timings' ? 'Timings'
                  : tab}
              </button>
            ))}
          </div>

          {/* Compilation Pipeline status & feedback bar */}
          <div className="bg-slate-950 px-4 py-1.5 border-b border-slate-900 text-[10px] flex items-center justify-between">
            <div className="flex items-center space-x-3 text-slate-600">
              <span className={result?.success ? "text-emerald-500" : "text-slate-600"}>SCAN</span>
              <span>&gt;</span>
              <span className={result?.success ? "text-emerald-500" : "text-slate-600"}>PARSE</span>
              <span>&gt;</span>
              <span className={result?.success ? "text-emerald-500" : "text-slate-600"}>IR</span>
              <span>&gt;</span>
              <span className={result?.success ? "text-emerald-500" : "text-slate-600"}>OPTIMIZE</span>
              <span>&gt;</span>
              <span className={result?.success ? "text-emerald-500" : "text-slate-600"}>CODEGEN</span>
            </div>
            <div className="flex items-center space-x-3">
              {result?.timings?.['Total Pipeline Time'] !== undefined && (
                <span className="text-slate-500 font-mono">
                  {result.timings['Total Pipeline Time'].toFixed(2)} ms
                </span>
              )}
              {result && (
                <span className={result.success ? "text-emerald-500 font-bold" : "text-rose-500 font-bold"}>
                  {result.success ? "BUILD OK" : "BUILD FAILED"}
                </span>
              )}
            </div>
          </div>

          {/* Diagnostics / Compile Error Feed */}
          {result && result.errors && result.errors.length > 0 && (
            <div className="bg-rose-950/20 border-b border-rose-900/50 p-3 space-y-1.5 text-xs">
              <div className="flex items-center space-x-1.5 text-rose-400 font-bold">
                <ShieldAlert className="w-4 h-4" />
                <span>Compiler Diagnostics</span>
              </div>
              {result.errors.map((err, idx) => (
                <div key={idx} className="text-rose-300/90 font-mono">
                  [Line {err.line}, Col {err.column}] {err.type}: {err.message}
                </div>
              ))}
            </div>
          )}

          {/* Tab contents routing */}
          <div className="flex-1 overflow-hidden relative">
            {activeTab === 'tokens' && result && <TokensView tokens={result.tokens} />}
            {activeTab === 'ast' && result && <ASTView ast={result.ast} />}
            {activeTab === 'ir' && result && <IRView irBefore={result.ir_before} irAfter={result.ir_after} />}
            {activeTab === 'log' && result && <OptimizationLog log={result.optimization_log} />}
            {activeTab === 'assembly' && result && (
              <AssemblyView assembly={result.assembly} allocation={result.register_allocation} />
            )}
            {activeTab === 'metrics' && result && (
              <MetricsPanel before={result.metrics_before} after={result.metrics_after} />
            )}
            {activeTab === 'cfg' && result && (
              <CFGView cfgMermaid={result.cfg_mermaid || ''} />
            )}
            {activeTab === 'diff' && result && (
              <AssemblyDiffView
                assemblyO0={result.assembly_o0 || ''}
                assemblyOptimized={result.assembly}
              />
            )}
            {activeTab === 'timings' && result && (
              <TimingsPanel timings={result.timings || {}} />
            )}
            
            {!result && (
              <div className="absolute inset-0 flex flex-col justify-center items-center text-slate-600 space-y-2 select-none">
                <Layers className="w-10 h-10 text-slate-800" />
                <span className="text-xs">Compile to generate reports and pipeline views</span>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
