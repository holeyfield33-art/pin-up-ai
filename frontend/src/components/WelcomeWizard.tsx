import React, { useState } from 'react';
import { Sparkles, Pin, Search, Tags, ArrowRight, Check } from 'lucide-react';

interface WelcomeWizardProps {
  onComplete: () => void;
}

const STEPS = [
  {
    icon: Sparkles,
    title: 'Welcome to Pin-Up AI',
    description:
      'Your personal, local-first knowledge base for AI conversation highlights. Everything stays on your machine — no cloud, no accounts.',
  },
  {
    icon: Pin,
    title: 'Pin Your Best AI Moments',
    description:
      'Create snippets to save valuable outputs from Claude, ChatGPT, Grok, or any AI assistant. Add titles, tags, and source info to keep everything organized.',
  },
  {
    icon: Search,
    title: 'Lightning-Fast Search',
    description:
      'Full-text search powered by FTS5 finds any snippet in milliseconds. Use ⌘K to search instantly, or filter by tags and collections.',
  },
  {
    icon: Tags,
    title: 'Organize with Tags & Collections',
    description:
      'Color-coded tags and named collections let you group and find snippets your way. Pro users get unlimited storage and MCP integration.',
  },
] as const;

export const WelcomeWizard: React.FC<WelcomeWizardProps> = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const Icon = current.icon;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 pt-6">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={`h-2 rounded-full transition-all ${
                i === step ? 'w-8 bg-purple-600' : i < step ? 'w-2 bg-purple-300' : 'w-2 bg-gray-200'
              }`}
            />
          ))}
        </div>

        {/* Content */}
        <div className="px-8 py-10 text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-purple-100">
            <Icon className="h-8 w-8 text-purple-600" />
          </div>

          <h2 className="text-xl font-semibold text-gray-900 mb-3">{current.title}</h2>
          <p className="text-sm text-gray-500 leading-relaxed">{current.description}</p>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between px-8 pb-8">
          <button
            onClick={onComplete}
            className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            Skip
          </button>

          <button
            onClick={() => (isLast ? onComplete() : setStep(step + 1))}
            className="inline-flex items-center gap-2 rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-purple-700 transition-colors"
          >
            {isLast ? (
              <>
                Get Started <Check className="h-4 w-4" />
              </>
            ) : (
              <>
                Next <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>

        {/* Keyboard shortcuts hint on last step */}
        {isLast && (
          <div className="border-t border-gray-100 px-8 py-4 bg-gray-50">
            <p className="text-xs text-gray-400 text-center">
              ⌘N New snippet · ⌘K Search · ⌘S Save · ⌘, Settings · Esc Close
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
