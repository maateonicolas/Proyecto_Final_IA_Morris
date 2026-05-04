# training/evaluate_az_model.py
#
# Evalúa el checkpoint AlphaZero-like morris_net_az.pt.

from pathlib import Path
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game_engine import GameState
from agents.GRP1.model import MorrisNet, predict
from agents.GRP1.neural_utils import (
    encode_state,
    legal_action_indices,
    policy_to_legal_action,
)


CHECKPOINT_PATH = ROOT / "training" / "checkpoints" / "morris_net_az.pt"


def load_az_checkpoint(path=CHECKPOINT_PATH, device="cpu"):
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró checkpoint AZ: {path}\n"
            f"Primero ejecuta: python training/train_az.py"
        )

    checkpoint = torch.load(path, map_location=device)

    model = MorrisNet(
        input_size=checkpoint.get("input_size", 80),
        action_size=checkpoint.get("action_size", 624),
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    return model, checkpoint


def evaluate_az_initial_state():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model, checkpoint = load_az_checkpoint(device=device)

    state = GameState()
    player = 1

    encoded = encode_state(state, player)
    legal_indices = legal_action_indices(state, player)

    policy_probs, value = predict(
        model=model,
        encoded_state=encoded,
        legal_action_indices=legal_indices,
        device=device,
    )

    action = policy_to_legal_action(
        policy_probs=policy_probs,
        state=state,
        player=player,
    )

    print("=" * 70)
    print("EVALUATE AZ MODEL — MorrisNet")
    print("=" * 70)
    print(f"Checkpoint      : {CHECKPOINT_PATH}")
    print(f"Device          : {device}")
    print(f"Dataset type    : {checkpoint.get('dataset_type')}")
    print(f"Dataset size    : {checkpoint.get('dataset_size')}")
    print(f"Epochs          : {checkpoint.get('epochs')}")
    print(f"Legal actions   : {len(legal_indices)}")
    print(f"Selected action : {action}")
    print(f"Estimated value : {value:.4f}")
    print("=" * 70)

    return action, value


if __name__ == "__main__":
    evaluate_az_initial_state()