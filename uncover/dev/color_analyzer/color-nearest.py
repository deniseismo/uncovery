main_colors = (
    (255, 255, 255, "white"),
    (0, 0, 0, "black"),
    (255, 0, 0, "red"),
    (0, 255, 0, "lime"),
    (0, 0, 255, 'blue'),
    (255, 255, 0, 'yellow'),
    (0, 255, 255, 'cyan'),
    (255, 0, 255, 'magenta'),
    (128, 0, 128, 'purple'),
    (0, 128, 128, 'teal'),
    (0, 128, 0, 'green'),
    (112, 66, 20, 'sepia'),
    (139, 69, 19, 'brown'),
    (128, 128, 128, 'gray'),
    (255, 140, 0, 'orange'),
    (128, 0, 0, 'maroon'),
    (54, 69, 79, 'charcoal')
)


def nearest_colour(base_colors, query_color):
    """
    :param base_colors: a list of main colors to base search off
    :param query_color: a query color
    :return:
    """
    return min(base_colors, key=lambda subject: sum((s - q) ** 2 for s, q in zip(subject, query_color)))


print(nearest_colour(
    main_colors,
    (65, 67, 68))
)
