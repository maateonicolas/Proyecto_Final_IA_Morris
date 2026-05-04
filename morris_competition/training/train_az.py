# training/train_az.py
#
# Entrenamiento AlphaZero-like para MorrisNet.
#
# Diferencia con train.py:
# - train.py usa policy one-hot.
# - train_az.py usa visit_policy generada por NeuralPUCTMCTS.
#
# Loss:
# - policy_loss = cross entropy suave entre visit_policy y policy_logits
# - value_loss  = MSE entre value predicho y resultado final

import pickle
from pathlib import Path
import sys

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.GRP1.model import MorrisNet


DATASET_PATH = ROOT / "training" / "data" / "self_play_az_dataset.pkl"
CHECKPOINT_DIR = ROOT / "training" / "checkpoints"
CHECKPOINT_PATH = CHECKPOINT_DIR / "morris_net_az.pt"

BATCH_SIZE = 64
EPOCHS = 30
LEARNING_RATE = 0.001
VALUE_LOSS_WEIGHT = 1.0


class AlphaZeroSelfPlayDataset(Dataset):
    """
    Dataset AlphaZero-like.

    Cada ejemplo contiene:
    - state: vector de tamaño 80
    - policy: visit_policy de tamaño 624
    - value: resultado final desde perspectiva del jugador
    """

    def __init__(self, dataset_path=DATASET_PATH):
        if not dataset_path.exists():
            raise FileNotFoundError(
                f"No se encontró el dataset: {dataset_path}\n"
                f"Primero ejecuta: python training/self_play_az.py"
            )

        with open(dataset_path, "rb") as f:
            self.data = pickle.load(f)

        if len(self.data) == 0:
            raise ValueError("El dataset AlphaZero está vacío.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]

        state = torch.tensor(sample["state"], dtype=torch.float32)
        policy = torch.tensor(sample["policy"], dtype=torch.float32)
        value = torch.tensor([sample["value"]], dtype=torch.float32)

        return state, policy, value


def soft_policy_cross_entropy(policy_logits, target_policy):
    """
    Cross entropy para una distribución objetivo completa.

    target_policy no es una clase única, sino una distribución de visitas.
    """

    log_probs = torch.log_softmax(policy_logits, dim=1)
    loss = -(target_policy * log_probs).sum(dim=1).mean()
    return loss


def train_az_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 70)
    print("TRAINING AZ — MorrisNet")
    print("=" * 70)
    print(f"Device            : {device}")
    print(f"Dataset           : {DATASET_PATH}")
    print(f"Checkpoint        : {CHECKPOINT_PATH}")
    print(f"Batch size        : {BATCH_SIZE}")
    print(f"Epochs            : {EPOCHS}")
    print(f"Learning rate     : {LEARNING_RATE}")
    print(f"Value loss weight : {VALUE_LOSS_WEIGHT}")
    print("=" * 70)

    dataset = AlphaZeroSelfPlayDataset(DATASET_PATH)

    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    model = MorrisNet().to(device)

    value_loss_fn = nn.MSELoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    for epoch in range(1, EPOCHS + 1):
        model.train()

        total_loss = 0.0
        total_policy_loss = 0.0
        total_value_loss = 0.0

        for states, target_policies, target_values in dataloader:
            states = states.to(device)
            target_policies = target_policies.to(device)
            target_values = target_values.to(device)

            optimizer.zero_grad()

            policy_logits, predicted_values = model(states)

            policy_loss = soft_policy_cross_entropy(
                policy_logits,
                target_policies,
            )

            value_loss = value_loss_fn(
                predicted_values,
                target_values,
            )

            loss = policy_loss + VALUE_LOSS_WEIGHT * value_loss

            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            total_policy_loss += policy_loss.item()
            total_value_loss += value_loss.item()

        avg_loss = total_loss / len(dataloader)
        avg_policy_loss = total_policy_loss / len(dataloader)
        avg_value_loss = total_value_loss / len(dataloader)

        print(
            f"Epoch {epoch:02d}/{EPOCHS} | "
            f"loss={avg_loss:.4f} | "
            f"policy_loss={avg_policy_loss:.4f} | "
            f"value_loss={avg_value_loss:.4f}"
        )

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_size": model.input_size,
            "action_size": model.action_size,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE,
            "dataset_size": len(dataset),
            "dataset_type": "alphazero_visit_policy",
        },
        CHECKPOINT_PATH,
    )

    print("=" * 70)
    print(f"Modelo AlphaZero guardado en: {CHECKPOINT_PATH}")
    print(f"Ejemplos usados             : {len(dataset)}")
    print("=" * 70)


if __name__ == "__main__":
    train_az_model()