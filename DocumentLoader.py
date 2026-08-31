from pathlib import Path
from Data import Document
from Data import Chunk



class DocumentLoader:

    def __init__(self, directory):
        self.directory = Path(directory)

    def load(self):
        documents = []

        for file_path in self.directory.glob("*.txt"):

            text = file_path.read_text(
                encoding="utf-8"
            )

            documents.append(
                Document(
                    text=text,
                    source=file_path.name
                )
            )

        return documents
