# Frontend Development Guide

## 📁 Project Structure

```
src/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── Documentation.tsx  # API documentation component
│   ├── GenerationInterface.tsx
│   ├── HeroSection.tsx
│   ├── Navigation.tsx
│   ├── ResultsDisplay.tsx
│   └── DocumentUpload.tsx
├── lib/                   # Utilities and shared code
│   ├── constants.ts       # Application constants
│   ├── hooks.ts           # Custom React hooks
│   ├── utils.ts           # Utility functions
│   └── index.ts           # Barrel exports
├── services/              # API and external services
│   └── api.ts             # API client and functions
└── types/                 # TypeScript type definitions
    └── index.ts           # Type definitions
```

## 🎯 Best Practices Implemented

### **1. Constants Management**
- All magic numbers and configuration values are centralized in `lib/constants.ts`
- Environment-specific values use `process.env` with fallbacks
- Constants are typed with `as const` for type safety

```typescript
import { UI_CONSTANTS, API_CONFIG } from '@/lib/constants';

// ✅ Good - using constants
setTimeout(() => setCopied(null), UI_CONSTANTS.COPY_FEEDBACK_DURATION);

// ❌ Bad - magic numbers
setTimeout(() => setCopied(null), 2000);
```

### **2. Custom Hooks**
- Reusable logic is extracted into custom hooks
- Hooks follow the `useXxx` naming convention
- Each hook has a single responsibility

```typescript
import { useCopyToClipboard } from '@/lib/hooks';

function MyComponent() {
  const { copyToClipboard, isCopied } = useCopyToClipboard();
  
  return (
    <button onClick={() => copyToClipboard('text', 'id')}>
      {isCopied('id') ? 'Copied!' : 'Copy'}
    </button>
  );
}
```

### **3. Utility Functions**
- Common operations are abstracted into utility functions
- Functions are pure and side-effect free where possible
- Comprehensive type safety

```typescript
import { formatFileSize, formatDuration } from '@/lib/utils';

const fileInfo = formatFileSize(1024 * 1024); // "1 MB"
const duration = formatDuration(125); // "2m 5s"
```

### **4. Type Safety**
- All functions have proper TypeScript types
- Generic types are used where appropriate
- No `any` types (use `unknown` when necessary)

### **5. Error Handling**
- Consistent error handling patterns
- Graceful degradation for non-critical features
- Development-only logging for debugging

```typescript
const logger = {
  info: (message: string, data?: unknown) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`ℹ️ ${message}`, data || '');
    }
  },
};
```

### **6. Import Organization**
- Use barrel exports from `lib/index.ts`
- Group imports by type (React, external libraries, internal)
- Use absolute imports with `@/` prefix

```typescript
// ✅ Good import organization
import { useState, useCallback } from 'react';
import { Download, Copy } from 'lucide-react';
import { useCopyToClipboard, formatFileSize } from '@/lib';
import { GenerationResults } from '@/types';
```

## 🔧 Development Guidelines

### **Adding New Components**
1. Create component in `src/components/`
2. Export from component file using default export
3. Add proper TypeScript props interface
4. Use custom hooks for reusable logic

### **Adding New Utilities**
1. Add function to appropriate section in `src/lib/utils.ts`
2. Include JSDoc comments
3. Add proper TypeScript types
4. Export from `src/lib/index.ts` if commonly used

### **Adding New Constants**
1. Add to appropriate section in `src/lib/constants.ts`
2. Use `as const` for type safety
3. Group related constants together

### **Adding New Hooks**
1. Create in `src/lib/hooks.ts`
2. Follow `useXxx` naming convention
3. Include proper return type interface
4. Use `useCallback` for function references

## 🎨 Styling Guidelines

### **Class Name Utility**
Use the `cn()` utility for conditional classes:

```typescript
import { cn } from '@/lib/utils';

<button 
  className={cn(
    'base-styles',
    isActive && 'active-styles',
    isDisabled && 'disabled-styles'
  )}
>
```

### **Theme Colors**
Use theme constants for consistent colors:

```typescript
import { THEME_COLORS } from '@/lib/constants';

<div style={{ backgroundColor: THEME_COLORS.PRIMARY }}>
```

## 📦 Dependencies

### **Core Dependencies**
- Next.js 15.4.2
- React 19.1.0
- TypeScript
- Tailwind CSS

### **UI Dependencies**
- Lucide React (icons)
- Radix UI components

### **Development Dependencies**
- ESLint
- TypeScript compiler

## 🚀 Performance Considerations

### **Component Optimization**
- Use `useCallback` for function references passed to children
- Use `useMemo` for expensive calculations
- Implement proper dependency arrays

### **Bundle Optimization**
- Tree-shaking friendly exports
- Lazy loading for large components
- Minimal external dependencies

## 🧪 Testing Guidelines

### **Component Testing**
- Test user interactions
- Test props and state changes
- Mock external dependencies

### **Utility Testing**
- Test edge cases
- Test type safety
- Test error conditions

## 📝 Code Review Checklist

- [ ] No magic numbers (use constants)
- [ ] Proper TypeScript types
- [ ] Consistent naming conventions
- [ ] No console.log in production code
- [ ] Proper error handling
- [ ] Reusable logic extracted to hooks/utils
- [ ] Clean import organization
- [ ] Proper component structure 