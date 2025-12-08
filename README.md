# 🤖 Amit Bot – Personal AI Assistant

Welcome to **Amit Bot**, an agentic AI-powered personal assistant built using **OpenAI**, **Streamlit**, and **custom agent tools**.  
This bot represents **Amit Prajapati**, a Machine Learning Engineer specializing in LLMs, data engineering, and intelligent automation.

Amit Bot can:

- 💬 Answer questions about Amit’s background, experience, and skills  
- 🤖 Behave like a conversational AI twin based on Amit’s resume  
- 📚 Retrieve contextual info from Amit’s PDF resume  
- ✉️ Detect emails in messages and automatically send follow-up invitations  
- 🧠 Maintain conversation memory within the session  
- ⚙️ Use a custom multi-agent system (Amit_Agent → Email_Writer agent)

---

## 🚀 Features

### **🧠 Agentic Chat Model**
The main “Amit_Agent”:

- Responds using Amit’s real background & resume (parsed from PDF)
- Understands context and maintains conversation history
- Detects when a user includes an email address
- Initiates agent-to-agent handoff to Email_Writer

---

### **✉️ Automated Email Sending**
A custom tool (`send_email`) enables:

- Composing follow-up emails  
- Sending professional messages directly using **SendGrid API**  
- Confirming email delivery back to the user  

All at runtime through LLM-driven automation.

---

### **📄 PDF Resume Parsing**
Amit Bot loads and extracts text from:

