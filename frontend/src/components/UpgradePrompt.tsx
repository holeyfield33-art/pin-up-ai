import React from 'react';
import { Sparkles, X, Zap, Lock, ArrowRight } from 'lucide-react';
import { cn } from '../utils/helpers';

/* -------------------------------------------------------------------------- */
/*  Types                                                                     */
/* -------------------------------------------------------------------------- */

interface UpgradePromptProps {
  /** "banner" = slim inline bar, "modal" = centered dialog, "card" = sidebar card */
  variant?: 'banner' | 'modal' | 'card';
  /** What triggered the prompt */
  reason?: 'snippet_limit' | 'trial_expired' | 'feature_locked' | 'generic';
  /** Custom message override */
  message?: string;
  /** Days left in trial (shown when > 0) */
  daysLeft?: number;
  onActivate: () => void;
  onDismiss?: () => void;
}

/* -------------------------------------------------------------------------- */
/*  Content map                                                               */
/* -------------------------------------------------------------------------- */

const REASONS: Record<string, { title: string; body: string; icon: React.ElementType }> = {
  snippet_limit: {
    title: 'Snippet limit reached',
    body: 'Free accounts are limited to 100 snippets. Upgrade to Pro for unlimited storage.',
    icon: Lock,
  },
  trial_expired: {
    title: 'Trial expired',
    body: 'Your 14-day trial has ended. Activate a license to continue using all features.',
    icon: Zap,
  },
  feature_locked: {
    title: 'Pro feature',
    body: 'This feature requires a Pro license. Upgrade to unlock collections, MCP, and more.',
    icon: Lock,
  },
  generic: {
    title: 'Upgrade to Pro',
    body: 'Unlock unlimited snippets, collections, MCP integration, and priority support.',
    icon: Sparkles,
  },
};

/* -------------------------------------------------------------------------- */
/*  Banner variant                                                            */
/* -------------------------------------------------------------------------- */

const Banner: React.FC<UpgradePromptProps> = ({ reason = 'generic', message, daysLeft, onActivate, onDismiss }) => {
  const content = REASONS[reason] || REASONS.generic;
  const Icon = content.icon;

  return (
    <div className="flex items-center gap-3 px-4 py-2.5 bg-gradient-to-r from-brand-600 to-brand-500 text-white text-sm">
      <Icon className="w-4 h-4 shrink-0" />
      <span className="flex-1">
        {message || content.body}
        {daysLeft !== undefined && daysLeft > 0 && (
          <span className="ml-1 opacity-80">({daysLeft} days left)</span>
        )}
      </span>
      <button
        onClick={onActivate}
        className="shrink-0 px-3 py-1 bg-white/20 hover:bg-white/30 rounded-md font-medium transition-colors"
      >
        Upgrade
      </button>
      {onDismiss && (
        <button onClick={onDismiss} className="shrink-0 p-0.5 hover:bg-white/20 rounded transition-colors">
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/*  Card variant (for sidebar)                                                */
/* -------------------------------------------------------------------------- */

const Card: React.FC<UpgradePromptProps> = ({ reason = 'generic', daysLeft, onActivate }) => {
  const content = REASONS[reason] || REASONS.generic;
  const Icon = content.icon;

  return (
    <div className="mx-3 my-2 p-3 rounded-lg bg-gradient-to-br from-brand-50 to-brand-100 dark:from-brand-900/30 dark:to-brand-800/20 border border-brand-200 dark:border-brand-700/50">
      <div className="flex items-center gap-2 mb-1.5">
        <Icon className="w-4 h-4 text-brand-600 dark:text-brand-400" />
        <span className="text-xs font-semibold text-brand-700 dark:text-brand-300">{content.title}</span>
      </div>
      <p className="text-xs text-brand-600 dark:text-brand-400 mb-2 leading-relaxed">
        {content.body}
      </p>
      {daysLeft !== undefined && daysLeft > 0 && (
        <p className="text-xs text-brand-500 dark:text-brand-400 mb-2 font-medium">
          {daysLeft} day{daysLeft !== 1 ? 's' : ''} remaining
        </p>
      )}
      <button
        onClick={onActivate}
        className={cn(
          'w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
          'bg-brand-600 hover:bg-brand-700 text-white',
        )}
      >
        <Sparkles className="w-3 h-3" />
        Upgrade to Pro
        <ArrowRight className="w-3 h-3" />
      </button>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/*  Modal variant                                                             */
/* -------------------------------------------------------------------------- */

const Modal: React.FC<UpgradePromptProps> = ({ reason = 'generic', message, daysLeft, onActivate, onDismiss }) => {
  const content = REASONS[reason] || REASONS.generic;
  const Icon = content.icon;

  const PRO_FEATURES = [
    'Unlimited snippets',
    'Collections & organization',
    'MCP server integration',
    'Import / Export',
    'Priority support',
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onDismiss?.()}
    >
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        {/* Header gradient */}
        <div className="bg-gradient-to-r from-brand-600 to-brand-500 px-6 py-5 text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Icon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold">{content.title}</h2>
              <p className="text-sm opacity-90">{message || content.body}</p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="px-6 py-4">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Everything in Pro:
          </p>
          <ul className="space-y-2">
            {PRO_FEATURES.map((feat) => (
              <li key={feat} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Sparkles className="w-3.5 h-3.5 text-brand-500 shrink-0" />
                {feat}
              </li>
            ))}
          </ul>
          {daysLeft !== undefined && daysLeft > 0 && (
            <p className="mt-3 text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-3 py-1.5 rounded">
              Your trial has {daysLeft} day{daysLeft !== 1 ? 's' : ''} remaining
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex gap-3">
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="flex-1 px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              Maybe later
            </button>
          )}
          <button
            onClick={onActivate}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              'bg-brand-600 hover:bg-brand-700 text-white',
            )}
          >
            <Sparkles className="w-4 h-4" />
            Activate License
          </button>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/*  Composite export                                                          */
/* -------------------------------------------------------------------------- */

export const UpgradePrompt: React.FC<UpgradePromptProps> = (props) => {
  switch (props.variant) {
    case 'banner':
      return <Banner {...props} />;
    case 'card':
      return <Card {...props} />;
    case 'modal':
      return <Modal {...props} />;
    default:
      return <Banner {...props} />;
  }
};
