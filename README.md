# 🧠 AI Assistant Table Documentation & SQL Validation Framework

This repository provides the documentation format and validation rules used by AI-powered assistants to generate **deterministic, schema-compliant SQL queries**.. It is a chat-based Streamlit application that integrates with the OpenAI Assistants API to help users ask natural language questions and receive deterministically structured SQL queries as responses. Each chat maintains its own context via OpenAI Threads, allowing follow-up queries in the same thread or new chats in separate threads.


It is designed for use with the **OpenAI Assistants API**, supporting a dual-assistant architecture:
- **SQL Assistant**: Generates context-aware SQL based on documented table structures.
- **QReview**: Validates the generated SQL against strict modeling and compliance rules.

---

💬 Core Features

✅ Persistent Threaded Conversations
	•	Each chat in the UI maps to a unique OpenAI thread.
	•	Chat context is preserved, so follow-up messages are understood in relation to earlier messages in the same thread.

➕ Add New Conversation
	•	Clicking the ➕ button starts a new thread (a new conversation).
	•	A new message list is initialized for that thread.

🗂️ Switch Between Conversations
	•	The sidebar lists all threads.
	•	Clicking a thread name switches the context and displays its chat history.

🤖 Assistant Interaction
	•	When the user submits a message:
	1.	The message is sent to OpenAI as part of the current thread.
	2.	A run is triggered on the selected Assistant ID.
	3.	The UI polls the run status until it’s complete.
	4.	Once done, the assistant’s response (SQL or text) is added to the chat.

🧠 Smart UI Behavior
	•	The first user input sets the chat title if it’s still labeled “Untitled”.
	•	SQL responses are displayed in code blocks with syntax highlighting.

---

✅ QReview Instructions (SQL Validator Assistant)

QReview checks for:
	•	Deduplication logic with versioning
	•	Business logic filters (e.g., delete or active flag)
	•	Schema-accurate joins and cardinality
	•	Binary/internal column exclusions
	•	Timezone handling in temporal filters

If SQL is valid:

TRUE  
✅ Follows deduplication logic  
✅ Filters deletes/inactives correctly  
✅ Schema joins & timezone handling are accurate

If SQL has issues:

FALSE  
🚫 Violation 1 – <explanation>  
🚫 Violation 2 – <explanation>  
✅ Suggested Fix:  

-- corrected SQL query here

---

📈 Sequence Diagram (Web Flow)

Here’s a visual breakdown of how the chat system works internally:

sequenceDiagram
    participant User
    participant Streamlit UI
    participant OpenAI API

    User->>Streamlit UI: Enters message
    Streamlit UI->>OpenAI API: Create message (thread_id)
    Streamlit UI->>OpenAI API: Create run (assistant_id, thread_id)
    loop While run not complete
        Streamlit UI->>OpenAI API: Poll run status
    end
    OpenAI API-->>Streamlit UI: Return assistant response
    Streamlit UI-->>User: Display message (text or SQL)

⸻

## 📁 Folder Structure

- `schema_docs/` – Documentation blocks for each schema and table.
- `README.md` – This file. Describes how to use the repo.
- `qreview_instructions.md` – Strict SQL validation checklist for QReview assistant.
- `examples/` – Sample queries and assistant conversations (optional).

🔄 Data Structure
	•	st.session_state["threads"]: List of threads { id, name }.
	•	st.session_state["current_thread"]: Current thread in use.
	•	st.session_state["messages"]: Dictionary mapping thread IDs to message lists.

---

## 📄 Table Documentation Format

Every table follows a structured documentation block that includes:

- **Schema & Table Name**
- **What This Table Contains** – Short description of the table’s purpose
- **Columns** – Names, types, and meanings
- **Excluded Columns** – Internal/binary columns not to be queried
- **Latest Record Logic** – Deduplication strategy using `ROW_NUMBER()`
- **Relationships** – Join keys and cardinality
- **Timezone Notes** – UTC storage and conversion rules
- **Common Queries** – Commonly asked questions, predicates
- **Sample Query Skeleton**

---

### 📋 Example Table Block (Change as per your schema)

```yaml
SCHEMA_NAME: <SCHEMA_NAME>

TABLE_NAME: <TABLE_NAME>

What This Table Contains  
<Brief description of what kind of data is in this table>

Columns  
Column          | Data Type | Description  
----------------|-----------|-------------------------------  
<column_1>      | <TYPE>    | <What the column represents>  
<column_2>      | <TYPE>    | <Description here>  
...

Excluded Columns  
<Change as per your schema>  
<Change as per your schema>  

Latest Record Logic  
<In case of a datalake: Change as per your schema>

Relationships  
<this_table.col> → <other_table.col> (1:1 | 1:N | N:1)  
...

Timezone Considerations  
All timestamps stored in <timezone>.  
<timezone change syntax if applicable>

Sample Query Skeleton

SELECT <column_list>
FROM <tbl>
WHERE <>

Common Queries  
- <Describe common query 1>  
- <Describe common query 2>  

Notes  
<Optional notes: JSON parsing hints, enum tips, caveats>

⸻

🔁 Adding New Tables
	1.	Duplicate the documentation block structure.
	2.	Fill in schema name, table name, and metadata.
	3.	Define excluded columns and deduplication logic.
	4.	Place inside schema_docs/.

⸻
💡 Best Practices
<as per your DB schema and query patterns>
⸻

🧩 Extensibility Ideas
	•	Add thread renaming and deletion.
	•	Integrate QReview validator for SQL feedback before final output.
	•	Allow user authentication for personalized history.
⸻

📦 Files & Assets
	•	logo.png: Displayed in the sidebar.
	•	schema.md: Optional schema file uploaded to OpenAI for Assistant context.

⸻
📬 Contact

For issues, raise a PR or open an issue in the repo.

⸻
