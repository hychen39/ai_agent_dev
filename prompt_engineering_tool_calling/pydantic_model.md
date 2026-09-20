# 補充: Pydantic model 及 Python 型別提示 (Type Hint)

## Pydantic model

### 什麼是 Pydantic model？

[Pydantic model](https://docs.pydantic.dev/latest/concepts/models/) 是一種使用 Python type hints 定義資料結構的 class。建立 Pydantic model 時，需要繼承 `BaseModel`，並將每一個欄位宣告為 annotated attribute。

例如，前面的 `CustomerMessageClassification` 定義一筆分類結果必須包含：

- `category`：值只能是 `"Billing"`、`"Delivery"` 或 `"Product"`。
- `reason`：值必須是字串。

因此，Pydantic model 可以視為應用程式中的 **data contract**：它明確規定一筆資料應包含哪些欄位、每個欄位的型態，以及必須符合哪些限制。

### Pydantic model 的用途

Pydantic model 主要用於接收及處理來自外部的資料，例如 API request、JSON、資料庫查詢結果或 LLM response。

它提供以下功能：

- **定義資料結構**：使用 type hints 與 `Field()` 宣告欄位、型態、預設值、說明及限制。
- **驗證資料**：檢查必要欄位、資料型態與允許值是否正確。
- **轉換資料**：在適合的情況下，將輸入值轉換成欄位要求的型態。
- **提供清楚的錯誤資訊**：資料無法通過驗證時，產生 `ValidationError`，指出發生問題的欄位與原因。
- **操作結構化資料**：驗證成功後，可以使用 object attribute 取得欄位值。
- **序列化資料**：將 model object 轉換成 Python dictionary 或 JSON string。
- **產生 JSON Schema**：將 model 的欄位與限制轉換成 JSON Schema，供 API、文件工具或 LLM 使用。

Pydantic validation 關注的是驗證後產生的 model object。只要建立成功，就能確定 object 中的欄位符合 model 定義的型態與限制。

### Pydantic model 的運作方式

1. 建立繼承自 `BaseModel` 的 class。
2. 使用 type hints 與 `Field()` 定義欄位及限制。
3. 將 Python dictionary、JSON 或其他外部資料交給 Pydantic model。
4. Pydantic 解析資料，並進行必要的型態轉換與驗證。
5. 驗證成功時，回傳 model object；驗證失敗時，拋出 `ValidationError`。
6. 使用 model object 的 attribute 或 serialization methods 取得資料。

### 範例：驗證客戶分類結果

以下程式碼沿用前面定義的 `CustomerMessageClassification`：

```python
classification_data = {
    "category": "Delivery",
    "reason": (
        "The order is marked as delivered, "
        "but the customer did not receive it."
    )
}

classification = CustomerMessageClassification.model_validate(
    classification_data
)

print(classification.category)
print(classification.reason)
```

預期輸出

```text
Delivery
The order is marked as delivered, but the customer did not receive it.
```

程式碼說明：

- `classification_data` 是一般的 Python dictionary，可能來自 API、JSON parser 或 LLM。
- `model_validate()` 依照 `CustomerMessageClassification` 的欄位定義驗證 dictionary。
- 驗證成功後，`classification` 是一個 `CustomerMessageClassification` object。
- 可以透過 `classification.category` 與 `classification.reason` 存取欄位，不需要再使用 dictionary key。

### 範例：處理無效資料

如果 category 不在 schema 允許的範圍內，Pydantic 會產生 `ValidationError`：

```python
from pydantic import ValidationError

invalid_data = {
    "category": "Shipping",
    "reason": "The customer did not receive the parcel."
}

try:
    CustomerMessageClassification.model_validate(invalid_data)
except ValidationError as error:
    print(error)
```

`"Shipping"` 不符合 `Literal["Billing", "Delivery", "Product"]` 的限制，因此不會建立無效的 `CustomerMessageClassification` object。應用程式可以捕捉 `ValidationError`，再決定要重新要求模型產生結果、記錄錯誤或停止後續處理。

### 常用的 Pydantic model methods

- `model_validate(data)`：驗證 Python dictionary 或既有的 model instance；若另外啟用對應設定，也可從其他 object 的 attributes 讀取資料。
- `model_validate_json(json_data)`：直接解析並驗證 JSON string 或 bytes。
- `model_dump()`：將 model object 轉換成 Python dictionary。
- `model_dump_json()`：將 model object 序列化成 JSON string。
- `model_json_schema()`：取得描述 model 欄位與限制的 JSON Schema。

```python
print(classification.model_dump())
print(classification.model_dump_json(indent=2))
print(CustomerMessageClassification.model_json_schema())
```

在 LangChain structured output 中，Pydantic model 一方面將 schema 提供給 LLM，另一方面驗證模型產生的結果。這可以確保輸出的結構、資料型態與允許值正確，但不能保證內容在語意上一定正確。例如，`reason` 即使是合法字串，仍可能包含錯誤的分類理由，因此應用程式仍需依任務風險進行額外檢查。

## 補充: Python 中的型別提示 (Type Hint)

### 什麼是 Type Hint？

[Type hint](https://docs.python.org/3/library/typing.html) 是寫在變數、function parameter、return value 或 class attribute 上的型別註記，用來說明程式預期使用的資料型別。

```python
customer_message: str = "My parcel has not arrived."

def classify_message(message: str) -> str:
    return "Delivery"
```

在這個例子中：

- `customer_message: str` 表示變數預期保存字串。
- `message: str` 表示 function parameter 預期接收字串。
- `-> str` 表示 function 預期回傳字串。

Python runtime 本身通常不會強制檢查 type hints。Type hints 主要提供給 IDE、type checker、linter 與其他 library 使用。例如，Pydantic 會在 runtime 讀取 model 中的 type hints，並將它們轉換成資料驗證規則與 JSON Schema。

### 在 Pydantic schema 中使用 Type Hint

Pydantic model 的基本欄位語法為：

```python
field_name: field_type
```

例如：

```python
from pydantic import BaseModel

class CustomerMessage(BaseModel):
    message: str
    order_id: int
```

`message: str` 與 `order_id: int` 不只是開發者閱讀的註記。Pydantic 會使用這些 type hints 檢查輸入資料，並確保驗證後的 `message` 是字串、`order_id` 是整數。

### 常用的 Type Hints

| 型別提示 | 欄位可以接受的資料 | 範例 |
|---|---|---|
| `str` | 字串 | `"Delivery"` |
| `int` | 整數 | `12345` |
| `float` | 浮點數 | `0.92` |
| `bool` | 布林值 | `True` |
| `list[str]` | 元素皆為字串的 list | `["parcel", "delivery"]` |
| `dict[str, str]` | key 與 value 皆為字串的 dictionary | `{"department": "logistics"}` |
| `Literal["Billing", "Delivery", "Product"]` | 只能是列出的其中一個值 | `"Delivery"` |
| `str \| None` | 字串或 `None` | `"agent_01"` 或 `None` |
| `CustomerMessageClassification` | 另一個 Pydantic model | 巢狀的分類結果 |

`list[str]` 不只表示欄位必須是 list，也表示 list 中的每一個元素都必須是字串。同樣地，`dict[str, str]` 分別限制 dictionary key 與 value 的型別。

### 使用 Literal 限制允許值

`Literal` 由 `typing` module 提供，表示欄位只能使用列出的固定值。

```python
from typing import Literal

category: Literal["Billing", "Delivery", "Product"]
```

`str` 允許任何字串；`Literal["Billing", "Delivery", "Product"]` 則只允許三個分類名稱。對 LLM structured output 而言，使用 `Literal` 可以防止模型產生 `"Shipping"`、`"Other"` 或其他不在系統定義中的 category。

### 必填、可為空值與預設值

定義 Pydantic schema 時，需要區分以下三種欄位：

```python
class ClassificationNote(BaseModel):
    reason: str
    reviewer: str | None
    internal_note: str | None = None
```

- `reason: str`：required，而且值必須是字串。
- `reviewer: str | None`：required，但傳入的值可以是字串或 `None`。
- `internal_note: str | None = None`：不是 required；未提供欄位時，使用預設值 `None`。

`str | None` 只表示 **nullable**，不代表該欄位可以省略。在 Pydantic v2 中，若要讓欄位可以省略，必須明確提供 default value，例如 `= None`。

`Optional[str]` 與 `str | None` 的意思相同：

```python
from typing import Optional

reviewer: Optional[str] = None
```

在 Python 3.10 以上的程式碼中，通常可以使用較簡潔的 `str | None`。

### 範例：客戶分類綱要中的型別提示

以下 schema 使用多種 type hints 描述較完整的 customer message classification result：

```python
from typing import Literal
from pydantic import BaseModel, Field

class DetailedCustomerMessageClassification(BaseModel):
    # List of values
    category: Literal["Billing", "Delivery", "Product"] = Field(
        description="The category assigned to the customer message."
    )
    # String 
    reason: str = Field(
        description="A short explanation for the classification."
    )
    # Float with range constraints
    confidence: float = Field(
        ge=0,
        le=1,
        description="The confidence score from 0 to 1."
    )
    # List of strings
    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that support the classification."
    )
    # Boolean with default value
    requires_follow_up: bool = Field(
        default=False,
        description="Whether a human agent should follow up."
    )
    # Nullable string with default value
    assigned_agent: str | None = Field(
        default=None,
        description="The assigned agent ID, if available."
    )
```

程式碼說明：

- `category` 使用 `Literal` 限制分類名稱。
- `reason: str` 要求分類理由必須是字串。
- `confidence: float` 要求信心分數為浮點數；`ge=0` 與 `le=1` 進一步限制數值範圍。
- `keywords: list[str]` 表示結果包含一個字串 list。`default_factory=list` 會在未提供欄位時建立空 list。
- `requires_follow_up: bool = False` 是具有預設值的布林欄位。
- `assigned_agent: str | None = None` 表示 agent ID 可以是字串或 `None`，而且此欄位可以省略。

驗證資料時，Pydantic 會同時使用 type hints 與 `Field()` 中的限制：

```python
result = DetailedCustomerMessageClassification.model_validate({
    "category": "Delivery",
    "reason": "The order was marked as delivered but was not received.",
    "confidence": 0.95,
    "keywords": ["courier", "delivered", "not received"],
    "requires_follow_up": True
})

print(result.category)         # Delivery
print(result.confidence)       # 0.95
print(result.assigned_agent)   # None
```

如果 `category` 是 `"Shipping"`、`confidence` 大於 `1`，或 `keywords` 中包含非字串資料，Pydantic 就會產生 `ValidationError`。

設計 LLM output schema 時，應盡量使用明確且具限制力的 type hints。若使用 `Any` 或過於寬鬆的型別，Pydantic 能執行的驗證較少，產生的 JSON Schema 也無法清楚告訴模型每個欄位應該輸出什麼資料。
