'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import ApiService from '../api/service';

// Define message types
type Message = {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
};

// Define product type from API service
type Product = {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url?: string;
  category: string;
  brand?: string;
  rating?: number;
  in_stock: boolean;
};

export default function ChatPage() {
  // State for messages, input, and session
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [suggestedProducts, setSuggestedProducts] = useState<Product[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session ID on component mount
  useEffect(() => {
    // Generate a random session ID
    const newSessionId = `session_${Math.random().toString(36).substring(2, 15)}`;
    setSessionId(newSessionId);
    
    // Add welcome message
    setMessages([
      {
        id: 'welcome',
        content: 'Hello! I\'m your AI shopping assistant. How can I help you today?',
        sender: 'assistant',
        timestamp: new Date(),
      },
    ]);
  }, []);

  // Scroll to bottom of messages when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;
    
    // Add user message to chat
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      content: input,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // In MVP, we'll use the REST API endpoint
      // In production, we might use WebSockets for real-time communication
      const response = await ApiService.sendChatMessage({
        session_id: sessionId,
        message: userMessage.content,
      });
      
      // Add assistant response to chat
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        content: response.response,
        sender: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Check if there are suggested products
      if (response.suggested_products && response.suggested_products.length > 0) {
        setSuggestedProducts(response.suggested_products);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gray-800">
            AI Shopping Assistant
          </Link>
        </div>
      </header>
      
      {/* Chat container */}
      <div className="flex-1 overflow-hidden flex flex-col max-w-7xl w-full mx-auto p-4">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 rounded-lg px-4 py-2">
                <p className="animate-pulse">Thinking...</p>
              </div>
            </div>
          )}
          
          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Suggested products */}
        {suggestedProducts.length > 0 && (
          <div className="mb-4">
            <h3 className="text-lg font-medium mb-2">Suggested Products</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {suggestedProducts.map((product) => (
                <div
                  key={product.id}
                  className="border rounded-lg p-4 bg-white shadow-sm"
                >
                  {product.image_url && (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-40 object-cover rounded-md mb-2"
                    />
                  )}
                  <h4 className="font-medium">{product.name}</h4>
                  <p className="text-sm text-gray-600 mb-2">{product.description}</p>
                  <p className="font-bold">${product.price.toFixed(2)}</p>
                  <button
                    className="mt-2 w-full bg-blue-500 text-white py-1 px-2 rounded hover:bg-blue-600 transition"
                    onClick={() => {
                      // In a real app, this would add to cart
                      alert(`Added ${product.name} to cart`);
                    }}
                  >
                    Add to Cart
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Input area */}
        <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about products or shopping..."
            className="flex-1 border border-gray-300 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white rounded-lg py-2 px-4 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
} 