# AI-Powered E-commerce Shopping Assistant

An intelligent AI-powered shopping assistant that allows users to shop using natural language conversations.

## Project Overview

This platform acts as a conversational shopping assistant for end-users, allowing them to shop using natural language. A customer can simply type a prompt like "Find me the best budget-friendly laptop" into the interface. The AI interprets this query and conducts an extensive search across the product catalog to retrieve suitable options.

## Key Features

- **Natural Language Shopping**: Users can describe what they're looking for in plain English
- **AI-Powered Product Recommendations**: The system uses LLMs to understand user intent and recommend products
- **Human-in-the-Loop**: Users remain in control for all critical decisions like purchases
- **Conversational Experience**: The assistant can ask clarifying questions and provide explanations

## Technical Architecture

The system consists of:

- **Frontend**: Next.js web application providing a chat interface
- **Backend**: Python-based microservices architecture
- **AI Agent**: LangGraph-powered autonomous agent for product search and recommendations
- **Database**: Product catalog and user session storage

## Getting Started

### Prerequisites

- Python 3.9+ for the backend
- Node.js 18+ for the frontend
- OpenAI API key (for the AI agent)
- Stripe API key (for payment processing)

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-shopping-assistant.git
cd ai-shopping-assistant
```

2. Create and activate a virtual environment:
```bash
# Create a virtual environment
cd backend
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory with the following content:

```bash
cd backend
echo "OPENAI_API_KEY=<your-openai-api-key>" > .env
```

5. Run the backend:
```bash
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to see the application.

## License

This project is proprietary and confidential. 