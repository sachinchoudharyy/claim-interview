import tempfile
import requests
import fitz

from groq import Groq

from app.core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def extract_pdf_text(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:

        text += page.get_text()

        text += "\n\n"

    doc.close()

    return text


def analyze_statement_from_url(file_url: str):

    response = requests.get(file_url)

    if response.status_code != 200:

        raise Exception("Unable to download PDF")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(response.content)

        pdf_path = temp_file.name

    extracted_text = extract_pdf_text(pdf_path)

    if len(extracted_text.strip()) < 100:

        return {
            "report":
            "Unable to extract meaningful text from this PDF."
        }

    if len(extracted_text) > 50000:

        extracted_text = extracted_text[:50000]

    prompt = f"""
You are a senior banking fraud investigator.

First determine whether this document is actually a bank statement.

If it is NOT a bank statement:

Return only:

This document does not appear to be a bank statement.
Please upload a valid bank statement PDF.

If it IS a bank statement:

Perform a complete investigation.

Review all visible information including:

- account holder details
- statement period
- balances
- sender accounts
- receiver accounts
- transaction descriptions
- cash deposits
- cash withdrawals
- UPI transfers
- IMPS transfers
- NEFT transfers
- RTGS transfers
- cheque activity
- recurring transactions
- salary patterns
- EMI patterns
- unusual transactions
- suspicious fund movements
- anomalies
- inconsistencies
- any red flags

Generate a detailed investigator report.


Explain all important observations.

Document Text:

{extracted_text}
"""

    result = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    report = result.choices[0].message.content

    return {
        "report": report
    }