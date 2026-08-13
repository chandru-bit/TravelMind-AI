# System Design & Architecture Document — TravelMind AI

## 1. Problem Statement & High-Level Overview

TravelMind AI is an AI-powered travel intelligence platform that solves the complexity and fragmentation of modern trip planning by combining predictive price analytics, weighted destination recommendation algorithms, day-by-day itinerary timeline generation, and budget optimization.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    User[Client / Browser Frontend] -->|HTTP / REST| Nginx[NGINX Load Balancer]
    Nginx -->|Proxy Forwarding| Gateway[API Gateway :8000]
    
    subgraph Microservices Cluster
        Gateway -->|/api/auth & /api/users| UserService[User Service :8001]
        Gateway -->|/api/trips| TripService[Trip Service :8002]
        Gateway -->|/api/recommendations| RecService[Recommendation Service :8003]
        Gateway -->|/api/ai| AIService[AI Service :8004]
        Gateway -->|/api/predictions| PredService[Prediction Service :8005]
        Gateway -->|/api/notifications| NotifService[Notification Service :8006]
    end

    subgraph Data & Caching Layer
        UserService --> PostgreSQL[(PostgreSQL / SQLite DB)]
        TripService --> PostgreSQL
        RecService --> PostgreSQL
        RecService --> Redis[(Redis Cache)]
        PredService --> PostgreSQL
        NotifService --> PostgreSQL
    end

    subgraph Intelligence Layer
        AIService -->|HTTP / Fallback| LLM[LLM API / Rule Engine]
        PredService -->|Scikit-Learn| ML[Linear Regression ML Model]
    end
```

---

## 3. Microservices Architecture & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Nginx as NGINX Load Balancer
    participant Gateway as API Gateway
    participant RecService as Recommendation Service
    participant Redis as Redis Cache
    participant DB as PostgreSQL DB

    User->>Nginx: POST /api/recommendations
    Nginx->>Gateway: Forward Request + X-Request-ID
    Gateway->>Gateway: Rate Limit Check (Redis)
    Gateway->>RecService: Route Request to :8003
    RecService->>Redis: Check Cache (Key: rec:budget:style)
    alt Cache Hit
        Redis-->>RecService: Return Cached Recommendations
    else Cache Miss
        RecService->>DB: Query Destinations & Weather Data
        DB-->>RecService: Return Destination Datasets
        RecService->>RecService: Execute Multi-Criteria Weighted Scoring Formula
        RecService->>Redis: Store Results (TTL: 300s)
    end
    RecService-->>Gateway: Return 200 OK + Scored Destinations
    Gateway-->>Nginx: Return Response
    Nginx-->>User: Display Recommendations Cards
```

---

## 4. Database ER Diagram

```mermaid
erDiagram
    USERS ||--o| USER_PREFERENCES : has
    USERS ||--o{ TRIPS : creates
    USERS ||--o{ FEEDBACK : submits
    USERS ||--o{ NOTIFICATIONS : receives
    TRIPS ||--o| ITINERARIES : generates
    ITINERARIES ||--o{ ITINERARY_ITEMS : contains

    USERS {
        string id PK
        string name
        string email
        string password_hash
        datetime created_at
    }

    USER_PREFERENCES {
        string id PK
        string user_id FK
        string home_location
        float budget
        string travel_style
        text interests_json
    }

    DESTINATIONS {
        string id PK
        string name
        string state_country
        float avg_cost
        string best_season
        float popularity
    }

    TRIPS {
        string id PK
        string user_id FK
        string source
        string destination
        string start_date
        string end_date
        float budget
    }

    ITINERARIES {
        string id PK
        string trip_id FK
        string destination
        integer total_days
        boolean is_ai_generated
    }

    ITINERARY_ITEMS {
        string id PK
        string itinerary_id FK
        integer day_number
        string time
        string activity
        float estimated_cost
    }

    PRICE_HISTORY {
        string id PK
        string destination
        float hotel_price
        float transport_price
        float demand_score
        string season
    }
```

---

## 5. Recommendation Scoring Flow

```mermaid
graph LR
    A[User Preferences & Input] --> B[Recommendation Engine]
    C[Destination Dataset] --> B
    D[Live / Cached Weather] --> B

    subgraph Weighted Scoring Formula
        B --> B1[Budget Score x 0.25]
        B --> B2[Interest Score x 0.30]
        B --> B3[Weather Score x 0.15]
        B --> B4[Activity Score x 0.15]
        B --> B5[Distance Score x 0.15]
    end

    B1 --> F[Sum Final Score]
    B2 --> F
    B3 --> F
    B4 --> F
    B5 --> F

    F --> G[Sort & Rank Destinations]
    G --> H[Generate Match % & Reasons]
```

---

## 6. AI Itinerary & Fallback Flow

```mermaid
flowchart TD
    Req[AI Itinerary Request] --> CheckConfig{LLM_API_KEY Configured & DEMO_MODE=false?}
    CheckConfig -- Yes --> CallLLM[Invoke LLM API /chat/completions]
    CallLLM --> LLMSuccess{HTTP 200 OK?}
    LLMSuccess -- Yes --> ParseJSON[Parse Structured Itinerary JSON]
    ParseJSON --> ReturnAI[Return AI-Generated Itinerary]

    CheckConfig -- No --> Fallback[Trigger Deterministic Rule-Based Generator]
    LLMSuccess -- Fail / Timeout --> Fallback
    Fallback --> AddBanner[Attach 'AI personalization unavailable' Banner]
    AddBanner --> ReturnStandard[Return Standard Itinerary]
```

---

## 7. Machine Learning Price Prediction Pipeline

```mermaid
graph TD
    HistoricalData[Historical Price History DB Records] --> DataPrep[Data Cleaning & Feature Engineering]
    DataPrep --> Features[Features: Hotel Price, Transport Price, Demand Score, Season Factor]
    Features --> Train[Scikit-Learn Linear Regression Model Fit]
    Train --> Evaluate[Model Metrics: MAE & R2 Score Calculation]
    Evaluate --> Inference[POST /predictions/price]
    Inference --> Output[Current Price vs Predicted Price, Trend, Booking Recommendation]
```

---

## 8. Error Handling & Circuit Breaker Flow

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: Failures >= 3
    Open --> HalfOpen: Cooldown Timeout (10s)
    HalfOpen --> Closed: Request Succeeds
    HalfOpen --> Open: Request Fails
    Open --> Fallback: Short-Circuit & Return Fallback Response
```

---

## 9. Nginx Load Balancing Diagram

```mermaid
graph TD
    Client[Client Browser] -->|HTTP Request| Nginx[NGINX Reverse Proxy & Load Balancer]
    subgraph Gateway Upstream Cluster
        Nginx -->|Round Robin 1| GW1[API Gateway Instance 1]
        Nginx -->|Round Robin 2| GW2[API Gateway Instance 2]
    end
```

---

## 10. Key System Design Concepts Implemented

1. **Client-Server Architecture**: Separates React Vite single page application from FastAPI backend services.
2. **RESTful Microservices**: Decoupled domain microservices (`user-service`, `trip-service`, `recommendation-service`, `prediction-service`, `ai-service`, `notification-service`).
3. **API Gateway**: Single entry point handling request routing, rate limiting, and request ID propagation.
4. **Nginx Load Balancer**: Reverse proxy routing requests with round-robin load balancing.
5. **Layered Repository Pattern**: Clean separation into Route Handlers -> Service Logic -> Repository Layer -> SQLAlchemy ORM.
6. **Stateless JWT Authentication**: Signed tokens containing user payload verified across all instances without shared session state.
7. **Redis Caching with Fallback**: Accelerated cache hits with graceful in-memory degradation if Redis is unreachable.
8. **Predictive Analytics (ML)**: Supervised Linear Regression predicting travel costs.
9. **Generative AI & Fallback**: Configurable LLM API integration with 100% reliable rule-based fallback generation.
10. **Resilience & Request Tracing**: Structured JSON logging embedding `X-Request-ID` across services, exponential backoff retries, and circuit breakers.
