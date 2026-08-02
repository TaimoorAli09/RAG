from langchain_text_splitters import RecursiveCharacterTextSplitter



text_splitter = RecursiveCharacterTextSplitter(

    chunk_size=1000,

    chunk_overlap=200
)



def create_chunks(pages):

    chunks = []


    for page in pages:


        page_chunks = text_splitter.split_text(
            page["text"]
        )


        for index, chunk in enumerate(page_chunks):


            chunks.append(

                {

                "page_number": page["page_number"],

                "chunk_number": index + 1,

                "text": chunk

                }

            )


    return chunks