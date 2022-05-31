path = "/Users/jnagy2/Documents/DissconaceLogs/log_20220525_220714.txt"

with open(path, "r") as fin:
    text = fin.readlines()


with open("delete.txt", "w+") as fout:
    for line in text:
        fout.write(line.strip().split(": ")[-1]+"\n")

