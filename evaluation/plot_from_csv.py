import pandas as pd
from matplotlib import pyplot as plt


####################### Plot Functions ########################

def time_plot(datas, names):
    fig, ax = plt.subplots()

    for n in range(len(datas)):
        data = datas[n]
        df = data[data.timeout == False]
        df = df.sort_values("real").reset_index(drop=True)
        df.index += 1
        df = df.reset_index()

        fig = df.plot(label= names[n], xlabel="Instances solved", ylabel="Real Time (s)", x="index", y="real", subplots=False, ax=ax)

    fig = fig.get_figure()
    fig.savefig("evaluation/plots/time_plot.pdf")

def programs_plot(datas, names):
    fig, ax = plt.subplots()

    for n in range(len(datas)):
        data = datas[n]
        df = data[data.timeout == False]
        df = df.sort_values("programs").reset_index(drop=True)
        df.index += 1
        df = df.reset_index()

        fig = df.plot(label= names[n], xlabel="Instances solved", ylabel="Attempted programs", x="index", y="programs", subplots=False, ax=ax)

    fig = fig.get_figure()
    fig.savefig("evaluation/plots/programs_plot.pdf")



files = ["evaluation/data/textbook-no_sketch.csv", "evaluation/data/test.csv"]
csv_list = []
name_list = []

for file in files:
    csv_list.append(pd.read_csv(file))
    name_list.append(file.rsplit("/", 1)[1][:-4])

time_plot(csv_list, name_list)
programs_plot([csv_list[1]], [name_list[1]])
