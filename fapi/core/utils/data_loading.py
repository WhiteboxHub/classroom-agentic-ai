import os
from typing import List, Tuple

from langchain.document_loaders import PyPDFLoader
from docx import Document


class FolderFileReader:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

    def read_folder(self) -> List[Tuple[str, str]]:
        """
        Reads all supported files in the folder and returns
        a list of (file_path, extracted_text).
        """
        results = []

        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)

            if not os.path.isfile(file_path):
                continue

            ext = os.path.splitext(filename)[1].lower()

            if ext == ".pdf":
                results.append((file_path, self.read_pdf(file_path)))

            elif ext == ".docx":
                results.append((file_path, self.read_word(file_path)))

            elif ext == ".txt":
                results.append((file_path, self.read_txt(file_path)))

        return results

    def read_pdf(self, file_path: str) -> str:
        """
        Reads a PDF using PyPDFLoader and returns all text.
        """
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        return "\n".join(page.page_content for page in pages)

    def read_word(self, file_path: str) -> str:
        """
        Reads a Word (.docx) file and returns all text.
        """
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    def read_txt(self, file_path: str) -> str:
        """
        Reads a text (.txt) file and returns its content.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
