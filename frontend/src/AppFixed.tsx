import { useState, useEffect, useRef, useCallback } from "react";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import { useADKEnhanced } from "@/hooks/useADKEnhanced";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ReactMarkdown from "react-markdown";
import { Copy, CopyCheck, AlertCircle, User, Bot, Wifi, WifiOff, RefreshCw, Server, Terminal } from "lucide-react";
import { AgentWorkflow } from "@/components/AgentWorkflow";
import { AgentWorkflowEnhanced } from "@/components/AgentWorkflowEnhanced";
import { LogPanelFixed } from "@/components/LogPanelFixed";
import { ErrorCard, StructuredError, parseErrorFromMessage, ErrorAction } from "@/components/ErrorCard";
import { ErrorCardPanel } from "@/components/ErrorCardPanel";
import { ToolOrchestrationDashboard } from "@/components/ToolOrchestrationDashboard";
// import { RightInfoPanel } from "@/components/RightInfoPanel";
import { useBackendLogger } from "@/hooks/useBackendLogger";

const MAX_HISTORICAL_WORKFLOWS = 10;

export default function AppFixed() {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [isLogPanelOpen, setIsLogPanelOpen] = useState(false);
  const [completedWorkflows, setCompletedWorkflows] = useState<Record<string, any>>({});
  const [shouldClearInput, setShouldClearInput] = useState(false);
  const [rightPanelTab, setRightPanelTab] = useState<'agents' | 'logs' | 'versions' | 'recovery' | 'automation' | 'mcp' | 'dashboard'>('agents');
  const [showDashboard, setShowDashboard] = useState(false);

  const { logs, logger, clearLogs, processADKEvents } = useBackendLogger();
  
  const { 
    messages, 
    processedEvents, 
    isLoading, 
    error, 
    connectionStatus,
    sendMessage, 
    stop,
    checkConnection,
    pollingStatus,
    pollingState,
    sseEnabled,
    sseConnectionStatus,
    toggleSSE,
    structuredErrors,
    dismissError,
    clearAllErrors,
    executeErrorAction
  } = useADKEnhanced();

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messages.length, processedEvents.length]);

  // Log connection status changes
  useEffect(() => {
    if (connectionStatus.isConnected) {
      logger.info('frontend', 'Backend connection established');
    } else if (connectionStatus.error) {
      logger.error('frontend', 'Backend connection lost', { error: connectionStatus.error });
    }
  }, [connectionStatus.isConnected, connectionStatus.error, logger]);

  // Enhanced error handling with structured errors
  useEffect(() => {
    if (error) {
      logger.error('frontend', 'Error occurred', error);
      
      // Parse error into structured format
      const structuredError = parseErrorFromMessage(error);
      if (structuredError) {
        setStructuredErrors(prev => {
          // Avoid duplicate errors
          const existingError = prev.find(e => 
            e.title === structuredError.title && 
            e.description === structuredError.description
          );
          if (existingError) return prev;
          
          // Keep only last 5 errors
          return [structuredError, ...prev.slice(0, 4)];
        });
      }
    }
  }, [error, logger]);

  // Process events for logging
  useEffect(() => {
    if (processedEvents.length > 0) {
      processADKEvents(processedEvents);
    }
  }, [processedEvents, processADKEvents]);

  // Save completed workflows with cleanup - fix infinite loop
  useEffect(() => {
    if (!isLoading && processedEvents.length > 0 && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant' && !completedWorkflows[lastMessage.id]) {
        setCompletedWorkflows(prev => {
          const updated = {
            ...prev,
            [lastMessage.id]: [...processedEvents]
          };
          
          // Cleanup old workflows
          const keys = Object.keys(updated);
          if (keys.length > MAX_HISTORICAL_WORKFLOWS) {
            const keysToDelete = keys.slice(0, keys.length - MAX_HISTORICAL_WORKFLOWS);
            keysToDelete.forEach(key => delete updated[key]);
          }
          
          return updated;
        });
        
        logger.info('frontend', 'Workflow completed', { 
          messageId: lastMessage.id, 
          steps: processedEvents.length 
        });
      }
    }
  }, [isLoading, processedEvents.length, messages.length]);

  const handleSubmit = useCallback(async (submittedInputValue: string) => {
    if (!submittedInputValue.trim()) return;
    
    setShouldClearInput(false);
    
    try {
      await sendMessage(submittedInputValue);
      setShouldClearInput(true);
    } catch (err) {
      console.error('Submit error:', err);
    }
  }, [sendMessage]);

  const handleCancel = useCallback(() => {
    stop();
  }, [stop]);

  const handleCopy = useCallback(async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  }, []);

  const handleRetry = useCallback(async () => {
    await checkConnection();
  }, [checkConnection]);

  const formatTimestamp = useCallback((timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  }, []);

  // Handle error card actions
  const handleErrorAction = useCallback((errorId: string, action: ErrorAction) => {
    setStructuredErrors(prev => {
      const errorIndex = prev.findIndex(e => e.id === errorId);
      if (errorIndex === -1) return prev;
      
      const updatedErrors = [...prev];
      const error = updatedErrors[errorIndex];
      
      switch (action) {
        case 'retry':
          // Increment retry count and attempt retry
          updatedErrors[errorIndex] = {
            ...error,
            retryCount: (error.retryCount || 0) + 1
          };
          logger.info('error-handling', `Retrying error: ${error.title}`, { errorId, retryCount: error.retryCount || 0 + 1 });
          // Could trigger actual retry logic here
          break;
          
        case 'degrade':
          // Mark as degraded and remove from active errors
          logger.info('error-handling', `Degrading gracefully for error: ${error.title}`, { errorId });
          return prev.filter(e => e.id !== errorId);
          
        case 'ignore':
          // Remove from active errors
          logger.info('error-handling', `Ignoring error: ${error.title}`, { errorId });
          return prev.filter(e => e.id !== errorId);
          
        default:
          break;
      }
      
      return updatedErrors;
    });
  }, [logger]);

  const toggleLogPanel = useCallback(() => {
    setIsLogPanelOpen(prev => !prev);
  }, []);

  // Copy server info for debugging
  const copyServerInfo = useCallback(async () => {
    const info = connectionStatus.serverInfo;
    const serverDetails = `
FeynmanCraft Demo Environment
============================
Backend: ${info?.edition || 'ADK'} 
Uptime: ${Math.floor((info?.uptime || 0) / 60)} minutes
MCP Tools: ${info?.tools_count || 0}
CORS Status: ${info?.cors_status || 'Unknown'}
Connection: ${connectionStatus.isConnected ? 'Connected' : 'Disconnected'}
Last Checked: ${new Date(connectionStatus.lastChecked).toISOString()}

Available Physics Tools:
- search_particle, get_property, list_decays
- find_decays, list_properties, resolve_identifier  
- database_info, get_property_details

Citation: ParticlePhysics MCP Server v1.0.0
Database: PDG 2025 edition
    `.trim();
    
    try {
      await navigator.clipboard.writeText(serverDetails);
      logger.info('frontend', 'Server info copied to clipboard');
    } catch (err) {
      console.error('Failed to copy server info:', err);
    }
  }, [connectionStatus, logger]);

  // Connection status indicator component
  const renderConnectionIndicator = () => (
    <div className="fixed top-4 right-4 z-50 flex items-center gap-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={toggleLogPanel}
        className={`h-8 px-3 text-xs ${isLogPanelOpen ? 'bg-neutral-700' : ''}`}
      >
        <Terminal className="h-3 w-3 mr-1" />
        Logs ({logs.length})
      </Button>
      
      <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs ${
        connectionStatus.isConnected 
          ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
          : 'bg-red-500/20 text-red-400 border border-red-500/30'
      }`}>
        {connectionStatus.isConnected ? (
          <>
            <Wifi className="h-3 w-3" />
            <span>
              {connectionStatus.serverInfo ? (
                <>
                  Connected • {connectionStatus.serverInfo.edition || 'ADK'} • 
                  {sseEnabled ? (
                    <span className={`${sseConnectionStatus.connected ? 'text-green-500' : 'text-yellow-500'}`}>
                      SSE {sseConnectionStatus.connected ? '✓' : '⚠'}
                    </span>
                  ) : (
                    <span className="text-blue-500">Polling</span>
                  )} • 
                  Uptime {Math.floor((connectionStatus.serverInfo.uptime || 0) / 60)}m • 
                  Tools: {connectionStatus.serverInfo.tools_count || 0}
                </>
              ) : (
                'Backend Connected'
              )}
            </span>
            {connectionStatus.serverInfo && (
              <Button
                variant="ghost"
                size="sm"
                onClick={copyServerInfo}
                className="h-5 w-5 p-0 hover:bg-green-500/20"
                title="Copy server info"
              >
                <Copy className="h-2 w-2" />
              </Button>
            )}
          </>
        ) : (
          <>
            <WifiOff className="h-3 w-3" />
            <span>
              {connectionStatus.error ? 
                `Disconnected: ${connectionStatus.error.substring(0, 30)}...` : 
                'Backend Disconnected'
              }
            </span>
          </>
        )}
      </div>
    </div>
  );

  // Function to safely render content
  const renderMessageContent = useCallback((content: string) => {
    try {
      // Check if content is JSON
      if ((content.trim().startsWith('{') && content.trim().endsWith('}')) || 
          (content.trim().startsWith('[') && content.trim().endsWith(']'))) {
        const parsed = JSON.parse(content);
        return (
          <pre className="overflow-x-auto text-xs bg-neutral-800 p-2 rounded max-w-full">
            <code>{JSON.stringify(parsed, null, 2)}</code>
          </pre>
        );
      }
    } catch (e) {
      // Not JSON, render as markdown
    }
    
    return <ReactMarkdown>{content}</ReactMarkdown>;
  }, []);

  // Backend not connected screen
  if (!connectionStatus.isConnected && messages.length === 0) {
    return (
      <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
{renderConnectionIndicator()}
        <main className="h-full w-full max-w-4xl mx-auto">
          <div className="flex flex-col items-center justify-center h-full gap-6">
            <div className="flex flex-col items-center gap-4">
              <div className="flex items-center gap-3">
                <Server className="h-12 w-12 text-red-400" />
                <WifiOff className="h-8 w-8 text-red-400" />
              </div>
              <h1 className="text-3xl font-bold text-red-400">Backend Not Available</h1>
              <div className="text-center max-w-md">
                <p className="text-neutral-300 mb-2">
                  Cannot connect to the FeynmanCraft ADK backend server.
                </p>
                <p className="text-sm text-neutral-400">
                  {connectionStatus.error || 'Please ensure the backend is running on port 8000.'}
                </p>
              </div>
              
              <div className="flex flex-col gap-3 mt-4">
                <Button
                  onClick={handleRetry}
                  className="flex items-center gap-2"
                  variant="default"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry Connection
                </Button>
                
                <div className="text-xs text-neutral-500 text-center">
                  <p>To start the backend, run:</p>
                  <code className="bg-neutral-700 px-2 py-1 rounded mt-1 inline-block">
                    adk web . --port 8000
                  </code>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Render welcome screen
  if (messages.length === 0) {
    return (
      <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
{renderConnectionIndicator()}
        <main className="h-full w-full max-w-4xl mx-auto">
          <WelcomeScreen
            handleSubmit={handleSubmit}
            isLoading={isLoading}
            onCancel={handleCancel}
            shouldClearInput={shouldClearInput}
          />
        </main>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
{renderConnectionIndicator()}
        <main className="h-full w-full max-w-4xl mx-auto">
          <div className="flex flex-col items-center justify-center h-full">
            <div className="flex flex-col items-center justify-center gap-4">
              <AlertCircle className="h-16 w-16 text-red-400" />
              <h1 className="text-2xl text-red-400 font-bold">Request Error</h1>
              <p className="text-red-400 text-center max-w-md">{error}</p>
              <div className="flex gap-2">
                <Button
                  variant="destructive"
                  onClick={() => window.location.reload()}
                >
                  Refresh Page
                </Button>
                <Button
                  variant="outline"
                  onClick={handleRetry}
                >
                  Check Connection
                </Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased relative">
      {renderConnectionIndicator()}
      
      {/* Left side - Main chat area */}
      <div className="flex flex-col flex-1 xl:pr-[24rem] min-w-0">
        <ScrollArea ref={scrollAreaRef} className="flex-1 overflow-y-auto">
        <div className="p-4 md:p-6 space-y-2 max-w-4xl mx-auto pt-16">
          {messages.map((message, index) => {
            return (
              <div key={message.id || `msg-${index}`} className="space-y-3">
                <div
                  className={`flex items-start gap-3 ${
                    message.role === "user" ? "justify-end" : ""
                  }`}
                >
                  {message.role === "user" ? (
                    // Human message bubble
                    <div className="flex items-start gap-3 max-w-[85%] md:max-w-[80%]">
                      <div className="relative group rounded-xl p-3 shadow-sm break-words bg-blue-600 text-white rounded-br-none">
                        <div className="prose prose-invert max-w-none">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>
                      </div>
                      <div className="relative flex flex-shrink-0 mt-1">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-white text-xs font-medium">
                          <User className="h-3 w-3" />
                        </div>
                      </div>
                    </div>
                  ) : (
                    // AI message bubble
                    <div className="flex flex-col gap-2 w-full">
                      <div className="flex items-start gap-3 max-w-[85%] md:max-w-[80%] w-full">
                        <div className="relative flex flex-shrink-0 mt-1">
                          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-neutral-700 text-neutral-100 text-xs font-medium">
                            <Bot className="h-3 w-3" />
                          </div>
                        </div>
                        <div className="relative group rounded-xl p-3 shadow-sm break-words bg-neutral-700 text-neutral-100 rounded-bl-none w-full overflow-hidden">
                          <div className="prose prose-invert max-w-none">
                            {renderMessageContent(message.content)}
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="mt-2 text-neutral-400 hover:text-neutral-200 h-6 px-2"
                            onClick={() => handleCopy(message.content, message.id)}
                          >
                            {copiedMessageId === message.id ? (
                              <>
                                <CopyCheck className="h-3 w-3 mr-1" />
                                <span className="text-xs">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="h-3 w-3 mr-1" />
                                <span className="text-xs">Copy</span>
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                      
                      {/* Show completed workflow for this message */}
                      {completedWorkflows[message.id] && (
                        <div className="flex items-start gap-3 ml-9">
                          <AgentWorkflowEnhanced 
                            events={completedWorkflows[message.id]} 
                            isLoading={false} 
                            isCompleted={true}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          
          {/* Structured Error Cards */}
          <ErrorCardPanel 
            errors={structuredErrors}
            onDismissError={dismissError}
            onExecuteAction={executeErrorAction}
            onClearAllErrors={clearAllErrors}
          />
          
          {/* Loading state with activity timeline */}
          {isLoading && (
            <div className="flex items-start gap-3 mt-3">
              <div className="relative flex flex-shrink-0 mt-1">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-neutral-700 text-neutral-100 text-xs font-medium">
                  <Bot className="h-3 w-3" />
                </div>
              </div>
              <AgentWorkflowEnhanced 
                events={processedEvents} 
                isLoading={true} 
                isCompleted={false}
                pollingStatus={pollingStatus}
              />
            </div>
          )}
          
          {/* Structured Error Cards */}
          {structuredErrors.length > 0 && (
            <div className="flex flex-col gap-3 mt-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-400" />
                <span className="text-sm font-medium text-red-300">
                  Active Issues ({structuredErrors.length})
                </span>
              </div>
              {structuredErrors.map(error => (
                <ErrorCard
                  key={error.id}
                  error={error}
                  onAction={handleErrorAction}
                  isCompact={structuredErrors.length > 2}
                />
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
      
      {/* Input area - fixed at bottom */}
      <div className="flex-shrink-0 border-t border-neutral-700/50 bg-neutral-800">
        <div className="max-w-4xl mx-auto">
          <InputForm
            onSubmit={handleSubmit}
            isLoading={isLoading || !connectionStatus.isConnected}
            onCancel={handleCancel}
            hasHistory={messages.length > 0}
            shouldClearInput={shouldClearInput}
          />
        </div>
      </div>
      </div>
      
      {/* Right side - Tabbed Panel */}
      <div className="w-96 xl:w-96 border-l border-neutral-700/50 flex-shrink-0 bg-neutral-900 xl:absolute xl:right-0 xl:top-0 xl:h-full">
        <div className="h-full overflow-hidden flex flex-col">
          {/* Tab Header */}
          <div className="flex border-b border-neutral-700/50 bg-neutral-800/50">
            <Button
              variant={rightPanelTab === 'mcp' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setRightPanelTab('mcp')}
              className="flex-1 rounded-none border-r border-neutral-700/50 text-xs"
            >
              MCP
            </Button>
            <Button
              variant={rightPanelTab === 'dashboard' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setRightPanelTab('dashboard')}
              className="flex-1 rounded-none text-xs"
            >
              Dashboard
            </Button>
          </div>
          
          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {rightPanelTab === 'mcp' && (
              <div className="p-4">
                <h3 className="text-lg font-semibold mb-4 text-white">MCP Integration</h3>
          
          <div className="space-y-4">
            <div className="bg-neutral-800 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                <span className="font-medium text-white">ParticlePhysics MCP Server</span>
              </div>
              <p className="text-sm text-neutral-300">Running on port 8002</p>
              <p className="text-xs text-neutral-400 mt-1">HTTP API integration active</p>
            </div>
            
            <div className="bg-neutral-800 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="h-2 w-2 bg-blue-400 rounded-full"></div>
                <span className="font-medium text-white">ADK Backend Integration</span>
              </div>
              <p className="text-sm text-neutral-300">Modified to use HTTP MCP client</p>
              <p className="text-xs text-neutral-400 mt-1">Fallback to subprocess if needed</p>
            </div>
            
            <div className="bg-neutral-800 p-4 rounded-lg">
              <h4 className="font-medium mb-2 text-white">Available Tools</h4>
              <div className="grid grid-cols-1 gap-1 text-xs">
                <div className="text-neutral-300">• search_particle</div>
                <div className="text-neutral-300">• get_property</div>
                <div className="text-neutral-300">• list_decays</div>
                <div className="text-neutral-300">• find_decays</div>
                <div className="text-neutral-300">• list_properties</div>
                <div className="text-neutral-300">• resolve_identifier</div>
                <div className="text-neutral-300">• database_info</div>
                <div className="text-neutral-300">• get_property_details</div>
              </div>
            </div>
            
            {processedEvents.length > 0 && (
              <div className="bg-neutral-800 p-4 rounded-lg">
                <h4 className="font-medium mb-2 text-white">Agent Workflow</h4>
                <div className="space-y-2">
                  {processedEvents.slice(-5).map((event, index) => (
                    <div key={index} className="text-xs">
                      <div className="text-neutral-300">{event.title}</div>
                      <div className="text-neutral-500">{event.data}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
                </div>
              </div>
            )}
            
            {rightPanelTab === 'dashboard' && (
              <div className="p-2">
                <ToolOrchestrationDashboard 
                  events={processedEvents}
                  isLive={isLoading}
                  onRefresh={() => window.location.reload()}
                />
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Log Panel */}
      <LogPanelFixed 
        isOpen={isLogPanelOpen}
        onClose={() => setIsLogPanelOpen(false)}
        logs={logs}
        onClear={clearLogs}
      />
    </div>
  );
}