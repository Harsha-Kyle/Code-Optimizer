import React from 'react';
import type { ResourceMetrics } from '../types';

interface MetricsPanelProps {
  before: ResourceMetrics;
  after: ResourceMetrics;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({ before, after }) => {
  if (!before || !after || Object.keys(before).length === 0) {
    return (
      <div className="text-gray-400 p-4 text-center text-sm">
        No metrics available. Compile your code to see target resource metrics.
      </div>
    );
  }

  const calculatePct = (b: number, a: number) => {
    if (b === 0) return '0%';
    const pct = ((b - a) / b) * 100;
    if (pct < 0) return `${Math.abs(pct).toFixed(1)}% regr`;
    return `${pct.toFixed(1)}%`;
  };

  const getMetricRow = (label: string, beforeVal: number, afterVal: number, suffix: string = '') => {
    const pct = ((beforeVal - afterVal) / (beforeVal || 1)) * 100;
    const isImprovement = pct > 0;
    const isWorse = pct < 0;

    return (
      <tr className="border-b border-slate-800 hover:bg-slate-900/50 transition-colors">
        <td className="py-2.5 px-4 font-sans text-slate-300 font-medium">{label}</td>
        <td className="py-2.5 px-4 text-right text-slate-400 font-mono">{beforeVal}{suffix}</td>
        <td className="py-2.5 px-4 text-right text-emerald-400 font-bold font-mono">{afterVal}{suffix}</td>
        <td className={`py-2.5 px-4 text-right font-semibold font-mono ${isImprovement ? 'text-emerald-400' : isWorse ? 'text-rose-400' : 'text-slate-500'}`}>
          {isImprovement ? '↓ ' : isWorse ? '↑ ' : ''}
          {calculatePct(beforeVal, afterVal)}
        </td>
      </tr>
    );
  };

  return (
    <div className="p-4 space-y-4 max-h-[500px] overflow-auto">
      {/* Overview stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="border border-slate-800 bg-slate-900/40 p-3 rounded-lg text-center">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Instruction Count</div>
          <div className="text-xl font-bold mt-1 text-slate-200">{after.instruction_count}</div>
          <div className="text-[10px] text-emerald-400 font-semibold mt-0.5">
            {calculatePct(before.instruction_count, after.instruction_count)} reduction
          </div>
        </div>

        <div className="border border-slate-800 bg-slate-900/40 p-3 rounded-lg text-center">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Estimated CPU Cycles</div>
          <div className="text-xl font-bold mt-1 text-slate-200">{after.estimated_cycles}</div>
          <div className="text-[10px] text-emerald-400 font-semibold mt-0.5">
            {calculatePct(before.estimated_cycles, after.estimated_cycles)} reduction
          </div>
        </div>

        <div className="border border-slate-800 bg-slate-900/40 p-3 rounded-lg text-center">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Flash Footprint</div>
          <div className="text-xl font-bold mt-1 text-slate-200">{after.code_size_bytes} B</div>
          <div className="text-[10px] text-emerald-400 font-semibold mt-0.5">
            {calculatePct(before.code_size_bytes, after.code_size_bytes)} reduction
          </div>
        </div>

        <div className="border border-slate-800 bg-slate-900/40 p-3 rounded-lg text-center">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Power Score</div>
          <div className="text-xl font-bold mt-1 text-slate-200">{after.estimated_power_cost}</div>
          <div className="text-[10px] text-emerald-400 font-semibold mt-0.5">
            {calculatePct(before.estimated_power_cost, after.estimated_power_cost)} reduction
          </div>
        </div>
      </div>

      {/* Detail Table */}
      <div className="border border-slate-800 rounded-lg bg-slate-950 overflow-hidden mt-4">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-slate-900 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-800 text-[10px]">
              <th className="py-2.5 px-4 text-left">Resource Metric</th>
              <th className="py-2.5 px-4 text-right">O0 (Unoptimized)</th>
              <th className="py-2.5 px-4 text-right">Optimized</th>
              <th className="py-2.5 px-4 text-right">Improvement</th>
            </tr>
          </thead>
          <tbody>
            {getMetricRow("Instruction Count", before.instruction_count, after.instruction_count)}
            {getMetricRow("Estimated Clock Cycles", before.estimated_cycles, after.estimated_cycles)}
            {getMetricRow("Stack Space", before.stack_usage_bytes, after.stack_usage_bytes, " B")}
            {getMetricRow("RAM memory Transactions", before.memory_accesses, after.memory_accesses)}
            {getMetricRow("Instruction Memory Size", before.code_size_bytes, after.code_size_bytes, " B")}
            {getMetricRow("Estimated Power Cost (Weighted)", before.estimated_power_cost, after.estimated_power_cost)}
          </tbody>
        </table>
      </div>
    </div>
  );
};
