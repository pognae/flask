def cond(x):
    if x:
        return x.startswith("notice_pop1") and not "notice_pop0" in x
    else:
        return False