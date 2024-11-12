from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
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

    def get_restaurant_data(self):
        for index in range(40):
            try:
                restaurant_elements = self.driver.find_elements(By.CLASS_NAME, "Nv2PK")
                # restaurant_elements = self.driver.find_elements(By.CSS_SELECTOR,
                #                                                 "div[aria-label=\"Results for restaurants in lahore\"] > div:not([class]) > div")

                if index >= len(restaurant_elements):
                    break

                restaurant = restaurant_elements[index]
                data = {
                    "name": "NA",
                    "rating": "NA",
                    "reviews_count": "NA",
                    "features": "NA",
                    "address": "NA",
                    "website": "NA",
                    "contact": "NA",
                    "plus_code": "NA"
                }

                try:
                    link = restaurant.find_element(By.TAG_NAME, "a")
                    self.driver.execute_script("arguments[0].click();", link)
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "zvLtDc")))
                    time.sleep(2)

                    try:
                        data["name"] = self.driver.find_element(By.CLASS_NAME, "DUwDvf").text
                    except:
                        data["name"] = "NA"

                    try:
                        rating_element = self.driver.find_element(By.CSS_SELECTOR, ".F7nice span span[aria-hidden='true']")
                        data["rating"] = rating_element.text
                    except:
                        data["rating"] = "NA"

                    try:
                        reviews_count_element = self.driver.find_element(By.CSS_SELECTOR, ".F7nice span span[aria-label]")
                        data["reviews_count"] = reviews_count_element.text.strip("()")
                    except:
                        data["reviews_count"] = "NA"

                    try:
                        features = self.driver.find_element(By.CLASS_NAME, "E0DTEd")
                        feature_texts = [feature.text for feature in features.find_elements(By.CLASS_NAME, "LTs0Rc")]
                        data["features"] = ", ".join(feature_texts)
                    except:
                        data["features"] = "NA"

                    try:
                        address_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
                        data["address"] = address_element.text
                    except:
                        data["address"] = "NA"

                    try:
                        website_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']")
                        data["website"] = website_element.get_attribute("href")
                    except:
                        data["website"] = "NA"

                    try:
                        contact_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id^='phone']")
                        data["contact"] = contact_element.text
                    except:
                        data["contact"] = "NA"

                    try:
                        plus_code_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='oloc']")
                        data["plus_code"] = plus_code_element.text
                    except:
                        data["plus_code"] = "NA"

                    self.location_data.append(data)

                    self.driver.execute_script("window.history.go(-1)")
                    time.sleep(2)

                except StaleElementReferenceException:
                    print("Stale element reference encountered; retrying...")
                    continue

            except Exception as e:
                print(f"Error extracting data for a restaurant: {e}")

    def scrape(self):
        self.search_restaurants()
        self.scroll_results(max_scrolls=10)
        self.get_restaurant_data()
        self.driver.quit()
        return self.location_data


scraper = RestaurantScraper()
data = scraper.scrape()
print(data)