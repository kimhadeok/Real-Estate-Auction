# Implementation Plan — Court Auction Crawler in `urlcheck.py`

This plan details how to write a Python script in [urlcheck.py](file:///d:/My-Dev/GitHub/Real-Estate-Auction/urlcheck.py) that uses Selenium to scrape the search result list from the Korean Court Auction site and save it to a CSV file.

## User Review Required

> [!IMPORTANT]
> - The script will use **Selenium** to dynamically load and interact with the page (WebSquare5).
> - We will run the Chrome browser in **headless mode** to fetch results.
> - The target search button ID specified by the user is `mf_wfm_mainFrame_btn_rletInit`. We will target this ID first, and also provide fallback/alternative logic to look for the general search button elements if that ID is not found or is configured differently on the page.

## Proposed Changes

### Scraping Script

#### [NEW] [urlcheck.py](file:///d:/My-Dev/GitHub/Real-Estate-Auction/urlcheck.py)
Create a Python script that:
1. Configures a headless Selenium Chrome WebDriver.
2. Navigates to `https://www.courtauction.go.kr/pgj/index.on?w2xPath=/pgj/ui/pgj100/PGJ151F00.xml`.
3. Waits for the DOM to load.
4. Clicks the search button with ID `mf_wfm_mainFrame_btn_rletInit` (as specified by the user) or its fallback elements.
5. Waits for the search results grid to load.
6. Parses the search results grid (locates the tables and rows).
7. Extracts columns (e.g. Court/Case number, Address/Details, Valuation, Court Department, Sale Date, Usage, Min Sale Price, Progress).
8. Exports the parsed data into a CSV file (e.g., `auction_results.csv`) using Pandas.
9. Safely closes the WebDriver.

## Verification Plan

### Automated Tests
- Run the script:
  `d:\My-Dev\GitHub\Real-Estate-Auction\.venv\Scripts\python.exe urlcheck.py`
- Verify that it successfully runs without exceptions and saves the output to a CSV file.

### Manual Verification
- Inspect the generated `auction_results.csv` to ensure all fields are correctly extracted.
