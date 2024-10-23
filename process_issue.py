from playwright.sync_api import sync_playwright, Playwright
import time
import os
import uuid


def set_multiline_output(name, value):
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
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
    time.sleep(2)  # wait for the page to load
    page.get_by_role("textbox", name="Enter a message...").click()
    page.get_by_role("textbox", name="Enter a message...").fill(
        f"""
Help me with answer this customer query. Respond like a professional support agent and say when you don't have any answer instead of providing an incorrect one.
Also, let them know these answers are AI generated and can have errors -
{ISSUE_BODY}
"""
    )
    page.get_by_label("Send message").click()
    time.sleep(12)  # required since we are streaming responses
    message_contents = page.query_selector_all(".message-content")
    last_message_content = message_contents[-1].text_content()
    print(last_message_content)
    set_multiline_output("response", last_message_content)
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
