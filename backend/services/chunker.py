import re
class Chunker:
    def split_sentences(self,text):
        sentences=re.split(r'(?<=[.!?])\s+',text)

        return sentences


    def chunk_docs(self,documents,chunk_size=500,overlap_sentences=3):

        chunks=[]
        for docs in documents:
            text=docs["text"]
            metadata=docs["metadata"]

            sentences=self.split_sentences(text)
            current_chunk=""
            recent_sentences=[]

            for sentence in sentences:
                if len(current_chunk)+len(sentence)<=chunk_size:
                    current_chunk+=sentence+" "
                    recent_sentences.append(sentence)
                    if len(recent_sentences)>overlap_sentences:
                        recent_sentences.pop(0)

                else:
                    chunks.append({
                        "text":current_chunk.strip(),
                        "metadata":metadata.copy()
                    })
                    current_chunk=" ".join(recent_sentences)+" "+sentence+" "
                    recent_sentences.append(sentence)
                    if len(recent_sentences)>overlap_sentences:
                        recent_sentences.pop(0)

            if current_chunk:
                chunks.append({
                    "text":current_chunk.strip(),
                    "metadata":metadata.copy()
                })

        return chunks