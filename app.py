import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI
from agents import Agent, Runner, trace, function_tool
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------------------------------
# LOAD RESUME TEXT
# -------------------------------------------------
def load_resume_text():
    reader = PdfReader("AMIT_PRAJAPATI.pdf")
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

linkedin = load_resume_text()

# -------------------------------------------------
# SEND EMAIL TOOL
# -------------------------------------------------
@function_tool
def send_email(to_email: str, subject: str, body: str):
    message = Mail(
        from_email="aprajapati@wpi.edu",
        to_emails=to_email,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return {
            "status": "sent",
            "code": response.status_code,
            "response_body": str(response.body)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

email_writer_instructions = """
You write short, concise, and professional follow-up emails.

When a user provides an email address, write a professional follow-up email:
- Thank them for connecting
- Ask for a suitable time to talk
- Then automatically send the email using send_email()

After sending, tell the user: "The email has been sent successfully!"
"""

Email_Writer = Agent(
    name="Email_Writer",
    instructions=email_writer_instructions,
    tools=[send_email],
    model="gpt-4o-mini",
    handoff_description="writing and sending follow-up emails"
)

# -------------------------------------------------
# MAIN AGENT
# -------------------------------------------------
name = "Amit Prajapati"

system_prompt = f"""
You are acting as {name} on his personal website.

Your job:
- Answer professionally using Amit's resume below.
- If the user includes an email (one '@' + domain, no spaces):
    → HANDOFF to Email_Writer automatically.
- After sending ONE email, do NOT send another.
- Stay helpful, polite, and confident.

RESUME CONTENT:
{linkedin}
"""

Amit_Agent = Agent(
    name="Amit_Agent",
    instructions=system_prompt,
    handoffs=[Email_Writer],
    model="gpt-4o"
)

# -------------------------------------------------
# ASYNC → SYNC WRAPPER
# -------------------------------------------------
async def chat_async(message, history):
    with trace("Automated_chatter"):
        prompt = "\n".join(
            f"{m['role']}: {m['content']}" for m in history + [{"role": "user", "content": message}]
        )
        result = await Runner.run(Amit_Agent, prompt)
        return result.final_output

def chat(message, history):
    return asyncio.run(chat_async(message, history))


# -------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------
st.set_page_config(page_title="Amit Prajapati", page_icon="🤖", layout="wide")

page = st.sidebar.radio("Navigation", ["Home", "Chat With Amit AI"])

# -------------------- HOME PAGE --------------------
if page == "Home":
    st.title("👋 Hi, I'm Amit Prajapati")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("Amit.png", width=250)
    with col2:
        st.subheader("Machine Learning Engineer | Data Scientist | AI Builder")
        st.write("""
        Welcome to my AI-powered portfolio.

        - 🧠 Machine Learning Engineer  
        - ⚙️ End-to-end Data Pipelines  
        - 🤖 LLMs, Agents, Automation  
        - ☁️ AWS | Azure | MLOps  

        Use the sidebar to chat with my AI twin!
        """)

# -------------------- CHAT PAGE --------------------
if page == "Chat With Amit AI":
    st.title("🤖 Chat With Amit AI")
    st.write("Ask me anything about my background, skills, or experience!")

    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = []

    # Display messages like ChatGPT
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

    # ChatGPT-style input at bottom
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        bot_reply = chat(user_input, st.session_state.history)
        st.session_state.history.append({"role": "assistant", "content": bot_reply})

        st.rerun()
