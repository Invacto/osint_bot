import time
from seleniumwire import webdriver
from stage_proxy import stage_proxy

url = "https://httpbin.org/ip"
file_path = "proxy.txt"
proxy_options = stage_proxy(file_path)

chrome_options = webdriver.ChromeOptions()

driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=proxy_options)

try:
    driver.get(url)
    time.sleep(5)
    print("Response from proxy server:")
    print(driver.page_source)

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()
