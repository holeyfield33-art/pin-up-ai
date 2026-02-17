import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Toast } from '../components/Toast';

describe('Toast', () => {
  const onClose = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders success toast', () => {
    render(<Toast message="Saved!" type="success" onClose={onClose} />);
    expect(screen.getByText('Saved!')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveClass('bg-green-50');
  });

  it('renders error toast', () => {
    render(<Toast message="Something failed" type="error" onClose={onClose} />);
    expect(screen.getByText('Something failed')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveClass('bg-red-50');
  });

  it('renders warning toast', () => {
    render(<Toast message="Watch out" type="warning" onClose={onClose} />);
    expect(screen.getByText('Watch out')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveClass('bg-yellow-50');
  });

  it('renders info toast', () => {
    render(<Toast message="FYI" type="info" onClose={onClose} />);
    expect(screen.getByText('FYI')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveClass('bg-blue-50');
  });

  it('calls onClose when dismiss button clicked', () => {
    render(<Toast message="Close me" type="success" onClose={onClose} />);
    fireEvent.click(screen.getByLabelText('Dismiss'));
    expect(onClose).toHaveBeenCalledOnce();
  });
});
