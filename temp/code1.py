def     fun(a, b, c, d):
    kol = len([a,b,c,d])                        # TODO rewrite this
    sr_ar = (a + b + c + d) / kol               # TODO may zero division?
    sr_geom = pow(a * b * c * d, kol)           # TODO wrong answer
    print("print # # # TODO''#' $'#' FIXME")    # comment
    sr_garm = kol / (1/a + 1/b + 1/c + 1/d)     # FIXME division zero, TODO round
    return (sr_ar, sr_geom, sr_garm)            # FIXME remove brackets
    # TODO add sr_...

def fun2(a, b, c, d):                           # FIXME copy function
    kol = len([a,b,c,d])
    # TODO rewrite this
    sr_ar = (a + b + c + d) / kol               # TODO may zero division?, FIXME format
    sr_geom = pow(a * b * c * d, kol)           # TODO wrong answer
    sr_garm = kol / (1/a + 1/b + 1/c + 1/d)     # FIXME division zero, TODO round
    return sr_ar, sr_geom, sr_garm

assert(fun(1,2,3,4) == fun2(1,2,3,4)) # TODO remove


assert (1 == 1)  # one-line comment
# one
# big
# comment
