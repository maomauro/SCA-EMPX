"""
Script de entrenamiento de un modelo de clasificación — Fase 0.

Entrena un clasificador sobre MNIST (dígitos 0-9). En cada época calcula:
- Función de costo (loss) en train y en validación.
- Dos métricas de desempeño (Accuracy y F1-score) en train y en validación.

Listo para ser instrumentado con MLFlow (Fase 1) y Comet ML (Fase 2).
Ejecutar desde la raíz del proyecto: uv run python training/train_classifier.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from torchvision.datasets import MNIST


# ── Modelo ───────────────────────────────────────────────────────────────────

class SmallCNN(nn.Module):
    """Red convolucional pequeña para clasificación de dígitos MNIST."""

    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Flatten(),
        )
        self.classifier = nn.Sequential(
            nn.Linear(32 * 7 * 7, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.25),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)


# ── Métricas ──────────────────────────────────────────────────────────────────

def accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Accuracy: proporción de predicciones correctas."""
    preds = logits.argmax(dim=1)
    return (preds == targets).float().mean().item()


def f1_macro(logits: torch.Tensor, targets: torch.Tensor, num_classes: int = 10) -> float:
    """F1-score macro (promedio de F1 por clase)."""
    preds = logits.argmax(dim=1)
    f1_sum = 0.0
    for c in range(num_classes):
        tp = ((preds == c) & (targets == c)).sum().float().item()
        fp = ((preds == c) & (targets != c)).sum().float().item()
        fn = ((preds != c) & (targets == c)).sum().float().item()
        if tp + fp + fn == 0:
            continue
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        if precision + recall > 0:
            f1_sum += 2 * precision * recall / (precision + recall)
    return f1_sum / num_classes if num_classes > 0 else 0.0


# ── Entrenamiento ─────────────────────────────────────────────────────────────

def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    num_classes: int,
) -> tuple[float, float, float]:
    """Una época de entrenamiento. Retorna (loss, accuracy, f1)."""
    model.train()
    total_loss = 0.0
    total_acc = 0.0
    total_f1 = 0.0
    n_batches = 0
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        logits = model(inputs)
        loss = criterion(logits, targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        total_acc += accuracy(logits.detach(), targets)
        total_f1 += f1_macro(logits.detach(), targets, num_classes)
        n_batches += 1
    n = max(n_batches, 1)
    return total_loss / n, total_acc / n, total_f1 / n


@torch.no_grad()
def eval_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    num_classes: int,
) -> tuple[float, float, float]:
    """Evaluación en validación. Retorna (loss, accuracy, f1)."""
    model.eval()
    total_loss = 0.0
    total_acc = 0.0
    total_f1 = 0.0
    n_batches = 0
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        logits = model(inputs)
        loss = criterion(logits, targets)
        total_loss += loss.item()
        total_acc += accuracy(logits, targets)
        total_f1 += f1_macro(logits, targets, num_classes)
        n_batches += 1
    n = max(n_batches, 1)
    return total_loss / n, total_acc / n, total_f1 / n


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Entrenar clasificador MNIST (Fase 0)")
    parser.add_argument("--epochs", type=int, default=3, help="Número de épocas")
    parser.add_argument("--batch-size", type=int, default=128, help="Tamaño de batch")
    parser.add_argument("--lr", type=float, default=1e-2, help="Learning rate")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Proporción para validación (0-1)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria")
    parser.add_argument("--out", type=str, default="", help="Carpeta para guardar modelo (opcional)")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    num_classes = 10

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    dataset_full = MNIST(root="./data", train=True, download=True, transform=transform)
    n_val = int(len(dataset_full) * args.val_ratio)
    n_train = len(dataset_full) - n_val
    dataset_train, dataset_val = random_split(dataset_full, [n_train, n_val])

    loader_train = DataLoader(
        dataset_train,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=False,
    )
    loader_val = DataLoader(
        dataset_val,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )

    model = SmallCNN(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    print("Fase 0 — Entrenamiento clasificador MNIST")
    print(f"  Device: {device}  Épocas: {args.epochs}  Batch: {args.batch_size}")
    print("  Métricas: loss (cost), accuracy, F1-macro (train y validación)")
    print("-" * 70)

    for epoch in range(1, args.epochs + 1):
        loss_train, acc_train, f1_train = train_epoch(
            model, loader_train, criterion, optimizer, device, num_classes
        )
        loss_val, acc_val, f1_val = eval_epoch(
            model, loader_val, criterion, device, num_classes
        )
        print(
            f"Epoch {epoch:2d}  "
            f"loss_train={loss_train:.4f}  loss_val={loss_val:.4f}  "
            f"acc_train={acc_train:.4f}  acc_val={acc_val:.4f}  "
            f"f1_train={f1_train:.4f}  f1_val={f1_val:.4f}"
        )

    if args.out:
        out_path = Path(args.out)
        out_path.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), out_path / "mnist_classifier.pt")
        print(f"\nModelo guardado en {out_path / 'mnist_classifier.pt'}")

    print("\nListo. En Fase 1 se añadirá MLFlow para registrar estas métricas por época.")


if __name__ == "__main__":
    main()
