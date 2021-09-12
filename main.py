import re
import itertools as iter


def getTextFun(file: str = "./temp/code1.py", fun : str = "fun") -> str:  # TODO update, FIXME refactor to lowercase
    """does not always work correctly, handles trivial cases"""
    text_fun = ""  # TODO rename text_fun, TODO smth
    try:
        with open(file, 'r') as f:
            is_fun = False
            for line in f:
                if re.match(rf"def +{fun}\(", line):  # find function, not function in function
                    is_fun = True
                elif not line.startswith(" ") and line != "\n":  # FIXME doesn't handle much
                    is_fun = False
                if is_fun:
                    text_fun += line
    except EnvironmentError:
        print(f"no file: {file}")
    if not text_fun:
        print(f"no {fun} in {file}")
    return text_fun


def count_metrics(text_fun: str):
    # used the assumptions:
    #     1) There are no line breaks
    #     2) "Docstring" is only one-line (and it string, not a comment)
    #     3) The function is compiled
    #     4) the code is not too fancy (only the main cases are processed)
    def comment_symbols(str):
        return str if str in ["'''", '"""'] else str[0]

    def remove_strings_and_comments(line):
        i = 0
        while True:
            leng = len(line)
            while i < leng and not line[i] in ["'", '"', "#"]:
                i += 1
            if i == leng:
                return line
            elif line[i] == "#":
                return line[0:i]
            else:
                comment_with = comment_symbols(line[i:i+3])
                line = line[0:i] + line[i + len(comment_with) + line[i + len(comment_with):leng].find(comment_with) + len(comment_with):leng]
                assert (len(line) != leng)

    def count_comment_fix_todo():
        # in one comment we believe that there are no more than 1 TODO and FIXME (combine them)
        # one line with code - separate comment, but block only comments - one comment
        def get_comment(line):  # only main cases processed (as far as i know the comments in python)
            while True:
                leng = len(line)
                i = 0
                while i < leng and not line[i] in ["'", '"', "#"]:
                    i += 1
                if i == leng:
                    return ""
                elif line[i] == "#":
                    return line[i:leng]
                else:
                    comment_with = comment_symbols(line[i:i+3])
                    i += len(comment_with)
                    line = line[i + line[i:leng].find(comment_with) + len(comment_with):leng]
                    assert(len(line) != leng)

        def find_in_comment(comment):
            res = (0 if re.search("TODO", comment) is None else 1,
                   0 if re.search("FIXME", comment) is None else 1)
            return res

        comment = ""
        count_todo, count_fixme = 0, 0
        for line in re.split(r"\n|;", text_fun):
            if re.match(r" *#", line):
                comment += line
            else:
                if comment:
                    count_todo, count_fixme = tuple(x + y for x, y in zip((count_todo, count_fixme), find_in_comment(comment)))
                    comment = ""
                if re.search(r"#", line):
                    count_todo, count_fixme = tuple(x + y for x, y in zip((count_todo, count_fixme), find_in_comment(get_comment(line))))
        if comment:
            count_todo, count_fixme = tuple(x + y for x, y in zip((count_todo, count_fixme), find_in_comment(get_comment(line))))
        return count_todo, count_fixme

    def count_var_count_use():  # does not process f-strings and for almost all non-trivial cases :(
        def get_vars(line, pattern = "[^\w\.]"):
            return list(filter(len, map(lambda str: "".join(iter.takewhile(lambda x: x != ".", str)), re.split(pattern, line))))

        dict = {}
        for line in re.split(r"\n|;", text_fun):
            line = remove_strings_and_comments(line)
            expressions = []
            change_line = (re.sub(',', '=', line[line.find('('):line.find(')')]) + ' = ') if re.match(r" *def ", line) else line
            change_line = re.sub(r"==|!=|>=|<=|\+=|-=|\*=|/=|%=|&=|^=|", "", change_line).replace(" in ", " = ")  # TODO add "|="
            # print(f"{line} -> {change_line}")
            k = 0
            for i in re.finditer("=", change_line):
                expressions.append(change_line[k:i.start()])
                k = i.start() + 1
            for exp in expressions:
                skip_next = False
                for var in get_vars(get_vars(exp, r" for | if | or | and |[^\w\.\:| |,]")[-1], "[^\w\.\:]"):  # TODO [-1] correct?
                    if skip_next:
                        skip_next = False
                        continue
                    q = var
                    if var == ":":
                        skip_next = True    # a : str = "some"
                        continue
                    elif var[-1] == ":":
                        q = var[0:-1]
                        skip_next = True    # a: str = "some"
                    elif var[0] == ":":
                        continue            # a :str = "some"
                    if q not in dict and q not in ["lambda", "not"]:  # not all
                        dict[q] = 0
            for var in get_vars(line):
                if var in dict:
                    dict[var] += 1
        return dict

    def count_fun_call():
        # assume that the function is called in one line
        # the function itself is also considered
        def matching_par(line):
            open_pars = list(map(lambda x: x.start(), (re.finditer('\(', line))))
            close_pars = list(map(lambda x: x.start(), (re.finditer('\)', line))))
            for i in range(len(open_pars) - 1):
                if close_pars[i] < open_pars[i+1]:
                    return close_pars[i]
            leng = len(close_pars)
            return len(line) if leng == 0 else close_pars[min(len(open_pars), len(close_pars)) - 1]
                # FIXME terrible, non-working code, line splitting is not handled

        def func_found(line):
            open_par = line.find('(')
            if open_par == -1:
                return None, []
            before_open = list(filter(len, re.split(r'\s', line[0:open_par])))

            name = None if (not before_open or not before_open[-1]) else before_open[-1]
            if name is not None:
                j = len(name)-1
                while j >= 0 and (name[j] in ['.', '_'] or name[j].isdigit() or name[j].isalpha()):
                    j -= 1
                name = None if j+1 == len(name) else name[j+1:len(name)]
            if name is not None:
                pos = name.rfind('.')
                if pos != -1:
                    name = '_' + name[pos:len(name)]
            close_par = matching_par(line)
            # print(f"{line} -> {name},   {line[open_par + 1:close_par]}, {line[close_par + 1:len(line)]}")
            return name, [line[open_par+1:close_par], line[close_par+1:len(line)]]

        dict = {}
        for line in re.split(r"\n|;", text_fun):
            lines = [remove_strings_and_comments(line)]
            while True:
                new_lines = []
                for line in lines:
                    fun_name, l = func_found(line)
                    new_lines += l
                    if fun_name is not None and fun_name not in ["return", "if", "not", "and", "or"]:  # not all
                        dict[fun_name] = 1 if fun_name not in dict else dict[fun_name] + 1
                lines = list(filter(len, new_lines))
                if not lines:
                    break

        return dict

    return count_comment_fix_todo(), count_var_count_use(), count_fun_call()


def check():
    metric1 = count_metrics(getTextFun())
    assert (metric1[0] == (5, 2))
    print(metric1[1])
    print(metric1[2])
    print()
    metric2 = count_metrics(getTextFun("./temp/code1.py", "fun2"))
    assert (metric2[0] == (4, 3))
    print(metric2[1])
    print(metric2[2])
    print()
    metric3 = count_metrics(getTextFun("./main.py", "getTextFun"))
    assert (metric3[0] == (2, 2))
    print(metric3[1])
    print(metric3[2])
    print()
    metric4 = count_metrics(getTextFun("./main.py", "count_metrics"))
    assert (metric4[0] == (3, 2))
    print(metric4[1])
    print(metric4[2])


if __name__ == "__main__":
    check()
