#!/usr/bin/env python3
"""
Générateur de bruit rose pour test de capsules microphoniques
Crée un fichier WAV avec du bruit rose (densité spectrale -3 dB/octave)
"""

import numpy as np
from scipy.io import wavfile
import argparse
import os

def generate_pink_noise(duration, sample_rate, num_rows=16):
    """
    Génère du bruit rose en utilisant la méthode de Voss-McCartney
    
    Args:
        duration: Durée en secondes
        sample_rate: Fréquence d'échantillonnage en Hz
        num_rows: Nombre de rangées pour l'algorithme (plus = plus précis)
    
    Returns:
        Signal audio normalisé entre -1 et 1
    """
    # Nombre total d'échantillons
    n_samples = int(duration * sample_rate)
    
    # Génération du bruit rose par la méthode des filtres en peigne
    # (plus simple et plus rapide que Voss-McCartney pour notre usage)
    
    # Générer du bruit blanc
    white_noise = np.random.randn(n_samples)
    
    # Appliquer un filtrage pour obtenir du bruit rose
    # Le bruit rose a une densité spectrale qui décroît de 3 dB par octave
    # On utilise une approximation par filtrage IIR
    
    # Coefficients de filtre approximatifs pour bruit rose
    # (méthode de Robert Bristow-Johnson)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004709510]
    a = [1.0, -2.494956002, 2.017265875, -0.522189400]
    
    # Appliquer le filtre
    from scipy.signal import lfilter
    pink_noise = lfilter(b, a, white_noise)
    
    # Normaliser pour éviter la saturation
    pink_noise = pink_noise / np.max(np.abs(pink_noise))
    
    return pink_noise

def generate_pink_noise_voss(n_samples, num_rows=16):
    """
    Méthode alternative : Voss-McCartney algorithm
    Plus précis mais plus lent
    """
    # Initialiser les rangées avec du bruit blanc
    rows = np.random.randn(num_rows, n_samples)
    
    # Créer le bruit rose par somme pondérée
    pink_noise = np.zeros(n_samples)
    
    for i in range(num_rows):
        # Décimation par facteur 2^i
        step = 2 ** i
        for j in range(0, n_samples, step):
            end = min(j + step, n_samples)
            pink_noise[j:end] += rows[i, j]
    
    # Normaliser
    pink_noise = pink_noise / np.max(np.abs(pink_noise))
    
    return pink_noise

def save_wav(filename, data, sample_rate, bit_depth=16):
    """
    Sauvegarde le signal audio en fichier WAV
    
    Args:
        filename: Nom du fichier de sortie
        data: Signal audio (float entre -1 et 1)
        sample_rate: Fréquence d'échantillonnage
        bit_depth: Profondeur en bits (16 ou 24)
    """
    # Convertir en format entier
    if bit_depth == 16:
        max_val = 32767
        dtype = np.int16
    elif bit_depth == 24:
        max_val = 8388607
        dtype = np.int32
    else:
        raise ValueError("Bit depth doit être 16 ou 24")
    
    # Appliquer le gain et convertir
    data_int = (data * max_val * 0.9).astype(dtype)  # 0.9 pour éviter le clipping
    
    # Sauvegarder
    wavfile.write(filename, sample_rate, data_int)
    print(f"✅ Fichier sauvegardé : {filename}")
    print(f"   Durée : {len(data) / sample_rate:.2f} secondes")
    print(f"   Fréquence d'échantillonnage : {sample_rate} Hz")
    print(f"   Profondeur : {bit_depth} bits")

def main():
    parser = argparse.ArgumentParser(
        description="Générateur de bruit rose pour test de capsules microphoniques"
    )
    
    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=10.0,
        help="Durée du signal en secondes (défaut: 10.0)"
    )
    
    parser.add_argument(
        "-r", "--rate",
        type=int,
        default=44100,
        help="Fréquence d'échantillonnage en Hz (défaut: 44100)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="pink_noise_test.wav",
        help="Nom du fichier de sortie (défaut: pink_noise_test.wav)"
    )
    
    parser.add_argument(
        "-b", "--bits",
        type=int,
        choices=[16, 24],
        default=16,
        help="Profondeur en bits (défaut: 16)"
    )
    
    parser.add_argument(
        "--voss",
        action="store_true",
        help="Utiliser l'algorithme Voss-McCartney (plus précis mais plus lent)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  GÉNÉRATEUR DE BRUIT ROSE")
    print("=" * 60)
    print(f"\nParamètres :")
    print(f"  Durée : {args.duration} secondes")
    print(f"  Fréquence d'échantillonnage : {args.rate} Hz")
    print(f"  Fichier de sortie : {args.output}")
    print(f"  Profondeur : {args.bits} bits")
    print(f"  Algorithme : {'Voss-McCartney' if args.voss else 'Filtrage IIR'}")
    print()
    
    # Générer le bruit rose
    print("🎵 Génération du bruit rose...")
    n_samples = int(args.duration * args.rate)
    
    if args.voss:
        pink_noise = generate_pink_noise_voss(n_samples)
    else:
        pink_noise = generate_pink_noise(args.duration, args.rate)
    
    # Sauvegarder en WAV
    save_wav(args.output, pink_noise, args.rate, args.bits)
    
    print("\n✅ Génération terminée !")
    print(f"\n📋 Utilisation :")
    print(f"   1. Copier {args.output} sur une clé USB")
    print(f"   2. Lire le fichier sur une enceinte de qualité")
    print(f"   3. Enregistrer avec vos capsules à tester")
    print(f"   4. Analyser avec analyze_capsules.py")

if __name__ == "__main__":
    main()
