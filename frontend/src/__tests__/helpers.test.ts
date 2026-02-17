import { describe, it, expect } from 'vitest';
import { formatDate, formatBytes, truncate, debounce, cn } from '../utils/helpers';

describe('formatDate', () => {
  it('shows "just now" for recent timestamps', () => {
    expect(formatDate(Date.now())).toBe('just now');
  });

  it('shows minutes ago', () => {
    const fiveMinAgo = Date.now() - 5 * 60_000;
    expect(formatDate(fiveMinAgo)).toBe('5m ago');
  });

  it('shows hours ago', () => {
    const threeHoursAgo = Date.now() - 3 * 3_600_000;
    expect(formatDate(threeHoursAgo)).toBe('3h ago');
  });

  it('shows days ago', () => {
    const twoDaysAgo = Date.now() - 2 * 86_400_000;
    expect(formatDate(twoDaysAgo)).toBe('2d ago');
  });

  it('shows date for older timestamps', () => {
    const oldDate = Date.now() - 30 * 86_400_000;
    const result = formatDate(oldDate);
    // Should be a formatted date string, not relative
    expect(result).not.toContain('ago');
  });
});

describe('formatBytes', () => {
  it('formats bytes', () => {
    expect(formatBytes(500)).toBe('500 B');
  });

  it('formats kilobytes', () => {
    expect(formatBytes(2048)).toBe('2.0 KB');
  });

  it('formats megabytes', () => {
    expect(formatBytes(5 * 1024 * 1024)).toBe('5.0 MB');
  });
});

describe('truncate', () => {
  it('returns short strings unchanged', () => {
    expect(truncate('hello', 10)).toBe('hello');
  });

  it('truncates long strings with ellipsis', () => {
    expect(truncate('hello world foo bar', 10)).toBe('hello worl…');
  });

  it('handles exact length', () => {
    expect(truncate('hello', 5)).toBe('hello');
  });
});

describe('debounce', () => {
  it('delays execution', async () => {
    let count = 0;
    const fn = debounce(() => count++, 50);
    fn();
    fn();
    fn();
    expect(count).toBe(0);
    await new Promise((r) => setTimeout(r, 100));
    expect(count).toBe(1);
  });
});

describe('cn', () => {
  it('joins class names', () => {
    expect(cn('a', 'b', 'c')).toBe('a b c');
  });

  it('filters falsy values', () => {
    expect(cn('a', false, null, undefined, 'b')).toBe('a b');
  });

  it('returns empty string for no classes', () => {
    expect(cn(false, null)).toBe('');
  });
});
