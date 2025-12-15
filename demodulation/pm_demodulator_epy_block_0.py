import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="phase_unwrap",
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        self.prev = 0.0
        self.offset = 0.0

    def work(self, input_items, output_items):
        x = input_items[0]
        y = output_items[0]

        for i, p in enumerate(x):
            dp = p - self.prev
            if dp > np.pi:
                self.offset -= 2*np.pi
            elif dp < -np.pi:
                self.offset += 2*np.pi
            y[i] = p + self.offset
            self.prev = p

        return len(y)
