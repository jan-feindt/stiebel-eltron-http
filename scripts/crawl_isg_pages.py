"""Crawl ISG web interface to discover all available pages.

This script connects to a Stiebel Eltron ISG device and crawls the web interface
to discover all available sub-pages, extracting their URLs and headings.

Usage:
    python scripts/crawl_isg_pages.py <ISG_IP_ADDRESS>
    python scripts/crawl_isg_pages.py 192.168.1.100

Output:
    Prints a list of all discovered pages with:
    - URL path (e.g., /?s=1,0)
    - Page heading/title
"""

import sys
import re
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup


def get_page_heading(soup):
    """Extract the main heading from the page.
    
    ISG pages typically have headings in:
    - <div id="sub_nav"> with class "left main sifr" (most pages) - HIGHEST PRIORITY  
    - Table headers with class="head" (info pages)
    - <div id="content"> first <h1> or <h2>
    """
    # PRIORITY 1: Try to find the main heading in sub_nav (most common for ISG pages)
    sub_nav = soup.find('div', id='sub_nav')
    if sub_nav:
        # Use lambda to match multiple classes
        main_heading = sub_nav.find('div', class_=lambda c: c and isinstance(c, (str, list)) and ('left' in str(c) and 'main' in str(c) and 'sifr' in str(c)))
        if main_heading:
            text = main_heading.get_text(strip=True)
            # Skip generic controller title
            if text and text not in ['STIEBEL ELTRON Reglersteuerung', '']:
                return text
    
    # PRIORITY 2: Try to find first table header with class="head"
    head_row = soup.find('tr', class_='head')
    if head_row:
        title_cell = head_row.find('td', class_='title')
        if title_cell:
            return title_cell.get_text(strip=True)
    
    # PRIORITY 3: Try to find h1 or h2 in content area
    content = soup.find('div', id='content')
    if content:
        heading = content.find(['h1', 'h2'])
        if heading:
            text = heading.get_text(strip=True)
            # Skip generic help text
            if text and text != 'Hilfe':
                return text
    
    # PRIORITY 4: Try to find title in meta or title tag
    title = soup.find('title')
    if title:
        return title.get_text(strip=True)
    
    return "No heading found"


def extract_links(soup, base_url):
    """Extract all ISG page links from the navigation.
    
    ISG uses links like:
    - /?s=1,0 (info pages)
    - /?s=2,7 (diagnosis pages)
    - /?s=5,0 (external heat source)
    """
    links = set()
    
    # Find all <a> tags
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # ISG pages use query parameters like ?s=1,0
        if href.startswith('/?s=') or href.startswith('?s='):
            # Normalize to include leading /
            if not href.startswith('/'):
                href = '/' + href
            
            full_url = urljoin(base_url, href)
            links.add(href)
    
    return links


def crawl_isg(host):
    """Crawl the ISG web interface and discover all pages.
    
    Args:
        host: IP address or hostname of ISG device
        
    Returns:
        dict: Mapping of URL paths to page headings
    """
    if not host.startswith('http://') and not host.startswith('https://'):
        host = f'http://{host}'
    
    print(f"Crawling ISG at {host}...")
    print()
    
    visited = set()
    to_visit = {'/'}  # Start with the index page
    pages = {}
    failed_pages = []
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (ISG Page Crawler)'
    })
    
    while to_visit:
        path = to_visit.pop()
        if path in visited:
            continue
            
        visited.add(path)
        url = urljoin(host, path)
        
        try:
            print(f"Fetching: {path:30}", end=' ... ')
            response = session.get(url, timeout=30)
            response.raise_for_status()
            print("✓")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get page heading
            heading = get_page_heading(soup)
            pages[path] = heading
            
            # Extract new links to visit
            new_links = extract_links(soup, host)
            for link in new_links:
                if link not in visited:
                    to_visit.add(link)
                    
        except requests.Timeout:
            print("TIMEOUT (skipped)")
            failed_pages.append((path, "Timeout"))
        except requests.RequestException as e:
            print(f"ERROR")
            failed_pages.append((path, str(e)))
    
    if failed_pages:
        print("\n" + "="*80)
        print("FAILED PAGES (timeout or error):")
        print("="*80)
        for path, reason in failed_pages:
            print(f"  {path:30} {reason}")
    
    return pages


def print_results(pages):
    """Print discovered pages in a formatted table."""
    print()
    print("=" * 80)
    print("DISCOVERED ISG PAGES")
    print("=" * 80)
    print()
    
    # Sort by URL path
    sorted_pages = sorted(pages.items(), key=lambda x: x[0])
    
    # Group by section (first parameter in ?s=X,Y)
    sections = {}
    for path, heading in sorted_pages:
        if path == '/':
            section = 'Index'
        else:
            # Extract section from ?s=X,Y
            match = re.search(r'\?s=(\d+),', path)
            if match:
                section = f"Section {match.group(1)}"
            else:
                section = 'Other'
        
        if section not in sections:
            sections[section] = []
        sections[section].append((path, heading))
    
    # Print grouped results
    for section, section_pages in sorted(sections.items()):
        print(f"\n{section}:")
        print("-" * 80)
        for path, heading in section_pages:
            print(f"  {path:30} {heading}")
    
    print()
    print(f"Total pages found: {len(pages)}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        print("\nError: ISG IP address required")
        print("\nUsage:")
        print("  python scripts/crawl_isg_pages.py <ISG_IP_ADDRESS>")
        print("\nExample:")
        print("  python scripts/crawl_isg_pages.py 192.168.1.100")
        sys.exit(1)
    
    host = sys.argv[1]
    
    try:
        pages = crawl_isg(host)
        print_results(pages)
    except KeyboardInterrupt:
        print("\n\nCrawl interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
