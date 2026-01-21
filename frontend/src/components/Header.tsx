import React from 'react';
import { Theme } from '../hooks/useTheme';
import { ThemeToggle } from './ThemeToggle';

/**
 * Props for the Header component.
 */
export interface HeaderProps {
  theme: Theme;
  onToggleTheme: () => void;
}

/**
 * Header component displaying the application title and theme toggle.
 * Provides consistent navigation header across the application.
 */
export const Header: React.FC<HeaderProps> = ({ theme, onToggleTheme }) => {
  const headerStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 24px',
    backgroundColor: 'var(--bg-secondary)',
    borderBottom: '1px solid var(--border-color)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  };

  const titleStyles: React.CSSProperties = {
    margin: 0,
    fontSize: '24px',
    fontWeight: 600,
    color: 'var(--text-primary)',
  };

  return (
    <header data-testid="header" style={headerStyles}>
      <h1 style={titleStyles}>nWave Step Viewer</h1>
      <ThemeToggle theme={theme} onToggle={onToggleTheme} />
    </header>
  );
};

export default Header;
