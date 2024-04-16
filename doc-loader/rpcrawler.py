import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import time
from urllib.parse import urljoin, urlparse

# Target domain
TARGET_DOMAIN = "docs.redpanda.com"
TARGET_VERSION = "/beta"
REDPANDA_SERVER = "localhost:19092"

# Create a Kafka producer
producer = KafkaProducer(
  bootstrap_servers=REDPANDA_SERVER,
  value_serializer=lambda v: v.encode('utf-8')
)


# Base URL
base_url = 'https://docs.redpanda.com/beta/home/'

def processDoc(url):
    # Send the document to Kafka
    producer.send("urls",url)
    producer.flush()


def is_target_version(url):
    """Check if the URL is within the target domain and path."""
    parsed_url = urlparse(url)
    print(f"Is Beta: {parsed_url.path.startswith(TARGET_VERSION)} and  url: {url} ")
    return parsed_url.path.startswith(TARGET_VERSION)


def crawl(url, visited=set()):
    print(f"Crawling: {url}")
    """Recursively crawl pages from the starting URL."""
    if url in visited:
        return
    else:
        visited.add(url)
    if url is is_target_version(url):
        processDoc(url)
    
    try:
        # Delay in seconds
        time.sleep(0.5)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Parse the HTML
            current_base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(response.url))
            soup = BeautifulSoup(response.text, 'lxml')
            for link in soup.find_all('a', href=True):
                href = link['href']
                next_page = urljoin(current_base_url, href)
                
                if next_page not in visited:
                    crawl(next_page, visited)
    except Exception as e:
        print(f"Failed to crawl {url}: {e}")

# Start crawling from the base URL
crawl(base_url)

print("Crawling complete.")
