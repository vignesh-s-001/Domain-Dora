"use client";

import { useLookup } from "@/hooks/useLookup";
import { SearchComponent } from "@/components/SearchComponent";
import { ResultsTabs } from "@/components/ResultsTabs";
import { AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ThemeToggle } from "@/components/theme-toggle";

export function LookupClient({ query }: { query: string }) {
  const { data, isLoading, error } = useLookup(query);

  return (
    <main className="min-h-screen p-6 md:p-12">
      <div className="max-w-5xl mx-auto flex items-center justify-between mb-12">
        <Link href="/" className="text-2xl font-serif font-bold text-neutral-900 dark:text-white tracking-tight hover:text-blue-500 dark:hover:text-blue-400 transition-colors">
          Domain-Dora
        </Link>
        <div className="w-full max-w-md hidden md:block ml-8">
          <SearchComponent initialQuery={query} />
        </div>
        <div className="ml-4">
          <ThemeToggle />
        </div>
      </div>

      <div className="md:hidden mb-8 w-full">
        <SearchComponent initialQuery={query} />
      </div>

      {isLoading && (
        <div className="flex flex-col items-center justify-center py-24">
          <Loader2 className="animate-spin text-blue-500 mb-4" size={48} />
          <h2 className="text-2xl font-medium text-neutral-900 dark:text-white">Analyzing infrastructure...</h2>
          <p className="text-neutral-500 dark:text-neutral-400 mt-2">Querying DNS, WHOIS, and SSL records</p>
        </div>
      )}

      {error && !isLoading && (
        <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl p-8 text-center max-w-2xl mx-auto mt-12">
          <AlertCircle className="mx-auto text-red-500 mb-4" size={48} />
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">Lookup Failed</h2>
          <p className="text-red-600 dark:text-red-400">{error.message}</p>
        </div>
      )}

      {data && !isLoading && !error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-8 max-w-5xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-neutral-900 dark:text-white">{data.query}</h1>
            <p className="text-neutral-500 dark:text-neutral-400 mt-3 flex items-center">
              <span className="uppercase tracking-wider text-xs font-semibold bg-blue-900/30 text-blue-400 py-1 px-2 rounded-md mr-3 border border-blue-800/30">
                {data.type}
              </span>
              Analyzed on {new Date(data.timestamp).toLocaleString()}
            </p>
          </div>
          <ResultsTabs data={data} />
        </motion.div>
      )}
    </main>
  );
}
