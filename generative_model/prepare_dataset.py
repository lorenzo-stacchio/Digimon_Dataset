import pandas as pd
import random

df = pd.read_csv("C:/Users/Lorenzo Stacchio/Progetti/Digimon_Dataset/dataset/dataset.csv")

print(df.columns)

df = df[["image_filename","description"]]

# choices_idx = random.choices(["train/", "val/"], weights=[0.9,0.1], k=len(df))
choices_idx  = ["train/"] *len(df)
train_samples = random.choice(list(range(len(df))))


df["image_filename"] = [idx + value for idx, value in zip (choices_idx, list(df["image_filename"]))]



df = df.rename(columns={"image_filename": "file_name"})

df.to_csv("C:/Users/Lorenzo Stacchio/Progetti/Digimon_Dataset/dataset/metadata.csv",index=False)