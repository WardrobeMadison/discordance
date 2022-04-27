import pandas as pd
from collections import defaultdict

df = pd.read_csv("/home/joe/Projects/Discordance/data/rstarrmap.txt", "\t")


dmap = defaultdict(list)
for _, row in df.iterrows():
    dmap[(row["protocolname"], row["led"], row["lightamplitude"], row["lightmean"])] = (row["lightamplitude_rstarr"], row["lightmean_rstarr"])


dmap

