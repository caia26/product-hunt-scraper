'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { supabase, Product } from './supabase';

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

const PAGE_SIZE = 20;

async function fetchProductsPaginated(page: number, pageSize: number): Promise<Product[]> {
  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .order('upvotes', { ascending: false })
    .range(from, to);
  if (error) {
    console.error('Error fetching products:', error);
    return [];
  }
  return data || [];
}

async function fetchTotalProductCount(): Promise<number> {
  const { count, error } = await supabase
    .from('products')
    .select('*', { count: 'exact', head: true });
  if (error) {
    console.error('Error fetching product count:', error);
    return 0;
  }
  return count || 0;
}

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showPageInput, setShowPageInput] = useState(false);
  const pageInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadProducts(page);
  }, [page]);

  useEffect(() => {
    fetchTotalProductCount().then(count => {
      setTotalPages(Math.max(1, Math.ceil(count / PAGE_SIZE)));
    });
  }, [products]);

  const loadProducts = async (pageNum: number) => {
    try {
      const data = await fetchProductsPaginated(pageNum, PAGE_SIZE);
      setProducts(data);
    } catch (error) {
      setMessage('Error loading products');
    }
  };

  const handleScrape = async () => {
    if (!startDate || !endDate) {
      setMessage('Please select both start and end dates');
      return;
    }
    setIsLoading(true);
    setMessage('');
    try {
      const res = await fetch('/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ startDate, endDate, maxProductsPerDay: 20, maxTotalProducts: 100 })
      });
      const result = await res.json();
      setMessage(result.message || 'Scraping started');
      setTimeout(() => loadProducts(1), 2000);
      setPage(1);
    } catch (error) {
      setMessage('Error starting scraping process');
    } finally {
      setIsLoading(false);
    }
  };

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
  
  // Pagination logic
  const renderPagination = () => {
    const pages: (number | string)[] = [];
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (page <= 3) {
        pages.push(1, 2, 3, '...', totalPages);
      } else if (page >= totalPages - 2) {
        pages.push(1, '...', totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, '...', page - 1, page, page + 1, '...', totalPages);
      }
    }
    return (
      <div className="flex items-center justify-center gap-2 mt-6 select-none">
        <button
          onClick={() => setPage(page - 1)}
          disabled={page === 1}
          className="rounded-full w-8 h-8 flex items-center justify-center text-red-500 disabled:text-gray-300 bg-white border border-gray-200"
        >
          &lt;
        </button>
        {pages.map((p, idx) =>
          p === '...'
            ? <span
                key={`ellipsis-${idx}`}
                className="w-8 h-8 flex items-center justify-center cursor-pointer text-gray-400 hover:text-blue-500"
                onClick={() => setShowPageInput(true)}
              >
                ...
              </span>
            : <button
                key={`page-${p}-${idx}`}
                onClick={() => setPage(Number(p))}
                className={`rounded-full w-8 h-8 flex items-center justify-center ${page === p ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-blue-100'}`}
                style={{ fontWeight: page === p ? 'bold' : 'normal', borderBottom: page === p ? '2px solid #3b82f6' : 'none' }}
              >
                {p}
              </button>
        )}
        <button
          onClick={() => setPage(page + 1)}
          disabled={page === totalPages}
          className="rounded-full w-8 h-8 flex items-center justify-center text-red-500 disabled:text-gray-300 bg-white border border-gray-200"
        >
          &gt;
        </button>
        {showPageInput && (
          <div className="ml-2 relative z-10">
            <input
              ref={pageInputRef}
              type="number"
              min={1}
              max={totalPages}
              defaultValue={page}
              className="w-16 px-2 py-1 border rounded focus:outline-none focus:ring"
              onKeyDown={e => {
                if (e.key === 'Enter') {
                  const val = Number((e.target as HTMLInputElement).value);
                  if (val >= 1 && val <= totalPages) setPage(val);
                  setShowPageInput(false);
                } else if (e.key === 'Escape') {
                  setShowPageInput(false);
                }
              }}
              onBlur={() => setShowPageInput(false)}
              autoFocus
            />
          </div>
        )}
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Product Hunt Database</h1>
        {/* Date Range Controls */}
        <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Date Range</h2>
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                id="startDate"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                id="endDate"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleScrape}
                disabled={isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                Scrape Products
              </button>
            </div>
          </div>
          {message && (
            <div className="mt-4 p-4 rounded-md bg-blue-50">
              <p className="text-sm text-blue-700">{message}</p>
            </div>
          )}
        </div>
        {/* Products Table */}
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
                          {product.website_url && (
                            <a 
                              href={product.website_url} 
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
        {renderPagination()}
      </div>
    </main>
  );
} 