import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from matplotlib import rcParams

flag_filter = False
flag_summarise = False
csv_list = []
name_list = []

filter = ['tests-examples/textbook/1', 'tests-examples/textbook/10', 'tests-examples/textbook/14', 'tests-examples/textbook/15', 'tests-examples/textbook/16', 'tests-examples/textbook/17', 'tests-examples/textbook/19', 'tests-examples/textbook/2', 'tests-examples/textbook/20', 'tests-examples/textbook/21', 'tests-examples/textbook/22', 'tests-examples/textbook/23', 'tests-examples/textbook/24', 'tests-examples/textbook/25', 'tests-examples/textbook/26', 'tests-examples/textbook/28', 'tests-examples/textbook/29', 'tests-examples/textbook/3', 'tests-examples/textbook/31', 'tests-examples/textbook/35', 'tests-examples/textbook/4', 'tests-examples/textbook/5', 'tests-examples/textbook/6', 'tests-examples/textbook/8', 'tests-examples/textbook/9', 'tests-examples/scythe/top_rated_posts/002', 'tests-examples/scythe/top_rated_posts/013', 'tests-examples/scythe/top_rated_posts/017', 'tests-examples/scythe/top_rated_posts/025', 'tests-examples/scythe/top_rated_posts/031', 'tests-examples/scythe/top_rated_posts/032', 'tests-examples/scythe/top_rated_posts/038', 'tests-examples/scythe/top_rated_posts/043', 'tests-examples/scythe/recent_posts/004', 'tests-examples/scythe/recent_posts/016', 'tests-examples/scythe/recent_posts/019', 'tests-examples/scythe/recent_posts/021', 'tests-examples/scythe/recent_posts/028', 'tests-examples/scythe/recent_posts/031', 'tests-examples/scythe/recent_posts/040', 'tests-examples/scythe/recent_posts/046', 'tests-examples/spider/architecture/0007', 'tests-examples/spider/architecture/0008', 'tests-examples/spider/architecture/0009', 'tests-examples/spider/architecture/0011', 'tests-examples/spider/architecture/0012', 'tests-examples/spider/architecture/0013', 'tests-examples/spider/architecture/0017']
summarise = ['tests-examples/textbook/10', 'tests-examples/textbook/14', 'tests-examples/textbook/15', 'tests-examples/textbook/17', 'tests-examples/textbook/18', 'tests-examples/textbook/22', 'tests-examples/textbook/25', 'tests-examples/textbook/3', 'tests-examples/textbook/4', 'tests-examples/textbook/5', 'tests-examples/textbook/6', 'tests-examples/textbook/7', 'tests-examples/textbook/8', 'tests-examples/textbook/9', 'tests-examples/scythe/top_rated_posts/001', 'tests-examples/scythe/top_rated_posts/002', 'tests-examples/scythe/top_rated_posts/004', 'tests-examples/scythe/top_rated_posts/005', 'tests-examples/scythe/top_rated_posts/006', 'tests-examples/scythe/top_rated_posts/007', 'tests-examples/scythe/top_rated_posts/008', 'tests-examples/scythe/top_rated_posts/009', 'tests-examples/scythe/top_rated_posts/011', 'tests-examples/scythe/top_rated_posts/012', 'tests-examples/scythe/top_rated_posts/013', 'tests-examples/scythe/top_rated_posts/014', 'tests-examples/scythe/top_rated_posts/016', 'tests-examples/scythe/top_rated_posts/019', 'tests-examples/scythe/top_rated_posts/021', 'tests-examples/scythe/top_rated_posts/027', 'tests-examples/scythe/top_rated_posts/028', 'tests-examples/scythe/top_rated_posts/029', 'tests-examples/scythe/top_rated_posts/034', 'tests-examples/scythe/top_rated_posts/036', 'tests-examples/scythe/top_rated_posts/037', 'tests-examples/scythe/top_rated_posts/038', 'tests-examples/scythe/top_rated_posts/043', 'tests-examples/scythe/top_rated_posts/047', 'tests-examples/scythe/top_rated_posts/048', 'tests-examples/scythe/top_rated_posts/049', 'tests-examples/scythe/top_rated_posts/051', 'tests-examples/scythe/top_rated_posts/055', 'tests-examples/scythe/top_rated_posts/057', 'tests-examples/scythe/recent_posts/007', 'tests-examples/scythe/recent_posts/009', 'tests-examples/scythe/recent_posts/011', 'tests-examples/scythe/recent_posts/012', 'tests-examples/scythe/recent_posts/016', 'tests-examples/scythe/recent_posts/032', 'tests-examples/scythe/recent_posts/040', 'tests-examples/scythe/recent_posts/045', 'tests-examples/scythe/recent_posts/051', 'tests-examples/spider/architecture/0003', 'tests-examples/spider/architecture/0009', 'tests-examples/spider/architecture/0011']


def greater_than(datas):
    big = datas[0]
    small = datas[1]
    for n in range(len(big)):
        if (float(big.real[n]) + 5) < float(small.real[n]):
            print(big.name[n])


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


#################### FILES ####################

dir = "evaluation/data/"
# files = ["evaluation/data/textbook-no_sketch.csv", "evaluation/data/on/off_no_children.csv", "evaluation/data/on/on_no_children.csv", "evaluation/data/on/off_no_children_all_constraints.csv", "evaluation/data/on/off_no_children_constraints.csv"]
# files = [dir+"st-no_sketch.csv", dir+"st-no_children.csv", dir+"st-no_root.csv"]
# files = [dir+"st-no_sketch.csv", dir+"st-no_sketch_no_out_ctr.csv", dir+"st-no_sketch_no_out_ctr_new_opt.csv"]
# files = [dir+"st-no_sketch_no_out_ctr_new_opt.csv", dir+"st-sketch_no_children_ctr_new_opt.csv", dir+"st-no_sketch_no_children_ctr_new_opt_flag.csv", dir+"new_no_children_off.csv", dir+"new_no_children_on.csv", dir+"new_no_sketch.csv", dir+"new_no_sketch_both.csv", dir+"new_no_children_on_both.csv", dir+"new_no_children_off_both.csv"]
files = [dir+'no_sketch.csv', dir+'Off/no_children.csv', dir+'Off/no_root.csv', dir+'On/no_children_on.csv', dir+'On/no_root_on.csv']

out_file = "plots"

# flag_filter = True
# flag_summarise = True


################# PREPARATIONS #################

if flag_filter:
    files = [dir + 'no_sketch.csv', dir + 'On/no_children_on.csv', dir + 'On/no_root_on.csv', dir + 'On/Filter/no_filter_on.csv', dir + 'On/Filter/only_filter_on.csv']
    out_file = "filter"
elif flag_summarise:
    files = [dir + 'no_sketch.csv', dir + 'On/no_children_on.csv', dir + 'On/no_root_on.csv', dir + 'On/Summarise/no_summarise_on.csv', dir+'On/Summarise/only_summarise_on.csv']
    out_file = "summarise"


for file in files:
    csv_list.append(pd.read_csv(file))
    name_list.append(file.rsplit("/", 1)[1][:-4])


if flag_filter:
    new_list = []
    for data in csv_list:
        new_list.append(data[data.name.isin(filter)])
    csv_list = new_list

elif flag_summarise:
    new_list = []
    for data in csv_list:
        new_list.append(data[data.name.isin(summarise)])
    csv_list = new_list


##################### RUN #####################

# greater_than(csv_list)

sol = check(csv_list, name_list)
if sol[0]:
    print("There are errors in csv: " + sol[1])
else:
    figs = [time_plot(csv_list, name_list), programs_plot(csv_list, name_list), solved_plot(csv_list, name_list), gt_plot(csv_list, name_list)]

    with PdfPages("evaluation/plots/"+out_file+".pdf") as pdf:
        for fig in figs:
            pdf.savefig(fig)
