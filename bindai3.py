# -*- coding: utf-8 -*-
"""bindAI3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Sm--rZTKd4GrwLPDdDRav4RSjAzio6dR
"""

# Install necessary libraries if not already installed
!pip install biopython
!pip install rdkit-pypi

import numpy as np
import pandas as pd
import requests
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Function to fetch SMILES strings from PubChem using the NCBI API
def fetch_smiles_from_pubchem(cid_list, api_key):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/property/CanonicalSMILES/JSON"
    smiles_data = []

    for cid in cid_list:
        url = base_url.format(cid)
        try:
            response = requests.get(url, params={"api_key": api_key})
            if response.status_code == 200:
                data = response.json()
                smiles = data["PropertyTable"]["Properties"][0]["CanonicalSMILES"]
                smiles_data.append(smiles)
            else:
                print(f"Error fetching data for CID {cid}: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred for CID {cid}: {str(e)}")

    return smiles_data

# Additional example CIDs
cid_list = ["2244", "3672", "5957", "1234", "4454", "2662", "3357", "2491", "5153", "5793"]  # Add more CIDs if needed
api_key = "266c8d48bb34a15b47565d7ad34005122508	"  # Replace with your NCBI API key
smiles_data = fetch_smiles_from_pubchem(cid_list, api_key)

# Define the preprocess_smiles function
def preprocess_smiles(smiles_data):
    # Create a simple character mapping for SMILES
    chars = sorted(set(''.join(smiles_data)))
    char_to_index = {c: i + 1 for i, c in enumerate(chars)}  # Start index at 1
    max_length = max(len(smiles) for smiles in smiles_data)

    # Convert SMILES to sequences
    def smiles_to_sequences(smiles, max_length):
        sequence = [char_to_index[char] for char in smiles]
        return sequence + [0] * (max_length - len(sequence))  # Pad with zeros

    # Convert all SMILES
    X_data = np.array([smiles_to_sequences(smiles, max_length) for smiles in smiles_data])

    return X_data, char_to_index, max_length

# Preprocess SMILES data
X_data, char_to_index, max_length = preprocess_smiles(smiles_data)

# Normalize the data
X_data = X_data / len(char_to_index)  # Normalize to range [0, 1]

# Define the generator model with dimensional adjustments
def build_generator(latent_dim, max_length, num_chars):
    model = keras.Sequential([
        layers.Dense(128, activation='relu', input_dim=latent_dim),
        layers.Dense(max_length * 1, activation='sigmoid'),  # Adjusted output size
        layers.Reshape((max_length, 1))  # Adjusting to 2D for dimensionality match
    ])
    return model

# Define the discriminator model
def build_discriminator(max_length, char_to_index):
    model = keras.Sequential([
        layers.Flatten(input_shape=(max_length, 1)),
        layers.Dense(128, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    return model

# Set parameters
latent_dim = 100  # Dimensionality of the latent space

# Build the GAN model
generator = build_generator(latent_dim, max_length, len(char_to_index))
discriminator = build_discriminator(max_length, char_to_index)

# Compile the discriminator
discriminator.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Create the GAN model
discriminator.trainable = False
gan_input = layers.Input(shape=(latent_dim,))
generated_sequence = generator(gan_input)
gan_output = discriminator(generated_sequence)
gan = keras.Model(gan_input, gan_output)
gan.compile(loss='binary_crossentropy', optimizer='adam')

# Training the GAN
def train_gan(epochs, batch_size, latent_dim):
    for epoch in range(epochs):
        # Generate random noise for the generator
        noise = np.random.normal(0, 1, size=[batch_size, latent_dim])

        # Generate fake SMILES sequences
        generated_smiles = generator.predict(noise)

        # Get a random set of real SMILES sequences
        idx = np.random.randint(0, X_data.shape[0], batch_size)
        real_smiles = X_data[idx].reshape(batch_size, max_length, 1)  # Reshape to match generated_smiles

        # Concatenate real and fake data
        X_combined = np.concatenate([real_smiles, generated_smiles])
        y_combined = np.concatenate([np.ones(batch_size), np.zeros(batch_size)])  # Labels

        # Train the discriminator
        d_loss = discriminator.train_on_batch(X_combined, y_combined)

        # Train the generator
        noise = np.random.normal(0, 1, size=[batch_size, latent_dim])
        g_loss = gan.train_on_batch(noise, np.ones(batch_size))

        # Print the progress
        if epoch % 100 == 0:
            print(f"Epoch: {epoch}, D Loss: {d_loss[0]}, D Acc.: {d_loss[1]}, G Loss: {g_loss}")

# Train the GAN
train_gan(epochs=1000, batch_size=32, latent_dim=latent_dim)

# Save the models to Google Drive
generator.save('/content/drive/MyDrive/generator_model.keras')
discriminator.save('/content/drive/MyDrive/discriminator_model.keras')

# Install necessary libraries if not already installed
!pip install biopython
!pip install rdkit-pypi

import numpy as np
import pandas as pd
import tensorflow as tf
from google.colab import drive

# Mount Google Drive to access saved models
drive.mount('/content/drive')

# Load the pre-trained generator model from Google Drive
generator_path = '/content/drive/MyDrive/generator_model.keras'

# Ensure model file exists
try:
    generator = tf.keras.models.load_model(generator_path)
    print("Generator model loaded successfully!")
except Exception as e:
    print("Failed to load model:", e)
    raise

# Function to generate SMILES strings
def generate_smiles(num_samples=5, latent_dim=100):
    # Generate random noise to feed into the generator model
    noise = np.random.normal(0, 1, (num_samples, latent_dim))
    generated = generator.predict(noise)
    # Convert the output to interpretable SMILES format (further decoding required for exact structure)
    return generated

# User Interaction
def main():
    try:
        # User inputs the number of SMILES sequences to generate
        num_samples = int(input("Enter the number of SMILES sequences you want to generate: "))

        print("\nGenerating new SMILES sequences...")
        generated_smiles = generate_smiles(num_samples=num_samples)

        # Display generated SMILES strings
        print("\nGenerated SMILES Sequences:\n", generated_smiles)

        # Option to save generated SMILES to Google Drive
        save_option = input("Save generated SMILES to Google Drive? (y/n): ")
        if save_option.lower() == 'y':
            pd.DataFrame(generated_smiles).to_csv('/content/drive/MyDrive/generated_smiles.csv', index=False)
            print("Generated SMILES saved to Google Drive.")
        else:
            print("Generated SMILES not saved.")
    except Exception as e:
        print("An error occurred:", e)

# Run the interactive main function
main()
