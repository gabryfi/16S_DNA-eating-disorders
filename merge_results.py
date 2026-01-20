import pandas as pd
import glob
import os
import re

# ==========================
# PARAMETRI
# ==========================
THRESHOLD = 0.01  # soglia in percentuale (0.01%)

# ==========================
# FUNZIONI
# ==========================
def normalize_genus(name):
    name = name.strip()  # rimuove spazi iniziali/finali (FIX FONDAMENTALE)
    name = name.replace("Escherichia/Shigella", "EscherichiaShigella")
    name = name.replace("Lachnospiraceae incertae sedis", "Lachnospiracea_incertae_sedis")
    name = re.sub(r"\s+", "_", name)
    name = name.replace("/", "")
    return name

# ==========================
# INPUT
# ==========================
files = glob.glob("*_bracken_report.txt")

all_samples = []

for f in files:
    sample = os.path.basename(f).replace("_bracken_report.txt", "")

    df = pd.read_csv(
        f,
        sep="\t",
        header=None,
        names=[
            "percent",
            "reads_clade",
            "reads_taxon",
            "rank",
            "taxid",
            "name"
        ]
    )

    # Tieni solo livello Genus
    df = df[df["rank"] == "G"][["name", "percent"]]

    # Normalizza i nomi dei generi
    df["name"] = df["name"].apply(normalize_genus)

    # Applica soglia 0.01%
    df.loc[df["percent"] < THRESHOLD, "percent"] = 0.0

    # Aggiungi nome campione
    df["sample"] = sample

    all_samples.append(df)

# ==========================
# MERGE FINALE
# ==========================
merged = pd.concat(all_samples)

table = merged.pivot_table(
    index="sample",
    columns="name",
    values="percent",
    fill_value=0
)

# Ordina alfabeticamente le colonne
table = table.sort_index(axis=1)

# ==========================
# OUTPUT
# ==========================
table.to_csv("bracken_genus_abundance_0.01pct.csv")

print("Creato file: bracken_genus_abundance_0.01pct.csv")
