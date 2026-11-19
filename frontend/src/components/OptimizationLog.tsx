import React from 'react';
import type { OptimizationLogEntry } from '../types';

interface OptimizationLogProps {
  log: OptimizationLogEntry[];
}

export const OptimizationLog: React.FC<OptimizationLogProps> = ({ log }) => {
  if (!log || log.length === 0) {
    return (
      <div className="text-gray-400 p-4 text-center text-sm">
        No transformations performed. Either the code is fully optimal or optimizations are disabled.
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3 overflow-auto max-h-[500px] text-xs">
      <div className="text-slate-400 font-semibold mb-2 uppercase text-[10px] tracking-wider border-b border-slate-800 pb-2">
        Transformation Log ({log.length} actions)
      </div>
      
      {log.map((entry, idx) => (
        <div key={idx} className="border border-slate-800 bg-slate-900/50 rounded-lg p-3 space-y-2">
          {/* Header */}
          <div className="flex justify-between items-center">
            <span className="bg-sky-950/80 text-sky-300 border border-sky-800/60 px-2 py-0.5 rounded font-mono font-bold tracking-tight">
              {entry.pass}
            </span>
            <span className="text-[10px] text-slate-500">Step #{idx + 1}</span>
          </div>
          
          {/* Reason */}
          <div className="text-slate-300 font-sans leading-relaxed">
            {entry.reason}
          </div>
          
          {/* Code snippet before/after */}
          <div className="grid grid-cols-2 gap-2 mt-1.5 font-mono text-[11px] bg-slate-950 p-2 rounded border border-slate-800/80">
            <div>
              <div className="text-rose-400 text-[10px] border-b border-rose-950/50 pb-1 mb-1 font-semibold uppercase">Before:</div>
              <div className="text-rose-300/85 truncate">{entry.before || "(empty)"}</div>
            </div>
            <div>
              <div className="text-emerald-400 text-[10px] border-b border-emerald-950/50 pb-1 mb-1 font-semibold uppercase">After:</div>
              <div className="text-emerald-300/85 truncate">{entry.after || "(deleted)"}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
