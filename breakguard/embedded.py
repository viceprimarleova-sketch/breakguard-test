"""Limited static GraphQL literal recognition; embedded findings stay manual."""
from __future__ import annotations

import re
from dataclasses import dataclass

JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}


@dataclass
class EmbeddedDocument:
    text: str
    first_line: int
    dynamic: bool = False


def extract_documents(text: str, suffix: str) -> list[EmbeddedDocument]:
    if suffix == ".rb":
        return _ruby_documents(text)
    if suffix not in JS_EXTENSIONS:
        return []
    documents = []
    i = 0
    while i < len(text):
        if text.startswith("//", i):
            end = text.find("\n", i)
            i = len(text) if end < 0 else end + 1
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = len(text) if end < 0 else end + 2
            continue
        quote = text[i]
        if quote not in "'\"`":
            i += 1
            continue
        start = i + 1
        i = start
        while i < len(text):
            if text[i] == "\\":
                i += 2
            elif text[i] == quote:
                break
            else:
                i += 1
        if quote == "`":
            content = text[start:i]
            prefix = text[max(0, start - 100):start - 1]
            marked = content.lstrip().startswith("#graphql")
            tagged = re.search(r"\b(?:gql|graphql)\s*$", prefix) is not None
            called = re.search(r"\b(?:graphql|gql)\s*\(\s*$", prefix) is not None
            if marked or tagged or called:
                documents.append(EmbeddedDocument(content, text.count("\n", 0, start) + 1,
                                                  dynamic="${" in content or i >= len(text)))
        i += 1
    return documents


def _ruby_documents(text: str) -> list[EmbeddedDocument]:
    lines = text.splitlines(keepends=True)
    documents = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.lstrip().startswith("#"):
            match = re.search(r"<<[-~]?[\"']?(GRAPHQL|GQL|QUERY|MUTATION)[\"']?\s*(?:\)|,)?\s*$", line)
            if match:
                start = i + 1
                i = start
                while i < len(lines) and lines[i].strip() != match.group(1):
                    i += 1
                content = "".join(lines[start:i])
                documents.append(EmbeddedDocument(content, start + 1,
                                                  dynamic="#{" in content or i == len(lines)))
        i += 1
    return documents
