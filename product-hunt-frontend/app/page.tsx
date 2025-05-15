import Link from 'next/link';
import { getTopProducts, Product } from './supabase';

export const revalidate = 3600; // Revalidate every hour

export default async function Home() {
  const products = await getTopProducts(20);
  
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
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tagline</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Upvotes</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Launch Date</th>
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
                        <div className="ml-4">
                          <Link href={`/product/${product.id}`} className="text-sm font-medium text-blue-600 hover:text-blue-800">{product.name}</Link>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{product.tagline}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{product.upvotes}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.launch_date ? new Date(product.launch_date).toLocaleDateString() : '-'}
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