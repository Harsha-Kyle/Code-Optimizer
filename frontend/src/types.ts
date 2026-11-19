export interface Token {
  type: string;
  value: string;
  line: number;
  column: number;
}

export interface CompilerError {
  line: number;
  column: number;
  type: string;
  message: string;
}

export interface OptimizationLogEntry {
  pass: string;
  before: string;
  after: string;
  reason: string;
}

export interface ResourceMetrics {
  instruction_count: number;
  estimated_cycles: number;
  code_size_bytes: number;
  stack_usage_bytes: number;
  memory_accesses: number;
  estimated_power_cost: number;
}

export interface RegisterAllocation {
  mapping: Record<string, string>;
  spills: Record<string, number>;
  spill_count: number;
  utilization: number;
}

export interface CompileResponse {
  success: boolean;
  errors: CompilerError[];
  tokens: Token[];
  ast: any;
  ir_before: string;
  ir_after: string;
  optimization_log: OptimizationLogEntry[];
  assembly: string;
  assembly_o0?: string;
  cfg_mermaid?: string;
  timings?: Record<string, number>;
  metrics_before: ResourceMetrics;
  metrics_after: ResourceMetrics;
  register_allocation: RegisterAllocation;
  id?: string;
}

export interface HardwareProfile {
  id: string;
  name: string;
  architecture: string;
  registers: number;
  word_size: string;
  ram: string;
  flash: string;
}
