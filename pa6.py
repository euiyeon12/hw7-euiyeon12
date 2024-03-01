import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urljoin

# Function to get the HTML content of a URL
def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    return response.content

# Function to extract course information from a course page
def extract_course_info(course_url):
    course_page = get_page(course_url)
    soup = BeautifulSoup(course_page, 'html.parser')

    # Extract relevant information
    course_number = soup.find('div', class_='course-number').text.strip()
    description = soup.find('div', class_='course-description').text.strip()
    
    # Find all the detail rows
    detail_rows = soup.find_all('div', class_='course-section')

    terms_offered = ""
    equivalent_courses = ""
    prerequisites = ""
    instructors = ""

    for row in detail_rows:
        label = row.find('span', class_='course-section-label').text.strip()
        value = row.find('span', class_='course-section-value').text.strip()
        
        if label == "Terms Offered:":
            terms_offered = value
        elif label == "Equivalent Courses:":
            equivalent_courses = value
        elif label == "Prerequisite(s):":
            prerequisites = value
        elif label == "Instructor(s):":
            instructors = value

    return [course_number, description, terms_offered, equivalent_courses, prerequisites, instructors]

# Main function to crawl the catalog and save data to CSV
def scrape_catalog(url):
    visited_urls = set()
    courses_data = []

    # Function to process a page
    def process_page(page_url):
        if page_url in visited_urls:
            return
        print("Processing:", page_url)
        visited_urls.add(page_url)

        page_content = get_page(page_url)
        soup = BeautifulSoup(page_content, 'html.parser')

        # Find all course links on the page
        course_links = soup.select('.courseblock a[href^="http://collegecatalog.uchicago.edu"]')
        for course_link in course_links:
            course_url = course_link['href']
            course_data = extract_course_info(course_url)
            courses_data.append(course_data)

        # Find next page link
        next_page_link = soup.find('a', class_='next')
        if next_page_link:
            next_page_url = urljoin(page_url, next_page_link['href'])
            time.sleep(3)  # Wait for 3 seconds before next request
            process_page(next_page_url)

    process_page(url)

    # Save data to CSV
    with open('uchicago_catalog.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Number', 'Description', 'Terms Offered', 'Equivalent Courses', 'Prerequisites', 'Instructors'])
        writer.writerows(courses_data)

    print("Scraping complete. Data saved to 'uchicago_catalog.csv'")

if __name__ == "__main__":
    base_url = 'http://collegecatalog.uchicago.edu'
    scrape_catalog(base_url)
