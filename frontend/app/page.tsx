import { SearchComponent } from "@/components/SearchComponent";
import { ThemeToggle } from "@/components/theme-toggle";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-[80vh] p-6 text-center relative">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>
      <div className="space-y-6 mb-10 max-w-3xl">
        <h1 className="text-5xl md:text-7xl font-serif font-bold tracking-tight text-neutral-900 dark:text-white mb-4">
          Domain*Dora
        </h1>
        <p className="text-lg md:text-xl text-neutral-600 dark:text-neutral-400 max-w-4xl mx-auto font-sans leading-relaxed">
          Understand what's behind any domain. Explore domain registration, DNS infrastructure, SSL certificates, IP networks, and more.
        </p>
      </div>

      <div className="w-full">
        <SearchComponent />
      </div>

      <div className="mt-8 text-neutral-500 text-sm">
        Try:
        <a href="/lookup/google.com" className="ml-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors">google.com</a> &middot;
        <a href="/lookup/8.8.8.8" className="mx-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors">8.8.8.8</a> &middot;
        <a href="/lookup/AS15169" className="text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors">AS15169</a>
      </div>
    </main>
  );
}
