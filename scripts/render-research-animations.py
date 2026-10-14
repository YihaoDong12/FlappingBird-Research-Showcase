"""Render editorial vector-style diagrams; motions and flow traces are illustrative."""
from pathlib import Path
from PIL import Image, ImageDraw
import math

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
W, H = 1000, 562
N = 80
BG = "#f6f2e9"
INK = "#3e4a4c"
TEAL = "#648f8c"
COPPER = "#ad7952"
GREY = "#b5c0bc"

def arrow(d, a, b, color=INK, width=5, head=12):
    d.line([a, b], fill=color, width=width)
    ang=math.atan2(b[1]-a[1], b[0]-a[0])
    p=[b,(b[0]-head*math.cos(ang-.55),b[1]-head*math.sin(ang-.55)),
       (b[0]-head*math.cos(ang+.55),b[1]-head*math.sin(ang+.55))]
    d.polygon(p, fill=color)

def wing(d, root, scale, phase, membrane=True):
    # A single prescribed flap angle. Ribs remain attached to the same root.
    angle=.47*math.sin(phase)
    points=[(0,0),(.30,-.14),(.85,-.20),(1.30,.04),(1.13,.47),(.73,.64),(.28,.46)]
    out=[]
    for x,y in points:
        # Fixed oblique view of a planar wing rotating about its root axis.
        xx=x*math.cos(angle)-y*math.sin(angle)
        yy=(x*math.sin(angle)+y*math.cos(angle))*.75
        out.append((root[0]+scale*xx,root[1]+scale*yy))
    if membrane:
        d.polygon(out,fill="#e5e5d9")
        for j in range(2,len(out)-1):
            d.polygon([out[0],out[j],out[j+1]],fill=["#e7e7dc","#eeeeE4","#dedfd4"][j%3])
    d.line(out+[out[0]], fill=INK, width=4)
    for p in out[2:]:
        d.line([out[1],p],fill="#6b7671",width=2)
    d.line(out[:4],fill=INK,width=5)
    for p in out[:4]:
        d.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=INK,outline="#f6f2e9",width=1)
    d.ellipse((root[0]-8,root[1]-8,root[0]+8,root[1]+8),fill="#89938e",outline=INK,width=2)

def sensor(d, x, y, s=1):
    def r(box,**kw):
        d.rounded_rectangle(tuple([x+box[0]*s,y+box[1]*s,x+box[2]*s,y+box[3]*s]),**kw)
    r((-38,0,38,45),radius=5,fill="#b5bcb5",outline=INK,width=2)
    r((-58,45,58,58),radius=4,fill="#83908a",outline=INK,width=2)
    for dx in [-25,25]:
        d.ellipse((x+(dx-3)*s,y+18*s,x+(dx+3)*s,y+24*s),fill=INK)

def camera(d,x,y,s=1):
    d.rounded_rectangle((x,y,x+63*s,y+48*s),radius=6,fill=INK)
    d.rectangle((x+63*s,y+9*s,x+87*s,y+39*s),fill="#87958d",outline=INK,width=2)
    d.ellipse((x+78*s,y+8*s,x+99*s,y+40*s),fill=INK)
    d.line([(x+28*s,y+48*s),(x+9*s,y+111*s)],fill=INK,width=3)
    d.line([(x+28*s,y+48*s),(x+58*s,y+111*s)],fill=INK,width=3)
    d.line([(x+28*s,y+48*s),(x+29*s,y+111*s)],fill=INK,width=3)

def pulse(d,a,b,t,color=TEAL):
    d.line([a,b],fill="#c3cfca",width=3)
    for offset in (0,.33,.66):
        q=(t+offset)%1
        x=a[0]+q*(b[0]-a[0]);y=a[1]+q*(b[1]-a[1])
        d.ellipse((x-4,y-4,x+4,y+4),fill=color)

def tunnel(k):
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    ph=2*math.pi*k/N
    d.ellipse((260,420,785,452),fill="#e3e0d6")
    # Clear test section, camera and force balance.
    d.rounded_rectangle((80,83,912,453),radius=17,fill="#f0f0e6",outline="#a8b3ae",width=3)
    d.line([(80,102),(912,102)],fill="#d2d9d2",width=2)
    d.line([(80,433),(912,433)],fill="#c9d2cb",width=3)
    for x in [80,912]:
        d.rectangle((x-8,69,x+8,471),fill="#a4ada5",outline=INK,width=2)
        for y in [92,440]:
            d.ellipse((x-3,y-3,x+3,y+3),fill=INK)
    # Sparse advancing streaks: diagrammatic air direction, not a CFD solution.
    for j in range(6):
        y=155+j*42
        d.line([(108,y),(286,y)],fill="#c6d9d1",width=2)
        xx=110+((k/N+j*.15)%1)*710
        bend=8*math.sin(ph+j)*max(0,(xx-500)/350)
        d.line([(xx,y+bend),(min(xx+35,875),y+bend)],fill=TEAL,width=3)
    sensor(d,385,375)
    d.rectangle((375,299,395,375),fill="#929e95",outline=INK,width=2)
    d.ellipse((315,215,420,318),fill="#b8c0b6",outline=INK,width=3)
    d.arc((322,218,413,314),-85,85,fill="#87948a",width=2)
    wing(d,(413,260),270,ph)
    camera(d,856,340,.9)
    d.line([(856,355),(579,278)],fill="#bac9be",width=2)
    return im

def pinn(k):
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im);ph=2*math.pi*k/N
    # Three equal visual groups with a shared phase and restrained node pulses.
    for x in [32,365,698]:
        d.rounded_rectangle((x,78,x+270,451),radius=14,fill="#f1f0e6",outline="#d4d8cb",width=2)
    camera(d,57,147,.55)
    wing(d,(151,257),91,ph)
    sensor(d,150,345,.7)
    d.line([(150,264),(150,345)],fill=INK,width=3)
    pulse(d,(111,178),(160,228),k/N)
    arrow(d,(309,263),(355,263),color=TEAL,width=6,head=12)
    wing(d,(402,246),157,ph)
    nodes=[(435,130),(480,106),(530,131),(590,110),(622,150),(465,376),(517,401),(577,373),(629,395)]
    for i,a in enumerate(nodes):
        for j,b in enumerate(nodes[i+1:],i+1):
            if math.dist(a,b)<115:
                d.line([a,b],fill="#b9c9bd",width=2)
        if i%2==0:
            pulse(d,a,(507,270),(k/N+i*.07)%1)
        active=(k//10)%len(nodes)==i
        r=6 if active else 4
        d.ellipse((a[0]-r,a[1]-r,a[0]+r,a[1]+r),fill=COPPER if active else TEAL)
    arrow(d,(641,263),(688,263),color=TEAL,width=6,head=12)
    wing(d,(742,246),135,ph)
    arrow(d,(843,238),(843,141),color=TEAL,width=5,head=12)
    arrow(d,(850,277),(932,277),color=COPPER,width=5,head=12)
    sensor(d,810,360,.8)
    d.line([(810,324),(810,360)],fill=INK,width=3)
    arrow(d,(781,355),(781,318),color="#82988f",width=4,head=9)
    return im

def save(name, renderer):
    frames=[renderer(k) for k in range(N)]
    frames[0].save(MEDIA/(name+".png"))
    palette=frames[0].quantize(colors=96,method=Image.Quantize.MEDIANCUT)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(MEDIA/(name+".gif"),save_all=True,append_images=frames[1:],
        duration=80,loop=0,optimize=True,disposal=2)
    print(name, (MEDIA/(name+".gif")).stat().st_size)

if __name__=="__main__":
    save("wind-tunnel-study-animated",tunnel)
    save("pinn-workflow-animated",pinn)
