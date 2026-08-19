import js from '@eslint/js'
import importX from 'eslint-plugin-import-x'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import n from 'eslint-plugin-n'
import promise from 'eslint-plugin-promise'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import jest from 'eslint-plugin-jest'
import tseslint from 'typescript-eslint'
import globals from 'globals'

export default [
  js.configs.recommended,
  importX.configs['flat/recommended'],

  {
    plugins: tseslint.configs.recommended[0].plugins,
  },
  {
    files: ['**/*.ts', '**/*.tsx', '**/*.mts', '**/*.cts'],
    ...tseslint.configs.recommended[1],
  },
  {
    files: ['**/*.ts', '**/*.tsx', '**/*.mts', '**/*.cts'],
    languageOptions: {
      parser: tseslint.configs.recommended[0].languageOptions.parser,
    },
    ...tseslint.configs.recommended[2],
  },

  {
    plugins: {
      'jsx-a11y': jsxA11y,
    },
    rules: jsxA11y.configs.recommended.rules,
  },

  n.configs['flat/recommended'],
  promise.configs['flat/recommended'],
  react.configs.flat.recommended,
  reactHooks.configs.flat.recommended,

  {
    files: ['**/*.jest.js', '**/*.jest.jsx', '**/*.jest.ts', '**/*.jest.tsx'],
    ...jest.configs['flat/recommended'],
  },

  {
    files: ['**/*.js', '**/*.jsx'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.commonjs,
        ...globals.es2021,
        ...globals.jquery,
      },
    },
    settings: {
      react: {
        version: 'detect',
      },
      'import-x/core-modules': [
        'django',
        '@uppy/core',
        '@uppy/dashboard',
        '@uppy/image-editor',
        '@uppy/compressor',
        '@uppy/core/css/style.min.css',
        '@uppy/dashboard/css/style.min.css',
        '@uppy/image-editor/css/style.min.css',
      ],
      'import-x/resolver': {
        node: {
          extensions: ['.js', '.jsx', '.ts', '.tsx', '.css'],
          moduleDirectory: ['node_modules', 'node_modules/.pnpm'],
        },
      },
    },
    rules: {
      'jsx-quotes': ['error', 'prefer-double'],
      'jsx-a11y/no-onchange': 'off',
      'react/prop-types': 'off',
      'n/no-missing-require': 'off',
      'n/no-unsupported-features/es-syntax': 'off',
      'n/no-unsupported-features/node-builtins': 'off',
      'n/no-missing-import': 'off',
      'n/no-unpublished-import': 'off',
      'n/no-extraneous-import': 'off',
      'import-x/named': 'off',
      'no-unused-vars': 'warn',
      'jest/valid-title': 'off',
      'jest/no-identical-title': 'off',
      'jest/no-export': 'off',
      'react-hooks/refs': 'off',
      'promise/catch-or-return': 'warn',
      'promise/always-return': 'warn',
    },
  },

  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.commonjs,
        ...globals.es2021,
        ...globals.jquery,
      },
    },
    settings: {
      react: {
        version: 'detect',
      },
      'import-x/core-modules': [
        'django',
        'adhocracy4',
        '@uppy/core',
        '@uppy/dashboard',
        '@uppy/image-editor',
        '@uppy/compressor',
        '@uppy/core/css/style.min.css',
        '@uppy/dashboard/css/style.min.css',
        '@uppy/image-editor/css/style.min.css',
      ],
      'import-x/resolver': {
        node: {
          extensions: ['.js', '.jsx', '.ts', '.tsx', '.css'],
          moduleDirectory: ['node_modules', 'node_modules/.pnpm'],
        },
      },
    },
    rules: {
      'jsx-quotes': ['error', 'prefer-double'],
      'jsx-a11y/no-onchange': 'off',
      'react/prop-types': 'off',
      'n/no-missing-require': 'off',
      'n/no-unsupported-features/es-syntax': 'off',
      'n/no-unsupported-features/node-builtins': 'off',
      'n/no-missing-import': 'off',
      'n/no-unpublished-import': 'off',
      'n/no-extraneous-import': 'off',
      'import-x/named': 'off',
      'no-unused-vars': 'warn',
      'jest/valid-title': 'off',
      'jest/no-identical-title': 'off',
      'jest/no-export': 'off',
      'react-hooks/refs': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      'promise/catch-or-return': 'warn',
      'promise/always-return': 'warn',
    },
  },

  {
    files: ['**/*.jest.js', '**/*.jest.jsx', '**/*.jest.ts', '**/*.jest.tsx', '**/__mocks__/*.js'],
    languageOptions: {
      globals: {
        ...globals.jest,
      },
    },
  },

  {
    ignores: ['node_modules/', 'venv/', '**/static/'],
  },
]
