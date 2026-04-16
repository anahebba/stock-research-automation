import os
import json
import urllib.request
import boto3
import random
import re
from datetime import datetime

# Claude API constants
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-5-haiku-20241022"

def get_env_vars():
    """Fetch required environment variables."""
    return {
        "claude_api_key": os.environ["claude_api_key"],
        "smtp_pass": os.environ["smtp_pass"],  # Used for SES compatibility
    }

def generate_prompt():
    """Generate a value investing prompt with strict formatting rules."""
    targets = [
        "India", "USA", "Europe", "USA", "Entire World",
        "Mexico", "UK", "Metal Industry", "Technology companies",
        "Japan", "Hong Kong", "China" , "Indian Microfinance" , "Indian SME", "USA Microcap" ,
        "Europe Laggards", "Australia", "Global banks", "Technology sector", "Biotech sector", "Stocks with insider buys"
    ]
    target = random.choice(targets)

    prompt = (
        f"You are an expert value investor. Please give me 5 specific small-cap or micro-cap stocks from {target} "
        f"that are either undervalued or in distressed sectors but have potential for a turnaround.\n\n"
        f"Prefer information from substack, seeking alpha, reddit and financial news. If not available use any source. Please make multiple web searches\n\n"
        f"Use this format for each stock:\n"
        f"**Company Name**:\n"
        f"- Industry:\n"
        f"- Why Underperforming:\n"
        f"- What can trigger a turnaround:\n\n"
        f"Do not add a title, introduction, or closing statement. Start directly with the list. "
        f"Do not write 'Here are 5 stocks…' or anything else. Just give the stock list. "
        f"Do not include any disclaimers, risk warnings, or 'Important Considerations' sections. "
        f"Do not mention that this is not financial advice or that users should do their own research. "
        f"Use useful links at the end if available."
    )

    return prompt, target

def extract_urls(obj):
    """Extract all URLs by converting JSON to string and using regex."""
    json_str = json.dumps(obj)
    urls = re.findall(r'https?://[^\s"\'<>]+', json_str)
    return list(set(urls))  # Remove duplicates

def call_claude(api_key, prompt):
    """Call Claude API and return summarised response and links."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": 2500,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 6
        }]
    }

    req = urllib.request.Request(
        CLAUDE_API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            raw_response = response.read().decode("utf-8")
            response_data = json.loads(raw_response)
            print("Claude API response:", response_data)

            # Extract text
            text_blocks = []
            for block in response_data.get("content", []):
                if isinstance(block, dict) and "text" in block:
                    text_blocks.append(block["text"].strip())

            all_text = "\n".join(text_blocks).strip()

            # Clean up and format the text properly
            all_text = format_stock_analysis(all_text)

            all_urls = extract_urls(response_data)
            urls_text = "\n".join(all_urls)

            return f"{all_text}\n\nUseful Links\n{urls_text}" if all_text or all_urls else "Response Not Found"

    except urllib.error.HTTPError as e:
        raise Exception(f"Claude API HTTPError: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"Claude API URLError: {e.reason}")

def format_stock_analysis(text):
    """Format the stock analysis text with proper structure and numbering."""
    # Split by stock entries (assuming they start with **)
    stock_entries = re.split(r'(\*\*[^*]+\*\*:)', text)
    
    formatted_text = ""
    stock_counter = 0
    
    for i in range(len(stock_entries)):
        if stock_entries[i].startswith('**') and stock_entries[i].endswith('**:'):
            stock_counter += 1
            company_name = stock_entries[i].replace('**', '').replace(':', '')
            
            # Add line break before each stock (except first)
            if stock_counter > 1:
                formatted_text += "\n\n"
            
            formatted_text += f"**{stock_counter}. {company_name}**:\n"
            
            # Process the content after the company name
            if i + 1 < len(stock_entries):
                content = stock_entries[i + 1].strip()
                formatted_content = format_stock_content(content)
                formatted_text += formatted_content
    
    return formatted_text

def format_stock_content(content):
    """Format individual stock content with proper bullet points."""
    # Split by lines and process each
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle bullet points that start with -
        if line.startswith('- '):
            # Check if it's a main category (Market Cap, Industry, etc.)
            if any(category in line for category in ['Industry:', 'Why Underperforming:', 'What can trigger a turnaround:']):
                formatted_lines.append(f"• **{line[2:]}**")
            else:
                # Regular bullet point
                formatted_lines.append(f"  - {line[2:]}")
        elif line.startswith('**') and line.endswith('**:'):
            # Skip company headers as they're handled separately
            continue
        else:
            # Regular text that should be indented under the last bullet
            if formatted_lines and not line.startswith('•'):
                formatted_lines.append(f"    {line}")
            else:
                formatted_lines.append(line)
    
    return '\n'.join(formatted_lines) + '\n'

def send_email_ses(smtp_pass, body, subject):
    """Send summary via AWS SES with HTML formatting."""
    smtp_user = "ananyahebbarwork1@gmail.com"
    email_to = "ananyahebbarwork1@gmail.com"
    region = "ap-south-1"

    ses = boto3.client("ses", region_name=region)

    # Convert markdown to HTML properly
    html_body = body
    
    # Replace **text** with <strong>text</strong> for better email compatibility
    html_body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_body)
    
    # Replace bullet points with proper HTML bullets
    html_body = re.sub(r'^• ', '&bull; ', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^  - ', '&nbsp;&nbsp;&nbsp;&nbsp;&bull; ', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^    ', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', html_body, flags=re.MULTILINE)
    
    # Add emojis to specific content in HTML
    html_body = re.sub(r'Market Cap:', '💰 Market Cap:', html_body)
    html_body = re.sub(r'Industry:', '🏭 Industry:', html_body)
    html_body = re.sub(r'Why Underperforming:', '📉 Why Underperforming:', html_body)
    html_body = re.sub(r'What can trigger a turnaround:', '🚀 What can trigger a turnaround:', html_body)
    html_body = re.sub(r'Useful Links', '🔗 Useful Links', html_body)
    
    # Add stock emoji to each numbered company
    html_body = re.sub(r'<strong>(\d+\. [^<]+)</strong>', r'📈 <strong>\1</strong>', html_body)
    
    # Make URLs clickable (smart links)
    url_pattern = r'(https?://[^\s<>"\']+)'
    html_body = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', html_body)
    
    # Replace line breaks with HTML breaks
    html_body = html_body.replace("\n", "<br>")

    html_wrapped = f"""
    <html>
    <body style='font-family: Arial, sans-serif; font-size:14px; line-height: 1.6; max-width: 800px; margin: 0 auto;'>
        <div style='padding: 20px;'>
            <h2 style='color: #2c5282; margin-bottom: 20px;'>Value Investment Opportunities</h2>
            {html_body}
        </div>
    </body>
    </html>
    """

    try:
        response = ses.send_email(
            Source=smtp_user,
            Destination={"ToAddresses": [email_to]},
            Message={
                "Subject": {"Data": f"📊 {subject}", "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_wrapped, "Charset": "UTF-8"},
                    "Text": {"Data": body, "Charset": "UTF-8"}  # fallback
                }
            }
        )
        print("SES Response:", response)
    except Exception as e:
        print("SES sending failed:", str(e))
        raise

def lambda_handler(event, context):
    """AWS Lambda entry point."""
    env = get_env_vars()
    prompt, target = generate_prompt()

    try:
        summary = call_claude(env["claude_api_key"], prompt)
        print("Summary from Claude:", summary)

        today_str = datetime.now().strftime("%d %b")
        subject = f"Daily Search {today_str} - {target}"

        send_email_ses(env["smtp_pass"], summary, subject)

        return {
            "statusCode": 200,
            "body": json.dumps("Email sent successfully.")
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
