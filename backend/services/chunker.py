import re
class Chunker:
    def split_sentences(self,text):
        sentences=re.split(r'(?<=[.!?])\s+',text)

        return sentences


    def chunk_docs(self,documents,chunk_size=500):

        chunks=[]
        for docs in documents:
            text=docs["text"]
            metadata=docs["metadata"]

            sentences=self.split_sentences(text)
            current_chunk=""
            last_sentence = ""

            for sentence in sentences:
                if len(current_chunk)+len(sentence)<=chunk_size:
                    current_chunk+=sentence+" "
                    last_sentence=sentence

                else:
                    chunks.append({
                        "text":current_chunk.strip(),
                        "metadata":metadata.copy()
                    })
                    current_chunk=last_sentence +" "+ sentence +" "

            if current_chunk:
                chunks.append({
                    "text":current_chunk.strip(),
                    "metadata":metadata.copy()
                })

        return chunks