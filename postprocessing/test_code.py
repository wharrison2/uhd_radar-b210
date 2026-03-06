import numpy as np
import matplotlib.pyplot as plt

x=np.array([1,3,6,10,15])
y=np.array([15,10,6,3,1])

plt.figure()
plt.title("Python Plotting Test")
plt.xlabel ("super useful x axis")
plt.ylabel ("super useful y axis")
plt.plot(x,y, label="Cool line")

plt.figure()
x2=np.arange(0,2,0.01)
y2=np.cos(x2*np.pi)
plt.title("Cool Cos Plot")
plt.xlabel ("boring numbers x axis")
plt.ylabel ("Cool cos values y axis")
plt.plot(x2,y2, label="Cosine")

plt.figure()
x2=np.arange(0,2,0.01)
y2=np.sin(x2*np.pi)
plt.title("Silly Sin Plot")
plt.xlabel ("boring numbers x axis")
plt.ylabel ("Silly sin values y axis")
plt.plot(x2,y2, label="Sine")
plt.show()