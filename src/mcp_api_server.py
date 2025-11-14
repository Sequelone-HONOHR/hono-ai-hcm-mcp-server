#!/usr/bin/env python3
"""
MCP Agent Pipeline for HRIS - Updated for JSON response structure
"""

import asyncio
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any, List
from datetime import datetime
import json
import subprocess
from pydantic import BaseModel
from typing import Optional
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp-agent")

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
    logger.info("✓ MCP imports successful")
except ImportError as e:
    logger.error(f"MCP import error: {e}")
    MCP_AVAILABLE = False

# FastAPI App
app = FastAPI(title="HRIS MCP Agent Pipeline", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MCPAgent:
    def __init__(self):
        self.server_configs = {
            "profile": {
                "script": "src/tools/profile.py",
                "description": "Employee Profile Management"
            },
            "team": {
                "script": "src/tools/team.py", 
                "description": "Team Management and Attendance"
            }
        }
        self.processes = {}
        self.sessions = {}
        self.clients = {}
    
    async def start_server(self, server_name: str):
        """Start an MCP server process"""
        if server_name not in self.server_configs:
            raise ValueError(f"Unknown server: {server_name}")
        
        if server_name in self.processes:
            logger.info(f"Server {server_name} already running")
            return
        
        config = self.server_configs[server_name]
        script_path = project_root / config["script"]
        
        if not script_path.exists():
            raise FileNotFoundError(f"Server script not found: {script_path}")
        
        # Start the server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(script_path),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes[server_name] = process
        logger.info(f"Started {server_name} server (PID: {process.pid})")
        
        # Connect MCP client
        try:
            server_params = StdioServerParameters(
                command=str(sys.executable),
                args=[str(script_path)],
                env=None
            )
            
            # For now, we'll use direct script execution instead of MCP client
            # since the servers are designed to run independently
            logger.info(f"✓ {server_name} server ready for direct execution")
            
        except Exception as e:
            logger.error(f"Failed to connect to {server_name} server: {e}")
            await self.stop_server(server_name)
            raise
    
    async def stop_server(self, server_name: str):
        """Stop an MCP server process"""
        if server_name in self.processes:
            process = self.processes[server_name]
            try:
                process.terminate()
                await process.wait()
                logger.info(f"Stopped {server_name} server")
            except Exception as e:
                logger.warning(f"Error stopping {server_name}: {e}")
            finally:
                self.processes.pop(server_name, None)
                self.sessions.pop(server_name, None)
                self.clients.pop(server_name, None)
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Dict[str, Any]:
        """Call a tool on an MCP server by executing the script directly"""
        if server_name not in self.server_configs:
            raise ValueError(f"Unknown server: {server_name}")
        
        config = self.server_configs[server_name]
        script_path = project_root / config["script"]
        
        if not script_path.exists():
            raise FileNotFoundError(f"Server script not found: {script_path}")
        
        # For direct execution, we'll simulate tool calls by running the scripts
        # In a real implementation, you'd use proper MCP client-server communication
        
        if server_name == "profile" and tool_name == "get_employee_profile":
            # Import and call the profile function directly
            try:
                from tools.profile import _handle_profile_request
                emp_code = arguments.get("emp_code")
                domain_url = arguments.get("domain_url")
                
                if not emp_code:
                    return {"data": None, "message": "Employee code is required", "status": False}
                
                if not domain_url:
                    return {"data": None, "message": "Domain URL is required", "status": False}
                result = await _handle_profile_request(emp_code, domain_url)
                
                # Handle both string and JSON responses for backward compatibility
                if isinstance(result, dict):
                    return result
                else:
                    return {"data": result, "message": "Profile data retrieved", "status": True}
                    
            except Exception as e:
                logger.error(f"Profile tool execution failed: {e}")
                return {"data": None, "message": f"Error: {str(e)}", "status": False}
        
        elif server_name == "team" and tool_name == "get_team_details":
            # Import and call the team function directly
            try:
                from tools.team import _handle_team_request
                emp_code = arguments.get("emp_code")
                start_date = arguments.get("start_date", f'{datetime.now().strftime("%Y-%m-%d")}')
                end_date = arguments.get("end_date", f'{datetime.now().strftime("%Y-%m-%d")}')
                status_code = arguments.get("status_code", "01")
                domain_url = arguments.get("domain_url")
                if not emp_code:
                    return {"data": None, "message": "Employee code is required", "status": False}
                if not domain_url:
                    return {"data": None, "message": "Domain URL is required", "status": False}
                result = await _handle_team_request(emp_code, start_date, end_date, status_code, domain_url)
                
                # Handle both string and JSON responses for backward compatibility
                if isinstance(result, dict):
                    return result
                else:
                    return {"data": result, "message": "Team data retrieved", "status": True}
                    
            except Exception as e:
                logger.error(f"Team tool execution failed: {e}")
                return {"data": None, "message": f"Error: {str(e)}", "status": False}
        
        else:
            return {"data": None, "message": f"Unknown tool: {tool_name} for server: {server_name}", "status": False}
    
    async def get_employee_profile(self, emp_code: str, domain_url: str) -> Dict[str, Any]:
        """Get employee profile via MCP server"""
        if not emp_code:
            return {"data": None, "message": "Employee code is required", "status": False}
        if not domain_url:
            return {"data": None, "message": "Domain URL is required", "status": False}
        return await self.call_tool("profile", "get_employee_profile", {
            "emp_code": emp_code,
            "domain_url": domain_url
        })
    
    async def get_team_details(self, emp_code: str, start_date: str = f'{datetime.now().strftime("%Y-%m-%d")}', 
                              end_date: str = f'{datetime.now().strftime("%Y-%m-%d")}', status_code: str = "01", 
                              domain_url: str = settings.DEFAULT_DOMAIN) -> Dict[str, Any]:
        """Get team details via MCP server"""
        if not emp_code:
            return {"data": None, "message": "Employee code is required", "status": False}
        if not domain_url:
            return {"data": None, "message": "Domain URL is required", "status": False}
        return await self.call_tool("team", "get_team_details", {
            "emp_code": emp_code,
            "start_date": start_date,
            "end_date": end_date,
            "status_code": status_code,
            "domain_url": domain_url
        })
    
    async def get_servers_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        status = {}
        
        for server_name, config in self.server_configs.items():
            try:
                script_path = project_root / config["script"]
                if script_path.exists():
                    status[server_name] = {
                        "status": "available",
                        "script": str(script_path),
                        "description": config["description"],
                        "running": server_name in self.processes
                    }
                else:
                    status[server_name] = {
                        "status": "script_not_found",
                        "script": str(script_path),
                        "description": config["description"],
                        "running": False
                    }
            except Exception as e:
                status[server_name] = {
                    "status": f"error: {str(e)}",
                    "description": config["description"],
                    "running": False
                }
        
        return status
    
    async def close_connections(self):
        """Close all connections"""
        for server_name in list(self.processes.keys()):
            await self.stop_server(server_name)
        
        logger.info("All MCP connections closed")

# Global MCP agent
mcp_agent = MCPAgent()

@app.on_event("startup")
async def startup_event():
    """Initialize MCP connections on startup"""
    logger.info("Starting HRIS MCP Agent Pipeline...")
    if not MCP_AVAILABLE:
        logger.warning("MCP library not available - running in limited mode")
    
    # Check server availability
    status = await mcp_agent.get_servers_status()
    logger.info("Server status on startup:")
    for server, info in status.items():
        logger.info(f"  {server}: {info['status']}")

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "HRIS MCP Agent Pipeline is running",
        "status": "healthy",
        "mcp_available": MCP_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/health": "Server status",
            "/api/profile": "Get employee profile (POST)", 
            "/api/team": "Get team details (POST)",
            "/api/analyze": "Advanced analysis (POST)",
            "/api/status": "MCP servers status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = await mcp_agent.get_servers_status()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "mcp_available": MCP_AVAILABLE,
            "servers": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProfileRequest(BaseModel):
    emp_code: str
    domain_url: Optional[str] = settings.DEFAULT_DOMAIN

class TeamRequest(BaseModel):
    emp_code: str
    start_date: str = "2025-11-04"
    end_date: str = "2025-11-04"
    status_code: Optional[str] = "01"
    domain_url: Optional[str] = settings.DEFAULT_DOMAIN

@app.post("/api/profile")
async def get_employee_profile(request: ProfileRequest):
    """Get employee profile via MCP server"""
    try:
        logger.info(f"Fetching profile for employee: {request.emp_code}")
        result = await mcp_agent.get_employee_profile(request.emp_code, request.domain_url)
        
        # Handle the new JSON response structure
        if isinstance(result, dict) and "status" in result:
            if result["status"]:
                return {
                    "success": True,
                    "employee_code": request.emp_code,
                    "data": result.get("data"),
                    "message": result.get("message", "Profile retrieved successfully"),
                    "server": "profile",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=400, detail=result.get("message", "Failed to retrieve profile"))
        else:
            # Fallback for old string response format
            return {
                "success": True,
                "employee_code": request.emp_code,
                "data": result,
                "server": "profile",
                "timestamp": datetime.now().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/team")
async def get_team_details(request: TeamRequest):
    """Get team details via MCP server"""
    try:
        logger.info(f"Fetching team details for manager: {request.emp_code} from {request.start_date} to {request.end_date}")
        result = await mcp_agent.get_team_details(
            request.emp_code, 
            request.start_date, 
            request.end_date, 
            request.status_code, 
            request.domain_url
        )
        
        # Handle the new JSON response structure
        if isinstance(result, dict) and "status" in result:
            if result["status"]:
                return {
                    "success": True,
                    "manager_code": request.emp_code,
                    "period": f"{request.start_date} to {request.end_date}",
                    "data": result.get("data"),
                    "message": result.get("message", "Team details retrieved successfully"),
                    "server": "team", 
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=400, detail=result.get("message", "Failed to retrieve team details"))
        else:
            # Fallback for old string response format
            return {
                "success": True,
                "manager_code": request.emp_code,
                "period": f"{request.start_date} to {request.end_date}",
                "data": result,
                "server": "team", 
                "timestamp": datetime.now().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/status")
async def get_status():
    """Get MCP servers status"""
    try:
        status = await mcp_agent.get_servers_status()
        
        return {
            "success": True,
            "mcp_available": MCP_AVAILABLE,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await mcp_agent.close_connections()

# Test function
async def test_mcp_operations():
    """Test MCP operations"""
    print("=== Testing HRIS MCP Operations ===")
    print(f"MCP Available: {MCP_AVAILABLE}")
    
    # Test individual servers
    print("\n1. Testing Profile Server...")
    try:
        profile_result = await mcp_agent.get_employee_profile("SMS0668")
        print(f"✅ Profile test completed")
        print(f"Status: {profile_result.get('status', 'N/A')}")
        print(f"Message: {profile_result.get('message', 'N/A')}")
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
    
    print("\n2. Testing Team Server...")
    try:
        team_result = await mcp_agent.get_team_details("SMS0668")
        print(f"✅ Team test completed") 
        print(f"Status: {team_result.get('status', 'N/A')}")
        print(f"Message: {team_result.get('message', 'N/A')}")
    except Exception as e:
        print(f"❌ Team test failed: {e}")
    
    print("\n3. Checking Server Status...")
    try:
        status = await mcp_agent.get_servers_status()
        print("✅ Server status:")
        for server, info in status.items():
            print(f"   {server}: {info['status']} (running: {info.get('running', False)})")
    except Exception as e:
        print(f"❌ Status check failed: {e}")
    
    print("\n4. Testing Chatbot Query...")
    
    print("\n🏁 Testing completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HRIS MCP Agent Pipeline")
    parser.add_argument("--mode", choices=["api", "test"], default="api", help="Run mode")
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    
    args = parser.parse_args()
    
    if args.mode == "test":
        # Run tests
        asyncio.run(test_mcp_operations())
    else:
        # Run API server
        print(f"🚀 Starting HRIS MCP Agent Pipeline on {args.host}:{args.port}")
        print(f"📡 MCP Available: {MCP_AVAILABLE}")
        print(f"🔧 Servers: profile, team")
        print(f"📊 Response Format: JSON")
        uvicorn.run(
            "mcp_api_server:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level="info"
        )