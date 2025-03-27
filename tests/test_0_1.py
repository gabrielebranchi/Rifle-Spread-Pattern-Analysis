import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import math
import threading
import random

# Imposta il metodo di resampling in base alla versione di Pillow
try:
    resample_method = Image.Resampling.LANCZOS
except AttributeError:
    resample_method = Image.LANCZOS

# --- Funzioni di supporto per il calcolo del cerchio minimo ---
def welzl(points, boundary_points=None):
    if boundary_points is None:
        boundary_points = []
    
    if len(points) == 0 or len(boundary_points) == 3:
        if len(boundary_points) == 0:
            return (0, 0, 0)  # Non esiste cerchio
        elif len(boundary_points) == 1:
            return (boundary_points[0][0], boundary_points[0][1], 0)
        elif len(boundary_points) == 2:
            return circle_from_two_points(boundary_points[0], boundary_points[1])
        else:
            return circle_from_three_points(boundary_points[0], boundary_points[1], boundary_points[2])

    # Scegli un punto a caso dalla lista
    point = points.pop(random.randint(0, len(points) - 1))
    circle = welzl(points, boundary_points)
    
    # Se il punto è all'interno del cerchio corrente, ritorna il cerchio
    if math.hypot(circle[0] - point[0], circle[1] - point[1]) <= circle[2]:
        points.append(point)  # Rimettere il punto
        return circle
    else:
        # Se il punto non è all'interno, includilo nei punti di confine
        boundary_points.append(point)
        result = welzl(points, boundary_points)
        points.append(point)  # Rimettere il punto
        boundary_points.pop()  # Rimuovi il punto di confine
        return result

def circle_from_two_points(p1, p2):
    cx = (p1[0] + p2[0]) / 2.0
    cy = (p1[1] + p2[1]) / 2.0
    r = math.hypot(p1[0] - p2[0], p1[1] - p2[1]) / 2.0
    return (cx, cy, r)

def circle_from_three_points(p1, p2, p3):
    d = 2 * (p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1]))
    if abs(d) < 1e-6:
        return None
    ux = ((p1[0]**2 + p1[1]**2)*(p2[1]-p3[1]) +
          (p2[0]**2 + p2[1]**2)*(p3[1]-p1[1]) +
          (p3[0]**2 + p3[1]**2)*(p1[1]-p2[1])) / d
    uy = ((p1[0]**2 + p1[1]**2)*(p3[0]-p2[0]) +
          (p2[0]**2 + p2[1]**2)*(p1[0]-p3[0]) +
          (p3[0]**2 + p3[1]**2)*(p2[0]-p1[0])) / d
    r = math.hypot(ux - p1[0], uy - p1[1])
    return (ux, uy, r)

# --- Classe della GUI ---
class ColpiAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisi Colpi su Bersaglio")

        # Frame superiore per pulsanti
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, pady=10)

        self.btn_load = tk.Button(top_frame, text="Seleziona Immagine", command=self.load_image)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        self.btn_process = tk.Button(top_frame, text="Analizza Colpi", command=self.process_image, state=tk.DISABLED)
        self.btn_process.pack(side=tk.LEFT, padx=5)

        self.btn_export = tk.Button(top_frame, text="Export Immagine", command=self.export_image, state=tk.DISABLED)
        self.btn_export.pack(side=tk.LEFT, padx=5)

        # Frame per i parametri modificabili
        params_frame = tk.Frame(root)
        params_frame.pack(side=tk.TOP, pady=10)

        tk.Label(params_frame, text="Threshold:").grid(row=0, column=0, padx=5, sticky='e')
        self.entry_threshold = tk.Entry(params_frame, width=5)
        self.entry_threshold.grid(row=0, column=1, padx=5)
        self.entry_threshold.insert(0, "150")

        tk.Label(params_frame, text="Area Minima:").grid(row=0, column=2, padx=5, sticky='e')
        self.entry_min_area = tk.Entry(params_frame, width=5)
        self.entry_min_area.grid(row=0, column=3, padx=5)
        self.entry_min_area.insert(0, "2")

        tk.Label(params_frame, text="Percentuale (%):").grid(row=0, column=4, padx=5, sticky='e')
        self.entry_percent = tk.Entry(params_frame, width=5)
        self.entry_percent.grid(row=0, column=5, padx=5)
        self.entry_percent.insert(0, "80")

        # Campo per la larghezza dell'immagine in millimetri
        tk.Label(params_frame, text="Larghezza (mm):").grid(row=0, column=6, padx=5, sticky='e')
        self.entry_width_mm = tk.Entry(params_frame, width=5)
        self.entry_width_mm.grid(row=0, column=7, padx=5)
        self.entry_width_mm.insert(0, "200")  # Valore predefinito

        # Casella di controllo per il debug
        self.debug_var = tk.BooleanVar()
        self.debug_checkbox = tk.Checkbutton(params_frame, text="Abilita Debug", variable=self.debug_var)
        self.debug_checkbox.grid(row=0, column=8, padx=5)

        # Barra di avanzamento e label della percentuale
        progress_frame = tk.Frame(root)
        progress_frame.pack(pady=10)

        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=5)

        self.progress_label = tk.Label(progress_frame, text="0%")
        self.progress_label.pack(side=tk.LEFT, padx=5)

        # Canvas per la visualizzazione dell'immagine
        self.canvas = tk.Canvas(root, width=800, height=600, bg="gray")
        self.canvas.pack(pady=10)

        self.image_path = None
        self.original_image = None  # immagine PIL caricata
        self.tk_image = None        # immagine Tkinter da visualizzare
        self.processed_img = None   # immagine PIL elaborata per l'export
        self.best_circle = None     # cerchio minimo trovato

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Immagini", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.btn_process.config(state=tk.NORMAL)
            self.btn_export.config(state=tk.DISABLED)
            self.progress_bar['value'] = 0
            self.progress_label.config(text="0%")

    def display_image(self, image_path):
        img = Image.open(image_path)
        max_size = (800, 600)
        img.thumbnail(max_size, resample_method)
        self.canvas.config(width=img.width, height=img.height)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(img.width // 2, img.height // 2, image=self.tk_image)
        self.original_image = img

    def process_image(self):
        if not self.image_path:
            messagebox.showerror("Errore", "Seleziona prima un'immagine!")
            return
        self.btn_process.config(state=tk.DISABLED)
        self.btn_export.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
        threading.Thread(target=self._process_image_thread, daemon=True).start()

    def _process_image_thread(self):
        try:
            threshold_value = int(self.entry_threshold.get())
            min_area = float(self.entry_min_area.get())
            percent_value = float(self.entry_percent.get()) / 100.0
            width_mm = float(self.entry_width_mm.get())  # Larghezza in millimetri
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Errore", "I parametri devono essere numerici!"))
            return

        image = cv2.imread(self.image_path)
        if image is None:
            self.root.after(0, lambda: messagebox.showerror("Errore", "Impossibile caricare l'immagine!"))
            return

        # Calcola la scala di conversione da pixel a millimetri
        width_pixels = image.shape[1]  # Larghezza in pixel
        scale = width_mm / width_pixels  # Scala in mm/pixel

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shots_centers = []
        for cnt in contours:
            if cv2.contourArea(cnt) > min_area:
                (x, y), _ = cv2.minEnclosingCircle(cnt)
                shots_centers.append((x, y))
        shots_centers = np.array(shots_centers)

        if len(shots_centers) == 0:
            self.root.after(0, lambda: messagebox.showerror("Errore", "Nessun colpo rilevato!"))
            return

        # Calcola il numero di punti da includere
        k = int(percent_value * len(shots_centers))
        if k <= 0:
            self.root.after(0, lambda: messagebox.showerror("Errore", "La percentuale è troppo bassa, nessun colpo selezionato!"))
            return

        # Trova il cerchio minimo che include almeno k punti
        min_radius = float('inf')
        best_circle = None

        for i, point in enumerate(shots_centers):
            # Calcola tutte le distanze dal punto corrente
            distances = []
            for p in shots_centers:
                dist = math.hypot(p[0] - point[0], p[1] - point[1])
                distances.append(dist)
            distances.sort()

            if len(distances) < k:
                continue  # Non abbastanza punti, salta

            # Il raggio è la distanza del k-esimo punto più vicino (indice k-1)
            radius = distances[k-1]

            # Aggiorna il cerchio minimo trovato
            if radius < min_radius:
                min_radius = radius
                best_circle = (point[0], point[1], radius)

            # Aggiorna la barra di avanzamento e la percentuale
            progress = ((i + 1) / len(shots_centers)) * 100
            self.root.after(0, self.update_progress, progress)

        if best_circle is None:
            self.root.after(0, lambda: messagebox.showerror("Errore", "Impossibile trovare un cerchio con la percentuale specificata!"))
            return

        # Salva il cerchio trovato per l'export
        self.best_circle = best_circle

        # Verifica il numero effettivo di punti dentro il cerchio
        cx, cy, r = best_circle
        count = 0
        for (x, y) in shots_centers:
            if math.hypot(x - cx, y - cy) <= r + 1e-6:  # Tolleranza per errori floating-point
                count += 1
        actual_percent = count / len(shots_centers)

        # Calcola i colpi dentro e fuori dal cerchio
        total_shots = len(shots_centers)
        shots_inside = count
        shots_outside = total_shots - shots_inside

        # Calcola la distanza dal centro reale al centro della circonferenza in millimetri
        center_x, center_y = width_pixels // 2, image.shape[0] // 2  # Centro reale (supponiamo che sia al centro dell'immagine)
        distance_pixels = math.hypot(cx - center_x, cy - center_y)  # Distanza in pixel
        distance_mm = distance_pixels * scale  # Distanza in millimetri

        # Disegna i colpi dentro e fuori dal cerchio
        output_image = image.copy()
        for (x, y) in shots_centers:
            if math.hypot(x - cx, y - cy) <= r + 1e-6:  # Colpo dentro il cerchio
                cv2.circle(output_image, (int(x), int(y)), 3, (0, 255, 0), -1)  # Verde
            else:  # Colpo fuori dal cerchio
                cv2.circle(output_image, (int(x), int(y)), 3, (0, 0, 255), -1)  # Rosso
        cv2.circle(output_image, (int(cx), int(cy)), int(r), (255, 0, 0), 2)  # Cerchio
        cv2.circle(output_image, (int(cx), int(cy)), 5, (0, 0, 255), -1)  # Centro

        # Stampa i dettagli dei colpi nella console se il debug è abilitato
        if self.debug_var.get():
            print("Dettagli dei colpi:")
            for i, (x, y) in enumerate(shots_centers):
                status = "dentro" if math.hypot(x - cx, y - cy) <= r + 1e-6 else "fuori"
                print(f"Colpo {i + 1}: ({x:.2f}, {y:.2f}) - {status}")
            print(f"Distanza dal centro reale: {distance_mm:.2f} mm")

        output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
        img_out = Image.fromarray(output_image_rgb)
        max_size = (800, 600)
        img_out.thumbnail(max_size, resample_method)
        self.processed_img = img_out

        self.root.after(0, self.update_progress, 100)
        self.root.after(0, lambda: self._update_canvas(img_out))
        self.root.after(0, lambda: messagebox.showinfo(
            "Successo",
            f"Analisi completata!\n"
            f"Percentuale effettiva: {actual_percent*100:.2f}%\n"
            f"Colpi totali: {total_shots}\n"
            f"Colpi dentro il cerchio: {shots_inside}\n"
            f"Colpi fuori dal cerchio: {shots_outside}\n"
            f"Distanza dal centro reale: {distance_mm:.2f} mm"
        ))
        self.root.after(0, lambda: self.btn_export.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.btn_process.config(state=tk.NORMAL))

    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"{int(value)}%")

    def _update_canvas(self, img_out):
        self.canvas.config(width=img_out.width, height=img_out.height)
        self.tk_image = ImageTk.PhotoImage(img_out)
        self.canvas.create_image(img_out.width // 2, img_out.height // 2, image=self.tk_image)

    def export_image(self):
        if self.image_path is None or self.best_circle is None:
            messagebox.showerror("Errore", "Nessuna immagine elaborata da esportare!")
            return

        # Carica l'immagine originale
        original_image = cv2.imread(self.image_path)
        if original_image is None:
            messagebox.showerror("Errore", "Impossibile caricare l'immagine originale!")
            return

        # Ottieni i centri dei colpi
        shots_centers = self._get_shots_centers(original_image)
        if shots_centers is None:
            return

        # Ottieni il cerchio minimo
        cx, cy, r = self.best_circle

        # Disegna i colpi dentro e fuori dal cerchio sull'immagine originale
        output_image = original_image.copy()
        for (x, y) in shots_centers:
            if math.hypot(x - cx, y - cy) <= r + 1e-6:  # Colpo dentro il cerchio
                cv2.circle(output_image, (int(x), int(y)), 3, (0, 255, 0), -1)  # Verde
            else:  # Colpo fuori dal cerchio
                cv2.circle(output_image, (int(x), int(y)), 3, (0, 0, 255), -1)  # Rosso
        cv2.circle(output_image, (int(cx), int(cy)), int(r), (255, 0, 0), 2)  # Cerchio
        cv2.circle(output_image, (int(cx), int(cy)), 5, (0, 0, 255), -1)  # Centro

        # Converti l'immagine OpenCV in formato PIL per l'export
        output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
        img_out = Image.fromarray(output_image_rgb)

        # Chiedi all'utente dove salvare l'immagine
        export_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("Tutti i file", "*.*")]
        )
        if export_path:
            try:
                img_out.save(export_path)
                messagebox.showinfo("Successo", f"Immagine esportata correttamente in:\n{export_path}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'esportazione: {e}")

    def _get_shots_centers(self, image):
        try:
            threshold_value = int(self.entry_threshold.get())
            min_area = float(self.entry_min_area.get())
        except ValueError:
            messagebox.showerror("Errore", "I parametri devono essere numerici!")
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shots_centers = []
        for cnt in contours:
            if cv2.contourArea(cnt) > min_area:
                (x, y), _ = cv2.minEnclosingCircle(cnt)
                shots_centers.append((x, y))
        return np.array(shots_centers)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColpiAnalyzer(root)
    root.mainloop()
