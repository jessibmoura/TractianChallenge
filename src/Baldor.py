from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from loguru import logger
from bs4 import BeautifulSoup
import requests
import json
import os
import random, time
import time

class Baldor:
    """
        A web scraping class for extracting product information from the Baldor Electric Company catalog.

        This class uses Selenium WebDriver to navigate through the Baldor website, handle cookie consent popups,
        interact with product category pages, and extract detailed information such as specifications, manuals,
        and images. Collected data is saved locally in JSON format along with any associated assets.

        Attributes
        ----------
        headers : dict
            HTTP headers used for requests (primarily the User-Agent).
        driver : selenium.webdriver.Chrome
            The Chrome WebDriver instance used for automation.
        wait : selenium.webdriver.support.ui.WebDriverWait
            Explicit wait handler for synchronizing element interaction.
        specs_keys : list
            List of specification keys to filter when parsing product data.
        product_json : dict
            Dictionary to store scraped product information.
    """
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

        self.specs_keys = ["HP","VOLTS","RPM","FRAME"]
        self.product_json = {}

    def open(self):
        """
        Opens the main catalog page of the Baldor website and handles any consent popups.
        """
        self.driver.get("https://www.baldor.com/catalog")
        self.handle_consent_popup()
    
    def handle_consent_popup(self):
        """
        Checks for and accepts the cookie consent popup if present.
        
        This method attempts to click on the 'Allow All' button to proceed with website access.
        """
        try:
            allow_all_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, './/div[@class="adroll_button_text" and contains(text(), "Allow All")]')
            ))
            allow_all_btn.click()
            logger.info("Clicked on 'Allow All' cookie banner.")
            time.sleep(4)
        except TimeoutException:
            logger.warning("No consent popup detected.")
    
    def load_products_page(self,target_category:str=None):
        """
        Loads a product category page from the Baldor catalog.

        Random delays are added to simulate human behavior and help 
        avoid bot detection by the website.

        Parameters
        ----------
        target_category : str, optional
            The name of a specific category to open. If not provided,
            a default category will be selected.
        """
        try:
            catalog_of_products = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, './/div[@class="ng-binding"]')
            ))
            time.sleep(random.uniform(2, 5))

            logger.info(f"Found {len(catalog_of_products)} categories of products on online catalog")

            if target_category is not None:
                for element in catalog_of_products:
                    if element.text.strip() == target_category:
                        element.click()
            else:
                if catalog_of_products:
                    self.driver.execute_script("arguments[0].click();", catalog_of_products[4])
                else:
                    raise Exception("No valid products found.")

            time.sleep(random.uniform(2, 5))

            logger.success("Successfully loaded products page:")
            print(self.driver.title)

        except TimeoutException:
            logger.error("Timeout: Page elements did not load in time.")
        except Exception as e:
            logger.error("General error:")
            print(e)
        
        finally:
            time.sleep(3)
    
    def scrap_product(self,limit:int=1):
        """
        Scrapes detailed information of one or more products listed on the product category page.

        Parameters
        ----------
        limit : int, optional
            The number of products to scrape. Default is 1.
        """
        products = self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, './/a[@class="ng-binding"]') 
        ))
        time.sleep(random.uniform(2, 5))
        
        for i in range(limit):
            if products:
                self.driver.execute_script("arguments[0].click();", products[i+1])
            else:
                raise Exception("No valid products found.")
            
            logger.success("Successfully loaded product detail page:")
            print(self.driver.title)

            self.__get_metadata()
            self.__get_manual_pdf()
            self.__get_img()
            self.__save_json()

            time.sleep(random.uniform(2, 5))
            self.driver.back()
    
    def __get_metadata(self):
        """
        Extracts product metadata from the product detail page.

        This includes the product ID, description, specifications (HP, VOLTS, RPM, FRAME),
        and bill of materials (BOM), if available.
        """
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Get Product's title and description
        title_elem = soup.find("div", class_="page-title")
        description_elem = soup.find("div", class_="product-description")

        title = title_elem.get_text(strip=True) if title_elem else None
        description = description_elem.get_text(strip=True) if description_elem else None

        self.product_json["product_id"] = title
        self.product_json["description"] = description

        specs = {}
        table = soup.find("table", class_="nameplate")
        if table is not None:
            rows = table.find_all("tr") if table else []
            for row in rows:
                headers = row.find_all("th")
                values = row.find_all("td")
                
                for th, td in zip(headers, values):
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)

                    if key not in self.specs_keys:
                        continue
                    specs[key.lower()] = value
        else:
            logger.warning("No specs table (class='nameplate') found.")
        
        self.product_json["specs"] = specs

        bom = []
        target_div = soup.find("div", attrs={"data-tab": "parts"})
        if target_div is not None:
            table = target_div.find("table", class_="data-table")
            if table:
                tbody = table.find("tbody")

                for row in tbody.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) == 3: 
                        product = {
                            "part_number": cells[0].get_text(strip=True),
                            "description": cells[1].get_text(strip=True),
                            "quantity": cells[2].get_text(strip=True)
                        }
                        bom.append(product)
            else:
                logger.warning("No BOM table (class='data-table') found inside parts div.")
        else:
            logger.warning("No div with data-tab='parts' found.")
        
        self.product_json["bom"] = bom


    def __get_manual_pdf(self):
        """
        Downloads the product manual PDF file, if available, and saves it to a local directory.
        """
        try:
            pdf_element = self.driver.find_element(by=By.XPATH,value='.//a[@id="infoPacket"]')
            pdf_url = pdf_element.get_attribute('href')

            p_id = self.product_json["product_id"] if self.product_json["product_id"] is not None else "Unidentified"
            path = f"output\\assets\\{p_id}"
            os.makedirs(path, exist_ok=True)

            pdf_filename = f"{path}\\manual.pdf"

            response = requests.get(pdf_url, headers=self.headers)

            if response.status_code == 200:
                with open(pdf_filename, 'wb') as f:
                    f.write(response.content)
                logger.success(f"PDF downloaded successfully and saved at: {pdf_filename}")
            else:
                logger.error(f"Failed to download PDF. Status code: {response.status_code}")
        except Exception:
            logger.warning("No PDF link found on the page.")
        
    def __get_img(self):
        """
        Downloads the main image of the product and saves it to a local directory.
        """
        try:
            img_element = self.driver.find_element(By.CLASS_NAME, 'product-image')
            img_url = img_element.get_attribute('src')

            p_id = self.product_json["product_id"] if self.product_json["product_id"] is not None else "Unidentified"
            path = f"output\\assets\\{p_id}"
            os.makedirs(path, exist_ok=True)

            img_filename = f"{path}\\img.jpg"

            response = requests.get(img_url, headers=self.headers)

            if response.status_code == 200:
                with open(img_filename, "wb") as f:
                    f.write(response.content)
                logger.success(f"Image downloaded successfully and saved at: {img_filename}")
            else:
                logger.error(f"Failed to download image: {response.status_code}")
        except Exception:
            logger.warning("No image element found on the page.")
    
    def __save_json(self):
        """
        Saves the collected product information into a JSON file named after the product ID.
        """
        p_id = self.product_json["product_id"] if self.product_json["product_id"] != None else "Unidentified"
        json_path = f"output\\{p_id}.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.product_json, f, ensure_ascii=False, indent=4)
        logger.success(f"JSON file saved at: {json_path}")

    def exit(self):
        """
        Closes the browser and ends the WebDriver session.
        """
        self.driver.quit()
    
