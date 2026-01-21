import { useState, useEffect, useCallback } from 'react';

/**
 * Theme type representing the available themes.
 */
export type Theme = 'dark' | 'light';

/**
 * localStorage key for persisting theme preference.
 */
const THEME_STORAGE_KEY = 'nwwatch-theme';

/**
 * Default theme when no preference is stored.
 */
const DEFAULT_THEME: Theme = 'dark';

/**
 * Return type for useTheme hook.
 */
export interface UseThemeResult {
  theme: Theme;
  toggleTheme: () => void;
}

/**
 * Validates if a value is a valid Theme.
 */
function isValidTheme(value: string | null): value is Theme {
  return value === 'dark' || value === 'light';
}

/**
 * Gets the initial theme from localStorage or returns default.
 */
function getInitialTheme(): Theme {
  // Only access localStorage in browser environment
  if (typeof window === 'undefined') {
    return DEFAULT_THEME;
  }

  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (isValidTheme(stored)) {
      return stored;
    }
  } catch (error) {
    // localStorage may be unavailable (e.g., private browsing)
    console.warn('Failed to read theme from localStorage:', error);
  }

  return DEFAULT_THEME;
}

/**
 * Custom hook for theme state management and persistence.
 * Handles reading from and writing to localStorage, and syncing with DOM.
 *
 * @returns Object containing current theme and toggle function
 */
export function useTheme(): UseThemeResult {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  /**
   * Toggles between dark and light themes.
   */
  const toggleTheme = useCallback(() => {
    setTheme((currentTheme) => (currentTheme === 'dark' ? 'light' : 'dark'));
  }, []);

  /**
   * Sync theme to localStorage and DOM whenever it changes.
   */
  useEffect(() => {
    // Update DOM attribute for CSS variable switching
    document.documentElement.dataset.theme = theme;

    // Persist to localStorage
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error);
    }
  }, [theme]);

  /**
   * Set initial DOM attribute on mount.
   */
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { theme, toggleTheme };
}

export default useTheme;
