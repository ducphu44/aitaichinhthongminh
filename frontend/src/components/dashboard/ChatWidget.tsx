"use client";

import { useState, useRef, useEffect } from "react";
import { askAI, AIAskResponse } from "@/lib/api";
import { FiSend, FiUser, FiCpu, FiDatabase, FiMessageSquare, FiX, FiMinus } from "react-icons/fi";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  used_tools?: string[];
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "ai",
      content: "Xin chào! Tôi là Trợ lý Cơ sở dữ liệu AI. Bạn muốn truy vấn thông tin gì từ hệ thống hôm nay?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isLoading, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");

    // Add user message
    const newMsg: Message = { id: Date.now().toString(), role: "user", content: userMessage };
    setMessages((prev) => [...prev, newMsg]);
    setIsLoading(true);

    try {
      const response: AIAskResponse = await askAI(userMessage);
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: response.answer_markdown,
        used_tools: response.used_tools,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error(error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: "Xin lỗi, đã xảy ra lỗi kết nối. Vui lòng thử lại sau.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-[0_8px_30px_rgb(59,130,246,0.4)] hover:shadow-[0_8px_30px_rgb(59,130,246,0.6)] hover:scale-105 transition-all duration-300 border border-blue-400/20"
          title="Database AI assistant"
        >
          <FiMessageSquare className="w-6 h-6 animate-pulse" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="flex flex-col w-96 h-[550px] bg-slate-900 border border-slate-700/60 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden transition-all duration-300">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-3 flex items-center justify-between shadow-md">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <FiDatabase className="text-white text-sm" />
              </div>
              <div>
                <h3 className="font-semibold text-sm tracking-wide">Database AI assistant</h3>
                <div className="flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span className="text-[10px] text-blue-100">Trực tuyến</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-white/90 hover:text-white"
                title="Thu nhỏ"
              >
                <FiMinus className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-white/90 hover:text-white"
                title="Đóng"
              >
                <FiX className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-950/40 scroll-smooth">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`flex max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    msg.role === "user" ? "bg-blue-600 ml-2.5" : "bg-slate-800 border border-slate-700 mr-2.5"
                  }`}>
                    {msg.role === "user" ? (
                      <FiUser className="text-white text-xs" />
                    ) : (
                      <FiDatabase className="text-blue-400 text-xs" />
                    )}
                  </div>

                  {/* Message Content */}
                  <div className="flex flex-col">
                    <span className={`text-[10px] text-slate-500 mb-1 ${msg.role === "user" ? "text-right" : "text-left"}`}>
                      {msg.role === "user" ? "User" : "Internal AI assistant"}
                    </span>
                    <div className={`px-3 py-2 rounded-2xl text-xs shadow-md border ${
                      msg.role === "user"
                        ? "bg-blue-600 border-blue-500 text-white rounded-tr-none"
                        : "bg-slate-800 border-slate-700 text-slate-100 rounded-tl-none prose prose-invert max-w-none"
                    }`}>
                      {msg.role === "user" ? (
                        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                      ) : (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            table: ({ node: _n, ...props }) => (
                              <div className="overflow-x-auto my-2 border border-slate-700 rounded-lg">
                                <table className="min-w-full text-[11px] text-left border-collapse" {...props} />
                              </div>
                            ),
                            thead: ({ node: _n, ...props }) => <thead className="bg-slate-700 text-slate-200" {...props} />,
                            th: ({ node: _n, ...props }) => <th className="px-3 py-1.5 font-semibold border-b border-slate-600" {...props} />,
                            td: ({ node: _n, ...props }) => <td className="px-3 py-1.5 border-b border-slate-700/50" {...props} />,
                            p: ({ node: _n, ...props }) => <p className="mb-1.5 leading-relaxed" {...props} />,
                            h1: ({ node: _n, ...props }) => <h1 className="text-sm font-bold mt-2 mb-1 text-blue-400" {...props} />,
                            h2: ({ node: _n, ...props }) => <h2 className="text-xs font-bold mt-2 mb-1 text-indigo-300" {...props} />,
                            ul: ({ node: _n, ...props }) => <ul className="list-disc pl-4 mb-1.5 space-y-0.5" {...props} />,
                            ol: ({ node: _n, ...props }) => <ol className="list-decimal pl-4 mb-1.5 space-y-0.5" {...props} />,
                            li: ({ node: _n, ...props }) => <li className="pl-0.5" {...props} />,
                            strong: ({ node: _n, ...props }) => <strong className="font-semibold text-white" {...props} />,
                            code: ({ node: _n, ...props }) => <code className="bg-slate-900 px-1 py-0.5 rounded text-blue-300 font-mono text-[10px]" {...props} />,
                            pre: ({ node: _n, ...props }) => <pre className="bg-slate-900 p-2 rounded-lg border border-slate-850 my-2 overflow-x-auto font-mono text-[10px] text-slate-300" {...props} />,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>
                    {msg.role === "ai" && msg.used_tools && msg.used_tools.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1.5">
                        {msg.used_tools.map((tool, idx) => (
                          <span key={idx} className="px-1.5 py-0.5 text-[9px] font-mono bg-indigo-950/40 text-indigo-300 border border-indigo-800/30 rounded flex items-center">
                            <FiCpu className="mr-0.5 w-2.5 h-2.5" /> {tool}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="flex flex-row max-w-[85%]">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-800 border border-slate-700 mr-2.5 flex items-center justify-center mt-1">
                    <FiDatabase className="text-blue-400 text-xs" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-500 mb-1">Internal AI assistant</span>
                    <div className="px-3 py-2 rounded-2xl rounded-tl-none bg-slate-800 border border-slate-700 text-slate-100 shadow-md">
                      <div className="flex items-center space-x-2 text-blue-400 text-xs">
                        <AiOutlineLoading3Quarters className="animate-spin w-3 h-3" />
                        <span>Đang truy vấn cơ sở dữ liệu...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions */}
          {messages.length === 1 && (
            <div className="px-4 py-2 bg-slate-950/20 border-t border-slate-800 flex flex-wrap gap-1.5">
              {[
                "Tổng ngân sách năm nay là bao nhiêu?",
                "Có phòng ban nào chi tiêu vượt hạn mức không?",
                "Xem 5 khoản chi lớn nhất gần đây",
              ].map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(suggestion)}
                  className="text-[10px] text-slate-400 bg-slate-800/40 hover:bg-slate-850 hover:text-slate-200 border border-slate-700/50 rounded-full px-2.5 py-1 transition-all duration-200 text-left max-w-full truncate"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {/* Input Area */}
          <div className="p-3 bg-slate-900 border-t border-slate-800/60">
            <form onSubmit={handleSubmit} className="relative flex items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question here..."
                className="w-full bg-slate-950 border border-slate-800 text-xs text-white rounded-full py-2.5 pl-4 pr-12 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent transition-all placeholder-slate-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="absolute right-1.5 p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 text-white rounded-full transition-colors flex items-center justify-center"
              >
                <FiSend className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
