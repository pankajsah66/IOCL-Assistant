'use client';
import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, FileText, Loader2, X, Sparkles } from 'lucide-react';
import Image from 'next/image';

interface Message {
  role: 'user' | 'assistant' | 'error';
  content: string;
  file?: string;
  preview?: string;
}

export default function ChatGPTStyle() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentBannerIndex, setCurrentBannerIndex] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Banner images - UPDATE THESE PATHS WITH YOUR IMAGE PATHS
  const bannerImages = [
    '/images/banner1.jpg',  // Replace with your image paths
    '/images/banner2.jpg',
    '/images/banner3.jpg',
    '/images/banner4.jpg',
  ];

  // IOCL Logo path - UPDATE THIS WITH YOUR LOGO PATH
  const ioclLogoPath = '/images/iocl-logo.png';  // Replace with your logo path

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-rotate banner images every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentBannerIndex((prev) => (prev + 1) % bannerImages.length);
    }, 5000); // Change image every 5 seconds

    return () => clearInterval(interval);
  }, [bannerImages.length]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAttachedFile(file);

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setPreviewUrl(null);
    }
  };

  const removeAttachment = () => {
    setAttachedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() && !attachedFile) return;

    const userMessage = input.trim();
    const file = attachedFile;
    const preview = previewUrl;
    const shouldUseContext = !file && !currentSessionId;

    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage || (file ? `[Attached: ${file.name}]` : ''),
      file: file?.name,
      preview: preview || undefined
    }]);

    setInput('');
    setAttachedFile(null);
    setPreviewUrl(null);
    setIsLoading(true);

    try {
      let response;

      if (file) {
        const formData = new FormData();
        
        if (file.type.startsWith('image/')) {
          formData.append('image', file);
        } else {
          formData.append('file', file);
        }
        
        if (userMessage) {
          formData.append('question', userMessage);
        }

        response = await fetch('http://localhost:5000/api/chat', {
          method: 'POST',
          body: formData,
        });
      } else {
        response = await fetch('http://localhost:5000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: userMessage,
            use_context: shouldUseContext,
            session_id: currentSessionId,
          }),
        });
      }

      const data = await response.json();

      if (data.success) {
        if (data.session_id) {
          setCurrentSessionId(data.session_id);
        }
        
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.answer
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'error',
          content: 'Error: ' + (data.error || 'Something went wrong')
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: 'Error: Could not connect to backend. Make sure it\'s running.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Header with Logo */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between relative">
        {/* IOCL Logo - Left Top */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2">
          <div className="w-12 h-12 rounded-full overflow-hidden bg-white flex items-center justify-center shadow-lg">
            <img 
              src={ioclLogoPath} 
              alt="IOCL Logo" 
              className="w-10 h-10 object-contain"
              onError={(e) => {
                // Fallback if image not found
                e.currentTarget.style.display = 'none';
                e.currentTarget.parentElement!.innerHTML = '<span class="text-orange-600 font-bold text-xs">IOCL</span>';
              }}
            />
          </div>
        </div>

        {/* Center Title */}
        <div className="flex items-center gap-3 mx-auto">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white font-semibold">IOCL Assistant</h1>
            <p className="text-xs text-gray-400">Powered by Mistral AI • Context Auto-Enabled</p>
          </div>
        </div>

        {/* Right spacer for balance */}
        <div className="w-12"></div>
      </div>

      {/* Banner Section */}
      <div className="relative w-full h-48 bg-gray-800 overflow-hidden">
        {/* Banner Images */}
        {bannerImages.map((img, idx) => (
          <div
            key={idx}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              idx === currentBannerIndex ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <img
              src={img}
              alt={`Banner ${idx + 1}`}
              className="w-full h-full object-cover"
              onError={(e) => {
                // Fallback gradient if image not found
                e.currentTarget.style.display = 'none';
                e.currentTarget.parentElement!.style.background = 
                  `linear-gradient(135deg, #667eea ${idx * 20}%, #764ba2 ${100 - idx * 20}%)`;
              }}
            />
          </div>
        ))}

        {/* Banner Indicators */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
          {bannerImages.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentBannerIndex(idx)}
              className={`w-2 h-2 rounded-full transition-all ${
                idx === currentBannerIndex 
                  ? 'bg-white w-8' 
                  : 'bg-white/50 hover:bg-white/75'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md px-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Ready when you are.</h2>
              <p className="text-gray-400 text-sm mb-4">
                Ask me anything, upload documents, or share images.
              </p>
              <div className="bg-gray-800 rounded-lg px-4 py-3 text-sm text-gray-300 border border-gray-700">
                <p className="font-semibold text-purple-400 mb-1">💡 Smart Memory</p>
                <p className="text-xs">Upload a file once, ask multiple questions about it until refresh!</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto py-8 px-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-6 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                    msg.role === 'user' 
                      ? 'bg-blue-600' 
                      : msg.role === 'error'
                      ? 'bg-red-600'
                      : 'bg-purple-600'
                  }`}>
                    <span className="text-white text-sm font-medium">
                      {msg.role === 'user' ? 'U' : msg.role === 'error' ? '!' : 'AI'}
                    </span>
                  </div>

                  <div className="flex flex-col gap-2">
                    {msg.preview && (
                      <img 
                        src={msg.preview} 
                        alt="Attached" 
                        className="rounded-lg max-w-xs"
                      />
                    )}
                    {msg.file && !msg.preview && (
                      <div className="bg-gray-800 rounded-lg px-3 py-2 flex items-center gap-2 text-sm text-gray-300">
                        <FileText className="w-4 h-4" />
                        {msg.file}
                      </div>
                    )}
                    {msg.content && (
                      <div className={`rounded-2xl px-4 py-3 ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : msg.role === 'error'
                          ? 'bg-red-900/50 text-red-200 border border-red-700'
                          : 'bg-gray-800 text-gray-100'
                      }`}>
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="mb-6 flex justify-start">
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                    <span className="text-white text-sm font-medium">AI</span>
                  </div>
                  <div className="bg-gray-800 rounded-2xl px-4 py-3">
                    <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-700 bg-gray-800 p-4">
        <div className="max-w-3xl mx-auto">
          {attachedFile && (
            <div className="mb-3 flex items-center gap-3 bg-gray-700 rounded-lg p-3">
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="w-16 h-16 object-cover rounded" />
              ) : (
                <div className="w-16 h-16 bg-gray-600 rounded flex items-center justify-center">
                  <FileText className="w-8 h-8 text-gray-400" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">{attachedFile.name}</p>
                <p className="text-xs text-gray-400">
                  {(attachedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button
                onClick={removeAttachment}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}

          <div className="bg-gray-700 rounded-2xl flex items-end gap-2 p-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".pdf,.txt,.png,.jpg,.jpeg,.gif,.webp"
              className="hidden"
            />
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-600"
              disabled={isLoading}
            >
              <Paperclip className="w-5 h-5" />
            </button>

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything..."
              rows={1}
              className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none resize-none py-2 px-2 max-h-32"
              disabled={isLoading}
              style={{ minHeight: '40px' }}
            />

            <button
              onClick={handleSendMessage}
              disabled={isLoading || (!input.trim() && !attachedFile)}
              className="p-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>

          <p className="text-xs text-gray-500 text-center mt-2">
            {attachedFile 
              ? '📎 File attached - answers from document' 
              : currentSessionId 
              ? '📄 Document in memory - asking about uploaded file'
              : '💡 Context enabled - answers from knowledge base'}
          </p>
        </div>
      </div>
    </div>
  );
}