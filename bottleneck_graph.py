import matplotlib.pyplot as plt

# Data
program_sizes = [2, 3, 4, 7, 8, 2, 3, 3, 5, 8]
programs_generated = [9, 14, 119, 11574, 85475, 12, 20, 47, 326, 661855]
test_cases = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(program_sizes, programs_generated, color='blue', s=100, edgecolor='k', label="Test Cases (denoted by number)")

# Add text labels with offset to avoid overlap
for i, tc in enumerate(test_cases):
    plt.text(
        program_sizes[i] + 0.1,  # Offset the label slightly to the right
        programs_generated[i] * 1.0,  # Offset the label slightly upward
        str(tc),
        fontsize=10,
        ha='left',  # Align label to the left of the point
        va='bottom'  # Align label above the point
    )

plt.xscale("linear")
plt.yscale("log")  # Log scale for clarity
plt.xlabel("Synthesized Program Size")
plt.ylabel("Number of Programs Generated (Log Scale)")
plt.title("Synthesized Program Size vs. Total Programs Generated")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend()
plt.show()
