from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from scraper import ECourtsScraper
import base64
from io import BytesIO
import json
from database import QueryLogger

app = FastAPI(title="ECourts Case Scraper")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Global scraper instance
scraper = None

# Initialize query logger
query_logger = QueryLogger()

# Load ECourts data
def load_ecourts_data():
    try:
        with open('ecourts_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

ecourts_data = load_ecourts_data()

class SearchRequest(BaseModel):
    court_complex: str
    case_type: str
    case_number: str
    year: str
    captcha_value: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/api/states")
async def get_states():
    """Get all available states"""
    states = list(ecourts_data.keys())
    return {"success": True, "states": states}

@app.post("/api/districts")
async def get_districts(request: Request):
    """Get districts for a specific state"""
    data = await request.json()
    state_name = data.get("state")
    
    if not state_name or state_name not in ecourts_data:
        raise HTTPException(status_code=400, detail="Invalid state name")
    
    districts = list(ecourts_data[state_name]["districts"].keys())
    return {"success": True, "districts": districts}

@app.post("/api/initialize")
async def initialize_scraper(request: Request):
    """Initialize the scraper session for a specific district"""
    global scraper
    
    data = await request.json()
    state_name = data.get("state")
    district_name = data.get("district")
    
    if not state_name or not district_name:
        raise HTTPException(status_code=400, detail="State and district required")
    
    if state_name not in ecourts_data or district_name not in ecourts_data[state_name]["districts"]:
        raise HTTPException(status_code=400, detail="Invalid state or district")
    
    court_url = ecourts_data[state_name]["districts"][district_name]["court_url"]
    
    try:
        scraper = ECourtsScraper(court_url)
        success = scraper.initialize_session()
        if success:
            return {"success": True, "message": f"Session initialized successfully for {district_name}, {state_name}"}
        else:
            return {"success": False, "message": "Failed to initialize session"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/court-complexes")
async def get_court_complexes():
    """Get available court complexes"""
    global scraper
    if not scraper:
        raise HTTPException(status_code=400, detail="Scraper not initialized")
    
    return {"success": True, "court_complexes": scraper.court_complex_map}

@app.post("/api/case-types")
async def get_case_types(request: Request):
    """Get case types for a court complex"""
    global scraper
    if not scraper:
        raise HTTPException(status_code=400, detail="Scraper not initialized")
    
    data = await request.json()
    court_complex_code = data.get("court_complex_code")
    
    if not court_complex_code:
        raise HTTPException(status_code=400, detail="Court complex code required")
    
    try:
        case_types = scraper.get_case_types(court_complex_code)
        return {"success": True, "case_types": case_types}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/captcha")
async def get_captcha():
    """Get CAPTCHA image"""
    global scraper
    if not scraper:
        raise HTTPException(status_code=400, detail="Scraper not initialized")
    
    try:
        captcha_image = scraper.get_captcha_image()
        if captcha_image:
            # Convert to base64 for frontend display
            image_base64 = base64.b64encode(captcha_image).decode('utf-8')
            return {"success": True, "captcha_image": f"data:image/png;base64,{image_base64}"}
        else:
            return {"success": False, "message": "Failed to get CAPTCHA"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/search")
async def search_case(request: Request):
    """Search for a case"""
    global scraper, query_logger
    if not scraper:
        raise HTTPException(status_code=400, detail="Scraper not initialized")
    
    data = await request.json()
    
    # Extract search parameters for logging
    state = data.get("state")
    district = data.get("district")
    court_complex = data.get("court_complex")
    case_type = data.get("case_type")
    case_number = data.get("case_number")
    case_year = data.get("year")
    captcha_value = data.get("captcha_value")
    
    try:
        result = scraper.search_case_by_number(
            case_type_code=case_type,
            case_number=case_number,
            year=case_year,
            captcha_value=captcha_value,
            court_complex_code=court_complex
        )
        
        if result:
            # Log successful query
            query_logger.log_query(
                state=state,
                district=district,
                court_complex=court_complex,
                case_type=case_type,
                case_number=case_number,
                case_year=case_year,
                captcha_value=captcha_value,
                request_data=data,
                response_data=result,
                raw_json_response=result,
                success=True
            )
            return {"success": True, "case_details": result}
        else:
            # Log failed query
            query_logger.log_query(
                state=state,
                district=district,
                court_complex=court_complex,
                case_type=case_type,
                case_number=case_number,
                case_year=case_year,
                captcha_value=captcha_value,
                request_data=data,
                response_data=None,
                success=False,
                error_message="No case found or search failed"
            )
            return {"success": False, "message": "No case found or search failed"}
    except Exception as e:
        # Log error
        query_logger.log_query(
            state=state,
            district=district,
            court_complex=court_complex,
            case_type=case_type,
            case_number=case_number,
            case_year=case_year,
            captcha_value=captcha_value,
            request_data=data,
            response_data=None,
            success=False,
            error_message=str(e)
        )
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/logs")
async def get_logs(limit: int = 50):
    """Get recent query logs"""
    global query_logger
    try:
        logs = query_logger.get_recent_queries(limit)
        return {"success": True, "logs": logs}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/stats")
async def get_stats():
    """Get query statistics"""
    global query_logger
    try:
        stats = query_logger.get_query_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 