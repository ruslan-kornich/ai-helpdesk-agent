from app.knowledge.retriever import KeywordRetriever


def test_retriever_finds_campaign_doc():
    retriever = KeywordRetriever()
    chunks = retriever.search("how do I send a bulk campaign", top_k=2)
    assert len(chunks) >= 1
    assert any("campaign" in chunk.lower() for chunk in chunks)


def test_retriever_finds_delivery_doc():
    retriever = KeywordRetriever()
    chunks = retriever.search("where can I see delivery reports", top_k=2)
    assert any("deliver" in chunk.lower() for chunk in chunks)


def test_retriever_returns_empty_for_no_overlap():
    retriever = KeywordRetriever()
    chunks = retriever.search("zzzzz qqqqq", top_k=2)
    assert chunks == []
