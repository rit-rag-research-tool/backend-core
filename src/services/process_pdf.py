from typing import List, Tuple
from pdf2image import convert_from_bytes
import fitz
import io

def process_pdf(pdf_bytes: bytes) -> Tuple[str, List[bytes]]:


    extracted_text = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page in doc:
        text = page.get_text("text")
        extracted_text.append(text.strip())

    extracted_text_str = "/d/=/-t/".join(extracted_text)

    images = convert_from_bytes(pdf_bytes, dpi=300)

    page_to_image = []
    for image in images:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        page_to_image.append(img_byte_arr.getvalue())

    return extracted_text_str, page_to_image
