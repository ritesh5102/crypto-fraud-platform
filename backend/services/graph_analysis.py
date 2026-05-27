"""Wallet transaction graph analysis using NetworkX."""

from typing import Any

import networkx as nx


class WalletGraphAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_transaction(self, wallet_from: str, wallet_to: str, amount: float, tx_id: str) -> None:
        if not self.graph.has_node(wallet_from):
            self.graph.add_node(wallet_from, tx_count=0, total_out=0.0)
        if not self.graph.has_node(wallet_to):
            self.graph.add_node(wallet_to, tx_count=0, total_in=0.0)

        self.graph.nodes[wallet_from]["tx_count"] = self.graph.nodes[wallet_from].get("tx_count", 0) + 1
        self.graph.nodes[wallet_to]["tx_count"] = self.graph.nodes[wallet_to].get("tx_count", 0) + 1
        self.graph.nodes[wallet_from]["total_out"] = self.graph.nodes[wallet_from].get("total_out", 0) + amount
        self.graph.nodes[wallet_to]["total_in"] = self.graph.nodes[wallet_to].get("total_in", 0) + amount

        if self.graph.has_edge(wallet_from, wallet_to):
            self.graph[wallet_from][wallet_to]["weight"] += amount
            self.graph[wallet_from][wallet_to]["count"] += 1
        else:
            self.graph.add_edge(wallet_from, wallet_to, weight=amount, count=1, tx_ids=[tx_id])

    def wallet_risk(self, wallet: str) -> tuple[float, list[str]]:
        if wallet not in self.graph:
            return 0.0, []

        flags: list[str] = []
        risk = 0.0
        out_degree = self.graph.out_degree(wallet)
        in_degree = self.graph.in_degree(wallet)

        if out_degree > 10:
            flags.append("Wallet linked to unusually high outbound activity (fan-out pattern)")
            risk += 0.35
        if in_degree > 10:
            flags.append("Wallet receiving from many sources (fan-in / mixer pattern)")
            risk += 0.35

        try:
            clustering = nx.clustering(self.graph.to_undirected(), wallet)
            if clustering > 0.6 and out_degree + in_degree > 5:
                flags.append("Dense local cluster — possible coordinated fraud ring")
                risk += 0.25
        except Exception:
            pass

        try:
            betweenness = nx.betweenness_centrality(self.graph)
            if betweenness.get(wallet, 0) > 0.1:
                flags.append("High betweenness centrality — intermediary hub wallet")
                risk += 0.2
        except Exception:
            pass

        return min(risk, 1.0), flags

    def suspicious_clusters(self, min_size: int = 3) -> list[dict[str, Any]]:
        undirected = self.graph.to_undirected()
        clusters = []
        for component in nx.connected_components(undirected):
            if len(component) >= min_size:
                subgraph = self.graph.subgraph(component)
                total_flow = sum(d.get("weight", 0) for _, _, d in subgraph.edges(data=True))
                clusters.append({
                    "wallets": list(component)[:20],
                    "size": len(component),
                    "edge_count": subgraph.number_of_edges(),
                    "total_flow": round(total_flow, 2),
                    "risk": "high" if len(component) > 5 else "medium",
                })
        return sorted(clusters, key=lambda c: c["size"], reverse=True)[:10]

    def to_visualization(self, max_nodes: int = 40) -> dict[str, Any]:
        nodes = []
        edges = []
        ranked = sorted(
            self.graph.nodes(),
            key=lambda n: self.graph.degree(n),
            reverse=True,
        )[:max_nodes]
        node_set = set(ranked)

        for n in ranked:
            risk, _ = self.wallet_risk(n)
            nodes.append({
                "id": n,
                "label": f"{n[:6]}...{n[-4:]}",
                "degree": self.graph.degree(n),
                "risk": round(risk, 2),
            })

        for u, v, data in self.graph.edges(data=True):
            if u in node_set and v in node_set:
                edges.append({
                    "source": u,
                    "target": v,
                    "weight": round(data.get("weight", 0), 2),
                    "count": data.get("count", 1),
                })

        return {"nodes": nodes, "edges": edges, "clusters": self.suspicious_clusters()}


# Singleton graph analyzer
graph_analyzer = WalletGraphAnalyzer()
