interface TimingsPanelProps {
  timings: Record<string, number>;
}

const STAGE_COLORS: Record<string, string> = {
  'Lexing':              'bg-violet-500',
  'Parsing':             'bg-sky-500',
  'Semantic Analysis':   'bg-yellow-500',
  'IR Generation':       'bg-orange-500',
  'Optimization':        'bg-emerald-500',
  'Register Allocation': 'bg-pink-500',
  'Code Generation':     'bg-cyan-500',
  'Total Pipeline Time': 'bg-slate-400',
};

const STAGE_DESC: Record<string, string> = {
  'Lexing':              'M1 — Tokenize source into lexemes',
  'Parsing':             'M1 — Build AST from token stream',
  'Semantic Analysis':   'M1 — Scope resolution and type checking',
  'IR Generation':       'M2 — Lower AST to Three-Address Code',
  'Optimization':        'M2 — Apply 7 optimization passes',
  'Register Allocation': 'M3 — Linear-scan allocator (R0–R11)',
  'Code Generation':     'M3 — Emit ARM Cortex-M assembly',
  'Total Pipeline Time': 'Full compile end-to-end',
};

export function TimingsPanel({ timings }: TimingsPanelProps) {
  if (!timings || Object.keys(timings).length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-slate-600 text-xs select-none">
        No timing data. Compile code first.
      </div>
    );
  }

  const stages = Object.entries(timings).filter(([k]) => k !== 'Total Pipeline Time');
  const total = timings['Total Pipeline Time'] ?? 0;

  return (
    <div className="h-full overflow-auto p-4 space-y-5">
      {/* Header */}
      <div className="border-b border-slate-800 pb-2">
        <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
          Pipeline Stage Execution Timings
        </div>
      </div>

      {/* Total summary */}
      <div className="flex items-center justify-between bg-slate-900/60 border border-slate-700 rounded px-4 py-3">
        <span className="text-slate-300 text-xs font-bold">Total Compile Time</span>
        <span className="text-sky-400 font-mono font-bold text-sm">{total.toFixed(3)} ms</span>
      </div>

      {/* Stacked bar chart */}
      <div>
        <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2 font-bold">Time Share</div>
        <div className="flex h-5 rounded overflow-hidden">
          {stages.map(([stage, ms]) => {
            const pct = total > 0 ? (ms / total) * 100 : 0;
            return (
              <div
                key={stage}
                title={`${stage}: ${ms.toFixed(3)} ms (${pct.toFixed(1)}%)`}
                className={`${STAGE_COLORS[stage] || 'bg-slate-500'} transition-all`}
                style={{ width: `${pct}%` }}
              />
            );
          })}
        </div>
        {/* Legend */}
        <div className="flex flex-wrap gap-x-4 gap-y-1.5 mt-2">
          {stages.map(([stage]) => (
            <div key={stage} className="flex items-center space-x-1.5 text-[10px] text-slate-400">
              <span className={`w-2 h-2 rounded-full inline-block ${STAGE_COLORS[stage] || 'bg-slate-500'}`} />
              <span>{stage}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Stage breakdown rows */}
      <div className="space-y-2">
        <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Stage Breakdown</div>
        {stages.map(([stage, ms]) => {
          const pct = total > 0 ? (ms / total) * 100 : 0;
          return (
            <div key={stage} className="bg-slate-900/40 border border-slate-800 rounded p-2.5 space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${STAGE_COLORS[stage] || 'bg-slate-500'}`} />
                  <span className="text-slate-200 text-xs font-semibold">{stage}</span>
                </div>
                <span className="font-mono text-xs text-slate-300 font-bold">{ms.toFixed(3)} ms</span>
              </div>
              {/* Progress bar for relative time */}
              <div className="w-full bg-slate-800 rounded h-1">
                <div
                  className={`${STAGE_COLORS[stage] || 'bg-slate-500'} h-1 rounded transition-all`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-slate-600">
                <span>{STAGE_DESC[stage] || ''}</span>
                <span>{pct.toFixed(1)}% of total</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
