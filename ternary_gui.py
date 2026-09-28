"""GUI para criar diagramas ternários interpolados em 2D.

A curva de separação é ajustada aos pontos 2F: abaixo dela a fase é 2F e
acima é 1F. Requer Python 3.9+, NumPy, SciPy e Matplotlib. Execute com
``python ternary_gui.py``.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch
from matplotlib.tri import Triangulation
from scipy.interpolate import PchipInterpolator

APP_VERSION = "1.0.0"
APP_DATE = "28/09/2026"  # Data fixa solicitada no prompt.
SQRT3 = np.sqrt(3.0)  # Altura de um triângulo equilátero de lado 1.
TEXT = {
    "pt": {
        "title": "Diagramas Ternários", "components": "Componentes", "names": "Nomes (A, B, C):",
        "data": "Dados de entrada", "hint": "Uma linha por ponto: fração A, fração B e fase (1F ou 2F). A curva de separação é ajustada aos pontos 2F: abaixo dela é 2F e acima é 1F.",
        "examples": "Exemplo:\n0.20, 0.30, 1F\n0.60, 0.10, 2F", "points": "Número de pontos:",
        "appearance": "Aparência", "color1": "Cor 1F", "color2": "Cor 2F", "line": "Estilo da linha:",
        "plot2d": "Gerar gráfico", "save": "Salvar gráfico", "about": "About",
        "canvas": "Visualização do gráfico", "invalid": "Dados inválidos", "need": "Informe pelo menos 3 pontos válidos para interpolar.",
        "line_error": "Linha {n}: use frações A e B entre 0 e 1 e fase 1F ou 2F.",
        "sum_error": "Linha {n}: A + B não pode exceder 1. A fração C é calculada como 1 − A − B.",
        "count_error": "O número de pontos informado ({given}) difere das linhas preenchidas ({actual}).",
        "save_first": "Gere um gráfico antes de salvar.", "saved": "Gráfico salvo com sucesso.",
        "about_text": f"Diagramas Ternários\nVersão {APP_VERSION}\nAutor: Dr. Arlan da Silva Gonçalves\nData: {APP_DATE}\n\nInstituto Federal de Educação, Ciência e Tecnologia do Espírito Santo – Campus Vila Velha / Campus Vitória\nUniversidade Federal do Espírito Santo – PPGQ / UFES",
        "color": "Cor", "file": "Salvar gráfico",
        "phase1": "1-fase", "phase2": "2-fase", "legend1": "Região 1F", "legend2": "Região 2F",
        "need_both": "Inclua pontos das duas regiões: 1F e 2F.",
        "need_2f": "Informe pelo menos 2 pontos 2F com frações A diferentes para ajustar a curva de separação.",
        "fit_error": "Não foi possível ajustar a curva com esses pontos: {error}",
    },
    "en": {
        "title": "Ternary Diagrams", "components": "Components", "names": "Names (A, B, C):",
        "data": "Input data", "hint": "One point per line: fraction A, fraction B, and phase (1F or 2F). The phase boundary is fitted to the 2F points: below it the phase is 2F and above it 1F.",
        "examples": "Example:\n0.20, 0.30, 1F\n0.60, 0.10, 2F", "points": "Number of points:",
        "appearance": "Appearance", "color1": "Color 1F", "color2": "Color 2F", "line": "Line style:",
        "plot2d": "Generate plot", "save": "Save plot", "about": "About",
        "canvas": "Plot preview", "invalid": "Invalid data", "need": "Enter at least 3 valid points to interpolate.",
        "line_error": "Line {n}: use A and B fractions from 0 to 1 and phase 1F or 2F.",
        "sum_error": "Line {n}: A + B cannot exceed 1. Fraction C is calculated as 1 − A − B.",
        "count_error": "The entered point count ({given}) differs from the filled rows ({actual}).",
        "save_first": "Generate a plot before saving.", "saved": "Plot saved successfully.",
        "about_text": f"Ternary Diagrams\nVersion {APP_VERSION}\nAuthor: Dr. Arlan da Silva Gonçalves\nDate: {APP_DATE}\n\nFederal Institute of Education, Science and Technology of Espírito Santo – Vila Velha / Vitória Campuses\nFederal University of Espírito Santo – PPGQ / UFES",
        "color": "Color", "file": "Save plot",
        "phase1": "1-phase", "phase2": "2-phase", "legend1": "1-phase region", "legend2": "2-phase region",
        "need_both": "Include points from both regions: 1F and 2F.",
        "need_2f": "Enter at least 2 points 2F with different A fractions to fit the phase boundary.",
        "fit_error": "Could not fit the curve with these points: {error}",
    },
}


class TernaryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.language = tk.StringVar(value="pt")
        self.color_1f = "#d3d3d3"
        self.color_2f = "#c0c0c0"
        self.line_style = tk.StringVar(value="-")
        self.figure: Figure | None = None
        self.canvas: FigureCanvasTkAgg | None = None
        self._build()

    def t(self, key: str) -> str:
        return TEXT[self.language.get()][key]

    def _build(self) -> None:
        self.root.title(self.t("title"))
        self.root.minsize(900, 620)
        self.root.geometry("1180x760")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.panel = ttk.Frame(self.root, padding=12)
        self.panel.grid(row=0, column=0, sticky="nsew")
        self.panel.columnconfigure(0, weight=1)
        self.view = ttk.LabelFrame(self.root, text=self.t("canvas"), padding=8)
        self.view.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)
        self.view.columnconfigure(0, weight=1)
        self.view.rowconfigure(0, weight=1)

        ttk.Label(self.panel, text="Language / Idioma").grid(row=0, column=0, sticky="w")
        language = ttk.Combobox(self.panel, textvariable=self.language, values=("pt", "en"), state="readonly", width=8)
        language.grid(row=1, column=0, sticky="w", pady=(2, 10))
        language.bind("<<ComboboxSelected>>", self._language_changed)

        self.components_box = ttk.LabelFrame(self.panel, text=self.t("components"), padding=8)
        self.components_box.grid(row=2, column=0, sticky="ew", pady=4)
        self.name_vars = [tk.StringVar(value=s) for s in ("A", "B", "C")]
        self.names_entry = ttk.Entry(self.components_box, textvariable=tk.StringVar(value="A, B, C"), width=27)
        self.names_entry.grid(row=0, column=0, sticky="ew")
        self.components_box.columnconfigure(0, weight=1)
        self.data_box = ttk.LabelFrame(self.panel, text=self.t("data"), padding=8)
        self.data_box.grid(row=3, column=0, sticky="nsew", pady=4)
        self.panel.rowconfigure(3, weight=1)
        self.hint_label = ttk.Label(self.data_box, text=self.t("hint"), wraplength=320, justify="left")
        self.hint_label.grid(row=0, column=0, sticky="w")
        self.data_text = tk.Text(self.data_box, width=38, height=15, wrap="none", undo=True)
        self.data_text.grid(row=1, column=0, sticky="nsew", pady=6)
        self.data_text.insert("1.0", "0.70, 0.15, 1F\n0.62, 0.30, 1F\n0.55, 0.20, 1F\n0.05, 0.10, 2F\n0.10, 0.45, 2F\n0.08, 0.80, 2F\n0.20, 0.25, 2F\n0.18, 0.65, 2F")
        self.data_box.rowconfigure(1, weight=1)
        self.data_box.columnconfigure(0, weight=1)
        self.count_row = ttk.Frame(self.panel)
        self.count_row.grid(row=4, column=0, sticky="ew", pady=4)
        self.points_label = ttk.Label(self.count_row, text=self.t("points"))
        self.points_label.grid(row=0, column=0, sticky="w")
        self.count_var = tk.StringVar(value="8")
        ttk.Entry(self.count_row, textvariable=self.count_var, width=8).grid(row=0, column=1, padx=6)
        self.appearance_box = ttk.LabelFrame(self.panel, text=self.t("appearance"), padding=8)
        self.appearance_box.grid(row=5, column=0, sticky="ew", pady=4)
        self.color1_button = ttk.Button(self.appearance_box, text=self.t("color1"), command=lambda: self._choose_color(1))
        self.color1_button.grid(row=0, column=0, sticky="ew", padx=2)
        self.color2_button = ttk.Button(self.appearance_box, text=self.t("color2"), command=lambda: self._choose_color(2))
        self.color2_button.grid(row=0, column=1, sticky="ew", padx=2)
        self.line_label = ttk.Label(self.appearance_box, text=self.t("line"))
        self.line_label.grid(row=1, column=0, sticky="w", pady=(7, 0))
        self.line_combo = ttk.Combobox(self.appearance_box, textvariable=self.line_style, values=("-", "--", ":", "-.", "None"), state="readonly", width=8)
        self.line_combo.grid(row=1, column=1, sticky="ew", pady=(7, 0))
        self.buttons = ttk.Frame(self.panel)
        self.buttons.grid(row=6, column=0, sticky="ew", pady=6)
        self.plot_button = ttk.Button(self.buttons, text=self.t("plot2d"), command=self.plot)
        self.plot_button.grid(row=0, column=0, sticky="ew", pady=2)
        self.save_button = ttk.Button(self.buttons, text=self.t("save"), command=self.save)
        self.save_button.grid(row=1, column=0, sticky="ew", pady=2)
        self.about_button = ttk.Button(self.buttons, text=self.t("about"), command=lambda: messagebox.showinfo(self.t("about"), TEXT[self.language.get()]["about_text"]))
        self.about_button.grid(row=2, column=0, sticky="ew", pady=2)
        self.buttons.columnconfigure(0, weight=1)

    def _language_changed(self, _event=None) -> None:
        self.root.title(self.t("title"))
        self.components_box.configure(text=self.t("components"))
        self.data_box.configure(text=self.t("data"))
        self.view.configure(text=self.t("canvas"))
        self.hint_label.configure(text=self.t("hint"))
        self.points_label.configure(text=self.t("points"))
        self.appearance_box.configure(text=self.t("appearance"))
        self.color1_button.configure(text=self.t("color1"))
        self.color2_button.configure(text=self.t("color2"))
        self.line_label.configure(text=self.t("line"))
        self.plot_button.configure(text=self.t("plot2d"))
        self.save_button.configure(text=self.t("save"))
        self.about_button.configure(text=self.t("about"))

    def _choose_color(self, phase: int) -> None:
        color = colorchooser.askcolor(title=self.t("color"))[1]
        if color:
            if phase == 1:
                self.color_1f = color
            else:
                self.color_2f = color

    def _read_data(self):
        # Converte as linhas editadas em coordenadas cartesianas do triângulo.
        rows = [line.strip() for line in self.data_text.get("1.0", "end").splitlines() if line.strip() and not line.strip().startswith("#")]
        try:
            expected = int(self.count_var.get())
            if expected != len(rows):
                raise ValueError(self.t("count_error").format(given=expected, actual=len(rows)))
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        xa, xb, phases = [], [], []
        for n, row in enumerate(rows, 1):
            parts = row.replace(";", " ").replace(",", " ").split()
            if len(parts) != 3:
                raise ValueError(self.t("line_error").format(n=n))
            try:
                a, b = float(parts[0]), float(parts[1])
            except ValueError as exc:
                raise ValueError(self.t("line_error").format(n=n)) from exc
            phase = parts[2].upper()
            if not (0 <= a <= 1 and 0 <= b <= 1) or phase not in ("1F", "2F"):
                raise ValueError(self.t("line_error").format(n=n))
            if a + b > 1 + 1e-10:
                raise ValueError(self.t("sum_error").format(n=n))
            xa.append(a)
            xb.append(b)
            phases.append(1 if phase == "1F" else 2)
        if len(rows) < 3:
            raise ValueError(self.t("need"))
        if len(set(zip(xa, xb))) < 3:
            raise ValueError(self.t("need"))
        names = [part.strip() for part in self.names_entry.get().split(",")]
        if len(names) != 3 or not all(names):
            raise ValueError("Informe exatamente três nomes de componentes separados por vírgulas." if self.language.get() == "pt" else "Enter exactly three component names separated by commas.")
        return np.asarray(xa), np.asarray(xb), np.asarray(phases), names

    @staticmethod
    def _to_cartesian(xa, xb):
        # Projeção baricêntrica: A no vértice superior, B à direita e C à esquerda.
        return np.asarray(xb) + 0.5 * np.asarray(xa), (SQRT3 / 2.0) * np.asarray(xa)

    def _binodal_curve(self, xa, xb, phases):
        # Curva de separação ajustada somente aos pontos 2F. Para cada abscissa
        # vale o ponto 2F mais alto, de modo que nenhum ponto 2F fique acima da
        # curva; o PCHIP liga esses pontos sem ondulação entre eles.
        selected = phases == 2
        abscissa, altura = self._to_cartesian(np.asarray(xa)[selected], np.asarray(xb)[selected])
        topmost: dict[float, float] = {}
        for x, y in zip(abscissa, altura):
            topmost[float(x)] = max(topmost.get(float(x), -np.inf), float(y))
        curve_x = np.array(sorted(topmost))
        curve_y = np.array([topmost[x] for x in curve_x])
        if curve_x.size < 2:
            raise ValueError(self.t("need_2f"))
        spline = PchipInterpolator(curve_x, curve_y)
        start, end = float(curve_x[0]), float(curve_x[-1])
        slope = spline.derivative()
        left_slope, right_slope = float(slope(start)), float(slope(end))

        def curve(x):
            # Dentro do intervalo dos pontos usa a spline; fora, prolonga a
            # tangente da extremidade até as bordas do triângulo.
            x = np.asarray(x, dtype=float)
            y = np.empty(x.shape, dtype=float)
            left, middle, right = x < start, (x >= start) & (x <= end), x > end
            y[middle] = spline(x[middle])
            y[left] = curve_y[0] + left_slope * (x[left] - start)
            y[right] = curve_y[-1] + right_slope * (x[right] - end)
            return y

        return curve

    def _phase_field(self, xa, xb, phases, resolution: int = 220):
        # Malha barycêntrica: cada ponto da grade tem xa + xb + xc = 1, então o
        # diagrama fica exatamente limitado pelo triângulo, sem máscara retangular.
        curve = self._binodal_curve(xa, xb, phases)
        steps = np.arange(resolution + 1)
        ia, ib = np.meshgrid(steps, steps, indexing="ij")
        keep = (ia + ib) <= resolution
        ga, gb = ia[keep] / resolution, ib[keep] / resolution
        gx, gy = self._to_cartesian(ga, gb)
        # Abaixo da curva ajustada é 2F (campo positivo); acima é 1F.
        return gx, gy, np.where(gy <= curve(gx), 1.0, -1.0)

    def _draw_frame_2d(self, ax) -> None:
        corners = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, SQRT3 / 2.0], [0.0, 0.0]])
        style = self.line_style.get()
        ax.plot(corners[:, 0], corners[:, 1], color="black", linewidth=1.5,
                linestyle="-" if style == "None" else style, zorder=5)

    def _draw_grid_2d(self, ax) -> None:
        # Grade tracejada "papel isométrico": três famílias de paralelas aos
        # lados, uma para cada fração, unindo as bordas do triângulo.
        height = SQRT3 / 2.0
        for value in np.arange(0.1, 1.0, 0.1):
            families = (
                ((0.5 * value, height * value), (1.0 - 0.5 * value, height * value)),  # xa
                ((value, 0.0), (0.5 + 0.5 * value, height * (1.0 - value))),            # xb
                ((0.5 * (1.0 - value), height * (1.0 - value)), (1.0 - value, 0.0)),    # xc
            )
            for (x0, y0), (x1, y1) in families:
                ax.plot((x0, x1), (y0, y1), color="black", linewidth=0.6,
                        linestyle="--", alpha=0.5, zorder=3)

    def _draw_axis_numbers(self, ax) -> None:
        # Base: fração de B cresce para a direita. Borda direita: fração de A de
        # baixo para cima. Borda esquerda: fração de C de cima para baixo.
        for value in np.arange(0.1, 1.0, 0.1):
            label = f"{int(round(value * 100))}"
            ax.text(value, -0.075, label, ha="center", va="center", fontsize=9, color="black")
            ax.text(1.0 - 0.5 * value + 0.043, (SQRT3 / 2.0) * value + 0.025, label,
                    ha="center", va="center", fontsize=9, color="black")
            ax.text(0.5 - 0.5 * value - 0.043, (SQRT3 / 2.0) * (1.0 - value) + 0.025, label,
                    ha="center", va="center", fontsize=9, color="black")

    def _draw_component_names(self, ax, names) -> None:
        ax.text(0.5, SQRT3 / 2.0 + 0.035, names[0], ha="center", va="bottom", fontsize=11)
        ax.text(0.0, -0.03, names[2], ha="right", va="center", fontsize=11)
        ax.text(1.0, -0.03, names[1], ha="left", va="center", fontsize=11)

    def _readable_color(self, color: str) -> str:
        red, green, blue = to_rgb(color)
        return "black" if 0.299 * red + 0.587 * green + 0.114 * blue > 0.55 else "white"

    def _draw_phase_names(self, ax, gx, gy, field) -> None:
        # Rótulos das fases dentro das regiões, no centroide de cada domo.
        for phase, key, color in ((1, "phase1", self.color_1f), (2, "phase2", self.color_2f)):
            selected = (field < 0) if phase == 1 else (field > 0)
            if not selected.any():
                continue
            ax.text(gx[selected].mean(), gy[selected].mean(), self.t(key), ha="center", va="center",
                    fontsize=11, color=self._readable_color(color), zorder=6)

    def _draw_legend_2d(self, ax) -> None:
        handles = [
            Patch(facecolor=self.color_1f, edgecolor="none", label=self.t("legend1")),
            Patch(facecolor=self.color_2f, edgecolor="none", label=self.t("legend2")),
        ]
        ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(-0.40, 1.02),
                  bbox_transform=ax.transData, frameon=False, fontsize=10,
                  handlelength=1.8, handleheight=0.8, borderpad=0.0, labelspacing=0.7)

    def _figure_2d(self, gx, gy, field, dx, dy, phases, names) -> Figure:
        fig = Figure(figsize=(7.6, 6.0), dpi=100, constrained_layout=True)
        ax = fig.add_subplot(111)
        triang = Triangulation(gx, gy)
        # Níveis além de ±1 para que os valores recortados continuem preenchidos.
        ax.tricontourf(triang, field, levels=[-1.5, 0.0, 1.5], colors=[self.color_1f, self.color_2f])
        style = self.line_style.get()
        ax.tricontour(triang, field, levels=[0.0], colors=["black"], linewidths=1.5,
                      linestyles="-" if style == "None" else style, zorder=4)
        self._draw_grid_2d(ax)
        self._draw_frame_2d(ax)
        for phase, color in ((1, self.color_1f), (2, self.color_2f)):
            selected = phases == phase
            ax.scatter(dx[selected], dy[selected], s=24, color=color, edgecolor="black",
                       linewidth=0.7, zorder=6)
        self._draw_axis_numbers(ax)
        self._draw_component_names(ax, names)
        self._draw_phase_names(ax, gx, gy, field)
        self._draw_legend_2d(ax)
        left, right, bottom, top = -0.44, 1.16, -0.14, 1.06
        ax.set_xlim(left, right)
        ax.set_ylim(bottom, top)
        ax.set_aspect("equal")
        ax.axis("off")
        # O título fica sobre o triângulo, e não sobre a área ocupada pela legenda.
        ax.set_title(" - ".join(names), fontsize=11, pad=12, x=(0.5 - left) / (right - left))
        return fig

    def plot(self) -> None:
        try:
            xa, xb, phases, names = self._read_data()
        except ValueError as exc:
            messagebox.showerror(self.t("invalid"), str(exc))
            return
        if len(np.unique(phases)) < 2:
            messagebox.showerror(self.t("invalid"), self.t("need_both"))
            return
        try:
            gx, gy, field = self._phase_field(xa, xb, phases)
        except (ValueError, np.linalg.LinAlgError) as exc:
            messagebox.showerror(self.t("invalid"), self.t("fit_error").format(error=exc))
            return
        dx, dy = self._to_cartesian(xa, xb)
        self.figure = self._figure_2d(gx, gy, field, dx, dy, phases, names)
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.view)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.view, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0, sticky="ew")

    def save(self) -> None:
        if self.figure is None:
            messagebox.showinfo(self.t("save"), self.t("save_first"))
            return
        path = filedialog.asksaveasfilename(title=self.t("file"), defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("SVG", "*.svg"), ("PostScript", "*.ps")])
        if path:
            try:
                self.figure.savefig(path, dpi=300, bbox_inches="tight")
            except (OSError, ValueError) as exc:
                messagebox.showerror(self.t("invalid"), str(exc))
            else:
                messagebox.showinfo(self.t("save"), self.t("saved"))


def main() -> None:
    root = tk.Tk()
    TernaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
