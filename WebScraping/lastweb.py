import requests
from bs4 import BeautifulSoup

def scrape_indeed(search_query, location):
    
    url = f"https://in.indeed.com/jobs?q=&l=india?q={search_query}&l={location}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}  


    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content,  
 'html.parser')

    job_listings = soup.find_all('div', class_='jobsearch-JobCard')
    job_data = []

    for listing in job_listings:
        title = listing.find('h2').text.strip()
        company = listing.find('span', class_='company').text.strip()
        location = listing.find('span', class_='location').text.strip()  

        link = listing.find('a', class_='jobsearch-JobCard__link')['href']
        job_data.append({'title': title, 'company': company, 'location': location, 'link': link})

    return job_data

# Example usage
search_query = "data scientist"
location = "india"
results = scrape_indeed(search_query, location)

for job in results:
    print(job)