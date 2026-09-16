# 課程名稱  

AI Agent 應用程式開發 (AI Agent Application Development)

## 授課教師

[資管系 陳宏益](https://hychen39.gitbook.io/cv)

hychen39@gm.cyut.edu.tw

04-23323000 ext. 4556

### 課程目標

培養學生:
- 開發 AI Agent 應用程式，協助企業解決問題並創造價值，
- 並具備可設計、可控制、可驗證之 Agent 系統工程能力。

教授 LangChain 與 LangGraph 核心框架，包含以下的知識、技能、態度:

知識:
- LLM 與 Agent 基礎: LLM 運作原理與限制（context window、hallucination）、 Prompt engineering 原則、Tool calling 機制、ReAct 與 Agentic Workflow 概念、Short-term / Long-term Memory 設計原則、Human-in-the-loop 設計原則
- LangChain 基礎架構: Chain vs Agent、Tools、Model Context Protocol (MCP)、Multi-agent 協作模型、LangSmith 觀測與追蹤
- LangGraph 基礎架構: Graph-based orchestration、Node、Edge、Router、State schema 與 state reducer、breakpoints、interrupts、long-term memory and profiles

技能:

- 開發具 tool-calling 能力的 agent
- 開發具 short-term 與 long-term memory 的 agent 程式
- 開發 LangGraph agentic workflow 程式
- 在 Agent 或 LangGraph workflow 加入 human-in-the-loop 
- 使用 LangSmith 進行 trace 與 debug

態度:

- 對 AI 輸出保持批判性思考
- 對自動化決策保持審慎態度
- 重視可觀察性與可驗證性
- 強調結構化設計，而非 prompt 拼湊
- 願意進行迭代優化與系統改進
- 對工程品質與系統可靠性負責

### 授課對象  

大四學生（具備 Python 程式設計與基礎軟體開發能力）


## 重要提醒

- 學生需要自行準備 LLM 模型 API key，課程不提供任何 API key。
- 學生需自行負擔 LLM 模型 API key 的費用，課程不提供任何補助。

## 課程涵蓋主題

- Part I：LangChain Agent 開發
- Part II：LangGraph Agentic Workflow 設計

[主題與課程講義索引](topic_notes_map.md)

## 教材

[自編講義 GitHub](Github url TBD)

## 參考資料

官方文件:
- [LangChain - Docs by LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/overview)

LangChain Academy 線上課程:
- [Foundation: Introduction to LangChain - Python | LangChain Academy](https://academy.langchain.com/courses/foundation-introduction-to-langchain-python) 
- [Foundation: Introduction to LangGraph - Python | LangChain Academy](https://academy.langchain.com/courses/intro-to-langgraph)
- [Quickstart: LangSmith Essentials](https://academy.langchain.com/courses/quickstart-langsmith-essentials)

書籍:
- LangChain 學習手冊｜使用 LangChain 與 LangGraph 建構 AI 與 LLM 應用程式 (Learning LangChain: Building AI and LLM Applications with LangChain and LangGraph) 作者：Mayo Oshin, Nuno Campos 出版年(西元)： 出版社：歐萊禮
[天瓏網路書店](https://www.tenlong.com.tw/products/9786264251815?list_name=srh)

- 從 AI Agent 到多代理人系統設計｜架構規劃與應用開發 (Building Applications with AI Agents: Designing and Implementing Multiagent Systems) 作者：Michael Albada 著 黃銘偉 譯 出版年(西元)： 出版社：歐萊禮
[天瓏網路書店 ](https://www.tenlong.com.tw/products/9786264253765?list_name=srh)


## 評分方式

心得與學習報告 30% 

期中技術報告 35%

期未技術或專題實作報告 35%

## 作業要求

### 心得與學習報告

上課隔週後，繳交心得與學習報告，內容包含：
- 上週學習心得與收穫
- 學習工作記錄

手寫 A4 紙一張，不可電腦打字
拍照後上傳至 TranClass 指定作業區

不接受遲交
- 若有特殊情況，請於上課前事先 email 告知授課教師
- 最多延遲一週，逾期不予受理

### 期中、期末技術報告

2 人一組為原則

研究課程內容未涵蓋之 LangChain 與 LangGraph 技術

針對某項功能與技術報告工作原理、使用時機、程式碼範例等。
可報告現有的 LangChain 與 LangGraph 範例程式碼，不需要自行撰寫程式碼。

除書面報告外(word), 每組皆要上台口頭報告。

### 期末專題報告

期末也可接受實作型專題報告

專題必須使用到 LangChain 或 LangGraph 技術

報告評份其中一項和 LangChain 或 LangGraph 技術使用的深度與廣度有關，使用越多、越深入，分數越高。

若要做「專題實作報告」，請於期中前 email 專題題目與簡介給授課教師，經同意後才可進行專題實作報告。


## 技術報告題材建議

- LangChain Academy 線上課程上的實作專案
  - 如 [https://academy.langchain.com/courses/take/intro-to-langgraph/lessons/58239934-lesson-1-parallelization](https://academy.langchain.com/courses/take/intro-to-langgraph/lessons/58239934-lesson-1-parallelization)
- [Foundation: Introduction to Deep Agents](https://academy.langchain.com/courses/take/foundation-introduction-to-deepagents/lessons/75788587-welcome)
- 官方網站其它文件或程式碼範例