import pytest
from app.services.graph import analyse_graph


def test_graph_finds_connected_cluster_and_central_actor():
    result = analyse_graph([{"id":"phone"},{"id":"upi"},{"id":"account"}], [{"source":"phone","target":"upi"},{"source":"upi","target":"account"}])
    assert result["components"] == 1
    assert result["mastermind_candidates"][0]["id"] == "upi"


def test_graph_rejects_unknown_endpoint():
    with pytest.raises(ValueError): analyse_graph([{"id":"a"}], [{"source":"a","target":"missing"}])
