# 🚀 Quick Start Guide

Get HRIS MCP Servers up and running in 5 minutes!

---

## Step 1: Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Access to your HRIS system
- `pip` (comes with Python)

---

## Step 2: Clone & Setup

```bash
# Clone the repository
git clone https://github.com/sequelone/hris_mcp_servers.git
cd hris_mcp_servers

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your values (use your favorite editor)
nano .env
```

**Minimum required:**
```env
GPT4O_API_KEY=sk-proj-your-api-key-here
BASE_URL=https://honoapp.honohr.com/api
```

---

## Step 4: Start the Server

```bash
python src/smolagent_api.py --host 0.0.0.0 --port 8000
```

You should see:
```
🚀 Starting Smolagent API Server on 0.0.0.0:8000
```

---

## Step 5: Test the API

Open a new terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# Query employee profile
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Get employee profile for SMS0668",
    "emp_code": "SMS0668",
    "domain_url": "honoenterpriseapp.honohr.com",
    "comp_code": "SEQUELONE"
  }'
```

Expected response:
```json
{
  "success": true,
  "data": {
    "query": "Get employee profile for SMS0668",
    "formatted_answer": {
      "has_data": true,
      "formatted_text": "**Employee Code:** SMS0668\n**Name:** Ashish Mittal..."
    }
  },
  "message": "Query processed successfully"
}
```

---

## What's Next?

### 1. Integrate with Claude Desktop

```json
{
  "mcpServers": {
    "hris": {
      "command": "python",
      "args": ["-m", "src.smolagent_api"]
    }
  }
}
```

### 2. Build a Chatbot

```python
import requests

API_URL = "http://localhost:8000/query"

def ask_hr(question, emp_code):
    response = requests.post(API_URL, json={
        "user_query": question,
        "emp_code": emp_code,
        "domain_url": "honoenterpriseapp.honohr.com",
        "comp_code": "SEQUELONE"
    })
    return response.json()["data"]["formatted_answer"]["formatted_text"]

# Usage
print(ask_hr("What's my manager?", "SMS0668"))
```

### 3. Deploy to Production

See [Deployment Guide](docs/deployment.md) for Docker, Kubernetes, and cloud options.

---

## Common Issues

### "Module not found: config"

**Fix:** Make sure you're running from the project root:
```bash
cd hris_mcp_servers
python src/smolagent_api.py
```

### "Authentication failed"

**Check:**
1. Your OpenAI API key is valid
2. Your domain URL is correct
3. Your HRIS credentials have proper access

### "Connection refused"

**Fix:** Make sure the server is running:
```bash
python src/smolagent_api.py --host localhost --port 8000
```

Then in another terminal:
```bash
curl http://localhost:8000/health
```

---

## Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server health check |
| `/query` | POST | Query with AI formatting |
| `/query_raw` | POST | Query without formatting |

---

## Example Queries

### Get Employee Profile
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Show me the profile for employee SMS0668",
    "emp_code": "SMS0668",
    "domain_url": "honoenterpriseapp.honohr.com",
    "comp_code": "SEQUELONE"
  }'
```

### Check Team Attendance
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Show team attendance for today",
    "emp_code": "SMS0668",
    "domain_url": "honoenterpriseapp.honohr.com",
    "comp_code": "SEQUELONE",
    "start_date": "2025-11-14",
    "end_date": "2025-11-14"
  }'
```

### Search HR Policy
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "What is the leave policy?",
    "emp_code": "SMS0668",
    "domain_url": "honoenterpriseapp.honohr.com",
    "comp_code": "SEQUELONE"
  }'
```

---

## Docker Quick Start

No Python installation needed!

```bash
# Build image
docker build -t hris-mcp .

# Run container
docker run -p 8000:8000 \
  -e GPT4O_API_KEY=sk-proj-xxx \
  -e BASE_URL=https://honoapp.honohr.com/api \
  hris-mcp

# Test
curl http://localhost:8000/health
```

---

## Next Steps

1. Read the [full documentation](README.md)
2. Explore the [API reference](docs/api-reference.md)
3. Check out [example integrations](examples/)
4. Join our [community](https://github.com/sequelone/hris_mcp_servers/discussions)

---

## Getting Help

- 📧 **Email:** support@sequelone.com
- 🐛 **Report Issues:** [GitHub Issues](https://github.com/sequelone/hris_mcp_servers/issues)
- 💬 **Discuss:** [GitHub Discussions](https://github.com/sequelone/hris_mcp_servers/discussions)
- 📚 **Docs:** [Full Documentation](README.md)

---

**Happy building! 🎉**
