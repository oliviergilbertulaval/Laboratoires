import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from scipy.optimize import curve_fit
from tqdm import tqdm

h = 6.62607015E-34 #m^2.kg.s^-1
c = 299792458 #m/s
k_B = 1.380649E-23 #m^2.kg.s^-2.K^-1
b = 2.897771955E-3 #m.K

fit_degree = 22


def planckslaw_radiance(wav, temp):
    wav = wav*10**(-9)
    return 2*h*c**2/wav**5*(1/(np.exp(h*c/(wav*k_B*temp))-1))

#Get the blackbodies for all temperatures in this range (which we expect the stars to be)
wavelengths = np.linspace(7, 1007, 1000)
blackbodies = []
blackbodies_temp = []
for t in range(3000, 13000):
    blackbodies.append(planckslaw_radiance(wavelengths, t))
    blackbodies_temp.append(t)


def show_blackbody(temp):
    plt.plot(wavelengths, blackbodies[temp-3000], label=f'T={blackbodies_temp[temp-3000]}K')
    plt.legend()
    plt.xlabel('$\lambda$ [nm]')
    plt.show()

#show_blackbody(5772) #T from 3000K-8000K

#Fit QE curves of ZWO ASI 224mc color:
def polynomial(x,coeffs):
    res = 0
    deg = len(coeffs)-1
    for i in range(len(coeffs)):
        res += coeffs[i]*x**(deg-i)
    return res

x_fit = np.linspace(400, 900, 1000)
#RED
red_file = pd.read_csv("PHY-2006/Projet1/data/stars_pictures/red_QE_curve.csv", delimiter=",", decimal=".", skiprows=1, encoding='latin-1', engine='python')
red_wav = np.array(red_file.iloc[:, 0])
red_QE = np.array(red_file.iloc[:, 1])

resr = np.polyfit(red_wav, red_QE, deg=fit_degree)
y_fit_red = polynomial(x_fit, resr)

#GREEN
green_file = pd.read_csv("PHY-2006/Projet1/data/stars_pictures/green_QE_curve.csv", delimiter=",", decimal=".", skiprows=1, encoding='latin-1', engine='python')
green_wav = np.array(green_file.iloc[:, 0])
green_QE = np.array(green_file.iloc[:, 1])

resg = np.polyfit(green_wav, green_QE, deg=fit_degree)
y_fit_green = polynomial(x_fit, resg)

#BLUE
blue_file = pd.read_csv("PHY-2006/Projet1/data/stars_pictures/blue_QE_curve.csv", delimiter=",", decimal=".", skiprows=1, encoding='latin-1', engine='python')
blue_wav = np.array(blue_file.iloc[:, 0])
blue_QE = np.array(blue_file.iloc[:, 1])

resb = np.polyfit(blue_wav, blue_QE, deg=fit_degree)
y_fit_blue = polynomial(x_fit, resb)

ax1 = plt.subplot(111)
ticklabels = ax1.get_xticklabels()
ticklabels.extend( ax1.get_yticklabels() )
for label in ticklabels:
    label.set_fontsize(14)
plt.plot(x_fit, y_fit_red, color='red')
#plt.plot(red_wav, red_QE, '.', color='red')
plt.plot(x_fit, y_fit_green, color='green')
#plt.plot(green_wav, green_QE, '.', color='green')
plt.plot(x_fit, y_fit_blue, color='blue')
#plt.plot(blue_wav, blue_QE, '.', color='blue')
plt.xlabel('Wavelength $\lambda$ [nm]', fontsize=17)
plt.ylabel("Relative response [%]", fontsize=17)
plt.show()


#We calcualte the B/R ratio as a function of the temperature by integrating the multiplication of the blackbody at temperature T with the functions:

B_R_ratio = []
B_G_ratio = []
G_R_ratio = []
B_sum = []
R_sum = []
G_sum = []
for i in tqdm(range(len(blackbodies))):
    b_array = (blackbodies[i]*polynomial(wavelengths, resb[0], resb[1], resb[2], resb[3], resb[4], resb[5], resb[6], resb[7], resb[8], resb[9]))
    r_array = (blackbodies[i]*polynomial(wavelengths, resr[0], resr[1], resr[2], resr[3], resr[4], resr[5], resr[6], resr[7], resr[8], resr[9]))
    g_array = (blackbodies[i]*polynomial(wavelengths, resg[0], resg[1], resg[2], resg[3], resg[4], resg[5], resg[6], resg[7], resg[8], resg[9]))
    B_sum.append(np.sum(b_array[b_array >= 0]))
    R_sum.append(np.sum(r_array[r_array >= 0]))
    G_sum.append(np.sum(g_array[g_array >= 0]))
    B_R_ratio.append(B_sum[i]/R_sum[i])
    B_G_ratio.append(B_sum[i]/G_sum[i])
    G_R_ratio.append(G_sum[i]/R_sum[i])

ax1 = plt.subplot(111)
ticklabels = ax1.get_xticklabels()
ticklabels.extend( ax1.get_yticklabels() )
for label in ticklabels:
    label.set_fontsize(14)
plt.plot(blackbodies_temp, B_R_ratio)
plt.xlabel('Température [K]', fontsize=17)
plt.ylabel("Ratio B/R", fontsize=17)
plt.show()

if False:
    ax1 = plt.subplot(111)
    ticklabels = ax1.get_xticklabels()
    ticklabels.extend( ax1.get_yticklabels() )
    for label in ticklabels:
        label.set_fontsize(14)
    plt.plot(blackbodies_temp, B_G_ratio)
    plt.xlabel('Température [K]', fontsize=17)
    plt.ylabel("Ratio B/G", fontsize=17)
    plt.show()

    ax1 = plt.subplot(111)
    ticklabels = ax1.get_xticklabels()
    ticklabels.extend( ax1.get_yticklabels() )
    for label in ticklabels:
        label.set_fontsize(14)
    plt.plot(blackbodies_temp, G_R_ratio)
    plt.xlabel('Température [K]', fontsize=17)
    plt.ylabel("Ratio G/R", fontsize=17)
    plt.show()

#Fit function to BR ratio
def fonc_fit(x, c1, c2, c3, c4, c5, c6):
    return c1+c2*x+c3*x**2+c4*x**3+c5*x**4+c6*x**5
ratio_fit = curve_fit(fonc_fit, B_R_ratio, blackbodies_temp)[0]

temps_sim = []
for i in range(len(B_R_ratio)):
    temps_sim.append(fonc_fit(B_R_ratio[i], ratio_fit[0], ratio_fit[1], ratio_fit[2], ratio_fit[3], ratio_fit[4], ratio_fit[5]))



ax1 = plt.subplot(121)
ax2 = plt.subplot(122)
ticklabels = ax1.get_xticklabels()
ticklabels.extend( ax1.get_yticklabels() )
ticklabels.extend( ax2.get_xticklabels() )
ticklabels.extend( ax2.get_yticklabels() )
for label in ticklabels:
    label.set_fontsize(14)
ax1.plot(B_R_ratio, blackbodies_temp, label='Fonction')
ax1.plot(B_R_ratio, temps_sim, label='Ajustement')
ax1.set_ylabel('Température [K]', fontsize=17)
ax1.set_xlabel("Ratio B/R", fontsize=17)
ax1.legend()

ax2.plot(B_R_ratio, np.array(temps_sim)-np.array(blackbodies_temp))
ax2.set_ylabel('Résiduel [K]', fontsize=17)
ax2.set_xlabel("Ratio B/R", fontsize=17)
plt.show()

print(ratio_fit)