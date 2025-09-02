import { useState, useCallback, useRef, useEffect } from 'react';
import { useAdvancedPolling, EnhancedEvent, TraceInfo } from './useAdvancedPolling';

export interface ADKMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
  author?: string;
}

export interface ProcessedEvent {
  title: string;
  data: string;
  timestamp: number;
  author: string;
  details?: string;
  traceInfo?: TraceInfo;
  status?: 'pending' | 'success' | 'error';
}

export interface ConnectionStatus {
  isConnected: boolean;
  lastChecked: number;
  error?: string;
  serverInfo?: {
    edition?: string;
    uptime?: number;
    tools_count?: number;
    cors_status?: string;
  };
}

export const useADKEnhanced = () => {
  const [messages, setMessages] = useState<ADKMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState<EnhancedEvent[]>([]);
  const [processedEvents, setProcessedEvents] = useState<ProcessedEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({ 
    isConnected: true, 
    lastChecked: Date.now() 
  });
  const [isWorkflowComplete, setIsWorkflowComplete] = useState(false);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const connectionCheckRef = useRef<NodeJS.Timeout | null>(null);
  
  const { 
    startPolling, 
    stopPolling, 
    processEventsWithTracing, 
    getPollingStatus,
    pollingState 
  } = useAdvancedPolling();

  // Enhanced connection check with server info
  const checkConnection = useCallback(async (): Promise<boolean> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('/list-apps', {
        method: 'GET',
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        // Try to get additional server info
        let serverInfo = {};
        try {
          const mcpResponse = await fetch('http://localhost:8002/health');
          if (mcpResponse.ok) {
            const mcpInfo = await mcpResponse.json();
            serverInfo = {
              edition: mcpInfo.edition || 'Unknown',
              uptime: mcpInfo.uptime_sec || 0,
              tools_count: Array.isArray(mcpInfo.tools) ? mcpInfo.tools.length : 0,
              cors_status: 'OK'
            };
          }
        } catch (e) {
          // MCP info optional
        }
        
        setConnectionStatus({ 
          isConnected: true, 
          lastChecked: Date.now(),
          serverInfo
        });
        return true;
      } else {
        setConnectionStatus({ 
          isConnected: false, 
          lastChecked: Date.now(),
          error: `Backend responded with status ${response.status}` 
        });
        return false;
      }
    } catch (err: any) {
      const errorMessage = err.name === 'AbortError' 
        ? 'Connection timeout - backend may be starting up'
        : 'Backend not responding - please check if ADK server is running';
        
      setConnectionStatus({ 
        isConnected: false, 
        lastChecked: Date.now(),
        error: errorMessage
      });
      return false;
    }
  }, []);

  // Enhanced event processing with better error handling
  const processEvents = useCallback((eventList: EnhancedEvent[]): ProcessedEvent[] => {
    const processed: ProcessedEvent[] = [];
    const seenSteps = new Set<string>();
    
    eventList.forEach((event, index) => {
      let processedEvent: ProcessedEvent | null = null;
      
      // Check for duplicates using stepId if available
      const stepKey = event.traceInfo?.stepId || `${event.author}_${index}`;
      if (seenSteps.has(stepKey) && event.author === 'planner_agent') {
        // Skip duplicate planning requests
        return;
      }
      seenSteps.add(stepKey);
      
      // Process based on author with enhanced trace info
      const baseEvent = {
        timestamp: event.timestamp * 1000,
        author: event.author,
        traceInfo: event.traceInfo,
        status: 'success' as const
      };
      
      if (event.author === 'planner_agent') {
        let details = '';
        if (event.content?.parts) {
          const textParts = event.content.parts
            .filter((part: any) => part.text)
            .map((part: any) => part.text)
            .join('');
          details = textParts.substring(0, 200) + (textParts.length > 200 ? '...' : '');
        }
        
        processedEvent = {
          ...baseEvent,
          title: "📋 Planning Request",
          data: "Analyzing request and creating execution plan",
          details
        };
      } else if (event.author === 'deep_research_agent') {
        let details = '';
        if (event.content?.parts) {
          const funcCall = event.content.parts.find((part: any) => part.functionCall);
          if (funcCall) {
            details = `Researching: ${funcCall.functionCall.args?.topic || 'Unknown topic'}`;
          }
        }
        
        processedEvent = {
          ...baseEvent,
          title: "🔬 Deep Research",
          data: "Performing comprehensive research on physics topic",
          details
        };
      } else if (event.author === 'kb_retriever_agent') {
        processedEvent = {
          ...baseEvent,
          title: "📚 Knowledge Base Search",
          data: "Searching for similar Feynman diagram examples"
        };
      } else if (event.author === 'physics_validator_agent') {
        processedEvent = {
          ...baseEvent,
          title: "⚖️ Physics Validation",
          data: "Validating particle interactions and physics rules"
        };
      } else if (event.author === 'diagram_generator_agent') {
        processedEvent = {
          ...baseEvent,
          title: "🎨 Diagram Generation",
          data: "Generating TikZ-Feynman LaTeX code"
        };
      } else if (event.author === 'tikz_validator_agent') {
        processedEvent = {
          ...baseEvent,
          title: "⚙️ LaTeX Compilation",
          data: "Compiling and validating TikZ code"
        };
      } else if (event.author === 'feedback_agent') {
        processedEvent = {
          ...baseEvent,
          title: "✅ Final Response",
          data: "Preparing Feynman diagram output"
        };
      } else if (event.author === 'root_agent') {
        // Check if this is a transfer event
        if (event.actions?.transferToAgent) {
          processedEvent = {
            ...baseEvent,
            title: "🔄 Agent Transfer",
            data: `Transferring to ${event.actions.transferToAgent}`
          };
        }
      }
      
      if (processedEvent) {
        processed.push(processedEvent);
      }
    });
    
    return processed;
  }, []);

  // Enhanced session polling
  const pollSession = useCallback(async (sessionId: string) => {
    console.log(`Polling session: ${sessionId}`);
    const response = await fetch(`/apps/feynmancraft_adk/users/user/sessions/${sessionId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        console.log(`Session ${sessionId} not found (404)`);
        setError('Session expired. Please try again.');
        setIsLoading(false);
        stopPolling();
        throw new Error('Session not found');
      }
      throw new Error(`Session polling failed: ${response.status}`);
    }
    
    const session = await response.json();
    console.log(`Session ${sessionId} has ${session.events?.length || 0} events`);
    
    // Process events with tracing
    const rawEvents = session.events || [];
    const enhancedEvents = processEventsWithTracing(rawEvents);
    setEvents(enhancedEvents);
    
    const processed = processEvents(enhancedEvents);
    setProcessedEvents(processed);
    
    // Improved completion detection
    const events = session.events || [];
    if (events.length > 0) {
      const lastEvent = events[events.length - 1];
      
      // Check for completion conditions
      const hasCompletedWorkflow = events.some((event: any) => event.author === 'feedback_agent');
      const hasNoRecentActivity = lastEvent && (Date.now() - lastEvent.timestamp * 1000) > 60000; // 60 seconds
      const hasSufficientProgress = events.length > 5; // At least 5 events
      
      if (hasCompletedWorkflow || (hasNoRecentActivity && hasSufficientProgress)) {
        console.log('Workflow completed, extracting results...');
        setIsLoading(false);
        setIsWorkflowComplete(true);
        stopPolling();
        
        // Extract final assistant message
        const assistantMessages: ADKMessage[] = [];
        
        // Look for feedback_agent messages first
        const feedbackEvents = events.filter((event: any) => event.author === 'feedback_agent');
        if (feedbackEvents.length > 0) {
          const feedbackEvent = feedbackEvents[feedbackEvents.length - 1];
          if (feedbackEvent.content?.parts) {
            const textParts = feedbackEvent.content.parts
              .filter((part: any) => part.text)
              .map((part: any) => part.text)
              .join('');
              
            if (textParts.trim()) {
              assistantMessages.push({
                id: feedbackEvent.id,
                content: textParts,
                role: 'assistant',
                timestamp: feedbackEvent.timestamp * 1000,
                author: feedbackEvent.author
              });
            }
          }
        }
        
        if (assistantMessages.length === 0) {
          events.reverse().forEach((event: any) => {
            if (event.content?.parts && event.author !== 'user' && event.author !== 'root_agent') {
              const textParts = event.content.parts
                .filter((part: any) => part.text && !part.functionCall && !part.functionResponse)
                .map((part: any) => part.text)
                .join('');
                
              if (textParts.trim() && assistantMessages.length === 0) {
                assistantMessages.push({
                  id: event.id,
                  content: textParts,
                  role: 'assistant',
                  timestamp: event.timestamp * 1000,
                  author: event.author
                });
              }
            }
          });
        }

        if (assistantMessages.length > 0) {
          setMessages(prev => [...prev, assistantMessages[0]]);
        } else {
          setError('No response received from agents. Please try again.');
        }
      }
    }
  }, [processEventsWithTracing, processEvents, stopPolling]);

  const sendMessage = useCallback(async (text: string) => {
    // First check connection
    const isConnected = await checkConnection();
    if (!isConnected) {
      setError('Cannot connect to backend. Please ensure ADK server is running on port 8000.');
      return;
    }

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    stopPolling();
    
    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    setIsLoading(true);
    setEvents([]);
    setProcessedEvents([]);
    setError(null);
    setIsWorkflowComplete(false);
    
    try {
      // Add user message immediately
      const userMessage: ADKMessage = {
        id: Date.now().toString(),
        content: text,
        role: 'user',
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, userMessage]);

      // Create session
      const sessionResponse = await fetch('/apps/feynmancraft_adk/users/user/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          state: {},
          events: []
        })
      });
      
      if (!sessionResponse.ok) {
        throw new Error(`Failed to create session: ${sessionResponse.status} ${sessionResponse.statusText}`);
      }
      
      const session = await sessionResponse.json();
      sessionIdRef.current = session.id;
      setCurrentSessionId(session.id);
      console.log('Created session:', session.id);
      
      // Start the request (fire and forget)
      fetch('/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          appName: "feynmancraft_adk",
          userId: "user",
          sessionId: session.id,
          newMessage: {
            parts: [{ text }],
            role: "user"
          },
          streaming: false
        })
      }).catch(err => {
        console.error('Request error:', err);
      });
      
      // Start enhanced polling
      startPolling(async () => {
        const sessionId = sessionIdRef.current || currentSessionId;
        if (sessionId) {
          await pollSession(sessionId);
        }
      });

    } catch (error: any) {
      setError(`Failed to start request: ${error.message}`);
      setIsLoading(false);
      stopPolling();
    }
  }, [checkConnection, pollSession, stopPolling, startPolling]);

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    stopPolling();
    setIsLoading(false);
    setError(null);
  }, [stopPolling]);

  // Initialize connection monitoring
  useEffect(() => {
    checkConnection();
    
    return () => {
      stopPolling();
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [checkConnection, stopPolling]);

  return {
    messages,
    events,
    processedEvents,
    isLoading,
    error,
    connectionStatus,
    sendMessage,
    stop,
    checkConnection,
    pollingStatus: getPollingStatus(),
    pollingState
  };
};