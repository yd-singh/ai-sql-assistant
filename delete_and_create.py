import os
import time
import json
import logging
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

# --------------------- INIT ---------------------
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
sql_assistant_id = os.environ.get("SQL_ASSISTANT_ID")
qreview_assistant_id = os.environ.get("QREVIEW_ASSISTANT_ID")  # ✅ Add this

# --------------------- SESSION STATE INIT ---------------------
if "qreview_thread" not in st.session_state:
    st.session_state["qreview_thread"] = {"id": client.beta.threads.create().id, "name": "QReview"}

if "qreview_feedback" not in st.session_state:
    st.session_state["qreview_feedback"] = {}  # maps message index to feedback string

# --------------------- GET RESPONSE FROM ASSISTANT ---------------------
def get_assistant_response(thread):
    messages = client.beta.threads.messages.list(thread_id=thread["id"])
    return [{"role": msg.role, "content": msg.content[0].text.value} for msg in reversed(messages.data)]

# --------------------- CHAT UTILS (EXTENDED) ---------------------
def wait_for_run_completion(run, thread, assistant_type="sql", message_index=None):
    with st.spinner("Thinking..."):
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread["id"], run_id=run.id)

            if run.status == "completed":
                # ✅ Handle QReview assistant return (text or SQL)
                if assistant_type == "qreview" and message_index is not None:
                    msgs = client.beta.threads.messages.list(thread_id=thread["id"])
                    assistant_msgs = [m for m in msgs.data if m.role == "assistant"]
                    if assistant_msgs:
                        latest_msg = assistant_msgs[0]
                        content = latest_msg.content[0].text.value.strip()
                        st.session_state["qreview_feedback"][message_index] = content
                break

            elif run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                for call in tool_calls:
                    if call.function.name == "generate_sql_query":
                        sql_args = eval(call.function.arguments)
                        sql_query = sql_args.get("sql", "[No SQL returned]")
                        if assistant_type == "sql":
                            st.session_state["messages"][thread["id"]].append({
                                "role": "assistant",
                                "content": f"```sql\n{sql_query}\n```"
                            })
                        elif assistant_type == "qreview" and message_index is not None:
                            st.session_state["qreview_feedback"][message_index] = f"```sql\n{sql_query}\n```"
                            st.write("📬 QReview (tool return):", sql_query)
                break

            elif run.status == "failed":
                st.error("Assistant failed to respond.")
                return

            time.sleep(1)

def run_qreview_on_sql(sql_text, message_index):
    thread = st.session_state["qreview_thread"]
    client.beta.threads.messages.create(thread_id=thread["id"], role="user", content=sql_text)
    run = client.beta.threads.runs.create(thread_id=thread["id"], assistant_id=qreview_assistant_id)
    wait_for_run_completion(run, thread, assistant_type="qreview", message_index=message_index)

def fix_query_with_feedback(sql_text, feedback_text, original_thread_id):
    # Construct a prompt to SQL Assistant
    prompt = f"""The following SQL query was reviewed, and feedback was provided.

    ### Original SQL:
    ```sql
    {sql_text}
    Feedback:
    {feedback_text}
    Please revise the query to address the feedback above. Return only the corrected SQL."""
    # Send message to the same thread used by SQL Assistant
    client.beta.threads.messages.create(
        thread_id=original_thread_id,
        role="user",
        content=prompt
    )

    # Trigger run on SQL Assistant
    run = client.beta.threads.runs.create(
        thread_id=original_thread_id,
        assistant_id=sql_assistant_id
    )

    # Wait for updated SQL response
    wait_for_run_completion(run, {"id": original_thread_id}, assistant_type="sql")

# --------------------- DISPLAY CHAT (MODIFIED) ---------------------
def display_chat():
    thread_id = st.session_state["current_thread"]["id"]
    for idx, msg in enumerate(st.session_state["messages"].get(thread_id, [])):
        with st.chat_message(msg["role"]):
            content = msg["content"]
            if msg["role"] == "assistant":
                # If content is a SQL code block, show it as code; otherwise, render as markdown.
                if content.strip().startswith("```sql") and content.strip().endswith("```"):
                    sql_code = content.strip().removeprefix("```sql").removesuffix("```").strip()
                    st.code(sql_code, language="sql")
                else:
                    st.markdown(content)
                
                # Always show the Repeat button (smaller button with 🔁) for SQL assistant responses
                if st.button("🔁", key=f"repeat_btn_{idx}"):
                    if content.strip().startswith("```sql") and content.strip().endswith("```"):
                        sql_code = content.strip().removeprefix("```sql").removesuffix("```").strip()
                    else:
                        sql_code = content.strip()
                    run_qreview_on_sql(sql_code, idx)
                
                # Display QReview feedback if available
                if idx in st.session_state["qreview_feedback"]:
                    st.markdown("**QReview Feedback:**")
                    feedback = st.session_state["qreview_feedback"][idx].strip()
                    if feedback.lower() == "true":
                        st.markdown(":white_check_mark: **The query is good. No changes needed.**")
                    elif feedback.startswith("```sql"):
                        revised_sql = feedback.removeprefix("```sql").removesuffix("```").strip()
                        st.code(revised_sql, language="sql")
                    else:
                        st.markdown(feedback)
            else:
                st.markdown(content)

# --------------------- MAIN APP ---------------------
def main():
    # ---------- SESSION STATE INIT (Safe Setup) ----------
    if "threads" not in st.session_state:
        new_thread = {"id": client.beta.threads.create().id, "name": "Untitled"}
        st.session_state["threads"] = [new_thread]
        st.session_state["current_thread"] = new_thread
        st.session_state["messages"] = {new_thread["id"]: []}

    if "messages" not in st.session_state:
        st.session_state["messages"] = {}

    if "qreview_thread" not in st.session_state:
        st.session_state["qreview_thread"] = {"id": client.beta.threads.create().id, "name": "QReview"}

    if "qreview_feedback" not in st.session_state:
        st.session_state["qreview_feedback"] = {}  # maps message index to feedback

    with st.sidebar:
        st.image("logo.png")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("### Chats")
        with col2:
            if st.button("➕", key="plus_button", help="Start a new conversation"):
                new_thread = {"id": client.beta.threads.create().id, "name": "New Conversation"}
                st.session_state["current_thread"] = new_thread
                st.session_state["threads"].append(new_thread)
                st.session_state["messages"][new_thread["id"]] = []

        for idx, thread in enumerate(st.session_state["threads"]):
            if st.button(thread["name"], key=f"thread_{idx}", help="Switch to this thread", use_container_width=True):
                st.session_state["current_thread"] = thread
                if thread["id"] not in st.session_state["messages"]:
                    st.session_state["messages"][thread["id"]] = get_assistant_response(thread)

    # Header
    with st.container():
        st.markdown("""
        <div class="header-card">
            <h2>Hey there!</h2>
            <p style='color: gray; font-size: 0.9em;'>
                I strive to be accurate and reliable, but it’s always wise to 
                <span style="background-color: rgba(255, 255, 150, 0.4); color: #333; font-weight: bold; padding: 2px 6px; border-radius: 4px;">
                Double Check</span> the important stuff—just in case. 🤖
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Chat UI
    display_chat()

    user_input = st.chat_input("Type a message...")
    if user_input:
        if st.session_state["current_thread"]["name"] == "Untitled":
            st.session_state["current_thread"]["name"] = user_input[:30] + ("..." if len(user_input) > 30 else "")

        thread_id = st.session_state["current_thread"]["id"]
        st.session_state["messages"][thread_id].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=sql_assistant_id)

        wait_for_run_completion(run, st.session_state["current_thread"])
        chat_history = get_assistant_response(st.session_state["current_thread"])
        st.session_state["messages"][thread_id] = chat_history

        with st.chat_message("assistant"):
            last_message = chat_history[-1]["content"]
            if last_message.strip().startswith("```sql") and last_message.strip().endswith("```"):
                sql_code = last_message.strip().removeprefix("```sql").removesuffix("```").strip()
                st.code(sql_code, language="sql")
            else:
                st.markdown(last_message)
            # Always show the Repeat button for SQL assistant response
            if st.button("🔁", key="repeat_btn_final"):
                if last_message.strip().startswith("```sql") and last_message.strip().endswith("```"):
                    sql_code = last_message.strip().removeprefix("```sql").removesuffix("```").strip()
                else:
                    sql_code = last_message.strip()
                run_qreview_on_sql(sql_code, len(chat_history)-1)

if __name__ == "__main__":
    main()