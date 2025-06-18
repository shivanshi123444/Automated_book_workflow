# src/scraper.py
import asyncio
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from config import RAW_CONTENT_DIR, SCREENSHOTS_DIR

async def fetch_content_and_screenshot(url: str, chapter_name: str) -> str | None:
    """
    Fetches content from a URL and saves a screenshot.
    Returns the extracted text content, or None if scraping fails.
    """
    print(f"Fetching content and screenshot for: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded") # Wait until DOM is loaded

            # Save screenshot
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{chapter_name}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to: {screenshot_path}")

            # Extract text content
            content_html = await page.content()
            soup = BeautifulSoup(content_html, 'html.parser')

            # --- IMPORTANT: Adjust the selector based on the actual website structure ---
            # For en.wikisource.org, the main content is typically within a div with id 'mw-content-text'.
            # If the structure changes or you target a different site, inspect the page (F12 in browser)
            # to find the most appropriate container for the chapter text.
            content_div = soup.find('div', id='mw-content-text')
            if content_div:
                # Correct way to find and remove multiple elements:
                # Use .select() with a CSS selector string to target tags to remove.
                for unwanted_tag in content_div.select('script, style, nav, sup, span, div.printfooter, table, .mw-editsection'):
                    unwanted_tag.extract() # Remove these elements from the parsed content

                text_content = content_div.get_text(separator='\n', strip=True)
            else:
                # Fallback to getting all visible text if specific div not found
                text_content = soup.get_text(separator='\n', strip=True)
                print("Warning: Specific content div (id='mw-content-text') not found. Extracted all visible text.")

            # Save raw content to a file
            raw_content_path = os.path.join(RAW_CONTENT_DIR, f"{chapter_name}.txt")
            with open(raw_content_path, "w", encoding="utf-8") as f:
                f.write(text_content)
            print(f"Raw content saved to: {raw_content_path}")

            await browser.close()
            return text_content
    except Exception as e:
        print(f"Error during scraping from {url}: {e}")
        return None

# Example usage for testing this module independently
async def main_scraper_test():
    url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
    chapter_name = "The_Gates_of_Morning_Book_1_Chapter_1"
    content = await fetch_content_and_screenshot(url, chapter_name)
    if content:
        print("\n--- Extracted Content Sample (First 500 chars) ---")
        print(content[:500])
        print("\nScraping test successful.") # Indicate success
    else:
        print("Scraping failed during test.") # Still print if content is None

if __name__ == "__main__":
    asyncio.run(main_scraper_test())
