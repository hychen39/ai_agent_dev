
# Memory Store in LangChain Agents (二)

## 學習目標

完成本章後，學生能：

- 區分短期記憶與跨 thread 的長期記憶。
- 使用 Tool 寫入與讀取 Memory Store。
- 整合 Agent、Checkpointer 與 Store，完成跨 thread 存取。

## 實作 2: 使用 Tool 保存及讀取 ERP 工作備忘錄

### 應用情境

ERP 使用者在處理採購單、請購單或其它文件時，可能會希望 Agent 記住需要後續
追蹤的事項。

例如，採購人員在查詢採購單 `B2048` 時告訴 Agent：

```text
備忘事項：採購單 B2048 等供應商補報價後再送審。
```

Agent 呼叫 Tool，將這筆工作備忘錄寫入 Memory Store。

之後，使用者在另一個對話 thread 詢問：

```text
我目前有哪些採購事項需要追蹤？
```

Agent 再呼叫 Tool，從 Memory Store 讀取這位使用者保存的 ERP 工作備忘錄，
並根據 Tool result 整理回覆。

此情境適合使用長期記憶的 Memory Store，不適合用短期記憶，因為工作備忘錄是使用者希望跨 thread 保存的
個人資料，不屬於某一個 thread 的 message history。

### 運作流程

第一個 thread 將工作備忘錄寫入 Memory Store：

```text
User
「備忘事項：採購單 B2048 等供應商補報價後再送審。」
    ↓
LLM 產生 save_erp_follow_up tool call
    ↓
save_erp_follow_up()
    ↓
runtime.store.put(...)
    ↓
ToolMessage
    ↓
LLM 回覆已完成保存
```

另一個 thread 按需讀取工作備忘錄：

```text
User
「我目前有哪些採購事項需要追蹤？」
    ↓
LLM 產生 get_erp_follow_ups tool call
    ↓
get_erp_follow_ups()
    ↓
runtime.store.search(...)
    ↓
ToolMessage
    ↓
LLM 整理並回覆追蹤事項
```

Tool 的回傳值會由 Agent 轉換成 `ToolMessage`，加入目前 thread 的 message
history。LLM 在下一次 model call 時就能看到 Tool 從 long-term memory 讀取的
資料。

### Memory Store 的資料設計

每一位 ERP 使用者都有自己的 namespace：

```python
namespace = ("users", user_id, "follow_ups")
```

本例使用 ERP 文件類型與文件編號組成 key：

```python
key = "PO-B2048"
```

實際保存的 value 是一個 dictionary：

```python
value = {
    "document_type": "PO",
    "document_id": "B2048",
    "note": "等供應商補報價後再送審"
}
```

完整的資料位置可以表示為：

```text
("users", "user_123", "follow_ups") / "PO-B2048"
                    namespace           key
```

將 `user_id` 放入 namespace，以隔離不同使用者的工作備忘錄。


### 建立自訂 Agent Context

定義 Static Context Schema `UserStaticContext` 保存目前登入 ERP 系統的使用者識別碼：

```python
from dataclasses import dataclass

@dataclass
class UserStaticContext:
    # 由 ERP 登入系統或應用程式提供的可信任識別碼
    user_id: str
```

`user_id` 由 ERP 登入系統或應用程式提供

Tool 可以透過 `runtime.context.user_id` 讀取這個值。

我們沒有放在短期記憶中，因為 `user_id` 不會隨對話改變，不需要用 Checkpointer 保存。
### 建立寫入工作備忘錄的 Tool

`save_erp_follow_up()` 接收 ERP 文件類型、文件編號及備忘錄內容，再使用
`runtime.store.put()` 寫入 Memory Store：

```python
from langchain.tools import ToolRuntime, tool

@tool
def save_erp_follow_up(
    document_type: str,
    document_id: str,
    note: str,
    runtime: ToolRuntime[UserStaticContext, None]
) -> str:
    """
    Save a follow-up note for an ERP document.

    Args:
        document_type: The ERP document type, such as purchase_order.
        document_id: The ERP document ID provided by the user.
        note: The follow-up note that the user wants to remember.
        runtime: The ToolRuntime object injected by LangChain.

    Returns:
        A message indicating that the follow-up note was saved.
    """

    assert runtime.store is not None

    # 從 Static Context 取得目前登入者
    user_id = runtime.context.user_id

    # 每一位 User 使用不同的 namespace
    namespace = ("users", user_id, "follow_ups")
    
    # 使用文件類型與文件編號識別一筆工作備忘錄
    key = f"{document_type}-{document_id}"

    runtime.store.put(
        namespace,
        key,
        {
            "document_type": document_type,
            "document_id": document_id,
            "note": note
        }
    )
    current_timestamp = datetime.now().isoformat()
    return f"已保存 {document_id} 的追蹤事項。 ({current_timestamp})"
```

`runtime` 參數由 LangChain 自動注入，不會出現在 LLM 可見的 Tool schema 中。
因此，LLM 只需要從 User message 取得：

- `document_type`
- `document_id`
- `note`

Tool 再從 Context 取得 `user_id`，建立該使用者專屬的 namespace。

`ToolRuntime[ContexT, StateT]` 採用泛型，`ContextT` 是  Context Schema，`StateT` 是 State Schema(自訂的短期憶型態)。

這兩個型別決定了以下屬性的回傳型別：
- `runtime.context` 的型別是 `ContextT`
- `runtime.state` 的型別是 `StateT`

### 建立讀取工作備忘錄的 Tool

`get_erp_follow_ups()` 從 Agent Context 取得目前
登入者 `user_id`，再使用 `runtime.store.search()` 讀取該 namespace 中的所有工作
備忘錄：

```python
@tool
def get_erp_follow_ups(
    runtime: ToolRuntime[UserStaticContext, None]
) -> list[dict]:
    """
    Get the current user's ERP follow-up notes.

    Args:
        runtime: The ToolRuntime object injected by LangChain.

    Returns:
        A list containing the current user's ERP follow-up notes.
    """

    assert runtime.store is not None

    user_id = runtime.context.user_id
    namespace = ("users", user_id, "follow_ups")
		
    # SearchItem
    items = runtime.store.search(namespace)

    return [
        {
            "memory_id": item.key,
            **item.value
        }
        for item in items
    ]
```

`search()` 回傳多個 `Item` 物件。每一個 `Item` 的 `value` 是原本保存的 ERP
工作備忘錄，`key` 則用來識別這筆 memory。

`item.value` 是 JSON-compatible dictionary.
使用 `**` 展開運算子將 `item.value` 的 key-value pair 展開。

例如，Tool 的回傳值可能是：

```python
[
    {
        "memory_id": "purchase_order-B2048",
        "document_type": "purchase_order",
        "document_id": "B2048",
        "note": "等供應商補報價後再送審"
    }
]
```

StructuredTool  會將此回傳值轉換成 `ToolMessage`，再呼叫 LLM 產生適合 User 閱讀的
回覆。

### 建立使用 Memory Store 的 ERP Agent

本例同時使用：

- `InMemorySaver`：保存每一個 thread 的 short-term memory。
- `InMemoryStore`：保存可以跨 thread 讀取的 ERP 工作備忘錄。

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

checkpointer = InMemorySaver()
store = InMemoryStore()

erp_memory_system_prompt = """
You are an ERP assistant.

Follow these rules:
- When the user asks you to remember or track an ERP document, call
  `save_erp_follow_up`.
- Preserve the ERP document ID provided by the user.
- When the user asks for saved ERP follow-up items, call
  `get_erp_follow_ups`.
- Base your answer on the tool result. Do not invent saved follow-up items.
"""

agent = create_agent(
    model=model_name,
    tools=[save_erp_follow_up, get_erp_follow_ups],
    system_prompt=erp_memory_system_prompt,
    checkpointer=checkpointer,
    store=store,
    context_schema=UserStaticContext
)
```

將 `store` 傳給 `create_agent()` 後，兩個 Tool 便能透過 `runtime.store` 取得同一個
`InMemoryStore`。

### Thread 1：寫入 ERP 工作備忘錄

應用程式將目前登入者的 `user_id` 放入 Context，並為這次對話指定
`thread_id="PO-B2048"`：

```python
user_context = UserStaticContext(user_id="user_123")

save_response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "備忘事項：採購單 B2048 "
                    "等供應商補報價後再送審。"
                )
            }
        ]
    },
    context=user_context,
    config={
        "configurable": {
            "thread_id": "PO-B2048"
        }
    }
)

print(save_response["messages"][-1].content)
```

LLM 產生的 tool call request 如下：

```python
{
    "name": "save_erp_follow_up",
    "args": {
        "document_type": "PO",
        "document_id": "B2048",
        "note": "等供應商補報價後再送審"
    }
}
```

Tool 將資料寫入：

```text
namespace = ("users", "user_123", "follow_ups")
key       = "PO-B2048"
```

產生的 Tool Message:

```
ToolMessage(content='已保存 B2048 的追蹤事項。 (2026-08-14T15:34:31.258644)', name='save_erp_follow_up', id='dcb7045a-3943-4e07-b317-9f8ffc32642f', tool_call_id='call_eAebj3LStCpTVzLUo5N4L1Gn'),
```

### Thread 2：讀取 ERP 工作備忘錄

接著，使用不同的 `thread_id` 開始另一段對話：

```python
read_response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "我目前有哪些採購事項需要追蹤？"
            }
        ]
    },
    context=user_context,
    config={
        "configurable": {
            "thread_id": "follow-up-list"
        }
    }
)

print(read_response["messages"][-1].content)
```

`PO-B2048` 與 `follow-up-list` 是兩個不同的 thread，所以兩者的
short-term memory 彼此獨立。但是，兩次 Agent invocation 使用相同的 Store，
而且 Context 中的 `user_id` 都是 `user_123`。

因此，`get_erp_follow_ups()` 可以從相同的 namespace 讀取 Thread 1 保存的
工作備忘錄。Agent 最後可以回覆：

```text
目前可追蹤的採購事項如下：\n\n- 記憶 ID: purchase_order-B2048\n  - 文件類型: purchase_order\n  - 文件編號: B2048\n  - 備忘事項: 採購單 B2048 等供應商補報價後再送審。\n\n需要我對這個追蹤做更新（如標記為已完成、修改備忘內容），或新增其他追蹤項目嗎？'
```

