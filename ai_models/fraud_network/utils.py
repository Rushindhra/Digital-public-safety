"""Utilities for fraud_network model package."""


def load_nodes(data: dict) -> list[dict]:
    return data.get("nodes", [])


def load_edges(data: dict) -> list[dict]:
    return data.get("edges", [])
