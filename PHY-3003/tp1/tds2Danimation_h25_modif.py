#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#GlowScript 3.0 VPython

# Hard-sphere gas.

# Bruce Sherwood
# Claudine Allen
"""


from vpython import *
import numpy as np
import math
import matplotlib.pyplot as plt
import pickle
from scipy.stats import maxwell, norm

# win = 500 # peut aider à définir la taille d'un autre objet visuel comme un histogramme proportionnellement à la taille du canevas.

# Déclaration de variables influençant le temps d'exécution de la simulation
Nelectrons = 200  # change this to have more or fewer electrons
Ncores = 9  # change this to have more or fewer static ionic cores
dt = 2E-8  # pas d'incrémentation temporel (plus petit pour les électrons)

# Déclaration de variables physiques "Typical values"
DIM = 2 #Nombre de degrés de liberté de la simulation 
mass = 9.1E-31 # electron mass
Relectron = 0.01*0.001 # wildly exaggerated size of an electron
Rcore = 0.04 # wildly exaggerated size of a static core
k = 1.4E-23 # Boltzmann constant
k_Boltzmann = 1.4E-23 # Boltzmann constant
T = 300 # around room temperature

#### CANEVAS DE FOND ####
L = 1 # container is a cube L on a side
gray = color.gray(0.7) # color of edges of container and spheres below
blue = color.blue # color of ionic cores
red = color.red # color of ionic cores
animation = canvas( width=750, height=500) # , align='left')
animation.range = L
# animation.title = 'Théorie cinétique des gaz parfaits'
# s = """  Simulation de particules modélisées en sphères dures pour représenter leur trajectoire ballistique avec collisions. Une sphère est colorée et grossie seulement pour l’effet visuel permettant de suivre sa trajectoire plus facilement dans l'animation, sa cinétique est identique à toutes les autres particules.

# """
# animation.caption = s

#### ARÊTES DE BOÎTE 2D ####
d = L/2+Relectron
r = 0.005
cadre = curve(color=gray, radius=r)
cadre.append([vector(-d,-d,0), vector(d,-d,0), vector(d,d,0), vector(-d,d,0), vector(-d,-d,0)])

#### POSITION ET QUANTITÉ DE MOUVEMENT INITIALE DES SPHÈRES ####
Spheres = [] # Objet qui contiendra les sphères pour l'animation
p = [] # quantité de mouvement des sphères
apos = [] # position des sphères
pavg = sqrt(2*mass*(DIM/2)*k*T) # average kinetic energy in 3D p**2/(2mass) = (3/2)kT : Principe de l'équipartition de l'énergie en thermodynamique statistique classique

for i in range(Nelectrons):
    x = L*random()-L/2 # position aléatoire qui tient compte que l'origine est au centre de la boîte
    y = L*random()-L/2
    z = 0
    if i == 0:  # garde une sphère plus grosse et colorée parmis toutes les grises
        Spheres.append(simple_sphere(pos=vector(x,y,z), radius=0.03, color=color.magenta)) #, make_trail=True, retain=100, trail_radius=0.3*Ratom))
    else: Spheres.append(simple_sphere(pos=vector(x,y,z), radius=Relectron*1000, color=blue))
    apos.append(vec(x,y,z)) # liste de la position initiale de toutes les sphères

    # ON UTILISE UNE QTE DE MOUVEMENT DISTRIBUÉE SELON MAXWELL-BOLTZMANN AU LIEU DE L'ÉQUIPARTITION
    v_moy = pavg/mass
    E_moy = np.mean(v_moy**2)*1/2*mass
    E_tot = E_moy*Nelectrons
    Temperature = 2*E_moy/k_Boltzmann/DIM
    p_ini = maxwell.rvs(scale=(k_Boltzmann*Temperature/mass)**0.5, size=1)*mass

#    theta = pi*random() # direction de coordonnées sphériques, superflue en 2D
    phi = 2*pi*random() # direction aléatoire pour la quantité de mouvement
    px = p_ini*cos(phi)  # qte de mvt initiale selon l'équipartition
    py = p_ini*sin(phi)
    pz = 0
    p.append(vector(px,py,pz)) # liste de la quantité de mouvement initiale de toutes les sphères


### ON INITIALISE LES COEURS IONIQUES STATIQUES ###
sides = int(np.sqrt(Ncores))
realNcores = 0
for i in range(sides):
    for k in range(sides):
        realNcores += 1
        x = ((i+0.5)/sides)*L-L/2 # position fixe environ équidistante, mais surtout périodique
        y = ((k+0.5)/sides)*L-L/2
        z = 0
        Spheres.append(simple_sphere(pos=vector(x,y,z), radius=Rcore, color=red))
        apos.append(vec(x,y,z)) # liste de la position initiale de toutes les sphères
        p.append(vector(0,0,0)) # liste de la quantité de mouvement initiale de toutes les sphères
if sides*Rcore*2 >= L:
    raise ValueError("The cores are touching.")
if Ncores != realNcores:
    print(f"Could not place {Ncores} cores periodically, placed {realNcores} instead!")
Ncores = realNcores

### CALCULATE TAU, THE RELAXATION/COLLISION TIME ###
avg_space_between_cores = L/sides # approximation
avg_velocity = pavg/mass
tau_time = avg_space_between_cores/avg_velocity

#initialization = pickle.load(open("PHY-3003/init.pkl", "rb"))
#apos,p = initialization[0], initialization[1]
#initialization = (apos,p)
#pickle.dump(initialization, open("PHY-3003/init.pkl", "wb"))

#### FONCTION POUR IDENTIFIER LES COLLISIONS, I.E. LORSQUE LA DISTANCE ENTRE LES CENTRES DE 2 SPHÈRES EST À LA LIMITE DE S'INTERPÉNÉTRER ####
def checkCollisions():
    hitlist = []   # initialisation
    r2 = Relectron+Rcore   # distance critique où les 2 sphères entre en contact à la limite de leur rayon
    r2 *= r2   # produit scalaire pour éviter une comparaison vectorielle ci-dessous
    for i in range(Nelectrons):
        ai = apos[i]
        for j in range(Nelectrons, Nelectrons+Ncores) :
            aj = apos[j]
            dr = ai - aj   # la boucle dans une boucle itère pour calculer cette distance vectorielle dr entre chaque paire de sphère
            if mag2(dr) < r2:   # test de collision où mag2(dr) qui retourne la norme élevée au carré de la distance intersphère dr
                hitlist.append([i,j]) # liste numérotant toutes les paires de sphères en collision
    
    return hitlist


def follow_particle(deltax, hitlist, deltapos, liste_p, p, liste_temps_entre_collision, liste_distance_entre_collision,liste_distance_x_entre_collision,liste_distance_y_entre_collision,liste_distance_z_entre_collision, n_particle=0, iterations_since_last_col=0):
    """
    n_particle: indice de la particule à suivre
    iterations_since_last_col: nombre d'itérations depuis que la particule a subit une collision
    liste_temps_entre_collision: liste de temps entre les collisions
    liste_distance_entre_collision: liste des distances entre les collisions
    liste_distance_x_entre_collision: liste des distances x entre les collisions
    liste_distance_y_entre_collision: liste des distances y entre les collisions
    liste_distance_z_entre_collision: liste des distances z entre les collisions
    """
    iterations_since_last_col += 1
    deltapos.x += np.abs(deltax[n_particle].x)
    deltapos.y += np.abs(deltax[n_particle].y)
    deltapos.z += np.abs(deltax[n_particle].z)
    particle_hit = False
    #coliisions = []
    for ij in hitlist:
        i,j = ij[0], ij[1]
        if i == n_particle or j == n_particle:
            particle_hit = True
            #coliisions.append([i,j])
    liste_p.append(p[n_particle].mag)
    if particle_hit:
        liste_temps_entre_collision.append(iterations_since_last_col*dt)
        liste_distance_entre_collision.append(deltapos.mag)
        liste_distance_x_entre_collision.append(np.abs(deltapos.x))
        liste_distance_y_entre_collision.append(np.abs(deltapos.y))
        liste_distance_z_entre_collision.append(np.abs(deltapos.z))
        return 0, vector(0,0,0)
    return iterations_since_last_col, deltapos


def champs(module, orientation="x"):
    """
    module: float représentant le module du champ électrique E souhaité
    orientation: string représentant l'orientation souhaitée du champ électrique
    """
    e = q = 1.602*10**(-19)
    module *= e*q
    
    if orientation == 'x':
        force_E = vector(module , 0, 0)
    elif orientation == 'y':
        force_E = vector(0, module , 0)
    else:
        raise ValueError("L'orientation n'est pas bonne. C'est soit 'x' ou 'y'.")
    
    return force_E

#### BOUCLE PRINCIPALE POUR L'ÉVOLUTION TEMPORELLE DE PAS dt ####
## ATTENTION : la boucle laisse aller l'animation aussi longtemps que souhaité, assurez-vous de savoir comment interrompre vous-même correctement (souvent `ctrl+c`, mais peut varier)
## ALTERNATIVE : vous pouvez bien sûr remplacer la boucle "while" par une boucle "for" avec un nombre d'itérations suffisant pour obtenir une bonne distribution statistique à l'équilibre
temps_entre_collision = dt
liste_temps_entre_collision = []
liste_distance_entre_collision = []
liste_distance_x_entre_collision = []
liste_distance_y_entre_collision = []
liste_distance_z_entre_collision = []
liste_p = []
liste_vector_x = []
liste_vector_y = []
iterations_since_last_col = 0
deltapos = vector(0,0,0)
from tqdm import tqdm
p_avg_list = []
liste_temps = []
tau_list = [] # même chose tout le temps, mais plus simple de faire une liste pour l'enregistrer

try:
    liste_tous_les_temps_collision = list(np.loadtxt("PHY-3003/data_tau_pt2.txt"))
except:
    liste_tous_les_temps_collision = []
temps_collision_particule = np.array([0 for i in range(Nelectrons)], dtype=float)

##############

module = 0.05 # valeur testées à date 0.001-0.05-0.01-0.1-0.2-1
module_champs = module*10**(12)

##########
orientation = 'x'
force = champs(module_champs, orientation)
for k in tqdm(range(1000)):

    
    rate(300)  # limite la vitesse de calcul de la simulation pour que l'animation soit visible à l'oeil humain!

    #### DÉPLACE TOUTES LES SPHÈRES D'UN PAS SPATIAL deltax
    vitesse = []   # vitesse instantanée de chaque sphère
    deltax = []  # pas de position de chaque sphère correspondant à l'incrément de temps dt
    temps_collision_particule += dt
    for i in range(Nelectrons):
        p[i]+=force

        vitesse.append(p[i]/mass)   # par définition de la quantité de nouvement pour chaque sphère
        deltax.append(vitesse[i] * dt)   # différence avant pour calculer l'incrément de position

        Spheres[i].pos = apos[i] = apos[i] + deltax[i]  # nouvelle position de l'atome après l'incrément de temps dt

    #### CONSERVE LA QUANTITÉ DE MOUVEMENT AUX COLLISIONS AVEC LES MURS DE LA BOÎTE ####
    for i in range(Nelectrons):
        loc = apos[i]
        if abs(loc.x) > L/2:
            if loc.x < 0: p[i].x =  abs(p[i].x)  # renverse composante x au mur de gauche
            else: p[i].x =  -abs(p[i].x)   # renverse composante x au mur de droite
        if abs(loc.y) > L/2:
            if loc.y < 0: p[i].y = abs(p[i].y)  # renverse composante y au mur du bas
            else: p[i].y =  -abs(p[i].y)  # renverse composante y au mur du haut

    # Calcule l'énergie totale:
    v_moy = np.mean(np.array([vitesse[i].mag for i in range(Nelectrons)]))
    E_moy = np.mean(v_moy**2)*1/2*mass
    E_tot = E_moy*Nelectrons
    Temperature = 2*E_moy/k_Boltzmann/DIM
    #print(v_moy)
    #print(E_moy, E_tot, Temperature)
    x = np.linspace(0, 200000, 1000)
    #print((k_Boltzmann*Temperature/mass)**0.5)
    #plt.plot(x, maxwell.pdf(x,scale=(k_Boltzmann*Temperature/mass)**0.5)**2*mass/k_Boltzmann/DIM)
    #plt.show()

    #### LET'S FIND THESE COLLISIONS!!! ####
    hitlist = checkCollisions()
    #print(hitlist)
    #input()
    #### CONSERVE LA QUANTITÉ DE MOUVEMENT AUX COLLISIONS ENTRE SPHÈRES ####
    for ij in hitlist:
        liste_tous_les_temps_collision.append(temps_collision_particule[i])
        temps_collision_particule[i] = 0

        # définition de nouvelles variables pour chaque paire de sphères en collision
        i = ij[0]  # extraction du numéro des 2 sphères impliquées à cette itération
        j = ij[1]
        posi = apos[i]   # position de chacune des 2 sphères
        posj = apos[j]
        vi = p[i]/mass   # vitesse de chacune des 2 sphères
        vj = p[j]/mass
        rrel = posi-posj  # vecteur pour la distance entre les centres des 2 sphères
        vrel = -vi   # vecteur pour la différence de vitesse entre les 2 sphères

        # exclusion de cas où il n'y a pas de changements à faire
        if vrel.mag2 == 0: continue  # exactly same velocities si et seulement si le vecteur vrel devient nul, la trajectoire des 2 sphères continue alors côte à côte
        if rrel.mag > Rcore: continue  # one atom went all the way through another, la collision a été "manquée" à l'intérieur du pas deltax

        # calcule la distance et temps d'interpénétration des sphères dures qui ne doit pas se produire dans ce modèle
        dx = dot(rrel, vrel.hat)       # rrel.mag*cos(theta) où theta is the angle between vrel and rrel:
        dy = cross(rrel, vrel.hat).mag # rrel.mag*sin(theta)
        alpha = asin(dy/(Relectron+Rcore))  # alpha is the angle of the triangle composed of rrel, path of atom j, and a line from the center of atom i to the center of atom j where atome j hits atom i
        d = (Relectron+Rcore)*cos(alpha)-dx # distance traveled into the atom from first contact
        deltat = d/vrel.mag         # time spent moving from first contact to position inside atom

        #### CHANGE L'INTERPÉNÉTRATION DES SPHÈRES PAR LA CINÉTIQUE DE COLLISION ####
        posi = posi-vi*deltat   # back up to contact configuration


        # On sample aléatoirement la vitesse d'une distribution de Maxwell-Boltzmann à température T
        #p_sampled = norm.rvs(scale=(k_Boltzmann*Temperature/mass)**0.5, size=1)*mass
        p_sampled = maxwell.rvs(scale=(k_Boltzmann*Temperature/mass)**0.5, size=1)*mass


        #rrel = hat(rrel)
        #p[i] = (p[i]-2*dot(p[i],rrel)*rrel)
        #p[i] = (p[i]/p[i].mag*p_sampled)[0] # bounce in center-of-momentum (com) frame

        #print(p[i])
        phi = 2*pi*random() # direction aléatoire pour la quantité de mouvement
        px = p_sampled*cos(phi)  # qte de mvt initiale selon l'équipartition
        py = p_sampled*sin(phi)
        pz = 0
        p[i] = vector(px,py,pz)

        """ rrel = hat(rrel)    # vecteur unitaire aligné avec rrel
        p[i] = p[i]-2*dot(p[i],rrel)*rrel # bounce in center-of-momentum (com) frame
        p[i] = p[i]*np.exp(-deltat/tau_time) # collision inélastique """

        apos[i] = posi+(p[i]/mass)*deltat # move forward deltat in time, ramenant au même temps où sont rendues les autres sphères dans l'itération
    p_avg_list.append(np.mean([p[i].mag for i in range(Nelectrons)]))

    liste_vector_x.append(np.mean([apos[i].x for i in range(Nelectrons)]))
    liste_vector_y.append(np.mean([apos[i].y for i in range(Nelectrons)]))
    liste_temps.append(dt*k)
    tau_list.append(tau_time)
    # **Appel de la fonction suit() ici**
    iterations_since_last_col, deltapos = follow_particle(deltax, hitlist, deltapos, liste_p, p, liste_temps_entre_collision,liste_distance_entre_collision,liste_distance_x_entre_collision, liste_distance_y_entre_collision, liste_distance_z_entre_collision,n_particle=0, iterations_since_last_col=iterations_since_last_col)
np.savetxt("PHY-3003/data_pt2.txt", np.array([liste_temps_entre_collision,liste_distance_entre_collision, liste_distance_x_entre_collision, liste_distance_y_entre_collision, liste_distance_z_entre_collision]).T)
np.savetxt("PHY-3003/data_p_pt2.txt", np.array([liste_temps, tau_list, liste_p, p_avg_list]).T)
np.savetxt("PHY-3003/data_tau_pt2.txt", np.array([liste_tous_les_temps_collision]).T)

np.savetxt(f"PHY-3003/data_vec_xy_with_module_{module}_{orientation}.txt", np.array([liste_temps, liste_vector_x, liste_vector_y]).T)

plt.show()