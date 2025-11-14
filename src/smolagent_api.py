from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Any
import requests
from datetime import datetime, timedelta
import uvicorn
from smolagents import CodeAgent, LiteLLMModel, tool
import logging
import json
import re
from typing import Dict
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HRQueryRequest(BaseModel):
    user_query: str
    emp_code: str
    domain_url: str
    comp_code: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    error: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="HR Assistant API",
    description="AI-powered HR assistant for employee profiles, team management, and policy search",
    version="1.0.0"
)

# Enhanced Profile API Tool with better error handling
@tool
def get_employee_profile(emp_code: str, domain_url: str) -> str:
    """
    Get comprehensive employee profile information including personal details, contact information, 
    employment details, and reporting structure.
    
    Args:
        emp_code: Employee code
        domain_url: Domain URL for authentication
    """
    try:
        response = requests.post(
            settings.HRIS_PROFILE_API,
            json={"emp_code": emp_code, "domain_url": domain_url}
        )
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            return str(result)
        elif response.status_code == 401:
            # Authentication error
            error_msg = "Authentication failed. Please check your credentials and domain URL."
            logger.error(f"❌ Authentication error for {emp_code}: {response.text}")
            return f"Error: {error_msg}"
        elif response.status_code == 400:
            # Bad request error
            error_data = response.json()
            errors = error_data.get('errors', [{}])
            error_msg = errors[0].get('message', 'Authentication required. Please log in.')
            logger.error(f"❌ API call failed: {response.status_code} - {error_msg}")
            return f"Error: {error_msg}"
        else:
            # Other errors
            logger.error(f"❌ API call failed: {response.status_code} - {response.text}")
            return f"Error calling profile API: {response.status_code} - {response.text}"
            
    except Exception as e:
        logger.error(f"❌ Exception in profile API: {str(e)}")
        return f"Error calling profile API: {str(e)}"

# Dynamic Team API Tool
@tool
def get_team_details(emp_code: str, start_date: str, end_date: str, domain_url: str) -> str:
    """
    Get team management details including attendance, leave status, and shift information.
    
    Args:
        emp_code: Manager's employee code
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        domain_url: Domain URL for authentication
    """
    try:
        response = requests.post(
            settings.HRIS_TEAM_API,
            json={
                "emp_code": emp_code,
                "start_date": start_date,
                "end_date": end_date,
                "domain_url": domain_url
            }
        )
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            return str(result)
        elif response.status_code in [401, 400]:
            error_data = response.json()
            errors = error_data.get('errors', [{}])
            error_msg = errors[0].get('message', 'Authentication failed')
            logger.error(f"❌ Authentication error for team {emp_code}: {error_msg}")
            return f"Error: {error_msg}"
        else:
            logger.error(f"❌ Team API call failed: {response.status_code} - {response.text}")
            return f"Error calling team API: {response.status_code} - {response.text}"
            
    except Exception as e:
        logger.error(f"❌ Exception in team API: {str(e)}")
        return f"Error calling team API: {str(e)}"

# Dynamic Policy Search Tool
@tool
def search_policies(query: str, comp_code: str) -> str:
    """
    Search HR policies, FAQs, and documentation using natural language queries.
    
    Args:
        query: Search query about HR policies, FAQs, or documentation
        comp_code: Company code
    """
    try:
        url = settings.POLICY_SEARCH_API
        payload = {
            "comp_code": comp_code,
            "query": query
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return str(result)
        else:
            logger.error(f"❌ Policy search failed: {response.status_code} - {response.text}")
            return f"Error searching policies: {response.status_code} - {response.text}"
            
    except Exception as e:
        logger.error(f"❌ Exception in policy search: {str(e)}")
        return f"Error searching policies: {str(e)}"

# Use centralized metadata from settings (falls back to empty dict)
api_metadata = getattr(settings, "API_METADATA", {})

# Generate comprehensive tool descriptions
def generate_tool_descriptions():
    """Generate detailed tool descriptions with metadata based on actual API structure"""
    
    profile_description = """
    Get comprehensive employee profile information from the HR system.
    
    Available Data Categories:
    
    BASIC INFORMATION:
    - Employee Code, Full Name, First/Middle/Last Name, Title, Employment Status
    
    PERSONAL DETAILS:
    - Date of Birth, Gender, Marital Status, Blood Group, Nationality
    - Father's Name, Spouse's Name, Aadhar Number, PAN Number, Religion, Caste
    
    CONTACT INFORMATION:
    - Mobile Numbers, Official Email, Personal Email
    - Mailing Address (complete address with line1, line2, line3, city, state, PIN)
    - Permanent Address (complete address details)
    
    EMPLOYMENT DETAILS:
    - Company Name, Work Location, Designation, Department
    - Date of Joining, Date of Confirmation, Date of Leaving
    - Confirmation Status, Payroll Status
    
    JOB INFORMATION:
    - Position Title, Function/Department, Business Unit, Role
    - Band Level, Grade Level, Employment Type
    
    REPORTING STRUCTURE:
    - Manager Name and Email, Functional Manager Name and Email
    - Business Unit Head and Email, Sub-Business Head and Email
    - Direct Reportees (list of employee codes)
    
    COMPENSATION:
    - Cost to Company (CTC), Annual CTC
    
    BANK DETAILS:
    - Bank Name, Account Number, IFSC Code
    
    DOCUMENTS:
    - Employee Photo, Aadhar Document, PAN Document, Address Proofs
    
    Sample Employee Data:
    {
        "Emp_Code": "SMS0668",
        "EMP_NAME": "Ashish Mittal",
        "DOB": "1995-04-30",
        "Gender": "Male",
        "MobileNo": "8447037094",
        "OEMailID": "ashish.mittal@hono.ai",
        "COMP_NAME": "SequelOne Solutions Pvt. Ltd.",
        "LOC_NAME": "Gurugram", 
        "DSG_NAME": "Sr. Manager - Software Development",
        "DOJ": "2020-04-01",
        "MNGR_NAME": "Prasanth Raghavulu",
        "DirectReportees": ["INT0084", "INT0091", "INT0093"],
        "CTC": "167440"
    }
    
    Args:
        emp_code: Employee code to fetch profile for
        domain_url: Domain URL for authentication
    """
    
    team_description = """
    Get comprehensive team management details including employee information, daily attendance status, 
    leave information, shift details, and attendance regularization for a specified date range.
    
    Available Data Categories:
    
    TEAM MEMBER INFORMATION:
    - Employee Code, Full Name, Function/Department, Designation, Official Email, Mobile Number
    
    DAILY ATTENDANCE STATUS:
    - Date (YYYY-MM-DD format), Current Status (In Office, Out Of Office, Leave, etc.)
    - Check-in Time (ISO timestamp), Check-out Time (ISO timestamp)
    
    HOLIDAY INFORMATION:
    - Holiday Status (null if not a holiday), Holiday Title/Name
    
    ATTENDANCE REGULARIZATION:
    - Regularization Status (Pending, Approved, Rejected, null if not applicable)
    - Regularized Check-in Time, Regularized Check-out Time, Regularization Remarks
    
    LEAVE INFORMATION:
    - Leave Status (null if not on leave), Leave Type (Casual, Sick, Privileged, etc.)
    - Leave Reason, Leave Nature (Full Day, Half Day, etc.)
    
    ON DUTY INFORMATION:
    - On Duty Status, On Duty Reason, On Duty Type
    
    SHIFT INFORMATION:
    - Scheduled Shift Name/Description, Shift Start Time, Shift End Time
    
    Common Status Values:
    - Attendance Status: "In Office", "Out Of Office", "Leave", "Weekly Off", "Holiday", "Absent"
    - Regularization Status: "Pending", "Approved", "Rejected"
    - Shift Types: "9 AM to 8 PM 9 hours", "General Shift", "Night Shift", "Flexible Shift"
    
    Sample Team Data:
    {
        "Emp_Code": "SMS1142",
        "EMP_NAME": "Shivansh Singhal",
        "FUNCT_NAME": "Engineering", 
        "DSG_NAME": "Software Developer",
        "OEMailID": "shivansh@hono.ai",
        "status": [
            {
                "date": "2025-11-04",
                "status": "In Office",
                "intime": "2025-11-04T08:46:47.000Z",
                "outTime": "2025-11-04T18:02:23.000Z",
                "shift": {
                    "scheduleShift": "9 AM to 8 PM 9 hours",
                    "shiftStart": "09:00:00",
                    "shiftEnd": "20:00:00"
                }
            }
        ]
    }
    
    Sample Team Member with Regularization:
    {
        "Emp_Code": "INT0131", 
        "EMP_NAME": "Harsh Sharma",
        "FUNCT_NAME": "Engineering",
        "DSG_NAME": "Intern",
        "status": [
            {
                "date": "2025-11-04",
                "status": "Out Of Office",
                "attendanceRegularisation": {
                    "arStatus": "Pending",
                    "arInTime": "09:30:00",
                    "arOutTime": "18:30:00",
                    "arRemark": "Testing"
                }
            }
        ]
    }
    
    Args:
        emp_code: Manager's employee code
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        domain_url: Domain URL for authentication
    """
    
    policy_description = """
    Search comprehensive HR policies, FAQs, and documentation from the company knowledge base.
    
    This tool provides accurate and detailed information about:
    - Leave Policies (casual, sick, privileged leaves, eligibility, application process)
    - PF and Advance Withdrawal Processes (while active employment, procedures, limits)
    - Attendance and Work Hours Policies (working hours, late coming, regularization)
    - Work From Home and Remote Work Guidelines (eligibility, approval process)
    - Medical Insurance and Benefits (coverage, claims process)
    - Travel and Expense Policies (reimbursement procedures, limits)
    - Code of Conduct and Compliance (company rules, disciplinary procedures)
    - Recruitment and Onboarding Procedures (hiring process, documentation)
    - Performance Management Guidelines (appraisal process, feedback mechanisms)
    - Compensation and Benefits (salary structure, bonuses, incentives)
    - Employee Separation Processes (resignation, exit formalities)
    
    Sample Policy Search:
    Query: "PF advance withdrawal process active"
    Answer: Detailed step-by-step procedure for PF advance withdrawal while employed including EPFO website process, form submission, and eligibility criteria...
    
    Args:
        query: Search query about HR policies, FAQs, or documentation
        comp_code: Company code
    """
    
    # Update tool descriptions
    get_employee_profile.description = profile_description
    get_team_details.description = team_description  
    search_policies.description = policy_description

# Initialize tool descriptions
generate_tool_descriptions()

# Model configuration loaded from settings
models = {}
for _name, _cfg in settings.LLM_MODELS.items():
    try:
        _kwargs = {}
        if _cfg.get("model_id") is not None:
            _kwargs["model_id"] = _cfg.get("model_id")
        if _cfg.get("api_key") is not None:
            _kwargs["api_key"] = _cfg.get("api_key")
        if _cfg.get("api_base") is not None:
            _kwargs["api_base"] = _cfg.get("api_base")
        if _cfg.get("completion_kwargs") is not None:
            _kwargs["completion_kwargs"] = _cfg.get("completion_kwargs")
        models[_name] = LiteLLMModel(**_kwargs)
    except Exception as e:
        logger.warning(f"Failed to initialize model {_name}: {e}")

def _try_extract_json(text: str):
    """Attempt to extract a JSON object from free-text output."""
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"(\{(?:[^{}]|(?1))*\})", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    match_arr = re.search(r"(\[(?:[^\[\]]|(?1))*\])", text, flags=re.DOTALL)
    if match_arr:
        try:
            return json.loads(match_arr.group(1))
        except Exception:
            pass
    raise ValueError("No JSON found in text")


def _clean_markdown_headings(text: str) -> str:
    """Remove markdown headings like ###, ##, # but keep bold, lists, tables."""
    if not text:
        return text
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n#{1,6}\s*", "\n", text)
    return text.strip()


def format_response_with_gpt(user_query: str, raw_response: str) -> Dict[str, object]:
    """
    Format raw response into clean markdown using GPT.
    Returns dict: { "has_data": bool, "formatted_text": str }
    """
    empties = [None, "", "null", "None", "[]", "{}"]
    if (isinstance(raw_response, str) and raw_response.strip() in empties) or raw_response is None:
        return {
            "has_data": False,
            "formatted_text": "**Information not available.**\n\nNo data was returned by the source."
        }

    instruction = f"""
You are an expert formatter that MUST return valid JSON ONLY (no commentary).
Given the user's query and raw response, decide if the response has meaningful information.

Return EXACTLY:
{{
  "has_data": true|false,
  "formatted_text": "<markdown-formatted-string>"
}}

Rules:
- has_data = true if the raw response has valid, useful information.
- has_data = false if it is empty, null, error text, or placeholders.
- formatted_text must be concise and readable markdown (no headings like ###, ##, #).
  Use **bold**, *italic*, bullet points (-), and tables (|column|) only.
- If has_data=false, set formatted_text to "**Information not available.**"
- Do not invent or guess data.
- Always output valid JSON only.

User Query:
\"\"\"{user_query}\"\"\"

Raw Response:
\"\"\"{raw_response}\"\"\"
"""

    payload = {
        "comp_code": "self_query",
        "usecase": "agents",
        "model": settings.FORMATTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a strict JSON-producing formatter. Return only JSON as specified."},
            {"role": "user", "content": instruction}
        ],
        "temperature": 0
    }

    try:
        resp = requests.post(settings.FORMATTER_ENDPOINT, json=payload, timeout=30)
    except requests.RequestException as e:
        logger.error("Request to GPT endpoint failed: %s", e)
        return {
            "has_data": False,
            "formatted_text": "**Information not available.**\n\nNetwork error while formatting."
        }

    if resp.status_code != 200:
        logger.error("GPT endpoint returned %s: %s", resp.status_code, resp.text[:400])
        return {
            "has_data": False,
            "formatted_text": "**Information not available.**\n\nFormatting service error."
        }

    try:
        resp_json = resp.json()
    except Exception:
        text = resp.text or ""
        try:
            resp_obj = _try_extract_json(text)
        except Exception:
            return {
                "has_data": False,
                "formatted_text": "**Information not available.**\n\nUnparseable response from formatter."
            }
    else:
        content = (
            resp_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        ) or resp.text or ""
        try:
            resp_obj = _try_extract_json(content)
        except Exception:
            if len(content.strip()) > 20:
                return {"has_data": True, "formatted_text": _clean_markdown_headings(content)}
            return {"has_data": False, "formatted_text": "**Information not available.**"}

    if not isinstance(resp_obj, dict):
        return {"has_data": False, "formatted_text": "**Information not available.**"}

    has_data = bool(resp_obj.get("has_data", False))
    formatted_text = _clean_markdown_headings(resp_obj.get("formatted_text", ""))

    if not formatted_text:
        formatted_text = "**Information not available.**" if not has_data else "**Data available but formatting incomplete.**"

    return {"has_data": has_data, "formatted_text": formatted_text}

# Fixed RawResponseHRAgent with proper docstrings
class RawResponseHRAgent:
    def __init__(self, emp_code: str, domain_url: str, comp_code: str, start_date: str = None, end_date: str = None):
        self.emp_code = emp_code
        self.domain_url = domain_url
        self.start_date = start_date or datetime.now().strftime("%Y-%m-%d")
        self.end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        self.comp_code = comp_code
        
        # Store raw responses
        self.raw_responses = []
        
        self.tools = [
            self.create_profile_tool(),
            self.create_team_tool(),
            self.create_policy_tool()
        ]
        
        self.agent = CodeAgent(
            tools=self.tools,
            model=models["gpt4o"],
            max_steps=6,
            additional_authorized_imports=['json']
        )
    
    def create_profile_tool(self):
        @tool
        def profile_tool(query: str) -> str:
            """
            Get comprehensive employee profile information including personal details, contact information, 
            employment details, and reporting structure.
            
            Args:
                query: Natural language query about employee profile
            """
            response = get_employee_profile(self.emp_code, self.domain_url)
            self.raw_responses.append({
                "tool": "profile",
                "query": query,
                "response": response
            })
            return response
        return profile_tool
    
    def create_team_tool(self):
        @tool
        def team_tool(query: str) -> str:
            """
            Get team management details including attendance, leave status, and shift information.
            
            Args:
                query: Natural language query about team management
            """
            response = get_team_details(self.emp_code, self.start_date, self.end_date, self.domain_url)
            self.raw_responses.append({
                "tool": "team", 
                "query": query,
                "response": response
            })
            return response
        return team_tool
    
    def create_policy_tool(self):
        @tool
        def policy_tool(query: str) -> str:
            """
            Search HR policies, FAQs, and documentation using natural language queries.
            
            Args:
                query: Search query about HR policies, FAQs, or documentation
            """
            response = search_policies(query, self.comp_code)
            self.raw_responses.append({
                "tool": "policy",
                "query": query,
                "response": response
            })
            return response
        return policy_tool
    
    # Update the agent's run method to use direct formatting for policy responses
    def run(self, user_query: str) -> dict:
        """Run the agent and return both final answer and raw responses"""
        final_answer = self.agent.run(user_query)
        
        # Check if last tool used was policy tool
        last_tool_used = None
        if self.raw_responses:
            last_tool_used = self.raw_responses[-1].get("tool")
        
        # Apply appropriate formatting based on tool type
        if last_tool_used == "policy":
            # For policy tool, use direct formatting to preserve exact content
            policy_response = self.raw_responses[-1]["response"] if self.raw_responses else final_answer
            formatted_answer = policy_response
        else:
            # For other tools, use GPT formatting
            formatted_answer = format_response_with_gpt(user_query, final_answer)
        
        return {
            "final_answer": final_answer,
            "formatted_answer": formatted_answer,
            "raw_responses": self.raw_responses,
            "success": True
        }
            
# Helper function to auto-detect date range from query
def detect_date_range(query: str) -> tuple:
    """Auto-detect start_date and end_date from natural language query"""
    query_lower = query.lower()
    today = datetime.now()
    
    # Default to current date
    start_date = today.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    # Detect date patterns
    if "today" in query_lower:
        start_date = today.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    
    elif "yesterday" in query_lower:
        yesterday = today - timedelta(days=1)
        start_date = yesterday.strftime("%Y-%m-%d")
        end_date = yesterday.strftime("%Y-%m-%d")
    
    elif "this week" in query_lower:
        start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    
    elif "last week" in query_lower:
        last_week_start = today - timedelta(days=today.weekday() + 7)
        last_week_end = last_week_start + timedelta(days=6)
        start_date = last_week_start.strftime("%Y-%m-%d")
        end_date = last_week_end.strftime("%Y-%m-%d")
    
    elif "this month" in query_lower:
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    
    elif "last month" in query_lower:
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        start_date = last_day_previous_month.replace(day=1).strftime("%Y-%m-%d")
        end_date = last_day_previous_month.strftime("%Y-%m-%d")
    
    return start_date, end_date


# FastAPI Routes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/query", response_model=APIResponse)
async def process_hr_query(request: HRQueryRequest):
    """Process natural language HR queries using AI agent with smart formatting"""
    try:
        start_date = request.start_date
        end_date = request.end_date
        
        if start_date is None or end_date is None:
            detected_start, detected_end = detect_date_range(request.user_query)
            start_date = start_date or detected_start
            end_date = end_date or detected_end
        
        logger.info(f"🔧 Processing Query:")
        logger.info(f"  Employee: {request.emp_code}")
        logger.info(f"  Domain: {request.domain_url}")
        logger.info(f"  Company: {request.comp_code}")
        logger.info(f"  Period: {start_date} to {end_date}")
        logger.info(f"🔍 Query: {request.user_query}")
        
        # Create and run agent
        agent = RawResponseHRAgent(request.emp_code, request.domain_url, request.comp_code, start_date, end_date)
        result = agent.run(request.user_query)
        
        # Determine overall success based on agent result
        success = result.get("success", True)
        message = "Query processed successfully" if success else "Response not found or contains errors"
        
        return APIResponse(
            success=success,
            data={
                "query": request.user_query,
                "final_answer": result["final_answer"],
                "formatted_answer": result["formatted_answer"],
                "raw_responses": result["raw_responses"],
                "last_tool_used": result["raw_responses"][-1].get("tool") if result["raw_responses"] else None,
                "parameters": {
                    "emp_code": request.emp_code,
                    "domain_url": request.domain_url,
                    "comp_code": request.comp_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            },
            message=message
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to process query",
            error=str(e)
        )

@app.post("/query_raw", response_model=APIResponse)
async def process_hr_query_raw(request: HRQueryRequest):
    """Process query and return raw responses only (no GPT formatting)"""
    try:
        start_date = request.start_date
        end_date = request.end_date
        
        if start_date is None or end_date is None:
            detected_start, detected_end = detect_date_range(request.user_query)
            start_date = start_date or detected_start
            end_date = end_date or detected_end
        
        # Create agent but don't apply GPT formatting
        agent = RawResponseHRAgent(request.emp_code, request.domain_url, request.comp_code, start_date, end_date)
        result = agent.run(request.user_query)
        
        success = result.get("success", True)
        message = "Query processed successfully" if success else "Response not found or contains errors"
        
        return APIResponse(
            success=success,
            data={
                "query": request.user_query,
                "final_answer": result["final_answer"],
                "raw_responses": result["raw_responses"],
                "last_tool_used": result["raw_responses"][-1].get("tool") if result["raw_responses"] else None,
                "parameters": {
                    "emp_code": request.emp_code,
                    "domain_url": request.domain_url,
                    "comp_code": request.comp_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            },
            message=message
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to process query",
            error=str(e)
        )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smol Agent API Pipeline")
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    
    args = parser.parse_args()

    # Run API server
    print(f"🚀 Starting Smolagent API Server on {args.host}:{args.port}")
    uvicorn.run(
        "smolagent_api:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info"
    )