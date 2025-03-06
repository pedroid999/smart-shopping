'use client';

import axios from 'axios';

// Define the base URL for the API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Define types
export type ChatRequest = {
  session_id: string;
  message: string;
  context?: Record<string, unknown>;
};

export type ChatResponse = {
  session_id: string;
  response: string;
  requires_action: boolean;
  action_data?: Record<string, unknown>;
  suggested_products?: Product[];
};

export type Product = {
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

export type ProductDetails = Product & {
  long_description?: string;
  specifications?: Record<string, unknown>;
  reviews?: Array<Record<string, unknown>>;
  related_products?: string[];
  tags?: string[];
};

export type SearchRequest = {
  query: string;
  filters?: Record<string, unknown>;
  page?: number;
  page_size?: number;
};

export type SearchResponse = {
  products: Product[];
  total: number;
  page: number;
  page_size: number;
};

export type CartAction = {
  action_type: 'add' | 'remove' | 'update';
  product_id: string;
  quantity?: number;
};

export type CartItem = {
  product: Product;
  quantity: number;
  item_total: number;
};

export type CartResponse = {
  session_id: string;
  items: CartItem[];
  subtotal: number;
  tax?: number;
  shipping?: number;
  total: number;
};

export type CheckoutRequest = {
  email: string;
  success_url: string;
  cancel_url: string;
  shipping_address?: Record<string, string>;
  billing_address?: Record<string, string>;
};

export type CheckoutResponse = {
  session_id: string;
  checkout_url: string;
  checkout_id: string;
};

// API service functions
export const ApiService = {
  // Chat API
  sendChatMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/api/chat', request);
    return response.data;
  },

  // Product search API
  searchProducts: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>('/api/search', request);
    return response.data;
  },

  // Get product details
  getProductDetails: async (productId: string): Promise<ProductDetails> => {
    const response = await apiClient.get<ProductDetails>(`/api/products/${productId}`);
    return response.data;
  },

  // Cart operations
  getCart: async (sessionId: string): Promise<CartResponse> => {
    const response = await apiClient.get<CartResponse>(`/api/cart/${sessionId}`);
    return response.data;
  },

  updateCart: async (sessionId: string, action: CartAction): Promise<CartResponse> => {
    const response = await apiClient.post<CartResponse>(`/api/cart/${sessionId}`, action);
    return response.data;
  },

  // Checkout
  createCheckout: async (sessionId: string, request: CheckoutRequest): Promise<CheckoutResponse> => {
    const response = await apiClient.post<CheckoutResponse>(`/api/checkout/${sessionId}`, request);
    return response.data;
  },
};

export default ApiService; 