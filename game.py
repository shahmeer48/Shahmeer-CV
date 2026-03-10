import pygame
import math
import random

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1200, 800
FPS = 60

TRACK_RADIUS = 1800
TRACK_WIDTH = 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NFS Drift Track")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 24, bold=True)

# ---------------- COLORS ----------------
ROAD = (45,45,50)
GRASS = (20,80,20)
WHITE = (255,255,255)
RED = (210,30,30)
CURB_RED = (200,30,30)
CURB_WHITE = (230,230,230)
SMOKE = (220,220,220)
NITRO = (0,255,255)

# ---------------- SKID MARK ----------------
class Skid:
    def __init__(self,x,y,a):
        self.x=x
        self.y=y
        self.a=a
        self.life=500

    def draw(self,surf,cx,cy):
        if self.life>0:
            alpha=int(120*(self.life/500))
            s=pygame.Surface((22,10),pygame.SRCALPHA)
            pygame.draw.rect(s,(0,0,0,alpha),(0,0,22,10))
            r=pygame.transform.rotate(s,-math.degrees(self.a))
            surf.blit(r,(self.x-cx,self.y-cy))
            self.life-=1

# ---------------- SMOKE ----------------
class Particle:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.vx=random.uniform(-2,2)
        self.vy=random.uniform(-2,2)
        self.size=random.randint(8,16)
        self.alpha=200

    def update(self):
        self.x+=self.vx
        self.y+=self.vy
        self.size+=0.4
        self.alpha-=4

# ---------------- CAR ----------------
class Car:
    def __init__(self):
        self.pos=pygame.Vector2(TRACK_RADIUS,0)
        self.vel=pygame.Vector2(0,0)
        self.angle=math.radians(-90)
        self.speed=0
        self.max_speed=35
        self.accel=0.6
        self.friction=0.98
        self.nitro=100
        self.drift=False

    def update(self,keys):

        steer=0.06 if self.speed<10 else 0.09

        if keys[pygame.K_LEFT]:
            self.angle-=steer
        if keys[pygame.K_RIGHT]:
            self.angle+=steer

        if keys[pygame.K_UP]:
            if self.speed<self.max_speed:
                self.speed+=self.accel

            if keys[pygame.K_LSHIFT] and self.nitro>0:
                self.speed+=0.8
                self.nitro-=1.5
        else:
            self.speed*=self.friction

        target=pygame.Vector2(math.cos(self.angle),math.sin(self.angle))*self.speed

        if keys[pygame.K_SPACE] and self.speed>8:
            grip=0.70
            self.drift=True
        else:
            grip=0.92
            self.drift=False

        self.vel=self.vel*grip + target*(1-grip)
        self.pos+=self.vel
        self.speed=self.vel.length()

        # ROAD LIMIT (road se bahir nahi jayega)
        dist=self.pos.length()
        min_r=TRACK_RADIUS-TRACK_WIDTH/2
        max_r=TRACK_RADIUS+TRACK_WIDTH/2

        if dist<min_r:
            self.pos.scale_to_length(min_r)
            self.speed*=0.4

        if dist>max_r:
            self.pos.scale_to_length(max_r)
            self.speed*=0.4

        if self.nitro<100:
            self.nitro+=0.2

    def draw(self,cx,cy):
        car=pygame.Surface((70,40),pygame.SRCALPHA)

        pygame.draw.rect(car,RED,(0,5,65,30),border_radius=8)
        pygame.draw.rect(car,(20,20,20),(18,8,28,20),border_radius=5)
        pygame.draw.rect(car,(255,255,180),(60,8,10,6))
        pygame.draw.rect(car,(255,255,180),(60,24,10,6))

        r=pygame.transform.rotate(car,-math.degrees(self.angle))

        screen.blit(
            r,
            r.get_rect(
                center=(self.pos.x-cx+WIDTH//2,self.pos.y-cy+HEIGHT//2)
            )
        )

# ---------------- INIT ----------------
car=Car()
camera=pygame.Vector2(0,0)
skids=[]
particles=[]

# ---------------- LOOP ----------------
running=True
while running:

    screen.fill(GRASS)

    keys=pygame.key.get_pressed()

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

    car.update(keys)

    # camera follow
    camera.x+= (car.pos.x-camera.x)*0.08
    camera.y+= (car.pos.y-camera.y)*0.08

    cx=WIDTH//2-camera.x
    cy=HEIGHT//2-camera.y

    # -------- TRACK --------
    pygame.draw.circle(screen,ROAD,(int(cx),int(cy)),TRACK_RADIUS+TRACK_WIDTH//2)
    pygame.draw.circle(screen,GRASS,(int(cx),int(cy)),TRACK_RADIUS-TRACK_WIDTH//2)

    # middle line
    pygame.draw.circle(screen,WHITE,(int(cx),int(cy)),TRACK_RADIUS,4)

    # curbs
    pygame.draw.circle(screen,CURB_RED,(int(cx),int(cy)),TRACK_RADIUS+TRACK_WIDTH//2+8,14)
    pygame.draw.circle(screen,CURB_WHITE,(int(cx),int(cy)),TRACK_RADIUS+TRACK_WIDTH//2+8,6)

    pygame.draw.circle(screen,CURB_RED,(int(cx),int(cy)),TRACK_RADIUS-TRACK_WIDTH//2-8,14)
    pygame.draw.circle(screen,CURB_WHITE,(int(cx),int(cy)),TRACK_RADIUS-TRACK_WIDTH//2-8,6)

    # -------- DRIFT EFFECTS --------
    if car.drift:
        skids.append(Skid(car.pos.x,car.pos.y,car.angle))

        for i in range(5):
            particles.append(
                Particle(
                    car.pos.x-math.cos(car.angle)*25,
                    car.pos.y-math.sin(car.angle)*25
                )
            )

    # skid draw
    for s in skids[:]:
        s.draw(screen,camera.x,camera.y)
        if s.life<=0:
            skids.remove(s)

    # smoke draw
    for p in particles[:]:
        p.update()

        surf=pygame.Surface((p.size*2,p.size*2),pygame.SRCALPHA)
        pygame.draw.circle(surf,(220,220,220,p.alpha),(p.size,p.size),p.size)

        screen.blit(
            surf,
            (p.x-camera.x-p.size+WIDTH//2,
             p.y-camera.y-p.size+HEIGHT//2)
        )

        if p.alpha<=0:
            particles.remove(p)

    car.draw(camera.x,camera.y)

    # -------- UI --------
    pygame.draw.rect(screen,(10,10,10),(30,HEIGHT-110,300,90),border_radius=12)

    speed=int(car.speed*12)
    sp=font.render(f"{speed} KM/H",True,WHITE)
    nt=font.render("NITRO",True,NITRO)

    pygame.draw.rect(screen,(40,40,40),(120,HEIGHT-45,160,16))
    pygame.draw.rect(screen,NITRO,(120,HEIGHT-45,car.nitro*1.6,16))

    screen.blit(sp,(50,HEIGHT-95))
    screen.blit(nt,(40,HEIGHT-55))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()