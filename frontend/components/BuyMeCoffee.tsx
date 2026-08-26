"use client";

import { motion } from "framer-motion";

export function BuyMeCoffee() {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
      <motion.a
        href="https://buymeacoffee.com/sun_god_vicky"
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-center gap-2 rounded-full bg-white/70 dark:bg-neutral-900/30 backdrop-blur-md px-5 py-3 font-semibold text-neutral-900 dark:text-white border border-neutral-200/50 dark:border-neutral-700/50 hover:bg-white/90 dark:hover:bg-neutral-800/40 transition-colors shadow-sm dark:shadow-none"
        initial={{ opacity: 0, y: 20, scale: 0.8 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{
          duration: 0.5,
          delay: 1,
          type: "spring",
          stiffness: 260,
          damping: 20
        }}
        whileHover={{
          scale: 1.05
        }}
        whileTap={{ scale: 0.95 }}
      >
        <motion.span
          animate={{ rotate: [0, -15, 15, -15, 0] }}
          transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut", repeatDelay: 3 }}
          className="text-xl"
        >
          ☕
        </motion.span>
        <span>Buy Me a Coffee</span>

        {/* Subtle shine effect wrapper */}
        <div className="absolute inset-0 overflow-hidden rounded-full pointer-events-none">
          <motion.div
            className="absolute top-0 left-0 h-full w-1/2 bg-white/30 skew-x-[-20deg]"
            initial={{ x: "-200%" }}
            animate={{ x: "300%" }}
            transition={{
              repeat: Infinity,
              duration: 2.5,
              ease: "easeInOut",
              repeatDelay: 4
            }}
          />
        </div>
      </motion.a>
    </div>
  );
}
