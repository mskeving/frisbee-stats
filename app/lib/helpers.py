def percentage(subset, total):
    """
    Given a subset (int) and total(int), return
    a formatted percentage (float)
    """
    percentage = float(subset) / float(total) * 100
    return "{0:.2f}".format(round(percentage, 2))
