import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Code2,
  MessageSquare,
  Send,
  Terminal,
  Users,
  Zap,
  Loader2,
  Bot,
  User,
  ChevronRight,
  Sparkles,
  Trash2,
  Plus,
  ChevronDown,
  ChevronUp,
  Bug,
} from "lucide-react";

const apiUrl = import.meta.env.VITE_API_URL;

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [stats, setStats] = useState(null);
  const [codeExecution, setCodeExecution] = useState(null);
  const messagesScrollRef = useRef(null);
  const inputRef = useRef(null);

  // Conversation state management
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);

  // Streaming state management
  const [streamingEvents, setStreamingEvents] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingStatus, setStreamingStatus] = useState(null);

  // Debug panel state
  const [debugData, setDebugData] = useState([]);
  const [codeExecutions, setCodeExecutions] = useState([]);
  const [isDebugOpen, setIsDebugOpen] = useState(false);

  // Fetch initial stats and conversations
  useEffect(() => {
    const initialize = async () => {
      await fetchStats();
      await fetchConversations();
    };
    initialize();
  }, []);

  // Auto-scroll messages to bottom when new messages arrive (only within chat box)
  useEffect(() => {
    const scrollElement = messagesScrollRef.current?.querySelector(
      "[data-radix-scroll-area-viewport]"
    );
    if (scrollElement) {
      scrollElement.scrollTop = scrollElement.scrollHeight;
    }
  }, [messages]);

  const fetchStats = async () => {
    try {
      const [teamRes, projectRes, incidentRes] = await Promise.all([
        fetch(`${apiUrl}/tools/team-members`),
        fetch(`${apiUrl}/tools/projects`),
        fetch(`${apiUrl}/tools/incidents`),
      ]);
      const [team, projects, incidents] = await Promise.all([
        teamRes.json(),
        projectRes.json(),
        incidentRes.json(),
      ]);

      const openIncidents = incidents.data.filter(
        (i) => i.status !== "resolved"
      );
      const p0Count = incidents.data.filter(
        (i) => i.severity === "P0" && i.status !== "resolved"
      ).length;

      setStats({
        teamCount: team.count,
        projectCount: projects.count,
        openIncidents: openIncidents.length,
        p0Incidents: p0Count,
        activeProjects: projects.data.filter((p) => p.status === "active")
          .length,
      });
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  const fetchConversations = async () => {
    try {
      setIsLoadingConversations(true);
      const response = await fetch(`${apiUrl}/conversations`);
      const data = await response.json();

      // Sort by updated_at descending (most recent first)
      const sortedConversations = data.conversations.sort(
        (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
      );

      setConversations(sortedConversations);

      // Auto-load most recent conversation if exists
      if (sortedConversations.length > 0) {
        await loadConversation(sortedConversations[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const response = await fetch(`${apiUrl}/conversations/${conversationId}`);
      const conversation = await response.json();

      // Map messages to format {role, content, created_at}
      const formattedMessages = conversation.messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
        created_at: msg.created_at,
      }));

      setMessages(formattedMessages);
      setCurrentConversationId(conversationId);
    } catch (err) {
      console.error("Failed to load conversation:", err);
    }
  };

  const deleteConversation = async (conversationId) => {
    try {
      await fetch(`${apiUrl}/conversations/${conversationId}`, {
        method: "DELETE",
      });

      // Remove from conversations list
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));

      // If deleted conversation was current, clear messages
      if (conversationId === currentConversationId) {
        setMessages([]);
        setCurrentConversationId(null);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
      alert("Failed to delete conversation. Please try again.");
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setCurrentConversationId(null);
    setCodeExecution(null);
    inputRef.current?.focus();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage = { role: "user", content: input.trim() };
    const inputText = input.trim();

    // Add user message to UI immediately
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);
    setStreamingEvents([]);
    setStreamingStatus("thinking");
    setCodeExecution(null);
    setDebugData([]); // Clear previous debug data
    setCodeExecutions([]); // Clear previous code executions

    try {
      let conversationId = currentConversationId;

      // Create new conversation if this is the first message
      if (!conversationId) {
        const createResponse = await fetch(`${apiUrl}/conversations`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: inputText.slice(0, 50),
          }),
        });
        const newConversation = await createResponse.json();
        conversationId = newConversation.id;
        setCurrentConversationId(conversationId);

        // Add to conversations list at the beginning
        setConversations((prev) => [
          {
            id: newConversation.id,
            title: newConversation.title,
            created_at: newConversation.created_at,
            updated_at: newConversation.updated_at,
            message_count: 0,
          },
          ...prev,
        ]);
      }

      // Save user message to backend
      await fetch(`${apiUrl}/conversations/${conversationId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: "user",
          content: inputText,
        }),
      });

      // Use fetch to stream events from Claude
      const response = await fetch(`${apiUrl}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: inputText,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Streaming API error: ${response.status}`);
      }

      // Read the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages (separated by \n\n)
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || ""; // Keep incomplete message in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const eventData = JSON.parse(line.slice(6));

              // Store raw event in debug data
              setDebugData((prev) => [
                ...prev,
                {
                  timestamp: new Date().toISOString(),
                  event: eventData,
                },
              ]);

              // Handle different event types
              if (eventData.type === "code_execution") {
                // Store code execution separately
                setCodeExecutions((prev) => [
                  ...prev,
                  {
                    timestamp: new Date().toISOString(),
                    code: eventData.code,
                  },
                ]);
                // Also add to streaming events for real-time display
                setStreamingEvents((prev) => [
                  ...prev,
                  {
                    ...eventData,
                    id: `code-${Date.now()}`,
                    status: "executing",
                  },
                ]);
                setStreamingStatus("writing_code");
              } else if (eventData.type === "thinking") {
                setStreamingStatus("thinking");
              } else if (eventData.type === "tool_call") {
                setStreamingEvents((prev) => [
                  ...prev,
                  { ...eventData, id: `${eventData.tool_name}-${Date.now()}` },
                ]);
                setStreamingStatus("calling_tools");
              } else if (eventData.type === "tool_result") {
                // Update existing tool call status
                setStreamingEvents((prev) =>
                  prev.map((evt) =>
                    evt.tool_name === eventData.tool_name &&
                    evt.status === "running"
                      ? { ...evt, status: eventData.status }
                      : evt
                  )
                );
              } else if (eventData.type === "response") {
                // Final response - add to messages
                const assistantMessage = {
                  role: "assistant",
                  content: eventData.content,
                };
                setMessages((prev) => [...prev, assistantMessage]);

                // Update conversation's updated_at
                setConversations((prev) => {
                  const updated = prev.map((c) =>
                    c.id === conversationId
                      ? {
                          ...c,
                          updated_at: new Date().toISOString(),
                          message_count: c.message_count + 2,
                        }
                      : c
                  );
                  return updated.sort(
                    (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
                  );
                });
              } else if (eventData.type === "error") {
                throw new Error(eventData.error || "Unknown error");
              }
            } catch (parseError) {
              console.error("Failed to parse SSE event:", parseError);
            }
          }
        }
      }

      // Close reader
      reader.releaseLock();
    } catch (err) {
      console.error("Failed to send message:", err);

      // Provide more specific error message
      let errorMessage =
        "❌ Failed to send message. Please check that the backend server is running and try again.";
      if (err.message.includes("Streaming API error")) {
        errorMessage =
          "❌ Claude AI is temporarily unavailable. Please try again in a moment.";
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: errorMessage,
        },
      ]);
    } finally {
      setIsStreaming(false);
      setStreamingEvents([]);
      setStreamingStatus(null);
    }
  };

  return (
    <div className="dark min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/structured_logo_white.png"
              alt="Structured AI"
              className="h-10 w-auto"
            />
            <div>
              <h1 className="text-lg font-bold text-foreground">
                STRUCTURED AI
              </h1>
              <p className="text-xs text-muted-foreground">Mission Control</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-muted-foreground">
                All Systems Operational
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard
            icon={<Users className="w-5 h-5" />}
            label="Team Members"
            value={stats?.teamCount ?? "—"}
            color="violet"
          />
          <StatCard
            icon={<Activity className="w-5 h-5" />}
            label="Active Projects"
            value={stats?.activeProjects ?? "—"}
            color="blue"
          />
          <StatCard
            icon={<AlertTriangle className="w-5 h-5" />}
            label="Open Incidents"
            value={stats?.openIncidents ?? "—"}
            color="amber"
            alert={stats?.openIncidents > 5}
          />
          <StatCard
            icon={<Zap className="w-5 h-5" />}
            label="P0 Critical"
            value={stats?.p0Incidents ?? "—"}
            color="red"
            alert={stats?.p0Incidents > 0}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <Card className="h-[600px] flex flex-col bg-card/50 backdrop-blur-sm border-border/40">
              <CardHeader className="pb-3 border-b border-border/40">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-violet-500" />
                    <CardTitle className="text-lg">Operations AI</CardTitle>
                  </div>
                  <Badge variant="secondary" className="gap-1">
                    <Sparkles className="w-3 h-3" />
                    Programmatic Tool Calling
                  </Badge>
                </div>
                <CardDescription>
                  Ask questions about team performance, incidents, and
                  operations
                </CardDescription>
              </CardHeader>

              <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
                {/* Messages */}
                <ScrollArea className="flex-1 p-4" ref={messagesScrollRef}>
                  <div className="space-y-4">
                    {messages.length === 0 && (
                      <div className="text-center py-12 text-muted-foreground">
                        <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-20" />
                        <p className="text-sm">
                          Start a conversation with your Operations AI
                        </p>
                        <p className="text-xs mt-2 max-w-md mx-auto">
                          Try: "Which projects have declining customer
                          satisfaction and open P1+ incidents?"
                        </p>
                      </div>
                    )}

                    {messages.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex gap-3 ${
                          msg.role === "user" ? "justify-end" : ""
                        }`}
                      >
                        {msg.role === "assistant" && (
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                            <Bot className="w-4 h-4 text-white" />
                          </div>
                        )}
                        <div
                          className={`rounded-lg px-4 py-3 max-w-[80%] ${
                            msg.role === "user"
                              ? "bg-violet-600 text-white"
                              : "bg-secondary"
                          }`}
                        >
                          {msg.role === "user" ? (
                            <p className="text-sm whitespace-pre-wrap">
                              {msg.content}
                            </p>
                          ) : (
                            <div className="text-sm prose prose-invert prose-sm max-w-none">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  // Headers
                                  h1: (props) => (
                                    <h1
                                      className="text-lg font-bold mt-4 mb-2 text-foreground"
                                      {...props}
                                    />
                                  ),
                                  h2: (props) => (
                                    <h2
                                      className="text-base font-bold mt-3 mb-2 text-foreground"
                                      {...props}
                                    />
                                  ),
                                  h3: (props) => (
                                    <h3
                                      className="text-sm font-bold mt-2 mb-1 text-foreground"
                                      {...props}
                                    />
                                  ),
                                  // Paragraphs
                                  p: (props) => (
                                    <p
                                      className="mb-2 text-foreground leading-relaxed"
                                      {...props}
                                    />
                                  ),
                                  // Lists
                                  ul: (props) => (
                                    <ul
                                      className="list-disc pl-4 mb-2 space-y-1"
                                      {...props}
                                    />
                                  ),
                                  ol: (props) => (
                                    <ol
                                      className="list-decimal pl-4 mb-2 space-y-1"
                                      {...props}
                                    />
                                  ),
                                  li: (props) => (
                                    <li
                                      className="text-foreground"
                                      {...props}
                                    />
                                  ),
                                  // Strong/Bold
                                  strong: (props) => (
                                    <strong
                                      className="font-bold text-violet-400"
                                      {...props}
                                    />
                                  ),
                                  // Em/Italic
                                  em: (props) => (
                                    <em
                                      className="italic text-foreground"
                                      {...props}
                                    />
                                  ),
                                  // Code
                                  code: ({ inline, ...props }) =>
                                    inline ? (
                                      <code
                                        className="bg-black/30 px-1.5 py-0.5 rounded text-amber-400 font-mono text-xs"
                                        {...props}
                                      />
                                    ) : (
                                      <code
                                        className="block bg-black/30 p-3 rounded font-mono text-xs text-emerald-400 overflow-x-auto"
                                        {...props}
                                      />
                                    ),
                                  // Blockquote
                                  blockquote: (props) => (
                                    <blockquote
                                      className="border-l-4 border-violet-500 pl-3 py-1 my-2 italic text-muted-foreground"
                                      {...props}
                                    />
                                  ),
                                  // Links
                                  a: (props) => (
                                    <a
                                      className="text-violet-400 hover:text-violet-300 underline"
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      {...props}
                                    />
                                  ),
                                  // Horizontal Rule
                                  hr: (props) => (
                                    <hr
                                      className="my-4 border-border/40"
                                      {...props}
                                    />
                                  ),
                                  // Tables
                                  table: (props) => (
                                    <div className="overflow-x-auto my-2">
                                      <table
                                        className="min-w-full border border-border/40 text-xs"
                                        {...props}
                                      />
                                    </div>
                                  ),
                                  thead: (props) => (
                                    <thead
                                      className="bg-secondary/50"
                                      {...props}
                                    />
                                  ),
                                  th: (props) => (
                                    <th
                                      className="border border-border/40 px-2 py-1 text-left font-bold"
                                      {...props}
                                    />
                                  ),
                                  td: (props) => (
                                    <td
                                      className="border border-border/40 px-2 py-1"
                                      {...props}
                                    />
                                  ),
                                }}
                              >
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                          )}
                        </div>
                        {msg.role === "user" && (
                          <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                            <User className="w-4 h-4" />
                          </div>
                        )}
                      </div>
                    ))}

                    {isStreaming && (
                      <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="bg-secondary rounded-lg px-4 py-3 border-l-4 border-violet-500 transition-all duration-300">
                          {/* Streaming status */}
                          {streamingStatus === "thinking" && (
                            <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
                              <span>🤔</span>
                              <span>Analyzing your question...</span>
                            </div>
                          )}

                          {/* Code execution section - show if there are any code events */}
                          {streamingEvents.filter(
                            (e) => e.type === "code_execution"
                          ).length > 0 && (
                            <div className="space-y-3 mb-4">
                              <div className="flex items-center gap-2 text-xs text-violet-400 animate-pulse">
                                <Code2 className="w-3 h-3" />
                                <span className="font-semibold">
                                  Claude wrote Python code
                                </span>
                              </div>
                              {streamingEvents
                                .filter((e) => e.type === "code_execution")
                                .map((event, idx) => (
                                  <div
                                    key={event.id || idx}
                                    className="bg-black/30 rounded p-3 border border-violet-500/30 animate-in fade-in duration-300"
                                  >
                                    <div className="flex items-center gap-2 mb-2">
                                      <Badge
                                        variant="outline"
                                        className="text-xs text-violet-400 border-violet-500/30"
                                      >
                                        Execution #{idx + 1}
                                      </Badge>
                                    </div>
                                    <pre className="text-xs font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap max-h-[200px] overflow-y-auto">
                                      {event.code}
                                    </pre>
                                  </div>
                                ))}
                            </div>
                          )}

                          {/* Tool calls section - show if there are any tool events */}
                          {streamingEvents.filter(
                            (e) => e.type !== "code_execution"
                          ).length > 0 && (
                            <div className="space-y-2">
                              <div className="flex items-center gap-2 text-xs text-amber-500">
                                <Terminal className="w-3 h-3" />
                                <span className="font-semibold">
                                  {streamingEvents.filter(
                                    (e) => e.type === "code_execution"
                                  ).length > 0
                                    ? "Code is calling tools"
                                    : "Calling tools directly"}
                                </span>
                              </div>
                              {streamingEvents
                                .filter((e) => e.type !== "code_execution")
                                .map((event, idx) => {
                                  // Format parameters for display
                                  const paramsStr = event.parameters
                                    ? Object.keys(event.parameters).length > 0
                                      ? JSON.stringify(event.parameters)
                                      : ""
                                    : "";

                                  return (
                                    <div
                                      key={event.id || idx}
                                      className="animate-in fade-in duration-300"
                                    >
                                      <div className="flex items-center gap-2 text-sm">
                                        {event.status === "running" && (
                                          <>
                                            <Loader2 className="w-3 h-3 animate-spin text-amber-500 flex-shrink-0" />
                                            <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                                              <div className="flex items-center gap-1">
                                                <span className="font-mono text-xs text-amber-500">
                                                  {event.tool_name}()
                                                </span>
                                                <span className="text-xs text-muted-foreground">
                                                  running...
                                                </span>
                                              </div>
                                              {paramsStr && (
                                                <span className="font-mono text-xs text-muted-foreground truncate">
                                                  {paramsStr}
                                                </span>
                                              )}
                                            </div>
                                          </>
                                        )}
                                        {event.status === "completed" && (
                                          <>
                                            <CheckCircle2 className="w-3 h-3 text-emerald-500 animate-in zoom-in duration-200 flex-shrink-0" />
                                            <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                                              <div className="flex items-center gap-1">
                                                <span className="font-mono text-xs text-emerald-500">
                                                  {event.tool_name}()
                                                </span>
                                                <span className="text-xs text-muted-foreground">
                                                  completed
                                                </span>
                                              </div>
                                              {paramsStr && (
                                                <span className="font-mono text-xs text-muted-foreground truncate">
                                                  {paramsStr}
                                                </span>
                                              )}
                                            </div>
                                          </>
                                        )}
                                        {event.status === "error" && (
                                          <>
                                            <AlertTriangle className="w-3 h-3 text-red-500 flex-shrink-0" />
                                            <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                                              <div className="flex items-center gap-1">
                                                <span className="font-mono text-xs text-red-500">
                                                  {event.tool_name}()
                                                </span>
                                                <span className="text-xs text-muted-foreground">
                                                  error
                                                </span>
                                              </div>
                                              {paramsStr && (
                                                <span className="font-mono text-xs text-muted-foreground truncate">
                                                  {paramsStr}
                                                </span>
                                              )}
                                            </div>
                                          </>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </ScrollArea>

                {/* Code Execution Display */}
                {codeExecution && (
                  <div className="border-t border-border/40 p-4 bg-black/20">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                      <Code2 className="w-3 h-3" />
                      <span>Code Execution</span>
                    </div>
                    <pre className="text-xs font-mono text-emerald-400 bg-black/40 rounded p-3 overflow-x-auto">
                      {codeExecution}
                    </pre>
                  </div>
                )}

                {/* Input */}
                <form
                  onSubmit={handleSubmit}
                  className="p-4 border-t border-border/40"
                >
                  <div className="flex gap-2">
                    <Input
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Ask about operations, incidents, or team performance..."
                      className="bg-secondary/50 border-border/40"
                      disabled={isStreaming}
                    />
                    <Button
                      type="submit"
                      disabled={isStreaming}
                      className="gap-2"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* Debug Panel */}
            <Card className="bg-card/50 backdrop-blur-sm border border-amber-500/30">
              <CardHeader
                className="pb-3 cursor-pointer hover:bg-secondary/20 transition-colors"
                onClick={() => setIsDebugOpen(!isDebugOpen)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bug className="w-5 h-5 text-amber-500" />
                    <CardTitle className="text-lg">Debug Panel</CardTitle>
                    <Badge variant="secondary" className="text-xs">
                      {debugData.length} events
                    </Badge>
                  </div>
                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                    {isDebugOpen ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                <CardDescription>
                  Raw backend response data for debugging
                </CardDescription>
              </CardHeader>
              {isDebugOpen && (
                <CardContent>
                  <div className="space-y-4 max-h-[600px] overflow-y-auto">
                    {/* Code Executions Section */}
                    {codeExecutions.length > 0 && (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm font-semibold text-violet-400 mb-2">
                          <Code2 className="w-4 h-4" />
                          <span>Python Code Executed by Claude</span>
                          <Badge variant="secondary" className="text-xs">
                            {codeExecutions.length}
                          </Badge>
                        </div>
                        {codeExecutions.map((item, idx) => (
                          <div
                            key={idx}
                            className="bg-black/40 rounded-lg p-4 border border-violet-500/30"
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <Badge
                                variant="outline"
                                className="text-xs text-violet-400 border-violet-500/30"
                              >
                                Execution #{idx + 1}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                {new Date(item.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <pre className="text-xs font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap bg-black/30 rounded p-3">
                              {item.code}
                            </pre>
                          </div>
                        ))}
                        <div className="border-t border-border/40 my-4" />
                      </div>
                    )}

                    {/* All Events Section */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm font-semibold text-amber-400 mb-2">
                        <Terminal className="w-4 h-4" />
                        <span>All Backend Events</span>
                        <Badge variant="secondary" className="text-xs">
                          {debugData.length}
                        </Badge>
                      </div>
                      {debugData.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          <Terminal className="w-8 h-8 mx-auto mb-2 opacity-30" />
                          <p className="text-sm">No debug data yet</p>
                          <p className="text-xs mt-1">
                            Send a message to see backend events
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          {debugData.map((item, idx) => (
                            <div
                              key={idx}
                              className="bg-black/30 rounded-lg p-3 border border-amber-500/20"
                            >
                              <div className="flex items-center gap-2 mb-2">
                                <Badge
                                  variant="outline"
                                  className="text-xs text-amber-400 border-amber-500/30"
                                >
                                  {item.event.type}
                                </Badge>
                                <span className="text-xs text-muted-foreground">
                                  {new Date(
                                    item.timestamp
                                  ).toLocaleTimeString()}
                                </span>
                              </div>
                              <pre className="text-xs font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap">
                                {JSON.stringify(item.event, null, 2)}
                              </pre>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Conversations Panel */}
            <Card className="bg-card/50 backdrop-blur-sm border-border/40">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-violet-500" />
                    <CardTitle className="text-lg">Conversations</CardTitle>
                    <Badge variant="secondary">{conversations.length}</Badge>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={startNewChat}
                    className="h-8 gap-1.5"
                  >
                    <Plus className="w-4 h-4" />
                    New
                  </Button>
                </div>
                <CardDescription>Recent conversation history</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-[200px] overflow-y-auto">
                  {isLoadingConversations ? (
                    // Loading skeletons
                    <>
                      {[1, 2, 3].map((i) => (
                        <div
                          key={i}
                          className="h-16 bg-secondary/30 rounded-lg animate-pulse"
                        />
                      ))}
                    </>
                  ) : conversations.length === 0 ? (
                    // Empty state
                    <div className="text-center py-8 text-muted-foreground">
                      <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-30" />
                      <p className="text-sm">No conversations yet</p>
                      <p className="text-xs mt-1">Start chatting below!</p>
                    </div>
                  ) : (
                    // Conversation list
                    conversations.map((conversation) => (
                      <ConversationItem
                        key={conversation.id}
                        conversation={conversation}
                        isActive={conversation.id === currentConversationId}
                        onClick={() => loadConversation(conversation.id)}
                        onDelete={() => deleteConversation(conversation.id)}
                      />
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Tool Calls Panel */}
            <Card className="bg-card/50 backdrop-blur-sm border-border/40">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-emerald-500" />
                  <CardTitle className="text-lg">Tool Execution</CardTitle>
                </div>
                <CardDescription>
                  Watch PTC orchestrate tools in real-time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <ToolCallItem
                    name="get_team_members"
                    status="available"
                    description="Fetch employee records"
                  />
                  <ToolCallItem
                    name="get_projects"
                    status="available"
                    description="Fetch project data"
                  />
                  <ToolCallItem
                    name="get_incidents"
                    status="available"
                    description="Fetch incident reports"
                  />
                  <div className="pt-3 border-t border-border/40">
                    <p className="text-xs text-muted-foreground">
                      <span className="text-amber-500">Challenge:</span>{" "}
                      Implement additional tools for budget, feedback, and
                      actions
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-card/50 backdrop-blur-sm border-border/40">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Example Queries</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {[
                  "List all open P0 incidents",
                  "Which teams have the most incidents?",
                  "Find projects with overdue deadlines",
                  "Who is on-call for infrastructure?",
                ].map((query, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(query)}
                    className="w-full text-left text-sm px-3 py-2 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors flex items-center justify-between group"
                  >
                    <span className="text-muted-foreground group-hover:text-foreground transition-colors">
                      {query}
                    </span>
                    <ChevronRight className="w-4 h-4 text-muted-foreground/50 group-hover:text-foreground/50" />
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ icon, label, value, color, alert }) {
  const colors = {
    violet: "from-violet-500/20 to-violet-500/5 text-violet-500",
    blue: "from-blue-500/20 to-blue-500/5 text-blue-500",
    amber: "from-amber-500/20 to-amber-500/5 text-amber-500",
    red: "from-red-500/20 to-red-500/5 text-red-500",
  };

  return (
    <Card
      className={`bg-gradient-to-br ${colors[color]} border-border/40 ${
        alert ? "ring-1 ring-red-500/50" : ""
      }`}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className={colors[color].split(" ").pop()}>{icon}</div>
          {alert && (
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          )}
        </div>
        <div className="mt-3">
          <p className="text-2xl font-bold text-foreground">{value}</p>
          <p className="text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function ToolCallItem({ name, status, description }) {
  const statusColors = {
    available: "bg-emerald-500",
    running: "bg-amber-500 animate-pulse",
    completed: "bg-blue-500",
  };

  return (
    <div className="flex items-center gap-3 p-2 rounded-lg bg-secondary/30">
      <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-mono text-foreground truncate">{name}</p>
        <p className="text-xs text-muted-foreground truncate">{description}</p>
      </div>
    </div>
  );
}

function ConversationItem({ conversation, isActive, onClick, onDelete }) {
  const formatTimeAgo = (dateString) => {
    // Backend sends UTC timestamps without 'Z', so append it to parse correctly
    const utcString = dateString.endsWith("Z") ? dateString : dateString + "Z";
    const date = new Date(utcString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return "just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      onClick={onClick}
      className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
        isActive
          ? "bg-violet-500/10 border border-violet-500/30"
          : "bg-secondary/30 hover:bg-secondary/50"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p
            className={`text-sm font-medium truncate ${
              isActive ? "text-violet-400" : "text-foreground"
            }`}
          >
            {conversation.title || "New Conversation"}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-xs text-muted-foreground">
              {formatTimeAgo(conversation.updated_at)}
            </p>
            {conversation.message_count > 0 && (
              <>
                <span className="text-muted-foreground">·</span>
                <p className="text-xs text-muted-foreground">
                  {conversation.message_count} messages
                </p>
              </>
            )}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/20 transition-opacity"
          title="Delete conversation"
        >
          <Trash2 className="w-3 h-3 text-red-500" />
        </button>
      </div>
    </div>
  );
}

export default App;
