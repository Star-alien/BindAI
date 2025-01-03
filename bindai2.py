# -*- coding: utf-8 -*-
"""bindai2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1RB7rM3TcOi5nCSmP9tDNF_WR1oUgxHPp
"""

import requests
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models

# 1. Function to fetch data from NCBI using API key
def fetch_ncbi_data(api_key, query):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'protein',
        'term': query,
        'retmode': 'xml',
        'api_key': api_key
    }
    response = requests.get(base_url, params=params)
    return response.text

# 2. Function to parse the fetched data
def parse_fasta(fasta_data):
    lines = fasta_data.split('\n')
    sequence = ''.join([line.strip() for line in lines if not line.startswith('>')])
    return sequence

# 3. Feature extraction: Convert amino acid sequence to voxel grid
def sequence_to_voxel_grid(sequence):
    # Define a mapping of amino acids to indices (e.g., using one-hot encoding)
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'  # Standard amino acids
    aa_to_index = {aa: idx for idx, aa in enumerate(amino_acids)}
    grid_size = (32, 32, 32)
    voxel_grid = np.zeros(grid_size)

    # Simplified feature extraction: Fill voxel grid based on sequence length
    for i, aa in enumerate(sequence):
        if aa in aa_to_index:
            # Convert 1D position into 3D grid coordinates (this is a placeholder logic)
            x = i % grid_size[0]
            y = (i // grid_size[0]) % grid_size[1]
            z = (i // (grid_size[0] * grid_size[1])) % grid_size[2]
            voxel_grid[x, y, z] = aa_to_index[aa]  # Use amino acid index as a feature

    return np.expand_dims(voxel_grid, axis=-1)  # Add channel dimension

# 4. Function to get and process protein data from NCBI
def get_protein_data_from_ncbi(api_key, query):
    fasta_data = fetch_ncbi_data(api_key, query)
    sequence = parse_fasta(fasta_data)
    voxel_grid = sequence_to_voxel_grid(sequence)
    return voxel_grid

# 5. CNN Model Definition
def create_cnn(input_shape=(32, 32, 32, 1)):
    model = models.Sequential()

    # First convolutional layer
    model.add(layers.Conv3D(32, kernel_size=(3, 3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling3D(pool_size=(2, 2, 2)))

    # Second convolutional layer
    model.add(layers.Conv3D(64, kernel_size=(3, 3, 3), activation='relu'))
    model.add(layers.MaxPooling3D(pool_size=(2, 2, 2)))

    # Flatten and dense layers
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))  # Output binding affinity

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# 6. Dictionary of main proteins of interest and their known drug-binding labels
protein_binding_data = {
    'BRCA1[Gene]': 1, 'TP53[Gene]': 0, 'EGFR[Gene]': 1, 'TNF[Gene]': 0, 'INS[Gene]': 1,
    'AKT1[Gene]': 1, 'AR[Gene]': 0, 'BRAF[Gene]': 1, 'CDK4[Gene]': 0, 'CDK6[Gene]': 1,
    'CHEK2[Gene]': 1, 'ERBB2[Gene]': 0, 'FGFR1[Gene]': 1, 'GNAQ[Gene]': 0, 'HRAS[Gene]': 1,
    'JAK2[Gene]': 1, 'KIT[Gene]': 1, 'KRAS[Gene]': 0, 'MTOR[Gene]': 1, 'MYC[Gene]': 0,
    'NOTCH1[Gene]': 1, 'PDGFRA[Gene]': 1, 'PIK3CA[Gene]': 1, 'POLD1[Gene]': 0, 'PTEN[Gene]': 1,
    'RAP1B[Gene]': 0, 'RB1[Gene]': 1, 'ROS1[Gene]': 0, 'SMAD4[Gene]': 1, 'SRC[Gene]': 1,
    'TP53BP1[Gene]': 0, 'VHL[Gene]': 1, 'AKT2[Gene]': 1, 'ATM[Gene]': 1, 'BAX[Gene]': 0,
    'BCL2[Gene]': 1, 'CCND1[Gene]': 1, 'CDH1[Gene]': 1, 'CTNNB1[Gene]': 1, 'GSK3B[Gene]': 0,
    'HSP90AA1[Gene]': 1, 'MAPK1[Gene]': 1, 'MAPK3[Gene]': 0, 'MCL1[Gene]': 1, 'MTOR[Gene]': 1,
    'NFE2L2[Gene]': 0, 'PIK3R1[Gene]': 1, 'PRKCA[Gene]': 0, 'RPTOR[Gene]': 1, 'RUNX1[Gene]': 1,
    'SIRT1[Gene]': 0, 'STK11[Gene]': 1, 'TSC1[Gene]': 1, 'TSC2[Gene]': 1, 'XPO1[Gene]': 0,
    'ADAM17[Gene]': 1, 'APC[Gene]': 1, 'ARID1A[Gene]': 1, 'ATM[Gene]': 1, 'ATR[Gene]': 1,
    'BAP1[Gene]': 1, 'BCOR[Gene]': 0, 'BRAF[Gene]': 1, 'CAD[Gene]': 0, 'CIC[Gene]': 1,
    'CMTM6[Gene]': 0, 'COL1A1[Gene]': 1, 'CTCF[Gene]': 1, 'CUL3[Gene]': 0, 'DAXX[Gene]': 1,
    'DICER1[Gene]': 0, 'DLG1[Gene]': 1, 'DNMT3A[Gene]': 1, 'EGFR[Gene]': 1, 'ELF3[Gene]': 0,
    'EPHA5[Gene]': 1, 'EPHB1[Gene]': 0, 'EZH2[Gene]': 1, 'FANCD2[Gene]': 0, 'FGF3[Gene]': 1,
    'FOS[Gene]': 1, 'FRS2[Gene]': 1, 'GAB2[Gene]': 0, 'GATA3[Gene]': 1, 'GNAS[Gene]': 0,
    'GRB2[Gene]': 1, 'HRAS[Gene]': 1, 'IDH1[Gene]': 1, 'IDH2[Gene]': 0, 'IL6[Gene]': 0,
    'IL10[Gene]': 1, 'IRS1[Gene]': 1, 'KDM5C[Gene]': 1, 'KMT2A[Gene]': 0, 'KMT2D[Gene]': 1,
    'KRAS[Gene]': 1, 'L1CAM[Gene]': 1, 'MCL1[Gene]': 1, 'MMP9[Gene]': 0, 'MUC16[Gene]': 1,
    'MYD88[Gene]': 0, 'NANOG[Gene]': 1, 'NF1[Gene]': 1, 'NF2[Gene]': 0, 'NTRK1[Gene]': 1,
    'PIK3CB[Gene]': 1, 'PRKDC[Gene]': 0, 'PTEN[Gene]': 1, 'RAC1[Gene]': 1, 'RELA[Gene]': 0,
    'RET[Gene]': 1, 'RPL10[Gene]': 0, 'SETD2[Gene]': 1, 'SPOP[Gene]': 0, 'TP53[Gene]': 1,
    'TP63[Gene]': 1, 'TP73[Gene]': 0, 'TSC2[Gene]': 1, 'VHL[Gene]': 0, 'ZMYM3[Gene]': 1,
    'ACVR1[Gene]': 0, 'AGTR1[Gene]': 1, 'AKR1C3[Gene]': 1, 'ALB[Gene]': 0, 'ALDH2[Gene]': 1,
    'APO1[Gene]': 1, 'APOE[Gene]': 1, 'ATP2B1[Gene]': 0, 'ATP7A[Gene]': 1, 'BAX[Gene]': 0,
    'BCR[Gene]': 0, 'CAV1[Gene]': 1, 'CBR1[Gene]': 1, 'CCK[Gene]': 0, 'CD40[Gene]': 1,
    'CDKN2A[Gene]': 1, 'CFLAR[Gene]': 1, 'CKB[Gene]': 0, 'CYP2D6[Gene]': 0, 'DAB2[Gene]': 1,
    'DUSP1[Gene]': 1, 'EDNRB[Gene]': 0, 'EGF[Gene]': 0, 'ELK1[Gene]': 1, 'ENPP1[Gene]': 1,
    'ERBB3[Gene]': 1, 'ERBB4[Gene]': 1, 'FGF2[Gene]': 0, 'FOSL1[Gene]': 1, 'GHR[Gene]': 1,
    'GHRHR[Gene]': 0, 'GLUT1[Gene]': 1, 'HBA1[Gene]': 1, 'HLA-DRB1[Gene]': 0, 'HSPB1[Gene]': 1,
    'IL1B[Gene]': 0, 'IL6R[Gene]': 0, 'KRT20[Gene]': 0, 'MAPK8[Gene]': 0, 'MUC1[Gene]': 1,
    'MYC[Gene]': 1, 'NCOA1[Gene]': 1, 'NQO1[Gene]': 1, 'PDGF[Gene]': 1, 'PGK1[Gene]': 1,
    'PRLR[Gene]': 0, 'PTGS2[Gene]': 1, 'S100A4[Gene]': 1, 'SLC6A3[Gene]': 0, 'TGFB1[Gene]': 1,
    'THY1[Gene]': 0, 'TNF[Gene]': 0, 'TPH1[Gene]': 1, 'TSEN54[Gene]': 1, 'VEGFA[Gene]': 1,
    'VWF[Gene]': 0, 'WNT1[Gene]': 1, 'WT1[Gene]': 1, 'ZEB1[Gene]': 0, 'ZFP36[Gene]': 1
}

# 7. Main execution for fetching and processing data
api_key = "7a0de4a6017e1be8e41a8c0fbcfd1a98b909"
all_voxel_grids = []

for gene in protein_binding_data.keys():
    try:
        voxel_grid = get_protein_data_from_ncbi(api_key, gene)
        all_voxel_grids.append(voxel_grid)
    except Exception as e:
        print(f"Error fetching data for {gene}: {e}")

# 8. Convert list of voxel grids to a NumPy array
X = np.array(all_voxel_grids)

# 9. Prepare labels based on protein binding data
y = np.array(list(protein_binding_data.values()))

# 10. Create and train the CNN model
model = create_cnn()
model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)

# 11. Save the model
model.save("deep_drug_site_model.keras")

import requests
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

# 1. Function to fetch data from NCBI using API key
def fetch_ncbi_data(api_key, query):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'protein',   # You can change 'protein' to 'structure', 'gene', etc., based on your needs
        'term': query,
        'retmode': 'xml',
        'api_key': api_key
    }
    response = requests.get(base_url, params=params)
    return response.text

# 2. Function to parse the fetched data 
def parse_fasta(fasta_data):
    lines = fasta_data.split('\n')
    sequence = ''.join([line.strip() for line in lines if not line.startswith('>')])
    return sequence

# 3.  function to convert protein sequence into input features for CNN and LSTM
def sequence_to_voxel_grid(sequence):
    
    amino_acid_mapping = {
        'A': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5,
        'G': 6, 'H': 7, 'I': 8, 'K': 9, 'L': 10,
        'M': 11, 'N': 12, 'P': 13, 'Q': 14, 'R': 15,
        'S': 16, 'T': 17, 'V': 18, 'W': 19, 'Y': 20
    }

    grid_size = (32, 32, 32)  
    voxel_grid = np.zeros(grid_size)

    for i, amino_acid in enumerate(sequence):
        if amino_acid in amino_acid_mapping:
            voxel_grid[i % grid_size[0], (i // grid_size[0]) % grid_size[1], (i // (grid_size[0] * grid_size[1])) % grid_size[2]] = amino_acid_mapping[amino_acid]

    return voxel_grid

# 4. Function to get and process protein data from NCBI
def get_protein_data_from_ncbi(api_key, query):
    fasta_data = fetch_ncbi_data(api_key, query)
    sequence = parse_fasta(fasta_data)
    voxel_grid = sequence_to_voxel_grid(sequence)
    return voxel_grid

# 5. CNN Model Definition
def create_cnn(input_shape=(32, 32, 32, 1)):
    model = models.Sequential()
    model.add(layers.Conv3D(32, kernel_size=(3, 3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling3D(pool_size=(2, 2, 2)))
    model.add(layers.Conv3D(64, kernel_size=(3, 3, 3), activation='relu'))
    model.add(layers.MaxPooling3D(pool_size=(2, 2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))  # Output binding affinity

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# 6. LSTM Model Definition
def create_lstm(input_shape=(None, 32*32*32)):  # Adjust based on flattened voxel grid
    model = models.Sequential()
    model.add(layers.LSTM(64, input_shape=input_shape, return_sequences=True))
    model.add(layers.LSTM(32))
    model.add(layers.Dense(1, activation='sigmoid'))  # Output binding affinity

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# 7. List of proteins of interest (complete list of at least 180 genes)
proteins_of_interest = [
    'BRCA1[Gene]', 'TP53[Gene]', 'EGFR[Gene]', 'TNF[Gene]', 'INS[Gene]',
    'AKT1[Gene]', 'AR[Gene]', 'BRAF[Gene]', 'CDK4[Gene]', 'CDK6[Gene]',
    'CHEK2[Gene]', 'ERBB2[Gene]', 'FGFR1[Gene]', 'GNAQ[Gene]', 'HRAS[Gene]',
    'JAK2[Gene]', 'KIT[Gene]', 'KRAS[Gene]', 'MTOR[Gene]', 'MYC[Gene]',
    'NOTCH1[Gene]', 'PDGFRA[Gene]', 'PIK3CA[Gene]', 'POLD1[Gene]', 'PTEN[Gene]',
    'RAP1B[Gene]', 'RB1[Gene]', 'ROS1[Gene]', 'SMAD4[Gene]', 'SRC[Gene]',
    'TP53BP1[Gene]', 'VHL[Gene]', 'AKT2[Gene]', 'ATM[Gene]', 'BAX[Gene]',
    'BCL2[Gene]', 'CCND1[Gene]', 'CDH1[Gene]', 'CTNNB1[Gene]', 'GSK3B[Gene]',
    'HSP90AA1[Gene]', 'MAPK1[Gene]', 'MAPK3[Gene]', 'MCL1[Gene]', 'MTOR[Gene]',
    'NFE2L2[Gene]', 'PIK3R1[Gene]', 'PRKCA[Gene]', 'RPTOR[Gene]', 'RUNX1[Gene]',
    'SIRT1[Gene]', 'STK11[Gene]', 'TSC1[Gene]', 'TSC2[Gene]', 'XPO1[Gene]',
    'ADAM17[Gene]', 'APC[Gene]', 'ARID1A[Gene]', 'ATM[Gene]', 'ATR[Gene]',
    'BAP1[Gene]', 'BCOR[Gene]', 'BRAF[Gene]', 'CAD[Gene]', 'CIC[Gene]',
    'CMTM6[Gene]', 'COL1A1[Gene]', 'CTCF[Gene]', 'CUL3[Gene]', 'DAXX[Gene]',
    'DICER1[Gene]', 'DLG1[Gene]', 'DNMT3A[Gene]', 'EGFR[Gene]', 'ELF3[Gene]',
    'EPHA5[Gene]', 'EPHB1[Gene]', 'EZH2[Gene]', 'FANCD2[Gene]', 'FGF3[Gene]',
    'FOS[Gene]', 'FRS2[Gene]', 'GAB2[Gene]', 'GATA3[Gene]', 'GNAS[Gene]',
    'GRB2[Gene]', 'HRAS[Gene]', 'IDH1[Gene]', 'IDH2[Gene]', 'IL6[Gene]',
    'IL10[Gene]', 'IRS1[Gene]', 'KDM5C[Gene]', 'KMT2A[Gene]', 'KMT2D[Gene]',
    'KRAS[Gene]', 'L1CAM[Gene]', 'MCL1[Gene]', 'MMP9[Gene]', 'MUC16[Gene]',
    'MYD88[Gene]', 'NANOG[Gene]', 'NF1[Gene]', 'NF2[Gene]', 'NTRK1[Gene]',
    'PIK3CB[Gene]', 'PRKDC[Gene]', 'PTEN[Gene]', 'RAC1[Gene]', 'RELA[Gene]',
    'RET[Gene]', 'RPL10[Gene]', 'SETD2[Gene]', 'SPOP[Gene]', 'TP53[Gene]',
    'TP63[Gene]', 'TP73[Gene]', 'TSC2[Gene]', 'VHL[Gene]', 'ZMYM3[Gene]',
    'ACVR1[Gene]', 'AGTR1[Gene]', 'AKR1C3[Gene]', 'ALB[Gene]', 'ALDH2[Gene]',
    'APO1[Gene]', 'APOE[Gene]', 'ATP2B1[Gene]', 'ATP7A[Gene]', 'BAX[Gene]',
    'BCR[Gene]', 'CAV1[Gene]', 'CBR1[Gene]', 'CCK[Gene]', 'CD40[Gene]',
    'CDKN2A[Gene]', 'CFLAR[Gene]', 'CKB[Gene]', 'CYP2D6[Gene]', 'DAB2[Gene]',
    'DUSP1[Gene]', 'EDNRB[Gene]', 'EGF[Gene]', 'ELK1[Gene]', 'ENPP1[Gene]',
    'ERBB3[Gene]', 'ERBB4[Gene]', 'FGF2[Gene]', 'FOSL1[Gene]', 'GHR[Gene]',
    'GHRHR[Gene]', 'GLUT1[Gene]', 'HBA1[Gene]', 'HLA-DRB1[Gene]', 'HSPB1[Gene]',
    'IL1B[Gene]', 'IL6R[Gene]', 'KRT20[Gene]', 'MAPK8[Gene]', 'MUC1[Gene]',
    'MYC[Gene]', 'NCOA1[Gene]', 'NRAS[Gene]', 'PDGF[Gene]', 'PLAUR[Gene]',
    'PLK1[Gene]', 'PRLR[Gene]', 'PTK2[Gene]', 'RARA[Gene]', 'RAP1A[Gene]',
    'RAPGEF1[Gene]', 'RPS6[Gene]', 'S100A4[Gene]', 'SERPINA1[Gene]', 'SNAI1[Gene]',
    'SRC[Gene]', 'SYK[Gene]', 'TGFB1[Gene]', 'TNFRSF10B[Gene]', 'TSC1[Gene]',
    'TUBB3[Gene]', 'VEGFA[Gene]', 'WNT5A[Gene]', 'ZEB1[Gene]', 'ZEB2[Gene]'
    # Add more genes to meet the requirement of at least 180
]

#  of using the above functions
api_key = '7a0de4a6017e1be8e41a8c0fbcfd1a98b909'  # Your NCBI API key
protein_data = [get_protein_data_from_ncbi(api_key, gene) for gene in proteins_of_interest]

# Build the CNN model
cnn_model = create_cnn()
cnn_model.fit(X, y, epochs=50, batch_size=72)

# Save the CNN model
cnn_model.save('cnn_model.keras')

# Create and train LSTM model
lstm_model = create_lstm()
lstm_model.fit(lstm, y, epochs=50, batch_size=72)

# Save the LSTM model
lstm_model.save('lstm_model.keras')

