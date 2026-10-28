# 使用 Code Evaluator 檢查訂單配料庫存

## 學習目標

完成本章後，你應能：

- 說明 Code Evaluator 在 Agent 評估中的用途。
- 從 LangSmith Run 的 `outputs.messages` 找出實際訂單資料。
- 解釋 `ingredient_stock_evaluator()` 的輸入、判斷流程與回傳結果。
- 根據訂單內容判斷 evaluator 應回傳 `score: 0` 或 `score: 1`。
- 區分此 evaluator 能檢查的業務規則及其未涵蓋的問題。

> 本章使用 [LangSlice Agent 的 Run 紀錄](run-01a06b7d-52cf-7b00-a3c8-fbcc7abae229.json)說明 evaluator 如何讀取 Agent 的實際輸出。若尚不了解 Run、Trace 與 ToolMessage，請先閱讀[〈使用 LangSmith Tracing 觀察 Agent 執行流程〉](tracing.md)。

---

## 1. 為什麼需要 Code Evaluator？

Agent 的最後回答看起來合理，不代表訂單一定符合業務規則。例如，Agent 可能告訴顧客「披薩已加入訂單」，但訂單中其實包含庫存為 0 的配料。

若判斷條件可以寫成明確規則，就不需要再呼叫 LLM 進行主觀判斷。這類評估適合使用 **Code Evaluator**：以一般程式碼讀取 Agent 執行結果，檢查特定條件，再回傳可統計的分數。

本章要測量的規則是：

> 訂單中的每一項披薩配料都必須有庫存；只要加入任何 `stock_units <= 0` 的配料，本次執行就不通過。

因此，評分定義為：

| 分數 | 意義 |
|---|---|
| `1` | 沒有在訂單中發現缺貨配料 |
| `0` | 訂單中至少包含一項缺貨配料 |

---

## 2. Evaluator 的完整程式碼

```python
"""Code evaluator for out-of-stock ingredients in pizza orders."""

import json

import database as db


def ingredient_stock_evaluator(run, example=None):
    outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {})
    outputs = outputs or {}

    # 針對 output 中的每個 message，檢查 ToolMessage 中的 order
    # 是否包含缺貨配料。
    for message in reversed(outputs.get("messages", [])):
        if isinstance(message, dict):
            role = message.get("role") or message.get("type")
            content = message.get("content")
        else:
            role = message.type
            content = message.content

        if role != "tool":
            continue

        result = json.loads(content)
        order = result.get("order")
        if not order:
            continue

        out_of_stock = {
            topping
            for pizza in order["pizzas"]
            for topping in pizza["toppings"]
            if db.get_ingredient(topping)["stock_units"] <= 0
        }

        return {
            "score": 0 if out_of_stock else 1,
            "comment": (
                f"Out-of-stock ingredients added: {', '.join(sorted(out_of_stock))}"
                if out_of_stock
                else "All ordered ingredients are in stock."
            ),
        }

    return {"score": 1, "comment": "No order found."}
```

這是一個 **reference-free evaluator**。雖然函數可以接收 `example`，但目前程式沒有讀取 `example` 或 `reference_outputs`；它直接根據 `run.outputs` 中的實際訂單及配料資料庫進行判斷。

---

## 3. 輸入資料從哪裡來？

### 3.1 `run` 是受評估的執行結果

LangSmith 執行實驗時，會把 Agent 在某一筆資料上的 Run 交給 evaluator。此函數首先取得：

```python
outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {})
```

這行同時支援兩種資料形態：

- 若 `run` 是 LangSmith `Run` 物件，使用 `run.outputs`。
- 若 `run` 是 dictionary，使用 `run.get("outputs", {})`。

`outputs = outputs or {}` 則保證當 outputs 是 `None` 時，後續仍可用空 dictionary 處理。

### 3.2 真正被檢查的是 ToolMessage

指定 Run 的 `outputs.messages` 同時包含：

- HumanMessage：顧客的要求。
- AIMessage：Model 的 Tool Call 或最後回答。
- ToolMessage：Tool 的實際執行結果。

訂單是由 Tool 建立與更新，因此 evaluator 不解析 Agent 最後的自然語言回答，而是只處理：

```python
if role != "tool":
    continue
```

**ToolMessage 中的 `order` 才是 evaluator 要驗證的結構化業務資料。**

---

## 4. 為什麼要反向讀取 Messages？

程式使用：

```python
for message in reversed(outputs.get("messages", [])):
```

同一個 Agent Run 可能包含多個 ToolMessage。例如：

```text
start_order
    ↓ 建立空訂單
add_pizza_to_order
    ↓ 加入披薩
confirm_order
    ↓ 確認最終訂單
Agent 最後回答
```

從後往前讀取時，最後的 AIMessage 會先被略過，接著遇到 `confirm_order` 的 ToolMessage。因為其中含有 `order`，evaluator 便使用這份最新訂單快照進行檢查並立即回傳結果。

若某個 ToolMessage 不含 `order`，程式會繼續向前尋找：

```python
order = result.get("order")
if not order:
    continue
```

因此，這段程式實際採用的是：

> 由後往前找到的第一則、具有 `order` 欄位的 ToolMessage。

---

## 5. 如何找出缺貨配料？

Evaluator 使用集合推導式（set comprehension）逐層展開訂單：

```python
out_of_stock = {
    topping
    for pizza in order["pizzas"]
    for topping in pizza["toppings"]
    if db.get_ingredient(topping)["stock_units"] <= 0
}
```

可將它讀成三個步驟：

1. 走訪 `order["pizzas"]` 中的每一張披薩。
2. 走訪每張披薩 `toppings` 中的每一項配料。
3. 呼叫 `db.get_ingredient(topping)` 查詢配料，保留 `stock_units <= 0` 的名稱。

使用 set 的效果是去除重複值。即使三張披薩都包含 `pineapple`，最後的 `out_of_stock` 仍只會保留一個：

```python
{"pineapple"}
```

---

## 6. 範例一：指定 Run 中的正常訂單

指定 Run 的使用者輸入是：

```text
can I get three large hand tossed mushroom pizzas for pickup?
name is Yusuf. place the order please.
```

Model 產生的 Tool Call arguments 為：

```json
{
  "crust": "hand tossed",
  "quantity": 3,
  "size": "large",
  "toppings": ["mushroom"]
}
```

`add_pizza_to_order` 執行後，訂單中的配料為：

```json
"toppings": ["mozzarella", "mushrooms"]
```

請注意兩項資料變化：

- Tool 自動加入預設配料 `mozzarella`。
- 使用者輸入的 `mushroom` 在訂單中被正規化為 `mushrooms`。

Evaluator 反向讀取 messages 後，會從 `confirm_order` 的 ToolMessage 取得最終訂單，概念上執行：

```python
db.get_ingredient("mozzarella")["stock_units"]
db.get_ingredient("mushrooms")["stock_units"]
```

若評估當下資料庫中的兩項庫存都大於 0，則：

```python
out_of_stock = set()
```

回傳結果為：

```json
{
  "score": 1,
  "comment": "All ordered ingredients are in stock."
}
```

這個分數表示「本次訂單沒有加入完全缺貨的配料」，不是對 Agent 整體品質的總分。

---

## 7. 範例二：訂單包含缺貨的 Pineapple

假設 ToolMessage 中的訂單包含：

```json
{
  "order": {
    "pizzas": [
      {
        "toppings": ["mozzarella", "pineapple"]
      }
    ]
  }
}
```

而配料資料庫回傳：

```python
db.get_ingredient("mozzarella")["stock_units"] > 0
db.get_ingredient("pineapple")["stock_units"] == 0
```

集合推導式的結果便是：

```python
out_of_stock = {"pineapple"}
```

Evaluator 回傳：

```json
{
  "score": 0,
  "comment": "Out-of-stock ingredients added: pineapple"
}
```

這個結果指出一項可定位的失敗：訂單資料中已經出現缺貨配料。Evaluator 不負責修正訂單，也不決定錯誤一定來自 Model；開發者仍須利用 Trace 檢查 Tool Call、Tool 邏輯及 ToolMessage，找出配料在哪個步驟被錯誤加入。

---

## 8. 找不到訂單時會發生什麼事？

若所有 messages 都不是 ToolMessage，或所有 ToolMessage 都沒有 `order`，程式最後回傳：

```json
{
  "score": 1,
  "comment": "No order found."
}
```

這裡的 `score: 1` 只能解讀為：

> 沒有觀察到「訂單加入缺貨配料」這項違規。

它不能解讀成「Agent 已正確完成使用者的訂餐要求」。如果測試案例原本要求 Agent 建立訂單，但 Agent 完全沒有建立訂單，這個 evaluator 仍可能給 1 分。因此，實驗中通常還需要另一個 evaluator 檢查「應建立訂單時是否真的產生訂單」。

---

## 9. 此 Evaluator 的責任邊界

### 9.1 能檢查的內容

- ToolMessage 是否包含訂單。
- 訂單中有哪些披薩配料。
- 這些配料在評估當下是否為 `stock_units <= 0`。
- 最新訂單是否仍包含完全缺貨的配料。


## 10. 重點整理

- `ingredient_stock_evaluator()` 是確定性的二元評分器，用來檢查最新訂單是否包含完全缺貨的配料。
- 評估資料來自 `run.outputs.messages` 中的 ToolMessage，不是 Agent 最後的自然語言回答。
- 反向搜尋讓 evaluator 優先使用最近一則含有 `order` 的 ToolMessage。
- 配料庫存由 `db.get_ingredient()` 在評估時查詢；`stock_units <= 0` 的配料會被加入 `out_of_stock` 集合。
- `out_of_stock` 非空時回傳 `score: 0`，否則回傳 `score: 1`。
- `example` 目前未被使用，因此評分不會比對 reference output。
- 單一 evaluator 只代表一項明確測量；1 分不代表 Agent 的所有行為都正確。



