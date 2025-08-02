import requests
from bs4 import BeautifulSoup
import json

def get_states():
    """Get all states from ECourts"""
    print("Getting states...")
    url = "https://ecourts.gov.in/ecourts_home/index.php"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    states = {}
    states_list = soup.find('ul', class_='state-district')
    
    for li in states_list.find_all('li'):
        link = li.find('a')
        if link:
            state_name = link.text.strip()
            state_url = "https://ecourts.gov.in" + link.get('href')
            states[state_name] = {'url': state_url, 'districts': {}}
            print(f"Found: {state_name}")
    
    return states

def get_districts(state_name, state_url):
    """Get districts for a state"""
    print(f"Getting districts for {state_name}...")
    
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    districts = {}
    districts_list = soup.find('ul', class_='state-district')
    
    for li in districts_list.find_all('li'):
        link = li.find('a')
        if link:
            district_name = link.text.strip()
            court_url = link.get('href')
            districts[district_name] = {'court_url': court_url, 'state': state_name}
            print(f"  Found: {district_name} -> {court_url}")
    
    return districts

# Main execution
print("Starting ECourts data collection...")

states = get_states()
print(f"\nFound {len(states)} states")

# Get districts for each state
for state_name, state_data in states.items():
    districts = get_districts(state_name, state_data['url'])
    state_data['districts'] = districts

# Save to JSON
with open('ecourts_data.json', 'w', encoding='utf-8') as f:
    json.dump(states, f, indent=2, ensure_ascii=False)

print(f"\nData saved to ecourts_data.json")
print(f"Total states: {len(states)}")
print(f"Total districts: {sum(len(state['districts']) for state in states.values())}") 