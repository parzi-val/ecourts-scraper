import requests
from bs4 import BeautifulSoup
import re
import json
import time

class ECourtsScraper:
    def __init__(self, district_court_url):
        """
        Initializes the scraper with a base URL and a requests session.
        The session object will automatically handle cookies.
        """
        self.base_url = district_court_url
        self.session = requests.Session()
        self.dynamic_tokens = {}
        self.case_type_map = {}
        self.court_complex_map = {}
        self.captcha_url = ""

    def _fetch_page_content(self, url, headers=None, data=None):
        """
        Helper to fetch a page and handle potential errors.
        Uses POST if data is provided, otherwise GET.
        """
        try:
            if data:
                response = self.session.post(url, data=data, headers=headers, timeout=15)
            else:
                response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def initialize_session(self):
        """
        Performs the full session initialization flow:
        1. Initial page load to get dynamic tokens.
        2. AJAX call to set the PHPSESSID cookie.
        3. Scrapes court complex map.
        4. Constructs the CAPTCHA URL.
        """
        # Ensure base_url doesn't end with slash to avoid double slashes
        base_url = self.base_url.rstrip('/')
        search_url = f"{base_url}/case-status-search-by-case-number/"
        print(f"Initializing session by fetching: {search_url}")

        # Step 1: Initial page load to get dynamic tokens
        initial_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en-IN;q=0.9,en;q=0.8,ml;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        response = self._fetch_page_content(search_url, headers=initial_headers)
        if not response:
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        
        self.dynamic_tokens = {}
        for hidden_input in soup.find_all('input', type='hidden'):
            if 'name' in hidden_input.attrs and hidden_input['name'].startswith('tok_'):
                self.dynamic_tokens[hidden_input['name']] = hidden_input['value']
            elif 'name' in hidden_input.attrs and hidden_input['name'] == 'scid':
                self.dynamic_tokens['scid'] = hidden_input['value']
        
        if not self.dynamic_tokens:
            print("Failed to find dynamic tokens. The HTML structure might have changed.")
            return False
        
        print(f"Dynamic tokens found: {self.dynamic_tokens}")

        # Step 2: Make the POST request to set the session cookie
        print("Making POST request to establish session and get cookies...")
        payload = {
            'time': int(time.time()),
            'lang': 'en',
            'action': 's3waas_pll_lang_cookie'
        }
        # Build cookie string from session cookies
        cookie_string = '; '.join([f"{name}={value}" for name, value in self.session.cookies.items()])
        
        # Ensure base_url doesn't end with slash to avoid double slashes
        base_url = self.base_url.rstrip('/')
        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en-IN;q=0.9,en;q=0.8,ml;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': base_url,
            'Referer': search_url,
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Add cookie header if cookies exist
        if cookie_string:
            headers['Cookie'] = cookie_string
        cookie_response = self._fetch_page_content(
            f"{base_url}/wp-admin/admin-ajax.php",
            headers=headers,
            data=payload
        )
        if not cookie_response:
            print("Failed to get session cookie. Exiting.")
            return False
            
        print("Session cookie established successfully.")

        # Step 3: Scrape the court complex options
        court_complex_select = soup.find('select', {'name': 'est_code'})
        if court_complex_select:
            for option in court_complex_select.find_all('option'):
                if option.text.strip() and 'value' in option.attrs:
                    self.court_complex_map[option.text.strip()] = option['value']
        else:
            print("Failed to find 'est_code' select element.")
            return False
        
        print(f"Court complexes found: {self.court_complex_map}")
        
        # Step 4: Construct CAPTCHA URL using the scid token
        if 'scid' in self.dynamic_tokens:
            # Ensure base_url doesn't end with slash to avoid double slashes
            base_url = self.base_url.rstrip('/')
            self.captcha_url = f"{base_url}/?_siwp_captcha&id={self.dynamic_tokens['scid']}"
        
        print(f"CAPTCHA URL constructed: {self.captcha_url}")
        
        return True

    def get_captcha_image(self):
        """Fetches the CAPTCHA image and returns its binary content."""
        if not self.captcha_url:
            print("Session not initialized. Please run initialize_session() first.")
            return None
            
        print(f"Fetching CAPTCHA image from: {self.captcha_url}")
        response = self._fetch_page_content(self.captcha_url)
        if response:
            return response.content
        return None

    def get_case_types(self, court_complex_code):
        """
        Fetches the case types for a given court complex code using an AJAX call.
        Returns a dictionary mapping case type names to their codes.
        """
        payload = {
            'action': 'get_case_types',
            'est_code': court_complex_code,
            'service_type': 'courtComplex',
            'es_ajax_request': '1',
            **self.dynamic_tokens  # Add dynamic tokens to payload
        }
        
        # Build cookie string from session cookies
        cookie_string = '; '.join([f"{name}={value}" for name, value in self.session.cookies.items()])
        
        # Ensure base_url doesn't end with slash to avoid double slashes
        base_url = self.base_url.rstrip('/')
        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en-IN;q=0.9,en;q=0.8,ml;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': base_url,
            'Referer': f"{base_url}/case-status-search-by-case-number/",
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Add cookie header if cookies exist
        if cookie_string:
            headers['Cookie'] = cookie_string
        
        print(f"Fetching case types for {court_complex_code}...")
        response = self._fetch_page_content(
            f"{base_url}/wp-admin/admin-ajax.php",
            headers=headers,
            data=payload
        )
        if not response:
            print(f"Case types request failed. Response status: {response.status_code if response else 'No response'}")
            print(f"Case types response text: {response.text if response else 'No response'}")
            return {}

        try:
            json_data = response.json()
            if not json_data.get('success'):
                print("Failed to get case types from API.")
                return {}

            soup = BeautifulSoup(json_data['data'], 'html.parser')
            case_types = {}
            for option in soup.find_all('option'):
                if 'value' in option.attrs and option['value'].isdigit():
                    case_types[option.text.strip()] = option['value']
            
            self.case_type_map = case_types
            print("Case types successfully extracted.")
            return case_types
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing case types response: {e}")
            return {}

    def search_case_by_number(self, case_type_code, case_number, year, captcha_value, court_complex_code):
        """
        Performs the main search request and returns the URL
        to the detailed case page.
        """
        print(f"Searching for case: {case_type_code}/{case_number}/{year}...")
        
        # Build the payload using a combination of static and dynamic values
        payload = {
            'service_type': 'courtComplex',
            'est_code': court_complex_code,
            'case_type': case_type_code,
            'reg_no': case_number,
            'reg_year': year,
            'siwp_captcha_value': captcha_value,
            'es_ajax_request': '1',
            'submit': 'Search',
            'action': 'get_cases',
            **self.dynamic_tokens  # Add dynamic tokens to payload
        }
        
        # Build cookie string from session cookies
        cookie_string = '; '.join([f"{name}={value}" for name, value in self.session.cookies.items()])
        
        # Ensure base_url doesn't end with slash to avoid double slashes
        base_url = self.base_url.rstrip('/')
        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en-IN;q=0.9,en;q=0.8,ml;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': base_url,
            'Referer': f"{base_url}/case-status-search-by-case-number/",
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Add cookie header if cookies exist
        if cookie_string:
            headers['Cookie'] = cookie_string
        
        
        response = self._fetch_page_content(
            f"{base_url}/wp-admin/admin-ajax.php",
            headers=headers,
            data=payload
        )
        if not response:
            print(f"Search request failed. Response status: {response.status_code if response else 'No response'}")
            print(f"Search response text: {response.text if response else 'No response'}")
            return None

        try:
            json_data = response.json()
            if not json_data.get('success'):
                print(f"Search failed or no cases found. Server response: {response.text}")
                return None
            
            # Save the HTML response to a file for debugging
            with open('search_response.html', 'w', encoding='utf-8') as f:
                f.write(json_data['data'])
            print("Search response HTML saved to 'search_response.html'")
            
            soup = BeautifulSoup(json_data['data'], 'html.parser')
            
            # Look for the case number in the response
            case_div = soup.find('a', {'data-cno': True})
            if case_div:
                cino = case_div.get('data-cno')
                print(f"Found case number: {cino}")
                
                # Call the separate function to get case details
                return self.get_case_details(cino, headers)
            else:
                print("Could not find case number in the results.")
                return None
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing final search response: {e}")
            return None

    def get_case_details(self, cino, headers):
        """
        Makes a POST request to get the case details URL using the CINO.
        Returns the case details URL or None if failed.
        """
        print(f"\nStep 5: Getting case details URL for CINO: {cino}")
        
        # Build the payload for case details request
        case_details_payload = {
            'cino': cino,
            'action': 'get_cnr_details',
            'es_ajax_request': '1'
        }
        
        
        
        # Ensure base_url doesn't end with slash to avoid double slashes
        base_url = self.base_url.rstrip('/')
        
        # Make the POST request to get case details
        case_details_response = self._fetch_page_content(
            f"{base_url}/wp-admin/admin-ajax.php",
            headers=headers,
            data=case_details_payload
        )
        
        if not case_details_response:
            print(f"Case details request failed. Response status: {case_details_response.status_code if case_details_response else 'No response'}")
            print(f"Case details response text: {case_details_response.text if case_details_response else 'No response'}")
            return None
        
        
        
        try:
            json_data = json.loads(case_details_response.text)
            # The HTML is returned as a JSON string with escaped characters
            html_content = json_data.get("data", "")
            
            # Save the HTML response to a file for debugging
            with open('case_details_response.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("Case details response HTML saved to 'case_details_response.html'")
            
            # Parse the HTML response to extract case details
            soup = BeautifulSoup(html_content, 'html.parser')
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
        
        # Extract case details from the tables
        case_details = {}
        
        # Extract Case Details table - FIXED SELECTOR
        case_details_table = soup.find('table', class_='data-table-1')
        if case_details_table and case_details_table.find('caption', string='Case Details'):
            tbody = case_details_table.find('tbody')
            if tbody:
                row = tbody.find('tr')
                if row:
                    cells = row.find_all('td')
                    if len(cells) >= 6:
                        case_details['case_type'] = cells[0].text.strip()
                        case_details['filing_number'] = cells[1].text.strip()
                        case_details['filing_date'] = cells[2].text.strip()
                        case_details['registration_number'] = cells[3].text.strip()
                        case_details['registration_date'] = cells[4].text.strip()
                        case_details['cnr_number'] = cells[5].text.strip()
        
        # Extract Case Status table - FIXED SELECTOR
        case_status_tables = soup.find_all('table', class_='data-table-1')
        for table in case_status_tables:
            caption = table.find('caption')
            if caption and caption.string == 'Case Status':
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    if row:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            case_details['first_hearing_date'] = cells[0].text.strip()
                            case_details['decision_date'] = cells[1].text.strip()
                            case_details['case_status'] = cells[2].text.strip()
                            case_details['nature_of_disposal'] = cells[3].text.strip()
                            case_details['court_number_and_judge'] = cells[4].text.strip()
                break
        
        # Extract Petitioner and Respondent info - STRUCTURE IS CORRECT
        petitioner_section = soup.find('h5', string='Petitioner and Advocate')
        if petitioner_section:
            petitioner_div = petitioner_section.find_next('div', class_='Petitioner')
            if petitioner_div:
                petitioner_list = petitioner_div.find('ul')
                if petitioner_list:
                    petitioner_items = petitioner_list.find_all('li')
                    case_details['petitioners'] = [item.find('p').text.strip() for item in petitioner_items if item.find('p')]
        
        respondent_section = soup.find('h5', string='Respondent and Advocate')
        if respondent_section:
            respondent_div = respondent_section.find_next('div', class_='respondent')
            if respondent_div:
                respondent_list = respondent_div.find('ul')
                if respondent_list:
                    respondent_items = respondent_list.find_all('li')
                    case_details['respondents'] = [item.find('p').text.strip() for item in respondent_items if item.find('p')]
        
        # Extract FIR Details - NEW SECTION THAT WAS MISSING
        fir_tables = soup.find_all('table', class_='data-table-1')
        for table in fir_tables:
            caption = table.find('caption')
            if caption and caption.string == 'FIR Details':
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    if row:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            case_details['police_station'] = cells[0].text.strip()
                            case_details['fir_number'] = cells[1].text.strip()
                            case_details['fir_year'] = cells[2].text.strip()
                break
        
                 # Extract Case History - FIXED SELECTOR AND BUSINESS DATE EXTRACTION
        case_history_tables = soup.find_all('table', class_='data-table-1')
        for table in case_history_tables:
            caption = table.find('caption')
            if caption and caption.string == 'Case History':
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    case_details['case_history'] = []
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            # For business date, extract text from the link if it exists
                            business_date_cell = cells[2]
                            business_date_link = business_date_cell.find('a')
                            business_date = business_date_link.text.strip() if business_date_link else business_date_cell.text.strip()
                            
                            history_entry = {
                                'registration_number': cells[0].text.strip(),
                                'judge': cells[1].text.strip(),
                                'business_date': business_date,
                                'hearing_date': cells[3].text.strip(),
                                'purpose': cells[4].text.strip()
                            }
                            case_details['case_history'].append(history_entry)
                break
        
        # Extract Acts - NEW SECTION FOR ONGOING CASES
        acts_tables = soup.find_all('table', class_='data-table-1')
        for table in acts_tables:
            caption = table.find('caption')
            if caption and caption.string == 'Acts':
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    case_details['acts'] = []
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            act_entry = {
                                'under_act': cells[0].text.strip(),
                                'under_section': cells[1].text.strip()
                            }
                            case_details['acts'].append(act_entry)
                break
        
        # Extract Orders - NEW SECTION FOR ONGOING CASES (WITH DOWNLOAD LINKS)
        orders_tables = soup.find_all('table', class_='data-table-1')
        for table in orders_tables:
            caption = table.find('caption')
            if caption and caption.string == 'Orders':
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    case_details['orders'] = []
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            # Extract order details and download link if present
                            order_number = cells[0].text.strip()
                            order_date = cells[1].text.strip()
                            order_details_cell = cells[2]
                            
                            # Check if there's a download link
                            download_link = None
                            order_details_text = order_details_cell.text.strip()
                            
                            link_element = order_details_cell.find('a')
                            if link_element and 'href' in link_element.attrs:
                                download_link = link_element['href']
                                order_details_text = link_element.text.strip()
                            
                            order_entry = {
                                'order_number': order_number,
                                'order_date': order_date,
                                'order_details': order_details_text,
                                'download_link': download_link
                            }
                            case_details['orders'].append(order_entry)
                break
        
        # Extract Process Details - NEW SECTION FOR ONGOING CASES
        process_tables = soup.find_all('table', class_='data-table-1')
        for table in process_tables:
            caption = table.find('caption')
            if caption and caption.string == 'Process Details':
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    case_details['process_details'] = []
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            process_entry = {
                                'process_id': cells[0].text.strip(),
                                'process_date': cells[1].text.strip(),
                                'process_title': cells[2].text.strip(),
                                'party_name': cells[3].text.strip(),
                                'issued_process': cells[4].text.strip()
                            }
                            case_details['process_details'].append(process_entry)
                break
        
        print(f"Successfully extracted case details: {case_details}")
        return case_details