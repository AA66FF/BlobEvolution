"""
blobEvolution.py, my little life simulation project.

Todo:
  Have blobs fire projectiles instead of lasers
  Some level of user interactivity
  Add a HUD to help with above

This program uses the open-source Zelle Graphics library, found at
http://mcsp.wartburg.edu/zelle/python/graphics.py.
"""

from graphics import *
from math import *
from random import *
from time import time,sleep

# Global variables

# Height of the window.
screenHeight = 900
# Width of the window.
screenWidth = 1500
# Velocity of all blobs is multiplied by (1 - this amount) every frame.
drag = 0.01
# Changes the magnitude of mutations. Don't set this too high!
mutationMult = 2
# Changes the magnitude of speed mutations. If 0, speed mutations will not occur.
speedMutationMult = 0.5
# Changes the magnitude of size mutations. If 0, size mutations will not occur.
sizeMutationMult = 0.5
# How different the blobs are from each other at the start.
randomStartMult = 0.1
# How bouncy the edges of the screen are.
wallElasticity = 1.8
# Initial time before plants can generate.
plantCooldown = 200
# Time, in frames, between when each plant spawns.
plantInterval = 30
# The amount of food a plant gives when eaten.
plantFood = 1000
# The base amount of food that meat gives when eaten.
meatFood = 2000
# The percentage of food that a dead blob drops when it dies. (Not actual percent)
meatFoodDroppedMult = 0.45
# How much food a blob gets from eating the wrong kind of food for its diet.
wrongFoodMult = 0.2
# Used in FPS calculations.
frame = 0
# Prey blobs' speed is multiplied by this amount.
aggroFalseBuff = 1.05
# Predator blobs' attack damage, range, and aggro range is multiplied by this amount.
aggroTrueBuff = 1.5
# The amount of food a blob needs to reproduce.
reproThreshold = 10000
# The amount of time blobs have to run away from their parents after they are born.
immunityTime = 600
# How powerful acceleration is.
accMult = 1.2
# How fast blobs are in the start.
speedMult = 0.7
# Affects the top speed of blobs.
speedLimitMod = 60
# Affects the amount of damage and health a blob gets from having a high size.
sizeHealthBuff = 1.4
# How much of a blobs' food ticks away every frame.
metabolismBase = 1.8
# Affects the increased food costs for having high health or speed.
metabolismModMult = 0
# Only used for printing the blob number in the console.
blobNum = 0
# Keeps track if F was pressed last. If true, all blobs vanish, speeding up the sim.
fast = False

blobs = []
plants = []
meat = []
bullets = []

win = GraphWin("Blob Evolution", screenWidth, screenHeight)
win.setBackground(color_rgb(160,230,230))
win.autoflush = False
t = Text(Point(screenWidth-50,20),frame)

def add(v1,v2):
    return [v1[0]+v2[0],v1[1]-v2[1]]

def sub(v1,v2):
    return [v1[0]-v2[0],v1[1]-v2[1]]

def mult(v1,mult):
    return [v1[0]*mult,v1[1]*mult]

def div(v1,div):
    return [v1[0]/div,v1[1]/div]

def dist(v1,v2):
    return sqrt((v1[0]-v2[0])**2+(v1[1]-v2[1])**2)

def normalize(vector):
    deg = 0
    if vector[0] >= 0 and vector[1] < 0:
        deg = atan(vector[0]/-vector[1])
    if vector[0] > 0 and vector[1] >= 0:
        deg = atan(-vector[1]/-vector[0])+radians(90)
    if vector[0] <= 0 and vector[1] > 0:
        deg = atan(vector[0]/-vector[1])+radians(180)
    if vector[0] < 0 and vector[1] <= 0:
        deg = atan(-vector[1]/-vector[0])+radians(270)
    return [sin(deg),-cos(deg)]

def angle(vector):
    deg = 0
    if vector[0] >= 0 and vector[1] < 0:
        deg = atan(vector[0]/-vector[1])
    if vector[0] > 0 and vector[1] >= 0:
        deg = atan(-vector[1]/-vector[0])+radians(90)
    if vector[0] <= 0 and vectorf[1] > 0:
        deg = atan(vector[0]/-vector[1])+radians(180)
    if vector[0] < 0 and vector[1] <= 0:
        deg = atan(-vector[1]/-vector[0])+radians(270)
    return deg

class SubSprite:
    # Part of Sprites. Shapes are drawn here.

    def __init__(self, pos, offset, image, fill="#FFFFFF", outline="#000000",\
    shape="Circle", dest=None):
        self.pos = pos
        self.offset = offset
        self.fill = fill
        self.outline = outline
        self.image = image
        self.shape = shape
        self.dest = dest
        self.image.setOutline(self.outline)
        self.image.setFill(self.fill)

    def draw(self):
        image = self.image
        if self.shape == "Circle":
            image.p1 = Point(self.pos[0]-image.radius,self.pos[1]-image.radius)
            image.p2 = Point(self.pos[0]+image.radius,self.pos[1]+image.radius)
        if self.shape == "Rectangle":
            image.p1 = Point(self.pos[0]+self.offset[0],self.pos[1]\
            +self.offset[1])
            image.p2 = Point(self.pos[0]+self.dest[0],self.pos[1]\
            +self.dest[1])
        if self.shape == "Line":
            image.p1 = Point(self.pos[0]+self.offset[0],self.pos[1]\
            +self.offset[1])
            image.p2 = Point(self.dest[0],self.dest[1])
        image.draw(win)

    def undraw(self):
        self.image.undraw()

    def redraw(self):
        self.undraw()
        self.draw()

class Sprite:
    # Combines all SubSprites into one single Sprite.

    def __init__(self, pos):
        self.pos = pos
        self.subSprites = []

    def addSubsprite(self,offset,image,fill="#FFFFFF",outline="#000000",\
    shape="Circle",dest=None):
        self.subSprites.append(SubSprite(self.pos,offset,image,fill,outline,\
        shape,dest))

    def draw(self):
        subsprites = self.subSprites[i]
        for i in range(len(self.subSprites)):
            subsprites.pos = self.pos
            subsprites.draw()

    def undraw(self):
        for i in range(len(self.subSprites)):
            self.subSprites[i].undraw()

    def redraw(self):
        for i in range(len(self.subSprites)):
            self.subSprites[i].pos = self.pos
            self.subSprites[i].redraw()

class Desire:
    # Blobs use these for desire calculations
    def __init__(self, ident, desire):
        self.ident = ident
        self.pos = self.ident.pos
        self.desire = desire

    def __repr__(self):
        return "{}".format(self.desire)

class Bullet:
    # Blobs shoot these
    def __init__(self):
        self.pos = [0,0]
        self.vel = [0,0]
        self.lifetime = 100
        self.damage = 5

    def draw(self):
        pass

class Blob:
# The main component of the simulation

    def __init__(self, pos):
        self.index = 0
        global blobNum
        blobNum += 1
        # Whether or not the blob will chase other blobs. (boolean)
        self.aggro = False
        # Random stats generation
        r = randint(0,2)
        rm = randomStartMult
        smm = speedMutationMult
        if r == 2:
            self.aggro = True
        # Depending on their aggro value, set their stats accordingly.
        if not self.aggro:
            speed = uniform(0.01-0.002*rm*smm,0.01+0.002*rm*smm)*speedMult\
            *aggroFalseBuff
            aggRange = uniform(50-10*rm,50+10*rm)
            attack = uniform(5-1*rm,5+1*rm)
            attackRange = uniform(40-5*rm,40+5*rm)
            mHealth = uniform(60-10*rm,60+10*rm)
            size = uniform(1-0.05*rm*sizeMutationMult,1+0.05*rm*sizeMutationMult)
        else:
            speed = uniform(0.01-0.002*rm*smm,0.01+0.002*rm*smm)*speedMult
            aggRange = uniform(50-10*rm,50+10*rm)*1.2
            attack = uniform(5-1*rm,5+1*rm)*aggroTrueBuff
            attackRange = uniform(40-5*rm,40+5*rm)*aggroTrueBuff
            mHealth = uniform(60-10*rm,60+10*rm)
            size = uniform(1-0.05*rm*sizeMutationMult,1+0.05*rm*sizeMutationMult)
        # Position vector. (must be list)
        self.pos = pos
        # Velocity vector. (must be list)
        self.vel = [uniform(-1,1),uniform(-1,1)]
        # Acceleration vector.
        self.acc = [0,0]
        # How fast the blob can accelerate. Also affects their speed limit.
        self.speed = speed
        self.effSpd = speed
        # If above 0, blob will run away from the nearest blob.
        self.fear = 0
        # The range of aggro's effect.
        self.aggRange = aggRange
        self.effAggR = aggRange
        # The size of the blob. Currently, is always set to 1.
        self.size = size
        # Amount of food that the blob needs to reproduce.
        self.reproThreshold = reproThreshold
        self.reproTime = 0
        # Number of frames that the blob has been alive.
        self.age = 0
        # The amount of damage the blob does.
        self.attack = attack
        # The distance that the blob can attack other blobs from.
        self.attackRange = attackRange
        self.effAttR = attackRange
        self.effAtt = attack
        if not self.aggro:
            self.effAtt *= 0.5
        self.effSpd /= self.size
        # If 0, the blob can attack.
        self.attackCooldown = 100
        # Maximum health of the blob.
        self.mHealth = mHealth
        self.effMH = mHealth*(size**sizeHealthBuff)
        # Health of the blob. Death happens at 0.
        self.health = self.effMH
        # The amount of food that the blob has. Death happens at 0.
        self.food = reproThreshold/2
        # The amount of food that ticks away every frame.
        self.metabolism = metabolismBase+\
        (self.speed*60+self.mHealth/80)*metabolismModMult
        if not self.aggro:
            self.metabolism /= 1.8
        # If false, blob is deleted from existence.
        self.alive = True
        # These values deal with the AI of the blob.
        self.desires = []
        self.lookingAround = False
        self.justAte = False
        self.target = 0
        self.targetPos = [0,0]
        # These values deal with the graphics.
        if self.aggro:
            self.color = [180,80,80]
        else:
            self.color = [80,180,180]
        self.sprite = Sprite(self.pos)
        self.sprite.addSubsprite([0,0],Circle(Point(self.pos[0],self.pos[1])\
        ,5*self.size),color_rgb(round(self.color[0]),round(self.color[1]),\
        round(self.color[2])),color_rgb(round((self.color[0])/2),round((self.\
        color[1])/2),round((self.color[2])/2)),"Circle",None)
        self.attackTarget = [0,0]
        self.sprite.addSubsprite([0,-4],Line(Point(self.pos[0],\
        self.pos[1]),Point(self.attackTarget[0],self.attackTarget[1]+4)),\
        "#440000","#440000","Line",self.attackTarget)
        self.sprite.addSubsprite([-self.effMH/6,8*self.size],Rectangle(\
        Point(0,0),Point(0,0)),"#900000","#900000","Rectangle",[self.effMH/6,\
        9*self.size])
        self.sprite.addSubsprite([-self.effMH/6,8*self.size],Rectangle(\
        Point(0,0),Point(0,0)),"#009000","#009000","Rectangle",[(-self.effMH\
        +self.health*2)/6,9*self.size])
        self.sprite.addSubsprite([-self.reproThreshold/400,-8*self.size],\
        Rectangle(Point(0,0),Point(0,0)),"#a06000","#a06000","Rectangle",\
        [self.reproThreshold/400,-9*self.size])
        self.sprite.addSubsprite([-self.reproThreshold/400,-8*self.size],\
        Rectangle(Point(0,0),Point(0,0)),"#00eeee","#00eeee","Rectangle",\
        [(-reproThreshold+self.food*2)/400,-9*self.size])

    def __repr__(self):
        return "Blob #{}\n------------------------\n\
Aggro: {}\n\
Speed: {}\n\
Size: {}\n\
Max Health: {}\n\
Attack Damage: {}\n\
Attack Range: {}\n\
Aggro Range: {}\n".format(blobNum,self.aggro,round(self.effSpd,6),\
round(self.size,4),round(self.effMH,2),round(self.effAtt,2),\
round(self.effAttR,2),round(self.effAggR,2))

    def reproduce(self):
        blob = Blob([self.pos[0]+uniform(-1,1),self.pos[1]+uniform(-1,1)])
        r = randint(0,6)
        mm = mutationMult
        smm = speedMutationMult
        szm = sizeMutationMult
        if r == 6:
            rr = random()
            if rr > 0.7:
                blob.aggro = not self.aggro
            else:
                blob.aggro = self.aggro
            blob.speed = self.speed+uniform(-0.0006*mm,0.0006*mm)*smm
            blob.aggRange = self.aggRange+uniform(-3*mm,3*mm)
            blob.size = self.size+uniform(-0.009*mm,0.009*mm)*szm
            blob.attack = self.attack+uniform(-0.6*mm,0.6*mm)
            blob.attackRange = self.attackRange+uniform(-3*mm,3*mm)
            blob.mHealth = self.mHealth+uniform(-6*mm,6*mm)
        else:
            rr = random()
            if rr > 0.9:
                blob.aggro = not self.aggro
            else:
                blob.aggro = self.aggro
            blob.speed = self.speed+uniform(-0.0002*mm,0.0002*mm)*smm
            blob.aggRange = self.aggRange+uniform(-1*mm,1*mm)
            blob.size = self.size+uniform(-0.003*mm,0.003*mm)*szm
            blob.attack = self.attack+uniform(-0.2*mm,0.2*mm)
            blob.attackRange = self.attackRange+uniform(-1*mm,1*mm)
            blob.mHealth = self.mHealth+uniform(-2*mm,2*mm)
        blob.vel = mult(self.vel,-2)
        blobs.append(blob)
        print(blob)

    def calcDesire(self,ident):
        desire = 0
        i = ident
        fpos = i.pos
        if self.aggro:
            if type(i) == Blob and i.aggro:
                desire += 55
            if type(i) == Blob and not i.aggro:
                desire += (i.food/60 + 10)
            if type(i) == Meat:
                desire += (i.food/30 + 20)
            if type(i) == Plant:
                desire += 20
        else:
            if type(i) == Plant:
                desire += 100
            if type(i) == Meat:
                desire += (i.food/50)
        if type(i) == Blob:
            desire += (self.effAtt-i.effAtt)*5
            desire += (self.effSpd-i.effSpd)*50
            desire += (self.health-self.effMH)/self.effMH*80
            desire += (i.effMH-i.health)/i.effMH*30
            if self.effMH > i.effMH:
                desire += (self.effMH-i.effMH)/4
            if self.aggro and not i.aggro:
                desire += 20
            if self.aggro and i.aggro:
                desire -= 10
            if not self.aggro and desire > 0:
                desire /= 10
            if i.age < immunityTime:
                desire = 0
            if self.age < immunityTime:
                desire = -10
        dist = sqrt((self.pos[0]-fpos[0])**2+(self.pos[1]-fpos[1])**2)
        desire *= (1/(dist/self.aggRange))
        if dist > 1.5*self.aggRange:
            desire *= (1/(dist/self.aggRange))
        self.desires.append(Desire(ident,desire))

    def applyForce(self,force):
        # Input force vector, blob moves in that direction.
        f = force
        self.acc[0] += f[0]/(self.size)*accMult
        self.acc[1] += f[1]/(self.size)*accMult

    def applyNegForce(self,force):
        # Input force vector, blob moves in the opposite direction.
        f = force
        self.acc[0] -= f[0]/(self.size)*accMult
        self.acc[1] -= f[1]/(self.size)*accMult

    def AI(self):
        # Deals with most of the blob's decision making.
        self.desires.sort(key=lambda x: x.desire, reverse=True)
        if self.justAte or self.age % 10 == 0:
            self.lookingAround = True
        for i in range(len(self.desires)):
            ipos = self.desires[i].ident.pos
            if (dist(self.pos,ipos) < 8):
                self.applyForce(div(normalize(sub(self.pos,ipos)),5))
        if self.desires[len(self.desires)-1].desire<=-self.desires[0].desire/10:
            ipos = self.desires[len(self.desires)-1].ident.pos
            self.applyForce(mult(normalize(sub(self.pos,ipos)),self.effSpd))
        else:
            ipos = self.desires[0].ident.pos
            self.applyForce(mult(normalize(sub(ipos,self.pos)),self.effSpd))

    def draw(self):
        # Draws the blob's sprite on screen.
        subsprites = self.sprite.subSprites
        subsprites[1].dest = [self.attackTarget[0],\
        self.attackTarget[1]+4]
        subsprites[2].dest = [self.effMH/6,9*self.size]
        subsprites[3].dest = [(-self.effMH\
        +self.health*2)/6,9*self.size]
        subsprites[4].dest = [self.reproThreshold/400,-9*self.size]
        subsprites[5].dest = [(-reproThreshold+self.food*2)/400,\
        -9*self.size]
        self.sprite.redraw()
        if self.age < 2:
            self.sprite.undraw()
        if self.attackCooldown < 120 or self.attackTarget == [0,0]:
            subsprites[1].undraw()

    def update(self):
        # Responsible for making sure all the movement vectors are in the
        # correct range.
        self.vel[0] *= 1-drag
        self.vel[1] *= 1-drag
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[0] += self.acc[0]
        self.vel[1] += self.acc[1]
        self.acc[0] *= 0
        self.acc[1] *= 0
        self.desires = []
        self.food -= self.metabolism
        self.distToClosestBlob = 1000
        self.distToClosestFood = 1000
        if self.pos[0] < 5:
            self.vel[0] *= -wallElasticity
            self.pos[0] += 1
        if self.pos[0] > screenWidth-5:
            self.vel[0] *= -wallElasticity
            self.pos[0] -= 1
        if self.pos[1] < 5:
            self.vel[1] *= -wallElasticity
            self.pos[1] += 1
        if self.pos[1] > screenHeight-5:
            self.vel[1] *= -wallElasticity
            self.pos[1] -= 1
        self.vel[0] = min(max(self.vel[0],-self.effSpd*speedLimitMod),\
        self.effSpd*speedLimitMod)
        self.vel[1] = min(max(self.vel[1],-self.effSpd*speedLimitMod),\
        self.effSpd*speedLimitMod)
        if self.attackCooldown > 0:
            self.attackCooldown -= 3
        if self.food < 1 or self.health < 1:
            self.alive = False
        if self.health > self.effMH:
            self.health = self.effMH
        self.age += 1
        if self.food > self.reproThreshold:
            self.reproTime += 200
            self.food -= self.reproThreshold/2
        if self.reproTime % 200 == 1:
            self.reproduce()
        if self.reproTime > 0:
            self.reproTime -= 1

class Plant:
    # Very simple object. Blobs eat these.
    def __init__(self,pos):
        self.pos = pos
        self.alive = True
        self.c = Circle(Point(pos[0],pos[1]),2)
        self.c.setFill("#20ff20")
        self.c.setOutline("#108f10")
        self.c.draw(win)

class Meat:
    # Simple object. When blobs die, they drop these.
    def __init__(self,pos,food):
        self.pos = pos
        self.food = food
        self.alive = True
        self.c = Circle(Point(pos[0],pos[1]),3)
        self.c.setFill("#ff6b6b")
        self.c.setOutline("#e04444")
        self.c.draw(win)

    def update(self):
        self.food -= 0.5
        if self.food <= 0:
            self.alive = False

for i in range(15):
    # Generate all blobs.
    blobs.append(Blob([uniform(10,screenWidth-10),uniform(10,\
    screenHeight-10)]))
    print(blobs[i])

for i in range(50):
    # Generate 50 plants for the blobs to eat in the start.
    plants.append(Plant([uniform(10,screenWidth-10),\
    uniform(10,screenHeight-10)]))

before = time()
before2 = 0
after = 0

while True:
    # Main loop. Goes on forever.

    # Responsible for the fast functionality; press f to make the blobs
    # disappear.
    if win.lastKey == "f":
        fast = True
    else:
        fast = False
    # Generates plants every plant interval.
    if plantCooldown <= 0:
        plants.append(Plant([uniform(10,screenWidth-10),\
        uniform(10,screenHeight-10)]))
        plantCooldown = plantInterval
    for i in range(len(blobs)):
        blobs[i].index = i
    # The blob loop.
    for i in range(len(blobs)-1, -1, -1):
        # This loop determines desire with all other blobs.
        for j in range(len(blobs)):
            if i != j:
                blobs[i].calcDesire(blobs[j])
        # This loop deals with interactions to all plants.
        for j in range(len(plants)-1, -1, -1):
            blobs[i].calcDesire(plants[j])
            # If they are close enough, eat the plant.
            if dist(blobs[i].pos,plants[j].pos) < 10:
                plants[j].alive = False
                if blobs[i].aggro == False:
                    blobs[i].food += plantFood
                else:
                    blobs[i].food += plantFood*wrongFoodMult
                blobs[i].justAte = True
                blobs[i].health += blobs[i].effMH/6
        # This loop determines distance to all meat.
        for j in range(len(meat)-1, -1, -1):
            blobs[i].calcDesire(meat[j])
            # If they are close enough, eat the meat.
            if dist(blobs[i].pos,meat[j].pos) < 10:
                meat[j].alive = False
                blobs[i].justAte = True
                if blobs[i].aggro == True:
                    blobs[i].food += meat[j].food
                else:
                    blobs[i].food += meat[j].food*wrongFoodMult
                blobs[i].health += blobs[i].effMH
        # Make the blobs react to their desires.
        blobs[i].AI()
        # Attack sequence. If the blob can attack, it will attack the nearest
        # blob to it.
        if type(blobs[i].desires[0].ident) == Blob:
            ident = blobs[i].desires[0].ident
            if blobs[i].attackCooldown <= 0:
                blobs[i].attackTarget = ident.pos
            if dist(blobs[i].pos,ident.pos) < blobs[i].attackRange and\
            ident.age > immunityTime and blobs[i].age > immunityTime and\
            blobs[i].attackCooldown <= 0:
                blobs[i].attackCooldown = 150
                blobs[ident.index].health -= blobs[i].effAtt*\
                (blobs[i].size**sizeHealthBuff)
        # Update blob position, velocity, acceleration, AI values, etc.
        blobs[i].update()
        # If fast mode is active, do not draw any blobs.
        if not fast:
            blobs[i].draw()
        else:
            blobs[i].sprite.undraw()
        # If the blob is dead, delete it and place a meat object at its position.
        if not blobs[i].alive:
            blobs[i].sprite.undraw()
            meat.append(Meat(blobs[i].pos,blobs[i].food*meatFoodDroppedMult\
            +meatFood))
            del blobs[i]
    # Plant loop, only responsible for deleting plants.
    for i in range(len(plants)-1, -1, -1):
        if not plants[i].alive:
            plants[i].c.undraw()
            del plants[i]
    # Meat loop, only responsible for deleting meat.
    if len(meat) > 0:
        for i in range(len(meat)-1, -1, -1):
            meat[i].update()
            if not meat[i].alive:
                meat[i].c.undraw()
                del meat[i]
    plantCooldown -= 1
    frame += 1
    after = time()
    # Drawing for the FPS counter in upper right corner.
    if time()-before >= 1:
        t.undraw()
        t = Text(Point(screenWidth-50,20),"{} FPS".format(frame))
        t.setFill("#000000")
        t.draw(win)
        frame = 0
        before = time()
    win.update()
