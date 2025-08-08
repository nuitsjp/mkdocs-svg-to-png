# Mermaid図表サンプル

このページでは、様々なMermaid図表タイプのサンプルを紹介します。これらの図表は、通常のビルドではSVG形式で表示され、PDF生成時（`ENABLE_PDF_EXPORT=1`）にPNG形式に変換されます。

## フローチャート

基本的なプロセスフローを表現します：

```mermaid
flowchart TD
    A[開始] --> B{条件判定}
    B -->|Yes| C[処理A実行]
    B -->|No| D[処理B実行]
    C --> E[結果を保存]
    D --> E
    E --> F[終了]

    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style B fill:#fff3e0
```

## シーケンス図

システム間の相互作用を時系列で表現します：

```mermaid
sequenceDiagram
    participant U as ユーザー
    participant W as Webサーバー
    participant A as APIサーバー
    participant D as データベース

    U->>+W: ログイン要求
    W->>+A: 認証リクエスト
    A->>+D: ユーザー情報取得
    D-->>-A: ユーザーデータ
    A-->>-W: 認証結果
    W-->>-U: ログイン完了

    Note over U,D: 認証プロセス
```

## ER図

データベース設計のエンティティ関係を表現します：

```mermaid
erDiagram
    USER ||--o{ ORDER : "places"
    ORDER ||--|{ ORDER_ITEM : "contains"
    PRODUCT ||--o{ ORDER_ITEM : "ordered"
    CATEGORY ||--o{ PRODUCT : "belongs to"

    USER {
        int user_id PK
        string email UK
        string name
        datetime created_at
    }

    ORDER {
        int order_id PK
        int user_id FK
        datetime order_date
        decimal total_amount
        string status
    }

    PRODUCT {
        int product_id PK
        int category_id FK
        string name
        decimal price
        int stock_quantity
    }
```

## クラス図

オブジェクト指向設計のクラス関係を表現します：

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() String
        +move() void
    }

    class Dog {
        +String breed
        +bark() String
        +wagTail() void
    }

    class Cat {
        +String color
        +boolean isIndoor
        +meow() String
        +purr() void
    }

    Animal <|-- Dog : 継承
    Animal <|-- Cat : 継承

    class Owner {
        +String name
        +feedAnimal(Animal) void
    }

    Owner o-- Animal : 飼っている
```

## 状態図

システムやオブジェクトの状態遷移を表現します：

```mermaid
stateDiagram-v2
    [*] --> 停止中
    停止中 --> 実行中 : 開始ボタン押下
    実行中 --> 一時停止 : 一時停止ボタン押下
    一時停止 --> 実行中 : 再開ボタン押下
    実行中 --> 完了 : 処理完了
    実行中 --> エラー : エラー発生
    一時停止 --> 停止中 : 停止ボタン押下
    完了 --> 停止中 : リセット
    エラー --> 停止中 : リセット
    停止中 --> [*] : アプリ終了
```

## ガントチャート

プロジェクトスケジュールとタスクの進行を表現します：

```mermaid
gantt
    title プロジェクト開発スケジュール
    dateFormat YYYY-MM-DD
    axisFormat %m/%d

    section 設計フェーズ
    要件定義         :done, req, 2024-01-01, 2024-01-15
    基本設計         :done, design, 2024-01-10, 2024-01-25
    詳細設計         :active, detail, 2024-01-20, 2024-02-05

    section 開発フェーズ
    フロントエンド開発 :dev1, after detail, 20d
    バックエンド開発   :dev2, after detail, 25d
    統合テスト        :test, after dev1, 10d

    section デプロイ
    本番リリース      :deploy, after test, 3d
```

## パイチャート

データの割合や構成比を表現します：

```mermaid
pie title 開発チーム構成
    "フロントエンド開発者" : 35
    "バックエンド開発者" : 30
    "QAエンジニア" : 20
    "DevOpsエンジニア" : 15
```

## フローチャート（条件分岐付き）

より複雑なフローチャートを表現します：

```mermaid
flowchart LR
    A[Start] --> B{Decision?}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E{Another check?}
    D --> E
    E -->|Pass| F[Success]
    E -->|Fail| G[Error Handler]
    G --> H[Retry?]
    H -->|Yes| B
    H -->|No| I[End]
    F --> I

    style F fill:#90EE90
    style I fill:#FFB6C1
    style G fill:#FFE4B5
```

---

これらの図表はすべて、Mermaidの記法で作成され、プラグインによって適切な形式（SVGまたはPNG）で表示されます。PDF生成時には自動的にPNG形式に変換されるため、文書の配布や印刷に適した形式で出力されます。
