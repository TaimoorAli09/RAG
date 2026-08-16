from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------
# Text Splitter Configuration
# ---------------------------------------------------------
# chunk_size:
# Maximum size of each chunk.
#
# chunk_overlap:
# Number of characters repeated between consecutive chunks.
# This helps preserve context when information is split
# between two chunks.
# ---------------------------------------------------------


# Maine 1000 / 200 ko 700 / 100 kyun kiya
# precision , accuracyy sahi ni thi 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)


def create_chunks(pages):
    """
    Split each PDF page into smaller meaningful chunks.

    Input:
        pages = [
            {
                "page_number": 1,
                "text": "..."
            },
            ...
        ]

    Output:
        [
            {
                "page_number": 1,
                "chunk_number": 1,
                "text": "..."
            },
            ...
        ]
    """

    chunks = []

    # Process each page separately
    for page in pages:

        # Split the page text into smaller chunks
        page_chunks = text_splitter.split_text(page["text"])

        # Store each generated chunk
        for index, chunk in enumerate(page_chunks):

            chunks.append(
                {
                    # Original PDF page number
                    "page_number": page["page_number"],
                    # Chunk number within that page
                    "chunk_number": index + 1,
                    # Actual chunk text
                    "text": chunk,
                }
            )

    return chunks
