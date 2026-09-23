
# AI Agent 開發課程大綱及講義索引

## Part I：LangChain Agent 開發

\$code_repo = https://github.com/hychen39/ai_agent_course_code/tree/main

### 0: LangChain Agent 開發環境建置與 Python Notebook 使用

[VSCode IDE 開發環境建置與 Python Notebook 使用](setup/setup_vscode.md)

[建立第一個使用 OpenAI API 的 ipynb](setup/first_ipynb_openai_api.md)

### 1：Prompt Engineering 與工具呼叫設計
- System prompt design 
  - [Prompt Engineering](./prompt_engineering_tool_calling/prompt_eng.md)
  - [Prompt Engineering Guided Lab](\$code_repo/labs/prompt_engineering/phone_service_guided_lab.ipynb)
  - Demo code: \$code_repo/notebooks/prompt-engineer-tool-calls/prompt_engineering.ipynb
  - [補充: Pydantic model 與 Type Hint](./prompt_engineering_tool_calling/pydantic_model.md)
- Tools design and calling  
- Model Context Protocol (MCP)  

###  2：Memory 與 Agent 行為動態

- Short-term & Long-term memory  
- Dynamic Agents  

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
