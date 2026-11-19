import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#0f172a',
    primaryTextColor: '#e2e8f0',
    primaryBorderColor: '#334155',
    lineColor: '#38bdf8',
    secondaryColor: '#1e293b',
    tertiaryColor: '#0f172a',
    background: '#020617',
    nodeBorder: '#334155',
    clusterBkg: '#1e293b',
    titleColor: '#38bdf8',
    edgeLabelBackground: '#1e293b',
    attributeBackgroundColorEven: '#1e293b',
    attributeBackgroundColorOdd: '#0f172a',
    fontFamily: 'ui-monospace, monospace',
    fontSize: '12px',
  },
  flowchart: {
    htmlLabels: true,
    curve: 'basis',
  },
  securityLevel: 'loose',
});

interface CFGViewProps {
  cfgMermaid: string;
}

export function CFGView({ cfgMermaid }: CFGViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState('');
  const [rendered, setRendered] = useState('');

  useEffect(() => {
    if (!cfgMermaid) return;

    const render = async () => {
      try {
        const id = `cfg-${Date.now()}`;
        const { svg } = await mermaid.render(id, cfgMermaid);
        setRendered(svg);
        setError('');
      } catch (e: any) {
        setError(e?.message || 'Failed to render CFG');
      }
    };

    render();
  }, [cfgMermaid]);

  if (!cfgMermaid) {
    return (
      <div className="h-full flex items-center justify-center text-slate-600 text-xs select-none">
        No CFG data available. Compile code first.
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-4 space-y-2">
        <span className="text-rose-400 text-xs font-mono">CFG render error: {error}</span>
        <pre className="text-slate-500 text-[10px] font-mono bg-slate-900/40 rounded p-2 w-full overflow-auto max-h-48">
          {cfgMermaid}
        </pre>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col overflow-auto p-3 bg-slate-950">
      <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-3 select-none font-bold">
        Control Flow Graph — Basic Blocks & Edges
      </div>
      <div
        ref={containerRef}
        className="flex-1 flex justify-center overflow-auto"
        dangerouslySetInnerHTML={{ __html: rendered }}
      />
    </div>
  );
}
