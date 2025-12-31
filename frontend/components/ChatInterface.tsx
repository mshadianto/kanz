'use client';

import { useEffect, useRef, useState } from 'react';
import { useChatStore } from '@/lib/store';
import { Send, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import toast from 'react-hot-toast';

export function ChatInterface() {
  const {
    messages,
    isLoading,
    selectedAgent,
    agents,
    sendMessage,
  } = useChatStore();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const query = input.trim();
    setInput('');

    try {
      await sendMessage(query);
    } catch (error) {
      toast.error('Failed to send message. Please try again.');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const getAgentInfo = (agentType?: string) => {
    if (!agentType) return null;
    return agents.find(a => a.type === agentType);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            {messages.map((message, idx) => (
              <div
                key={message.id || idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={
                    message.role === 'user'
                      ? 'message-user'
                      : 'message-assistant'
                  }
                >
                  {message.role === 'assistant' && message.agent_type && (
                    <div className="flex items-center gap-2 mb-2 text-caption text-macos-text-secondary">
                      <span>{getAgentInfo(message.agent_type)?.icon}</span>
                      <span className="font-medium">
                        {getAgentInfo(message.agent_type)?.name}
                      </span>
                    </div>
                  )}
                  
                  {message.role === 'user' ? (
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  ) : (
                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  )}

                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-macos-border">
                      <div className="text-caption text-macos-text-secondary font-medium mb-2">
                        📚 Sources ({message.sources.length})
                      </div>
                      <div className="space-y-1.5">
                        {message.sources.slice(0, 3).map((source: any, idx: number) => (
                          <div
                            key={idx}
                            className="text-caption text-macos-text-tertiary line-clamp-2"
                          >
                            {idx + 1}. {source.content.substring(0, 100)}...
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="message-assistant">
                  <div className="flex items-center gap-2 text-macos-text-secondary">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-body">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-macos-border bg-macos-surface p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about Saudi Arabia investment opportunities..."
              className="input-macos w-full resize-none min-h-[52px] max-h-32"
              rows={1}
              disabled={isLoading}
            />
            {selectedAgent && (
              <div className="absolute top-2 right-2">
                <span className="badge-agent bg-macos-blue/10 text-macos-blue">
                  {agents.find(a => a.type === selectedAgent)?.icon}
                  <span className="text-xs">
                    {agents.find(a => a.type === selectedAgent)?.name}
                  </span>
                </span>
              </div>
            )}
          </div>
          
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary h-[52px] px-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

function EmptyState() {
  const { selectedAgent, agents } = useChatStore();
  
  const suggestions = [
    {
      icon: '💰',
      title: 'Investment Analysis',
      query: 'What are the key financial incentives for a $200M data center in NEOM?',
    },
    {
      icon: '🎯',
      title: 'Strategic Assessment',
      query: 'Compare NEOM vs King Abdullah Economic City for tech infrastructure investment',
    },
    {
      icon: '⚠️',
      title: 'Risk Analysis',
      query: 'What are the main regulatory risks and how to mitigate them?',
    },
    {
      icon: '📊',
      title: 'ROI Projection',
      query: 'Calculate expected IRR and payback period for AI infrastructure investment',
    },
  ];

  return (
    <div className="flex items-center justify-center h-full">
      <div className="max-w-3xl w-full space-y-8 px-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="text-6xl mb-4">🇸🇦</div>
          <h1 className="text-display font-bold text-balance">
            Saudi Investment Advisor
          </h1>
          <p className="text-body-lg text-macos-text-secondary text-balance">
            AI-powered analysis of Saudi Arabia investment opportunities
          </p>
        </div>

        {/* Selected agent info */}
        {selectedAgent && (
          <div className="card-macos p-4">
            <div className="flex items-center gap-3">
              <div className="text-3xl">
                {agents.find(a => a.type === selectedAgent)?.icon}
              </div>
              <div>
                <div className="font-semibold text-body">
                  {agents.find(a => a.type === selectedAgent)?.name}
                </div>
                <div className="text-caption text-macos-text-secondary">
                  {agents.find(a => a.type === selectedAgent)?.description}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Suggested queries */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => useChatStore.getState().sendMessage(suggestion.query)}
              className="card-macos p-4 text-left hover:shadow-macos-lg transition-all duration-200 hover:-translate-y-0.5"
            >
              <div className="flex items-start gap-3">
                <div className="text-2xl">{suggestion.icon}</div>
                <div className="flex-1">
                  <div className="font-medium text-body mb-1">
                    {suggestion.title}
                  </div>
                  <div className="text-caption text-macos-text-secondary line-clamp-2">
                    {suggestion.query}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
