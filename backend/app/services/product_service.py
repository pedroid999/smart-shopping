"""
Product service for handling product search and retrieval.
In the MVP, this uses a mock product database.
In a production environment, this would connect to Elasticsearch or another search engine.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
import random
from datetime import datetime

# Local imports
from app.models.response_models import Product, ProductDetails

logger = logging.getLogger(__name__)

# Mock product data for the MVP
MOCK_PRODUCTS = [
    {
        "id": "p1001",
        "name": "Budget Gaming Laptop",
        "description": "Affordable gaming laptop with great performance",
        "price": 799.99,
        "image_url": "https://example.com/images/laptop1.jpg",
        "category": "Laptops",
        "brand": "TechX",
        "rating": 4.3,
        "in_stock": True,
        "long_description": "This budget gaming laptop offers excellent value with a powerful processor, dedicated graphics card, and a high refresh rate display. Perfect for gamers on a budget.",
        "specifications": {
            "processor": "AMD Ryzen 5 5600H",
            "memory": "8GB DDR4",
            "storage": "512GB SSD",
            "display": "15.6-inch FHD (1920x1080) 144Hz",
            "graphics": "NVIDIA GeForce GTX 1650",
            "operating_system": "Windows 11 Home"
        },
        "tags": ["gaming", "budget", "laptop", "nvidia", "amd"]
    },
    {
        "id": "p1002",
        "name": "Ultra-thin Professional Laptop",
        "description": "Sleek and powerful laptop for professionals",
        "price": 1299.99,
        "image_url": "https://example.com/images/laptop2.jpg",
        "category": "Laptops",
        "brand": "Macrosoft",
        "rating": 4.7,
        "in_stock": True,
        "long_description": "The ultimate professional laptop with a beautiful design, long battery life, and powerful performance. Perfect for business users and creators.",
        "specifications": {
            "processor": "Intel Core i7-1185G7",
            "memory": "16GB LPDDR4X",
            "storage": "1TB SSD",
            "display": "14-inch QHD (2560x1440) IPS",
            "graphics": "Intel Iris Xe Graphics",
            "operating_system": "Windows 11 Pro"
        },
        "tags": ["professional", "thin", "lightweight", "business", "premium"]
    },
    {
        "id": "p1003",
        "name": "Smart 4K Television",
        "description": "4K UHD Smart TV with voice control",
        "price": 549.99,
        "image_url": "https://example.com/images/tv1.jpg",
        "category": "Televisions",
        "brand": "VisionPlus",
        "rating": 4.5,
        "in_stock": True,
        "long_description": "Experience stunning 4K resolution and smart features with this affordable television. Includes popular streaming apps and voice control capabilities.",
        "specifications": {
            "screen_size": "55 inches",
            "resolution": "3840x2160 (4K UHD)",
            "refresh_rate": "60Hz",
            "smart_platform": "SmartHub OS",
            "connectivity": "WiFi, Bluetooth, HDMI x3, USB x2",
            "audio": "20W speakers with Dolby Audio"
        },
        "tags": ["television", "4k", "smart tv", "entertainment", "streaming"]
    },
    {
        "id": "p1004",
        "name": "Wireless Noise Cancelling Headphones",
        "description": "Premium wireless headphones with active noise cancellation",
        "price": 249.99,
        "image_url": "https://example.com/images/headphones1.jpg",
        "category": "Audio",
        "brand": "SoundMaster",
        "rating": 4.8,
        "in_stock": True,
        "long_description": "These premium wireless headphones deliver exceptional sound quality and industry-leading noise cancellation. With long battery life and comfortable design, they're perfect for travel or daily use.",
        "specifications": {
            "type": "Over-ear",
            "connectivity": "Bluetooth 5.0, 3.5mm jack",
            "battery_life": "Up to 30 hours",
            "noise_cancellation": "Active, adjustable levels",
            "color": "Black",
            "weight": "250g"
        },
        "tags": ["audio", "wireless", "headphones", "noise cancelling", "bluetooth"]
    },
    {
        "id": "p1005",
        "name": "High-Performance Smartphone",
        "description": "Flagship smartphone with advanced camera system",
        "price": 899.99,
        "image_url": "https://example.com/images/phone1.jpg",
        "category": "Smartphones",
        "brand": "Pear",
        "rating": 4.9,
        "in_stock": True,
        "long_description": "This flagship smartphone features the latest technology including an advanced camera system, powerful processor, and all-day battery life. Perfect for photography enthusiasts and power users.",
        "specifications": {
            "display": "6.5-inch OLED (2778x1284) 120Hz",
            "processor": "OctoCore 5nm chipset",
            "memory": "8GB RAM",
            "storage": "256GB",
            "camera": "Triple camera: 48MP main, 12MP ultrawide, 12MP telephoto",
            "battery": "4500mAh",
            "operating_system": "PearOS 15"
        },
        "tags": ["smartphone", "camera", "mobile", "5g", "flagship"]
    }
]

class ProductService:
    """Service for retrieving and searching products."""
    
    def __init__(self):
        """Initialize the product service with mock data for MVP."""
        self.products = {p["id"]: p for p in MOCK_PRODUCTS}
        logger.info(f"Initialized ProductService with {len(self.products)} products")
        
    def search_products(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        page: int = 1, 
        page_size: int = 10
    ) -> List[Product]:
        """
        Search for products based on query and filters.
        
        Args:
            query: Search query text
            filters: Optional filters (price range, category, etc.)
            page: Page number for pagination
            page_size: Number of results per page
            
        Returns:
            List of matching products
        """
        # In a real app, this would use Elasticsearch or similar
        # For MVP, we'll do a simple text search on our mock data
        
        results = []
        query = query.lower()
        
        for product_data in self.products.values():
            # Simple text matching on various fields
            if (query in product_data["name"].lower() or 
                query in product_data["description"].lower() or 
                query in product_data["category"].lower() or 
                query in product_data.get("brand", "").lower()):
                
                # Apply filters if provided
                if filters:
                    # Example filter: price range
                    if "min_price" in filters and product_data["price"] < filters["min_price"]:
                        continue
                    if "max_price" in filters and product_data["price"] > filters["max_price"]:
                        continue
                    
                    # Example filter: category
                    if "category" in filters and product_data["category"] != filters["category"]:
                        continue
                    
                    # Example filter: brand
                    if "brand" in filters and product_data["brand"] != filters["brand"]:
                        continue
                
                # Add to results
                results.append(Product(**product_data))
        
        # Handle pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return results[start_idx:end_idx]
    
    def get_product_details(self, product_id: str) -> Optional[ProductDetails]:
        """
        Get detailed information about a specific product.
        
        Args:
            product_id: Unique product identifier
            
        Returns:
            ProductDetails object if found, None otherwise
        """
        if product_id in self.products:
            return ProductDetails(**self.products[product_id])
        return None
    
    def get_products_by_category(self, category: str, limit: int = 10) -> List[Product]:
        """
        Get products by category.
        
        Args:
            category: Product category
            limit: Maximum number of products to return
            
        Returns:
            List of products in the category
        """
        results = []
        for product_data in self.products.values():
            if product_data["category"] == category:
                results.append(Product(**product_data))
                if len(results) >= limit:
                    break
        return results
    
    def get_related_products(self, product_id: str, limit: int = 5) -> List[Product]:
        """
        Get products related to a specific product.
        
        Args:
            product_id: Product to find related items for
            limit: Maximum number of related products to return
            
        Returns:
            List of related products
        """
        # In a real app, this would use a recommendation algorithm
        # For MVP, we'll just return products in the same category
        
        if product_id not in self.products:
            return []
        
        product = self.products[product_id]
        category = product["category"]
        
        results = []
        for pid, pdata in self.products.items():
            if pid != product_id and pdata["category"] == category:
                results.append(Product(**pdata))
                if len(results) >= limit:
                    break
        
        return results 