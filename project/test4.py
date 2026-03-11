call_counts = 0

def repeat_text(text, repeat):
    return text * repeat

def decor(f):
    def wrapper(text, repeat):
        global call_counts
        call_counts += 1
        return f(text, repeat)

    return wrapper

repeat_text = decor(repeat_text)
print(repeat_text("a", 2))
print(repeat_text("b", 4))
print(repeat_text("b", 4))
print(call_counts)
