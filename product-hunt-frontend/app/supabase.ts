import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface Product {
  id: string;
  name: string;
  tagline: string;
  description: string | null;
  url: string | null;
  website_url: string | null;
  thumbnail_url: string | null;
  launch_date: string | null;
  upvotes: number;
  maker_ids: string[] | null;
  topics: string[] | null;
  created_at: string;
  updated_at: string;
}

export async function getTopProducts(limit = 10): Promise<Product[]> {
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .order('upvotes', { ascending: false })
    .limit(limit);
  
  if (error) {
    console.error('Error fetching products:', error);
    return [];
  }
  
  return data || [];
}

export async function getProductById(id: string): Promise<Product | null> {
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .eq('id', id)
    .single();
  
  if (error) {
    console.error('Error fetching product:', error);
    return null;
  }
  
  return data;
}

export async function getProductsByDate(date: string): Promise<Product[]> {
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .eq('launch_date', date)
    .order('upvotes', { ascending: false });
  
  if (error) {
    console.error('Error fetching products by date:', error);
    return [];
  }
  
  return data || [];
}

export async function searchProducts(query: string): Promise<Product[]> {
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .or(`name.ilike.%${query}%,tagline.ilike.%${query}%,description.ilike.%${query}%`)
    .order('upvotes', { ascending: false })
    .limit(20);
  
  if (error) {
    console.error('Error searching products:', error);
    return [];
  }
  
  return data || [];
} 