
# AI Agent 開發課程大綱及講義索引

## Part I：LangChain Agent 開發


### 0: LangChain Agent 開發環境建置與 Python Notebook 使用

[VSCode IDE 開發環境建置與 Python Notebook 使用](setup/setup_vscode.md)

[建立第一個使用 OpenAI API 的 ipynb](setup/first_ipynb_openai_api.md)

### 1：Prompt Engineering 與工具呼叫設計
- System prompt design 
  - [Prompt Engineering](./prompt_engineering_tool_calling/prompt_eng.md)
  - [Prompt Engineering Guided Lab](https://github.com/hychen39/ai_agent_course_code/tree/main/labs/prompt_engineering/phone_service_guided_lab.ipynb)
  - Demo code: https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/prompt-engineer-tool-calls/prompt_engineering.ipynb
  - [補充: Pydantic model 與 Type Hint](./prompt_engineering_tool_calling/pydantic_model.md)
- Tools design and calling  
  - [Tool Calling](./prompt_engineering_tool_calling/tool_calling.md)
    - [Demo](https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/prompt-engineer-tool-calls/tool_call.ipynb)
    - [Guided Lab](https://github.com/hychen39/ai_agent_course_code/tree/main/labs/prompt_engineering/tool_calling_guided_lab.ipynb)
- Model Context Protocol (MCP)  
  - [Model Context Protocol (MCP)](./prompt_engineering_tool_calling/mcp_tool_service.md)
    - [Demo](https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/prompt-engineer-tool-calls/mcp_deepwiki.ipynb)

###  2：Memory 與 Agent 行為動態

- Short-term 
  - [Short-term memory (1)](./memory/memory_1.md)
    - [Demo: Use short-term memory in Agent](https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/memory/memory.ipynb)
    - [Guided Lab](https://github.com/hychen39/ai_agent_course_code/tree/main/labs/memory/short_term_memory_guided_lab_student.ipynb)
  - [Short-term memory (2)](./memory/memory_2.md)
    - [Demo: Customized memory schema](https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/memory/memory_customize.ipynb)
    - [CRM Chatbot with Authorization Check](https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/memory/crm_chatbot_autho_check.ipynb)
    - [Guided Lab](https://github.com/hychen39/ai_agent_course_code/tree/main/labs/memory/custom_state_guided_lab_student.ipynb)
- Long-term memory and Dynamic Agents
  - [Long-term memory (1)](./memory/memory_store_1.md)
    - [Memory Store 的基本操作方法](https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/memory/memory_store_basic_op.ipynb)
    - [實作 1: 儲存及套用使用者的偏好](https://github.com/hychen39/ai_agent_course_code/tree/main/notebooks/memory/memory_store_case_study_1.ipynb)
  - [Long-term memory (2)](./memory/memory_store_2.md)
    - [實作 2: 使用 Tool 保存及讀取 ERP 工作備忘錄](notebooks/memory/memory_store_case_study_1.ipynb)
- 補充: [Python 泛型(Generic)程式設計](./memory/Python_Generics_Introduction.md)

### 3：Agent 協作與人機互動設計
- Multi-Agent systems  
- Human in the Loop  

### 4：Agent 觀測與除錯
- LangSmith Studio  


## Part II：LangGraph Agentic Workflow 設計

### 1. Introduction to LangGraph
- Chain  
- Graph (Node & Edge)  
- Router  
- Agent with memory  

### 2. State and Memory Management
- State schema & reducer  
- Multiple schemas  
- Message trimming / filtering / summarizing (視進度選擇性授課)

### 3. Human in the Loop
- Breakpoints  
- Manual intervention  
- Editing states  
- Dynamic breakpoints  
- Streaming (視進度選擇性授課)

### 4. Agentic Workflow (視進度選擇性授課)
- Parallelization  
- Sub-graph  
- Map-reduce  

### 5. Long-term Memory Engineering (視進度選擇性授課)
- Save & retrieve long-term memory  
- Complex schema (profile)  
- Collection of profiles  
- TrustCall library  
