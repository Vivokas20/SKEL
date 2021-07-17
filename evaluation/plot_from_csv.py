import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from matplotlib import rcParams

####################### Plot Functions ########################

def check(datas, name_list):

    for n in range(len(datas)):
        df = datas[n]
        df = df[df.timeout == False]
        programs = pd.isnull(df.programs)
        programs = programs[programs == True]
        if len(programs) > 0:
            return True, name_list[n]

    return False, None

def time_plot(datas, names):
    fig, ax = plt.subplots()

    for n in range(len(datas)):
        df = datas[n]
        df = df[df.timeout == False]
        df = df.sort_values("real").reset_index(drop=True)
        df.index += 1
        df = df.reset_index()

        fig = df.plot(label= names[n], xlabel="Solved Instances", ylabel="Real Time (s)", x="index", y="real", style='.-', subplots=False, ax=ax)
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

        fig = df.plot(label= names[n], xlabel="Solved Instances", ylabel="Attempted programs", x="index", y="programs", style='.-', subplots=False, ax=ax)
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
    fig = df.plot(kind="barh", xlabel="Benchmark", ylabel="Solved Instances") # figsize = (6.4, 4.8)
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
    fig = df.plot(kind="barh", xlabel="Benchmark", ylabel="Solved Instances") # figsize = (6.4, 4.8)
    fig.get_legend().remove()
    fig = fig.get_figure()
    return fig


# files = ["evaluation/data/textbook-no_sketch.csv", "evaluation/data/on/off_no_children.csv", "evaluation/data/on/on_no_children.csv", "evaluation/data/on/off_no_children_all_constraints.csv", "evaluation/data/on/off_no_children_constraints.csv"]
dir = "evaluation/data/"
# files = [dir+"st-no_sketch.csv", dir+"st-no_children.csv", dir+"st-no_root.csv"]
# files = [dir+"st-no_sketch.csv", dir+"st-no_sketch_no_out_ctr.csv", dir+"st-no_sketch_no_out_ctr_new_opt.csv"]
files = [dir+"st-no_sketch_no_out_ctr_new_opt.csv", dir+"st-sketch_no_children_ctr_new_opt.csv", dir+"st-no_sketch_no_children_ctr_new_opt_flag.csv", dir+"new_no_children_off.csv", dir+"new_no_children_on.csv", dir+"new_no_sketch.csv", dir+"new_no_sketch_both.csv", dir+"new_no_children_on_both.csv", dir+"new_no_children_off_both.csv"]
out_file = "compare_new_opt_max_min"

csv_list = []
name_list = []

for file in files:
    csv_list.append(pd.read_csv(file))
    name_list.append(file.rsplit("/", 1)[1][:-4])

sol = check(csv_list, name_list)
if sol[0]:
    print("There are errors in csv: " + sol[1])
else:
    figs = [time_plot(csv_list, name_list), programs_plot(csv_list, name_list), solved_plot(csv_list, name_list), gt_plot(csv_list, name_list)]

    with PdfPages("evaluation/plots/"+out_file+".pdf") as pdf:
        for fig in figs:
            pdf.savefig(fig)
