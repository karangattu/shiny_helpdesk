from playwright.sync_api import sync_playwright, Playwright
import time
import os
import uuid


def set_multiline_output(name, value):
    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a") as fh:
        delimiter = uuid.uuid1()
        print(f"{name}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)


def format_as_markdown(content):
    # Split the content into lines
    lines = content.split("\n")

    # Initialize variables
    formatted_lines = []
    in_code_block = False

    for line in lines:
        # Check for the start of a code block
        if line.strip().startswith("app.py"):
            formatted_lines.append("```python")
            in_code_block = True
            continue

        # Check for the end of a code block
        if line.strip() == "Run app →":
            if in_code_block:
                formatted_lines.append("```")
                in_code_block = False
            formatted_lines.append(line)
            continue

        # Format headers
        if (
            line.strip().startswith("Basic")
            or line.strip().startswith("Layout")
            or line.strip().startswith("Collapsible")
        ):
            formatted_lines.append(f"## {line.strip()}")
            continue

        # Add the line as is
        formatted_lines.append(line)

    # Ensure the last code block is closed if necessary
    if in_code_block:
        formatted_lines.append("```")

    # Join the formatted lines
    return "\n".join(formatted_lines)


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
    formatted_content = format_as_markdown(last_message_content)
    print(formatted_content)
    # # remove Run app → from last_message_content
    # last_message_content = last_message_content.replace("Run app →", "").strip()
    set_multiline_output("RESPONSE", formatted_content)
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
