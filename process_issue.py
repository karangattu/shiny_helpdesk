from playwright.sync_api import sync_playwright, Playwright
import time
import os
import uuid


def set_multiline_output(name, value):
    env_file = os.getenv('GITHUB_ENV')
    with open(env_file, "a") as fh:
        delimiter = uuid.uuid1()
        print(f"{name}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)


def run(playwright: Playwright):
    ISSUE_BODY = os.environ["ISSUE_BODY"]
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    page.goto("https://gallery.shinyapps.io/assistant")
    page.get_by_label("Python").check()
    page.get_by_text("Who can see my activity?").click()
    page.get_by_text("Who can see my activity?").click()
    page.get_by_role("textbox", name="Enter a message...").click()
    page.get_by_role("textbox", name="Enter a message...").fill(
        f"""
Help me with answer this customer query. Respond like a professional support agent and say when you don't have any answer instead of providing an incorrect one.
Also, let them know these answers are AI generated and can have errors. -
{ISSUE_BODY}
"""
    )
    page.get_by_label("Send message").click()
    time.sleep(12)  # required since we are streaming responses
    message_contents = page.query_selector_all(".message-content")
    last_message_content = message_contents[-1].text_content()
    # remove Run app → from last_message_content
    last_message_content = last_message_content.replace("Run app →", "").strip()
    # add ```python in the line after app.py
    last_message_content = last_message_content.replace("app.py", "app.py\n```python")
    # add ``` in the end after app = App(app_ui, server)
    last_message_content = last_message_content.replace("app = App(app_ui, server)", "app = App(app_ui, server)\n```")
    set_multiline_output("RESPONSE", last_message_content)
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
