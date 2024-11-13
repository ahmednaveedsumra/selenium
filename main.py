import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


class RestaurantScraper:
    location_data = []
    visited_links = set()

    def __init__(self):
        self.driver = webdriver.Edge()
        self.wait = WebDriverWait(self.driver, 15)

    def search_restaurants(self, search_term="restaurants in Lahore"):
        self.driver.get("https://www.google.com/maps/")
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(search_term)
        search_button = self.driver.find_element(By.ID, "searchbox-searchbutton")
        search_button.click()
        time.sleep(5)

    def clean_data(self, text):
        if not text:
            return "NA"
        unwanted_chars = ['\ue5ca', '\ue0c8', '\ue0b0', '\uf186', '\n', '·']
        for char in unwanted_chars:
            text = text.replace(char, "")
        return text.strip() if text.strip() else "NA"

    def get_restaurant_data(self):
        restaurant_elements = self.driver.find_elements(By.XPATH,
                                                        "//div[@role='feed']//div[contains(@jsaction,'mouseover')]")
        for restaurant in restaurant_elements:
            try:
                data = {}
                name_element = restaurant.find_element(By.XPATH, ".//a[@aria-label]")
                restaurant_name = self.clean_data(name_element.get_attribute("aria-label"))
                link = restaurant.find_element(By.TAG_NAME, "a")
                restaurant_url = link.get_attribute("href")

                if restaurant_url in self.visited_links:
                    continue

                self.visited_links.add(restaurant_url)

                self.driver.execute_script("arguments[0].click();", link)
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "id-content-container")))
                time.sleep(3)

                data["name"] = restaurant_name

                rating_elements = self.driver.find_elements(By.CSS_SELECTOR, ".fontDisplayLarge")
                data["rating"] = self.clean_data(rating_elements[0].text) if rating_elements else "NA"

                feature_elements = self.driver.find_elements(By.XPATH, '//*[@role="group"]')
                feature_texts = [feature.text for feature in feature_elements]
                data["features"] = ", ".join(
                    [self.clean_data(text) for text in feature_texts]) if feature_texts else "NA"

                address_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-item-id='address']")
                data["address"] = self.clean_data(address_elements[0].text) if address_elements else "NA"

                website_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-item-id='authority']")
                data["website"] = website_elements[0].get_attribute("href") if website_elements else "NA"

                contact_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-item-id^='phone']")
                data["contact"] = self.clean_data(contact_elements[0].text) if contact_elements else "NA"

                plus_code_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-item-id='oloc']")
                data["plus_code"] = self.clean_data(plus_code_elements[0].text) if plus_code_elements else "NA"

                self.location_data.append(data)

                self.driver.execute_script("window.history.go(-1)")
                time.sleep(3)

            except NoSuchElementException as e:
                print(f"Error extracting data for a restaurant (element not found): {e}")
                self.driver.execute_script("window.history.go(-1)")
                time.sleep(3)
            except StaleElementReferenceException:
                print("Stale element encountered; retrying...")
                continue

    def scroll_and_scrape(self, max_restaurants=40):
        total_restaurants = 0
        scrollable_div = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='feed']")))
        previous_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

        while total_restaurants < max_restaurants:

            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(7)
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

            if new_height == previous_height:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(5)

            previous_height = new_height
            self.get_restaurant_data()
            total_restaurants = len(self.location_data)

    def save_data_to_csv(self, filename="restaurants.csv"):
        if not self.location_data:
            print("No data to save.")
            return

        fieldnames = ["name", "rating", "features", "address", "website", "contact", "plus_code"]

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for restaurant in self.location_data:
                writer.writerow(restaurant)

        print(f"Data saved to {filename}")

    def scrape(self):
        try:
            self.search_restaurants()
            self.scroll_and_scrape(max_restaurants=40)
        finally:
            self.driver.quit()
        return self.location_data


scraper = RestaurantScraper()
data = scraper.scrape()

scraper.save_data_to_csv("restaurants.csv")