#!/bin/bash

# URL de la page OKX pour Bitcoin
URL="https://www.okx.com/price/bitcoin-btc"

# Fichier temporaire pour sauvegarder le HTML téléchargé
HTML_FILE="okx_bitcoin.html"

# Dossier de sortie et fichier CSV de sortie
# Ici, on remonte d'un niveau (..) pour accéder au dossier Data qui se trouve dans PGL_Project
DATA_DIR="../Data"
OUTPUT_FILE="$DATA_DIR/bitcoin_price.csv"

# Créer le dossier Data s'il n'existe pas
mkdir -p "$DATA_DIR"

# Télécharger la page en suivant les redirections et en simulant un navigateur
curl -s -L \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36" \
  "$URL" > "$HTML_FILE"

echo "La page a été téléchargée dans : $HTML_FILE"

# Extraction du prix depuis la div ciblée
PRICE=$(sed -n 's/.*<div class="index_price__VXAhl">\([^<]*\)<\/div>.*/\1/p' "$HTML_FILE")
PRICE=$(echo "$PRICE" | xargs)  # Suppression des espaces superflus

echo "Prix extrait : $PRICE"

# Récupération de la date et de l'heure d'exécution
EXECUTION_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Enregistrement dans le fichier CSV au format "date,prix"
echo "$EXECUTION_DATE,$PRICE" >> "$OUTPUT_FILE"

# Affichage du contenu du fichier CSV
cat "$OUTPUT_FILE"
