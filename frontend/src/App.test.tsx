import { render, screen } from '@testing-library/react';

import App from './App';

describe('App component', () => {
  it('renders the application title', () => {
    render(<App />);
    const titleElement = screen.getByText(/NeverEatAlone/i);
    expect(titleElement).toBeInTheDocument();
  });

  it('renders the application description', () => {
    render(<App />);
    const descriptionElement = screen.getByText(/Connect with people/i);
    expect(descriptionElement).toBeInTheDocument();
  });
});
