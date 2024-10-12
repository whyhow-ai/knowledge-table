"""Tests for the graph routing schema"""

"""Tests for the graph API routing schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.graph import (
    Prompt, Cell, Column, Document, Row, Table,
    ExportTriplesRequest, ExportTriplesResponse
)


class TestPrompt:
    def test_valid_prompt(self):
        prompt_data = {
            "entityType": "person",
            "id": "1",
            "query": "What is the person's name?",
            "rules": ["rule1", "rule2"],
            "type": "text"
        }
        prompt = Prompt(**prompt_data)
        assert prompt.entityType == "person"
        assert prompt.id == "1"
        assert prompt.query == "What is the person's name?"
        assert prompt.rules == ["rule1", "rule2"]
        assert prompt.type == "text"

    def test_invalid_prompt_missing_field(self):
        invalid_data = {
            "entityType": "person",
            "id": "1",
            "query": "What is the person's name?",
            "rules": ["rule1", "rule2"]
            # Missing 'type' field
        }
        with pytest.raises(ValidationError):
            Prompt(**invalid_data)


class TestCell:
    def test_valid_cell(self):
        cell_data = {
            "answer": {"text": "John Doe"},
            "columnId": "col1",
            "dirty": True,
            "rowId": "row1"
        }
        cell = Cell(**cell_data)
        assert cell.answer == {"text": "John Doe"}
        assert cell.columnId == "col1"
        assert cell.dirty is True
        assert cell.rowId == "row1"

    def test_cell_with_string_dirty(self):
        cell_data = {
            "answer": {"text": "John Doe"},
            "columnId": "col1",
            "dirty": "true",
            "rowId": "row1"
        }
        cell = Cell(**cell_data)
        assert cell.dirty == "true"


class TestColumn:
    def test_valid_column(self):
        column_data = {
            "id": "col1",
            "prompt": {
                "entityType": "person",
                "id": "1",
                "query": "What is the person's name?",
                "rules": ["rule1"],
                "type": "text"
            },
            "width": 100,
            "hidden": False
        }
        column = Column(**column_data)
        assert column.id == "col1"
        assert isinstance(column.prompt, Prompt)
        assert column.width == 100
        assert column.hidden is False

    def test_column_with_string_values(self):
        column_data = {
            "id": "col1",
            "prompt": {
                "entityType": "person",
                "id": "1",
                "query": "What is the person's name?",
                "rules": ["rule1"],
                "type": "text"
            },
            "width": "100px",
            "hidden": "false"
        }
        column = Column(**column_data)
        assert column.width == "100px"
        assert column.hidden == "false"


class TestDocument:
    def test_valid_document(self):
        document_data = {
            "id": "doc1",
            "name": "Test Document",
            "author": "John Doe",
            "tag": "test",
            "page_count": 10
        }
        document = Document(**document_data)
        assert document.id == "doc1"
        assert document.name == "Test Document"
        assert document.author == "John Doe"
        assert document.tag == "test"
        assert document.page_count == 10

    def test_document_with_string_page_count(self):
        document_data = {
            "id": "doc1",
            "name": "Test Document",
            "author": "John Doe",
            "tag": "test",
            "page_count": "10"
        }
        document = Document(**document_data)
        assert document.page_count == "10"


class TestRow:
    def test_valid_row(self):
        row_data = {
            "id": "row1",
            "document": {
                "id": "doc1",
                "name": "Test Document",
                "author": "John Doe",
                "tag": "test",
                "page_count": 10
            },
            "hidden": False
        }
        row = Row(**row_data)
        assert row.id == "row1"
        assert isinstance(row.document, Document)
        assert row.hidden is False

    def test_row_with_string_hidden(self):
        row_data = {
            "id": "row1",
            "document": {
                "id": "doc1",
                "name": "Test Document",
                "author": "John Doe",
                "tag": "test",
                "page_count": 10
            },
            "hidden": "false"
        }
        row = Row(**row_data)
        assert row.hidden == "false"


class TestTable:
    def test_valid_table(self):
        table_data = {
            "columns": [
                {
                    "id": "col1",
                    "prompt": {
                        "entityType": "person",
                        "id": "1",
                        "query": "What is the person's name?",
                        "rules": ["rule1"],
                        "type": "text"
                    },
                    "width": 100,
                    "hidden": False
                }
            ],
            "rows": [
                {
                    "id": "row1",
                    "document": {
                        "id": "doc1",
                        "name": "Test Document",
                        "author": "John Doe",
                        "tag": "test",
                        "page_count": 10
                    },
                    "hidden": False
                }
            ],
            "cells": [
                {
                    "answer": {"text": "John Doe"},
                    "columnId": "col1",
                    "dirty": True,
                    "rowId": "row1"
                }
            ]
        }
        table = Table(**table_data)
        assert len(table.columns) == 1
        assert len(table.rows) == 1
        assert len(table.cells) == 1


class TestExportTriplesRequest:
    def test_valid_export_triples_request(self):
        request_data = {
            "columns": [
                {
                    "id": "col1",
                    "prompt": {
                        "entityType": "person",
                        "id": "1",
                        "query": "What is the person's name?",
                        "rules": ["rule1"],
                        "type": "text"
                    },
                    "width": 100,
                    "hidden": False
                }
            ],
            "rows": [
                {
                    "id": "row1",
                    "document": {
                        "id": "doc1",
                        "name": "Test Document",
                        "author": "John Doe",
                        "tag": "test",
                        "page_count": 10
                    },
                    "hidden": False
                }
            ],
            "cells": [
                {
                    "answer": {"text": "John Doe"},
                    "columnId": "col1",
                    "dirty": True,
                    "rowId": "row1"
                }
            ]
        }
        request = ExportTriplesRequest(**request_data)
        assert len(request.columns) == 1
        assert len(request.rows) == 1
        assert len(request.cells) == 1


class TestExportTriplesResponse:
    def test_valid_export_triples_response(self):
        response_data = {
            "triples": [
                {
                    "triple_id": "t1",
                    "head": {
                        "label": "Treatment",
                        "name": "natalizumab"
                    },
                    "tail": {
                        "label": "Disease",
                        "name": "multiple sclerosis"
                    },
                    "relation": {
                        "name": "treats"
                    },
                    "chunk_ids": ["t1_cm248iq3a00023b6jkfnv001v_c1", "t1_cm248iq3a00023b6jkfnv001v_c2"]
                }
            ],
            "chunks": [
                {
                    "chunk_id": "t1_cm248iq3a00023b6jkfnv001v_c1",
                    "content": "Sample content",
                    "page": "1",
                    "triple_id": "t1"
                }
            ]
        }
        response = ExportTriplesResponse(**response_data)
        assert len(response.triples) == 1
        assert len(response.chunks) == 1
        assert response.triples[0]["triple_id"] == "t1"
        assert response.chunks[0]["chunk_id"] == "t1_cm248iq3a00023b6jkfnv001v_c1"

    def test_invalid_export_triples_response(self):
        invalid_data = {
            "triples": [
                {
                    "triple_id": "t1",
                    "head": {
                        "label": "Treatment",
                        "name": "natalizumab"
                    },
                    "tail": {
                        "label": "Disease",
                        "name": "multiple sclerosis"
                    },
                    "relation": {
                        "name": "treats"
                    },
                    "chunk_ids": ["t1_cm248iq3a00023b6jkfnv001v_c1", "t1_cm248iq3a00023b6jkfnv001v_c2"]
                }
            ]
            # Missing 'chunks' field
        }
        with pytest.raises(ValidationError):
            ExportTriplesResponse(**invalid_data)
