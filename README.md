# ECourts Case Scraper Web Application

A modern web interface for searching and retrieving case details from the ECourts system. This application provides a sequential, step-by-step interface that guides users through the case search process.

## Features

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

1. **Initialize Session**: Click the "Initialize Session" button to establish a connection with the ECourts system.

2. **Select Court Complex**: Choose the court complex where your case was filed from the dropdown menu.

3. **Select Case Type**: Choose the appropriate case type from the dynamically loaded options.

4. **Enter Case Details**: Provide the case number and filing year.

5. **Solve CAPTCHA**: Enter the characters shown in the CAPTCHA image to verify you're a human user.

6. **View Results**: Review the comprehensive case details that are displayed in organized sections.

### Features

- **Progress Tracking**: The sidebar shows your current progress through the 6-step process
- **Form Validation**: Each step validates input before allowing progression
- **Error Handling**: Clear error messages for failed operations
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface using Tailwind CSS

## API Endpoints

The application provides the following API endpoints:

- `POST /api/initialize` - Initialize the scraper session
- `GET /api/court-complexes` - Get available court complexes
- `POST /api/case-types` - Get case types for a court complex
- `GET /api/captcha` - Get CAPTCHA image
- `POST /api/search` - Search for a case

## File Structure

```
├── main.py                 # FastAPI application
├── scraper.py             # ECourts scraper logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
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