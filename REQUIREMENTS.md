# TravelMind AI — Functional & Non-Functional Requirements Matrix

This document provides complete traceability for all Functional Requirements (FR-01 to FR-16) and Non-Functional Requirements (NFR-01 to NFR-10) for **TravelMind AI**.

---

## 1. Functional Requirements Matrix

| Req ID | Requirement Title | Description & Scope | Priority | Related Module | System Design Concept | Implementation Status |
|---|---|---|---|---|---|---|
| **FR-01** | User Registration | Register user via Name, Email, Password. Validates required fields, email format, password strength, duplicate email. Passwords securely hashed. | HIGH | `user-service` | Password Hashing (PBKDF2/SHA256), Validation | **COMPLETED** |
| **FR-02** | User Login | Authenticate via Email & Password using JWT. Returns access_token and user payload. 401 Unauthorized on invalid credentials. | HIGH | `user-service` | Stateless JWT Authentication, RBAC | **COMPLETED** |
| **FR-03** | User Profile | View & update user profile information and travel preferences via `/users/me` and `/users/me/preferences`. | MEDIUM | `user-service` | Repository Pattern, Layered API | **COMPLETED** |
| **FR-04** | User Onboarding | Collect home location, budget, travel style (Budget/Balanced/Premium/Luxury), interests (Beach, Mountains, Adventure, etc.), food preferences, and traveler count. | HIGH | `user-service`, `frontend` | Preference Store, Personalization | **COMPLETED** |
| **FR-05** | Trip Planning | Create, view, update, and delete trip plans (Source, Destination, Dates, Budget, Traveler count, Interests). | HIGH | `trip-service` | Relational Data Modeling, CRUD | **COMPLETED** |
| **FR-06** | Destination Recommendation | Deterministic scoring engine formula: `Score = Budget*0.25 + Interest*0.30 + Weather*0.15 + Activity*0.15 + Distance*0.15`. Returns match %, cost, reasons. | CRITICAL | `recommendation-service` | Multi-Criteria Decision Analysis | **COMPLETED** |
| **FR-07** | Weather Integration | External weather integration with Redis caching and demo weather fallback. Weather failures must not crash the app. | MEDIUM | `recommendation-service`, `shared/cache` | Graceful Degradation, Fallback | **COMPLETED** |
| **FR-08** | ML Price Prediction | Scikit-Learn Linear Regression model predicting travel prices based on historical hotel, transport, demand, and season metrics. | CRITICAL | `prediction-service` | Predictive Analytics, Supervised ML | **COMPLETED** |
| **FR-09** | AI Service | Dedicated AI Service generating personalized day-by-day itineraries and recommendation explanations using LLM APIs. | HIGH | `ai-service` | Generative AI Integration | **COMPLETED** |
| **FR-10** | AI Fallback | Deterministic rule-based fallback itinerary generator when LLM API is unavailable, explicitly stating `"AI personalization unavailable — showing standard itinerary."` | HIGH | `ai-service` | Fault Tolerance, Fallback | **COMPLETED** |
| **FR-11** | Itinerary Timeline | Generate & display interactive day-by-day activity timelines. Supports activity item add, edit, delete, and reorder. | HIGH | `trip-service`, `frontend` | Interactive UI Timeline, CRUD | **COMPLETED** |
| **FR-12** | Budget Optimizer | Calculate and visualize category allocations (Transport, Accommodation, Food, Activities, Shopping, Emergency). Over-budget warning & suggestions. | HIGH | `frontend` | Financial Optimization | **COMPLETED** |
| **FR-13** | Booking Recommendations | Display simulated flight, hotel, and activity recommendation cards. | MEDIUM | `frontend` | E-Commerce Integration (Simulated) | **COMPLETED** |
| **FR-14** | Saved Trips | Save, view, update, and delete trips. | MEDIUM | `trip-service` | Relational Storage | **COMPLETED** |
| **FR-15** | Feedback System | Collect user rating, comment, and helpfulness metrics stored in PostgreSQL to refine travel match scoring. | MEDIUM | `recommendation-service` | Feedback Loop, Rating Engine | **COMPLETED** |
| **FR-16** | Dashboard | Centralized travel intelligence dashboard displaying welcome metrics, recommendations, upcoming trips, price trends, and weather status. | HIGH | `frontend` | Dashboard Visualization | **COMPLETED** |

---

## 2. Non-Functional Requirements Matrix

| Req ID | NFR Category | Technical Target / Specification | Related Component | Implementation Status |
|---|---|---|---|---|
| **NFR-01** | Performance | Target <500ms normal API response and <200ms cached Redis response where practical. | `gateway`, `redis` | **COMPLETED** |
| **NFR-02** | Scalability | Microservice architecture supporting horizontal container replication (`docker compose scale`). | All Microservices | **COMPLETED** |
| **NFR-03** | Availability | Fault isolation: Failure of AI, ML, Weather, or Redis must not crash the core recommendation or trip system. | `resilience`, `fallback` | **COMPLETED** |
| **NFR-04** | Reliability | Centralized database transactions, connection pooling, and exponential backoff retry mechanisms. | `shared/resilience`, `shared/database` | **COMPLETED** |
| **NFR-05** | Security | JWT token authentication, PBKDF2 password hashing, CORS protection, input validation, zero plain-text secrets. | `shared/auth`, `gateway` | **COMPLETED** |
| **NFR-06** | Usability | Responsive dark-mode glassmorphism UI with loading skeletons, empty state placeholders, and error toasts. | `frontend` | **COMPLETED** |
| **NFR-07** | Maintainability | Layered architecture (API -> Service -> Repository Pattern -> SQLAlchemy ORM) with reusable shared components. | `services/*`, `shared/*` | **COMPLETED** |
| **NFR-08** | Observability | Structured JSON logging embedding `X-Request-ID` tracing across API Gateway and microservices. | `shared/logging` | **COMPLETED** |
| **NFR-09** | Data Integrity | PostgreSQL relational foreign key constraints, indexes, unique constraints, and schema validations. | `database/models.py` | **COMPLETED** |
| **NFR-10** | Deployability | Docker and Docker Compose containerization for single-command deployment (`docker compose up -d --build`). | `docker-compose.yml` | **COMPLETED** |
