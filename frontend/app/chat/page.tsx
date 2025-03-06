'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

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

// Define cart type
type Cart = {
  session_id: string;
  items: Array<{
    product: Product;
    quantity: number;
    item_total: number;
  }>;
  subtotal: number;
  tax?: number;
  shipping?: number;
  total: number;
};

// Define action data type
type ActionData = {
  type: string;
  product?: Product;
  quantity?: number;
  session_id: string;
  cart?: Cart;
  email?: string;
  success_url?: string;
  cancel_url?: string;
};

export default function ChatPage() {
  // State for messages, input, and session
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [suggestedProducts, setSuggestedProducts] = useState<Product[]>([]);
  const [requiresAction, setRequiresAction] = useState(false);
  const [actionData, setActionData] = useState<ActionData | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    
    if ((!input.trim() && !selectedImage) || isLoading) return;
    
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
      let response;
      
      // If there's an image, use the multipart/form-data endpoint
      if (selectedImage) {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('message', input.trim() ? input : 'Here is an image I want to share.');
        formData.append('image', selectedImage);
        
        try {
          response = await fetch('http://localhost:8000/api/chat/with-image', {
            method: 'POST',
            body: formData,
          });
          
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `Error: ${response.status}`);
          }
        } catch (error) {
          console.error('Image upload error:', error);
          
          // Add error message to chat
          const errorMessage: Message = {
            id: `error_${Date.now()}`,
            content: `Sorry, I couldn't process your image. ${error instanceof Error ? error.message : 'Please try again.'}`,
            sender: 'assistant',
            timestamp: new Date(),
          };
          
          setMessages((prev) => [...prev, errorMessage]);
          setIsLoading(false);
          
          // Clear the image after error
          setSelectedImage(null);
          setImagePreview(null);
          
          return; // Exit early
        }
        
        // Clear the image after successful sending
        setSelectedImage(null);
        setImagePreview(null);
      } else {
        // Otherwise use the regular JSON endpoint
        response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            message: userMessage.content,
          }),
        });
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add assistant response to chat
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        content: data.response,
        sender: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Check if there are suggested products
      if (data.suggested_products && data.suggested_products.length > 0) {
        setSuggestedProducts(data.suggested_products);
      }
      
      // Check if there's an action that requires user confirmation
      if (data.requires_action && data.action_data) {
        setRequiresAction(true);
        setActionData(data.action_data);
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

  // Handle confirming an action
  const handleConfirmAction = async (confirmed: boolean) => {
    if (!actionData) return;
    
    try {
      setIsLoading(true);
      
      const response = await fetch('http://localhost:8000/api/action/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          action_type: actionData.type,
          action_data: actionData,
          confirmed,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Add confirmation message to chat
      const confirmationMessage: Message = {
        id: `confirmation_${Date.now()}`,
        content: confirmed 
          ? result.message || 'Action confirmed successfully.' 
          : 'Action cancelled.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, confirmationMessage]);
      
      // If it was a checkout action and it was successful, redirect to checkout URL
      if (confirmed && actionData.type === 'checkout' && result.status === 'success' && result.data?.checkout?.checkout_url) {
        window.location.href = result.data.checkout.checkout_url;
      }
    } catch (error) {
      console.error('Error confirming action:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        content: 'Sorry, I encountered an error processing your request.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setRequiresAction(false);
      setActionData(null);
    }
  };

  // Handle image selection
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      
      // Create a preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle clicking the image upload button
  const handleImageUploadClick = () => {
    fileInputRef.current?.click();
  };

  // Handle removing the selected image
  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
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
      
      {/* Main content */}
      <div className="flex-1 overflow-hidden flex flex-row max-w-7xl w-full mx-auto p-4">
        {/* Chat area */}
        <div className="flex-1 overflow-hidden flex flex-col">
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
          
          {/* Action confirmation */}
          {requiresAction && actionData && (
            <div className="mb-4 p-4 border border-yellow-300 bg-yellow-50 rounded-lg">
              <h3 className="text-lg font-medium mb-2">Confirm Action</h3>
              
              {actionData.type === 'add_to_cart' && actionData.product && (
                <div>
                  <p>Add to cart: {actionData.product.name}</p>
                  <p>Quantity: {actionData.quantity || 1}</p>
                  <p>Price: ${actionData.product.price.toFixed(2)}</p>
                </div>
              )}
              
              {actionData.type === 'checkout' && (
                <div>
                  <p>Proceed to checkout</p>
                  <p>Total: ${actionData.cart?.total.toFixed(2) || '0.00'}</p>
                </div>
              )}
              
              <div className="flex mt-4 space-x-2">
                <button
                  onClick={() => handleConfirmAction(true)}
                  className="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
                  disabled={isLoading}
                >
                  Confirm
                </button>
                <button
                  onClick={() => handleConfirmAction(false)}
                  className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
                  disabled={isLoading}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
          
          {/* Image preview */}
          {imagePreview && (
            <div className="mb-4 relative">
              <img 
                src={imagePreview} 
                alt="Selected" 
                className="h-32 object-contain rounded border border-gray-300" 
              />
              <button
                onClick={handleRemoveImage}
                className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
              >
                ×
              </button>
            </div>
          )}
          
          {/* Input area */}
          <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
            <button
              type="button"
              onClick={handleImageUploadClick}
              className="bg-gray-200 text-gray-700 rounded-lg p-2 hover:bg-gray-300 focus:outline-none"
              disabled={isLoading}
            >
              📷
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageSelect}
              accept="image/*"
              className="hidden"
            />
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
              disabled={isLoading || (!input.trim() && !selectedImage)}
            >
              Send
            </button>
          </form>
        </div>
        
        {/* Product carousel */}
        {suggestedProducts.length > 0 && (
          <div className="w-80 ml-4 overflow-y-auto border-l border-gray-200 pl-4">
            <h3 className="text-lg font-medium mb-4">Suggested Products</h3>
            <div className="space-y-4">
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
                    onClick={async () => {
                      try {
                        const response = await fetch(`http://localhost:8000/api/cart/${sessionId}`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            action_type: 'add',
                            product_id: product.id,
                            quantity: 1,
                          }),
                        });
                        
                        if (!response.ok) {
                          throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        
                        // Add a message to the chat
                        const cartMessage: Message = {
                          id: `cart_${Date.now()}`,
                          content: `Added ${product.name} to your cart.`,
                          sender: 'assistant',
                          timestamp: new Date(),
                        };
                        
                        setMessages((prev) => [...prev, cartMessage]);
                      } catch (error) {
                        console.error('Error adding to cart:', error);
                      }
                    }}
                  >
                    Add to Cart
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 