# ECourts Case Scraper Web Application

A modern web interface for searching and retrieving case details from the ECourts system. This application provides a sequential, step-by-step interface that guides users through the case search process.

## Features

- **Multi-State Support**: Supports all district courts across India with state and district selection
- **Sequential Form Flow**: Step-by-step form with progress tracking
- **Progress Sidebar**: Visual progress indicator showing current step and completion status
- **Dynamic Loading**: Court complexes and case types are loaded dynamically
- **CAPTCHA Support**: Built-in CAPTCHA image display and input
- **Comprehensive Results**: Displays all case details including:
  - Case information (type, filing number, registration details)
  - Case status (hearing dates, decision date, disposal nature)
  - FIR details (police station, FIR number)
  - Petitioners and respondents
  - Complete case history
  - Additional tables for ongoing cases (Acts, Orders with download links, Process Details)
- **Database Logging**: All queries and responses are logged to SQLite database
- **Admin Dashboard**: View query statistics, recent logs, and raw JSON responses
- **Query Analytics**: Track success rates, most searched states, and error patterns

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Access the Web Interface**:
   Open your browser and navigate to `http://localhost:8000`

## Usage

### Step-by-Step Process

1. **Select State**: Choose the state where your case was filed from the dropdown menu.

2. **Select District**: Choose the district court from the dynamically loaded options.

3. **Initialize Session**: Click the "Initialize Session" button to establish a connection with the selected district court.

4. **Select Court Complex**: Choose the court complex where your case was filed from the dropdown menu.

5. **Select Case Type**: Choose the appropriate case type from the dynamically loaded options.

6. **Enter Case Details**: Provide the case number and filing year.

7. **Solve CAPTCHA**: Enter the characters shown in the CAPTCHA image to verify you're a human user.

8. **View Results**: Review the comprehensive case details that are displayed in organized sections.

### Features

- **Progress Tracking**: The sidebar shows your current progress through the 6-step process
- **Form Validation**: Each step validates input before allowing progression
- **Error Handling**: Clear error messages for failed operations
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface using Tailwind CSS

## How the Scraping Works

The ECourts scraper operates through a multi-step process that mimics human interaction with the ECourts website:

### 1. Session Initialization
- **Initial Request**: Makes a GET request to the district court's homepage to establish a session
- **Cookie Management**: Captures and maintains essential cookies (`PHPSESSID`, `pll_language`) for session continuity
- **AJAX Setup**: Sends a POST request to `wp-admin/admin-ajax.php` with `action: 's3waas_pll_lang_cookie'` to explicitly establish session cookies

### 2. Dynamic Token Extraction
- **Hidden Fields**: Extracts dynamic tokens from the initial page response (e.g., `tok_...`, `scid`)
- **Session Validation**: These tokens are required for subsequent AJAX requests to prevent CSRF attacks
- **Request Headers**: Maintains browser-like headers including `Referer`, `Origin`, `X-Requested-With`, and proper `Cookie` headers

### 3. Court Complex and Case Type Loading
- **Court Complexes**: Fetches available court complexes via AJAX call to `wp-admin/admin-ajax.php`
- **Case Types**: Dynamically loads case types for the selected court complex
- **Payload Structure**: Each request includes extracted tokens, action parameters, and proper form data

### 4. CAPTCHA Handling
- **Image Retrieval**: Downloads CAPTCHA image from the court's CAPTCHA endpoint
- **Base64 Encoding**: Converts image to base64 for frontend display
- **User Input**: Captures user's CAPTCHA solution for verification

### 5. Case Search Process
- **Search Request**: Sends case details (number, year, type) along with CAPTCHA solution
- **Response Parsing**: Handles JSON responses containing HTML data in the `"data"` field
- **Multi-step Extraction**: For successful searches, extracts case number (`data-cno`) from search results

### 6. Case Details Retrieval
- **Secondary Request**: Makes another AJAX call with the extracted case number (`cino`)
- **HTML Parsing**: Uses BeautifulSoup to parse the detailed case information
- **Data Extraction**: Extracts structured data from multiple HTML tables:
  - **Case Details**: Filing number, registration date, case type
  - **Case Status**: Hearing dates, decision date, disposal nature
  - **FIR Details**: Police station, FIR number, registration date
  - **Parties**: Petitioners and respondents with their advocates
  - **Case History**: Complete chronological case timeline
  - **Additional Tables**: For ongoing cases, extracts "Acts", "Orders" (with download links), and "Process Details"

### 7. Error Handling and Logging
- **Database Logging**: All queries and responses are logged to SQLite database
- **Error Tracking**: Failed requests are logged with error messages
- **Session Recovery**: Handles session timeouts and connection issues
- **Graceful Degradation**: Provides clear error messages for various failure scenarios

### Technical Implementation Details

- **HTTP Session Management**: Uses `requests.Session()` for persistent cookies and headers
- **AJAX Replication**: Mimics browser AJAX behavior with proper headers and payloads
- **HTML Parsing**: BeautifulSoup for robust HTML parsing and data extraction
- **URL Construction**: Handles dynamic URL generation based on selected state/district
- **Modular Design**: Supports all district courts through the same scraping logic

### Security Considerations

- **Rate Limiting**: Respects server response times to avoid overwhelming the target
- **Session Validation**: Maintains proper session state throughout the process
- **CAPTCHA Compliance**: Requires human interaction for case searches
- **Error Recovery**: Gracefully handles network issues and server errors

## API Endpoints

The application provides the following API endpoints:

### Core Scraping Endpoints
- `GET /api/states` - Get all available states
- `POST /api/districts` - Get districts for a specific state
- `POST /api/initialize` - Initialize the scraper session for a district
- `GET /api/court-complexes` - Get available court complexes
- `POST /api/case-types` - Get case types for a court complex
- `GET /api/captcha` - Get CAPTCHA image
- `POST /api/search` - Search for a case

### Admin and Logging Endpoints
- `GET /api/logs` - Get recent query logs
- `GET /api/stats` - Get query statistics
- `GET /admin` - Admin dashboard interface

## File Structure

```
├── main.py                 # FastAPI application
├── scraper.py             # ECourts scraper logic
├── database.py            # SQLite database logging
├── requirements.txt       # Python dependencies
├── ecourts_data.json     # State and district court data
├── queries.db            # SQLite database for query logs
├── templates/
│   ├── index.html        # Main web interface
│   └── admin.html        # Admin dashboard
└── static/
    └── js/
        └── app.js        # Frontend JavaScript logic
```

## Technical Details

- **Backend**: FastAPI with async/await support
- **Frontend**: Vanilla JavaScript with Axios for API calls
- **Styling**: Tailwind CSS for responsive design
- **Icons**: Font Awesome for UI icons
- **Scraping**: BeautifulSoup for HTML parsing

## Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- Invalid user input
- CAPTCHA failures
- Case not found scenarios
- Session timeout issues

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Security Notes

- CAPTCHA verification prevents automated abuse
- Session management ensures proper authentication
- Input validation prevents injection attacks
- HTTPS recommended for production deployment

## Troubleshooting

1. **Session Initialization Fails**: Check internet connectivity and try refreshing the page
2. **CAPTCHA Not Loading**: Click the "Refresh CAPTCHA" button
3. **Case Not Found**: Verify the case number and year are correct
4. **Slow Loading**: The application may take a few seconds to load court complexes and case types

## Development

To modify the application:

1. **Add New Features**: Edit `main.py` for backend changes, `templates/index.html` for UI changes
2. **Modify Scraping Logic**: Edit `scraper.py` for changes to the scraping behavior
3. **Update Frontend Logic**: Edit `static/js/app.js` for JavaScript changes

## License

This project is for educational and research purposes. Please ensure compliance with the target website's terms of service. 