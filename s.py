from selenium import webdriver

driver = webdriver.Chrome()

driver.get("https://www.python.org")

driver.save_screenshot("homepage.png")

driver.quit()