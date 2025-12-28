import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
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
} from 'lucide-react'

const apiUrl = import.meta.env.VITE_API_URL

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [codeExecution, setCodeExecution] = useState(null)
  const messagesEndRef = useRef(null)

  // Fetch initial stats
  useEffect(() => {
    fetchStats()
  }, [])

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchStats = async () => {
    try {
      const [teamRes, projectRes, incidentRes] = await Promise.all([
        fetch(`${apiUrl}/tools/team-members`),
        fetch(`${apiUrl}/tools/projects`),
        fetch(`${apiUrl}/tools/incidents`),
      ])
      const [team, projects, incidents] = await Promise.all([
        teamRes.json(),
        projectRes.json(),
        incidentRes.json(),
      ])

      const openIncidents = incidents.data.filter(i => i.status !== 'resolved')
      const p0Count = incidents.data.filter(i => i.severity === 'P0' && i.status !== 'resolved').length

      setStats({
        teamCount: team.count,
        projectCount: projects.count,
        openIncidents: openIncidents.length,
        p0Incidents: p0Count,
        activeProjects: projects.data.filter(p => p.status === 'active').length,
      })
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setCodeExecution(null)

    // Simulate AI response - candidates will implement actual API call
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "👋 I'm your Mission Control AI assistant! I can help you analyze team performance, investigate incidents, and answer operational questions.\n\n**Note to candidates:** This is where you'll implement the Programmatic Tool Calling integration with Claude. The AI should be able to:\n\n1. Write Python code that orchestrates multiple tool calls\n2. Process data without polluting the context\n3. Return only the final results\n\nTry asking me something like:\n- \"Which teams have the most open incidents?\"\n- \"List all P0 incidents and who's assigned to them\"\n- \"Which projects have engineers with unresolved P1+ incidents?\"",
      }])
      setIsLoading(false)
    }, 1000)
  }

  return (
    <div className="dark min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/structured_logo_white.png" alt="Structured AI" className="h-10 w-auto" />
            <div>
              <h1 className="text-lg font-bold text-foreground">STRUCTURED AI</h1>
              <p className="text-xs text-muted-foreground">Mission Control</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-muted-foreground">All Systems Operational</span>
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
            value={stats?.teamCount ?? '—'}
            color="violet"
          />
          <StatCard
            icon={<Activity className="w-5 h-5" />}
            label="Active Projects"
            value={stats?.activeProjects ?? '—'}
            color="blue"
          />
          <StatCard
            icon={<AlertTriangle className="w-5 h-5" />}
            label="Open Incidents"
            value={stats?.openIncidents ?? '—'}
            color="amber"
            alert={stats?.openIncidents > 5}
          />
          <StatCard
            icon={<Zap className="w-5 h-5" />}
            label="P0 Critical"
            value={stats?.p0Incidents ?? '—'}
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
                  Ask questions about team performance, incidents, and operations
                </CardDescription>
              </CardHeader>

              <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
                {/* Messages */}
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4">
                    {messages.length === 0 && (
                      <div className="text-center py-12 text-muted-foreground">
                        <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-20" />
                        <p className="text-sm">Start a conversation with your Operations AI</p>
                        <p className="text-xs mt-2 max-w-md mx-auto">
                          Try: "Which projects have declining customer satisfaction and open P1+ incidents?"
                        </p>
                      </div>
                    )}

                    {messages.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}
                      >
                        {msg.role === 'assistant' && (
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                            <Bot className="w-4 h-4 text-white" />
                          </div>
                        )}
                        <div
                          className={`rounded-lg px-4 py-3 max-w-[80%] ${
                            msg.role === 'user'
                              ? 'bg-violet-600 text-white'
                              : 'bg-secondary'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        </div>
                        {msg.role === 'user' && (
                          <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                            <User className="w-4 h-4" />
                          </div>
                        )}
                      </div>
                    ))}

                    {isLoading && (
                      <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="bg-secondary rounded-lg px-4 py-3">
                          <Loader2 className="w-4 h-4 animate-spin" />
                        </div>
                      </div>
                    )}

                    <div ref={messagesEndRef} />
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
                <form onSubmit={handleSubmit} className="p-4 border-t border-border/40">
                  <div className="flex gap-2">
                    <Input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Ask about operations, incidents, or team performance..."
                      className="bg-secondary/50 border-border/40"
                      disabled={isLoading}
                    />
                    <Button type="submit" disabled={isLoading} className="gap-2">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
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
                      <span className="text-amber-500">Challenge:</span> Implement additional tools for budget, feedback, and actions
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
  )
}

function StatCard({ icon, label, value, color, alert }) {
  const colors = {
    violet: 'from-violet-500/20 to-violet-500/5 text-violet-500',
    blue: 'from-blue-500/20 to-blue-500/5 text-blue-500',
    amber: 'from-amber-500/20 to-amber-500/5 text-amber-500',
    red: 'from-red-500/20 to-red-500/5 text-red-500',
  }

  return (
    <Card className={`bg-gradient-to-br ${colors[color]} border-border/40 ${alert ? 'ring-1 ring-red-500/50' : ''}`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className={colors[color].split(' ').pop()}>
            {icon}
          </div>
          {alert && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
        </div>
        <div className="mt-3">
          <p className="text-2xl font-bold text-foreground">{value}</p>
          <p className="text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  )
}

function ToolCallItem({ name, status, description }) {
  const statusColors = {
    available: 'bg-emerald-500',
    running: 'bg-amber-500 animate-pulse',
    completed: 'bg-blue-500',
  }

  return (
    <div className="flex items-center gap-3 p-2 rounded-lg bg-secondary/30">
      <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-mono text-foreground truncate">{name}</p>
        <p className="text-xs text-muted-foreground truncate">{description}</p>
      </div>
    </div>
  )
}

export default App
