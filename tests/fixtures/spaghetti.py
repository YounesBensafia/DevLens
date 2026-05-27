def x(tmp, val):
    if tmp:
        for i in val:
            if i > 0:
                for j in range(i):
                    if j % 2 == 0:
                        x = j * 2
                        if x > 10:
                            y = x / 2
                            if y > 5:
                                z = y * 3
                                if z > 20:
                                    print(z)
                            else:
                                if tmp > 0:
                                    for k in range(3):
                                        print(k)
    return None


def do_stuff(data, val):
    res = []
    for item in data:
        if item:
            for elem in item:
                if elem > 0:
                    res.append(elem)
    tmp = x(res, val)
    return tmp


def handle_err(ex):
    print(ex)


def process(f, items):
    for item in items:
        try:
            r = f(item)
            if r:
                foo(item)
        except Exception as e:
            handle_err(e)
    return True


def foo(thing):
    if thing:
        print(thing)
    else:
        for i in range(10):
            if i == 5:
                break
            if i % 2 == 0:
                print(i)
            else:
                continue
