import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from matplotlib import rcParams

####################### Plot Functions ########################

def time_plot(datas, names):
    fig, ax = plt.subplots()

    for n in range(len(datas)):
        df = datas[n]
        df = df[df.timeout == False]
        df = df.sort_values("real").reset_index(drop=True)
        df.index += 1
        df = df.reset_index()

        fig = df.plot(label= names[n], xlabel="Instances", ylabel="Real Time (s)", x="index", y="real", style='.-', subplots=False, ax=ax)
        # df.plot(style='.-', markevery=5)

    fig = fig.get_figure()
    return fig

def programs_plot(datas, names):
    fig, ax = plt.subplots()

    for n in range(len(datas)):
        df = datas[n]
        df = df[df.timeout == False]
        df = df.sort_values("programs").reset_index(drop=True)
        df.index += 1
        df = df.reset_index()

        fig = df.plot(label= names[n], xlabel="Instances solved", ylabel="Attempted programs", x="index", y="programs", style='.-', subplots=False, ax=ax)
        # fig.yaxis.set_major_formatter(mtick.PercentFormatter())
        # fig = df.plot(label=names[n], xlabel="Instance", ylabel="Attempted programs", x="name", y="programs", subplots=False, ax=ax)

    fig = fig.get_figure()
    return fig

def solved_plot(datas, names):
    index = []
    values = []

    for n in range(len(datas)):
        data = datas[n]
        df = data[data.timeout == False]
        index.append(names[n])
        values.append(len(df.index))

    df = pd.DataFrame({"solved": values}, index=index)

    rcParams.update({'figure.autolayout': True})
    fig = df.plot(kind="barh", xlabel="Benchmark", ylabel="Solved instances") # figsize = (6.4, 4.8)
    fig.get_legend().remove()
    fig = fig.get_figure()
    return fig

def gt_plot(datas, names):
    index = []
    values = []

    for n in range(len(datas)):
        data = datas[n]
        df = data[data.ground_truth == True]
        index.append(names[n])
        values.append(len(df.index))

    df = pd.DataFrame({"solved": values}, index=index)

    rcParams.update({'figure.autolayout': True})
    fig = df.plot(kind="barh", xlabel="Benchmark", ylabel="Solved instances") # figsize = (6.4, 4.8)
    fig.get_legend().remove()
    fig = fig.get_figure()
    return fig


# files = ["evaluation/data/textbook-no_sketch.csv", "evaluation/data/on/off_no_children.csv", "evaluation/data/on/on_no_children.csv", "evaluation/data/on/off_no_children_all_constraints.csv", "evaluation/data/on/off_no_children_constraints.csv"]
dir = "evaluation/data/"
files = [dir+"st-no_sketch.csv", dir+"st-no_children.csv", dir+"st-no_root.csv"]
csv_list = []
name_list = []

for file in files:
    csv_list.append(pd.read_csv(file))
    name_list.append(file.rsplit("/", 1)[1][:-4])

figs = [time_plot(csv_list, name_list), programs_plot(csv_list, name_list), solved_plot(csv_list, name_list), gt_plot(csv_list, name_list)]

with PdfPages("evaluation/plots/plots.pdf") as pdf:
    for fig in figs:
        pdf.savefig(fig)

# programs_plot([csv_list[1]], [name_list[1]])
