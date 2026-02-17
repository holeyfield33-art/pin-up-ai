import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { WelcomeWizard } from '../components/WelcomeWizard';

describe('WelcomeWizard', () => {
  const onComplete = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders first step', () => {
    render(<WelcomeWizard onComplete={onComplete} />);
    expect(screen.getByText(/Welcome to Pin-Up AI/i)).toBeInTheDocument();
  });

  it('shows Skip button', () => {
    render(<WelcomeWizard onComplete={onComplete} />);
    expect(screen.getByText('Skip')).toBeInTheDocument();
  });

  it('shows Next button on first step', () => {
    render(<WelcomeWizard onComplete={onComplete} />);
    expect(screen.getByText('Next')).toBeInTheDocument();
  });

  it('advances to next step on Next click', () => {
    render(<WelcomeWizard onComplete={onComplete} />);
    fireEvent.click(screen.getByText('Next'));
    // Step 2 should be visible — look for pin-related content
    expect(screen.queryByText(/Welcome to Pin-Up AI/i)).not.toBeInTheDocument();
  });

  it('calls onComplete when Skip is clicked', () => {
    render(<WelcomeWizard onComplete={onComplete} />);
    fireEvent.click(screen.getByText('Skip'));
    expect(onComplete).toHaveBeenCalledOnce();
  });

  it('shows progress dots', () => {
    const { container } = render(<WelcomeWizard onComplete={onComplete} />);
    // 4 dots rendered as small div elements in the progress bar
    const dots = container.querySelectorAll('.rounded-full');
    expect(dots.length).toBe(4);
  });

  it('shows Get Started on last step', () => {
    render(<WelcomeWizard onComplete={onComplete} />);
    // Navigate to last step
    fireEvent.click(screen.getByText('Next'));
    fireEvent.click(screen.getByText('Next'));
    fireEvent.click(screen.getByText('Next'));
    expect(screen.getByText('Get Started')).toBeInTheDocument();
  });

  it('calls onComplete on Get Started click', () => {
    render(<WelcomeWizard onComplete={onComplete} />);
    // Navigate to last step
    fireEvent.click(screen.getByText('Next'));
    fireEvent.click(screen.getByText('Next'));
    fireEvent.click(screen.getByText('Next'));
    fireEvent.click(screen.getByText('Get Started'));
    expect(onComplete).toHaveBeenCalledOnce();
  });
});
