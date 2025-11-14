# MCP Marketplace Listing

## Product Overview

**HRIS MCP Servers** bring enterprise HR data directly into your LLMs and AI applications through the Model Context Protocol standard.

### Key Value Propositions

✅ **Instant HR Data Access** - Query employee profiles, attendance, and policies in natural language  
✅ **Enterprise Integration** - Works with any HRIS system (Honohr, Workday, SAP SuccessFactors, etc.)  
✅ **MCP-Native** - Full compliance with Model Context Protocol specification  
✅ **Production-Ready** - Token management, error handling, comprehensive logging  
✅ **Developer-Friendly** - REST API + MCP servers, detailed documentation, sample code  
✅ **Zero Secrets in Code** - Environment-based configuration, fully secure  

---

## Installation

### Via MCP Marketplace

1. Open your MCP client (Claude Desktop, LM Studio, etc.)
2. Search for "HRIS MCP Servers"
3. Click "Install"
4. Configure with your HRIS credentials

### Manual Installation

```bash
git clone https://github.com/sequelone/hris_mcp_servers.git
cd hris_mcp_servers
pip install -r requirements.txt
python src/smolagent_api.py
```

---

## Use Cases

### 1. HR Chatbot Integration
Integrate HRIS data directly into your HR chatbot for instant employee information queries without manual lookups.

**Example:** "What's the leave balance for John Doe?"  
**Response:** Instant access to leave records, policies, and pending requests.

### 2. LLM-Powered HR Assistant
Build an AI assistant that can answer employee questions about leaves, policies, team structure, and more.

**Example:** "Can I apply for work from home tomorrow?"  
**Response:** Policy-aware response with approval steps.

### 3. Workplace Automation
Automate HR workflows by connecting HRIS to your automation platform through MCP.

**Example:** Auto-notify managers of team leaves, attendance anomalies.

### 4. Intelligence Dashboards
Build data-driven HR dashboards powered by natural language queries.

**Example:** "Show team productivity metrics for Q4"  
**Response:** Attendance-based insights and trends.

### 5. Internal Knowledge Base
Create a searchable HR knowledge base that understands natural language policy queries.

**Example:** "What's the maternity leave policy?"  
**Response:** Detailed policy with conditions and application process.

### 6. Employee Self-Service
Build employee portals that use LLMs to provide personalized HR information.

---

## Supported Platforms

| Platform | Status | Integration |
|----------|--------|-------------|
| Claude Desktop | ✅ Fully Supported | MCP Server |
| ChatGPT | ✅ Fully Supported | REST API / Custom GPT |
| LM Studio | ✅ Fully Supported | MCP Server |
| LangChain | ✅ Fully Supported | Tool Integration |
| LlamaIndex | ✅ Fully Supported | Tool Integration |
| Custom Applications | ✅ Fully Supported | REST API |
| Zapier | 🔄 Coming Soon | Webhook Integration |
| Slack | 🔄 Coming Soon | Slash Commands |

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| 👤 Employee Profiles | 100+ fields including personal, employment, compensation data |
| 👥 Team Management | Real-time attendance, leaves, shifts, regularization |
| 📖 Policy Search | Natural language HR policy queries with intelligent matching |
| 🔐 Token Management | Automatic token generation, caching, and refresh |
| 🤖 AI Formatting | Smart response formatting with markdown and JSON |
| 📊 Comprehensive Data | From basic info to organizational hierarchy and benefits |
| 🛡️ Secure by Default | No hard-coded secrets, environment-based config |
| 🚀 Production Ready | Error handling, logging, monitoring, scalability |

---

## Sample Conversations

### Example 1: Employee Lookup
```
User: "What's Ashish Mittal's current role and manager?"