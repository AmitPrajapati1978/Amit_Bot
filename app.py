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
You write professional, well-formatted follow-up emails for Amit Prajapati.

When a user provides an email address, compose a professional follow-up email with:

Subject: "Follow-Up: Discussion Opportunity"

Body (HTML formatted):
- Greeting with recipient's name (if known, otherwise "Hi there")
- Thank them for connecting
- Express interest in discussion
- Ask for their availability
- Professional closing
- Sign with "Best regards, Amit Prajapati"

Format the email body as clean HTML with proper spacing and professional styling.
After composing, automatically send using send_email().
Confirm to user: "✅ Email sent successfully to [email]"
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
You are acting as {name} on his personal AI-powered portfolio website.

Your responsibilities:
- Answer questions professionally using Amit's resume information below
- Be conversational, friendly, and confident
- If user provides an email address (contains '@' and domain):
    → Automatically HANDOFF to Email_Writer to send a follow-up
- After ONE email is sent, do NOT send duplicates
- Provide specific details from the resume when relevant

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
# STREAMLIT UI WITH CUSTOM STYLING
# -------------------------------------------------
st.set_page_config(
    page_title="Amit Prajapati - AI Portfolio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling 
st.markdown("""
<style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Card styling */
    .stApp {
        background: rgba(255, 255, 255, 0.95);
    }
    
    /* Headers */
    h1 {
        color: #1e3a8a;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #3730a3;
    }
    
    /* Sidebar */
    python[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f3f4f6 0%, #e5e7eb 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #f8fafc;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Profile section */
    .profile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    /* Skills badges */
    .skill-badge {
        display: inline-block;
        background: #e0e7ff;
        color: #3730a3;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-weight: 500;
        font-size: 14px;
    }
    
    /* Chat input */
    .stChatInput {
        border-radius: 25px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio("", ["🏠 Home", "💬 Chat With Amit AI"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📫 Connect")
    st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/amit-prajapati-2210261b5/)")
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/AmitPrajapati1978)")
    st.markdown("[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:aprajapati@wpi.edu)")

# -------------------- HOME PAGE --------------------
if page == "🏠 Home":
    # Hero Section
    st.markdown("""
    <div class="profile-header">
        <h1 style="color: white; margin: 0;">👋 Hi, I'm Amit Prajapati</h1>
        <p style="font-size: 20px; margin-top: 10px; color: #e0e7ff;">
            Machine Learning Engineer | Data Scientist | AI Builder
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("Amit.png", width=280, use_column_width=True)
        
    with col2:
        st.markdown("### 🚀 About Me")
        st.write("""
        Welcome to my AI-powered portfolio! I'm passionate about building intelligent 
        systems that solve real-world problems.
        """)
        
        st.markdown("### 💼 What I Do")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("🧠 **Machine Learning**")
            st.write("Building ML models & pipelines")
            
            st.markdown("🤖 **AI Agents**")
            st.write("LLMs, automation & intelligence")
            
        with col_b:
            st.markdown("📊 **Data Engineering**")
            st.write("ETL, pipelines & analytics")
            
            st.markdown("☁️ **Cloud & MLOps**")
            st.write("AWS, Azure & deployment")
    
    # Skills Section
    st.markdown("---")
    st.markdown("### 🛠️ Technical Skills")
    st.markdown("""
    <div>
        <span class="skill-badge">Python</span>
        <span class="skill-badge">Machine Learning</span>
        <span class="skill-badge">Deep Learning</span>
        <span class="skill-badge">NLP</span>
        <span class="skill-badge">LLMs</span>
        <span class="skill-badge">AWS</span>
        <span class="skill-badge">Azure</span>
        <span class="skill-badge">MLOps</span>
        <span class="skill-badge">Data Engineering</span>
        <span class="skill-badge">SQL</span>
        <span class="skill-badge">PyTorch</span>
        <span class="skill-badge">TensorFlow</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 **Try the Chat**: Use the sidebar to chat with my AI twin and learn more about my experience!")

# -------------------- CHAT PAGE --------------------
elif page == "💬 Chat With Amit AI":
    st.markdown("""
    <div class="profile-header">
        <h1 style="color: white; margin: 0;">🤖 Chat With Amit AI</h1>
        <p style="color: #e0e7ff; margin-top: 10px;">
            Ask me anything about Amit's background, skills, experience, or projects!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick prompts
    st.markdown("### 💭 Quick Questions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📚 Tell me about your experience"):
            st.session_state.quick_prompt = "Tell me about your work experience"
    with col2:
        if st.button("🛠️ What are your skills?"):
            st.session_state.quick_prompt = "What are your technical skills?"
    with col3:
        if st.button("🎯 Recent projects?"):
            st.session_state.quick_prompt = "What are your recent projects?"
    
    st.markdown("---")
    
    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = []
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
    
    # Handle quick prompts
    if "quick_prompt" in st.session_state:
        user_input = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        
        st.session_state.history.append({"role": "user", "content": user_input})
        bot_reply = chat(user_input, st.session_state.history)
        st.session_state.history.append({"role": "assistant", "content": bot_reply})
        st.rerun()
    
    # Chat input at bottom
    user_input = st.chat_input("💬 Type your message here...")
    
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        
        with st.spinner("🤔 Thinking..."):
            bot_reply = chat(user_input, st.session_state.history)
        
        st.session_state.history.append({"role": "assistant", "content": bot_reply})
        st.rerun()
    
    # Clear chat button
    if st.session_state.history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.history = []
            st.rerun()
