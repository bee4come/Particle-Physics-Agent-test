import React, { useState, useMemo, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, Activity, Clock, Zap, TrendingUp, Filter, RefreshCw, Maximize2 } from 'lucide-react';

interface ToolMetrics {
  name: string;
  category: 'mcp' | 'search' | 'validation' | 'generation' | 'compilation' | 'analysis';
  calls: number;
  totalDuration: number;
  avgDuration: number;
  successRate: number;
  lastUsed: number;
  p95Duration: number;
  p99Duration: number;
  errorCount: number;
  concurrentCalls: number;
  correlationIds: string[];
}

interface HeatmapCell {
  hour: number;
  day: string;
  value: number;
  calls: number;
  avgDuration: number;
  errors: number;
}

interface ToolOrchestrationDashboardProps {
  events: Array<{
    timestamp: number;
    tool?: string;
    duration?: number;
    status?: string;
    traceInfo?: {
      traceId: string;
      stepId: string;
      sessionId?: string;
    };
  }>;
  isLive?: boolean;
  onRefresh?: () => void;
}

const categoryColors = {
  mcp: 'bg-blue-500',
  search: 'bg-green-500', 
  validation: 'bg-yellow-500',
  generation: 'bg-purple-500',
  compilation: 'bg-red-500',
  analysis: 'bg-cyan-500'
};

const categoryLabels = {
  mcp: 'MCP Tools',
  search: 'Search Tools',
  validation: 'Validation Tools', 
  generation: 'Generation Tools',
  compilation: 'Compilation Tools',
  analysis: 'Analysis Tools'
};

function categorializeTool(toolName: string): ToolMetrics['category'] {
  const name = toolName.toLowerCase();
  if (name.includes('mcp') || name.includes('particle') || name.includes('physics')) return 'mcp';
  if (name.includes('search') || name.includes('kb') || name.includes('retriev')) return 'search';
  if (name.includes('valid') || name.includes('check')) return 'validation';
  if (name.includes('generat') || name.includes('diagram') || name.includes('tikz')) return 'generation';
  if (name.includes('compil') || name.includes('latex')) return 'compilation';
  return 'analysis';
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

function getIntensityColor(value: number, max: number): string {
  const intensity = Math.min(value / max, 1);
  if (intensity === 0) return 'bg-neutral-800';
  if (intensity <= 0.2) return 'bg-green-900/50';
  if (intensity <= 0.4) return 'bg-green-700/50';
  if (intensity <= 0.6) return 'bg-yellow-600/50';
  if (intensity <= 0.8) return 'bg-orange-500/50';
  return 'bg-red-500/50';
}

export function ToolOrchestrationDashboard({ events, isLive, onRefresh }: ToolOrchestrationDashboardProps) {
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('6h');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'calls' | 'duration' | 'errors' | 'performance'>('calls');
  const [isExpanded, setIsExpanded] = useState(false);

  // Process events into tool metrics
  const toolMetrics = useMemo(() => {
    const now = Date.now();
    const timeRangeMs = {
      '1h': 60 * 60 * 1000,
      '6h': 6 * 60 * 60 * 1000, 
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000
    }[timeRange];

    // Filter events by time range and presence of tool
    const relevantEvents = events.filter(e => 
      e.tool && 
      e.timestamp > (now - timeRangeMs)
    );

    // Group by tool name
    const toolGroups = new Map<string, typeof relevantEvents>();
    relevantEvents.forEach(event => {
      if (!event.tool) return;
      if (!toolGroups.has(event.tool)) {
        toolGroups.set(event.tool, []);
      }
      toolGroups.get(event.tool)!.push(event);
    });

    // Calculate metrics for each tool
    const metrics: ToolMetrics[] = [];
    toolGroups.forEach((toolEvents, toolName) => {
      const durations = toolEvents.filter(e => e.duration).map(e => e.duration!);
      const errors = toolEvents.filter(e => e.status === 'failed' || e.status === 'error');
      const successes = toolEvents.filter(e => e.status === 'completed' || e.status === 'success');
      const correlationIds = [...new Set(toolEvents.map(e => e.traceInfo?.traceId).filter(Boolean))] as string[];

      // Calculate percentiles
      const sortedDurations = durations.sort((a, b) => a - b);
      const p95Index = Math.floor(sortedDurations.length * 0.95);
      const p99Index = Math.floor(sortedDurations.length * 0.99);

      metrics.push({
        name: toolName,
        category: categorializeTool(toolName),
        calls: toolEvents.length,
        totalDuration: durations.reduce((sum, d) => sum + d, 0),
        avgDuration: durations.length > 0 ? durations.reduce((sum, d) => sum + d, 0) / durations.length : 0,
        successRate: toolEvents.length > 0 ? (successes.length / toolEvents.length) * 100 : 0,
        lastUsed: Math.max(...toolEvents.map(e => e.timestamp)),
        p95Duration: sortedDurations[p95Index] || 0,
        p99Duration: sortedDurations[p99Index] || 0,
        errorCount: errors.length,
        concurrentCalls: 0, // TODO: Calculate based on overlapping timestamps
        correlationIds
      });
    });

    return metrics;
  }, [events, timeRange]);

  // Filter and sort metrics
  const filteredMetrics = useMemo(() => {
    let filtered = toolMetrics;
    
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(m => m.category === categoryFilter);
    }

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'calls': return b.calls - a.calls;
        case 'duration': return b.totalDuration - a.totalDuration;
        case 'errors': return b.errorCount - a.errorCount;
        case 'performance': return a.avgDuration - b.avgDuration;
        default: return 0;
      }
    });
  }, [toolMetrics, categoryFilter, sortBy]);

  // Generate heatmap data
  const heatmapData = useMemo(() => {
    const now = new Date();
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const hours = Array.from({ length: 24 }, (_, i) => i);
    
    const cells: HeatmapCell[] = [];
    const cellMap = new Map<string, { calls: number; durations: number[]; errors: number }>();

    // Initialize cells
    days.forEach((day, dayIndex) => {
      hours.forEach(hour => {
        const key = `${dayIndex}-${hour}`;
        cellMap.set(key, { calls: 0, durations: [], errors: 0 });
      });
    });

    // Populate with event data
    events.filter(e => e.tool && e.timestamp > (Date.now() - 7 * 24 * 60 * 60 * 1000))
      .forEach(event => {
        const date = new Date(event.timestamp);
        const dayIndex = (date.getDay() + 6) % 7; // Convert Sunday=0 to Monday=0
        const hour = date.getHours();
        const key = `${dayIndex}-${hour}`;
        
        const cell = cellMap.get(key);
        if (cell) {
          cell.calls++;
          if (event.duration) cell.durations.push(event.duration);
          if (event.status === 'failed' || event.status === 'error') cell.errors++;
        }
      });

    // Convert to cells array
    days.forEach((day, dayIndex) => {
      hours.forEach(hour => {
        const key = `${dayIndex}-${hour}`;
        const data = cellMap.get(key)!;
        cells.push({
          hour,
          day,
          value: data.calls,
          calls: data.calls,
          avgDuration: data.durations.length > 0 ? data.durations.reduce((a, b) => a + b) / data.durations.length : 0,
          errors: data.errors
        });
      });
    });

    return cells;
  }, [events]);

  const maxHeatmapValue = Math.max(...heatmapData.map(c => c.value));
  const totalCalls = toolMetrics.reduce((sum, m) => sum + m.calls, 0);
  const avgDuration = toolMetrics.length > 0 ? 
    toolMetrics.reduce((sum, m) => sum + m.avgDuration, 0) / toolMetrics.length : 0;
  const overallSuccessRate = toolMetrics.length > 0 ?
    toolMetrics.reduce((sum, m) => sum + m.successRate, 0) / toolMetrics.length : 0;

  return (
    <div className={`bg-neutral-900/50 border border-neutral-700 rounded-lg p-4 space-y-4 ${isExpanded ? 'fixed inset-4 z-50 overflow-y-auto' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-white">Tool Orchestration Dashboard</h3>
            {isLive && (
              <Badge variant="outline" className="text-green-400 border-green-400/30 animate-pulse">
                LIVE
              </Badge>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {onRefresh && (
            <Button variant="ghost" size="sm" onClick={onRefresh} className="h-7 px-2">
              <RefreshCw className="h-3 w-3" />
            </Button>
          )}
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setIsExpanded(!isExpanded)}
            className="h-7 px-2"
          >
            <Maximize2 className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardContent className="p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-neutral-400">Total Calls</p>
                <p className="text-xl font-semibold text-white">{formatNumber(totalCalls)}</p>
              </div>
              <Activity className="h-4 w-4 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardContent className="p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-neutral-400">Avg Duration</p>
                <p className="text-xl font-semibold text-white">{formatDuration(avgDuration)}</p>
              </div>
              <Clock className="h-4 w-4 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardContent className="p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-neutral-400">Success Rate</p>
                <p className="text-xl font-semibold text-white">{overallSuccessRate.toFixed(1)}%</p>
              </div>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardContent className="p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-neutral-400">Active Tools</p>
                <p className="text-xl font-semibold text-white">{toolMetrics.length}</p>
              </div>
              <Zap className="h-4 w-4 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1">
          <span className="text-xs text-neutral-400">Time:</span>
          {(['1h', '6h', '24h', '7d'] as const).map(range => (
            <Button
              key={range}
              variant={timeRange === range ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setTimeRange(range)}
              className="h-6 px-2 text-xs"
            >
              {range}
            </Button>
          ))}
        </div>
        
        <div className="flex items-center gap-1">
          <span className="text-xs text-neutral-400">Category:</span>
          <Button
            variant={categoryFilter === 'all' ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setCategoryFilter('all')}
            className="h-6 px-2 text-xs"
          >
            All
          </Button>
          {Object.entries(categoryLabels).map(([key, label]) => (
            <Button
              key={key}
              variant={categoryFilter === key ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setCategoryFilter(key)}
              className="h-6 px-2 text-xs"
            >
              {label}
            </Button>
          ))}
        </div>
        
        <div className="flex items-center gap-1">
          <span className="text-xs text-neutral-400">Sort:</span>
          {([
            { key: 'calls', label: 'Calls' },
            { key: 'duration', label: 'Duration' }, 
            { key: 'errors', label: 'Errors' },
            { key: 'performance', label: 'Performance' }
          ] as const).map(({ key, label }) => (
            <Button
              key={key}
              variant={sortBy === key ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setSortBy(key)}
              className="h-6 px-2 text-xs"
            >
              {label}
            </Button>
          ))}
        </div>
      </div>

      <div className={`grid gap-4 ${isExpanded ? 'grid-cols-1 xl:grid-cols-2' : 'grid-cols-1'}`}>
        {/* Tool Metrics Table */}
        <Card className="bg-neutral-800/30 border-neutral-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Tool Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent className="p-3">
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredMetrics.slice(0, 12).map((metric, index) => (
                <div key={metric.name} className="flex items-center justify-between p-2 rounded bg-neutral-800/30">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className={`w-3 h-3 rounded-full ${categoryColors[metric.category]}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white truncate">{metric.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {categoryLabels[metric.category]}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-xs text-neutral-400">{metric.calls} calls</span>
                        <span className="text-xs text-neutral-400">{formatDuration(metric.avgDuration)} avg</span>
                        <span className="text-xs text-neutral-400">{metric.successRate.toFixed(1)}% success</span>
                        {metric.errorCount > 0 && (
                          <span className="text-xs text-red-400">{metric.errorCount} errors</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-neutral-400">
                    P95: {formatDuration(metric.p95Duration)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Activity Heatmap */}
        <Card className="bg-neutral-800/30 border-neutral-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">7-Day Activity Heatmap</CardTitle>
          </CardHeader>
          <CardContent className="p-3">
            <div className="space-y-2">
              {/* Hour labels */}
              <div className="grid grid-cols-25 gap-px">
                <div className="w-8" />
                {Array.from({ length: 24 }, (_, i) => (
                  <div key={i} className="text-xs text-neutral-400 text-center w-3">
                    {i % 6 === 0 ? i : ''}
                  </div>
                ))}
              </div>
              
              {/* Days and cells */}
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, dayIndex) => (
                <div key={day} className="grid grid-cols-25 gap-px">
                  <div className="w-8 text-xs text-neutral-400 pr-2">{day}</div>
                  {Array.from({ length: 24 }, (_, hour) => {
                    const cell = heatmapData.find(c => c.day === day && c.hour === hour);
                    const intensity = getIntensityColor(cell?.value || 0, maxHeatmapValue);
                    return (
                      <div
                        key={hour}
                        className={`w-3 h-3 rounded-sm ${intensity} border border-neutral-700/30`}
                        title={cell ? `${day} ${hour}:00 - ${cell.calls} calls, ${formatDuration(cell.avgDuration)} avg${cell.errors > 0 ? `, ${cell.errors} errors` : ''}` : `${day} ${hour}:00 - No activity`}
                      />
                    );
                  })}
                </div>
              ))}
              
              {/* Legend */}
              <div className="flex items-center gap-2 text-xs text-neutral-400 mt-3 pt-2 border-t border-neutral-700">
                <span>Less</span>
                <div className="flex gap-px">
                  {[0, 0.2, 0.4, 0.6, 0.8, 1].map((intensity, i) => (
                    <div key={i} className={`w-3 h-3 rounded-sm ${getIntensityColor(intensity * maxHeatmapValue, maxHeatmapValue)}`} />
                  ))}
                </div>
                <span>More</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {filteredMetrics.length === 0 && (
        <div className="text-center py-8 text-neutral-400">
          <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No tool activity data available for the selected time range.</p>
        </div>
      )}
    </div>
  );
}