def partialOrderings(string, solved):
    '''Returns number of ordered lists satisfying a path string.
        NOTE:This is an upperbound on number of pathstring solutions
    '''
    count = 0
    solved[string] = []
    if len(string) == 1:
        solved[string] = 1
        return
    if string[0] == "D":
        partial = string[1:]
        if (partial not in solved):
            partialOrderings(partial, solved)
        count += solved[partial]
    if string[len(string) - 1] == "U":
        partial = string[:len(string) - 1]
        if (partial not in solved):
            partialOrderings(partial, solved)
        count += solved[partial]
    for i in range(0, len(string) - 1):
        if string[i] == "U":
            if string[i + 1] == "D":
                partial1 = string[:i] + "U" + string[i + 2:]
                partial2 = string[:i] + "D" + string[i + 2:]
                if partial1 not in solved:
                    partialOrderings(partial1, solved)
                count += solved[partial1]
                if partial2 not in solved:
                    partialOrderings(partial2, solved)
                count += solved[partial2]
                i += 1
    solved[string] = count
    return count
