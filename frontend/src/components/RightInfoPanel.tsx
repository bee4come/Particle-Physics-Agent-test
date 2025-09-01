
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Users, 
  ScrollText, 
  History,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RightInfoPanelProps {
  activeTab: 'agents' | 'logs' | 'versions';
  onTabChange: (tab: 'agents' | 'logs' | 'versions') => void;
  
  // Agent data
  agentEvents?: Array<{
    id: string;
    title: string;
    status: 'idle' | 'processing' | 'completed' | 'error';
    progress: number;
    timestamp: number;
    data: string;
    details?: string;
  }>;
  
  // Log data
  logs?: Array<{
    id: string;
    level: 'info' | 'warning' | 'error';
    message: string;
    timestamp: number;
    source?: string;
  }>;
  
  // Version data
  versions?: Array<{
    id: string;
    timestamp: number;
    triggerSource: string;
    summary: string;
    starred?: boolean;
  }>;
  
  className?: string;
}

export function RightInfoPanel({
  activeTab,
  onTabChange,
  agentEvents = [],
  logs = [],
  versions = [],
  className
}: RightInfoPanelProps) {
  
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'processing':
        return <div className="h-4 w-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      default:
        return <Activity className="h-4 w-4 text-neutral-400" />;
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-400 bg-red-500/10 border-red-500/30';
      case 'warning':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      default:
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
    }
  };

  return (
    <div className={cn("flex flex-col h-full bg-neutral-900", className)}>
      <Tabs value={activeTab} onValueChange={(value) => onTabChange(value as 'agents' | 'logs' | 'versions')} className="flex flex-col h-full">
        {/* Tab Headers */}
        <div className="flex-shrink-0 border-b border-neutral-800 px-4 py-2">
          <TabsList className="grid w-full grid-cols-3 bg-neutral-800">
            <TabsTrigger 
              value="agents" 
              className="flex items-center gap-2 data-[state=active]:bg-neutral-700"
            >
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Agents</span>
              {agentEvents.length > 0 && (
                <Badge variant="secondary" className="text-xs px-1 py-0 ml-1">
                  {agentEvents.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger 
              value="logs" 
              className="flex items-center gap-2 data-[state=active]:bg-neutral-700"
            >
              <ScrollText className="h-4 w-4" />
              <span className="hidden sm:inline">Logs</span>
              {logs.length > 0 && (
                <Badge variant="secondary" className="text-xs px-1 py-0 ml-1">
                  {logs.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger 
              value="versions" 
              className="flex items-center gap-2 data-[state=active]:bg-neutral-700"
            >
              <History className="h-4 w-4" />
              <span className="hidden sm:inline">Versions</span>
              {versions.length > 0 && (
                <Badge variant="secondary" className="text-xs px-1 py-0 ml-1">
                  {versions.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          {/* Agents Tab */}
          <TabsContent value="agents" className="h-full m-0 p-0">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-3">
                {agentEvents.length > 0 ? (
                  agentEvents.map((event) => (
                    <div
                      key={event.id}
                      className="p-3 rounded-lg bg-neutral-800 border border-neutral-700 space-y-2"
                    >
                      {/* Agent Header */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(event.status)}
                          <span className="text-sm font-medium text-neutral-200">
                            {event.title}
                          </span>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-neutral-400">
                          <Clock className="h-3 w-3" />
                          {formatTimestamp(event.timestamp)}
                        </div>
                      </div>

                      {/* Progress Bar */}
                      {event.status === 'processing' && (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-neutral-400">Progress</span>
                            <span className="text-neutral-300">{event.progress}%</span>
                          </div>
                          <div className="w-full bg-neutral-700 rounded-full h-1.5">
                            <div 
                              className="h-1.5 bg-blue-500 rounded-full transition-all duration-500"
                              style={{ width: `${event.progress}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {/* Agent Description */}
                      <p className="text-sm text-neutral-300">
                        {event.data}
                      </p>

                      {/* Details */}
                      {event.details && (
                        <div className="text-xs text-neutral-400 bg-neutral-900 p-2 rounded border">
                          {event.details.length > 150 
                            ? `${event.details.substring(0, 150)}...` 
                            : event.details
                          }
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="flex items-center justify-center h-32 text-neutral-500">
                    <div className="text-center space-y-2">
                      <Users className="h-8 w-8 mx-auto opacity-50" />
                      <p className="text-sm">No agent activity yet</p>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs" className="h-full m-0 p-0">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-2">
                {logs.length > 0 ? (
                  logs.map((log) => (
                    <div
                      key={log.id}
                      className={cn(
                        "p-3 rounded-lg border text-sm",
                        getLogLevelColor(log.level)
                      )}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge 
                              variant="outline" 
                              className="text-xs px-1 py-0 uppercase"
                            >
                              {log.level}
                            </Badge>
                            {log.source && (
                              <span className="text-xs opacity-75">
                                {log.source}
                              </span>
                            )}
                          </div>
                          <p className="leading-relaxed">
                            {log.message}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 text-xs opacity-75 flex-shrink-0">
                          <Clock className="h-3 w-3" />
                          {formatTimestamp(log.timestamp)}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex items-center justify-center h-32 text-neutral-500">
                    <div className="text-center space-y-2">
                      <ScrollText className="h-8 w-8 mx-auto opacity-50" />
                      <p className="text-sm">No logs available</p>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Versions Tab */}
          <TabsContent value="versions" className="h-full m-0 p-0">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-3">
                {versions.length > 0 ? (
                  versions.map((version) => (
                    <div
                      key={version.id}
                      className="p-3 rounded-lg bg-neutral-800 border border-neutral-700 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-400 rounded-full" />
                          <span className="text-sm font-medium text-neutral-200">
                            Version {version.id}
                          </span>
                          {version.starred && (
                            <span className="text-yellow-400">⭐</span>
                          )}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-neutral-400">
                          <Clock className="h-3 w-3" />
                          {formatTimestamp(version.timestamp)}
                        </div>
                      </div>

                      <div className="space-y-1">
                        <Badge 
                          variant="outline" 
                          className="text-xs px-2 py-0.5 bg-neutral-700 border-neutral-600"
                        >
                          {version.triggerSource}
                        </Badge>
                        <p className="text-sm text-neutral-300">
                          {version.summary}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex items-center justify-center h-32 text-neutral-500">
                    <div className="text-center space-y-2">
                      <History className="h-8 w-8 mx-auto opacity-50" />
                      <p className="text-sm">No versions saved yet</p>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}