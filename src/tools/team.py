import asyncio
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-team")

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions, ServerCapabilities
    import mcp.types as types
    import requests
    import json
    from tools.token_manager import token_manager
    from config import settings
    logger.info("✓ All imports successful")
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

# Create server
app = Server("hris-team")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_team_details",
            description="Get team details including attendance, leave status, shift information for a manager and date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "emp_code": {
                        "type": "string",
                        "description": "Manager's employee code"
                    },
                    "start_date": {
                        "type": "string", 
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "status_code": {
                        "type": "string",
                        "description": "Status code",
                        "default": "01"
                    },
                    "domain_url": {
                        "type": "string",
                        "description": "Domain URL for authentication",
                        "default": settings.DEFAULT_DOMAIN
                    }
                },
                "required": ["emp_code", "start_date", "end_date"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "get_team_details":
            emp_code = arguments.get("emp_code", "").strip()
            start_date = arguments.get("start_date", "").strip()
            end_date = arguments.get("end_date", "").strip()
            status_code = arguments.get("status_code", "01")
            domain_url = arguments.get("domain_url", settings.DEFAULT_DOMAIN)
            
            if not emp_code or not start_date or not end_date:
                return [types.TextContent(type="text", text="❌ Employee code, start date, and end date are required")]

            result = await _handle_team_request(emp_code, start_date, end_date, status_code, domain_url)
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(type="text", text=f"❌ Unknown tool: {name}")]
            
    except Exception as e:
        return [types.TextContent(type="text", text=f"❌ Error: {str(e)}")]

async def _handle_team_request(emp_code: str, start_date: str, end_date: str, status_code: str, domain_url: str) -> str:
    """Single function to handle team API call and response processing"""
    logger.info(f"🔄 Making GraphQL request for team details: {emp_code} from {start_date} to {end_date}")
    base_url = settings.BASE_API_URL
    query = """
    query GetTeamDetailsList($employeeInput: EmployeeDetailsInput) {
  getTeamDetailsList(employeeInput: $employeeInput) {
    Emp_Code
    EMP_NAME
    FUNCT_NAME
    DSG_NAME
    OEMailID
    MobileNo
    status {
      date
      status
      intime
      outTime
      holiday {
        holidayStatus
        holidayTitle
        
      }
      attendanceRegularisation {
        arStatus
        arInTime
        arOutTime
        arRemark
      }
      leave {
        leaveStatus
        leaveType
        leaveReason
        leaveNature
      }
      onDuty {
        onDutyStatus
        onDutyReason
        odDutyType
      }
      shift {
        scheduleShift
        shiftStart
        shiftEnd
      }
    }
  }
}

    """
    
    variables = {
        "employeeInput": {
            "empCode": emp_code,
            "startDate": start_date,
            "endDate": end_date,
            "statusCode": status_code
        }
    }
    
    try:
        # Token will be automatically handled (reused or regenerated)
        token_info = token_manager.get_token_info()
        logger.info(f"🔑 Token Info: {token_info}")
        
        # This will automatically generate new token if expired or reuse existing one
        token = token_manager.get_token(emp_code, domain_url)
        logger.info(f"🔄 Using token for employee code: {emp_code}")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'contextempcode': emp_code
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        response = requests.post(
            base_url + "/graphql",
            headers=headers,
            data=json.dumps(payload)
        )
        logger.info(f"🔄 Making GraphQL request for team details: {emp_code}")
        if response.status_code == 200:
            logger.info(f"✅ GraphQL request successful for team details: {emp_code}")
            result = response.json()
        elif response.status_code == 401 or (response.status_code == 400 and "UNAUTHENTICATED" in response.text):
            # Token might be invalid, generate new one and retry
            logger.warning("🔄 Token invalid, generating new token...")
            token = token_manager.generate_token(emp_code, domain_url)
            headers['Authorization'] = f'Bearer {token}'
            headers['contextempcode'] = emp_code
            response = requests.post(
                base_url + "/graphql",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Team data retrieved successfully after token refresh for: {emp_code}")
                result = response.json()
            else:
                logger.error(f"API call failed after token refresh: {response.status_code} - {response.text}")
                raise Exception({"data": None, "message": f"API call failed after token refresh: {response.status_code} - {response.text}", "status": False})
        else:
            logger.error(f"API call failed: {response.status_code} - {response.text}")
            raise Exception({"data": None, "message": f"API call failed: {response.status_code} - {response.text}", "status": False})
        
        team_data = result.get('data', {}).get('getTeamDetailsList', [])
        
        if not team_data:
            logger.warning(f"❌ No team data found for the provided criteria.")
            return {"data": None, "message": "❌ No team data found for the provided criteria.", "status": False}

        return {"data": team_data, "message": "✅ Team details fetched successfully.", "status": True}
            
    except Exception as e:
        logger.error(f"❌ Error fetching team details: {str(e)}")
        return {"data": None, "message": f"❌ Error fetching team details: {str(e)}", "status": False}

async def main():
    logger.info("🚀 Starting Team MCP Server...")
    
    # Create server capabilities
    capabilities = ServerCapabilities(
        tools=types.ToolsCapability(),
        resources=types.ResourcesCapability(),
        prompts=types.PromptsCapability()
    )
    
    # Get stdio streams
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hris-team",
                server_version="1.0.0",
                capabilities=capabilities
            )
        )

if __name__ == "__main__":
    asyncio.run(main())