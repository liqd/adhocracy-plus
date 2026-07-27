const config = {
  testEnvironment: 'jsdom',
  modulePaths: [
    '<rootDir>',
    '<rootDir>/apps/userdashboard/assets/js/a4_candy_userdashboard'
  ],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/__mocks__/styleMock.js',
    '\\.(gif|ttf|eot|svg)$': '<rootDir>/__mocks__/fileMock.js',
    '(django)': '<rootDir>/__mocks__/djangoMock.js',
    '^(\\.\\/ModerationFeedbackForm$|^\\.\\/ModerationFeedback$)': '<rootDir>/__mocks__/customComponentMock.js',
    '^(\\.\\/api$)': '<rootDir>/__mocks__/apiMock.js',
    '(adhocracy4)': '<rootDir>/__mocks__/a4Mock.js'
  },
  testMatch: [
    '**/*.jest.js',
    '**/*.jest.jsx'
  ],
  collectCoverage: true,
  collectCoverageFrom: [
    '**/*.jsx',
    '!**/coverage/**',
    '!**/node_modules/**',
    '!**/babel.config.js',
    '!**/jest.setup.js',
    '!**/chrome/**',
    '!**/site-packages/adhocracy4/**',
    '!static/**'
  ],
  testPathIgnorePatterns: [
    '/(.*/site-packages/adhocracy4/.*)/',
    '/(static/.*)/'
  ],
  transform: {
    '^.+\\.[t|j]sx?$': 'babel-jest'
  },
  transformIgnorePatterns: [
    // Transform all node_modules (both flat npm and pnpm virtual store)
    '[/\\\\]node_modules[/\\\\]\\.pnpm[/\\\\].+[/\\\\]node_modules[/\\\\](?!.+).+\\.(js|jsx|mjs|cjs|ts|tsx)$',
    '[/\\\\]node_modules[/\\\\](?!.+).+\\.(js|jsx|mjs|cjs|ts|tsx)$'
  ]
}

module.exports = config
