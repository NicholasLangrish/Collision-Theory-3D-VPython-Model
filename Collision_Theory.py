#Library imports 
from vpython import *
from random import randint

scene.background = vec(0.8,0.9,1) #Set background color to light blue

#Build translucent box from (0,0,0) to (100,100,100)
bottom_border = box(pos=vec(50,0,50), size=vec(100,1,100), color=vec(0.8,0.8,0.8), opacity=0.3)
top_border = box(pos=vec(50,100,50), size=vec(100,1,100), color=vec(0.8,0.8,0.8), opacity=0.3)
front_border = box(pos=vec(50,50,0), size=vec(100,100,1), color=vec(0.8,0.8,0.8), opacity=0.3)
back_border = box(pos=vec(50,50,100), size=vec(100,100,1), color=vec(0.8,0.8,0.8), opacity=0.3)
left_border = box(pos=vec(0,50,50), size=vec(1,100,100), color=vec(0.8,0.8,0.8), opacity=0.3)
right_border = box(pos=vec(100,50,50), size=vec(1,100,100), color=vec(0.8,0.8,0.8), opacity=0.3)
x_axis = arrow(pos=vec(0,0,0), axis=vec(100,0,0), shaftwidth=3, headwidth=6, color=color.black)
y_axis = arrow(pos=vec(0,0,0), axis=vec(0,100,0), shaftwidth=3, headwidth=6, color=color.black)
z_axis = arrow(pos=vec(0,0,0), axis=vec(0,0,100), shaftwidth=3, headwidth=6, color=color.black)

#dt is delta time, how much the simulation moves on with each step. t is the current simulation length
dt = 0.01
t=0

#Setting up various basic global variables
reactions = 0
go = False
num_particles = 2
particle_radius = 2
high_vel = 30
low_vel = 10
activation_energy = 0
reactions_per_s = 0

#objects of class particle will be stored in a list
particles = []
velocities = []

#Initialise the graph of rate of reaction
graph(width=600, height=400, title='Rate of reaction against time', xtitle='Time [s]', ytitle='Reactions per second')
r_curve = gcurve(color=color.green)
r_dots = gdots(color=color.green)

#go/pause simulation
def goButtonPressed(b):
    global go
    if not go:
        go = True
        b.text = 'Pause'
    else:
        go = False
        b.text = 'Resume'

#Initialise go button
go_button = button(bind=goButtonPressed, text='Go')

#Reset simulation
def resetButtonPressed(b):
    global go
    global num_particles
    global velocities
    global high_vel
    global low_vel
    global particles
    global particle_radius
    global go_button
    global r_curve
    global r_dots
    global t
    global reactions
    global reactions_per_s

    #Clear graph
    r_curve.data = []
    r_dots.data = []

    t = 0

    reactions = 0
    reactions_per_s = 0
    
    #Make all old particles invisible and remove from particles list
    for i in particles:
        i.object.visible = False
    particles = []

    #Pause simulation until go pressed
    go_button.text = 'Go'
    go = False
    while not go:
        rate(1/dt)

    #Create a random list of velocities for particles
    for i in range(num_particles*3):
        if randint(0,1) == 0:
            velocities.append(randint(-high_vel, -low_vel))
        else:
            velocities.append(randint(low_vel,high_vel))

    #Create particles
    for i in range(num_particles):
        particles.append(Particle(vec(randint(5,95),randint(5,95),randint(5,95)), [velocities[num_particles],velocities[num_particles+1],velocities[num_particles+2]], particle_radius, color.red))

#Return values from sliders to global variables
def particlesSliderUsed(s):
    global num_particles
    num_particles = s.value

def radiusSliderUsed(s):
    global particle_radius
    particle_radius = s.value

def temperatureSliderUsed(s):
    global high_vel
    global low_vel
    high_vel = 20 + int(10 * s.value)
    low_vel = int(10 * s.value)

def activationEnergySliderUsed(s):
    global activation_energy
    activation_energy = 100 * s.value

#Set up GUI (other than go button)    
scene.append_to_caption('                  ')
reset_button = button(bind=resetButtonPressed, text='Reset')
scene.append_to_caption('\n\n')

wtext(text='<b>Results</b>')
scene.append_to_caption('\n\n')

reactions_text = wtext(text=('Reactions: '+str(reactions)))
scene.append_to_caption('\n\n')

rate_text = wtext(text=('Reactions per second: '+str(reactions_per_s)))
scene.append_to_caption('\n\n')

wtext(text='<b>Parameters</b>')
scene.append_to_caption('\n\n')

wtext(text='Select number of particles (2-100)')
scene.append_to_caption('\n\n')

slider(bind=particlesSliderUsed, min=2, max=100, step=2)
scene.append_to_caption('\n\n')

wtext(text='Select particle radius (1-5)')
scene.append_to_caption('\n\n')

slider(bind=radiusSliderUsed, min=1, max=5, step=1)
scene.append_to_caption('\n\n')

wtext(text='Set temperature')
scene.append_to_caption('\n\n')

slider(bind=temperatureSliderUsed)
scene.append_to_caption('\n\n')

wtext(text='Set activation energy (Warning! this value is the percent of the maximum possible activation energy in a perfect collision)')
scene.append_to_caption('\n\n')

slider(bind=activationEnergySliderUsed)
scene.append_to_caption('\n\n')

#Class for standards reactants and particles
class Particle():
    #Initialise vpython object 
    def __init__(self, position, velocity, radius, colour):
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.vz = velocity[2]
        self.mass = (4/3)*pi*radius**3
        self.radius = radius
        self.object = sphere(pos=position, radius=radius, color=colour)
        self.reacted = False

    #Run every dt
    def move(self,l):
        global reactions
        global reactions_per_s
        global reactions_text

        #Actual movement
        self.object.pos.x += self.vx * dt
        self.object.pos.y += self.vy * dt
        self.object.pos.z += self.vz * dt

        #Check for collisions with particles
        for i in l:
            #Calculate distance between particles
            distance = sqrt(abs(self.object.pos.x-i.object.pos.x)**2+abs(self.object.pos.y-i.object.pos.y)**2+abs(self.object.pos.z-i.object.pos.z)**2)
            if distance < 2*self.radius:
                #Reaction will occur
                if not self.reacted and not i.reacted and sqrt(self.vx**2+self.vy**2+self.vz**2)+sqrt(i.vx**2+i.vy**2+i.vz**2) > activation_energy:
                    l.remove(i)
                    i.object.visible = False
                    self.object.color = color.green
                    self.reacted = True
                    self.vx = (self.vx+i.vx)/2
                    self.vy = (self.vy+i.vy)/2
                    self.vz = (self.vz+i.vz)/2
                    reactions += 1
                    reactions_per_s += 1
                    reactions_text.text = 'Reactions: ' + str(reactions)
                    break
                #Reaction will not occur
                else:
                    vx_store = self.vx
                    vy_store = self.vy
                    vz_store = self.vz
                    self.vx = i.vx
                    self.vy = i.vy
                    self.vz = i.vz
                    i.vx = vx_store
                    i.vy = vy_store
                    i.vz = vz_store
                    self.object.pos.x += 0.5
                    self.object.pos.y += 0.5
                    self.object.pos.z += 0.5
                    i.object.pos.x -= 0.5
                    i.object.pos.y -= 0.5
                    i.object.pos.z -= 0.5
                    break

        #Establish borders where the particle is touching the wall
        upper_bound = 100-self.radius
        lower_bound = 0+self.radius    
        
        #Checks if particle is touching outer walls            
        if self.object.pos.x > upper_bound:
            self.vx *= -1
            self.object.pos.x = 95
        elif self.object.pos.x < lower_bound:
            self.vx *= -1
            self.object.pos.x = 5
        if self.object.pos.y > upper_bound:
            self.vy *= -1
            self.object.pos.y = 95
        elif self.object.pos.y < lower_bound:
            self.vy *= -1
            self.object.pos.y = 5
        if self.object.pos.z > upper_bound:
            self.vz *= -1
            self.object.pos.z = 95
        elif self.object.pos.z < lower_bound:
            self.vz *= -1
            self.object.pos.z = 5

        #Return new list of particles (if reaction has occured one of the reactants is removed)
        return l

#Start the simulation
resetButtonPressed(reset_button)

while True:
    rate(1/dt)
    if go:
        #Check if integer number of seconds, and plot graph
        if int(t) == t:
            r_curve.plot(t,reactions_per_s)
            r_dots.plot(t,reactions_per_s)
            reactions_per_s = 0
        #Move all particles
        for i in particles:
            particles.remove(i)
            particles = i.move(particles)
            particles.append(i)
            rate_text.text = 'Reactions per second: ' +str(reactions_per_s)#
        #Time increases by delta time
        t = round(t+dt,2)