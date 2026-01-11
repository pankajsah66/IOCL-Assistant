'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, MessageCircle, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';

interface Message {
  type: 'user' | 'bot' | 'system' | 'error';
  content: string;
}

export default function ContextQA() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [contextLoaded, setContextLoaded] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkContextStatus();
  }, []);

  const checkContextStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/context-status');
      const data = await response.json();
      setContextLoaded(data.loaded);
      
      if (data.loaded) {
        setMessages([
          {
            type: 'system',
            content: '✓ Context loaded successfully! You can now ask questions.'
          }
        ]);
      } else {
        setMessages([
          {
            type: 'error',
            content: `⚠ Context file not found at: ${data.file_path}. Please check the backend configuration.`
          }
        ]);
      }
    } catch (error) {
      setMessages([
        {
          type: 'error',
          content: 'Error: Could not connect to backend. Make sure backend_api.py is running.'
        }
      ]);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !contextLoaded) return;

    const userMessage = input.trim();
    setInput('');
    
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/context-qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setMessages(prev => [...prev, { type: 'bot', content: data.answer }]);
      } else {
        setMessages(prev => [...prev, { 
          type: 'error', 
          content: 'Error: ' + data.error 
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: 'Error: Could not connect to backend.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Context-based Q&A
          </h1>
          <p className="text-gray-600">Ask questions based on predefined context</p>
          
          {/* Navigation */}
          <div className="mt-4">
            <Link 
              href="/"
              className="text-blue-600 hover:text-blue-700 underline"
            >
              ← Back to Document Upload
            </Link>
          </div>
        </div>

        {/* Context Status Card */}
        <div className={`mb-6 p-4 rounded-xl border-2 ${
          contextLoaded 
            ? 'bg-green-50 border-green-200' 
            : contextLoaded === false 
            ? 'bg-red-50 border-red-200' 
            : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="flex items-center gap-3">
            {contextLoaded ? (
              <>
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-green-800 font-medium">Context loaded and ready</span>
              </>
            ) : contextLoaded === false ? (
              <>
                <XCircle className="w-5 h-5 text-red-600" />
                <span className="text-red-800 font-medium">Context file not found</span>
              </>
            ) : (
              <>
                <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
                <span className="text-gray-800 font-medium">Checking context status...</span>
              </>
            )}
          </div>
        </div>

        {/* Chat Section */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header Bar */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4">
            <div className="flex items-center gap-3">
              <MessageCircle className="w-5 h-5" />
              <span className="font-medium">Ask Anything</span>
            </div>
          </div>

          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gray-50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-6 py-3 ${
                    msg.type === 'user'
                      ? 'bg-purple-600 text-white'
                      : msg.type === 'bot'
                      ? 'bg-white text-gray-800 shadow-md border border-gray-200'
                      : msg.type === 'system'
                      ? 'bg-green-100 text-green-800 border border-green-200'
                      : 'bg-red-100 text-red-800 border border-red-200'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {msg.type === 'bot' && (
                      <MessageCircle className="w-5 h-5 mt-1 flex-shrink-0" />
                    )}
                    {msg.type === 'error' && (
                      <AlertCircle className="w-5 h-5 mt-1 flex-shrink-0" />
                    )}
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl px-6 py-3 shadow-md border border-gray-200">
                  <div className="flex items-center gap-3">
                    <Loader2 className="w-5 h-5 animate-spin text-purple-600" />
                    <span className="text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4 bg-white">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={contextLoaded ? "Ask your question..." : "Context not loaded"}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                disabled={isLoading || !contextLoaded}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !input.trim() || !contextLoaded}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-xl flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>Powered by Mistral AI • Indian Oil Corporation Limited</p>
        </div>
      </div>
    </div>
  );
}