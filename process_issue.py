import os
import time
import uuid

from playwright.sync_api import Playwright, sync_playwright
from openai import OpenAI


def format_response_markdown(response):
    # Initialize OpenAI client
    client = OpenAI()
    messages = (
        [
            {"role": "system", "content": "Return this response in a markdown format"},
            {"role": "user", "content": response},
        ]
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content


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
        if line.strip().startswith("app.py") or line.strip().startswith("app_core.py"):
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
Help me with answer this customer query. Respond with a terse response.
If it is a feature request or adding more documentation, just respond that the team will look into it.
If it is a bug, check if they have provided all necessary information for reproducing the bug. If not ask them for missing information. Also, let them know that the team will investigate it.
Also, let them know these answers are AI generated and can have errors when providing a response. -
{ISSUE_BODY}
"""
    )
    page.get_by_label("Send message").click()
    time.sleep(12)  # required since we are streaming responses
    message_contents = page.query_selector_all(".message-content")
    last_message_content = message_contents[-1].text_content()
    formatted_content = format_response_markdown(last_message_content)
    # remove Run app → from formatted_content
    formatted_content = formatted_content.replace("Run app →", "")
    # write it to a file
    with open("output.md", "w") as f:
        f.write(formatted_content)
    set_multiline_output("RESPONSE", formatted_content)
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
