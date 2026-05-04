# training/train.py
#
# Primer entrenamiento de red neuronal para Nine Men's Morris.
#
# Entrada:
#   training/data/self_play_dataset.pkl
#
# Salida:
#   training/checkpoints/morris_net.pt
#
# La red aprende:
#   - policy: acción elegida por el agente durante self-play
#   - value: resultado final desde la perspectiva del jugador

import pickle
from pathlib import Path
import sys

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.GRP1.model import MorrisNet


DATASET_PATH = ROOT / "training" / "data" / "self_play_dataset.pkl"
CHECKPOINT_DIR = ROOT / "training" / "checkpoints"
CHECKPOINT_PATH = CHECKPOINT_DIR / "morris_net.pt"

BATCH_SIZE = 32
EPOCHS = 15
LEARNING_RATE = 0.001


class MorrisSelfPlayDataset(Dataset):
    """
    Dataset generado por self-play.

    Cada ejemplo contiene:
    - state: vector de tamaño 80
    - policy: vector one-hot de tamaño 624
    - value: resultado final [-1, 0, 1]
    """

    def __init__(self, dataset_path):
        if not dataset_path.exists():
            raise FileNotFoundError(
                f"No se encontró el dataset: {dataset_path}\n"
                f"Primero ejecuta: python training/self_play.py"
            )

        with open(dataset_path, "rb") as f:
            self.data = pickle.load(f)

        if len(self.data) == 0:
            raise ValueError("El dataset está vacío.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]

        state = torch.tensor(sample["state"], dtype=torch.float32)

        # La policy viene como one-hot.
        # CrossEntropyLoss espera el índice de la clase correcta.
        policy_vector = sample["policy"]
        policy_target = torch.tensor(
            policy_vector.index(1.0),
            dtype=torch.long
        )

        value = torch.tensor([sample["value"]], dtype=torch.float32)

        return state, policy_target, value


def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 70)
    print("TRAINING — MorrisNet")
    print("=" * 70)
    print(f"Device        : {device}")
    print(f"Dataset       : {DATASET_PATH}")
    print(f"Checkpoint    : {CHECKPOINT_PATH}")
    print(f"Batch size    : {BATCH_SIZE}")
    print(f"Epochs        : {EPOCHS}")
    print(f"Learning rate : {LEARNING_RATE}")
    print("=" * 70)

    dataset = MorrisSelfPlayDataset(DATASET_PATH)
    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    model = MorrisNet().to(device)

    policy_loss_fn = nn.CrossEntropyLoss()
    value_loss_fn = nn.MSELoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    for epoch in range(1, EPOCHS + 1):
        model.train()

        total_loss = 0.0
        total_policy_loss = 0.0
        total_value_loss = 0.0

        for states, policy_targets, values in dataloader:
            states = states.to(device)
            policy_targets = policy_targets.to(device)
            values = values.to(device)

            optimizer.zero_grad()

            policy_logits, predicted_values = model(states)

            policy_loss = policy_loss_fn(policy_logits, policy_targets)
            value_loss = value_loss_fn(predicted_values, values)

            loss = policy_loss + value_loss

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
        },
        CHECKPOINT_PATH
    )

    print("=" * 70)
    print(f"Modelo guardado en: {CHECKPOINT_PATH}")
    print(f"Ejemplos usados   : {len(dataset)}")
    print("=" * 70)


if __name__ == "__main__":
    train_model()