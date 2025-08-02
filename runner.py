from scraper import ECourtsScraper
import os
from PIL import Image
from io import BytesIO

def run_test_flow():
    """
    Simulates the entire scraping process to confirm the flow works.
    """
    # --- 1. CONFIGURATION ---
    DISTRICT_COURT_URL = "https://chamba.dcourts.gov.in"
    
    # --- 2. INITIALIZE SCRAPER AND SESSION ---
    print("Step 1: Initializing scraper session and getting cookies...")
    scraper = ECourtsScraper(DISTRICT_COURT_URL)
    
    if not scraper.initialize_session():
        print("Failed to initialize session. Exiting.")
        return
        
    print("\nSession initialized successfully.")
    
    # --- 3. GET COURT COMPLEX AND CASE TYPES (Simulated) ---
    print("\nStep 2: Simulating user selecting a court complex and getting case types...")
    court_complex_name = "Chamba"
    court_complex_code = scraper.court_complex_map.get(court_complex_name)
    
    if not court_complex_code:
        print(f"Court complex '{court_complex_name}' not found. Exiting.")
        return

    print(f"Selected court complex: {court_complex_name} (Code: {court_complex_code})")
    
    case_types = scraper.get_case_types(court_complex_code)
    if not case_types:
        print("Failed to get case types. Exiting.")
        return
    
    print("Case types fetched successfully.")
    
    # --- 4. SOLVE CAPTCHA (Manual Intervention) ---
    print("\nStep 3: Fetching and displaying CAPTCHA for manual solving...")
    captcha_image_data = scraper.get_captcha_image()
    if not captcha_image_data:
        print("Failed to get CAPTCHA image. Exiting.")
        return
        
    try:
        image = Image.open(BytesIO(captcha_image_data))
        image.show()
    except Exception as e:
        print(f"Could not open image automatically. Please save and view manually. Error: {e}")
    
    captcha_value = input("Please enter the CAPTCHA code shown in the image: ").strip()
    if not captcha_value:
        print("No CAPTCHA value entered. Exiting.")
        return
        
    # --- 5. PERFORM THE SEARCH ---
    print("\nStep 4: Performing the final case search...")
    case_type_name = "Motor Vehc Act"
    case_type_code = case_types.get(case_type_name)
    
    if not case_type_code:
        print(f"Case type '{case_type_name}' not found. Exiting.")
        return

    case_number = "1557"
    year = "2024"
    
    case_details = scraper.search_case_by_number(
        case_type_code, 
        case_number, 
        year, 
        captcha_value, 
        court_complex_code
    )
    
    if not case_details:
        print("Search failed. Check your CAPTCHA and try again.")
        return
        
    
    if case_details:
        print("\n--- Final Case Data ---")
        for key, value in case_details.items():
            if isinstance(value, dict):
                print(f"{key.capitalize()}:")
                for sub_key, sub_value in value.items():
                    print(f"  - {sub_key}: {sub_value}")
            elif isinstance(value, list):
                print(f"{key.capitalize()}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{key.capitalize()}: {value}")
    else:
        print("Failed to scrape final case details.")
        
    print("\nTest flow complete.")

if __name__ == "__main__":
    try:
        from scraper import ECourtsScraper
    except ImportError:
        print("Error: Could not import ECourtsScraper class. Make sure it's in a file named `scraper_class.py`.")
        exit()
        
    run_test_flow()