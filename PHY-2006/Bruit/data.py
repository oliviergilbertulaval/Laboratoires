import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm


def get_values_from_file(filename):
    values = pd.read_csv(filename, delimiter="\t", decimal=",", skiprows=0)
    return values

data = []
clusters_of_data = []
data_highs = []
data_lows = []
for k in range(3,7):
    file = get_values_from_file(f'PHY-2006/Bruit/labBruit_{k}.lvm')
    for n in range(6):
        for i, val in enumerate(file.iloc[:, n]):
            if np.isnan(val) or i < 2500 or i > 22500 or val > 0.76:
                pass
            else:
                data.append(val)
for i in range(len(data)):
    if i % 5000 == 0:
        clusters_of_data.append([])
    clusters_of_data[i//5000].append(data[i])

for i in clusters_of_data:
    if np.mean(i) > 0.71:
        data_highs.append(i)
    else:
        data_lows.append(i)
plt.plot(data)
plt.show()
#for i in range(len(clusters_of_data)-1):
#    plt.plot(range(i*5000, (i+1)*5000), clusters_of_data[i])
#plt.plot(range(len(data_highs)), data_highs)
#plt.plot(range(len(data_highs), len(data_highs)+len(data_lows)), data_lows)


#print(np.mean(data_highs), np.mean(data_lows))
allHIGH = []
allLOW = []
for i in data_highs:
    allHIGH.extend(i)
for i in data_lows:
    allLOW.extend(i)
print('BEFORE:')
print('STD low:', np.std(allLOW))
print('STD high:', np.std(allHIGH))
print('--------------------')

ax1, ax2 = plt.subplot(111), plt.subplot(111)


mu1, std1 = norm.fit(allLOW) 
mu2, std2 = norm.fit(allHIGH)



ax1.hist(allLOW, 23, density=True, alpha=0.5, color='b', label='Fermé')
xmin1, xmax1 = ax1.get_xlim()
x1 = np.linspace(xmin1, xmax1, 100)
p1 = norm.pdf(x1, mu1, std1)
ax2.hist(allHIGH, 24, density=True, alpha=0.5, color='r', label='Ouvert')
xmin2, xmax2 = ax2.get_xlim()
x2 = np.linspace(xmin2, xmax2, 100)
p2 = norm.pdf(x2, mu2, std2)

ax1.plot(x1, p1, linewidth=3, color='b', linestyle='dashed')
ax2.plot(x2, p2, linewidth=3, color='r', linestyle='dashed')

ax1.vlines(mu1, 0, 35, linewidth=2, color='b', alpha=0.8, linestyle=(0, (1,1)))
ax2.vlines(mu2, 0, 35, linewidth=2, color='r', alpha=0.8, linestyle=(0, (1,1)))
middle = (mu1+mu2)/2
plt.annotate('', xy=(mu1,35), xytext=(mu2,35), arrowprops=dict(arrowstyle='<->'))
plt.text(middle-0.018, 36, f'$\Delta$V = 0.0381V', fontsize=16)
ax1.set_xlabel(r'Tension (V)', size=17)
ax1.set_ylabel(r'Densité de probabilité normalisée', size=17)
plt.legend()
plt.show()

analyse = []


for i in range(int(len(clusters_of_data)/2)):
    analyse.extend(data_lows[i])
    analyse.extend(data_highs[i])

bas = []
haut = []
for i in range(len(data_lows)):
    bas.extend(data_lows[i])
    haut.extend(data_highs[i])

ecart_bas = []
ecart_haut = []
from tqdm import tqdm
for i in tqdm(range(1,len(bas))):
    ecart_bas.append(np.std(bas[:i]))
    ecart_haut.append(np.std(haut[:i]))

plt.plot(ecart_bas)
plt.plot(ecart_haut)
plt.show()



cycles = [[],]
last_dim = 0

data = analyse[160000:]
plt.plot(data)
plt.show()

for i in range(len(data)):
    dim = int(i // 10000)
    if dim != last_dim:
        cycles.append([])
    cycles[dim].append(data[i])
    last_dim = dim

cycles = cycles[:-1]

ax1 = plt.subplot(131)
ax2 = plt.subplot(132, sharex=ax1, sharey=ax1)
ax3 = plt.subplot(133, sharex=ax1, sharey=ax1)

ax1.plot(data[:10000])
ax1.set_title('Données brutes')
ax2.plot(np.mean(cycles, axis=0))
ax2.set_title(f'Données moyennées sur {last_dim+1} cycles')
ax3.plot(np.median(cycles, axis=0))
ax3.set_title(f'Données "médiannées" sur {last_dim+1} cycles')
plt.show()


low_mean, high_mean = np.mean(np.mean(cycles, axis=0)[200:4500]), np.mean(np.mean(cycles, axis=0)[5200:9500])
low_std, high_std = np.std(np.mean(cycles, axis=0)[200:4500]), np.std(np.mean(cycles, axis=0)[5200:9500])
print('LOW:', low_mean)
print('HIGH:', high_mean)
print('Difference:', high_mean-low_mean)
print('STD low:', low_std)
print('STD high:', high_std)
plt.plot(np.mean(cycles, axis=0)[200:4500])
plt.plot(np.mean(cycles, axis=0)[5200:9500])
plt.hlines([low_mean, high_mean], 0, 4300, linestyles='dashed', colors=['red', 'green'])
plt.fill_between(range(0,4300), low_mean-low_std, low_mean+low_std, color='red', alpha=0.4)
plt.fill_between(range(0,4300), high_mean-high_std, high_mean+high_std, color='green', alpha=0.4)
plt.show()