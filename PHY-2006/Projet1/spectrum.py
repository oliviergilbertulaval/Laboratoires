import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

h = 6.62607015E-34 #m^2.kg.s^-1
c = 299792458 #m/s
k_B = 1.380649E-23 #m^2.kg.s^-2.K^-1
b = 2.897771955E-3 #m.K


def open_spectrum(filepath):
    file = pd.read_csv(filepath, delimiter="\t", decimal=",", skiprows=14, encoding='latin-1', engine='python')
    wavelengths = np.array(file.iloc[:, 0])
    counts = np.array(file.iloc[:, 1])
    density = counts/np.max(counts)
    return wavelengths, counts, density

def sensitivity(wav):
    '''Returns the photons/count for a wavelength'''
    return 86

#Start with the atmosphere
atm_wav_list, atm_counts_list, atm_energydensity_list = [], [], []
for i in range(1, 5):
    w, cts, d = open_spectrum(f'PHY-2006/Projet1/data/atmosphere/atmo{i}.txt')
    atm_wav_list.append(w)
    atm_counts_list.append(cts)
    atm_energydensity_list.append(d)

atm_wav = np.mean(atm_wav_list, axis=0)
atm_counts = np.mean(atm_counts_list, axis=0)/100
atm_energydensity = np.mean(atm_energydensity_list, axis=0)

#Start with the sun
sun_wav_list, sun_counts_list, sun_energydensity_list = [], [], []

for i in range(11, 16):
    w, cts, d = open_spectrum(f'PHY-2006/Projet1/data/sun/sun{i}.txt')
    sun_wav_list.append(w)
    sun_counts_list.append(cts)
    sun_energydensity_list.append(d)


sun_wav = np.mean(sun_wav_list, axis=0)
sun_counts = np.mean(sun_counts_list, axis=0)
sun_radiance = []
for i in range(len(sun_wav)):
    #Integration time of 2ms, so we calculate the radiance in W/m^2/nm
    photon_count = sun_counts[i]*sensitivity(sun_wav[i])
    photon_energy = h*c/sun_wav[i]
    sun_radiance.append(photon_count*photon_energy/0.002/(np.pi*(2.5E-6)**2))
sun_energydensity = np.mean(sun_energydensity_list, axis=0)/0.56

ax1 = plt.subplot(111)
ticklabels = ax1.get_xticklabels()
ticklabels.extend( ax1.get_yticklabels() )
for label in ticklabels:
    label.set_fontsize(14)
ax1.plot(sun_wav, sun_radiance, label='Données')
#ax1.plot(atm_wav, atm_counts, label=f'Atmosphère')
plt.xlabel('$\lambda$ [nm]', fontsize=17)
plt.ylabel("Radiance [W/m$^2$/nm]", fontsize=17)
plt.legend(fontsize=14)
plt.show()











def planckslaw(wav, temp):
    wav = wav*10**(-9)
    return 8*np.pi*h*c/wav**5*(1/(np.exp(h*c/(wav*k_B*temp))-1))/865000 #865000 est le max de la fonction pour un corps noir de T=5500K



#Fit Wien's law
wav_peak = sun_wav[np.where(sun_counts == np.max(sun_counts))]
temp_wien = b/(wav_peak*10**(-9))
print('Wavelenght peak [nm]:', wav_peak)
print('Temperature:', temp_wien)
print(b/5778)

wav_sim = np.linspace(200, 1900, 1000)
sed_sim = planckslaw(wav_sim, temp_wien)

#Fit planck's law
from scipy.optimize import curve_fit
if False:
    plt.plot(sun_wav)
    plt.xlabel('Index')
    plt.ylabel('$\lambda$ [nm]')
    plt.show()
temp_experimentale = curve_fit(planckslaw, sun_wav[1600:2500], sun_energydensity[1600:2500], p0=[6500])[0]
temp_experimentale = curve_fit(planckslaw, sun_wav, sun_energydensity, p0=[6500])[0]
sed_fit = planckslaw(wav_sim, temp_experimentale)

ax1 = plt.subplot(111)
ticklabels = ax1.get_xticklabels()
ticklabels.extend( ax1.get_yticklabels() )
for label in ticklabels:
    label.set_fontsize(14)
for i in range(len(sun_wav_list)):
    ax1.plot(sun_wav_list[i], sun_energydensity_list[i], color='purple')
ax1.plot(sun_wav, sun_energydensity, label='Données')

ax1.plot(wav_sim, sed_sim, label=f'Corps noir de $T={round(temp_wien[0])}$K')
ax1.plot(wav_sim, sed_fit, label=f'Corps noir de $T={round(temp_experimentale[0])}$K')
plt.xlabel('$\lambda$ [nm]', fontsize=17)
plt.ylabel("$I/I_\mathrm{max}$", fontsize=17)
plt.legend(fontsize=14)
plt.show()