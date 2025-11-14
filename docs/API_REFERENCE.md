# API Reference

Complete API documentation for HRIS MCP Servers.

---

## Base URL

```
http://localhost:8000
```

---

## Authentication

All requests require the following parameters in the request body:

- `emp_code` (string, required) - Employee code
- `domain_url` (string, required) - HRIS domain URL
- `comp_code` (string, required) - Company code

---

## Endpoints

### Health Check

Check if the server is running and healthy.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T10:30:45.123456"
}
```

**Status Codes:**
- `200` - Server is healthy

---

### Query with AI Formatting

Process an HR query with intelligent AI-powered response formatting.

**Request:**
```http
POST /query
Content-Type: application/json

{
  "user_query": "What is John's job title?",
  "emp_code": "SMS0668",
  "domain_url": "honoenterpriseapp.honohr.com",
  "comp_code": "SEQUELONE",
  "start_date": "2025-11-04",
  "end_date": "2025-11-14"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_query` | string | ✅ Yes | Natural language query about HR data |
| `emp_code` | string | ✅ Yes | Employee code (context for the query) |
| `domain_url` | string | ✅ Yes | HRIS domain URL |
| `comp_code` | string | ✅ Yes | Company code |
| `start_date` | string | ❌ No | Start date (YYYY-MM-DD, auto-detected if not provided) |
| `end_date` | string | ❌ No | End date (YYYY-MM-DD, auto-detected if not provided) |

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "What is John's job title?",
    "final_answer": "Employee SMS0668 is Ashish Mittal with job title Sr. Manager - Software Development",
    "formatted_answer": {
      "has_data": true,
      "formatted_text": "**Employee:** Ashish Mittal\n**Job Title:** Sr. Manager - Software Development\n**Department:** Engineering"
    },
    "raw_responses": [
      {
        "tool": "profile",
        "query": "What is John's job title?",
        "response": "{...}"
      }
    ],
    "last_tool_used": "profile",
    "parameters": {
      "emp_code": "SMS0668",
      "domain_url": "honoenterpriseapp.honohr.com",
      "comp_code": "SEQUELONE",
      "start_date": "2025-11-14",
      "end_date": "2025-11-14"
    }
  },
  "message": "Query processed successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Authentication failed
- `500` - Server error

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the query was processed successfully |
| `data.query` | string | The original user query |
| `data.final_answer` | string | Raw response from the AI agent |
| `data.formatted_answer` | object | AI-formatted response with `has_data` and `formatted_text` |
| `data.raw_responses` | array | Raw responses from each tool used |
| `data.last_tool_used` | string | Last tool used (profile, team, or policy) |
| `data.parameters` | object | Parameters used for the query |
| `message` | string | Human-readable status message |
| `error` | string | Error message if `success` is false |

---

### Query Raw (No Formatting)

Process an HR query and return raw, unformatted responses.

**Request:**
```http
POST /query_raw
Content-Type: application/json

{
  "user_query": "Get profile for SMS0668",
  "emp_code": "SMS0668",
  "domain_url": "honoenterpriseapp.honohr.com",
  "comp_code": "SEQUELONE"
}
```

**Parameters:** Same as `/query`

**Response:** Same structure as `/query` but without AI formatting

---

## Tools

### 1. Employee Profile Tool

Returns comprehensive employee information.

**Query Examples:**
- "Get profile for SMS0668"
- "What's John's email and phone?"
- "Show direct reportees for SMS0668"
- "What's the CTC for John?"

**Available Fields:**

#### Basic Information
- `Emp_Code` - Employee code
- `EMP_NAME` - Full name
- `Emp_FName`, `Emp_MName`, `Emp_LName` - First, middle, last name
- `Status_Code`, `STATUS_NAME` - Employment status

#### Personal Details
- `DOB` - Date of birth
- `Gender` - Gender
- `Marital_Status` - Marital status
- `BloodGroup_Name` - Blood group
- `NATIONALITY_NAME` - Nationality
- `FatherName`, `spouseName` - Family information
- `AadharNo`, `PANNo` - Identity documents

#### Contact Information
- `MobileNo`, `OEMailID`, `PEMailID` - Contact details
- `MailingAddress`, `MAddr1-3`, `MCity`, `MState`, `MPin` - Mailing address
- `PAddr1-3`, `PCity`, `PState`, `PPin` - Permanent address

#### Employment Details
- `COMP_NAME` - Company name
- `LOC_NAME` - Location
- `DSG_NAME` - Designation
- `DEPT_NAME` - Department
- `DOJ` - Date of joining
- `DOC` - Date of confirmation
- `DOL` - Date of leaving

#### Job Information
- `PositionTitle` - Position title
- `FUNCT_NAME` - Function/department
- `BUSSNAME` - Business unit
- `ROLE_NAME` - Role
- `BAND_NAME` - Band level
- `GRD_NAME` - Grade level

#### Reporting Structure
- `MNGR_NAME`, `Mngr_Emailid` - Manager details
- `FUNCATONAL_MNGR_NAME` - Functional manager
- `BussUnitHead` - Business unit head
- `DirectReportees` - List of direct reportees

#### Compensation
- `CTC` - Cost to company
- `AnnualCTC` - Annual CTC

#### Bank & Documents
- `SMOP_NAME`, `SMOPNo`, `IFSC_CODE` - Bank details
- `EmpImage`, `AadharDocument`, `PANAttachment` - Documents

---

### 2. Team Management Tool

Returns team attendance, leaves, and shift information.

**Query Examples:**
- "Show team details for SMS0668"
- "Team attendance for today"
- "Who's on leave this week?"
- "Shift schedule for the team"

**Available Data:**

#### Team Member Info
- `Emp_Code` - Employee code
- `EMP_NAME` - Employee name
- `FUNCT_NAME` - Function
- `DSG_NAME` - Designation
- `OEMailID` - Official email
- `MobileNo` - Mobile number

#### Daily Status
- `date` - Attendance date (YYYY-MM-DD)
- `status` - Status (In Office, Out Of Office, Leave, etc.)
- `intime` - Check-in time (ISO format)
- `outTime` - Check-out time (ISO format)

#### Holiday Information
- `holidayStatus` - Is it a holiday?
- `holidayTitle` - Holiday name

#### Leave Information
- `leaveStatus` - On leave?
- `leaveType` - Type (Casual, Sick, Privileged, etc.)
- `leaveReason` - Reason for leave
- `leaveNature` - Full day or half day

#### Shift Information
- `scheduleShift` - Shift name
- `shiftStart` - Start time (HH:MM:SS)
- `shiftEnd` - End time (HH:MM:SS)

#### Attendance Regularization
- `arStatus` - Regularization status (Pending, Approved, Rejected)
- `arInTime` - Regularized check-in
- `arOutTime` - Regularized check-out
- `arRemark` - Regularization remarks

**Status Values:**
- **Attendance Status:** In Office, Out Of Office, Leave, Weekly Off, Holiday, Absent
- **Regularization Status:** Pending, Approved, Rejected
- **Shift Types:** 9 AM to 8 PM 9 hours, General Shift, Night Shift, Flexible Shift

---

### 3. Policy Search Tool

Search HR policies and FAQs using natural language.

**Query Examples:**
- "What's the leave policy?"
- "How many casual leaves do we get?"
- "PF advance withdrawal process"
- "Work from home policy"
- "Travel reimbursement limits"

**Returns:**
- Policy text
- Eligibility criteria
- Procedures and guidelines
- Links to documentation

---

## Error Responses

### Authentication Error
```json
{
  "success": false,
  "message": "Failed to process query",
  "error": "Authentication failed. Please check your credentials and domain URL.",
  "data": null
}
```

### Invalid Parameters
```json
{
  "success": false,
  "message": "Failed to process query",
  "error": "Employee code is required",
  "data": null
}
```

### Server Error
```json
{
  "success": false,
  "message": "Failed to process query",
  "error": "Internal server error: details here",
  "data": null
}
```

---

## Rate Limiting

Current implementation supports:
- **100+ requests per minute** from a single client
- **1000+ concurrent users** (depends on backend capacity)
- Burst handling with graceful degradation

For production deployments, configure rate limiting in `settings.py`.

---

## Response Formats

### Formatted Response (from `/query`)
```json
{
  "has_data": true,
  "formatted_text": "**Bold text** and *italic* with - bullet points"
}
```

Uses Markdown format for human readability and LLM processing.

### Raw Response (from `/query_raw`)
```json
{
  "data": {...raw_data...},
  "message": "Success message",
  "status": true
}
```

---

## Pagination

Not currently supported. For large datasets, use date range filtering:

```json
{
  "user_query": "Team attendance for this month",
  "start_date": "2025-11-01",
  "end_date": "2025-11-30"
}
```

---

## Best Practices

### 1. Use Specific Queries
❌ Bad: "Get info"  
✅ Good: "Get profile for employee SMS0668"

### 2. Include Date Range for Time-Series Data
❌ Bad: "Show attendance"  
✅ Good: "Show team attendance for this week"

### 3. Handle Errors Gracefully
```python
response = requests.post(API_URL, json=payload)
if response.status_code == 200:
    data = response.json()
    if data["success"]:
        # Process data
    else:
        print(f"Error: {data['error']}")
```

### 4. Cache Responses When Possible
Profile data rarely changes, so cache for 1 hour:
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_employee_profile(emp_code):
    # Fetch and cache
    pass
```

### 5. Use Raw Responses for Structured Processing
Use `/query_raw` when building automated workflows that need JSON structure.

---

## Webhooks (Coming Soon)

Subscribe to changes in employee data:

```json
{
  "event": "employee.profile.updated",
  "emp_code": "SMS0668",
  "timestamp": "2025-11-14T10:30:45.123456",
  "changes": {
    "designation": "Sr. Manager - Software Development"
  }
}
```

---

## Changelog

### v1.0.0 (November 2025)
- Initial API release
- Profile, Team, and Policy tools
- REST API endpoints
- MCP server support
- Token management

---

## Support

- 📧 **Email:** support@sequelone.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/sequelone/hris_mcp_servers/issues)
- 📚 **Documentation:** [Full Docs](README.md)
