"""Locate executable GraphQL fields and plan edits using parsed source ranges.

Parsing proves syntax, not Shopify schema compatibility or application behavior.
Ambiguous response shapes and changes that could leave invalid GraphQL stay manual.
"""
from __future__ import annotations

from dataclasses import dataclass

from graphql import GraphQLError, parse
from graphql.language import (
    FieldNode, FragmentDefinitionNode, FragmentSpreadNode, InlineFragmentNode,
    IntValueNode, Node, OperationDefinitionNode, SelectionSetNode, VariableNode,
)


GRAPHQL_ACTIONS = {"remove_graphql_field_block", "replace_price_rule"}


@dataclass
class QueryField:
    node: FieldNode
    parent: SelectionSetNode
    parent_type: str | None
    line: int


@dataclass
class Edit:
    start: int
    end: int
    replacement: str
    line: int
    action: str


def query_fields(text: str) -> list[QueryField] | None:
    try:
        document = parse(text)
    except GraphQLError:
        return None
    fields: list[QueryField] = []

    def walk(selection_set: SelectionSetNode, owner: str | None):
        for selection in selection_set.selections:
            if isinstance(selection, FieldNode):
                fields.append(QueryField(
                    selection, selection_set, owner,
                    selection.loc.start_token.line,
                ))
                if selection.selection_set:
                    child_type = "Customer" if selection.name.value == "customer" else None
                    walk(selection.selection_set, child_type)
            elif isinstance(selection, InlineFragmentNode):
                child_type = selection.type_condition.name.value if selection.type_condition else owner
                walk(selection.selection_set, child_type)

    for definition in document.definitions:
        if isinstance(definition, OperationDefinitionNode):
            walk(definition.selection_set, None)
        elif isinstance(definition, FragmentDefinitionNode):
            walk(definition.selection_set, definition.type_condition.name.value)
    return fields


def matches_action(field: QueryField, action: str) -> bool:
    if action == "remove_graphql_field_block":
        return field.node.name.value == "lastIncompleteCheckout"
    if action == "replace_price_rule":
        return (field.node.name.value == "priceRule"
                and field.parent_type == "DraftOrderDiscountNotAppliedWarning")
    return False


def _nodes(node: Node):
    yield node
    for key in node.keys:
        if key == "loc":
            continue
        value = getattr(node, key, None)
        if isinstance(value, Node):
            yield from _nodes(value)
        elif isinstance(value, (tuple, list)):
            for child in value:
                if isinstance(child, Node):
                    yield from _nodes(child)


def _simple_discount_selection(node: FieldNode) -> bool:
    """Only automate the response data covered by Shopify's published example."""
    if not node.selection_set:
        return True
    allowed = {"priceRule": {"title", "discountCodes"}, "discountCodes": {"nodes"},
               "nodes": {"code"}, "title": set(), "code": set()}
    for child in node.selection_set.selections:
        if not isinstance(child, FieldNode) or child.name.value not in allowed[node.name.value]:
            return False
        if child.alias or child.directives:
            return False
        if child.arguments:
            if child.name.value != "discountCodes" or len(child.arguments) != 1:
                return False
            argument = child.arguments[0]
            if (argument.name.value != "first" or not isinstance(argument.value, IntValueNode)
                    or argument.value.value != "1"):
                return False
        if child.name.value in {"discountCodes", "nodes"} and not child.selection_set:
            return False
        if child.name.value in {"title", "code"} and child.selection_set:
            return False
        if not _simple_discount_selection(child):
            return False
    return True


def render_edits(text: str, edits: list[Edit]) -> str:
    for edit in sorted(edits, key=lambda item: item.start, reverse=True):
        text = text[:edit.start] + edit.replacement + text[edit.end:]
    return text


def plan_edits(text: str, requested: set[tuple[int, str]], fields=None) -> list[Edit]:
    fields = query_fields(text) if fields is None else fields
    if fields is None:
        return []
    edits: list[Edit] = []
    for field in fields:
        node = field.node
        for action in GRAPHQL_ACTIONS:
            if (field.line, action) not in requested or not matches_action(field, action):
                continue
            if node.alias or node.arguments or node.directives:
                continue
            # Removing these can orphan variable/fragment definitions elsewhere.
            if any(isinstance(n, (VariableNode, FragmentSpreadNode)) for n in _nodes(node)):
                continue
            start, end = node.loc.start, node.loc.end
            if action == "remove_graphql_field_block":
                if field.parent_type != "Customer" or len(field.parent.selections) <= 1:
                    continue
                replacement = ""
                line_start = text.rfind("\n", 0, start) + 1
                line_end = text.find("\n", end)
                line_end = len(text) if line_end < 0 else line_end
                if not text[line_start:start].strip() and not text[end:line_end].strip():
                    start = line_start
                    end = line_end + (line_end < len(text))
            else:
                if not _simple_discount_selection(node):
                    continue
                existing = {s.name.value for s in field.parent.selections
                            if isinstance(s, FieldNode) and not s.alias and not s.directives}
                names = [name for name in ("discountTitle", "discountCode") if name not in existing]
                prefix = text[text.rfind("\n", 0, start) + 1:start]
                newline = "\r\n" if "\r\n" in text else "\n"
                separator = " " if prefix.strip() else newline + prefix
                replacement = separator.join(names)
            edits.append(Edit(start, end, replacement, field.line, action))
    edits.sort(key=lambda edit: edit.start)
    if any(a.end > b.start for a, b in zip(edits, edits[1:])):
        return []
    try:
        parse(render_edits(text, edits))
    except GraphQLError:
        # Combined removals can empty a selection even if each looked safe alone.
        return []
    return edits
