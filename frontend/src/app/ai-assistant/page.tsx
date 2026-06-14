"use client";

import { useState, useRef, useEffect } from "react";
import { askAI, AIAskResponse } from "@/lib/api";
import { FiSend, FiUser, FiCpu } from "react-icons/fi";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  used_tools?: string[];
}

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "ai",
      content: "Xin chào! Tôi là Trợ lý Tài chính AI (với khả năng Function Calling). Bạn muốn hỏi gì về ngân sách, chi tiêu hay thanh toán hôm nay?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

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
    <div className="flex flex-col h-[calc(100vh-2rem)] max-w-5xl mx-auto rounded-2xl overflow-hidden bg-gray-900 border border-gray-800 shadow-2xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900/40 to-purple-900/40 border-b border-gray-800 p-6 flex items-center space-x-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
          <FiCpu className="text-white text-2xl" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
            AI Financial Analyst
          </h1>
          <p className="text-sm text-gray-400">Hệ thống AI Agent tự động gọi SQL Tools và trả về báo cáo chuẩn Markdown</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-gray-900 via-gray-900 to-black">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`flex max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 ${
                msg.role === "user" ? "bg-blue-600 ml-3" : "bg-gradient-to-tr from-purple-600 to-blue-500 mr-3"
              }`}>
                {msg.role === "user" ? <FiUser className="text-white text-sm" /> : <FiCpu className="text-white text-sm" />}
              </div>
              
              <div className="flex flex-col">
                <div className={`p-4 rounded-2xl shadow-md ${
                  msg.role === "user" 
                    ? "bg-blue-600 text-white rounded-tr-none" 
                    : "bg-gray-800 border border-gray-700 text-gray-100 rounded-tl-none prose prose-invert max-w-none"
                }`}>
                  {msg.role === "user" ? (
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        table: ({node: _n, ...props}) => <div className="overflow-x-auto my-4"><table className="min-w-full text-sm text-left border-collapse" {...props} /></div>,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        thead: ({node: _n, ...props}) => <thead className="bg-slate-800 text-slate-200" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        th: ({node: _n, ...props}) => <th className="px-4 py-2 font-semibold border-b border-slate-700" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        td: ({node: _n, ...props}) => <td className="px-4 py-2 border-b border-slate-800/50" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        p: ({node: _n, ...props}) => <p className="mb-2" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        h1: ({node: _n, ...props}) => <h1 className="text-xl font-bold mt-4 mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        h2: ({node: _n, ...props}) => <h2 className="text-lg font-bold mt-4 mb-2 text-indigo-300" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        h3: ({node: _n, ...props}) => <h3 className="text-base font-semibold mt-3 mb-1 text-slate-300" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        ul: ({node: _n, ...props}) => <ul className="list-disc pl-5 mb-2 space-y-1" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        ol: ({node: _n, ...props}) => <ol className="list-decimal pl-5 mb-2 space-y-1" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        li: ({node: _n, ...props}) => <li className="pl-1" {...props} />,
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        strong: ({node: _n, ...props}) => <strong className="font-semibold text-slate-200" {...props} />,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
                {msg.role === "ai" && msg.used_tools && msg.used_tools.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2 ml-2">
                    <span className="text-xs text-gray-500 flex items-center">Công cụ đã dùng:</span>
                    {msg.used_tools.map((tool, idx) => (
                      <span key={idx} className="px-2 py-1 text-[10px] font-mono bg-purple-900/30 text-purple-300 border border-purple-700/50 rounded flex items-center">
                        <FiCpu className="mr-1" /> {tool}
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
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-tr from-purple-600 to-blue-500 mr-3 flex items-center justify-center mt-1">
                <FiCpu className="text-white text-sm" />
              </div>
              <div className="p-4 rounded-2xl rounded-tl-none bg-gray-800 border border-gray-700 text-gray-100 shadow-md">
                <div className="flex items-center space-x-2 text-blue-400">
                  <AiOutlineLoading3Quarters className="animate-spin" />
                  <span className="text-sm">Đang suy nghĩ và truy xuất dữ liệu (Function Calling)...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-900 border-t border-gray-800">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ví dụ: Lấy cho tôi báo cáo tổng quan ngân sách năm nay?"
            className="w-full bg-gray-800 border border-gray-700 text-white rounded-full py-4 pl-6 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow shadow-inner placeholder-gray-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-2 p-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-full transition-colors flex items-center justify-center"
          >
            <FiSend />
          </button>
        </form>
        <p className="text-center text-xs text-gray-600 mt-3">
          AI Agent sẽ tự động chọn công cụ (Tools) truy vấn SQL phù hợp để trả lời.
        </p>
      </div>
    </div>
  );
}
