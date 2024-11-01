# -*- coding: utf-8 -*-
"""GAN/VAE.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZxeaD40XZBdn07LATBPo2ooqXfM3SfCc
"""

!pip install torch rdkit transformers chembl_webresource_client

import torch
import torch.nn as nn
import torch.optim as optim
from transformers import BertTokenizerFast
from chembl_webresource_client.new_client import new_client
import pandas as pd

# Fetch a limited number of SMILES strings from ChEMBL (first 500 entries)
compound_client = new_client.molecule
molecule_data = compound_client.filter(molecule_properties__full_molformula__isnull=False).only('molecule_chembl_id', 'molecule_structures')[:2500]  # Fetch first 500 entries

# Extract SMILES data with error handling
smiles_data = []
for molecule in molecule_data:
    molecule_structures = molecule.get('molecule_structures')
    if molecule_structures is not None:
        smiles = molecule_structures.get('canonical_smiles')
        if smiles:
            smiles_data.append(smiles)

# Convert to DataFrame
smiles_df = pd.DataFrame(smiles_data, columns=['smiles'])
print(f"Fetched {len(smiles_df)} SMILES strings from ChEMBL.")

# Tokenize SMILES strings
tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")
encoded_smiles = [tokenizer(smiles, padding="max_length", max_length=50, truncation=True, return_tensors="pt")["input_ids"]
                  for smiles in smiles_df['smiles']]
encoded_smiles = torch.cat(encoded_smiles, dim=0)
print(f"Tokenized {len(encoded_smiles)} SMILES strings.")

# VAE Encoder
class Encoder(nn.Module):
    def __init__(self, latent_dim, hidden_dim=256):
        super(Encoder, self).__init__()
        self.fc1 = nn.Linear(50, hidden_dim)
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)

    def forward(self, x):
        h = torch.relu(self.fc1(x))
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

# VAE Decoder
class Decoder(nn.Module):
    def __init__(self, latent_dim, hidden_dim=256):
        super(Decoder, self).__init__()
        self.fc1 = nn.Linear(latent_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 50)

    def forward(self, z):
        h = torch.relu(self.fc1(z))
        return torch.sigmoid(self.fc2(h))

# Discriminator for GAN
class Discriminator(nn.Module):
    def __init__(self, input_dim=50, hidden_dim=256):
        super(Discriminator, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        h = torch.relu(self.fc1(x))
        return torch.sigmoid(self.fc2(h))

# Hyperparameters
latent_dim = 128
lr = 0.0002
epochs = 10  # Reduced for quick testing

# Model initialization
encoder = Encoder(latent_dim)
decoder = Decoder(latent_dim)
discriminator = Discriminator()

# Optimizers
opt_vae = optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=lr)
opt_discriminator = optim.Adam(discriminator.parameters(), lr=lr)

# Loss functions
reconstruction_loss_fn = nn.MSELoss()

# Enable anomaly detection for debugging
torch.autograd.set_detect_anomaly(True)

# Training loop
for epoch in range(epochs):
    for real_data in encoded_smiles:
        real_data = real_data.float()  # Convert to float tensor
        real_data.requires_grad = True  # Ensure gradients are tracked for real data

        # VAE Forward Pass
        mu, logvar = encoder(real_data)
        std = torch.exp(0.5 * logvar)
        z = mu + std * torch.randn_like(std)  # Reparameterization trick

        # Decoder (Generator) forward pass
        reconstructed = decoder(z)

        # Compute VAE losses
        reconstruction_loss = reconstruction_loss_fn(reconstructed, real_data)
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        vae_loss = reconstruction_loss + kl_loss

        # Check for NaN values
        if torch.isnan(vae_loss).any():
            print("NaN detected in VAE loss.")
            continue

        # Backpropagate VAE loss
        opt_vae.zero_grad()
        vae_loss.backward(retain_graph=True)  # Keep graph for D loss computation
        opt_vae.step()

        # Discriminator - Train with real and fake data
        real_pred = discriminator(real_data)

        # Use no_grad for reconstructed to avoid tracking its gradients
        with torch.no_grad():
            fake_pred = discriminator(reconstructed)

        # Clamp values to avoid log(0)
        real_pred = torch.clamp(real_pred, 1e-10, 1.0)
        fake_pred = torch.clamp(fake_pred, 1e-10, 1.0)

        d_loss = -torch.mean(torch.log(real_pred) + torch.log(1 - fake_pred))

        # Backpropagate Discriminator loss
        opt_discriminator.zero_grad()
        d_loss.backward()
        opt_discriminator.step()

        # GAN Loss - Train Generator (Decoder)
        fake_pred = discriminator(reconstructed)
        fake_pred = torch.clamp(fake_pred, 1e-10, 1.0)  # Clamp again for stability
        g_loss = -torch.mean(torch.log(fake_pred))

        # Backpropagate Generator loss
        opt_vae.zero_grad()
        g_loss.backward()
        opt_vae.step()

# Function to generate new molecules
def generate_smiles(num_samples=5):
    with torch.no_grad():
        z = torch.randn(num_samples, latent_dim)  # Sample random latent vectors
        generated_smiles = decoder(z)
        # Map generated tensor back to SMILES if possible (requires further decoding/validation)
        return generated_smiles

# Generate samples
generated_samples = generate_smiles(num_samples=5)
print(generated_samples)

# Step 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Step 2: Define your models (ensure these are already defined in your code)
# encoder, decoder, and discriminator should be your model instances

import torch
import os

# Step 3: Save Models Function
def save_models(encoder, decoder, discriminator, model_dir):
    # Create the directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)

    # Save the models
    torch.save(encoder.state_dict(), os.path.join(model_dir, 'encoder.pth'))
    torch.save(decoder.state_dict(), os.path.join(model_dir, 'decoder.pth'))
    torch.save(discriminator.state_dict(), os.path.join(model_dir, 'discriminator.pth'))

    print("Models saved successfully to Google Drive!")

