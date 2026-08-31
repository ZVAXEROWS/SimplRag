import re

from Data import Chunk


class Chunker:

    def __init__(self, max_chunk_size=1000):
        self.max_chunk_size = max_chunk_size

        self.section_pattern = re.compile(
            r"^\d+\.\s+.+$",
            re.MULTILINE
        )

        self.list_pattern = re.compile(
            r"^\s*(?:[-*•]|\d+[.)])\s+",
            re.MULTILINE
        )

    # ========================================================
    # PUBLIC METHOD
    # ========================================================

    def chunk(self, document):

        sections = self._detect_sections(
            document.text
        )

        chunks = []

        for section in sections:

            section_chunks = self._process_section(
                section["text"]
            )

            for chunk_id, text in enumerate(section_chunks):

                chunks.append(
                    Chunk(
                        text=text,
                        source=document.source,
                        section_id=section["section_id"],
                        section_title=section["section_title"],
                        chunk_id=chunk_id
                    )
                )

        return chunks

    # ========================================================
    # 1. DETECT SECTIONS
    # ========================================================

    def _detect_sections(self, text):

        matches = list(
            self.section_pattern.finditer(text)
        )

        # CASE 1:
        # No sections found
        if not matches:

            return [
                {
                    "text": text.strip(),
                    "section_id": 0,
                    "section_title": "General"
                }
            ]

        sections = []

        # Text before first section
        if matches[0].start() > 0:

            intro = text[
                :matches[0].start()
            ].strip()

            if intro:

                sections.append(
                    {
                        "text": intro,
                        "section_id": 0,
                        "section_title": "Introduction"
                    }
                )

        # Extract sections
        for index, match in enumerate(matches):

            start = match.start()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(text)

            section_text = text[
                start:end
            ].strip()

            header = match.group().strip()

            section_id = int(
                header.split(".", 1)[0]
            )

            section_title = header.split(
                ".", 1
            )[1].strip()

            sections.append(
                {
                    "text": section_text,
                    "section_id": section_id,
                    "section_title": section_title
                }
            )

        return sections

    # ========================================================
    # 2. PROCESS SECTION
    # ========================================================

    def _process_section(self, text):

        # Small section → keep it intact
        if len(text) <= self.max_chunk_size:

            return [text]

        # Large section → hierarchical splitting
        return self._split_large_text(text)

    # ========================================================
    # 3. SPLIT LARGE TEXT
    # ========================================================

    def _split_large_text(self, text):

        blocks = self._split_into_blocks(text)

        chunks = []
        current_chunk = ""

        for block in blocks:

            block = block.strip()

            if not block:
                continue

            # Block itself is too large
            if len(block) > self.max_chunk_size:

                if current_chunk:

                    chunks.append(
                        current_chunk.strip()
                    )

                    current_chunk = ""

                chunks.extend(
                    self._split_by_sentences(block)
                )

                continue

            # Add block to current chunk
            if self._fits(
                current_chunk,
                block
            ):

                if current_chunk:
                    current_chunk += "\n\n"

                current_chunk += block

            else:

                if current_chunk:

                    chunks.append(
                        current_chunk.strip()
                    )

                current_chunk = block

        if current_chunk:

            chunks.append(
                current_chunk.strip()
            )

        return chunks

    # ========================================================
    # 4. SPLIT INTO BLOCKS
    # ========================================================

    def _split_into_blocks(self, text):

        lines = text.splitlines()

        blocks = []
        current_block = []

        for line in lines:

            stripped = line.strip()

            if not stripped:

                if current_block:

                    blocks.append(
                        "\n".join(current_block)
                    )

                    current_block = []

                continue

            # List item
            if self.list_pattern.match(stripped):

                current_block.append(stripped)

            else:

                current_block.append(stripped)

        if current_block:

            blocks.append(
                "\n".join(current_block)
            )

        return blocks

    # ========================================================
    # 5. SENTENCE SPLITTING
    # ========================================================

    def _split_by_sentences(self, text):

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        chunks = []
        current = ""

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            if self._fits(
                current,
                sentence
            ):

                if current:
                    current += " "

                current += sentence

            else:

                if current:

                    chunks.append(
                        current.strip()
                    )

                current = sentence

        if current:

            chunks.append(
                current.strip()
            )

        return chunks

    # ========================================================
    # 6. SIZE CHECK
    # ========================================================

    def _fits(self, current, new_text):

        if not current:
            return len(new_text) <= self.max_chunk_size

        return (
            len(current)
            + len(new_text)
            + 2
            <= self.max_chunk_size
        )

    def print_chunks(self, chunks):

        print("\n" + "=" * 70)
        print("ALL CHUNKS")
        print("=" * 70)

        for chunk in chunks:

            print(f"\nSource: {chunk.source}")
            print(f"Section ID: {chunk.section_id}")
            print(f"Section Title: {chunk.section_title}")
            print(f"Chunk ID: {chunk.chunk_id}")
            print(f"Characters: {len(chunk.text)}")

            print("\nText:")
            print(chunk.text)

            print("\n" + "-" * 70)