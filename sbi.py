#%%
import os
import time
from pathlib import Path

import dotenv
from playwright.sync_api import sync_playwright

dotenv.load_dotenv()

HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

PDF_DIR = os.environ.get("PDF_DIR", "./")
FETCH_ALL = os.environ.get("FETCH_ALL", "false").lower() == "true"

if not os.environ.get("SBI_ACCOUNT") or not os.environ.get("SBI_PASSWORD"):
    raise ValueError("SBI_ACCOUNT or SBI_PASSWORD is not set")

print("=== SBI PDF ===")
print("Run at", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS)
    context = browser.new_context(
        locale='ja-JP',
        accept_downloads=True,
    )
    page = context.new_page()
    page.goto('https://www.sbisec.co.jp/ETGate')
    page.locator("//div[@id='user_input']/input").fill(os.environ.get("SBI_ACCOUNT"))
    page.locator("//div[@id='password_input']/input").fill(os.environ.get("SBI_PASSWORD"))
    with page.expect_navigation():
        page.locator("//p[@class='sb-position-c']/input").click()
    page.wait_for_load_state("networkidle");
    page.locator("//li/a[contains(text(),'電子交付書面')]").last.click()

    with context.expect_page() as new_page_info:
        page.locator("//td[@id='browsing']/a").click()
        
    if new_page_info.value is not None:
        page.close()
        page = new_page_info.value
   
    page.wait_for_load_state("networkidle");
    total_count = int(page.locator("//div[contains(@class,'control__counter')]/span").inner_text())
    items = page.locator("//mat-accordion[contains(@class,'items')]/mat-expansion-panel")
    print(f"Found {items.count()=} items")
    while items.count() < total_count and items.count() < 100:
        page.evaluate("""
            () => {
                window.scrollTo(0,document.body.scrollHeight);
            }
        """);
        time.sleep(1)
        page.evaluate("""
            () => {
                window.scrollTo(0,0);
            }
        """);
        page.wait_for_load_state("networkidle");
        items = page.locator("//mat-accordion[contains(@class,'item')]/mat-expansion-panel")
        print(f"Found {items.count()=} items")
    print(f"Found {items.count()} items")
    for idx in range(0, items.count()):
        item = items.nth(idx)
        if not FETCH_ALL and item.locator("//mat-expansion-panel-header[not(contains(@class,'-read'))]").count()==0:
            continue
        item.click()
        page.wait_for_load_state("networkidle")
        with page.expect_download() as pdf_new_tab:
            download_btn = item.locator("//button[contains(@class,'-pdf')]").last
            download_btn.click(modifiers=['Alt'])
            pdf = pdf_new_tab.value
            date = item.locator("//span[@class='item__date']").inner_text()
            filename = item.locator("//span[@class='item__type']").inner_text()
            year_month = date.split('/')[0:2]
            pdf_file = Path(PDF_DIR)/ Path(f"{''.join(year_month)}/{date.replace('/','-')} {filename}.pdf")
            pdf_file.parent.mkdir(parents=True, exist_ok=True)
            if HEADLESS:
                print(f"save {pdf_file}")
                pdf.save_as(pdf_file)
            else:
                print("Skip pdf[%s] save, because headless is false" % pdf_file)
    print("Done")
    browser.close()

# %%
