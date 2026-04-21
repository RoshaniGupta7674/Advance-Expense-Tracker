# Spendora: Advanced Financial AI System - Project Documentation

## 1. Project Overview, Architecture, and Methodologies

*   **Comprehensive Introduction and Core System Objectives:** 
    The Spendora Advanced Financial AI System is designed to revolutionize how individuals interact with their personal finance by providing a robust, highly intuitive, and intelligent tracking mechanism for daily economic activities. Our primary objective with this system is to bridge the gap between complex financial analysis and everyday usability, enabling users to seamlessly monitor their income streams, track miscellaneous expenses, and manage life savings all within a unified, meticulously crafted dashboard interface. By integrating cuttingedge artificial intelligence, the application is capable of not only recording transactions but also actively parsing receipt images utilizing standard Optical Character Recognition combined with deep learning large language models (specifically the Gemini API), transforming unstructured visual data into structured, actionable database entries. We aim to empower the end-user with immediate awareness of their fiscal health, mitigating the risk of inadvertent overspending through aggressive adherence to predefined budget limits. Furthermore, Spendora explicitly tackles the administrative burden of recursive utility and subscription costs by incorporating a smart reminder system, which inherently guarantees that bills are rolled over or marked paid appropriately, avoiding any late penalty fees while drastically simplifying the user’s monthly accounting obligations.

*   **Extensive System Scope and Feature Capabilities:** 
    The functional footprint of Spendora extends vastly beyond conventional data entry software, evolving into an omnipotent personal finance concierge. Functionally, it incorporates intelligent Voice Command operations that allow hands-free submission of financial logs, capturing tone and context to appropriately categorize either an expense or income entry dynamically. The system provides profound insights through its dynamically generated visual analytics, rendering pie charts, bar graphs, and localized historic data points that demonstrate trends securely over customized temporal periods—such as last week, previous month, or an entire fiscal year. Beyond mere tracking, the system aggressively enforces limits; when a user approaches eighty percent of their categorized budget, preemptive threshold alerts trigger, giving users a crucial buffer window to correct their spending trajectory. The integration of predictive mathematics also projects future month expenditures based on rolling historical averages, establishing an environment where predictive financial modeling is continuously available. With the inclusion of a rigorous savings vault concept, Spendora effectively isolates disposable wealth from invested/saved wealth, creating a transparent, accurate representation of a person's net liquidity at any given second, ultimately cultivating superior financial habits and disciplined wealth generation strategies over their lifetime.

*   **Robust Technological Stack and Foundational Architecture:** 
    The application rests on a highly scalable, Model-View-Template (MVT) architectural pattern inherently provided by the Django web framework, which allows for exceptionally secure, rapid, and maintainable product development utilizing Python. The backend relies on an optimized relational database, seamlessly transitioning from SQLite for local environments to robust enterprise schemas, ensuring rigid transactional integrity, data normalization, and prevention of anomalous data behavior such as orphaned category records or misallocated funds. On the frontend, we bypass heavyweight Javascript framework requirements, instead synthesizing a pristine, high-performance vanilla HTML, CSS, and lightweight JS environment. Our deliberate styling avoids off-the-shelf component libraries in favor of entirely custom CSS rules built around vibrant, warm color palettes, dynamic glassmorphism UI elements, and highly responsive micro-animations that yield a phenomenally tactile and premium user experience. Artificial Intelligence tasks are offloaded to external asynchronous Google Gemini Flash API endpoints via secure backend tunnels, preventing client-side API key exposure while guaranteeing virtually instantaneous optical and contextual processing necessary for voice routing and visual receipt parsing. This decoupled, highly modular methodology means Spendora is incredibly resilient to failure and remarkably easy to upgrade without refactoring the foundational core logic.

*   **Impenetrable Security Models and Authentication Procedures:** 
    Realizing the immense sensitivity surrounding personal financial data led to implementing an incredibly stringent and resilient security layer around the Spendora platform. Authentication inherently leverages modern hashing algorithms (like PBKDF2 with SHA256) embedded within the Django authentication framework, meaning raw passwords are mathematically obfuscated and entirely irretrievable even in the event of a total database breach. We extended normal authentication methodologies by implementing a proprietary User Profile schema that injects custom, user-defined security questions natively into the registration loop, offering an independent account recovery mechanism that is uniquely siloed from external vectors, ensuring users can bypass locked accounts rapidly but purely securely. In addition, route protection is universally applied across every single accessible view; decorators rigidly enforce session validation, ensuring an unauthorized user cannot brute-force internal dashboard URIs or maliciously execute POST requests utilizing CSRF tokenization defenses. Cross-Site Request Forgery is intrinsically nullified alongside active protections against SQL Injection due to Django’s utilization of parameterization in its highly advanced standard Object Relational Mapper, making the Spendora instance effectively invulnerable to standardized top web vulnerabilities.

---

## 2. Integrated System Diagrams

Below are the complete suite of system diagrams documenting the Spendora database relationships, data flow, and Unified Modeling Language (UML) specifications.

### 2.1 Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USER ||--o{ USER_PROFILE : "has one"
    USER ||--o{ CATEGORY : "creates"
    USER ||--o{ EXPENSE : "logs"
    USER ||--o{ INCOME : "earns"
    USER ||--o{ SAVING : "saves"
    USER ||--o{ BUDGET : "sets"
    USER ||--o{ BILL_REMINDER : "schedules"
    CATEGORY ||--o{ EXPENSE : "categorizes"
    CATEGORY ||--o{ BUDGET : "is limited by"

    USER {
        int id PK
        string username
        string email
        string password
    }
    USER_PROFILE {
        int id PK
        int user_id FK
        string security_question
        string security_answer
        string plain_password
    }
    CATEGORY {
        int id PK
        int user_id FK
        string name
    }
    EXPENSE {
        int id PK
        int user_id FK
        int category_id FK
        decimal amount
        string description
        date date
    }
    INCOME {
        int id PK
        int user_id FK
        string source
        decimal amount
        date date
        string note
        datetime created_at
    }
    SAVING {
        int id PK
        int user_id FK
        string source
        decimal amount
        date date
        string note
        datetime created_at
    }
    BUDGET {
        int id PK
        int user_id FK
        int category_id FK
        decimal limit
        date month
    }
    BILL_REMINDER {
        int id PK
        int user_id FK
        string title
        decimal amount
        date due_date
        boolean is_recurring
        boolean is_paid
    }
```

### 2.2 Data Flow Diagram (DFD) - Context Level (Level 0)

```mermaid
flowchart TD
    US((User))
    AI((Google Gemini AI))
    DB[(Database System)]

    sys{Spendora AI \nFinancial System}

    US -- "Authentication, Settings, Target Limits" --> sys
    US -- "Voice Input, Receipt Images, Form Data" --> sys
    
    sys -- "Dashboard Analytics, Limit Alerts" --> US
    sys -- "Login Success/Fail, Reminders" --> US

    sys -- "Image/Voice Data" --> AI
    AI -- "Transcribed/Parsed Financial JSON" --> sys

    sys -- "SQL Queries (Read/Write)" --> DB
    DB -- "Record Sets, User State" --> sys
```

### 2.3 Data Flow Diagram (DFD) - Level 1

```mermaid
flowchart TD
    User((User))
    AI((Gemini API))
    DB[(Spendora Database)]

    subgraph Spendora Application
        Auth[1. Authentication & Security Process]
        Input[2. Data Ingestion & Parser]
        Engine[3. Analytics & Alert Engine]
    end

    User -- "Credentials" --> Auth
    Auth -- "Validation" --> DB
    DB -- "Session Token" --> Auth
    Auth -- "Access Granted" --> User

    User -- "Image/Voice/Text" --> Input
    Input -- "Raw AI Payload" --> AI
    AI -- "Structured Data" --> Input
    Input -- "Save Entity" --> DB

    DB -- "Transactions/Budgets" --> Engine
    Engine -- "Chart Data, Alerts, AI Predictions" --> User
```

### 2.4 UML Use Case Diagram

```mermaid
flowchart LR
    User((User))

    subgraph Spendora Financial System
        UC1([Register/Login])
        UC2([Recover Password via Security Q.])
        UC3([Add Income/Expense/Saving via Form])
        UC4([Add Transaction via Voice Action])
        UC5([Scan Receipt via AI Image OCR])
        UC6([Set & Monitor View Budgets])
        UC7([Manage Recurring Bill Reminders])
        UC8([View Dashboard Analytics & Insights])
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
```

### 2.5 UML Class Diagram

```mermaid
classDiagram
    class User {
        +id: Integer
        +username: String
        +email: String
        +password: String
        +login()
        +logout()
    }
    class UserProfile {
        +security_question: String
        +security_answer: String
        +plain_password: String
        +verify_answer()
    }
    class Category {
        +name: String
        +get_total_expenses()
    }
    class Transaction {
        <<Abstract>>
        +amount: Decimal
        +date: Date
        +note: String
        +save()
    }
    class Expense {
        +description: String
        +category_id: Integer
    }
    class Income {
        +source: String
        +created_at: DateTime
    }
    class Saving {
        +source: String
        +created_at: DateTime
    }
    class Budget {
        +limit: Decimal
        +month: Date
        +check_threshold(expense_amount)
    }
    class BillReminder {
        +title: String
        +due_date: Date
        +is_recurring: Boolean
        +is_paid: Boolean
        +rollover_if_needed()
    }

    Transaction <|-- Expense
    Transaction <|-- Income
    Transaction <|-- Saving

    User "1" --> "1" UserProfile : owns
    User "1" --> "*" Category : creates
    User "1" --> "*" Transaction : initiates
    User "1" --> "*" Budget : sets
    User "1" --> "*" BillReminder : schedules
    Category "1" <-- "*" Expense : belongs to
    Category "1" <-- "*" Budget : constrained by
```

### 2.6 UML Sequence Diagram (Receipt AI Scanning Flow)

```mermaid
sequenceDiagram
    actor User
    participant Frontend as View (HTML/JS)
    participant Server as Django Controller
    participant Gemini as AI API
    participant DB as Database

    User->>Frontend: Upload image receipt & Click Scan
    Frontend->>Server: HTTP POST /scan_receipt/ (multipart/form-data)
    Server->>Gemini: API Request (Image Base64 + Schema Prompt)
    activate Gemini
    Gemini-->>Server: JSON Response (Amount, Category, Description, Date)
    deactivate Gemini
    Server->>DB: Query or Create Category
    DB-->>Server: Category Instance
    Server->>DB: INSERT INTO Expense (...)
    DB-->>Server: Success
    Server-->>Frontend: JSON {status: "success", parsed_data}
    Frontend-->>User: Refresh Dashboard / Show Success Alert
```

### 2.7 UML Activity Diagram (Adding Expense/Checking Budget)

```mermaid
stateDiagram-v2
    [*] --> Start_Action
    Start_Action --> Input_Expense_Details: User submits form or voice
    Input_Expense_Details --> Validate_Data
    
    state Validate_Data {
        [*] --> Check_Numeric
        Check_Numeric --> valid?
        valid? --> True
        valid? --> False
    }
    
    Validate_Data --> Show_Error : False
    Show_Error --> Input_Expense_Details
    
    Validate_Data --> Save_To_Database : True
    Save_To_Database --> Fetch_Category_Budget
    
    Fetch_Category_Budget --> Calculate_Usage
    
    state is_over_limit <<choice>>
    Calculate_Usage --> is_over_limit
    
    is_over_limit --> Update_Dashboard : No/Under 80%
    is_over_limit --> Trigger_Threshold_Warning : >= 80%
    
    Trigger_Threshold_Warning --> Update_Dashboard
    Update_Dashboard --> [*]
```

### 2.8 UML State Machine / Statechart Diagram (Bill Reminder Lifecycle)

```mermaid
stateDiagram-v2
    [*] --> Scheduled: Created by User
    
    Scheduled --> Approaching_Due_Date : Time passes
    Approaching_Due_Date --> Dashboard_Alert_Triggered : < 3 Days remaining
    
    Dashboard_Alert_Triggered --> Paid : User marks as Paid
    Scheduled --> Paid: User marks as Paid
    
    Paid --> Rollover_Generation : Is Recurring? (True)
    Paid --> [*] : Is Recurring? (False)
    
    Rollover_Generation --> Scheduled : New Month Instance Created
    
    Dashboard_Alert_Triggered --> Overdue : Due Date Exceeded (User idle)
    Overdue --> Paid : User finally marks paid
```

### 2.9 UML Component Diagram

```mermaid
flowchart TB
    subgraph Client Application [Frontend Environment]
        UI[UI/UX Rendering Engine]
        JS[Javascript Fetch / Interactive Handlers]
    end

    subgraph Backend Environment [Spendora Core]
        RC[Routing Controller / URLs]
        AuthC[Authentication Module]
        Core[Transaction Management Module]
        AIM[AI Integration Service]
    end

    subgraph Storage [Persistence Layer]
        DB[(SQL Relational Database)]
    end
    
    subgraph External [Cloud]
        GAPI[Google Gemini Flash]
    end

    UI <-->|HTTP GET/POST / WS| RC
    JS <-->|AJAX / JSON| RC
    
    RC --> AuthC
    RC --> Core
    RC --> AIM
    
    AuthC <--> DB
    Core <--> DB
    AIM <--> |REST API| GAPI
```

### 2.10 UML Deployment Diagram

```mermaid
flowchart TD
    subgraph User Device
        Browser[Modern Web Browser\nChrome, Safari, Edge]
    end

    subgraph Cloud Infrastructure provider/LocalHost
        subgraph Web Server Node
            WS[Gunicorn / WSGI HTTP Server]
            Django[Django Application Process]
        end
        
        subgraph Database Node
            SQL[(Relational Database Service\nPostgreSQL or SQLite)]
        end
    end

    subgraph Third Party Services
        Google[Google Cloud Platform\nAI/ML Endpoints]
    end

    Browser -- "HTTPS (Port 443)\nor HTTP (8000)" --> WS
    WS -- "Local Socket" --> Django
    Django -- "TCP (Port 5432) OR Local I/O" --> SQL
    Django -- "HTTPS API Call" --> Google
```

### 2.11 UML Communication (Collaboration) Diagram

```mermaid
flowchart TD
    U([User])
    V[Dashboard View]
    C[Expense Controller]
    B[Budget Model]
    DB[(Database)]

    U -->|1. Submit Add Expense Request| V
    V -->|2. POST Data| C
    C -->|3. Validate & Map Data| C
    C -->|4. Query Limit| B
    B -->|4.1. SQL SELECT| DB
    B -->|4.2. Return Limit| C
    C -->|5. Insert Expense| DB
    C -->|6. Calculate Usage| C
    C -->|7. Return State & HTTP Response| V
    V -->|8. Render Updated Charts| U
```

### 2.12 UML Object Diagram

```mermaid
classDiagram
    class User_Admin {
        username = "admin_user"
        email = "admin@spendora.local"
    }
    class Cat_Food {
        name = "Groceries"
    }
    class Exp_Morning {
        amount = 45.50
        description = "Walmart Weekly Run"
        date = "2026-04-02"
    }
    class Bud_Food {
        limit = 500.00
        month = "2026-04-01"
    }
    class Bill_Netflix {
        title = "Netflix Subscription"
        amount = 15.99
        due_date = "2026-04-15"
        is_recurring = true
    }

    User_Admin --> Cat_Food : has created
    User_Admin --> Exp_Morning : has logged
    User_Admin --> Bud_Food : has set
    User_Admin --> Bill_Netflix : is subscribed to
    Exp_Morning --> Cat_Food : categorized under
    Bud_Food --> Cat_Food : monitors limit for
```
