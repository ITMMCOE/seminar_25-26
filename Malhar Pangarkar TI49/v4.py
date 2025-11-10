import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_breast_cancer, make_moons, load_iris, load_wine, load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt

# =========================================
# Device
# =========================================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")


# =========================================
# Neural Nets
# =========================================
class PureSignedMeasureNN(nn.Module):
    def __init__(self, input_dim, omega=1.5, alpha=0.3):
        super(PureSignedMeasureNN, self).__init__()
        self.signed_measure = SignedMeasure(omega=omega, alpha=alpha)
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 16)
        self.output_fc = nn.Linear(16, 1)
        
    def forward(self, x):
        x = self.signed_measure(self.fc1(x))
        x = self.signed_measure(self.fc2(x))
        x = self.signed_measure(self.fc3(x))
        out = torch.sigmoid(self.output_fc(x))
        return out

class ReLUNN(nn.Module):
    def __init__(self, input_dim):
        super(ReLUNN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 16)
        self.output_fc = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        out = torch.sigmoid(self.output_fc(x))
        return out

# =========================================
# Training and Evaluation
# =========================================
def train(model, criterion, optimizer, X_train, y_train, epochs=300):
    model.train()
    losses = []
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
    return losses

def evaluate(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        outputs = model(X_test)
        preds = (outputs >= 0.5).float()
        acc = (preds.eq(y_test).sum().item()) / len(y_test)
    return acc

# =========================================
# Dataset loaders
# =========================================
def prepare_data(X, y):
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return (torch.tensor(X_train, dtype=torch.float32).to(device),
            torch.tensor(X_test, dtype=torch.float32).to(device),
            torch.tensor(y_train.reshape(-1,1), dtype=torch.float32).to(device),
            torch.tensor(y_test.reshape(-1,1), dtype=torch.float32).to(device),
            X.shape[1])

def load_medical():
    from sklearn.datasets import load_breast_cancer
    data = load_breast_cancer()
    return prepare_data(data.data, data.target)

def load_moons():
    from sklearn.datasets import make_moons
    X, y = make_moons(n_samples=500, noise=0.25, random_state=42)
    return prepare_data(X, y)

def load_iris_binary():
    data = load_iris()
    X = data.data
    y = (data.target != 0).astype(int)
    return prepare_data(X, y)

def load_wine_binary():
    data = load_wine()
    X = data.data
    y = (data.target != 0).astype(int)
    return prepare_data(X, y)

def load_digits_binary():
    data = load_digits()
    mask = (data.target == 0) | (data.target == 1)
    X = data.data[mask]
    y = data.target[mask]
    return prepare_data(X, y)

# =========================================
# Experiment Runner
# =========================================
def run_experiment(dataset_name, loader_fn, runs=5, epochs=300):
    print(f"\n=== Dataset: {dataset_name} ===")
    X_train, X_test, y_train, y_test, input_dim = loader_fn()
    criterion = nn.BCELoss()

    sm_accs, relu_accs = [], []
    sm_loss_plot, relu_loss_plot = None, None

    for r in range(runs):
        # Signed Measure
        model_sm = PureSignedMeasureNN(input_dim).to(device)
        optimizer = optim.Adam(model_sm.parameters(), lr=0.001)
        losses_sm = train(model_sm, criterion, optimizer, X_train, y_train, epochs)
        acc_sm = evaluate(model_sm, X_test, y_test)
        sm_accs.append(acc_sm)
        if r == 0: sm_loss_plot = losses_sm

        # ReLU
        model_relu = ReLUNN(input_dim).to(device)
        optimizer = optim.Adam(model_relu.parameters(), lr=0.001)
        losses_relu = train(model_relu, criterion, optimizer, X_train, y_train, epochs)
        acc_relu = evaluate(model_relu, X_test, y_test)
        relu_accs.append(acc_relu)
        if r == 0: relu_loss_plot = losses_relu

    print(f"SignedMeasureNN: {np.mean(sm_accs):.4f} ± {np.std(sm_accs):.4f}")
    print(f"ReLU NN:         {np.mean(relu_accs):.4f} ± {np.std(relu_accs):.4f}")

    # Plot training loss for first run
    plt.figure(figsize=(6,4))
    plt.plot(sm_loss_plot, label='SignedMeasure Loss')
    plt.plot(relu_loss_plot, label='ReLU Loss')
    plt.title(f"Training Loss Curve — {dataset_name}")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    return np.mean(sm_accs), np.std(sm_accs), np.mean(relu_accs), np.std(relu_accs)

# =========================================
# Run All Datasets
# =========================================
datasets = {
    "Breast Cancer": load_medical,
    "Moons": load_moons,
    "Iris": load_iris_binary,
    "Wine": load_wine_binary,
    "Digits (0 vs 1)": load_digits_binary
}

results = {}
for name, loader in datasets.items():
    results[name] = run_experiment(name, loader, runs=5, epochs=300)

# =========================================
# Summary Plot with Error Bars
# =========================================
labels = list(results.keys())
sm_mean = [results[k][0] for k in labels]
sm_std  = [results[k][1] for k in labels]
relu_mean = [results[k][2] for k in labels]
relu_std  = [results[k][3] for k in labels]

x = np.arange(len(labels))
width = 0.35

plt.figure(figsize=(10,6))
plt.bar(x - width/2, sm_mean, width, yerr=sm_std, capsize=4, label='SignedMeasure NN')
plt.bar(x + width/2, relu_mean, width, yerr=relu_std, capsize=4, label='ReLU NN')

plt.ylabel('Accuracy')
plt.title('QPNN (Signed Measure) vs ReLU — Mean ± Std over 5 runs')
plt.xticks(x, labels, rotation=30)
plt.legend()
plt.tight_layout()
plt.show()
