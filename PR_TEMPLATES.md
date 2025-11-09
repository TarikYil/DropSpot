# Pull Request Templates

## feature/auth-service → main

### Title
feat: Add Authentication Service with JWT and Role Management

### Description

This PR introduces the complete authentication service for DropSpot platform.

#### Features Added
- User registration and login endpoints
- JWT access token and refresh token management
- Role-based access control (Admin, User, Superuser)
- Argon2 password hashing for secure password storage
- Token refresh mechanism
- Automatic default admin user creation on startup
- Role and permission management endpoints

#### Technical Details
- FastAPI-based REST API
- PostgreSQL database with SQLAlchemy ORM
- JWT token authentication
- Environment-based configuration
- Docker containerization support

#### Files Changed
- `auth_service/` - Complete authentication service implementation
- `docker-compose.yml` - Auth service configuration
- `init-db/` - Database initialization scripts

#### Testing
- Unit tests for auth utilities
- Integration tests for authentication endpoints
- Role management tests

#### Breaking Changes
None

#### Migration Notes
- Default admin user is automatically created on first startup
- Credentials: admin/admin123 (should be changed in production)

---

## feature/backend-service → main

### Title
feat: Add Backend Service with Drop Management, Waitlist, and Claim System

### Description

This PR introduces the core backend service handling drop management, waitlist operations, and claim processing.

#### Features Added
- Drop CRUD operations (Admin only)
- Waitlist management with idempotent join/leave operations
- Claim system with location-based verification
- Transaction and pessimistic locking for race condition prevention
- Database unique constraints for data integrity
- Seed-based claim code generation
- Alembic database migrations
- Automatic migration execution on startup

#### Technical Details
- Pessimistic locking using `with_for_update()` for critical operations
- Unique constraints on (drop_id, user_id) for waitlist and claim tables
- Atomic transactions for stock management
- Location-based distance calculation for claim verification
- Seed-based system for reproducible claim codes

#### Files Changed
- `backend/` - Complete backend service implementation
- `backend/alembic/` - Database migration scripts
- `docker-compose.yml` - Backend service configuration

#### Key Endpoints
- `POST /api/drops/{drop_id}/join` - Join waitlist (case format)
- `POST /api/drops/{drop_id}/leave` - Leave waitlist (case format)
- `POST /api/drops/{drop_id}/claim` - Create claim (case format)
- `POST /api/admin/drops` - Create drop (Admin)
- `PUT /api/admin/drops/{drop_id}` - Update drop (Admin)
- `DELETE /api/admin/drops/{drop_id}` - Delete drop (Admin)

#### Testing
- Integration tests for case format endpoints
- Idempotency tests
- Race condition tests
- Stock management tests

#### Breaking Changes
None

#### Migration Notes
- Database migrations are automatically applied on startup
- Unique constraints are added to waitlist and claim tables

---

## feature/frontend → main

### Title
feat: Add React Frontend Application with Modern UI

### Description

This PR introduces the complete frontend application built with React, Vite, and Tailwind CSS.

#### Features Added
- Modern and responsive user interface
- User authentication (Sign in / Sign up)
- Drop listing page with search and filtering
- Drop detail page with waitlist and claim functionality
- Admin panel for drop management
- Super admin panel for user and role management
- Settings page for user profile management
- AI chatbot widget (bottom right corner)
- Protected routes with authentication
- Toast notifications for user feedback
- Loading states and error handling

#### Technical Details
- React 18 with functional components and hooks
- Vite for fast development and optimized builds
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication
- Context API for state management
- Component-based architecture

#### Files Changed
- `frontend/` - Complete frontend application
- `docker-compose.yml` - Frontend service configuration

#### Key Components
- Home page with drop listing
- Drop detail page
- Login and registration pages
- Admin panel
- Super admin panel
- Settings page
- Chatbot widget

#### Testing
- Component tests for Home and DropDetail
- API mock tests
- User interaction tests

#### Breaking Changes
None

---

## feature/ai-service → main

### Title
feat: Add AI Service with Gemini-based RAG Chatbot

### Description

This PR introduces an AI-powered chatbot service using Google Gemini Pro with RAG (Retrieval Augmented Generation) capabilities.

#### Features Added
- Gemini Pro AI integration
- RAG system for context-aware responses
- Real-time data retrieval from backend service
- User-specific information with token authentication
- Chat history support for contextual conversations
- Platform knowledge base (drops, waitlist, claims)

#### Technical Details
- FastAPI-based service
- Google Gemini Pro API integration
- RAG pattern implementation
- Context-aware prompt engineering
- Async API calls for better performance

#### Files Changed
- `ai_service/` - Complete AI service implementation
- `docker-compose.yml` - AI service configuration
- `.env.example` - Environment variable template

#### Key Endpoints
- `POST /api/chat/ask` - Ask question to AI
- `GET /health` - Health check endpoint

#### Configuration
- Environment variables for API key and model settings
- Configurable RAG parameters (context length, chat history)
- Safety settings for content filtering

#### Testing
- AI response quality tests
- RAG context retrieval tests
- Error handling tests

#### Breaking Changes
None

#### Migration Notes
- Requires GEMINI_API_KEY environment variable
- See `.env.example` for configuration template

---

## feature/test-service → main

### Title
feat: Add Comprehensive Test Suite with Unit and Integration Tests

### Description

This PR introduces a complete test infrastructure for the DropSpot platform.

#### Features Added
- Unit tests for auth utilities and models
- Integration tests for API endpoints
- Frontend component tests
- Test fixtures and helpers
- Docker-based test environment
- Test coverage reporting
- Pytest configuration with markers

#### Technical Details
- Pytest framework for Python tests
- Vitest for frontend component tests
- Separate test databases for isolation
- Docker Compose test profile
- Test markers for categorization (unit, integration, auth, backend)

#### Files Changed
- `tests/` - Complete test suite
- `docker-compose.yml` - Test service configuration
- `frontend/src/__tests__/` - Frontend component tests

#### Test Coverage
- Auth service: Unit and integration tests
- Backend service: Case format endpoints, idempotency tests
- Frontend: Component tests for Home and DropDetail

#### Test Execution
```bash
# Backend tests
docker-compose --profile test run --rm test_service pytest tests/ -v

# Frontend tests
cd frontend && npm test
```

#### Breaking Changes
None

---

## feature/database-migrations → main

### Title
feat: Add Database Migration System with Alembic

### Description

This PR introduces database migration management using Alembic for schema versioning.

#### Features Added
- Alembic migration system
- Database initialization scripts
- Unique constraints for waitlist and claim tables
- Automatic migration execution on startup
- Migration rollback support

#### Technical Details
- Alembic for database version control
- PostgreSQL-specific migrations
- Unique constraints: (drop_id, user_id) for waitlist and claim
- Automatic migration on backend service startup

#### Files Changed
- `backend/alembic/` - Alembic configuration and migrations
- `init-db/` - Database initialization scripts
- `backend/main.py` - Automatic migration execution

#### Migrations Included
- Add unique constraints for waitlist (drop_id, user_id)
- Add unique constraints for claim (drop_id, user_id)

#### Breaking Changes
None

#### Migration Notes
- Migrations are automatically applied on backend service startup
- Manual migration: `alembic upgrade head`
- Rollback: `alembic downgrade -1`

---

## General PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are added/updated and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or clearly documented)
- [ ] Environment variables are documented
- [ ] Docker configuration is updated if needed
- [ ] README is updated for the service

