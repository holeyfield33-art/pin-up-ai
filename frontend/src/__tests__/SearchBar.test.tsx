import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchBar } from '../components/SearchBar';

describe('SearchBar', () => {
  const onChange = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders with placeholder', () => {
    render(<SearchBar value="" onChange={onChange} />);
    expect(screen.getByPlaceholderText(/Search snippets/)).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    render(<SearchBar value="" onChange={onChange} placeholder="Find code…" />);
    expect(screen.getByPlaceholderText('Find code…')).toBeInTheDocument();
  });

  it('displays current value', () => {
    render(<SearchBar value="react hooks" onChange={onChange} />);
    expect(screen.getByDisplayValue('react hooks')).toBeInTheDocument();
  });

  it('shows clear button when value present', () => {
    render(<SearchBar value="test" onChange={onChange} />);
    expect(screen.getByLabelText('Clear search')).toBeInTheDocument();
  });

  it('hides clear button when empty', () => {
    render(<SearchBar value="" onChange={onChange} />);
    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();
  });

  it('clears value and calls onChange on clear click', () => {
    render(<SearchBar value="test" onChange={onChange} />);
    fireEvent.click(screen.getByLabelText('Clear search'));
    expect(onChange).toHaveBeenCalledWith('');
  });

  it('has search input with correct aria-label', () => {
    render(<SearchBar value="" onChange={onChange} />);
    expect(screen.getByLabelText('Search snippets')).toBeInTheDocument();
  });
});
