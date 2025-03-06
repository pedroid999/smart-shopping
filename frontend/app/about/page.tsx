import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gray-800">
            AI Shopping Assistant
          </Link>
          <nav>
            <Link href="/chat" className="text-blue-500 hover:text-blue-700">
              Start Shopping
            </Link>
          </nav>
        </div>
      </header>
      
      {/* Main content */}
      <main className="max-w-7xl mx-auto py-12 px-6">
        <h1 className="text-3xl font-bold mb-8">About Our AI Shopping Assistant</h1>
        
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">How It Works</h2>
          <p className="mb-4">
            Our AI-powered shopping assistant uses advanced natural language processing to understand
            your shopping needs and preferences. Simply describe what you&apos;re looking for in plain English,
            and our assistant will help you find the perfect products.
          </p>
          <p className="mb-4">
            For example, you can say things like:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>&quot;I need a budget-friendly laptop for college&quot;</li>
            <li>&quot;Find me noise-cancelling headphones under $300&quot;</li>
            <li>&quot;What&apos;s a good smartphone with an excellent camera?&quot;</li>
          </ul>
          <p>
            The assistant will ask clarifying questions if needed and provide personalized recommendations
            based on your requirements.
          </p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Key Features</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-xl font-medium mb-2">Natural Language Shopping</h3>
              <p>Shop using conversational language instead of navigating complex menus or filters.</p>
            </div>
            <div>
              <h3 className="text-xl font-medium mb-2">Personalized Recommendations</h3>
              <p>Get product suggestions tailored to your specific needs and preferences.</p>
            </div>
            <div>
              <h3 className="text-xl font-medium mb-2">Product Comparisons</h3>
              <p>The assistant can compare different products to help you make the best choice.</p>
            </div>
            <div>
              <h3 className="text-xl font-medium mb-2">Human-in-the-Loop</h3>
              <p>You remain in control of all purchasing decisions, with the AI as your helpful guide.</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Technology</h2>
          <p className="mb-4">
            Our platform is built using cutting-edge AI technology:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Large Language Models for natural conversation and understanding</li>
            <li>LangGraph for orchestrating the AI agent&apos;s reasoning and actions</li>
            <li>Next.js for a fast, responsive user interface</li>
            <li>Python backend with FastAPI for efficient processing</li>
          </ul>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t mt-12 py-8 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-gray-600">
            &copy; {new Date().getFullYear()} AI Shopping Assistant. All rights reserved.
          </p>
          <div className="mt-4">
            <Link href="/chat" className="text-blue-500 hover:text-blue-700">
              Start Shopping Now
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
} 