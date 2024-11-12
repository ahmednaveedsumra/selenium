from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time


class RestaurantScraper:
    location_data = []

    def __init__(self):
        self.driver = webdriver.Edge()
        self.wait = WebDriverWait(self.driver, 10)

    def search_restaurants(self, search_term="restaurants in Lahore"):
        self.driver.get("https://www.google.com/maps/")
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(search_term)
        search_button = self.driver.find_element(By.ID, "searchbox-searchbutton")
        search_button.click()
        time.sleep(5)

    def scroll_results(self, max_scrolls=10):
        scrollable_div = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='feed']")))
        for _ in range(max_scrolls):
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(2)

    def clean_data(self, text):
        # Remove unwanted characters like \ue5ca\n, \ue0c8\n, \ue0b0\n, \uf186\n
        unwanted_chars = ['\ue5ca', '\ue0c8', '\ue0b0', '\uf186', '\n']
        for char in unwanted_chars:
            text = text.replace(char, "")
        return text.strip()  # Also remove leading/trailing whitespace

    def get_restaurant_data(self):
        for index in range(40):  # Adjust this as needed
            try:
                restaurant_elements = self.driver.find_elements(By.CLASS_NAME, "Nv2PK")
                if index >= len(restaurant_elements):
                    break

                restaurant = restaurant_elements[index]
                data = {}

                link = restaurant.find_element(By.TAG_NAME, "a")
                self.driver.execute_script("arguments[0].click();", link)
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "zvLtDc")))
                time.sleep(2)

                data["name"] = self.clean_data(self.driver.find_element(By.CLASS_NAME, "DUwDvf").text)
                data["rating"] = self.clean_data(
                    self.driver.find_element(By.CSS_SELECTOR, ".F7nice span span[aria-hidden='true']").text)
                data["reviews_count"] = self.clean_data(
                    self.driver.find_element(By.CSS_SELECTOR, ".F7nice span span[aria-label]").text.strip("()"))

                features = self.driver.find_element(By.CLASS_NAME, "E0DTEd")
                feature_texts = [self.clean_data(feature.text) for feature in
                                 features.find_elements(By.CLASS_NAME, "LTs0Rc")]
                data["features"] = ", ".join(feature_texts)

                data["address"] = self.clean_data(
                    self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']").text)
                data["website"] = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']").get_attribute(
                    "href")
                data["contact"] = self.clean_data(
                    self.driver.find_element(By.CSS_SELECTOR, "[data-item-id^='phone']").text)
                data["plus_code"] = self.clean_data(
                    self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='oloc']").text)

                self.location_data.append(data)
                self.driver.execute_script("window.history.go(-1)")
                time.sleep(2)

            except StaleElementReferenceException:
                print("Stale element reference encountered; retrying...")
                continue
            except NoSuchElementException as e:
                print(f"Error extracting data for a restaurant (element not found): {e}")
                continue

    def scrape(self):
        try:
            self.search_restaurants()
            self.scroll_results(max_scrolls=10)
            self.get_restaurant_data()
        finally:
            self.driver.quit()
        return self.location_data


scraper = RestaurantScraper()
data = scraper.scrape()
print(data)
