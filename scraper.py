import sys
import requests
from bs4 import BeautifulSoup

url = sys.argv[1]
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print("Title:")
print(soup.title.get_text().strip() 
      if soup.title 
      else "(no title found)")

print("\nBody:")
if soup.body:
    print(soup.body.get_text(separator=' ', strip=True))
else:    
    print("(no body found)")

print("\nLinks:")
for a in soup.find_all('a'):
    link = a.get('href')
    if link:
        print(link) 