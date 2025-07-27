# Source Code (src/)

Clean Architecture implementation with domain-driven design principles.

## Structure

- **`domain/`** - Core business logic and entities (pure business rules)
- **`application/`** - Use cases and application services (orchestration layer) 
- **`infrastructure/`** - External concerns (databases, APIs, repositories)
- **`presentation/`** - User interfaces and visualization components

## Dependency Flow

```
presentation/ → application/ → domain/
                     ↓
             infrastructure/
```

Infrastructure and presentation depend on domain abstractions, not concrete implementations.