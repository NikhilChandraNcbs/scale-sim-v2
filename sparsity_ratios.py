def generate_ripple_effect(M, step_size=10):
    """
    Generate ripple effect for N:M sparsity ratios such that all ratios are active.

    Args:
        M (int): The "M" value in N:M sparsity ratios.
        step_size (int): Increment step for percentages.

    Returns:
        list: A list of dictionaries containing percentages for each ratio.
    """
    num_ratios = M // 2  # Number of valid N:M ratios (N = 1 to M/2)
    steps = []
    
    # Initialize percentages: 100% to first ratio
    percentages = [0] * num_ratios
    percentages[0] = 100

    while percentages[-1] < 100:  # While last ratio hasn't reached 100%
        steps.append(percentages[:])  # Store current state

        # Reduce from leftmost active ratio and distribute to others
        for i in range(num_ratios):
            if percentages[i] > 0:
                percentages[i] -= step_size  # Reduce current ratio
                if i + 1 < num_ratios:
                    percentages[i + 1] += step_size  # Increase next ratio
                break

    # Final step: Ensure last ratio reaches 100%
    percentages = [0] * (num_ratios - 1) + [100]
    steps.append(percentages)

    return steps

# Example usage
M = 8  # Array height
ripple_steps = generate_ripple_effect(M)
print(ripple_steps)

# Print the generated table
print(f"{'Step':<5} {' | '.join([f'{n+1}:{M}' for n in range(M // 2)])}")
for step, values in enumerate(ripple_steps):
    print(f"{step:<5} {' | '.join([str(v).rjust(3) for v in values])}")
