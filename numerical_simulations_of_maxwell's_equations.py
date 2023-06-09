# -*- coding: utf-8 -*-
"""Numerical Simulations of Maxwell's Equations

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1drKEzpJ4c0o3NexjAfF-yE_OKQO2iUFA
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from ipywidgets import *
from tqdm import tqdm

"""# Resources:
chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://eecs.wsu.edu/~schneidj/ufdtd/ufdtd.pdf

chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://static.uni-graz.at/fileadmin/_Persoenliche_Webseite/puschnig_peter/unigrazform/Theses/Ohner_FDTD_Bachelorarbeit_final.pdf

"""

"""
YASH MELKANI
This implementation assumes medium that is linear, isotropic and non-disperisve. For now loss is set to zero
Perfectly Matched Layers are not implemented here so boundaries reflect waves.  
Also only working with TE polarization right now
"""

epsilon = 8.854187817e-12  
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # s
grid_size = (500, 500) # x by y
nt = 3000 # number of timesteps

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*10, 50*10) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))

nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))
# ex_history = np.zeros((nt, *Ex.shape))


for i in range(nt):
    # update E
    Ex[:, 1:-1] = Ex[:, 1:-1] + (dt/(epsilon * dy)) * \
    (Hz[:, 1:] - Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = Ey[1:-1, :] - (dt/(epsilon * dx)) * \
    (Hz[1:, :] - Hz[:-1, :]) # y comp update
    # add E source

    # update H
    Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - \
    (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    Hz[200,:] += 2*np.exp(-(1/20000)*(i-1250)**2)

    #save history
    hz_history[i, :, :] = Hz
    # ex_history[i, :, :] = Ex

"""
YASH MELKANI
Code for cool plotting stuff
"""

def plot_hz_history(ts):
    # plt.imshow(ex_history[ts,:,:])
    plt.imshow(hz_history[ts,:,:])
    plt.colorbar()
    plt.show()


interact(plot_hz_history, ts= widgets.IntSlider(value=1, min=0, max=nt-1, step=1));

# Animations
fig = plt.figure()
image = plt.imshow(hz_history[0,:,:], vmin = 0, vmax = 1)
def updatefig(i):
    image.set_array(hz_history[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=50)

# save gif to notebook files
# ani.save('original_example.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())

"""## Including Loss & PMLs"""

"""
YASH MELKANI
This implementation assumes medium that is linear, isotropic and non-disperisve.  
Also only working with TE polarization right now
"""

epsilon = 8.854187817e-12  
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # i think this is s

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*10, 50*10) # x by y


Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))

Hzx = np.zeros(Hz.shape)
Hzy = np.zeros(Hz.shape)

sigma_x = np.zeros(Ey.shape)
sigma_y = np.zeros(Ex.shape)

pml_len = 20 # width of a pml layer
R_0 = 1e6 # The reflection coeff at the boundaries of the computational space (edge of our simulation)
m = 3
sigma_max_x = -np.log(R_0) * c * (m+1) / (2 * np.sqrt(mu/epsilon) * pml_len * dx) 
sigma_max_y = -np.log(R_0) * c * (m+1) / (2 * np.sqrt(mu/epsilon) * pml_len * dy) 
for i in range(pml_len):
    sigma_x[i,:] = sigma_max_x * ((pml_len - i) / pml_len)**m
    sigma_x[-1-i,:] = sigma_max_x * ((pml_len - i) / pml_len)**m
    sigma_y[i:] = sigma_max_y * ((pml_len - i) / pml_len)**m
    sigma_y[-1-i,:] = sigma_max_y * ((pml_len - i) / pml_len)**m

nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))

for i in tqdm(range(nt)):
    # update E
    Ex[:, 1:-1] = (2*epsilon - sigma_y[:, 1:-1] * dt) / (2*epsilon + sigma_y[:, 1:-1] * dt) * Ex[:, 1:-1] \
    + (2*dt / ((2*epsilon + sigma_y[:, 1:-1] * dt) * dy)) * (Hz[:, 1:] - Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = (2*epsilon - sigma_x[1:-1, :] * dt) / (2*epsilon + sigma_x[1:-1, :] * dt) * Ey[1:-1, :] \
    - (2*dt / ((2*epsilon + sigma_x[1:-1, :] * dt) * dx)) * (Hz[1:, :] - Hz[:-1, :]) # y comp update
    
    # add E source

    # update H
    Hzx = (2*mu - sigma_x[1:, :] * dt) / (2*mu + sigma_x[1:, :] * dt) * Hzx \
    - (2*dt / ((2*mu + sigma_x[1:, :] * dt) * dx)) * (Ey[1:, :] - Ey[:-1, :])
    Hzy = (2*mu - sigma_y[:, 1:] * dt) / (2*mu + sigma_y[:, 1:] * dt) * Hzy \
    + (2*dt / ((2*mu + sigma_y[:, 1:] * dt) * dy)) * (Ex[:, 1:] - Ex[:, :-1])

    Hz = Hzx + Hzy

    # add H source
    Hzx[200,200] += 2*np.exp(-(1/20000)*(i-1250)**2)

    #save history
    hz_history[i, :, :] = Hz

"""
YASH MELKANI
Code for cool plotting stuff
"""

def plot_hz_history(ts):
    # plt.imshow(ex_history[ts,:,:])
    plt.imshow(hz_history[ts,:,:])
    plt.colorbar()
    plt.show()


interact(plot_hz_history, ts= widgets.IntSlider(value=1, min=0, max=nt-1, step=1));

"""## DEMO: WAVE REFLECTION AT BOUNDARY OF TWO MATERIALS"""

"""
OWEN DOYLE
TEz polarization, with planar source and with normal incidence to boundary of two media.
"""
epsilon = 8.854187817e-12
epsilon2 = 10*epsilon
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # i think this is s

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*10, 50*10) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))



# metal wall with pinhole(s)
epsilon_grid = np.ones((grid_size[0] - 1, grid_size[1] - 1))*epsilon
epsilon_grid[(grid_size[0])//2:, :] = epsilon2


nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))
# ex_history = np.zeros((nt, *Ex.shape))


for i in range(nt):
    # update E
    Ex[:, 1:-1] = Ex[:, 1:-1] + (dt/(epsilon_grid[:, :-1] * dy)) * (Hz[:, 1:] - Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = Ey[1:-1, :] - (dt/(epsilon_grid[1:, :] * dx)) * (Hz[1:, :] - Hz[:-1, :]) # y comp update
   
    # add E source

    # update H
    Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    Hz[0,:] += 2*np.exp(-(1/1000)*(i-500)**2)

    #save history
    hz_history[i, :, :] = Hz

hz_history_plane = hz_history

def plot_hz_history(ts):
    plt.imshow(hz_history_plane[ts,:,:], vmin = 0, vmax = 2)
    plt.colorbar()
    plt.show()

interact(plot_hz_history, ts= widgets.IntSlider(value=1, min=0, max=nt-1, step=1));

Magnitude_incident = sum(sum(hz_history[700, :, :]))
Magnitude_reflect  = sum(sum(hz_history[1500, :(grid_size[0])//2, :]))
Magnitude_transmit = sum(sum(hz_history[1500, (grid_size[0])//2:, :]))

print(Magnitude_incident)
print(Magnitude_reflect)
print(Magnitude_transmit)
print("---")

Reflection_Coeff = Magnitude_reflect/Magnitude_incident
Transmission_Coeff = Magnitude_transmit/Magnitude_incident

print("Reflection_Coeff", Reflection_Coeff)
print("Transmission_Coeff", Transmission_Coeff)

(0.5194938532959157 - 0.5194934801516027)/0.5194938532959157 *100

(0.4805061467040843 - 0.48050651984838416)/0.4805061467040843*100

Magnitude_incident = sum(sum(hz_history[700, :, :]))
Magnitude_reflect  = sum(sum(hz_history[1500, :(grid_size[0])//2, :]))
Magnitude_transmit = sum(sum(hz_history[1500, (grid_size[0])//2:, :]))

Reflection_Coeff = Magnitude_reflect/Magnitude_incident
Transmission_Coeff = Magnitude_transmit/Magnitude_incident

print("Reflection_Coeff", Reflection_Coeff)
print("Transmission_Coeff", Transmission_Coeff)



"""TODO (MAYBE?): CALCULATE REFLECTION COEFFICIENT FROM ABOVE DATA"""

# Animations
fig = plt.figure()
image = plt.imshow(hz_history[0,:,:], vmin = 0, vmax = 2)
def updatefig(i):
    image.set_array(hz_history[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=60)

# save gif to notebook files
# ani.save('two_materials.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())



"""## DEMO: PINHOLE"""

"""
OWEN DOYLE
TEz polarization, with planar source and with normal incidence to metal plate with pinholes.
"""

epsilon = 8.854187817e-12
epsilon2 = np.Inf
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # i think this is s

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*10, 50*10) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))



# metal wall with pinhole(s)
hole_n = 1
hole_w = 10
hole_loc = np.linspace(0,grid_size[1]-1,hole_n+2).astype(int)[1:-1]
hole_mask = np.zeros(grid_size[1]-1)
hole_mask[hole_loc] = 1
hole_mask = np.convolve(np.ones(hole_w), hole_mask, mode="same")
hole_mask = abs(hole_mask - 1)
hole_mask = hole_mask.astype(bool)

epsilon_grid = np.ones((grid_size[0] - 1, grid_size[1] - 1))*epsilon
epsilon_grid[(grid_size[0]//2)-5:grid_size[0]//2, hole_mask] = epsilon2


nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))
# ex_history = np.zeros((nt, *Ex.shape))


for i in range(nt):
    # update E
    Ex[:, 1:-1] = Ex[:, 1:-1] + (dt/(epsilon_grid[:, :-1] * dy)) * (Hz[:, 1:] - Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = Ey[1:-1, :] - (dt/(epsilon_grid[1:, :] * dx)) * (Hz[1:, :] - Hz[:-1, :]) # y comp update
   
    # add E source

    # update H
    Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    Hz[0,:] += 2*np.exp(-(1/1000)*(i-500)**2)

    #save history
    hz_history[i, :, :] = Hz

hz_history_pinhole = hz_history

def plot_hz_history(ts):
    plt.imshow(hz_history_pinhole[ts,:,:], vmin = 0, vmax = 2)
    plt.colorbar()
    plt.show()


interact(plot_hz_history, ts= widgets.IntSlider(value=1, min=0, max=nt-1, step=1));

# Animations
fig = plt.figure()
image = plt.imshow(hz_history[0,:,:], vmin = 0, vmax = 2)
def updatefig(i):
    image.set_array(hz_history[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=50)

# save gif to notebook files
ani.save('pinhole10.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())

"""## DEMO: STATIC"""

"""
OWEN DOYLE
TEz polarization, STATIC.
"""
epsilon = 8.854187817e-12
# epsilon2 = 10*epsilon
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # i think this is s

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*10, 50*10) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))



# metal wall with pinhole(s)
epsilon_grid = np.ones((grid_size[0] - 1, grid_size[1] - 1))*epsilon
# epsilon_grid[(grid_size[0])//2:, :] = epsilon2


nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))
# ex_history = np.zeros((nt, *Ex.shape))


for i in range(nt):
    # update E
    Ex[:, 1:-1] = Ex[:, 1:-1] + (dt/(epsilon_grid[:, :-1] * dy)) * (Hz[:, 1:] - Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = Ey[1:-1, :] - (dt/(epsilon_grid[1:, :] * dx)) * (Hz[1:, :] - Hz[:-1, :]) # y comp update
   
    # add E source

    # update H
    Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    Hz[250,250] = 2 #*np.exp(-(1/1000)*(i-500)**2)

    #save history
    hz_history[i, :, :] = Hz

hz_history_static = hz_history

def plot_hz_history(ts):
    plt.imshow(hz_history_static[ts,:,:], vmin = 0, vmax = 2)
    plt.colorbar()
    plt.show()


interact(plot_hz_history, ts= widgets.IntSlider(value=1, min=0, max=nt-1, step=1));

# Animations
fig = plt.figure()
image = plt.imshow(hz_history_static[0,:,:], vmin = 0, vmax = 2)
def updatefig(i):
    image.set_array(hz_history_static[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=50)

# save gif to notebook files
# ani.save('static.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())

"""## 3D"""

"""
OWEN DOYLE
TEz polarization, 3D.
"""
epsilon = 8.854187817e-12
# epsilon2 = 10*epsilon
mu = 4 * np.pi * 1e-7
condE = 0 # electric conductivity
condH = 0 # magnetic conductivity

c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dz = 0.1 # m
if dx == dy and dy == dz:
    delta = dx

dt = 1e-10 # i think this is s

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50, 50, 50) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1],     grid_size[2]))
Ey = np.zeros((grid_size[0],     grid_size[1] - 1, grid_size[2]))
Ez = np.zeros((grid_size[0],     grid_size[1],    grid_size[2] - 1))


Hx = np.zeros((grid_size[0],     grid_size[1] - 1, grid_size[2] - 1))
Hy = np.zeros((grid_size[0] - 1, grid_size[1],     grid_size[2] - 1))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1, grid_size[2]))


Chxh = (1-(condH*dt)/(2*mu)) / (1+(condH*dt)/(2*mu))
Chyh = Chxh
Chzh = Chxh
Chxe = 1/(1+(condH*dt)/(2*mu)) * dt/(mu*delta)
Chye = Chxe
Chze = Chxe

Cexe = (1-(condE*dt)/(2*epsilon)) / (1+(condE*dt)/(2*epsilon))
Ceye = Cexe
Ceze = Cexe
Cexh = 1/(1+(condE*dt)/(2*mu)) * dt/(epsilon*delta)
Ceyh = Cexh
Cezh = Cexh

# metal wall with pinhole(s)
# epsilon_grid = np.ones((grid_size[0] - 1, grid_size[1] - 1))*epsilon
# epsilon_grid[(grid_size[0])//2:, :] = epsilon2


nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))
# ex_history = np.zeros((nt, *Ex.shape))


for i in range(nt):
    # update E
    Ex[:, 1:-1, 1:-1] = Cexe*Ex[:, 1:-1, 1:-1] + Cexh*((Hz[:,1:,:] - Hz[:,:-1,:]) - (Hy[:,:,1:] - Hy[:,:,:-1]))
    Ey[1:-1, :, 1:-1] = Ceye*Ey[1:-1, :, 1:-1] + Ceyh*((Hx[:,:,1:] - Hx[:,:,:-1]) - (Hz[1:,:,:] - Hz[:-1,:,:]))
    Ez[1:-1, 1:-1, :] = Ceze*Ez[1:-1, 1:-1, :] + Cezh*((Hy[1:,:,:] - Hy[:-1,:,:]) - (Hx[:,1:,:] - Hx[:,:-1,:]))
    # add E source

    # update H
    Hx = Chxh*Hx[:,:,:] + Chxe*((Ey[:,:,1:] - Ey[:,:,:-1]) - (Ez[:,1:,:] - Ez[:,:-1,:]))
    Hy = Chyh*Hy[:,:,:] + Chye*((Ez[1:,:,:] - Ez[:-1,:,:]) - (Ex[:,:,1:] - Ex[:,:,:-1]))
    Hz = Chzh*Hz[:,:,:] + Chze*((Ex[:,1:,:] - Ex[:,:-1,:]) - (Ey[1:,:,:] - Ey[:-1,:,:]))

#     Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    Hz[0,:] += 2*np.exp(-(1/1000)*(i-500)**2)

    #save history
    hz_history[i, :, :] = Hz

hz_history_3D = hz_history

# Animations
fig = plt.figure()
image = plt.imshow(hz_history_3D[0,:,:], vmin = 0, vmax = 2)
def updatefig(i):
    image.set_array(hz_history_3D[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=50)

# save gif to notebook files
#ani.save('two_materials.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())

"""# DEMO: Antenna Beamforming





"""

"""
LUKE ANDERSON
Phased Array Beamforming using point sources with an offset phase
"""
epsilon = 8.854187817e-12
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # i think this is s

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*5, 50*15) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))

nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))

for i in range(nt):
    # update E
    Ex[:, 1:-1] = Ex[:, 1:-1] + (dt/(epsilon * dy)) * (Hz[:, 1:] - Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = Ey[1:-1, :] - (dt/(epsilon * dx)) * (Hz[1:, :] - Hz[:-1, :]) # y comp update
    # add E source

    # update H
    Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    def gaussian(x, y, delay):
      Hz[x, y] += 10*np.exp(-0.0005*(i-delay)**2)

    for j in range(10, grid_size[0], grid_size[0] // 8):
        gaussian(j, 0, 2000)
        gaussian(j, 0, j)
        gaussian(j, 0, 1200 - j)


    #save history
    hz_history[i, :, :] = Hz

# Animations
fig = plt.figure()
image = plt.imshow(hz_history[0,:,:], vmin = 0, vmax = 1)
def updatefig(i):
    image.set_array(hz_history[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=50)

# save gif to notebook files
# ani.save('beamforming.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())

"""# DEMO: Parabolic Dish"""

"""
LUKE ANDERSON
A plane wave signal being collected and focused by a parabolic reflector
"""
epsilon = 8.854187817e-12
epsilon2 = np.Inf
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # i think this is s

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*10, 50*10) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))

# Parabola
epsilon_grid = np.ones((grid_size[0] - 1, grid_size[1] - 1))*epsilon
for i in range(50, grid_size[0] - 50):
    for j in range(grid_size[1] - 1):
      if j > 400 - ((i - 250) / 18 )**2:
        epsilon_grid[i, j] = epsilon2

nt = 3000 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))

for i in range(nt):
    # update E
    Ex[:, 1:-1] = Ex[:, 1:-1] + (dt/(epsilon_grid[:, :-1] * dy)) * (Hz[:, 1:] - Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = Ey[1:-1, :] - (dt/(epsilon_grid[1:, :] * dx)) * (Hz[1:, :] - Hz[:-1, :]) # y comp update
    # add E source

    # update H
    Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    def gaussian(x, y, delay):
      Hz[x, y] += 2*np.exp(-(1/20000)*(i-250)**2)

    for l in range (0, grid_size[0] - 1):
      gaussian(l, 0, 0)

    #save history
    hz_history[i, :, :] = Hz

def plot_hz_history(ts):
    plt.imshow(hz_history[ts,:,:], vmin = 0, vmax = 5)
    plt.colorbar()
    plt.show()


interact(plot_hz_history, ts= widgets.IntSlider(value=1, min=0, max=nt-1, step=1));

# Animations
fig = plt.figure()
image = plt.imshow(hz_history[0,:,:], vmin = 0, vmax = 5)
def updatefig(i):
    image.set_array(hz_history[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=60)

# save gif to notebook files
# ani.save('parabola.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())

"""# Propagation in a lossy medium"""

"""
LUKE ANDERSON
An antenna array propagating through a lossy medium
"""
epsilon = 8.854187817e-12  
mu = 4 * np.pi * 1e-7
c = 1/np.sqrt(epsilon*mu) # m/s
dx = 0.1 # m
dy = 0.1 # m
dt = 1e-10 # i think this is s

# Adjust loss based on material properties (use 0 for free space)
loss = 0.015
loss_coef_E = (1 - loss) / (1 + loss)
loss_coef_H = 1 / (1 + loss)

if dt > 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)):
    print(dt, 1 / (c * np.sqrt(1/dx**2 + 1/dy**2)))
    print("dt not small enough given c, dx, dy")

grid_size = (50*10, 50*10) # x by y

Ex = np.zeros((grid_size[0] - 1, grid_size[1]))
Ey = np.zeros((grid_size[0], grid_size[1] - 1))
Ez = np.zeros((grid_size[0], grid_size[1]))

Hx = np.zeros((grid_size[0], grid_size[1]))
Hy = np.zeros((grid_size[0], grid_size[1]))
Hz = np.zeros((grid_size[0] - 1, grid_size[1] - 1))

nt = 1700 # number of timesteps

hz_history = np.zeros((nt, *Hz.shape))

for i in range(nt):
  
    # update E
    Ex[:, 1:-1] = Ex[:, 1:-1] + loss_coef_E * (dt/(epsilon * dy)) * (Hz[:, 1:] - loss_coef_H * Hz[:, :-1]) # x comp update
    Ey[1:-1, :] = Ey[1:-1, :] - loss_coef_E * (dt/(epsilon * dx)) * (Hz[1:, :] - loss_coef_H * Hz[:-1, :]) # y comp update

    # add E source

    # update H
    Hz[:, :] = Hz[:, :] + (dt/(mu * dy)) * (Ex[:, 1:] - Ex[:, :-1]) - (dt/(mu * dx)) * (Ey[1:, :] - Ey[:-1, :])

    # add H source
    def gaussian(x, y, delay):
      Hz[x, y] += 50*np.exp(-0.001*(i-delay)**2)

    gaussian(0, 0, 0)

    #save history
    hz_history[i, :, :] = Hz

# Animations
fig = plt.figure()
image = plt.imshow(hz_history[0,:,:], vmin = 0, vmax = 2)
def updatefig(i):
    image.set_array(hz_history[i,:,:])
    return [image]
plt.close()
# Begin Animation
ani = animation.FuncAnimation(fig, updatefig, frames=range(0, nt, 20), interval=60)

# save gif to notebook files
# ani.save('lossy.gif')

from IPython.display import HTML
HTML(ani.to_jshtml())