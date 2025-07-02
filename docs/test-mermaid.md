# Mermaidテストページ

このページでは、Mermaidの各種図を使用して、SVGからPNGへの変換機能をテストします。

## フローチャート

基本的なフローチャートです：

```mermaid
flowchart TD
    A[開始] --> B{条件判定}
    B -->|Yes| C[処理A]
    B -->|No| D[処理B]
    C --> E[終了]
    D --> E
```

## シーケンス図

システム間の相互作用を表現するシーケンス図です：

```mermaid
sequenceDiagram
    participant A as ユーザー
    participant B as サーバー
    participant C as データベース

    A->>B: リクエスト送信
    B->>C: データ取得
    C-->>B: データ返却
    B-->>A: レスポンス送信
```

## ガントチャート

プロジェクトスケジュールを表現するガントチャートです：

```mermaid
gantt
    title プロジェクトスケジュール
    dateFormat  YYYY-MM-DD
    section 設計
    要件定義    :done, des1, 2024-01-01,2024-01-15
    設計書作成  :done, des2, 2024-01-10,2024-01-25
    section 開発
    実装        :active, dev1, 2024-01-20,2024-02-15
    テスト      :dev2, 2024-02-10,2024-02-25
```

## クラス図

オブジェクト指向設計のクラス関係を表現するクラス図です：

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +String color
        +meow()
    }

    Animal <|-- Dog
    Animal <|-- Cat
```

## ER図

データベース設計のER図です：

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : ordered_in

    USER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int user_id FK
        date order_date
    }
    PRODUCT {
        int id PK
        string name
        decimal price
    }
    ORDER_ITEM {
        int order_id FK
        int product_id FK
        int quantity
    }
```

## 状態図

システムの状態遷移を表現する状態図です：

```mermaid
stateDiagram-v2
    [*] --> 停止中
    停止中 --> 実行中 : 開始
    実行中 --> 一時停止 : 一時停止
    一時停止 --> 実行中 : 再開
    実行中 --> 停止中 : 停止
    一時停止 --> 停止中 : 停止
    停止中 --> [*]
```

## パイチャート

データの割合を表現するパイチャートです：

```mermaid
pie title プログラミング言語使用率
    "Python" : 35
    "JavaScript" : 25
    "Java" : 15
    "TypeScript" : 12
    "その他" : 13
```

---

これらの図はすべて、通常のビルドではSVG形式で保存され、`ENABLE_PDF_EXPORT=1`環境変数が設定されている場合にのみPNG形式に変換されます。
