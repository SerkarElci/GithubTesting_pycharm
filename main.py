import math
import tkinter as tk
from tkinter import ttk


class PendulumApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Pendulum Simulation")
        self.root.geometry("840x680")

        # Simulation values
        self.gravity = 9.81
        self.time_step = 0.02
        self.length_m = 1.5
        self.mass_kg = 2.0
        self.angle = math.radians(35)
        self.angular_velocity = 0.0
        self.simulation_running = True

        # Drawing values
        self.canvas_width = 800
        self.canvas_height = 520
        self.pivot_x = self.canvas_width / 2
        self.pivot_y = 80
        self.scale_px_per_m = 170

        self._build_ui()
        self._draw_scene()
        self._animate()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        controls = ttk.LabelFrame(container, text="Pendulum Controls", padding=10)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Line length (m):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.length_var = tk.StringVar(value=f"{self.length_m:.2f}")
        ttk.Entry(controls, textvariable=self.length_var, width=12).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )

        ttk.Label(controls, text="Bob weight / mass (kg):").grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=5
        )
        self.mass_var = tk.StringVar(value=f"{self.mass_kg:.2f}")
        ttk.Entry(controls, textvariable=self.mass_var, width=12).grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=5
        )

        ttk.Button(controls, text="Apply", command=self.apply_settings).grid(
            row=0, column=4, padx=8, pady=5
        )

        self.pause_button = ttk.Button(controls, text="Pause", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=5, padx=8, pady=5)

        self.message_var = tk.StringVar(value="")
        ttk.Label(controls, textvariable=self.message_var, foreground="#8B0000").grid(
            row=1, column=0, columnspan=6, sticky=tk.W, padx=5, pady=(5, 0)
        )

        self.canvas = tk.Canvas(
            container,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            highlightthickness=1,
            highlightbackground="#888888",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

    def apply_settings(self) -> None:
        try:
            length = float(self.length_var.get())
            mass = float(self.mass_var.get())
            if length <= 0 or mass <= 0:
                raise ValueError
        except ValueError:
            self.message_var.set("Please enter positive numbers for line length and bob weight.")
            return

        self.length_m = length
        self.mass_kg = mass
        self.angle = math.radians(35)
        self.angular_velocity = 0.0
        self.message_var.set("")
        self._draw_scene()

    def toggle_pause(self) -> None:
        self.simulation_running = not self.simulation_running
        self.pause_button.config(text="Pause" if self.simulation_running else "Resume")

    def _animate(self) -> None:
        if self.simulation_running:
            angular_acceleration = -(self.gravity / self.length_m) * math.sin(self.angle)
            self.angular_velocity += angular_acceleration * self.time_step
            self.angular_velocity *= 0.999  # gentle damping
            self.angle += self.angular_velocity * self.time_step
            self._draw_scene()

        self.root.after(int(self.time_step * 1000), self._animate)

    def _draw_scene(self) -> None:
        self.canvas.delete("all")

        line_length_px = self.length_m * self.scale_px_per_m
        max_reach = self.canvas_height - self.pivot_y - 30
        line_length_px = min(line_length_px, max_reach)

        bob_x = self.pivot_x + line_length_px * math.sin(self.angle)
        bob_y = self.pivot_y + line_length_px * math.cos(self.angle)

        bob_radius = max(8, min(48, 12 + self.mass_kg * 3))

        self.canvas.create_line(
            self.pivot_x,
            self.pivot_y,
            bob_x,
            bob_y,
            width=3,
            fill="#333333",
        )

        self.canvas.create_oval(
            bob_x - bob_radius,
            bob_y - bob_radius,
            bob_x + bob_radius,
            bob_y + bob_radius,
            fill="#2E86DE",
            outline="#1B4F72",
            width=2,
        )

        self.canvas.create_oval(
            self.pivot_x - 6,
            self.pivot_y - 6,
            self.pivot_x + 6,
            self.pivot_y + 6,
            fill="#444444",
            outline="",
        )

        self.canvas.create_text(
            10,
            10,
            anchor=tk.NW,
            text=f"Length: {self.length_m:.2f} m    Bob mass: {self.mass_kg:.2f} kg",
            fill="#222222",
            font=("Arial", 11),
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = PendulumApp(root)
    root.mainloop()
