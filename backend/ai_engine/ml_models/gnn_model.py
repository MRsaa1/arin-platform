"""
ARIN Platform - Graph Neural Network Model
GNN модель для предсказания влияния на основе графа зависимостей
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, Batch
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
import networkx as nx
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


class GNNModel(nn.Module):
    """
    Graph Neural Network модель для предсказания влияния рисков
    
    Использует Graph Convolutional Network (GCN) или
    Graph Attention Network (GAT) для обучения на графе зависимостей
    """
    
    def __init__(
        self,
        input_dim: int = 10,
        hidden_dim: int = 64,
        output_dim: int = 1,
        num_layers: int = 3,
        model_type: str = "GCN"
    ):
        """
        Инициализация GNN модели
        
        Args:
            input_dim: Размерность входных признаков узла
            hidden_dim: Размерность скрытых слоев
            output_dim: Размерность выхода (1 для предсказания риска)
            num_layers: Количество слоев
            model_type: Тип модели (GCN или GAT)
        """
        super(GNNModel, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.model_type = model_type
        
        # Выбор типа слоев
        if model_type == "GAT":
            ConvLayer = GATConv
            self.heads = 4  # Количество attention heads для GAT
        else:
            ConvLayer = GCNConv
            self.heads = 1
        
        # Построение слоев
        self.convs = nn.ModuleList()
        
        # Первый слой
        self.convs.append(
            ConvLayer(input_dim, hidden_dim, heads=self.heads, concat=(model_type == "GAT"))
        )
        
        # Промежуточные слои
        for _ in range(num_layers - 2):
            if model_type == "GAT":
                self.convs.append(
                    ConvLayer(
                        hidden_dim * self.heads if model_type == "GAT" else hidden_dim,
                        hidden_dim,
                        heads=self.heads,
                        concat=True
                    )
                )
            else:
                self.convs.append(ConvLayer(hidden_dim, hidden_dim))
        
        # Последний слой
        if num_layers > 1:
            final_input_dim = hidden_dim * self.heads if model_type == "GAT" else hidden_dim
            self.convs.append(ConvLayer(final_input_dim, hidden_dim))
        
        # Выходной слой
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, batch: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Признаки узлов [num_nodes, input_dim]
            edge_index: Индексы ребер [2, num_edges]
            batch: Batch вектор для агрегации
            
        Returns:
            Предсказания [num_nodes, output_dim] или [batch_size, output_dim]
        """
        # Применение сверточных слоев
        for i, conv in enumerate(self.convs[:-1]):
            x = conv(x, edge_index)
            x = F.relu(x)
            x = self.dropout(x)
        
        # Последний слой
        if len(self.convs) > 0:
            x = self.convs[-1](x, edge_index)
            x = F.relu(x)
        
        # Агрегация для графа (если batch указан)
        if batch is not None:
            x = global_mean_pool(x, batch)
        
        # Выходной слой
        x = self.fc(x)
        
        return x


class GNNPredictor:
    """
    Обертка для GNN модели с методами обучения и предсказания
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        input_dim: int = 10,
        hidden_dim: int = 64,
        model_type: str = "GCN"
    ):
        """
        Инициализация GNN Predictor
        
        Args:
            model_path: Путь к сохраненной модели
            input_dim: Размерность входных признаков
            hidden_dim: Размерность скрытых слоев
            model_type: Тип модели (GCN или GAT)
        """
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.model_type = model_type
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if model_path and Path(model_path).exists():
            self.load(model_path)
        else:
            self.model = GNNModel(
                input_dim=input_dim,
                hidden_dim=hidden_dim,
                output_dim=1,
                model_type=model_type
            ).to(self.device)
            
    def graph_to_pyg_data(
        self,
        graph: nx.DiGraph,
        node_features: Optional[Dict[str, np.ndarray]] = None
    ) -> Data:
        """
        Преобразование NetworkX графа в PyTorch Geometric Data
        
        Args:
            graph: NetworkX граф
            node_features: Словарь {node_id: feature_vector}
            
        Returns:
            PyTorch Geometric Data объект
        """
        # Получение списка узлов
        nodes = list(graph.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        # Создание edge_index
        edges = []
        for source, target in graph.edges():
            edges.append([node_to_idx[source], node_to_idx[target]])
        
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        
        # Создание признаков узлов
        if node_features is None:
            # Использование свойств узлов из графа
            x = []
            for node in nodes:
                node_data = graph.nodes[node]
                features = [
                    node_data.get("risk_score", 0.0),
                    node_data.get("degree_centrality", 0.0) if "degree_centrality" in node_data else 0.0,
                    node_data.get("betweenness_centrality", 0.0) if "betweenness_centrality" in node_data else 0.0,
                    node_data.get("closeness_centrality", 0.0) if "closeness_centrality" in node_data else 0.0,
                    1.0 if node_data.get("node_type") == "bank" else 0.0,
                    1.0 if node_data.get("node_type") == "company" else 0.0,
                    1.0 if node_data.get("node_type") == "sector" else 0.0,
                    1.0 if node_data.get("node_type") == "region" else 0.0,
                    1.0 if node_data.get("node_type") == "asset" else 0.0,
                    0.0  # Padding
                ]
                x.append(features[:self.input_dim])
        else:
            x = [node_features.get(node, np.zeros(self.input_dim)) for node in nodes]
        
        x = torch.tensor(x, dtype=torch.float)
        
        return Data(x=x, edge_index=edge_index)
        
    def predict_influence(
        self,
        graph: nx.DiGraph,
        source_node: str,
        target_nodes: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Предсказание влияния от исходного узла на целевые узлы
        
        Args:
            graph: Граф зависимостей
            source_node: ID исходного узла
            target_nodes: Список целевых узлов (если None, все узлы)
            
        Returns:
            Словарь {target_node: predicted_influence_score}
        """
        if self.model is None:
            logger.warning("Model not loaded, returning default predictions")
            return {}
        
        if source_node not in graph:
            logger.warning(f"Source node {source_node} not in graph")
            return {}
        
        self.model.eval()
        
        # Преобразование графа
        data = self.graph_to_pyg_data(graph)
        data = data.to(self.device)
        
        # Предсказание для всех узлов
        with torch.no_grad():
            predictions = self.model(data.x, data.edge_index)
            predictions = predictions.squeeze().cpu().numpy()
        
        # Маппинг предсказаний на узлы
        nodes = list(graph.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        results = {}
        for node in target_nodes if target_nodes else nodes:
            if node in node_to_idx:
                idx = node_to_idx[node]
                results[node] = float(predictions[idx])
        
        return results
        
    def train(
        self,
        graphs: List[nx.DiGraph],
        labels: List[Dict[str, float]],
        epochs: int = 100,
        lr: float = 0.01
    ):
        """
        Обучение модели
        
        Args:
            graphs: Список графов для обучения
            labels: Список словарей {node_id: true_influence_score}
            epochs: Количество эпох
            lr: Learning rate
        """
        if self.model is None:
            self.model = GNNModel(
                input_dim=self.input_dim,
                hidden_dim=self.hidden_dim,
                output_dim=1,
                model_type=self.model_type
            ).to(self.device)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        self.model.train()
        
        for epoch in range(epochs):
            total_loss = 0
            
            for graph, label_dict in zip(graphs, labels):
                # Преобразование графа
                data = self.graph_to_pyg_data(graph)
                data = data.to(self.device)
                
                # Получение меток
                nodes = list(graph.nodes())
                y = torch.tensor([
                    label_dict.get(node, 0.0) for node in nodes
                ], dtype=torch.float).to(self.device).unsqueeze(1)
                
                # Forward pass
                optimizer.zero_grad()
                pred = self.model(data.x, data.edge_index)
                loss = criterion(pred, y)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(graphs):.4f}")
        
        logger.info("Model training completed")
        
    def save(self, model_path: str):
        """Сохранение модели"""
        if self.model is None:
            logger.warning("No model to save")
            return
        
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "model_type": self.model_type
        }, model_path)
        
        logger.info(f"Model saved to {model_path}")
        
    def load(self, model_path: str):
        """Загрузка модели"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        self.model = GNNModel(
            input_dim=checkpoint["input_dim"],
            hidden_dim=checkpoint["hidden_dim"],
            output_dim=1,
            model_type=checkpoint["model_type"]
        ).to(self.device)
        
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        
        logger.info(f"Model loaded from {model_path}")

