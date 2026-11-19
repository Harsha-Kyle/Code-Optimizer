import React from 'react';

interface IRViewProps {
  irBefore: string;
  irAfter: string;
}

export const IRView: React.FC<IRViewProps> = ({ irBefore, irAfter }) => {
  if (!irBefore) {
    return (
      <div className="text-gray-400 p-4 text-center text-sm">
        No IR generated. Write code and hit compile.
      </div>
    );
  }

  const beforeLines = irBefore.split('\n');
  const afterLines = irAfter ? irAfter.split('\n') : [];

  return (
    <div className="grid grid-cols-2 gap-4 p-4 text-xs font-mono select-text leading-relaxed">
      {/* Before Panel */}
      <div className="border border-slate-700 bg-slate-900 rounded p-3 overflow-auto max-h-[500px]">
        <div className="border-b border-slate-700 pb-2 mb-2 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
          Raw Intermediate Representation (O0)
        </div>
        <pre className="text-slate-300">
          {beforeLines.map((line, idx) => (
            <div key={idx} className="hover:bg-slate-800/40 px-1 py-0.5 rounded">
              <span className="text-slate-600 inline-block w-6 text-right mr-3 select-none">{idx + 1}</span>
              {line}
            </div>
          ))}
        </pre>
      </div>

      {/* After Panel */}
      <div className="border border-slate-700 bg-slate-900 rounded p-3 overflow-auto max-h-[500px]">
        <div className="border-b border-slate-700 pb-2 mb-2 text-slate-400 font-semibold tracking-wider uppercase text-[10px] flex justify-between">
          <span>Optimized Intermediate Representation</span>
          {irAfter && irBefore !== irAfter && (
            <span className="text-emerald-400 font-normal normal-case">Code simplified</span>
          )}
        </div>
        <pre className="text-slate-300">
          {afterLines.length > 0 ? (
            afterLines.map((line, idx) => {
              const isDifferent = !beforeLines.includes(line);
              return (
                <div 
                  key={idx} 
                  className={`px-1 py-0.5 rounded transition-colors ${
                    isDifferent ? 'bg-emerald-950/40 text-emerald-300 border-l-2 border-emerald-500 -ml-[2px]' : 'hover:bg-slate-800/40'
                  }`}
                >
                  <span className="text-slate-600 inline-block w-6 text-right mr-3 select-none">{idx + 1}</span>
                  {line}
                </div>
              );
            })
          ) : (
            <div className="text-gray-500">No optimizations applied.</div>
          )}
        </pre>
      </div>
    </div>
  );
};
