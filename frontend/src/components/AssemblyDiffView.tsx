import { DiffEditor } from '@monaco-editor/react';

interface AssemblyDiffViewProps {
  assemblyO0: string;
  assemblyOptimized: string;
}

export function AssemblyDiffView({ assemblyO0, assemblyOptimized }: AssemblyDiffViewProps) {
  if (!assemblyO0 && !assemblyOptimized) {
    return (
      <div className="h-full flex items-center justify-center text-slate-600 text-xs select-none">
        No assembly data. Compile code first.
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900/40 border-b border-slate-900 text-[10px] text-slate-500 uppercase tracking-widest select-none">
        <span className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-rose-500 inline-block"></span>
          <span>Unoptimized Assembly (O0)</span>
        </span>
        <span className="text-slate-600">vs</span>
        <span className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
          <span>Optimized Assembly</span>
        </span>
      </div>
      <div className="flex-1 min-h-0">
        <DiffEditor
          height="100%"
          language="asm"
          original={assemblyO0}
          modified={assemblyOptimized}
          theme="vs-dark"
          options={{
            fontSize: 12,
            fontFamily: 'ui-monospace, monospace',
            readOnly: true,
            minimap: { enabled: false },
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            renderSideBySide: true,
            diffWordWrap: 'off',
          }}
        />
      </div>
    </div>
  );
}
