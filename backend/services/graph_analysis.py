"""Wallet graph analysis using NetworkX."""

from typing import Any
import networkx as nx


class WalletGraphAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_transaction(self, wallet_from: str, wallet_to: str, amount: float, tx_id: str) -> None:
        for w in (wallet_from, wallet_to):
            if not self.graph.has_node(w):
                self.graph.add_node(w, tx_count=0, total_out=0.0, total_in=0.0)
        self.graph.nodes[wallet_from]["tx_count"] += 1
        self.graph.nodes[wallet_to]["tx_count"] += 1
        self.graph.nodes[wallet_from]["total_out"] += amount
        self.graph.nodes[wallet_to]["total_in"] += amount
        if self.graph.has_edge(wallet_from, wallet_to):
            self.graph[wallet_from][wallet_to]["weight"] += amount
            self.graph[wallet_from][wallet_to]["count"] += 1
        else:
            self.graph.add_edge(wallet_from, wallet_to, weight=amount, count=1, tx_ids=[tx_id])

    def wallet_risk(self, wallet: str) -> tuple[float, list[str]]:
        if wallet not in self.graph:
            return 0.0, []
        flags, risk = [], 0.0
        out_d, in_d = self.graph.out_degree(wallet), self.graph.in_degree(wallet)
        if out_d > 10:
            flags.append("Wallet linked to unusually high outbound activity (fan-out pattern)")
            risk += 0.35
        if in_d > 10:
            flags.append("Wallet receiving from many sources (fan-in / mixer pattern)")
            risk += 0.35
        try:
            if nx.clustering(self.graph.to_undirected(), wallet) > 0.6 and out_d + in_d > 5:
                flags.append("Dense local cluster — possible coordinated fraud ring")
                risk += 0.25
        except Exception:
            pass
        return min(risk, 1.0), flags

    def suspicious_clusters(self, min_size: int = 3) -> list[dict[str, Any]]:
        clusters = []
        for component in nx.connected_components(self.graph.to_undirected()):
            if len(component) >= min_size:
                sg = self.graph.subgraph(component)
                total_flow = sum(d.get("weight", 0) for _, _, d in sg.edges(data=True))
                clusters.append({
                    "wallets": list(component)[:20], "size": len(component),
                    "edge_count": sg.number_of_edges(), "total_flow": round(total_flow, 2),
                    "risk": "high" if len(component) > 5 else "medium",
                })
        return sorted(clusters, key=lambda c: c["size"], reverse=True)[:10]

    def to_visualization(self, max_nodes: int = 40) -> dict[str, Any]:
        ranked = sorted(self.graph.nodes(), key=lambda n: self.graph.degree(n), reverse=True)[:max_nodes]
        node_set = set(ranked)
        nodes = [{"id": n, "label": f"{n[:6]}...{n[-4:]}", "degree": self.graph.degree(n),
                  "risk": round(self.wallet_risk(n)[0], 2)} for n in ranked]
        edges = [{"source": u, "target": v, "weight": round(d.get("weight", 0), 2), "count": d.get("count", 1)}
                 for u, v, d in self.graph.edges(data=True) if u in node_set and v in node_set]
        return {"nodes": nodes, "edges": edges, "clusters": self.suspicious_clusters()}


graph_analyzer = WalletGraphAnalyzer()
