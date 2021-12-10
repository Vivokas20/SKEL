import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from matplotlib import rcParams
import numpy as np

flag_filter = False
flag_summarise = False
flag_both = False
flag_union = False
csv_list = []
name_list = []

filter = ['tests-examples/textbook/1', 'tests-examples/textbook/10', 'tests-examples/textbook/14', 'tests-examples/textbook/15', 'tests-examples/textbook/16', 'tests-examples/textbook/17', 'tests-examples/textbook/19', 'tests-examples/textbook/2', 'tests-examples/textbook/20', 'tests-examples/textbook/21', 'tests-examples/textbook/22', 'tests-examples/textbook/23', 'tests-examples/textbook/24', 'tests-examples/textbook/25', 'tests-examples/textbook/26', 'tests-examples/textbook/28', 'tests-examples/textbook/29', 'tests-examples/textbook/3', 'tests-examples/textbook/31', 'tests-examples/textbook/35', 'tests-examples/textbook/4', 'tests-examples/textbook/5', 'tests-examples/textbook/6', 'tests-examples/textbook/8', 'tests-examples/textbook/9', 'tests-examples/scythe/top_rated_posts/002', 'tests-examples/scythe/top_rated_posts/013', 'tests-examples/scythe/top_rated_posts/017', 'tests-examples/scythe/top_rated_posts/025', 'tests-examples/scythe/top_rated_posts/031', 'tests-examples/scythe/top_rated_posts/032', 'tests-examples/scythe/top_rated_posts/038', 'tests-examples/scythe/top_rated_posts/043', 'tests-examples/scythe/recent_posts/004', 'tests-examples/scythe/recent_posts/016', 'tests-examples/scythe/recent_posts/019', 'tests-examples/scythe/recent_posts/021', 'tests-examples/scythe/recent_posts/028', 'tests-examples/scythe/recent_posts/031', 'tests-examples/scythe/recent_posts/040', 'tests-examples/scythe/recent_posts/046', 'tests-examples/spider/architecture/0007', 'tests-examples/spider/architecture/0008', 'tests-examples/spider/architecture/0009', 'tests-examples/spider/architecture/0011', 'tests-examples/spider/architecture/0012', 'tests-examples/spider/architecture/0013', 'tests-examples/spider/architecture/0017']
summarise = ['tests-examples/textbook/10', 'tests-examples/textbook/14', 'tests-examples/textbook/15', 'tests-examples/textbook/17', 'tests-examples/textbook/18', 'tests-examples/textbook/22', 'tests-examples/textbook/25', 'tests-examples/textbook/4', 'tests-examples/textbook/5', 'tests-examples/textbook/6', 'tests-examples/textbook/7', 'tests-examples/textbook/8', 'tests-examples/textbook/9', 'tests-examples/scythe/top_rated_posts/001', 'tests-examples/scythe/top_rated_posts/002', 'tests-examples/scythe/top_rated_posts/004', 'tests-examples/scythe/top_rated_posts/006', 'tests-examples/scythe/top_rated_posts/007', 'tests-examples/scythe/top_rated_posts/008', 'tests-examples/scythe/top_rated_posts/009', 'tests-examples/scythe/top_rated_posts/012', 'tests-examples/scythe/top_rated_posts/013', 'tests-examples/scythe/top_rated_posts/014', 'tests-examples/scythe/top_rated_posts/016', 'tests-examples/scythe/top_rated_posts/019', 'tests-examples/scythe/top_rated_posts/021', 'tests-examples/scythe/top_rated_posts/027', 'tests-examples/scythe/top_rated_posts/028', 'tests-examples/scythe/top_rated_posts/029', 'tests-examples/scythe/top_rated_posts/034', 'tests-examples/scythe/top_rated_posts/036', 'tests-examples/scythe/top_rated_posts/037', 'tests-examples/scythe/top_rated_posts/038', 'tests-examples/scythe/top_rated_posts/043', 'tests-examples/scythe/top_rated_posts/047', 'tests-examples/scythe/top_rated_posts/048', 'tests-examples/scythe/top_rated_posts/049', 'tests-examples/scythe/top_rated_posts/051', 'tests-examples/scythe/top_rated_posts/055', 'tests-examples/scythe/top_rated_posts/057', 'tests-examples/scythe/recent_posts/009', 'tests-examples/scythe/recent_posts/011', 'tests-examples/scythe/recent_posts/016', 'tests-examples/scythe/recent_posts/040', 'tests-examples/scythe/recent_posts/045', 'tests-examples/scythe/recent_posts/051', 'tests-examples/spider/architecture/0003', 'tests-examples/spider/architecture/0009', 'tests-examples/spider/architecture/0011']
both = ['tests-examples/textbook/15', 'tests-examples/scythe/recent_posts/021', 'tests-examples/spider/architecture/0009', 'tests-examples/textbook/4', 'tests-examples/scythe/top_rated_posts/002', 'tests-examples/textbook/29', 'tests-examples/textbook/8', 'tests-examples/textbook/25', 'tests-examples/scythe/top_rated_posts/038', 'tests-examples/scythe/recent_posts/004', 'tests-examples/textbook/2', 'tests-examples/textbook/26', 'tests-examples/textbook/14', 'tests-examples/scythe/top_rated_posts/017', 'tests-examples/scythe/top_rated_posts/013', 'tests-examples/scythe/top_rated_posts/043', 'tests-examples/textbook/10', 'tests-examples/textbook/23', 'tests-examples/textbook/22', 'tests-examples/textbook/9', 'tests-examples/textbook/5', 'tests-examples/scythe/recent_posts/028', 'tests-examples/textbook/17', 'tests-examples/textbook/6', 'tests-examples/scythe/recent_posts/016', 'tests-examples/scythe/recent_posts/040', 'tests-examples/spider/architecture/0011', 'tests-examples/textbook/3']
union = ['tests-examples/scythe/top_rated_posts/029', 'tests-examples/textbook/29', 'tests-examples/textbook/31', 'tests-examples/textbook/4', 'tests-examples/textbook/21', 'tests-examples/textbook/28', 'tests-examples/textbook/15', 'tests-examples/textbook/20', 'tests-examples/scythe/recent_posts/045', 'tests-examples/scythe/top_rated_posts/057', 'tests-examples/spider/architecture/0009', 'tests-examples/scythe/recent_posts/016', 'tests-examples/scythe/top_rated_posts/031', 'tests-examples/scythe/top_rated_posts/013', 'tests-examples/scythe/top_rated_posts/027', 'tests-examples/spider/architecture/0007', 'tests-examples/scythe/recent_posts/051', 'tests-examples/scythe/recent_posts/021', 'tests-examples/scythe/top_rated_posts/036', 'tests-examples/scythe/top_rated_posts/007', 'tests-examples/scythe/recent_posts/028', 'tests-examples/scythe/top_rated_posts/038', 'tests-examples/scythe/recent_posts/004', 'tests-examples/scythe/top_rated_posts/021', 'tests-examples/scythe/top_rated_posts/037', 'tests-examples/scythe/top_rated_posts/051', 'tests-examples/textbook/8', 'tests-examples/spider/architecture/0003', 'tests-examples/textbook/16', 'tests-examples/scythe/top_rated_posts/016', 'tests-examples/scythe/top_rated_posts/048', 'tests-examples/scythe/top_rated_posts/028', 'tests-examples/scythe/top_rated_posts/004', 'tests-examples/textbook/3', 'tests-examples/scythe/top_rated_posts/006', 'tests-examples/scythe/recent_posts/009', 'tests-examples/scythe/top_rated_posts/009', 'tests-examples/textbook/9', 'tests-examples/textbook/2', 'tests-examples/scythe/top_rated_posts/017', 'tests-examples/spider/architecture/0011', 'tests-examples/textbook/19', 'tests-examples/scythe/recent_posts/046', 'tests-examples/textbook/14', 'tests-examples/scythe/recent_posts/040', 'tests-examples/scythe/recent_posts/019', 'tests-examples/textbook/24', 'tests-examples/spider/architecture/0012', 'tests-examples/textbook/25', 'tests-examples/textbook/5', 'tests-examples/scythe/top_rated_posts/001', 'tests-examples/spider/architecture/0013', 'tests-examples/textbook/1', 'tests-examples/scythe/top_rated_posts/049', 'tests-examples/textbook/23', 'tests-examples/textbook/17', 'tests-examples/scythe/recent_posts/011', 'tests-examples/scythe/top_rated_posts/012', 'tests-examples/scythe/top_rated_posts/032', 'tests-examples/textbook/10', 'tests-examples/scythe/recent_posts/031', 'tests-examples/scythe/top_rated_posts/047', 'tests-examples/textbook/7', 'tests-examples/scythe/top_rated_posts/019', 'tests-examples/scythe/top_rated_posts/008', 'tests-examples/textbook/26', 'tests-examples/scythe/top_rated_posts/025', 'tests-examples/textbook/6', 'tests-examples/scythe/top_rated_posts/043', 'tests-examples/scythe/top_rated_posts/014', 'tests-examples/textbook/22', 'tests-examples/scythe/top_rated_posts/002', 'tests-examples/textbook/18', 'tests-examples/scythe/top_rated_posts/034', 'tests-examples/scythe/top_rated_posts/055', 'tests-examples/spider/architecture/0008', 'tests-examples/textbook/35', 'tests-examples/spider/architecture/0017']


def greater_than(datas):        # 1st data that must take the longest
    big = datas[0]
    small = datas[1]
    big = big[big.name.isin(small.name)].reset_index(drop=True)
    small = small[small.name.isin(big.name)].reset_index(drop=True)

    for n in big.index:
        if (float(big.real[n]) + 5) < float(small.real[n]):
            print(big.name[n])

def miscellaneous(datas):        # 1st data that must take the longest
    no_opt = datas[0]
    opt = datas[1]

    a = no_opt[(no_opt.timeout == False) & (no_opt.ground_truth == True)]
    b = opt[(opt.timeout == False) & (opt.ground_truth == True)]
    c = a[a.name.isin(b.name)]
    d = a[~a.name.isin(b.name)]

    print(len(a))
    print(len(b))
    print(len(c))
    print(d)

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


        fig = df.plot(label= names[n], xlabel="#Solved Instances", ylabel="Real Time (s)", x="index", y="real", style='.-', subplots=False, ax=ax)
        fig.set_ylim(-2,100)    # baseline / filter
        fig.set_ylim(-1, 50)    # summarise
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

        fig = df.plot(label= names[n], xlabel="#Solved Instances", ylabel="#Attempted programs", x="index", y="programs", style='.-', subplots=False, ax=ax)
        fig.set_ylim(-100, 2000)    # baseline/summarise
        # fig.set_ylim(-100, 4000)  # filter

        # fig.yaxis.set_major_formatter(mtick.PercentFormatter())
        # fig = df.plot(label=names[n], xlabel="Instance", ylabel="Attempted programs", x="name", y="programs", subplots=False, ax=ax)

    fig = fig.get_figure()
    return fig

def ground_truth(datas, names):
    index = []
    solved = []
    gtruth = []

    for n in range(len(datas)):
        data = datas[n]
        df = data[data.timeout == False]
        df2 = data[data.ground_truth == True]
        name = names[n]
        if name.endswith("aggregate"):
            name = name[:-9] + "\n" + name[-9:]
        name = name[:14] + "\n" + name[14:]
        index.append(name)
        solved.append(len(df.index))
        gtruth.append(len(df2.index))


    df = pd.DataFrame({"solved": solved, "correct": gtruth}, index=index)

    rcParams.update({'figure.autolayout': True})
    fig = df.plot(kind="bar", xlabel="Benchmark", ylabel="#Solved Instances", rot=0)  # figsize = (6.4, 4.8)

    for p in fig.patches:
        fig.annotate(str(p.get_height()), (p.get_x() + p.get_width()/2, p.get_height() * 1.005), ha="center")

    # fig.legend(loc=(0.004,0.875))
    fig.legend(loc="lower left")

    fig = fig.get_figure()
    return fig

def solved_plot(datas, names):
    fig, ax = plt.subplots()

    index = []
    values = []

    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    for n in range(len(datas)):
        df = datas[n]
        index.append(names[n])

        if n == 0:
            common = df[df.timeout == False]
        else:
            common_names = df[df.timeout == False].name
            common = common[common.name.isin(common_names)]

        tp = len(df[(df.timeout == False) & (df.ground_truth == True)])
        fp = len(df[(df.timeout == False) & (df.ground_truth == False)])
        fn = len(df[df.timeout == True])

        values.append([round(tp/(tp+fp+fn), 4), round(tp/(tp+fp), 4), round(tp/(tp+fn), 4)])

    for n in range(len(datas)):
        df = datas[n][datas[n].name.isin(common.name)]
        avg_time = df['real'].mean()
        avg_programs = df['programs'].mean()
        values[n].append(round(avg_time, 4))
        values[n].append(round(avg_programs, 4))
        values[n].append(len(datas[n][datas[n].timeout == False]))


    ax.table(cellText=values, rowLabels=index, colLabels=["Accuracy", "Precision", "Recall", "Real", "Programs", "Solved"], loc='center')

    fig.tight_layout()

    fig = fig.get_figure()
    return fig


#################### FILES ####################

dir = "evaluation/data/"
# files = ["evaluation/data/textbook-no_sketch.csv", "evaluation/data/on/off_no_children.csv", "evaluation/data/on/on_no_children.csv", "evaluation/data/on/off_no_children_all_constraints.csv", "evaluation/data/on/off_no_children_constraints.csv"]
# files = [dir+"st-no_sketch.csv", dir+"st-no_children.csv", dir+"st-no_root.csv"]
# files = [dir+"st-no_sketch.csv", dir+"st-no_sketch_no_out_ctr.csv", dir+"st-no_sketch_no_out_ctr_new_opt.csv"]
# files = [dir+"st-no_sketch_no_out_ctr_new_opt.csv", dir+"st-sketch_no_children_ctr_new_opt.csv", dir+"st-no_sketch_no_children_ctr_new_opt_flag.csv", dir+"new_no_children_off.csv", dir+"new_no_children_on.csv", dir+"new_no_sketch.csv", dir+"new_no_sketch_both.csv", dir+"new_no_children_on_both.csv", dir+"new_no_children_off_both.csv"]

files = [dir+'no_sketch.csv', dir+'New/Off/no_children_off.csv', dir+'New/On/no_children_on.csv', dir+'New/Off/no_root_off.csv', dir+'New/On/no_root_on.csv']
out_file = "plots"

############ Baseline ##################
files = [dir+'no_sketch.csv', dir+'New/Off/no_children_off.csv', dir+'New/Off/no_root_off.csv']
name_list = ["No sketch", "Sketch with no children", "Sketch with no root"]
out_file = "Tese/baseline"

############ Optimization ################
files = [dir+'New/Off/no_children_off.csv', dir+'New/On/no_children_on.csv', dir+'New/Off/no_root_off.csv', dir+'New/On/no_root_on.csv']
name_list = ["Sketch with no children", "Sketch with no children optimized", "Sketch with no root", "Sketch with no root optimized"]
out_file = "Tese/baseline_optimization"

# files = [dir+'New/Off/no_children_off.csv', dir+'New/On/no_children_on.csv']
# name_list = ["Sketch with no children", "Sketch with no children optimized"]
# out_file = "Tese/baseline_optimization_children"

# files = [dir+'New/Off/no_root_off.csv', dir+'New/On/no_root_on.csv']
# name_list = ["Sketch with no root", "Sketch with no root optimized"]
# out_file = "Tese/baseline_optimization_roots"



# flag_filter = True
# flag_summarise = True
# flag_both = True
# flag_union = True


################# PREPARATIONS #################

if flag_filter:
    # files = [dir + 'no_sketch.csv', dir + 'New/On/no_children_on.csv', dir + 'New/On/no_root_on.csv', dir + 'New/On/Filter/no_filter_on.csv', dir + 'New/On/Filter/only_filter_on.csv']
    # files = [dir + 'no_sketch.csv', dir + 'New/Off/no_children_off.csv', dir + 'New/Off/no_root_off.csv', dir + 'New/Off/Filter/no_filter_off.csv', dir + 'New/Off/Filter/only_filter_off.csv']
    # out_file = "filter_on"
    # out_file = "filter_off"

    files = [dir + 'New/On/no_children_on.csv', dir + 'New/On/Filter/no_root_no_filter_on.csv', dir + 'New/On/Filter/no_child_only_filter_on.csv', dir+'New/On/no_root_on.csv']
    name_list = ["Sketch with no children", "Sketch with no root and no filter", "Sketch with no children except filter", "Sketch with no root"]
    out_file = "Tese/only_filter_optimized"
elif flag_summarise:
    # files = [dir + 'no_sketch.csv', dir + 'New/On/no_children_on.csv', dir + 'New/On/no_root_on.csv', dir + 'New/On/Summarise/no_summarise_on.csv', dir+'New/On/Summarise/only_summarise_on.csv']
    # files = [dir + 'no_sketch.csv', dir + 'New/Off/no_children_off.csv', dir + 'New/Off/no_root_off.csv', dir + 'New/Off/Summarise/no_summarise_off.csv', dir + 'New/Off/Summarise/only_summarise_off.csv']
    # out_file = "summarise_on"
    # out_file = "summarise_off"

    files = [dir + 'New/On/no_children_on.csv', dir + 'New/On/Summarise/no_root_no_summarise_on.csv', dir + 'New/On/Summarise/no_child_only_summarise.csv', dir+'New/On/no_root_on.csv']
    name_list = ["Sketch with no children", "Sketch with no root and no aggregate", "Sketch with no children except aggregate", "Sketch with no root"]
    out_file = "Tese/only_summarise_optimized"
elif flag_both:
    files = [dir + 'New/On/no_children_on.csv', dir + 'New/On/Both/no_root_no_both_on.csv', dir + 'New/On/Both/sketch_no_child_only_both_on.csv', dir + 'New/On/no_root_on.csv']
    # name_list = ["Sketch with no children", "Sketch with no root and no aggregate", "Sketch with no children except aggregate", "Sketch with no root"]
    out_file = "only_both_optimized"
elif flag_union:
    files = [dir + 'New/On/no_children_on.csv', dir + 'New/On/Union/no_root_no_union_on.csv', dir + 'New/On/Union/sketch_no_child_only_both_on.csv', dir + 'New/On/no_root_on.csv']
    # name_list = ["Sketch with no children", "Sketch with no root and no aggregate", "Sketch with no children except aggregate", "Sketch with no root"]
    out_file = "only_union_optimized"


for file in files:
    csv_list.append(pd.read_csv(file))
if not name_list:
    for file in files:
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

elif flag_both:
    new_list = []
    for data in csv_list:
        new_list.append(data[data.name.isin(both)])
    csv_list = new_list

elif flag_union:
    new_list = []
    for data in csv_list:
        new_list.append(data[data.name.isin(union)])
    csv_list = new_list

##################### RUN #####################

miscellaneous(csv_list)

# sol = check(csv_list, name_list)
# if sol[0]:
#     print("There are errors in csv: " + sol[1])
# else:
#     figs = [time_plot(csv_list, name_list), programs_plot(csv_list, name_list), ground_truth(csv_list, name_list), solved_plot(csv_list, name_list)]
#
#     with PdfPages("evaluation/plots/"+out_file+".pdf") as pdf:
#         for fig in figs:
#             pdf.savefig(fig)
