import Link from 'next/link';
import { getTopProducts, Product } from './supabase';

// Expanded color mapping for topics with more categories
const topicColors: { [key: string]: string } = {
  // Technology
  'AI': 'bg-purple-100 text-purple-800',
  'Artificial Intelligence': 'bg-purple-100 text-purple-800',
  'Machine Learning': 'bg-purple-100 text-purple-800',
  'Developer Tools': 'bg-blue-100 text-blue-800',
  'Development': 'bg-blue-100 text-blue-800',
  'Programming': 'bg-blue-100 text-blue-800',
  'API': 'bg-blue-100 text-blue-800',
  'Web App': 'bg-blue-100 text-blue-800',
  'Mobile App': 'bg-blue-100 text-blue-800',
  'SaaS': 'bg-blue-100 text-blue-800',
  'Software': 'bg-blue-100 text-blue-800',
  
  // Business & Productivity
  'Productivity': 'bg-green-100 text-green-800',
  'Business': 'bg-green-100 text-green-800',
  'Startup': 'bg-green-100 text-green-800',
  'Workflow': 'bg-green-100 text-green-800',
  'Project Management': 'bg-green-100 text-green-800',
  'CRM': 'bg-green-100 text-green-800',
  'HR': 'bg-green-100 text-green-800',
  
  // Design & Creative
  'Design': 'bg-pink-100 text-pink-800',
  'Design Tools': 'bg-pink-100 text-pink-800',
  'UI/UX': 'bg-pink-100 text-pink-800',
  'Graphic Design': 'bg-pink-100 text-pink-800',
  'Creative': 'bg-pink-100 text-pink-800',
  
  // Marketing & Analytics
  'Marketing': 'bg-yellow-100 text-yellow-800',
  'SEO': 'bg-yellow-100 text-yellow-800',
  'Social Media': 'bg-yellow-100 text-yellow-800',
  'Analytics': 'bg-indigo-100 text-indigo-800',
  'Data': 'bg-indigo-100 text-indigo-800',
  'Business Intelligence': 'bg-indigo-100 text-indigo-800',
  
  // Social & Communication
  'Social': 'bg-red-100 text-red-800',
  'Communication': 'bg-red-100 text-red-800',
  'Community': 'bg-red-100 text-red-800',
  'Chat': 'bg-red-100 text-red-800',
  'Messaging': 'bg-red-100 text-red-800',
  
  // Finance & Money
  'Finance': 'bg-emerald-100 text-emerald-800',
  'Fintech': 'bg-emerald-100 text-emerald-800',
  'Payments': 'bg-emerald-100 text-emerald-800',
  'Banking': 'bg-emerald-100 text-emerald-800',
  
  // Education & Learning
  'Education': 'bg-cyan-100 text-cyan-800',
  'Learning': 'bg-cyan-100 text-cyan-800',
  'Edtech': 'bg-cyan-100 text-cyan-800',
  'Online Learning': 'bg-cyan-100 text-cyan-800',
  
  // Default for any unmatched topics
  'default': 'bg-gray-100 text-gray-800'
};

export const revalidate = 3600;

export default async function Home() {
  const products = await getTopProducts(20);
  
  const getTopicColor = (topic: string) => {
    // Try exact match first
    if (topicColors[topic]) {
      return topicColors[topic];
    }
    
    // Try case-insensitive match
    const lowerTopic = topic.toLowerCase();
    for (const [key, value] of Object.entries(topicColors)) {
      if (key.toLowerCase() === lowerTopic) {
        return value;
      }
    }
    
    // If no match found, use default
    return topicColors.default;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };
  
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Product Hunt Database</h1>
        
        {products.length === 0 ? (
          <div className="bg-white p-6 rounded-md shadow-sm">
            <p className="text-gray-600">No products found. Make sure your Supabase connection is properly configured.</p>
          </div>
        ) : (
          <div className="overflow-hidden bg-white shadow-sm rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="w-64 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Votes</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Launch Date</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Topics</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product: Product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-md flex items-center justify-center">
                          {product.thumbnail_url ? (
                            <img src={product.thumbnail_url} alt="" className="h-10 w-10 rounded-md" />
                          ) : (
                            <span className="text-gray-500 text-xs">PH</span>
                          )}
                        </div>
                        <div className="ml-4 min-w-0">
                          <div className="flex items-center gap-2">
                            <Link href={`/product/${product.id}`} className="text-sm font-medium text-blue-600 hover:text-blue-800 truncate max-w-[180px]" title={product.name}>
                              {product.name}
                            </Link>
                            {product.url && (
                              <a 
                                href={product.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                                title="Visit website"
                              >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-500 line-clamp-2">{product.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{product.upvotes}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(product.launch_date)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-2">
                        {product.topics?.map((topic, index) => (
                          <span 
                            key={index}
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTopicColor(topic)}`}
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
} 