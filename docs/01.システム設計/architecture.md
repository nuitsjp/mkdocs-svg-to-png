# システムアーキテクチャ

## 全体アーキテクチャ

```mermaid
graph TB
    subgraph "外部システム"
        EXT1[外部API A]
        EXT2[外部API B]
        EXT3[レガシーシステム]
    end
    
    subgraph "DMZ"
        LB[Load Balancer]
        WAF[Web Application Firewall]
    end
    
    subgraph "Web層"
        WEB1[Web Server 1]
        WEB2[Web Server 2]
        WEB3[Web Server 3]
    end
    
    subgraph "アプリケーション層"
        APP1[App Server 1]
        APP2[App Server 2]
        APP3[App Server 3]
        QUEUE[Message Queue]
        CACHE[Redis Cache]
    end
    
    subgraph "データ層"
        DB1[Primary DB]
        DB2[Replica DB]
        DWH[Data Warehouse]
        BACKUP[Backup Storage]
    end
    
    subgraph "外部サービス"
        EMAIL[Email Service]
        SMS[SMS Service]
        MONITOR[Monitoring]
        LOG[Log Analytics]
    end
    
    Internet --> WAF
    WAF --> LB
    LB --> WEB1
    LB --> WEB2
    LB --> WEB3
    
    WEB1 --> APP1
    WEB2 --> APP2
    WEB3 --> APP3
    
    APP1 --> QUEUE
    APP2 --> QUEUE
    APP3 --> QUEUE
    
    APP1 --> CACHE
    APP2 --> CACHE
    APP3 --> CACHE
    
    APP1 --> DB1
    APP2 --> DB1
    APP3 --> DB1
    
    DB1 --> DB2
    DB1 --> DWH
    DB1 --> BACKUP
    
    APP1 --> EMAIL
    APP2 --> SMS
    APP3 --> EXT1
    APP1 --> EXT2
    APP2 --> EXT3
    
    ALL --> MONITOR
    ALL --> LOG
```

## マイクロサービス構成

```mermaid
graph TB
    subgraph "API Gateway"
        GW[Gateway Service]
    end
    
    subgraph "認証・認可"
        AUTH[Auth Service]
        PERM[Permission Service]
    end
    
    subgraph "ビジネスサービス"
        USER[User Service]
        ORDER[Order Service]
        PAYMENT[Payment Service]
        INVENTORY[Inventory Service]
        NOTIFICATION[Notification Service]
    end
    
    subgraph "データストア"
        USERDB[(User DB)]
        ORDERDB[(Order DB)]
        PAYMENTDB[(Payment DB)]
        INVENTORYDB[(Inventory DB)]
    end
    
    CLIENT[Client Application] --> GW
    GW --> AUTH
    GW --> USER
    GW --> ORDER
    GW --> PAYMENT
    GW --> INVENTORY
    
    AUTH --> PERM
    USER --> USERDB
    ORDER --> ORDERDB
    ORDER --> INVENTORY
    ORDER --> NOTIFICATION
    PAYMENT --> PAYMENTDB
    PAYMENT --> NOTIFICATION
    INVENTORY --> INVENTORYDB
```

## セキュリティレイヤー

```mermaid
graph LR
    subgraph "セキュリティ層"
        A[WAF] --> B[DDoS Protection]
        B --> C[SSL/TLS Termination]
        C --> D[Rate Limiting]
        D --> E[Authentication]
        E --> F[Authorization]
        F --> G[Data Encryption]
        G --> H[Audit Logging]
    end
