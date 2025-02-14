import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});

test('error handling verification', () => {
  // Intentionally failing test to verify CI error handling
  expect(true).toBe(false);
});
