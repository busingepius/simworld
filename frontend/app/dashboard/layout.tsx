"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    const token = localStorage.getItem('simworld_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  if (!isClient) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0B0F19] text-gray-900 dark:text-gray-100 font-sans selection:bg-indigo-500/30">
      <nav className="sticky top-0 z-50 backdrop-blur-md bg-white/70 dark:bg-[#0B0F19]/70 border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="flex items-center gap-2 group">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 dark:bg-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/30 group-hover:scale-105 transition-transform">
                  S
                </div>
                <span className="text-xl font-extrabold tracking-tight text-gray-900 dark:text-white">SimWorld</span>
              </Link>
              <div className="hidden sm:flex items-center space-x-1">
                <Link href="/dashboard" className="px-3 py-2 rounded-md text-sm font-medium bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white transition-colors">
                  Overview
                </Link>
                <Link href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  Analytics
                </Link>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  localStorage.removeItem('simworld_token');
                  router.push('/login');
                }}
                className="text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white px-3 py-2 rounded-md transition-colors"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="relative">
        <div className="absolute inset-x-0 top-0 h-96 bg-gradient-to-b from-indigo-50/50 to-transparent dark:from-indigo-900/10 pointer-events-none" />
        <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8 relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
}
