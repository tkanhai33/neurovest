from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from backend.app.stacks.chat_public.rag.embedding_client import (
    EmbeddingBatch,
)
from backend.app.stacks.chat_public.rag.local_index import (
    LocalKnowledgeIndex,
    discover_allowlisted_sources,
    extract_pdf_pages,
    is_allowed_source,
)


ROOT = Path(__file__).resolve().parents[5]


class FakeEmbeddingClient:
    model = "fake-pdf-embedding"

    def embed(
        self,
        texts,
    ) -> EmbeddingBatch:
        vectors = []

        for text in texts:
            lowered = str(
                text
            ).lower()

            vector = (
                1.0
                if "factor" in lowered
                else 0.1,
                1.0
                if "strategy" in lowered
                else 0.1,
                1.0
                if "risk" in lowered
                else 0.1,
            )

            magnitude = (
                sum(
                    value * value
                    for value in vector
                )
                ** 0.5
            )

            vectors.append(
                tuple(
                    value / magnitude
                    for value in vector
                )
            )

        return EmbeddingBatch(
            model=self.model,
            dimensions=3,
            vectors=tuple(
                vectors
            ),
        )


def test_research_pdf_is_allowlisted() -> None:
    pdf = (
        ROOT
        / "knowledge"
        / "research"
        / "ssrn"
        / "ssrn-3247865.pdf"
    )

    assert pdf.is_file()

    assert is_allowed_source(
        pdf,
        root=ROOT,
    )


def test_downloads_pdf_is_not_allowlisted() -> None:
    external_pdf = (
        Path.home()
        / "Downloads"
        / "ssrn-3247865.pdf"
    )

    assert not is_allowed_source(
        external_pdf,
        root=ROOT,
    )


def test_pdf_extraction_returns_page_metadata() -> None:
    pdf = (
        ROOT
        / "knowledge"
        / "research"
        / "academic"
        / "Fama–French_three-factor_model.pdf"
    )

    pages = extract_pdf_pages(
        pdf
    )

    assert pages

    assert all(
        isinstance(
            page["page_number"],
            int,
        )
        and page["page_number"] > 0
        and str(
            page["text"]
        ).strip()
        for page in pages
    )


def test_scanned_or_blank_pdf_returns_no_text(
    tmp_path: Path,
) -> None:
    pdf = (
        tmp_path
        / "blank.pdf"
    )

    writer = PdfWriter()
    writer.add_blank_page(
        width=612,
        height=792,
    )

    with pdf.open(
        "wb"
    ) as handle:
        writer.write(
            handle
        )

    assert extract_pdf_pages(
        pdf
    ) == []


def test_discovery_contains_all_research_pdfs() -> None:
    sources = discover_allowlisted_sources(
        ROOT
    )

    research_pdfs = {
        path.relative_to(
            ROOT
        ).as_posix()
        for path in sources
        if (
            path.suffix.lower()
            == ".pdf"
            and "knowledge/research/"
            in path.relative_to(
                ROOT
            ).as_posix()
        )
    }

    assert research_pdfs == {
        (
            "knowledge/research/academic/"
            "Fama–French_three-factor_model.pdf"
        ),
        (
            "knowledge/research/ssrn/"
            "ssrn-3145152.pdf"
        ),
        (
            "knowledge/research/ssrn/"
            "ssrn-3247865.pdf"
        ),
        (
            "knowledge/research/ssrn/"
            "ssrn-6289958.pdf"
        ),
        (
            "knowledge/research/ssrn/"
            "ssrn-6562398.pdf"
        ),
    }


def test_pdf_chunks_keep_source_and_page_metadata(
    tmp_path: Path,
) -> None:
    source = (
        ROOT
        / "knowledge"
        / "research"
        / "academic"
        / "Fama–French_three-factor_model.pdf"
    )

    index = LocalKnowledgeIndex(
        index_path=(
            tmp_path
            / "index.json"
        ),
        embedding_client=FakeEmbeddingClient(),
    )

    payload = index.build_from_paths(
        paths=[
            source,
        ],
        root=ROOT,
        chunk_words=100,
        overlap_words=15,
    )

    assert payload[
        "document_count"
    ] == 1

    assert payload[
        "chunk_count"
    ] > 0

    for chunk in payload[
        "chunks"
    ]:
        assert (
            chunk["source_type"]
            == "pdf"
        )

        assert (
            chunk["metadata"][
                "research_corpus"
            ]
            is True
        )

        assert (
            chunk["metadata"][
                "page_number"
            ]
            is not None
        )


@pytest.mark.parametrize(
    "filename",
    [
        "ssrn-3145152.pdf",
        "ssrn-3247865.pdf",
        "ssrn-6289958.pdf",
        "ssrn-6562398.pdf",
    ],
)
def test_srrn_pdf_has_extractable_text(
    filename: str,
) -> None:
    path = (
        ROOT
        / "knowledge"
        / "research"
        / "ssrn"
        / filename
    )

    pages = extract_pdf_pages(
        path
    )

    assert pages

    extracted_word_count = sum(
        len(
            str(
                page["text"]
            ).split()
        )
        for page in pages
    )

    assert extracted_word_count > 100
