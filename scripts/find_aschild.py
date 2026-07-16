import glob, re
files = glob.glob("frontend/**/*.tsx", recursive=True)
for f in files:
    for i, l in enumerate(open(f, encoding="utf-8").readlines()):
        if re.search(r"asChild.*isLoading|isLoading.*asChild|loading.*asChild|asChild.*loading", l, re.I):
            print(f"{f}:{i+1}: {l.strip()}")
