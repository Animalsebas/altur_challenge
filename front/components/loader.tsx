"use client";

import React from 'react';
import { Logo } from '@/components/icons'

export const CallAnalysisLoader = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-black transition-colors duration-500 p-8">
      
      <div className="relative w-24 h-24 mb-6">
        <Logo 
          size={96}
          className="animate-spin-slow" 
        />
        
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-indigo-500/50 dark:bg-indigo-400/30 animate-pulse" />
        </div>
      </div>

      <p className="text-xl font-semibold text-gray-700 dark:text-gray-300 animate-typing overflow-hidden whitespace-nowrap border-r-4 border-r-indigo-500 pr-1">
        Analyzing call...
      </p>
      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 opacity-0 animate-fade-in delay-1000">
        This will take a moment.
      </p>

    </div>
  );
};