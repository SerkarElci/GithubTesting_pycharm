import math
import tkinter as tk
from tkinter import ttk


class PendulumApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Spring Pendulum Simulation")
        self.root.geometry("900x720")

        # Simulation values
        self.gravity = 9.81
        self.time_step = 0.01
        self.length_m = 1.8  # rest length of cable
        self.mass_kg = 2.0
        self.spring_k = 22.0  # N/m (lower = springier)

        # State (polar coordinates around the pivot)
        self.angle = math.radians(14)
        self.angular_velocity = 0.0
        self.radial_length = self.length_m * 0.5  # drop from mid range of cable length
        self.radial_velocity = 0.0
        self.simulation_running = True

        # Damping (helps keep motion stable)
        self.radial_damping = 0.06
        self.angular_damping = 0.01

        # Drawing values
        self.canvas_width = 860
        self.canvas_height = 560
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

        ttk.Label(controls, text="Cable length (m):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
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

        ttk.Label(controls, text="Cable springiness (N/m):").grid(
            row=0, column=4, sticky=tk.W, padx=5, pady=5
        )
        self.spring_var = tk.StringVar(value=f"{self.spring_k:.2f}")
        ttk.Entry(controls, textvariable=self.spring_var, width=12).grid(
            row=0, column=5, sticky=tk.W, padx=5, pady=5
        )

        ttk.Button(controls, text="Apply", command=self.apply_settings).grid(
            row=0, column=6, padx=8, pady=5
        )

        self.pause_button = ttk.Button(controls, text="Pause", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=7, padx=8, pady=5)

        self.message_var = tk.StringVar(value="")
        ttk.Label(controls, textvariable=self.message_var, foreground="#8B0000").grid(
            row=1, column=0, columnspan=8, sticky=tk.W, padx=5, pady=(5, 0)
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
            spring = float(self.spring_var.get())
            if length <= 0 or mass <= 0 or spring <= 0:
                raise ValueError
        except ValueError:
            self.message_var.set("Enter positive numbers for cable length, bob weight, and springiness.")
            return

        self.length_m = length
        self.mass_kg = mass
        self.spring_k = spring

        # Restart state: bob starts from mid-cable so it drops and stretches the spring cable.
        self.angle = math.radians(14)
        self.angular_velocity = 0.0
        self.radial_length = self.length_m * 0.5
        self.radial_velocity = 0.0

        self.message_var.set("")
        self._draw_scene()

    def toggle_pause(self) -> None:
        self.simulation_running = not self.simulation_running
        self.pause_button.config(text="Pause" if self.simulation_running else "Resume")

    def _animate(self) -> None:
        if self.simulation_running:
            # Elastic pendulum dynamics in polar coordinates.
            # angle=0 means straight down.
            radial_accel = (
                self.radial_length * (self.angular_velocity ** 2)
                - self.gravity * math.cos(self.angle)
                - (self.spring_k / self.mass_kg) * (self.radial_length - self.length_m)
                - self.radial_damping * self.radial_velocity
            )

            safe_radius = max(self.radial_length, 0.2)
            angular_accel = (
                (-self.gravity * math.sin(self.angle) - 2 * self.radial_velocity * self.angular_velocity)
                / safe_radius
                - self.angular_damping * self.angular_velocity
            )

            self.radial_velocity += radial_accel * self.time_step
            self.angular_velocity += angular_accel * self.time_step

            self.radial_length += self.radial_velocity * self.time_step
            self.angle += self.angular_velocity * self.time_step

            # Keep cable from collapsing too close to the pivot.
            self.radial_length = max(0.18, self.radial_length)

            self._draw_scene()

        self.root.after(int(self.time_step * 1000), self._animate)

    def _draw_spring_cable(self, bob_x: float, bob_y: float) -> None:
        dx = bob_x - self.pivot_x
        dy = bob_y - self.pivot_y
        cable_px = math.hypot(dx, dy)
        if cable_px < 8:
            return

        ux = dx / cable_px
        uy = dy / cable_px
        px = -uy
        py = ux

        coils = max(9, int(cable_px / 24))
        amplitude = min(14, 5 + max(0, (self.length_m - self.radial_length)) * 7)

        points = [self.pivot_x, self.pivot_y]
        for i in range(1, coils):
            t = i / coils
            base_x = self.pivot_x + dx * t
            base_y = self.pivot_y + dy * t
            direction = 1 if i % 2 == 0 else -1
            points.extend([base_x + px * amplitude * direction, base_y + py * amplitude * direction])
        points.extend([bob_x, bob_y])

        self.canvas.create_line(*points, fill="#333333", width=2.4, smooth=True)

    def _draw_scene(self) -> None:
        self.canvas.delete("all")

        line_length_px = self.radial_length * self.scale_px_per_m
        max_reach = self.canvas_height - self.pivot_y - 30
        line_length_px = min(line_length_px, max_reach)

        bob_x = self.pivot_x + line_length_px * math.sin(self.angle)
        bob_y = self.pivot_y + line_length_px * math.cos(self.angle)

        bob_radius = max(8, min(48, 12 + self.mass_kg * 3))

        self._draw_spring_cable(bob_x, bob_y)

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
            12,
            12,
            anchor=tk.NW,
            text=(
                f"Cable length: {self.length_m:.2f} m   "
                f"Current stretch length: {self.radial_length:.2f} m   "
                f"Bob mass: {self.mass_kg:.2f} kg   "
                f"Springiness: {self.spring_k:.2f} N/m"
            ),
            fill="#222222",
            font=("Arial", 10),
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = PendulumApp(root)
    root.mainloop()
