import asyncio
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-profile")

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
app = Server("hris-profile")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_employee_profile",
            description="Get comprehensive employee profile details including personal information, contact details, employment information",
            inputSchema={
                "type": "object",
                "properties": {
                    "emp_code": {
                        "type": "string",
                        "description": "Employee code to fetch profile for"
                    },
                    "domain_url": {
                        "type": "string", 
                        "description": "Domain URL for authentication",
                        "default": settings.DEFAULT_DOMAIN
                    }
                },
                "required": ["emp_code"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "get_employee_profile":
            emp_code = arguments.get("emp_code", "").strip()
            domain_url = arguments.get("domain_url", settings.DEFAULT_DOMAIN)
            
            if not emp_code:
                return [types.TextContent(type="text", text="❌ Employee code is required")]

            result = await _handle_profile_request(emp_code, domain_url)
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(type="text", text=f"❌ Unknown tool: {name}")]
            
    except Exception as e:
        return [types.TextContent(type="text", text=f"❌ Error: {str(e)}")]

async def _handle_profile_request(emp_code: str, domain_url: str) -> str:
    """Single function to handle profile API call and response processing"""
    logger.info(f"🔍 Profile request received for employee: {emp_code}")
    base_url = settings.BASE_API_URL
    query = """
    query GetEmployeeDetails($empCode: ID!) {
  getEmployeeDetails(Emp_Code: $empCode) {
    Emp_Code
    Emp_Name
    Emp_Title
    Emp_FName
    Emp_MName
    Emp_LName
    Status_Code
    MAddr1
    MAddr2
    MAddr3
    MCity
    MRegion
    MState
    MCountry
    MPin
    MPhoneNo
    PAddr1
    PAddr2
    PAddr3
    PCity
    PRegion
    PState
    PCountry
    PPin
    PPhoneNo
    MobileNo
    PagerNo
    FaxNo
    DOB
    BirthPlace
    Domicile
    Sex
    MStatus
    DOM
    Religion
    Cast
    Nationality
    PassportNo
    PassportValidityDate
    PassportAddress
    PassportPlace
    DLNo
    DLValidityDate
    DLAddress
    DLPlace
    FathHusb
    FathHusbName
    FathHusbOcupation
    EmergencyName
    EmergencyRelation
    EmergencyAddress
    EmergencyPhoneNo
    DrName
    DrAddress
    DrPhoneNo
    BloodGrp
    FoodChoice
    OEMailID
    OEMailPWD
    PEMailID
    PEMailPWD
    OccupationCode
    EmpImage
    UpdatedBy
    UpdatedOn
    BANKDATE
    REHIREDATE
    LOAINDATE
    TRFINDATE
    COUNTRY
    CONV_EXEMP
    FNFSTATUS
    BRANCH_NAME
    FULLNAME
    AadharNo
    PIssuePlace
    DIssuePlace
    PIssueDate
    DIssueDate
    MArea
    Anniversary
    BloodGroup
    contract_end
    applicable
    GroupID
    FacialID
    Facial_status
    ImageUploadDateTime
    Recruitment_CandidateId
    Recruitment_RFRId
    PassportDocument
    DLDocument
    AadharDocument
    currAddrDocument
    permAddrDocument
    creation_time
    Payroll_Status
    EmailRequired
    FatherName
    spouseName
    birthCountry
    disabilityPercentage
    birthState
    DisplayName
    UserName
    AadhaarName
    DLPlaceOfIssue
    DLDateOfIssue
    DLValidity
    PValidateDate
    PAddress
    PPlaceOfIssue
    ReportStatus
    REGIME
    PayrollEligible
    gaurdianRelationship
    gaurdianPhoneNo
    PerGuardianName
    MLatitude
    MLongitude
    EmpSign
    NEWDIVI_CODE
    NEWREGN_CODE
    Section_Code
    NEWDSG_CODE
    NEWDSGID
    newWLOC_CODE
    NEWcompCode
    NEWLOC_CODE
    EMP_NAME
    BloodGroup_Name
    Title_Name
    Gender
    ERO_EMAILID
    Ero_NAME
    Marital_Status
    DOC_DUE
    MailingAddress
    PositionId
    posid
    PositionCode
    PositionTitle
    DOJ
    OriginalDOJ
    DOJCenter
    DOC
    DOR
    DOL
    DOL_WEF
    DOS
    ServiceAgreementTenure
    ServiceAgreementEnddate
    ConfirmStatus
    ConfirmStartDate
    CONFIRM_DUE_DATE
    ActualConfirmationDate
    CONFIRM_REQ
    STATUS_NAME
    PayrollStatus
    JobProfile
    PayrollStatus_Name
    COMP_CODE
    COMP_NAME
    COMPCODE
    COMP_ADDR
    COMP_CITY
    COMP_STATE
    COMP_PIN
    CompanyAddress
    COMP_PFNO
    COMP_ESINO
    COMP_PANNO
    COMP_TANNO
    COMP_HRID
    LOC_CODE
    LOC_NAME
    Loc_Type_Name
    Unit
    Unit_Name
    STATE_CODE
    STATE_NAME
    DEPT_CODE
    DEPT_NAME
    COST_CODE
    PROC_CODE
    PROC_NAME
    TYPE_CODE
    TYPECODE
    TYPE_NAME
    GRD_CODE
    GRD_NAME
    DSG_CODE
    DSGCODE
    DSG_NAME
    Role_Code
    RoleCode
    ROLE_NAME
    MNGR_CODE
    MNGR_NAME
    BussCode
    BUSSNAME
    SUBBuss_Code
    SUBBUSSNAME
    Regn_Code
    REGN_NAME
    Divi_Code
    DIVI_NAME
    WLOC_CODE
    WLOC_NAME
    FUNCT_CODE
    FUNCTCODE
    FUNCT_NAME
    SFUNCT_CODE
    SUBFUNCT_NAME
    MNGR_CODE2
    FUNCATONAL_MNGR_NAME
    BandId
    BAND_NAME
    Registration_No
    Trade
    WorkPhone
    WorkPhoneExt
    BussUnitHead_Code
    BussUnitHead
    BussUnitHead_Emailid
    SubBussUnitHead_Code
    SubBussHead
    SubBussHead_Email
    FunctionHead_Code
    FunctionHead
    FunctionHead_Email
    SubFunctHead_code
    SubFunctionHead
    SubFunctionHead_Email
    Mngr_Emailid
    FUNCATONAL_MNGR_Emailid
    CTC
    HRD_TRN_WEF
    Trn_WEF
    Trn_Date
    GuardianName
    ERO
    RETIRE_DATE
    HRDMASTStateID
    PState_Name
    S_State
    VISANO
    VISAEXP
    WRKPERNO
    WIPEXP
    VISADOC
    WORKDOC
    SubFunctCODE
    GRDCODE
    LOCCODE
    BANDCODE
    Section
    Section_Name
    Level_Code
    LeadershipLevel_Name
    EventId
    EventReasonId
    Event_Name
    EventReason_Name
    HRBP_NAME
    NATIONALITY_NAME
    PreviousEmployeeCode
    AdditionalResponsibilityes
    InductionCompletionDate
    RG_NRG
    RG_NRG_NAME
    accessID
    accesscode
    ESI_YN
    ESI_EffectiveDate
    ESICEffectiveDate
    MED_YN
    TDS_YN
    RPFC_YN
    PTAX_YN
    SAF_YN
    ESP_YN
    VPF_PER
    Child_Number
    CHILDNO
    LWF_YN
    ReasonMedAndESI
    EmpEntity
    EmpEntity_Name
    Category
    NoticePeriod
    DOJ_WEF
    Prob_Period
    Prob_Period_Extended
    LeavReason
    workFlow_id
    confirmPolicy_id
    State
    PositionAssignedDate
    SequenceNumber
    HRBP
    Sourceofhiring
    AnnualCTC
    PANNo
    PANAttachment
    UNNo
    ESINo
    ESIRegionCode
    PFNo
    PFRegionCode
    PFOffice
    PFState
    PANNoEmployer
    PTaxState
    PTaxLocation
    TANNo
    IFSC_CODE
    RIFSC_CODE
    SMOP_NAME
    SMOP_Code
    SMOPNo
    SMOP_No
    RMOP_NAME
    RMOPNo
    Tds_cal
    rpfc
    Sect_Code
    LocationType
    City_Name
    PANName
    pastyearExp
    pastyearMon
    Line
    Line_Name
    City
    SubBandName
    EmpGroup_NAME
    Category_Name
    SSS_YN
    PHILHEALTH_YN
    HDMF_YN
    SSS_With_PF
    Minimum_wage_emp
    SSS_Show_PF_Sep
    PayCycle
    TaxMethod
    SSNo
    PhilhelathNo
    HDMFNo
    TINNo
    ContractStartDate
    ContractEndDate
    DirectReportees
    occassion
    Schedule_Shift
    Shift_start
    Shift_end
    Shiftmandatoryhrs
    Intime
    PEmailID

  }
}
    """
    
    variables = {"empCode": emp_code}
    
    try:
        # Token will be automatically handled (reused or regenerated)
        token_info = token_manager.get_token_info()
        logger.info(f"🔑 Token Info: {token_info}")
        
        # This will automatically generate new token if expired or reuse existing one
        token = token_manager.get_token(emp_code, domain_url)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'contextempcode': emp_code
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        logger.info(f"full request headers: {headers}")
        logger.info(f"Data Payload: {payload}")
        
        response = requests.post(
            base_url + "/graphql",
            headers=headers,
            data=json.dumps(payload)
        )
        logger.info(f"🔄 Making GraphQL request for profile: {emp_code}")
        
        if response.status_code == 200:
            logger.info(f"✅ Profile data retrieved successfully for: {emp_code}")
            result = response.json()
        elif response.status_code == 401 or (response.status_code == 400 and "UNAUTHENTICATED" in response.text):
            # Token might be invalid, generate new one and retry
            logger.warning("🔄 Token invalid, generating new token...")
            token = token_manager.generate_token(emp_code, domain_url)
            headers['Authorization'] = f'Bearer {token}'
            
            response = requests.post(
                base_url + "/graphql",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Profile data retrieved successfully after token refresh for: {emp_code}")
                result = response.json()
            else:
                logger.error(f"API call failed after token refresh: {response.status_code} - {response.text}")
                raise Exception({"data": None, "message": f"API call failed after token refresh: {response.status_code} - {response.text}", "status": False})
        else:
            logger.error(f"API call failed: {response.status_code} - {response.text}")
            raise Exception({"data": None, "message": f"API call failed: {response.status_code} - {response.text}", "status": False})
        
        employee_data = result.get('data', {}).get('getEmployeeDetails', {})
        
        if not employee_data:
            logger.warning(f"❌ No employee data found for the provided employee code: {emp_code}")
            return {"data": None, "message": "❌ No employee data found for the provided employee code.", "status": False}
        
        
        logger.info(f"✅ Employee profile fetched successfully for: {emp_code}")
        return {"data": employee_data, "message": "✅ Employee profile fetched successfully.", "status": True}
            
    except Exception as e:
        logger.error(f"❌ Error fetching employee profile: {str(e)}")
        return {"data": None, "message": f"❌ Error fetching employee profile: {str(e)}", "status": False}

async def main():
    logger.info("🚀 Starting Profile MCP Server...")
    
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
                server_name="hris-profile",
                server_version="1.0.0",
                capabilities=capabilities
            )
        )

if __name__ == "__main__":
    asyncio.run(main())