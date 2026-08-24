"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search } from 'lucide-react';
import { motion } from 'framer-motion';

export function SearchComponent({ initialQuery = '' }: { initialQuery?: string }) {
  const [query, setQuery] = useState(initialQuery);
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      let cleanQuery = query.trim();
      // Remove protocol if user pasted a full URL
      cleanQuery = cleanQuery.replace(/^https?:\/\//i, '');
      // Remove trailing slash if exists
      cleanQuery = cleanQuery.replace(/\/$/, '');
      
      router.push(`/lookup/${encodeURIComponent(cleanQuery)}`);
    }
  };

  return (
    <motion.form 
      onSubmit={handleSearch}
      className="relative w-full max-w-2xl mx-auto"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-neutral-400 group-focus-within:text-white transition-colors">
          <Search size={20} />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search domain, IP address, or ASN..."
          className="w-full pl-12 pr-24 py-4 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 transition-all shadow-sm hover:border-neutral-300 dark:hover:border-neutral-700"
          autoFocus
        />
        <button
          type="submit"
          disabled={!query.trim()}
          className="absolute right-2 top-2 bottom-2 px-6 bg-neutral-900 dark:bg-white text-white dark:text-black font-medium rounded-full hover:bg-neutral-800 dark:hover:bg-neutral-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Analyze
        </button>
      </div>
    </motion.form>
  );
}
