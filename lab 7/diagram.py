import matplotlib.pyplot as plt


def plot(score, average_score):
    plt.clf()                   # clear current figure
    plt.title('stata')
    plt.xlabel('Games')
    plt.ylabel('Points')
    plt.plot(score)
    plt.plot(average_score)
    plt.ylim(ymin = 0)
    plt.text(len(score) - 1, score[-1], str(score[-1]))
    plt.text(len(average_score) - 1, average_score[-1], str(average_score[-1]))
    plt.show(block = False)     # show and continue game
    plt.pause(.5)