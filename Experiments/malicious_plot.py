import numpy as np
import matplotlib.pyplot as plt

# Data for each category
credit = np.array([0.05])
credit_no_inflation = np.array([0.1])
maxmin = np.array([0.5])
fair = np.array([0])

# Calculate means and standard deviations
means = [np.mean(credit), np.mean(credit_no_inflation), np.mean(maxmin), np.mean(fair)]
stds = [np.std(credit), np.std(credit_no_inflation), np.std(maxmin), np.std(fair)]

# Set up the bar labels and colors
labels = ['Credit','Credit-No-Inflation', 'MaxMin', 'Fair']
colors = ['blue', 'green','red', 'yellow']  # Specify colors here

# Creating the bar plot
x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects = ax.bar(x, means, width, yerr=stds, capsize=5, color=colors)

# Add some text for labels, title, and custom x-axis tick labels, etc.
ax.set_ylabel('Domination time')
ax.set_title('Domination time for different allocation algorithms')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(rects, labels)

# Function to attach a text label above each bar, displaying its height
def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(round(height, 2)),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects)

plt.show()
