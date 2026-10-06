from services.text_chunker import chunk_markdown
def test_empty_markdown():
    assert chunk_markdown("") == []

def test_extracts_content_and_heading():
    markdown = """
# Introduction
    Reading Lizard is an AI tutor.

## Event Loop

The event loop handles asynchronous callbacks.
"""
    chunks = chunk_markdown(markdown)

    assert len(chunks) == 2
    assert chunks[0]["section_title"] == "Introduction"
    assert chunks[1]["section_title"] == "Event Loop"


def test_chunk_size_limit():
    markdown = "# Long Section\n\n" + ("word " * 2000)

    chunks = chunk_markdown(
        markdown,
        max_chars=500,
        overlap_chars=50,
    )

    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= 500 for chunk in chunks)


def test_chunk_ids_are_sequential():
    markdown = "# First\n\nContent one.\n\n# Second\n\nContent two."
    chunks = chunk_markdown(markdown)

    assert [chunk["chunk_id"] for chunk in chunks] == list(
        range(len(chunks))
    )


if __name__ == "__main__":
    test_empty_markdown()
    test_extracts_content_and_heading()
    test_chunk_size_limit()
    test_chunk_ids_are_sequential()

    print("All chunking tests passed!")
