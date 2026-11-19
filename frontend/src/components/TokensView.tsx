import React from 'react';
import type { Token } from '../types';

interface TokensViewProps {
  tokens: Token[];
}

export const TokensView: React.FC<TokensViewProps> = ({ tokens }) => {
  if (!tokens || tokens.length === 0) {
    return (
      <div className="text-gray-400 p-4 text-center text-sm">
        No token stream generated. Write code and hit compile.
      </div>
    );
  }

  return (
    <div className="p-4 overflow-auto max-h-[500px]">
      <div className="border border-slate-800 rounded-lg bg-slate-950 overflow-hidden text-xs">
        <table className="w-full">
          <thead>
            <tr className="bg-slate-900 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-800 text-[10px]">
              <th className="py-2.5 px-4 text-left">Token Type</th>
              <th className="py-2.5 px-4 text-left">Lexeme (Value)</th>
              <th className="py-2.5 px-4 text-right">Location</th>
            </tr>
          </thead>
          <tbody>
            {tokens.map((token, idx) => (
              <tr key={idx} className="border-b border-slate-900 hover:bg-slate-900/40 font-mono transition-colors">
                <td className="py-2 px-4 text-sky-400 font-bold">{token.type}</td>
                <td className="py-2 px-4 text-slate-300">
                  {token.value === "" ? (
                    <span className="text-slate-600 italic">empty</span>
                  ) : (
                    <code>{token.value}</code>
                  )}
                </td>
                <td className="py-2 px-4 text-right text-slate-500">
                  Line {token.line}, Col {token.column}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
