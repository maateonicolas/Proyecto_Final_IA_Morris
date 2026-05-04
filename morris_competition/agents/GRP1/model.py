import torch
import torch.nn as nn
import torch.nn.functional as F


INPUT_SIZE = 80
ACTION_SIZE = 624


class MorrisNet(nn.Module):
    """
    Primera red neuronal para Nine Men's Morris.

    Entrada:
        Vector de estado codificado con tamaño 80.

    Salidas:
        policy_logits: puntaje para cada acción posible.
        value: estimación del estado en rango [-1, 1].

    ACTION_SIZE = 624:
        - 24 acciones de place
        - 24 * 24 acciones de move/fly
        - 24 acciones de capture
    """

    def __init__(self, input_size=INPUT_SIZE, action_size=ACTION_SIZE):
        super().__init__()

        self.input_size = input_size
        self.action_size = action_size

        self.body = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, 64),
            nn.ReLU(),
        )

        self.policy_head = nn.Linear(64, action_size)

        self.value_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Tanh()
        )

    def forward(self, x):
        """
        x shape:
            [batch_size, INPUT_SIZE]

        returns:
            policy_logits shape: [batch_size, ACTION_SIZE]
            value shape: [batch_size, 1]
        """

        features = self.body(x)

        policy_logits = self.policy_head(features)
        value = self.value_head(features)

        return policy_logits, value


def create_model():
    return MorrisNet()


def save_model(model, path):
    torch.save(model.state_dict(), path)


def load_model(path, device="cpu"):
    model = MorrisNet()
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()
    return model


def predict(model, encoded_state, legal_action_indices=None, device="cpu"):
    """
    Predice policy y value para un estado.

    encoded_state:
        lista o tensor de tamaño 80.

    legal_action_indices:
        lista de índices legales. Si se pasa, se enmascaran las acciones ilegales.

    returns:
        policy_probs, value
    """

    model.eval()

    with torch.no_grad():
        x = torch.tensor(encoded_state, dtype=torch.float32, device=device).unsqueeze(0)

        policy_logits, value = model(x)

        policy_logits = policy_logits.squeeze(0)

        if legal_action_indices is not None:
            mask = torch.full_like(policy_logits, float("-inf"))
            mask[legal_action_indices] = policy_logits[legal_action_indices]
            policy_logits = mask

        policy_probs = F.softmax(policy_logits, dim=0)

        return policy_probs.cpu(), float(value.item())