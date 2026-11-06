#!/usr/bin/env python3
"""
Analyse comparative de capsules microphoniques
Compare les enregistrements de bruit rose pour identifier les capsules défectueuses
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import welch
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import glob
import os
import datetime

def load_and_analyze(filename):
    """
    Charge un fichier WAV et analyse son spectre
    
    Returns:
        dict avec : freqs, psd, rms, peak_freq
    """
    # Charger le fichier
    sample_rate, data = wavfile.read(filename)
    
    # Convertir en float normalisé
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    
    # Si stéréo, prendre seulement le premier canal
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # Calculer le RMS
    rms = np.sqrt(np.mean(data**2))
    rms_db = 20 * np.log10(rms) if rms > 0 else -100
    
    # Calculer le spectre de puissance (PSD) avec Welch
    freqs, psd = welch(data, fs=sample_rate, nperseg=2048)
    
    # Convertir en dB
    psd_db = 10 * np.log10(psd + 1e-10)  # +1e-10 pour éviter log(0)
    
    # Trouver la fréquence de pic (devrait être large pour bruit rose)
    peak_idx = np.argmax(psd)
    peak_freq = freqs[peak_idx]
    
    return {
        'filename': filename,
        'sample_rate': sample_rate,
        'duration': len(data) / sample_rate,
        'rms': rms,
        'rms_db': rms_db,
        'freqs': freqs,
        'psd_db': psd_db,
        'peak_freq': peak_freq
    }

def compare_capsules(results, output_pdf="analyse_capsules.pdf"):
    """
    Compare les résultats et génère un rapport PDF
    """
    print("\n" + "=" * 60)
    print("  ANALYSE COMPARATIVE DES CAPSULES")
    print("=" * 60)
    
    # Calculer les statistiques
    rms_values = [r['rms_db'] for r in results]
    mean_rms = np.mean(rms_values)
    std_rms = np.std(rms_values)
    
    print(f"\n📊 Statistiques :")
    print(f"   Nombre de capsules : {len(results)}")
    print(f"   RMS moyen : {mean_rms:.2f} dB")
    print(f"   Écart-type : {std_rms:.2f} dB")
    
    # Identifier les outliers
    threshold = 6.0  # dB
    outliers = []
    
    print(f"\n📋 Résultats détaillés :")
    for i, r in enumerate(results):
        deviation = r['rms_db'] - mean_rms
        status = "✅ OK" if abs(deviation) < threshold else "❌ REJETÉE"
        
        print(f"   {os.path.basename(r['filename']):30s} : {r['rms_db']:6.2f} dB "
              f"(Δ {deviation:+5.2f} dB) {status}")
        
        if abs(deviation) >= threshold:
            outliers.append((i, r, deviation))
    
    if outliers:
        print(f"\n⚠️  {len(outliers)} capsule(s) hors tolérance (±{threshold} dB)")
    else:
        print(f"\n✅ Toutes les capsules sont dans la tolérance (±{threshold} dB)")
    
    # Générer le rapport PDF
    print(f"\n📄 Génération du rapport : {output_pdf}")
    
    with PdfPages(output_pdf) as pdf:
        # Page 1 : Superposition des spectres
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for r in results:
            deviation = r['rms_db'] - mean_rms
            color = 'red' if abs(deviation) >= threshold else 'blue'
            alpha = 0.7 if abs(deviation) >= threshold else 0.5
            
            ax.semilogx(r['freqs'], r['psd_db'], 
                       label=f"{os.path.basename(r['filename'])} ({r['rms_db']:.1f} dB)",
                       color=color, alpha=alpha, linewidth=1.5)
        
        ax.set_xlabel('Fréquence (Hz)', fontsize=12)
        ax.set_ylabel('Densité spectrale de puissance (dB)', fontsize=12)
        ax.set_title('Comparaison des réponses en fréquence des capsules\n(Bruit rose)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, which="both", ls="-", alpha=0.3)
        ax.legend(loc='upper right', fontsize=9)
        ax.set_xlim([20, 20000])
        
        # Ajouter une note
        text = (f"Date : {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                f"Nombre de capsules : {len(results)}\n"
                f"RMS moyen : {mean_rms:.2f} dB\n"
                f"Écart-type : {std_rms:.2f} dB\n"
                f"Seuil de rejet : ±{threshold} dB")
        ax.text(0.02, 0.98, text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()
        
        # Page 2 : Tableau récapitulatif
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        # Créer le tableau
        table_data = []
        headers = ['Capsule', 'RMS (dB)', 'Écart (dB)', 'Statut']
        
        for r in results:
            deviation = r['rms_db'] - mean_rms
            status = "✅ CONFORME" if abs(deviation) < threshold else "❌ REJETÉE"
            table_data.append([
                os.path.basename(r['filename']),
                f"{r['rms_db']:.2f}",
                f"{deviation:+.2f}",
                status
            ])
        
        # Ajouter la ligne de statistiques
        table_data.append(['', '', '', ''])
        table_data.append(['MOYENNE', f"{mean_rms:.2f}", "0.00", ""])
        table_data.append(['ÉCART-TYPE', f"{std_rms:.2f}", "", ""])
        
        # Dessiner le tableau
        table = ax.table(cellText=table_data, colLabels=headers,
                        cellLoc='center', loc='center',
                        colWidths=[0.4, 0.2, 0.2, 0.2])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Colorer les cellules
        for i, row in enumerate(table_data):
            if i < len(results):
                deviation = float(row[2])
                if abs(deviation) >= threshold:
                    for j in range(4):
                        table[i+1, j].set_facecolor('#ffcccc')
                else:
                    for j in range(4):
                        table[i+1, j].set_facecolor('#ccffcc')
        
        # Colorer les en-têtes
        for j in range(4):
            table[0, j].set_facecolor('#4472C4')
            table[0, j].set_text_props(color='white', fontweight='bold')
        
        ax.set_title('Rapport d\'analyse comparative des capsules', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()
    
    print(f"✅ Rapport généré : {output_pdf}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyse comparative de capsules microphoniques"
    )
    
    parser.add_argument(
        "-i", "--input-dir",
        type=str,
        default=".",
        help="Dossier contenant les fichiers WAV (défaut: dossier courant)"
    )
    
    parser.add_argument(
        "-p", "--pattern",
        type=str,
        default="*.wav",
        help="Motif pour trouver les fichiers (défaut: *.wav)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="analyse_capsules.pdf",
        help="Nom du rapport PDF (défaut: analyse_capsules.pdf)"
    )
    
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=6.0,
        help="Seuil de rejet en dB (défaut: 6.0)"
    )
    
    args = parser.parse_args()
    
    # Trouver tous les fichiers WAV
    search_pattern = os.path.join(args.input_dir, args.pattern)
    wav_files = sorted(glob.glob(search_pattern))
    
    if not wav_files:
        print(f"❌ Aucun fichier WAV trouvé dans {args.input_dir}")
        print(f"   Motif recherché : {search_pattern}")
        return
    
    print(f"\n🔍 {len(wav_files)} fichier(s) WAV trouvé(s)")
    
    # Analyser chaque fichier
    results = []
    for wav_file in wav_files:
        print(f"   Analyse : {os.path.basename(wav_file)}...", end=" ")
        try:
            result = load_and_analyze(wav_file)
            results.append(result)
            print(f"✅ ({result['duration']:.1f}s, {result['rms_db']:.1f} dB)")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    if len(results) < 2:
        print("\n⚠️  Il faut au moins 2 fichiers valides pour une comparaison")
        return
    
    # Comparer et générer le rapport
    compare_capsules(results, args.output)

if __name__ == "__main__":
    main()
