import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    """
    Phase Unwrapping Block

    This block performs phase unwrapping on a stream of phase samples
    (in radians) produced by a Complex-to-Arg block. It removes the
    discontinuities caused by phase wrapping at ±π, producing a
    continuous phase signal suitable for phase demodulation.
    """

    def __init__(self):
        # Initialize the GNU Radio synchronous block
        # One float input (wrapped phase)
        # One float output (unwrapped phase)
        gr.sync_block.__init__(
            self,
            name="phase_unwrap",
            in_sig=[np.float32],
            out_sig=[np.float32]
        )

        # Store the previous phase sample
        self.prev = 0.0

        # Accumulated phase offset used to correct wrapping
        self.offset = 0.0

    def work(self, input_items, output_items):
        """
        Perform phase unwrapping on the input phase samples.

        input_items[0]  : wrapped phase values in range [-π, π]
        output_items[0] : continuous (unwrapped) phase values
        """

        x = input_items[0]   # Input phase samples
        y = output_items[0]  # Output unwrapped phase samples

        for i, p in enumerate(x):
            # Calculate phase difference between consecutive samples
            dp = p - self.prev

            # Detect positive phase wrap (jump from -π to +π)
            if dp > np.pi:
                self.offset -= 2 * np.pi

            # Detect negative phase wrap (jump from +π to -π)
            elif dp < -np.pi:
                self.offset += 2 * np.pi

            # Apply accumulated offset to unwrap the phase
            y[i] = p + self.offset

            # Update previous phase value
            self.prev = p

        # Return the number of output samples produced
        return len(y)

