import numpy as np
import copy
import pandas as pd
import os

# load social accounting matrix
current_path = os.path.abspath(os.path.dirname(__file__))
sam_path = os.path.join(current_path, "data", "Databank_CGE_2017.xlsx")
df_sam2 = pd.read_excel(sam_path, index_col=0, header=0)
df_sam2 = df_sam2.fillna(0.)
num_commodities = 34

# create new dataframe with sam in format of type 1
factors = ["K", "L"]
agents = ["HH_bottom40R", "HH_top60R", "HH_bottom40U", "HH_top60U", "Govt"]
taxes = ["TC", "TE", "TK", "TY"]
inv = ["Investment"]
row = ["ROW"]
ind_full = list(range(1, 2 * num_commodities + 1))
ind = list(range(1, num_commodities + 1))

points_full = ind_full + factors + agents + taxes + inv + row
points = ind + factors + agents + taxes + inv + row
points_without_ind = factors + agents + taxes + inv + row

num_rows = len(points_full)

idx2points = {el: points_full[i] for i, el in enumerate(df_sam2.index[:num_rows])}
col2points = {el: points_full[i] for i, el in enumerate(df_sam2.columns[:num_rows])}

# drop other rows & columns
df_sam2.drop(df_sam2.index[num_rows + 1:], inplace=True)
df_sam2.drop(columns=df_sam2.columns[num_rows:], inplace=True)

# rename rows & columns
df_sam2.rename(index=idx2points, inplace=True)
df_sam2.rename(columns=col2points, inplace=True)

# create sam in format type1
df_sam1 = copy.deepcopy(df_sam2)
df_sam1.drop(df_sam2.index[num_commodities:2 * num_commodities], inplace=True)
df_sam1.drop(columns=df_sam2.columns[num_commodities:2 * num_commodities], inplace=True)
#************* read data from sam2 *************#
for j in ind:
    for i in ind:
        df_sam1.loc[i, j] = df_sam2.loc[i + num_commodities, j]
    df_sam1.loc[j, points_without_ind[0]:] = df_sam2.loc[j, points_without_ind[0]:] + df_sam2.loc[j + num_commodities, points_without_ind[0]:]

for point in points_without_ind:
    for i in ind:
        df_sam1.loc[point, i] = df_sam2.loc[point, i] + df_sam2.loc[point, i + num_commodities]
for i in ind:
    df_sam1.loc[i, i] = df_sam2.loc[i, i + num_commodities] - df_sam1.loc[i, i]

i = 19
print(df_sam1.loc[i, i])
df_sam1.loc[i, i] += 885.8614684853083
print(df_sam1.loc[i, i])

i = 21
df_sam1.loc[i, i] -= 885.8614684853083
# check
for i in ind:
    if abs(df_sam1.loc[i].sum() - df_sam1[i].sum()) >= 1e-07:
        print(i)
        print(df_sam1.loc[i].sum() - df_sam1[i].sum())


# df_sam1.to_excel(os.path.join(current_path, "data", "databank_2017_type1.xlsx"))