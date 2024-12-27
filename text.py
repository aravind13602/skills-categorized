import requests
import json
import time

# Define the URL and headers for LinkedIn Data API
url = 'https://linkedin-data-api.p.rapidapi.com/get-company-posts?username=microsoft&start=0'
headers = {
    'x-rapidapi-host': 'linkedin-data-api.p.rapidapi.com',
    'x-rapidapi-key': '676274f451mshb24f00c92308af1p148d71jsneee4850c1b97'
}

# Function to fetch skill category dynamically using Lightcast API
def fetch_skill_category(skill_name):
    # Lightcast API URL and credentials
    client_id = 'mvzpk2p4fopw73db'  # Provided Client ID
    secret = 'dNU2qmTH'  # Provided Secret
    scope = 'emsi_open'  # Scope
    
    # Endpoint URL for Lightcast (formerly EMSI) to search skills
    api_url = f"https://api.lightcast.io/skills"

    # Prepare the request headers
    headers = {
        'Authorization': f'Bearer {get_access_token(client_id, secret, scope)}'  # Pass the token from the get_access_token function
    }

    try:
        # Request to search for the skill
        params = {'search': skill_name}
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                category = data["data"][0].get("category", "Unknown")
                return category
            else:
                print(f"No category found for {skill_name}")
                return "Unknown"
        else:
            print(f"Error fetching category for {skill_name}: {response.status_code} - {response.text}")
            return "Unknown"
    except Exception as e:
        print(f"Error occurred while fetching category for {skill_name}: {e}")
        return "Unknown"

# Function to get the access token from Lightcast using client credentials
def get_access_token(client_id, secret, scope):
    url = 'https://auth.emsicloud.com/connect/token'
    payload = {
        'client_id': client_id,
        'client_secret': secret,
        'grant_type': 'client_credentials',
        'scope': scope
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            token = response.json().get('access_token')
            return token
        else:
            print(f"Error getting access token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while getting access token: {e}")
        return None

# Function to extract skills from the posts (simple extraction for demonstration)
def extract_skills_from_posts(posts):
    skills = []
    
    # A list of common skills/keywords we might want to track in the posts
    common_keywords = ["AI", "Excel", "Tech", "Data", "Leadership", "Marketing", "Cloud", "Machine Learning", "Software Engineering"]
    
    for post in posts:
        # Extract skills from post content (assuming post['content'] contains text with skills)
        content = post.get('text', '')
        if not content:
            continue
        
        # Search for common keywords in the post text
        for keyword in common_keywords:
            if keyword.lower() in content.lower():  # Case insensitive matching
                skills.append(keyword)
    
    return skills

# Function to manage the rate limit (1000 requests per hour)
def manage_rate_limit(requests_made, max_requests=1000, interval=3600):
    if requests_made >= max_requests:
        print(f"Rate limit reached. Waiting for {interval} seconds...")
        time.sleep(interval)  # Wait for the time interval (1 hour = 3600 seconds)
        return 0  # Reset the request counter
    return requests_made

# Track the number of requests made
requests_made = 0

# Send the GET request to the LinkedIn Data API
try:
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        
        # Debugging: Print the response structure to check what data we have
        print(f"Response Data: {json.dumps(data, indent=4)}")

        # Get posts from the response
        posts = data.get("data", [])
        if not posts:
            print("No posts found in the response.")
        
        # Extract skills from the posts
        skills = extract_skills_from_posts(posts)
        if not skills:
            print("No skills found in the posts.")
        
        # Categorize the extracted skills dynamically
        categorized_skills = []
        for skill in skills:
            category = fetch_skill_category(skill)
            categorized_skills.append({
                "skill": skill,
                "category": category
            })
        
        # Save the categorized skills to a JSON file
        output_file = 'categorized_skills.json'
        with open(output_file, 'w') as f:
            json.dump(categorized_skills, f, indent=4)
        
        print(f"Categorized skills have been saved to '{output_file}'.")
        
        # Increment the request count and manage rate limit
        requests_made += 1
        requests_made = manage_rate_limit(requests_made)

    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")
