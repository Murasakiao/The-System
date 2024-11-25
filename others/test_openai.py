import matplotlib.pyplot as plt
import numpy as np

# Generate a smooth progression using an exponential curve
levels_smooth = list(range(1, 26))
base_points = 150  # Starting points multiplier for level progression
growth_rate = 1.15  # Growth rate for progression

# Calculate points using an exponential formula
points_smooth = [int(base_points * (growth_rate**(level - 1))) for level in levels_smooth]
list = points_smooth

# Plotting the smoothed level progression
plt.figure(figsize=(12, 6))
plt.plot(levels_smooth, points_smooth, marker='o', linestyle='-', color='green', label='Smooth Points Required')

# Adding labels and title
plt.title("Smoothed Level Progression System (Up to Level 25)", fontsize=16)
plt.xlabel("Level", fontsize=12)
plt.ylabel("Cumulative Points Required", fontsize=12)

# Adding grid and annotations for readability
plt.grid(True, linestyle='--', alpha=0.7)
for level, point in zip(levels_smooth, points_smooth):
    if level % 5 == 0:  # Annotate every 5th level for clarity
        plt.text(level, point + 500, f"{point}", ha='center', fontsize=8, color='black')

# Legend and display
plt.legend()
plt.tight_layout()
plt.show()
print(list)

# Displaying the generated points
points_smooth
