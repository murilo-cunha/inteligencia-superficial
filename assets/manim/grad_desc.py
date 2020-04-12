#!/usr/bin/env python

from manimlib.imports import *
import numpy as np
from typing import Callable, Tuple


# To watch one of these scenes, run the following:
# python -m manim example_scenes.py SquareToCircle -pl
#
# Use the flat -l for a faster rendering at a lower
# quality.
# Use -s to skip to the end and just save the final frame
# Use the -p to have the animation (or image, if -s was
# used) pop up once done.
# Use -n <number> to skip ahead to the n'th animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1080
# for a 1920x1080 video)

# Resources:
# https://github.com/Elteoremadebeethoven/AnimationsWithManim
# https://www.reddit.com/user/TheoremofBeethoven/
# https://stackoverflow.com/questions/tagged/manim
# https://www.youtube.com/playlist?list=PL2B6OzTsMUrwo4hA3BBfS7ZR34K361Z8F

class CostGraph(GraphScene):
    CONFIG = {
        "x_min": -0.5,
        "x_max": 10,
        "y_min": -0.5,
        "y_max": 5,
        "y_bottom_tick": 0,
        "x_leftmost_tick": 0,
        "x_axis_label": "$p$",
        "y_axis_label": "$f$",
        "graph_origin": 2.5 * DOWN + 4 * LEFT,
        "axes_color": WHITE,
        # "x_labeled_nums": range(0, 12, 2),
        "cost_func": lambda x: (1 / 5) * (x - 5) ** 2 + 1 / 2,
        "cost_func_color": YELLOW,
        "derivative": lambda x: (2 / 5) * (x - 5),
        "tangent_line": lambda x, pt: (2 / 5) * (x - 5) * (x - pt[0]) + pt[1],
    }

    def construct(self):
        self.setup_axes(animate=True)
        cost_func = self.get_graph(self.cost_func, self.cost_func_color, x_min=0.25, x_max=self.x_max - 0.25)
        self.play(ShowCreation(cost_func))


class CostDerivativesGraph(GraphScene):
    CONFIG = {
        "x_min": -0.5,
        "x_max": 10,
        "y_min": -0.5,
        "y_max": 5,
        "y_bottom_tick": 0,
        "x_leftmost_tick": 0,
        "x_axis_label": "$p$",
        "y_axis_label": "$f$",
        "graph_origin": 2.5 * DOWN + 6 * LEFT,
        "axes_color": WHITE,
        "cost_func": lambda x: (1 / 5) * (x - 5) ** 2 + 1 / 2,
        "cost_func_color": YELLOW,
        "derivative": lambda x: (2 / 5) * (x - 5),
        "tangent_line": lambda x_o, y_o, m: lambda x: m * (x - x_o) + y_o,
        "inverse_tangent_line": lambda x_o, y_o, m: lambda y: (y - y_o) / m + x_o,
        "line_color": RED,
        "start_at_animation_number": 1,
        # "camera_config": {"background_color": WHITE}
    }

    def get_boundaries(self, inv_func: Callable[[float], int]) -> Tuple[float, float]:
        """

        :param y_min: Lower limit for the y-axis
        :param y_max: Higher limit for the y-axis
        :param inv_func: Inverse of the function we're graphing
        :return: The x-value pairs (for y_max and y_min) that we should limit the graph to
        """
        x_bound_y_min = inv_func(self.y_min)
        x_bound_y_max = inv_func(self.y_max)

        x_min_bound = min(x_bound_y_min, x_bound_y_max)
        x_max_bound = max(x_bound_y_min, x_bound_y_max)

        if x_min_bound < self.x_min: x_min_bound = self.x_min
        if x_max_bound > self.x_max: x_max_bound = self.x_max

        return x_min_bound, x_max_bound

    def construct(self):
        # This needs to be the first thing
        self.setup_axes(animate=False)

        # Define cost function for graphing
        cost_func_graph = self.get_graph(self.cost_func, color=self.cost_func_color, x_min=0.25,
                                         x_max=self.x_max - 0.25)

        # Define x and y values we will iterate over
        x_values = list(range(2, 10))
        x_values.remove(5)  # Would be undefined there (slope = zero)
        x_values = x_values + x_values[-2::-1]  # Reverse list

        y_values = [self.cost_func(x) for x in x_values]
        # pts = zip(x_values, y_values)

        # Get these points in the graph and make the dots
        graph_pts = [self.input_to_graph_point(x, cost_func_graph) for x in
                     x_values]  # Equivalent to self.coords_to_point(x,y)
        dots = [Dot(graph_pt) for graph_pt in graph_pts]

        # Get the vertical lines from axis to graph
        vertical_lines = [self.get_vertical_line_to_graph(x, cost_func_graph, color=self.line_color)
                          for x in x_values]

        # Find the tangents lines
        # Slopes
        slopes = [self.derivative(x) for x in x_values]
        # Define the boundaries for the tangent graph
        boundaries_x = [self.get_boundaries(self.inverse_tangent_line(x, y, m))
                        for x, y, m in zip(x_values, y_values, slopes)]
        # Get the tangent
        tangent_lines = [self.tangent_line(x, y, m) for x, y, m in zip(x_values, y_values, slopes)]
        tangent_lines_graph = [self.get_graph(tangent_line, self.line_color, x_min=boundary_x[0], x_max=boundary_x[1])
                               for tangent_line, boundary_x in zip(tangent_lines, boundaries_x)]

        # Text animations
        slopes_text = [TextMobject('$f\'(p)$ = $m$ = ', '{0:.1f}'.format(m)).move_to(5 * RIGHT).scale(1) for m in
                       slopes]

        # Animations start here
        self.add(cost_func_graph)
        for i in range(len(x_values)):
            if not i:
                self.add(
                    vertical_lines[i],
                    dots[i],
                    tangent_lines_graph[i],
                    slopes_text[i]
                )
            else:

                self.play(
                    ReplacementTransform(vertical_lines[i - 1], vertical_lines[i]),
                    ReplacementTransform(dots[i - 1], dots[i]),
                    ReplacementTransform(tangent_lines_graph[i - 1], tangent_lines_graph[i]),
                    ReplacementTransform(slopes_text[i - 1], slopes_text[i])
                )
                self.wait(0.25)


class CostSteps(GraphScene):
    CONFIG = {
        "x_min": -0.5,
        "x_max": 10,
        "y_min": -0.5,
        "y_max": 5,
        "y_bottom_tick": 0,
        "x_leftmost_tick": 0,
        "x_axis_label": "$p$",
        "y_axis_label": "$f$",
        "graph_origin": 2.5 * DOWN + 6 * LEFT,
        "axes_color": WHITE,
        "cost_func": lambda x: (1 / 5) * (x - 5) ** 2 + 1 / 2,
        "cost_func_color": YELLOW,
        "derivative": lambda x: (2 / 5) * (x - 5),
        "tangent_line": lambda x_o, y_o, m: lambda x: m * (x - x_o) + y_o,
        "inverse_tangent_line": lambda x_o, y_o, m: lambda y: (y - y_o) / m + x_o,
        "line_color": RED,
        "start_at_animation_number": 1
    }

    def get_boundaries(self, inv_func: Callable[[float], int]) -> Tuple[float, float]:
        """

        :param y_min: Lower limit for the y-axis
        :param y_max: Higher limit for the y-axis
        :param inv_func: Inverse of the function we're graphing
        :return: The x-value pairs (for y_max and y_min) that we should limit the graph to
        """
        x_bound_y_min = inv_func(self.y_min)
        x_bound_y_max = inv_func(self.y_max)

        x_min_bound = min(x_bound_y_min, x_bound_y_max)
        x_max_bound = max(x_bound_y_min, x_bound_y_max)

        if x_min_bound < self.x_min: x_min_bound = self.x_min
        if x_max_bound > self.x_max: x_max_bound = self.x_max

        return x_min_bound, x_max_bound

    def do_every_step(self, x, cost_func_graph):
        # Calculate the corresponding y value
        y = self.cost_func(x)

        # Get the point in the graph and make a dot
        graph_pt = self.input_to_graph_point(x, cost_func_graph)
        dot = Dot(graph_pt)

        # Get the vertical line
        vertical_line = self.get_vertical_line_to_graph(x, cost_func_graph, color=self.line_color)

        # Get the tangent line functions and graphs
        m = self.derivative(x)
        tangent_line = self.tangent_line(x, y, m)
        # For graph
        tangent_line_xbound = self.get_boundaries(self.inverse_tangent_line(x, y, m))
        tangent_line_graph = self.get_graph(tangent_line, self.line_color, x_min=tangent_line_xbound[0],
                                            x_max=tangent_line_xbound[1])
        return dot, vertical_line, m, tangent_line_graph

    def generate_derivative_text(self, m):
        return TextMobject('$f\'(p)$', ' = ', '$m$', ' = ', ' {0:.2f}'.format(m)).move_to(4.5 * RIGHT + UP)

    def construct(self):
        # This needs to be the first thing
        self.setup_axes(animate=False)

        # Define cost function for graphing
        cost_func_graph = self.get_graph(self.cost_func, color=self.cost_func_color, x_min=0.25,
                                         x_max=self.x_max - 0.25)

        # Set hyperparameters
        alpha = 4
        n_steps = 4

        # Get the starting point
        x_prev = 6.5

        dot_prev, vertical_line_prev, m_prev, tangent_line_graph_prev = self.do_every_step(x_prev, cost_func_graph)

        # Text fields
        derivative_text_prev = TextMobject('$f\'(p)$', ' = ', '$m$').move_to(4.5 * RIGHT + UP)
        p_text_prev = TextMobject('$p_{t}$', '$\leftarrow$', '$p_{(t-1)}$', '-', '$m_{(t-1)}$').move_to(
            4.5 * RIGHT + DOWN)

        # Animations start here
        self.add(
            cost_func_graph
        )
        self.play(
            FadeIn(dot_prev),
            Write(derivative_text_prev),
            Write(p_text_prev)
        )
        self.wait(1)
        for i in range(n_steps):
            # Get next parameters
            x = x_prev - alpha * m_prev
            dot, vertical_line, m, tangent_line_graph = self.do_every_step(x, cost_func_graph)

            # Build transitions
            arrow = Arrow(dot_prev.get_center(), dot.get_center())
            derivative_text = self.generate_derivative_text(m_prev)

            # Turns out we didn't use the examples with number filled in
            # p_text = TextMobject('$p_{t}$', '$\leftarrow$', '{0:.2f}'.format(x_prev), '-', '{0:.2f}'.format(m_prev)).move_to(5 * RIGHT + DOWN)

            # For an applied example
            # if m_prev < 0:
            #     p_text = TextMobject('$p_{t}$', '$\leftarrow$', '{0:.2f}'.format(x_prev), '-', '({0:.2f})'.format(m_prev)).move_to(5*RIGHT + DOWN)
            # else:
            #     p_text = TextMobject('$p_{t}$', '$\leftarrow$', '{0:.2f}'.format(x_prev), '-', '{0:.2f}'.format(m_prev)).move_to(5*RIGHT + DOWN)

            # Animate
            # Draw tangent line and show derivative
            self.play(
                ShowCreation(vertical_line_prev, run_time=0.5),
                ShowCreation(tangent_line_graph_prev),
                Transform(derivative_text_prev, derivative_text)
            )
            # Growing arrow and populate values
            self.play(
                GrowArrow(arrow, run_time=2),
                ReplacementTransform(derivative_text[2], p_text_prev[-1]),  # Populate the slope value
                # Transform(p_text_prev, p_text_prev) # Populate the dot values
            )
            # Move dot and perform step
            self.play(
                ReplacementTransform(dot_prev, dot, run_time=0.5),
                FadeOut(vertical_line_prev),
                FadeOut(tangent_line_graph_prev),
                ReplacementTransform(p_text_prev[2:].copy(), p_text_prev[0])
            )
            # Make arrow go away
            self.play(
                FadeOut(arrow),
                ReplacementTransform(dot.copy(), p_text_prev[2]),
                ReplacementTransform(derivative_text[2], p_text_prev[-1])
            )
            # Update values
            x_prev = x
            dot_prev = dot
            vertical_line_prev = vertical_line
            m_prev = m
            tangent_line_graph_prev = tangent_line_graph
        self.play(
            FadeOut(dot_prev),
            FadeOut(derivative_text_prev),
            FadeOut(p_text_prev),
        )


class CostLargeSteps(GraphScene):
    CONFIG = {
        "x_min": -0.5,
        "x_max": 10,
        "y_min": -0.5,
        "y_max": 5,
        "y_bottom_tick": 0,
        "x_leftmost_tick": 0,
        "x_axis_label": "$p$",
        "y_axis_label": "$f$",
        "graph_origin": 2.5 * DOWN + 6 * LEFT,
        "axes_color": WHITE,
        "cost_func": lambda x: (1 / 2) * (x - 5) ** 2 + 1 / 2,
        "cost_func_color": YELLOW,
        "derivative": lambda x: (x - 5),
        "tangent_line": lambda x_o, y_o, m: lambda x: m * (x - x_o) + y_o,
        "inverse_tangent_line": lambda x_o, y_o, m: lambda y: (y - y_o) / m + x_o,
        "line_color": RED,
        "start_at_animation_number": 1
    }

    def get_boundaries(self, inv_func: Callable[[float], int]) -> Tuple[float, float]:
        """

        :param y_min: Lower limit for the y-axis
        :param y_max: Higher limit for the y-axis
        :param inv_func: Inverse of the function we're graphing
        :return: The x-value pairs (for y_max and y_min) that we should limit the graph to
        """
        x_bound_y_min = inv_func(self.y_min)
        x_bound_y_max = inv_func(self.y_max)

        x_min_bound = min(x_bound_y_min, x_bound_y_max)
        x_max_bound = max(x_bound_y_min, x_bound_y_max)

        if x_min_bound < self.x_min: x_min_bound = self.x_min
        if x_max_bound > self.x_max: x_max_bound = self.x_max

        return x_min_bound, x_max_bound

    def do_every_step(self, x, cost_func_graph):
        # Calculate the corresponding y value
        y = self.cost_func(x)

        # Get the point in the graph and make a dot
        graph_pt = self.input_to_graph_point(x, cost_func_graph)
        dot = Dot(graph_pt)

        # Get the vertical line
        vertical_line = self.get_vertical_line_to_graph(x, cost_func_graph, color=self.line_color)

        # Get the tangent line functions and graphs
        m = self.derivative(x)
        tangent_line = self.tangent_line(x, y, m)
        # For graph
        tangent_line_xbound = self.get_boundaries(self.inverse_tangent_line(x, y, m))
        tangent_line_graph = self.get_graph(tangent_line, self.line_color, x_min=tangent_line_xbound[0],
                                            x_max=tangent_line_xbound[1])
        return dot, vertical_line, m, tangent_line_graph

    def generate_derivative_text(self, m):
        return TextMobject('$f\'(p)$', ' = ', '$m$', ' = ', ' {0:.2f}'.format(m)).move_to(4.5 * RIGHT + UP)

    def construct(self):
        # This needs to be the first thing
        self.setup_axes(animate=False)

        # Define cost function for graphing
        cost_func_graph = self.get_graph(self.cost_func, color=self.cost_func_color, x_min=2, x_max=self.x_max - 2)

        # Set hyperparameters
        alpha = 2.25
        n_steps = 3

        # Get the starting point
        x_prev = 6.5

        dot_prev, vertical_line_prev, m_prev, tangent_line_graph_prev = self.do_every_step(x_prev, cost_func_graph)

        # Text fields
        derivative_text_prev = TextMobject('$f\'(p)$', ' = ', '$m$').move_to(4.5 * RIGHT + UP)
        p_text_prev = TextMobject('$p_{t}$', '$\leftarrow$', '$p_{(t-1)}$', '-', '$m_{(t-1)}$').move_to(
            4.5 * RIGHT + DOWN)

        # Animations start here
        self.add(
            cost_func_graph
        )
        self.play(
            FadeIn(dot_prev),
            Write(derivative_text_prev),
            Write(p_text_prev)
        )
        self.wait(1)
        for i in range(n_steps):
            # Get next parameters
            x = x_prev - alpha * m_prev
            dot, vertical_line, m, tangent_line_graph = self.do_every_step(x, cost_func_graph)

            # Build transitions
            arrow = Arrow(dot_prev.get_center(), dot.get_center())
            derivative_text = self.generate_derivative_text(m_prev)
            # p_text = TextMobject('$p_{t}$', '$\leftarrow$', '{0:.2f}'.format(x_prev), '-', '{0:.2f}'.format(m_prev)).move_to(5 * RIGHT + DOWN)

            # For an applied example
            # if m_prev < 0:
            #     p_text = TextMobject('$p_{t}$', '$\leftarrow$', '{0:.2f}'.format(x_prev), '-', '({0:.2f})'.format(m_prev)).move_to(5*RIGHT + DOWN)
            # else:
            #     p_text = TextMobject('$p_{t}$', '$\leftarrow$', '{0:.2f}'.format(x_prev), '-', '{0:.2f}'.format(m_prev)).move_to(5*RIGHT + DOWN)

            # Animate
            # Draw tangent line and show derivative
            self.play(
                ShowCreation(vertical_line_prev, run_time=0.5),
                ShowCreation(tangent_line_graph_prev),
                Transform(derivative_text_prev, derivative_text)
            )
            # Growing arrow and populate values
            self.play(
                GrowArrow(arrow, run_time=2),
                ReplacementTransform(derivative_text[2], p_text_prev[-1]),  # Populate the slope value
                # Transform(p_text_prev, p_text_prev) # Populate the dot values
            )
            # Move dot and perform step
            self.play(
                ReplacementTransform(dot_prev, dot, run_time=0.5),
                FadeOut(vertical_line_prev),
                FadeOut(tangent_line_graph_prev),
                ReplacementTransform(p_text_prev[2:].copy(), p_text_prev[0])
            )
            # Make arrow go away
            self.play(
                FadeOut(arrow),
                ReplacementTransform(dot.copy(), p_text_prev[2]),
                ReplacementTransform(derivative_text[2], p_text_prev[-1])
            )
            # Update values
            x_prev = x
            dot_prev = dot
            vertical_line_prev = vertical_line
            m_prev = m
            tangent_line_graph_prev = tangent_line_graph
        self.play(
            FadeOut(dot_prev),
            FadeOut(derivative_text_prev),
            FadeOut(p_text_prev),
        )


class CostTwoDimensions(ThreeDScene):
    CONFIG = {
        "cost": lambda x, y: np.array([x, y, (x / 2) ** 2 + (y / 1.5) ** 2 - 4]),
        "tangent_plane": lambda x_o, y_o, z_o: lambda x, y: np.array(
            [x, y, ((2/2) * (x - x_o)) + ((2*-3/1.5**2) * (y - y_o)) + z_o]),
        "gradient": np.array([1 / 2, 2 / 1.5 ** 2]),
        "alpha": 0.5,
        "xy_start_point": np.array([2, -3], dtype='float64'),
        "n_steps": 5,
        "point_color": RED,

        "parametric_kwargs": {
            "u_min": -3.5,
            "u_max": 3.5,
            "v_min": -3.5,
            "v_max": 3.5,
            "checkerboard_colors": [YELLOW_D, YELLOW_E],
            "resolution": 32  # TODO: Change this once we are happy
        },
        "func_opacity": 0.75
    }

    def get_updated_weights(self, weights: np.array):
        weights = weights - self.alpha*self.get_gradient_at_point(weights)
        return weights

    def get_gradient_at_point(self, weights: np.array):
        return weights*self.gradient

    def get_gradient_text(self, gradients: np.array):
        assert gradients.shape == (2,), "Bad input: gradients shape: {}".format(gradients.shape)
        gradient_x, gradient_y = gradients
        gradient_x_text = TexMobject("\\frac{\partial f}{\partial x}", "=", '{0:.1f}'.format(gradient_x)).to_corner(UP+LEFT)
        gradient_y_text = TexMobject("\\frac{\partial f}{\partial y}", "=", '{0:.1f}'.format(gradient_y)).next_to(gradient_x_text, DOWN)
        return gradient_x_text, gradient_y_text

    def construct(self):
        # axes = ThreeDAxes()  # We are not using axes here

        # Cost function graph
        cost_graph = ParametricSurface(
            self.cost,
            **self.parametric_kwargs
        ).set_opacity(self.func_opacity)

        # Tangent plane at the starting point
        tangent_graph = ParametricSurface(
            self.tangent_plane(*list(self.cost(*self.xy_start_point.tolist()))),
            u_min=self.parametric_kwargs['u_min'],
            u_max=self.parametric_kwargs['u_max'],
            v_min=self.parametric_kwargs['v_min'],
            v_max=self.parametric_kwargs['v_max'],
            checkerboard_colors=[RED],
            resolution=10
        ).set_opacity(1)

        # Initialize the weights - remember that the weights are the xy coordinates in the xyz plane
        xy_values = [self.xy_start_point]
        # Compute the nexts xy value pairs
        for i in range(self.n_steps-1): xy_values.append(self.get_updated_weights(xy_values[i]))

        # Compute the gradient values for the text
        gradient_values = [self.get_gradient_at_point(weight) for weight in xy_values]
        gradient_text = [self.get_gradient_text(gradient) for gradient in gradient_values]

        # Compute the points and arrows that perform the descent
        points = [Dot(self.cost(x, y), color=self.point_color).scale(1.5) for x,y in xy_values]
        arrows = [Arrow(points[i], points[i+1], color=self.point_color) for i in range(len(points)-1)]

        # Animations
        # Setup
        self.set_camera_orientation(phi=50 * DEGREES)
        # self.add(axes)  # We don't need axes here
        self.play(ShowCreation(cost_graph))

        # Start the descent
        for i in range(self.n_steps):
            if not i:
                self.play(ShowCreation(points[i]))
                self.add_fixed_in_frame_mobjects(gradient_text[i][0], gradient_text[i][1])
                self.play(
                    Write(gradient_text[i][0]),
                    Write(gradient_text[i][1])
                )
                self.begin_ambient_camera_rotation(rate=0.2)
                self.play(ShowCreation(tangent_graph))
                self.wait(4)
                self.play(FadeOut(tangent_graph))
            else:
                self.play(GrowArrow(arrows[i-1], run_time=3))
                self.add_fixed_in_frame_mobjects(gradient_text[i][0], gradient_text[i][1])
                self.play(
                    ReplacementTransform(points[i-1], points[i]),
                    ReplacementTransform(gradient_text[i-1][0], gradient_text[i][0]),
                    ReplacementTransform(gradient_text[i - 1][1], gradient_text[i][1])
                )
                self.play(FadeOut(arrows[i-1]))
        self.wait(5)
        self.play(
            FadeOut(points[-1]),
            FadeOut(arrows[-1]),
            FadeOut(gradient_text[-1][0]),
            FadeOut(gradient_text[-1][1])
        )

