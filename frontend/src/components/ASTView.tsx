import React, { useState } from 'react';

interface ASTViewProps {
  ast: any;
}

export const ASTView: React.FC<ASTViewProps> = ({ ast }) => {
  if (!ast || Object.keys(ast).length === 0) {
    return (
      <div className="text-gray-400 p-4 text-center text-sm">
        No AST generated. Write code and hit compile.
      </div>
    );
  }

  return (
    <div className="p-4 overflow-auto max-h-[500px] text-xs font-mono select-none">
      <TreeNode label="Program" data={ast} defaultOpen={true} />
    </div>
  );
};

interface TreeNodeProps {
  label: string;
  data: any;
  defaultOpen?: boolean;
}

const TreeNode: React.FC<TreeNodeProps> = ({ label, data, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);
  const isObject = data && typeof data === 'object';
  const hasChildren = isObject && Object.keys(data).length > 0;

  const renderValue = (val: any) => {
    if (val === null) return <span className="text-gray-500">null</span>;
    if (typeof val === 'boolean') return <span className="text-purple-400">{val.toString()}</span>;
    if (typeof val === 'number' || (!isNaN(val) && !isNaN(parseFloat(val)))) return <span className="text-amber-400">{val}</span>;
    return <span className="text-emerald-400">"{val}"</span>;
  };

  if (!hasChildren) {
    return (
      <div className="pl-4 py-1 flex items-center">
        <span className="text-gray-400 mr-2">{label}:</span>
        {renderValue(data)}
      </div>
    );
  }

  // Filter keys to display
  const childKeys = Object.keys(data).filter(k => k !== 'type');

  return (
    <div className="pl-4 py-1">
      <div 
        className="flex items-center cursor-pointer hover:bg-slate-800/50 py-0.5 rounded px-1 -ml-1 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <span className="text-blue-400 mr-1.5">{open ? '▼' : '▶'}</span>
        <span className="text-sky-300 font-bold">{label}</span>
        {data.type && <span className="text-gray-500 text-[10px] ml-2">({data.type})</span>}
      </div>
      
      {open && (
        <div className="border-l border-slate-700 ml-1.5 pl-2 mt-1">
          {childKeys.map(key => {
            const val = data[key];
            if (Array.isArray(val)) {
              return (
                <div key={key} className="py-1">
                  <div className="text-gray-400 font-semibold mb-1">{key}[]:</div>
                  <div className="border-l border-slate-800 ml-2 pl-2">
                    {val.map((item, idx) => (
                      <TreeNode key={idx} label={`[${idx}]`} data={item} />
                    ))}
                  </div>
                </div>
              );
            }
            return <TreeNode key={key} label={key} data={val} />;
          })}
        </div>
      )}
    </div>
  );
};
