'use client';

import { useEffect } from 'react';
import { useChatStore } from '@/lib/store';
import {
  Plus,
  MessageSquare,
  Trash2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import toast from 'react-hot-toast';

export function Sidebar() {
  const {
    sessions,
    currentSession,
    agents,
    selectedAgent,
    isSidebarOpen,
    loadSessions,
    loadAgents,
    createNewSession,
    loadSession,
    deleteSession,
    setSelectedAgent,
    toggleSidebar,
  } = useChatStore();

  useEffect(() => {
    loadSessions();
    loadAgents();
  }, [loadSessions, loadAgents]);

  const handleNewChat = async () => {
    try {
      await createNewSession();
      toast.success('New session created');
    } catch (error) {
      toast.error('Failed to create session');
    }
  };

  const handleLoadSession = async (sessionId: string) => {
    try {
      await loadSession(sessionId);
    } catch (error) {
      toast.error('Failed to load session');
    }
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('Delete this conversation?')) return;

    try {
      await deleteSession(sessionId);
      toast.success('Session deleted');
    } catch (error) {
      toast.error('Failed to delete session');
    }
  };

  if (!isSidebarOpen) {
    return (
      <button
        onClick={toggleSidebar}
        className="fixed left-0 top-1/2 -translate-y-1/2 z-50 btn-secondary p-2 rounded-l-none"
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    );
  }

  return (
    <div className="w-72 bg-macos-surface border-r border-macos-border flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-macos-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-body">Conversations</h2>
          <button
            onClick={toggleSidebar}
            className="p-1.5 hover:bg-macos-gray-200 rounded-macos transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>
        
        <button
          onClick={handleNewChat}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Agent Selection */}
      <div className="p-4 border-b border-macos-border">
        <div className="text-caption text-macos-text-secondary font-medium mb-3">
          Select Advisor
        </div>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => setSelectedAgent(null)}
            className={`p-2 rounded-macos text-caption font-medium transition-all ${
              selectedAgent === null
                ? 'bg-macos-blue text-white'
                : 'bg-macos-gray-100 hover:bg-macos-gray-200'
            }`}
          >
            <div className="text-lg mb-1">🤖</div>
            <div>Auto</div>
          </button>
          
          {agents.map((agent) => (
            <button
              key={agent.type}
              onClick={() => setSelectedAgent(agent.type)}
              className={`p-2 rounded-macos text-caption font-medium transition-all ${
                selectedAgent === agent.type
                  ? 'bg-macos-blue text-white'
                  : 'bg-macos-gray-100 hover:bg-macos-gray-200'
              }`}
              title={agent.description}
            >
              <div className="text-lg mb-1">{agent.icon}</div>
              <div className="line-clamp-2 leading-tight">{agent.name.split(' ')[0]}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="text-center py-8 text-caption text-macos-text-secondary">
            No conversations yet
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => handleLoadSession(session.id)}
                className={`w-full text-left p-3 rounded-macos group transition-all ${
                  currentSession?.id === session.id
                    ? 'bg-macos-blue/10 border border-macos-blue/20'
                    : 'hover:bg-macos-gray-100'
                }`}
              >
                <div className="flex items-start gap-2">
                  <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 text-macos-text-secondary" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-caption line-clamp-2 mb-1">
                      {session.session_name}
                    </div>
                    <div className="text-xs text-macos-text-tertiary">
                      {new Date(session.created_at).toLocaleDateString()}
                      {session.message_count && (
                        <span className="ml-2">• {session.message_count} msgs</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-600" />
                  </button>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-macos-border">
        <div className="text-xs text-macos-text-tertiary text-center">
          KANZ v1.0
        </div>
      </div>
    </div>
  );
}
