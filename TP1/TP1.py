import urllib
import urllib.robotparser
import re
import json
import time
from collections import deque
from bs4 import BeautifulSoup


def print_html_all(url: str):
    """
    Prints all the text from a page with a given url.
    """
    with urllib.request.urlopen(url) as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, "html.parser")
    print(soup.prettify())


def get_html_components(url: str) -> dict:
    """
    Extracts all the components needed (title, description and links) from a page with a given url.
    """
    with urllib.request.urlopen(url) as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, "html.parser")

    title = soup.title
    if title is not None:
        title = title.string
    else:
        title = ""

    description = soup.find("p", class_="product-description")
    if description is not None:
        description = description.get_text()
    else:
        description = ""

    links = []
    all_links = soup.find_all(href=re.compile(r"^http"))  # To only keep real links
    if all_links is not None:
        for link in all_links:
            links.append(link.get("href"))

    output = {
        "url": url,
        "title": title,
        "description": description,
        "links": links,
    }
    return output


def get_robots_url(url: str) -> str:
    """
    Gives the robots.txt's url from a page with a given url.
    """
    o = urllib.parse.urlparse(url)
    url_robot = f"{o.scheme}://{o.netloc}/robots.txt"
    return url_robot


def is_allowed(
    url: str,
    rp: urllib.robotparser.RobotFileParser,
    useragent: str = "*",
) -> bool:
    """
    Returns True if a page with a given url can be parsed by the crawler, False otherwise.
    """
    return rp.can_fetch(useragent, url)


def update_queue(
    queue: deque, visited: set, new_urls: list, rp: urllib.robotparser.RobotFileParser
) -> deque:
    """
    Gives the updated queue.
    """
    for url in new_urls:
        if (
            is_allowed(url, rp) and not url in visited
        ):  # We check if the page can be parsed and if it has not already been
            o = urllib.parse.urlparse(url)
            if "product" in o.path:  # To priorize pages with 'product' token
                queue.appendleft(url)
            else:
                queue.append(url)
    return queue


def crawler(url: str, path_out: str, n_max: int = 50):
    """
    Crawls a number of pages starting from a given url.
    """
    i = 0
    data = []
    queue = deque([url])
    visited = set()

    robot_url = get_robots_url(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robot_url)
    rp.read()

    with open(path_out, "w", encoding="utf-8") as f:
        while i < n_max and queue:  # We only want to extract n_max pages
            current_url = queue.popleft()  # We remove the first url from the queue
            if (
                current_url in visited
            ):  # If the page has already been crawled, we skip it
                continue

            visited.add(current_url)
            new = get_html_components(
                current_url
            )  # We get the data we need from the page
            ligne = json.dumps(new, ensure_ascii=False)
            f.write(ligne + "\n")
            init = i == 0
            queue = update_queue(queue, visited, new["links"], rp)
            time.sleep(0.5)  # To avoid overload
            print(f"Page {i+1}/{n_max} has been crawled!")
            i += 1


if __name__ == "__main__":
    url = "https://web-scraping.dev/products"
    path_out = "TP1/output/products.jsonl"
    n_max = 50
    crawler(url, path_out, n_max)

    with open(path_out, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f if line.strip()]

    data.sort(key=lambda x: x.get("url", ""))

    with open(path_out, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(d, ensure_ascii=False) + "\n" for d in data)
