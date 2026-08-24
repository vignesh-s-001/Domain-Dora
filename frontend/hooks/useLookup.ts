import { useQuery } from '@tanstack/react-query';
import { LookupResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

async function fetchLookup(query: string): Promise<LookupResponse> {
  const response = await fetch(`${API_BASE_URL}/lookup/${encodeURIComponent(query)}`);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch lookup data');
  }
  
  return response.json();
}

export function useLookup(query: string) {
  return useQuery<LookupResponse, Error>({
    queryKey: ['lookup', query],
    queryFn: () => fetchLookup(query),
    enabled: !!query,
    retry: false, // Don't retry on 404s/400s
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
