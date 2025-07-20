from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

# ==============================
# CONFIG
# ==============================
START_URL = "https://kon-1809--konnect-op.netlify.app/dashboard/opportunity-matrix/"

WAIT_TIME = 0.2  # ⚡️ Faster

# ==============================
# SETUP SELENIUM
# ==============================
options = Options()
# Uncomment to run headless after login
# options.add_argument("--headless=new")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(START_URL)

print("🔑 Please log in manually in the opened browser window.")
input("✅ After you finish logging in and the matrix grid is fully loaded, press ENTER here to continue...")

wait = WebDriverWait(driver, 60)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='cellContent']")))

print("✅ Grid loaded. Extracting headers...")

# ==============================
# EXTRACT HEADERS
# ==============================
origins_elements = driver.find_elements(By.CSS_SELECTOR, "div.cursor-pointer.d-flex.justify-content-center")
origins = [o.text.strip().split("\n")[0] for o in origins_elements if o.text.strip()]
print(f"✅ Found {len(origins)} origins.")

dest_elements = driver.find_elements(By.CSS_SELECTOR, "div.tx-14.cursor-pointer.d-flex.align-items-center.justify-content-center")
destinations = [d.text.strip() for d in dest_elements if d.text.strip()]
print(f"✅ Found {len(destinations)} destinations.")

# ==============================
# ASK USER FOR START ORIGIN
# ==============================
print("✅ Origins found:")
for idx, name in enumerate(origins):
    print(f"{idx}: {name}")

start_origin_name = input("\n💬 Enter origin name to start from (exact, case sensitive). Leave empty to start from first: ").strip()

if start_origin_name:
    try:
        START_ROW = origins.index(start_origin_name)
    except ValueError:
        print("❌ Origin name not found. Starting from first.")
        START_ROW = 0
else:
    START_ROW = 0

print(f"✅ Will start from row index: {START_ROW} ({origins[START_ROW]})")

# ==============================
# Prepare CSV
# ==============================
csv_file = "opportunity_matrix_data.csv"
file_exists = os.path.exists(csv_file)

if not file_exists:
    with open(csv_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Origin", "Destination", "Dest Pop", "Distance", "Cell Text"])

# ==============================
# Start scraping
# ==============================
for row_idx in range(START_ROW, len(origins)):
    origin_name = origins[row_idx]
    
    for col_idx, dest_name in enumerate(destinations):
        x_offset = col_idx * 150
        y_offset = row_idx * 150
        driver.execute_script("window.scrollTo(arguments[0], arguments[1]);", x_offset, y_offset)
        time.sleep(WAIT_TIME)

        cells = driver.find_elements(By.CSS_SELECTOR, "div[class*='cellContent']")

        cell_saved = False
        for cell in cells:
            try:
                text = cell.text.strip()
                if not text:
                    continue
            except:
                continue

            distance = "NA"
            dest_pop = "NA"
            for line in text.splitlines():
                if "Distancia:" in line:
                    distance = line.split(":")[1].strip()
                if "Dest Pop:" in line:
                    dest_pop = line.split(":")[1].strip()

            # Save regardless of conditions if you'd like; or keep this filter
            if dest_pop in ["NA", "0", ""] or distance in ["NA", "0 km", ""]:
                with open(csv_file, "a", newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([origin_name, dest_name, dest_pop, distance, text])
                print(f"✅ Saved: {origin_name} → {dest_name} (Dest Pop: {dest_pop}, Distance: {distance})")
                cell_saved = True
                break

        # Save empty row if nothing saved
        if not cell_saved:
            with open(csv_file, "a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([origin_name, dest_name, "NA", "NA", ""])
            print(f"⚠️ Empty: {origin_name} → {dest_name}")

print("✅ All data saved to 'opportunity_matrix_data.csv'.")
driver.quit()
#aayash_ahmad_bhat