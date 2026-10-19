from manimlib import *


class RubiksCubeTest(Scene):
    def construct(self):
        square = Square()
        square.set_fill(BLUE, opacity=0.7)

        self.play(ShowCreation(square))
        self.play(Rotate(square, angle=PI / 2))
        self.wait()
