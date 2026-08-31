from dataclasses import dataclass


@dataclass
class Document:
    text: str
    source: str


@dataclass
class Chunk:
    text: str
    source: str
    section_id: int
    section_title: str
    chunk_id: int