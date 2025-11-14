# Centralized settings for HRIS MCP servers
import os
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

# External services
DEVGPT_BASE = os.getenv("DEVGPT_BASE", "https://devgpt.honohr.com")
FORMATTER_ENDPOINT = os.getenv("FORMATTER_ENDPOINT", f"{DEVGPT_BASE}/openai")
FORMATTER_MODEL = os.getenv("FORMATTER_MODEL", "chatgpt-4o-latest")
OLLAMA_BASE = os.getenv("OLLAMA_BASE", f"{DEVGPT_BASE}/ollama")

# HRIS API base (GraphQL endpoints)
BASE_API_URL = os.getenv("BASE_URL", "https://honoapp.honohr.com/api")
HRIS_PROFILE_API = os.getenv("HRIS_PROFILE_API", f"{DEVGPT_BASE}/hris/api/profile")
HRIS_TEAM_API = os.getenv("HRIS_TEAM_API", f"{DEVGPT_BASE}/hris/api/team")
POLICY_SEARCH_API = os.getenv("POLICY_SEARCH_API", f"{DEVGPT_BASE}/genaisearch/rfpsearch/")

# Application defaults
DEFAULT_DOMAIN = os.getenv("DEFAULT_DOMAIN", "honoenterpriseapp.honohr.com")
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))

# LLM model configurations (kept out of code; keys should be provided via env)
LLM_MODELS = {
	"gpt4o": {
		"model_id": os.getenv("GPT4O_MODEL_ID", "chatgpt-4o-latest"),
		"api_key": os.getenv("GPT4O_API_KEY", None),
		# allow optional api_base for providers that need it
		"api_base": os.getenv("GPT4O_API_BASE", None)
	},
	"deepseek": {
		"model_id": os.getenv("DEEPSEEK_MODEL_ID", "ollama/deepseek-r1:latest"),
		"api_base": os.getenv("DEEPSEEK_API_BASE", OLLAMA_BASE),
		"completion_kwargs": {
			"stream": False,
			"format": "json",
			"options": {"temperature": 0, "top_k": 50}
		}
	}
}

# API metadata (tool descriptions and sample data). Keep this centralized so other modules can import it.
# If you prefer to load from a JSON file, set API_METADATA_FILE env to a path and it will be loaded.
API_METADATA_FILE = os.getenv("API_METADATA_FILE", "")
if API_METADATA_FILE and Path(API_METADATA_FILE).exists():
	try:
		with open(API_METADATA_FILE, "r", encoding="utf-8") as f:
			API_METADATA = json.load(f)
	except Exception:
		API_METADATA = {}
else:
	# Minimal default metadata; modules may override or extend at runtime
	API_METADATA = {
    "employee_profile": {
        "description": "Comprehensive employee profile information including personal details, contact information, employment details, job information, and organizational hierarchy",
        "fields": {
            "basic_info": {
                "Emp_Code": "Unique employee code",
                "EMP_NAME": "Full name of employee",
                "Emp_Title": "Title code (1=Mr., etc.)",
                "Emp_FName": "First name",
                "Emp_MName": "Middle name", 
                "Emp_LName": "Last name",
                "Status_Code": "Employment status code",
                "STATUS_NAME": "Employment status name"
            },
            "personal_details": {
                "DOB": "Date of birth",
                "Gender": "Gender",
                "Marital_Status": "Marital status",
                "BloodGroup_Name": "Blood group",
                "NATIONALITY_NAME": "Nationality",
                "FatherName": "Father's name",
                "spouseName": "Spouse's name",
                "AadharNo": "Aadhar number",
                "PANNo": "PAN number",
                "Religion": "Religion code",
                "Cast": "Caste information"
            },
            "contact_information": {
                "MobileNo": "Mobile number",
                "OEMailID": "Official email",
                "PEMailID": "Personal email", 
                "MPhoneNo": "Mailing address phone",
                "PPhoneNo": "Permanent address phone",
                "MailingAddress": "Complete mailing address",
                "MAddr1": "Mailing address line 1",
                "MAddr2": "Mailing address line 2", 
                "MAddr3": "Mailing address line 3",
                "MCity": "Mailing city code",
                "MState": "Mailing state code",
                "MPin": "Mailing PIN code",
                "PAddr1": "Permanent address line 1",
                "PAddr2": "Permanent address line 2",
                "PAddr3": "Permanent address line 3",
                "PCity": "Permanent city code", 
                "PState": "Permanent state code",
                "PPin": "Permanent PIN code"
            },
            "employment_details": {
                "COMP_NAME": "Company name",
                "LOC_NAME": "Work location",
                "DSG_NAME": "Designation",
                "DEPT_NAME": "Department",
                "DOJ": "Date of joining",
                "DOC": "Date of confirmation",
                "DOL": "Date of leaving",
                "ConfirmStatus": "Confirmation status",
                "PayrollStatus_Name": "Payroll status"
            },
            "job_information": {
                "PositionTitle": "Job position title",
                "FUNCT_NAME": "Function/department",
                "BUSSNAME": "Business unit",
                "ROLE_NAME": "Role",
                "BAND_NAME": "Band level",
                "GRD_NAME": "Grade level",
                "TYPE_NAME": "Employment type"
            },
            "reporting_structure": {
                "MNGR_NAME": "Manager name",
                "Mngr_Emailid": "Manager email",
                "FUNCATONAL_MNGR_NAME": "Functional manager name",
                "FUNCATONAL_MNGR_Emailid": "Functional manager email",
                "BussUnitHead": "Business unit head",
                "BussUnitHead_Emailid": "Business unit head email",
                "SubBussHead": "Sub-business head", 
                "SubBussHead_Email": "Sub-business head email",
                "DirectReportees": "List of direct reportees"
            },
            "compensation": {
                "CTC": "Cost to company",
                "AnnualCTC": "Annual CTC"
            },
            "bank_details": {
                "SMOP_NAME": "Bank name",
                "SMOPNo": "Bank account number",
                "IFSC_CODE": "IFSC code"
            },
            "documents": {
                "EmpImage": "Employee photo filename",
                "AadharDocument": "Aadhar document filename",
                "PANAttachment": "PAN document filename",
                "currAddrDocument": "Current address proof filename",
                "permAddrDocument": "Permanent address proof filename"
            }
        },
        "sample_data": {
            "Emp_Code": "SMS0668",
            "EMP_NAME": "Ashish Mittal",
            "Emp_Title": "1",
            "Emp_FName": "Ashish",
            "Emp_MName": " ",
            "Emp_LName": "Mittal",
            "DOB": "1995-04-30",
            "Gender": "Male", 
            "Marital_Status": "Unmarried",
            "BloodGroup_Name": "O +ve",
            "MobileNo": "8447037094",
            "OEMailID": "ashish.mittal@hono.ai",
            "PEMailID": "ashishmittal.528@gmail.com",
            "MailingAddress": "Signature Global Park 3 C-7-2F 48 - 122103",
            "COMP_NAME": "SequelOne Solutions Pvt. Ltd.",
            "LOC_NAME": "Gurugram",
            "DSG_NAME": "Sr. Manager - Software Development",
            "DOJ": "2020-04-01",
            "MNGR_NAME": "Prasanth Raghavulu",
            "Mngr_Emailid": "prasanth@hono.ai",
            "PositionTitle": "Sr. Manager-Software Development",
            "FUNCT_NAME": "Engineering",
            "BUSSNAME": "Engineering",
            "ROLE_NAME": "Software Development",
            "BAND_NAME": "3",
            "CTC": "167440",
            "DirectReportees": ["INT0084", "INT0091", "INT0093", "INT0097", "INT0126", "INT0131", "SMS0919", "SMS1038", "SMS1142", "SMS1150"],
            "AadharNo": "940978626105",
            "PANNo": "CFOPM4485E"
        }
    },
    "team_management": {
        "description": "Team management details including employee information, daily attendance status, leave information, shift details, and attendance regularization",
        "fields": {
            "team_member_info": {
                "Emp_Code": "Employee code",
                "EMP_NAME": "Employee full name",
                "FUNCT_NAME": "Function/department",
                "DSG_NAME": "Designation",
                "OEMailID": "Official email address",
                "MobileNo": "Mobile number"
            },
            "daily_status": {
                "date": "Attendance date (YYYY-MM-DD)",
                "status": "Current status (In Office, Out Of Office, Leave, etc.)",
                "intime": "Check-in time (ISO format)",
                "outTime": "Check-out time (ISO format)"
            },
            "holiday_info": {
                "holidayStatus": "Holiday status (null if not holiday)",
                "holidayTitle": "Holiday title/name"
            },
            "attendance_regularization": {
                "arStatus": "Regularization status (Pending, Approved, Rejected, null if not applicable)",
                "arInTime": "Regularized check-in time",
                "arOutTime": "Regularized check-out time", 
                "arRemark": "Regularization remarks/comments"
            },
            "leave_info": {
                "leaveStatus": "Leave status (null if not on leave)",
                "leaveType": "Type of leave (Casual, Sick, Privileged, etc.)",
                "leaveReason": "Reason for leave",
                "leaveNature": "Nature of leave (Full Day, Half Day, etc.)"
            },
            "on_duty_info": {
                "onDutyStatus": "On duty status",
                "onDutyReason": "Reason for on duty",
                "odDutyType": "Type of on duty"
            },
            "shift_info": {
                "scheduleShift": "Scheduled shift name/description",
                "shiftStart": "Shift start time (HH:MM:SS)",
                "shiftEnd": "Shift end time (HH:MM:SS)"
            }
        },
        "sample_data": {
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
                    "holiday": {
                        "holidayStatus": "null",
                        "holidayTitle": "null"
                    },
                    "attendanceRegularisation": {
                        "arStatus": "null",
                        "arInTime": "null",
                        "arOutTime": "null",
                        "arRemark": "null"
                    },
                    "leave": {
                        "leaveStatus": "null",
                        "leaveType": "null",
                        "leaveReason": "null",
                        "leaveNature": "null"
                    },
                    "onDuty": {
                        "onDutyStatus": "",
                        "onDutyReason": "",
                        "odDutyType": ""
                    },
                    "shift": {
                        "scheduleShift": "9 AM to 8 PM 9 hours",
                        "shiftStart": "09:00:00",
                        "shiftEnd": "20:00:00"
                    }
                }
            ]
        },
        "common_status_values": {
            "attendance_status": ["In Office", "Out Of Office", "Leave", "Weekly Off", "Holiday", "Absent"],
            "regularization_status": ["Pending", "Approved", "Rejected", "null"],
            "shift_types": ["9 AM to 8 PM 9 hours", "General Shift", "Night Shift", "Flexible Shift"]
        }
    },
    "policy_search": {
        "description": "HR policies, FAQs, and documentation search from company knowledge base",
        "fields": {
            "search_results": {
                "query": "Original search query",
                "answer": "Detailed policy answer with procedures and guidelines",
                "status": "Search success status",
                "source": "HR Policy Knowledge Base"
            }
        },
        "sample_data": {
            "query": "PF advance withdrawal process active",
            "answer": "PF advance withdrawal process while active: We can initiate the PF advance (while active in employment) from our PF account for specific reasons such as purchasing a home, medical emergencies, education, or marriage. Process -> Visit the EPFO Website -> Online services -> Claim (Form-31, 19 & 10C) -> Enter the Bank account number updated in EPFO records Under KYC details and click on Verify...",
            "status": True,
            "source": "HR Policy Knowledge Base"
        }
    }
}


__all__ = [
	"BASE_DIR",
	"DEVGPT_BASE",
	"FORMATTER_ENDPOINT",
	"FORMATTER_MODEL",
	"OLLAMA_BASE",
	"BASE_API_URL",
	"HRIS_PROFILE_API",
	"HRIS_TEAM_API",
	"POLICY_SEARCH_API",
	"DEFAULT_DOMAIN",
	"TOKEN_EXPIRY_HOURS",
	"LLM_MODELS",
	"API_METADATA",
]

