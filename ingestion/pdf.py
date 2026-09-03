from pypdf import PdfReader

def read_pdf(file_path):

    documents=[]
    reader=PdfReader(file_path)

    total_pages=len(reader.pages)
    print(f"Total Pages:{total_pages}\n")

    for index,page in enumerate(reader.pages[4:],start=1):
        text=page.extract_text()
        if not text:
            continue

        documents.append({
            "text":text,
            "metadata":{
                "filename":file_path,
                "page":index
            }
        })
    return documents



