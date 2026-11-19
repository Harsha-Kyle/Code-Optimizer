import React from 'react';
import type { RegisterAllocation } from '../types';

interface AssemblyViewProps {
  assembly: string;
  allocation: RegisterAllocation;
}

export const AssemblyView: React.FC<AssemblyViewProps> = ({ assembly, allocation }) => {
  if (!assembly) {
    return (
      <div className="text-gray-400 p-4 text-center text-sm">
        No assembly generated. Write code and hit compile.
      </div>
    );
  }

  const asmLines = assembly.split('\n');

  return (
    <div className="grid grid-cols-3 gap-4 p-4 text-xs font-mono select-text leading-relaxed">
      {/* Code Area */}
      <div className="col-span-2 border border-slate-700 bg-slate-900 rounded p-3 overflow-auto max-h-[500px]">
        <div className="border-b border-slate-700 pb-2 mb-2 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
          Target Output (ARM Assembly)
        </div>
        <pre className="text-slate-300">
          {asmLines.map((line, idx) => {
            const isComment = line.trim().startsWith('@');
            return (
              <div 
                key={idx} 
                className={`px-1 py-0.5 rounded ${isComment ? 'text-slate-500 font-sans italic bg-slate-950/20' : 'hover:bg-slate-800/40'}`}
              >
                <span className="text-slate-600 inline-block w-6 text-right mr-3 select-none">{idx + 1}</span>
                {line}
              </div>
            );
          })}
        </pre>
      </div>

      {/* Allocation Panel */}
      <div className="border border-slate-700 bg-slate-900 rounded p-3 space-y-4">
        <div>
          <div className="border-b border-slate-700 pb-2 mb-2 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
            Register Mapping
          </div>
          {Object.keys(allocation.mapping).length > 0 ? (
            <table className="w-full text-slate-300">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800">
                  <th className="text-left pb-1">Variable</th>
                  <th className="text-right pb-1">Register</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(allocation.mapping).map(([variable, register]) => (
                  <tr key={variable} className="hover:bg-slate-800/30">
                    <td className="py-1 text-sky-400">{variable}</td>
                    <td className="py-1 text-right text-amber-400 font-bold">{register}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-slate-500 italic">No variables allocated.</div>
          )}
        </div>

        <div>
          <div className="border-b border-slate-700 pb-2 mb-2 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
            Spill Allocation
          </div>
          {Object.keys(allocation.spills).length > 0 ? (
            <table className="w-full text-slate-300">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800">
                  <th className="text-left pb-1">Variable</th>
                  <th className="text-right pb-1">Stack Offset</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(allocation.spills).map(([variable, offset]) => (
                  <tr key={variable} className="hover:bg-slate-800/30">
                    <td className="py-1 text-rose-400">{variable}</td>
                    <td className="py-1 text-right text-slate-400">SP + #{offset}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-emerald-500 italic">No register spills!</div>
          )}
        </div>
      </div>
    </div>
  );
};
