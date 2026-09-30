import numpy as np

from nltk.tokenize import sent_tokenize

from .embedding import generate_embedding


def chunking(documents: list):

    sentences = []

    # ---------------------------------------------
    # 1. Convert extracted documents into sentences
    # ---------------------------------------------

    for document in documents:

        page_sentences = sent_tokenize(
            document["text"]
        )

        for sentence in page_sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            sentences.append({
                "metadata": document["metadata"],
                "text": sentence,
            })

    # ---------------------------------------------
    # 2. Not enough sentences for semantic chunking
    # ---------------------------------------------

    if len(sentences) < 2:
        return sentences

    # ---------------------------------------------
    # 3. Generate sentence embeddings
    # ---------------------------------------------

    embeddings_sentences = [
        generate_embedding(sentence["text"])
        for sentence in sentences
    ]

    # Convert to NumPy array
    sentence_embeddings = np.array(
        embeddings_sentences,
        dtype=np.float32
    )

    # ---------------------------------------------
    # 4. Normalize embeddings
    # ---------------------------------------------

    norms = np.linalg.norm(
        sentence_embeddings,
        axis=1,
        keepdims=True
    )

    sentence_embeddings = (
        sentence_embeddings /
        np.maximum(norms, 1e-12)
    )

    # ---------------------------------------------
    # 5. Calculate similarity between
    #    consecutive sentences
    # ---------------------------------------------

    similarities = []

    for i in range(len(sentence_embeddings) - 1):

        score = np.dot(
            sentence_embeddings[i],
            sentence_embeddings[i + 1]
        )

        similarities.append(
            float(score)
        )

    # ---------------------------------------------
    # 6. Find semantic boundaries
    # ---------------------------------------------

    similarities = np.array(
        similarities,
        dtype=np.float32
    )

    threshold = np.percentile(
        similarities,
        20
    )

    boundaries = []

    for i, similarity in enumerate(similarities):

        if similarity <= threshold:

            boundaries.append(i + 1)

    # ---------------------------------------------
    # 7. Create chunks
    # ---------------------------------------------

    chunks = []

    start = 0

    for boundary in boundaries:

        chunk_sentences = sentences[
            start:boundary
        ]

        if not chunk_sentences:
            continue

        chunk_text = " ".join(
            sentence["text"]
            for sentence in chunk_sentences
        )

        chunks.append({
            "text": chunk_text,

            "metadata_start": (
                chunk_sentences[0]["metadata"]
            ),

            "metadata_end": (
                chunk_sentences[-1]["metadata"]
            ),
        })

        start = boundary

    # ---------------------------------------------
    # 8. Add remaining sentences
    # ---------------------------------------------

    if start < len(sentences):

        chunk_sentences = sentences[start:]

        chunk_text = " ".join(
            sentence["text"]
            for sentence in chunk_sentences
        )

        chunks.append({
            "text": chunk_text,

            "metadata_start": (
                chunk_sentences[0]["metadata"]
            ),

            "metadata_end": (
                chunk_sentences[-1]["metadata"]
            ),
        })

    return chunks