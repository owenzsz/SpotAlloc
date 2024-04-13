import numpy as np
import matplotlib.pyplot as plt

# Data for each category
credit = np.array([4945.6, 5123.9, 4985.7, 5309.4, 5745.6])
maxmin = np.array([5135.2, 6470.4, 6189.2, 5009.1, 5531.0])
fair = np.array([0, 0, 0, 0, 0])

# Calculate means and standard deviations
means = [np.mean(credit), np.mean(maxmin), np.mean(fair)]
stds = [np.std(credit), np.std(maxmin), np.std(fair)]

# Set up the bar labels and colors
labels = ['Credit', 'MaxMin', 'Fair']
colors = ['blue', 'green', 'red']  # Specify colors here

# Creating the bar plot
x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects = ax.bar(x, means, width, yerr=stds, capsize=5, color=colors)

# Add some text for labels, title, and custom x-axis tick labels, etc.
ax.set_ylabel('Values')
ax.set_title('Values and SD by Category')
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
