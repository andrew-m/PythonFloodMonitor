"""
The MIT License (MIT)
Copyright (c) 2015 Olivier Devoisin
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math


class LttbException(Exception):
    pass


def largest_triangle_three_buckets(data, threshold):
    if not isinstance(data, list):
        raise LttbException("data is not a list")
    if not isinstance(threshold, int) or threshold <= 2 or threshold >= len(data):
        raise LttbException("threshold not well defined")
    for i in data:
        if not isinstance(i, (list, tuple)) or len(i) != 2:
            raise LttbException("datapoints are not lists or tuples")

    every = (len(data) - 2) / (threshold - 2)

    a = 0
    next_a = 0
    max_area_point = (0, 0)

    sampled = [data[0]]

    for i in range(0, threshold - 2):
        avg_x = 0
        avg_y = 0
        avg_range_start = int(math.floor((i + 1) * every) + 1)
        avg_range_end = int(math.floor((i + 2) * every) + 1)
        avg_rang_end = avg_range_end if avg_range_end < len(data) else len(data)

        avg_range_length = avg_rang_end - avg_range_start

        while avg_range_start < avg_rang_end:
            avg_x += data[avg_range_start][0]
            avg_y += data[avg_range_start][1]
            avg_range_start += 1

        avg_x /= avg_range_length
        avg_y /= avg_range_length

        range_offs = int(math.floor((i + 0) * every) + 1)
        range_to = int(math.floor((i + 1) * every) + 1)

        point_ax = data[a][0]
        point_ay = data[a][1]

        max_area = -1

        while range_offs < range_to:
            area = (
                math.fabs(
                    (point_ax - avg_x) * (data[range_offs][1] - point_ay)
                    - (point_ax - data[range_offs][0]) * (avg_y - point_ay)
                )
                * 0.5
            )

            if area > max_area:
                max_area = area
                max_area_point = data[range_offs]
                next_a = range_offs
            range_offs += 1

        sampled.append(max_area_point)
        a = next_a

    sampled.append(data[len(data) - 1])

    return sampled
