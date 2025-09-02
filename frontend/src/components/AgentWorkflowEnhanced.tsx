import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Clock, BarChart3, Minimize2, Maximize2 } from 'lucide-react';

interface ProcessedEvent {
  title: string;
  data: string;
  timestamp: number;
  author: string;
  details?: string;
  traceInfo?: {
    traceId: string;
    stepId: string;
    tool?: string;
    duration?: number;
  };
}

interface EventGroup {
  type: 'Planning' | 'Transfer' | 'Search' | 'Validation' | 'Generation' | 'Compilation' | 'Response' | 'Other';
  events: ProcessedEvent[];
  totalDuration: number;
  avgDuration: number;
  p50Duration: number;
  p95Duration: number;
}

interface AgentWorkflowEnhancedProps {
  events: ProcessedEvent[];
  isLoading: boolean;
  isCompleted?: boolean;
  pollingStatus?: string;
}

export function AgentWorkflowEnhanced({ events, isLoading, isCompleted, pollingStatus }: AgentWorkflowEnhancedProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());
  const [showLatencies, setShowLatencies] = useState(false);
  
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatDuration = (duration: number) => {
    return `${duration}ms`;
  };

  // Group events by stage type with deduplication
  const groupEvents = (): EventGroup[] => {
    const groups = new Map<string, ProcessedEvent[]>();
    const seenEvents = new Set<string>();
    
    events.forEach(event => {
      // Create unique key to prevent duplicates
      const eventKey = `${event.author}_${event.title}_${Math.floor(event.timestamp / 1000)}`;
      if (seenEvents.has(eventKey)) return;
      seenEvents.add(eventKey);
      
      let groupType = 'Other';
      
      if (event.title.includes('Planning')) {
        groupType = 'Planning';
      } else if (event.title.includes('Transfer')) {
        groupType = 'Transfer';
      } else if (event.title.includes('Search')) {
        groupType = 'Search';
      } else if (event.title.includes('Validation')) {
        groupType = 'Validation';
      } else if (event.title.includes('Generation')) {
        groupType = 'Generation';
      } else if (event.title.includes('Compilation')) {
        groupType = 'Compilation';
      } else if (event.title.includes('Response')) {
        groupType = 'Response';
      }
      
      if (!groups.has(groupType)) {
        groups.set(groupType, []);
      }
      groups.get(groupType)!.push(event);
    });

    // Convert to EventGroup array with statistics
    return Array.from(groups.entries()).map(([type, groupEvents]) => {
      const durations = groupEvents
        .map(e => e.traceInfo?.duration || 0)
        .filter(d => d > 0)
        .sort((a, b) => a - b);

      const totalDuration = durations.reduce((sum, d) => sum + d, 0);
      const avgDuration = durations.length > 0 ? Math.round(totalDuration / durations.length) : 0;
      const p50Duration = durations.length > 0 ? durations[Math.floor(durations.length * 0.5)] : 0;
      const p95Duration = durations.length > 0 ? durations[Math.floor(durations.length * 0.95)] : 0;

      return {
        type: type as EventGroup['type'],
        events: groupEvents,
        totalDuration,
        avgDuration,
        p50Duration,
        p95Duration
      };
    }).sort((a, b) => {
      // Sort by first event timestamp in group
      const aTime = Math.min(...a.events.map(e => e.timestamp));
      const bTime = Math.min(...b.events.map(e => e.timestamp));
      return aTime - bTime;
    });
  };

  const toggleGroup = (groupType: string) => {
    const newCollapsed = new Set(collapsedGroups);
    if (newCollapsed.has(groupType)) {
      newCollapsed.delete(groupType);
    } else {
      newCollapsed.add(groupType);
    }
    setCollapsedGroups(newCollapsed);
  };

  const collapseAll = () => {
    const allGroups = groupEvents().map(g => g.type);
    setCollapsedGroups(new Set(allGroups));
  };

  const expandAll = () => {
    setCollapsedGroups(new Set());
  };

  const eventGroups = groupEvents();

  // Always show workflow if loading or has events
  if (!isLoading && events.length === 0) {
    return null;
  }

  const getGroupIcon = (type: EventGroup['type']) => {
    switch (type) {
      case 'Planning': return '📋';
      case 'Transfer': return '🔄';
      case 'Search': return '📚';
      case 'Validation': return '⚖️';
      case 'Generation': return '🎨';
      case 'Compilation': return '⚙️';
      case 'Response': return '✅';
      default: return '📌';
    }
  };

  const getGroupColor = (type: EventGroup['type']) => {
    switch (type) {
      case 'Planning': return 'bg-blue-500/10 border-blue-500/30';
      case 'Transfer': return 'bg-purple-500/10 border-purple-500/30';
      case 'Search': return 'bg-green-500/10 border-green-500/30';
      case 'Validation': return 'bg-yellow-500/10 border-yellow-500/30';
      case 'Generation': return 'bg-orange-500/10 border-orange-500/30';
      case 'Compilation': return 'bg-red-500/10 border-red-500/30';
      case 'Response': return 'bg-emerald-500/10 border-emerald-500/30';
      default: return 'bg-gray-500/10 border-gray-500/30';
    }
  };

  return (
    <div className="relative group max-w-[85%] md:max-w-[80%] rounded-xl p-3 shadow-sm break-words bg-neutral-700 text-neutral-100 rounded-bl-none w-full">
      {/* Enhanced Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-medium text-neutral-200">
            🔄 Agent Workflow {isCompleted && '(Completed)'}
          </h4>
          {eventGroups.length > 1 && (
            <Badge variant="secondary" className="text-xs">
              {eventGroups.length} stages
            </Badge>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          {events.length > 0 && (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowLatencies(!showLatencies)}
                className="h-6 px-2 text-xs"
                title="Toggle latency display"
              >
                <BarChart3 className="h-3 w-3" />
              </Button>
              
              {eventGroups.length > 1 && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={collapseAll}
                    className="h-6 px-2 text-xs"
                    title="Collapse all stages"
                  >
                    <Minimize2 className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={expandAll}
                    className="h-6 px-2 text-xs"
                    title="Expand all stages"
                  >
                    <Maximize2 className="h-3 w-3" />
                  </Button>
                </>
              )}
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="h-6 px-2 text-xs"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="h-3 w-3 mr-1" />
                    Collapse
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-3 w-3 mr-1" />
                    Expand ({events.length} events)
                  </>
                )}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Event timeline with swim lanes */}
      {isExpanded && (
        <div className="space-y-3">
          {eventGroups.map((group) => {
            const isGroupCollapsed = collapsedGroups.has(group.type);
            
            return (
              <div 
                key={group.type}
                className={`border-l-4 pl-3 rounded-r-lg ${getGroupColor(group.type)}`}
              >
                {/* Group Header */}
                <div 
                  className="flex items-center justify-between py-2 cursor-pointer hover:bg-neutral-800/30 rounded px-2 -ml-2"
                  onClick={() => toggleGroup(group.type)}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-base">{getGroupIcon(group.type)}</span>
                    <span className="font-medium text-sm">{group.type}</span>
                    <Badge variant="outline" className="text-xs">
                      {group.events.length}
                    </Badge>
                    {showLatencies && group.p50Duration > 0 && (
                      <div className="flex items-center gap-2 text-xs text-neutral-400">
                        <span>P50: {formatDuration(group.p50Duration)}</span>
                        <span>P95: {formatDuration(group.p95Duration)}</span>
                        <span>Avg: {formatDuration(group.avgDuration)}</span>
                      </div>
                    )}
                  </div>
                  {isGroupCollapsed ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />}
                </div>

                {/* Group Events */}
                {!isGroupCollapsed && (
                  <div className="space-y-1 ml-4">
                    {group.events.map((event, index) => (
                      <div 
                        key={`${event.author}-${index}`}
                        className="flex items-start gap-2 p-2 rounded bg-neutral-800/30 text-xs"
                      >
                        <div className="flex flex-col flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="secondary" className="text-xs px-2 py-0.5">
                              {event.title}
                            </Badge>
                            <span className="text-xs text-neutral-400 flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatTimestamp(event.timestamp)}
                            </span>
                            {event.traceInfo && (
                              <span className="text-xs text-neutral-500 font-mono">
                                #{event.traceInfo.traceId}
                                {event.traceInfo.duration && (
                                  <span className="text-green-400 ml-1">
                                    • {formatDuration(event.traceInfo.duration)}
                                  </span>
                                )}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-neutral-300">
                            {event.data}
                          </p>
                          {event.details && (
                            <div className="text-xs text-neutral-400 mt-1 bg-neutral-900/50 p-1.5 rounded">
                              {event.details.length > 100 ? `${event.details.substring(0, 100)}...` : event.details}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
          
          {/* Enhanced loading indicator */}
          {isLoading && !isCompleted && (
            <div className="flex items-center gap-2 pt-2 border-l-4 border-blue-500/30 pl-3">
              <div className="animate-spin h-3 w-3 border border-blue-400 border-t-transparent rounded-full"></div>
              <span className="text-sm text-neutral-300">
                {pollingStatus || 'Processing...'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Collapsed summary */}
      {!isExpanded && eventGroups.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-neutral-400">
          <span>Stages: {eventGroups.map(g => `${getGroupIcon(g.type)} ${g.events.length}`).join(', ')}</span>
          {showLatencies && (
            <span className="ml-2">
              Total time: {formatDuration(eventGroups.reduce((sum, g) => sum + g.totalDuration, 0))}
            </span>
          )}
        </div>
      )}
    </div>
  );
}