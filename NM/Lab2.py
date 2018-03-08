from math import sin, cos

def incremental_search(x_i, x_u, ns):
    h = (x_u - x_i) / ns
    results = []

    while x_i < x_u:
        print x_i
        f1 = cos(3 * x_i) + sin(10 * x_i)
        f2 = cos(3 * (x_i + h)) + sin(10 * (x_i + h))
        if (f1 * f2) < 0:
            results.append((x_i, x_i + h))
        x_i += h

    for idx, interval in enumerate(results):
        print "Interval %d: %s" % (idx+1, interval)


if __name__ == "__main__":
    incremental_search(3, 6, 50.0)
