import pdfplumber

def pdf_to_text(pdf_path, output_txt="output.txt"):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {i} ---\n"
                text += page_text

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ Text extracted and saved to", output_txt)


if __name__ == "__main__":
    pdf_to_text("sample.pdf")
