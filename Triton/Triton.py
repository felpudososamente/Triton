from typing import Any
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import sora
from scipy.fft import fft, fftfreq
from scipy.optimize import curve_fit
from astropy.time import Time
from sora import Occultation, Body, Star, LightCurve, Observer
from sora.ephem import EphemPlanete, EphemHorizons, EphemKernel
from sora.extra import draw_ellipse
import time
import warnings
warnings.filterwarnings('ignore')
inicio = time.time()

#Se inicializan las efemérides
ephem_triton=EphemPlanete(ephem='triton_ephem.txt',name='Triton' , spkid=801) #Geocentricas
#Se inicia el objeto
triton = Body(name='Triton', database=None, spkid=801, orbit_class='satellite' ,ephem=ephem_triton)
#Y la estrella
star_occ = Star(code='2610107911326516992', catalogue='gaiadr2')

#--------Se introduce el tiempo de la ocultación en unidades de fecha juliana
times = '2017-10-05 23:51:38'
t = Time(times)
jd_time=Time(t.jd, format='jd')
print('Fecha:' , t)
print('Fecha Juliana:' ,jd_time)
print(type(jd_time))
#---------------------------------------------------------------------------

#Se declara la ocultación
occ = Occultation(star=star_occ, body=triton, time=jd_time,ephem=ephem_triton)
print(occ)
#Lee el archivo con la información correspondiente a cada observatorio
Lc_data=pd.read_csv('Lc_Data.csv')
#Hay un total de 90 curvas de luz. Como calcular las 90 sería muy demorado, es mejor poner las primeras n

#Número de curvas de luz a analizar. 
n=90

#Número de cuentas que realiza para hacer el ajuste

loop=1000

#Las 90 curvas con 1000 cuentas tarda unas 5 o 6 horas en compilar. 
#Para cálculos cortos recomiendo 5 curvas de luz a 300 cuentas. 


#Se inicialializan los observadores
obs=[]
for i in range(n):
  obs.append(Observer(name=Lc_data['Name'][i],lat=Lc_data['Lat'][i], lon=Lc_data['Lon'][i], height =Lc_data['Altitude'][i]))

#-----------Esta sección es para organizar los nombrse de los archivos en sus respectivas carpetas ---------
#----Es posible compacatarlo más pero a mi me queda más cómodo así por separado

#Ubicación de los archivos .dat de las curvas de luz
data='/home/felipe/Triton/Archivos/'
data_curva=[]
for i in Lc_data['LC']:
  data_nombre=data+i
  data_curva.append(data_nombre)

#Donde guardar las gráficas de las curvas de luz
Lc_pngCdL='/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/CurvasDeLuz/'
ubi_pngCdL=[]
for i in Lc_data['Name']:
  ubicacion_nombre=Lc_pngCdL+i+'.png'
  ubi_pngCdL.append(ubicacion_nombre)

#Aquí guarda las gráficas de las curvas de luz pero con los parámetros calculados de la ocultación
Lc_pngOD='/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/CurvasOccDet/'
ubi_pngOD=[]
for i in Lc_data['Name']:
  ubicacion_nombre=Lc_pngOD+i+'.png'
  ubi_pngOD.append(ubicacion_nombre)

#Acá guarda las curvas de luz ya ajustadas
Lc_pngM='/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/CurvasModeladas/'
ubi_pngM=[]
for i in Lc_data['Name']:
  ubicacion_nombre=Lc_pngM+i+'.png'
  ubi_pngM.append(ubicacion_nombre)

Lc_pngModelos='/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/Modelos/'
ubi_pngModelos=[]
for i in Lc_data['Name']:
  ubicacion_nombre=Lc_pngModelos+i+'.png'
  ubi_pngModelos.append(ubicacion_nombre)


#Guarda las gráficas de la distribución Chi^2 para el ajuste de Inmersión
Chi_imer_ubi='/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/ChiImmersion/'
Chi_imer=[]
for i in Lc_data['Name']:
  ubicacion_nombre=Chi_imer_ubi+i+'.png'
  Chi_imer.append(ubicacion_nombre)

#Guarda las gráficas de la distribución Chi^2 para el ajuste de Emersión
Chi_emer_ubi='/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/ChiEmersion/'
Chi_emer=[]
for i in Lc_data['Name']:
  ubicacion_nombre=Chi_emer_ubi+i+'.png'
  Chi_emer.append(ubicacion_nombre)

#--------------------------Aquí acaba la sección de la ubicación de los archivos-----------------------------------

#Declaramos un vector Lc[] donde se guarda la información de las curvas de luz
Lc=[]

#Y un vector occ_dat[] donde guarda los datos de los parámetros de la ocultación
occ_dat=[]

print('Se están preparando las gráficas')
print('  ')
#Lee los archivos de la curva de luz y los grafica

for i in range(n):
  Lc.append(LightCurve(name=Lc_data['Name'][i], file=data_curva[i],tref='2017-10-05 00:00', exptime=Lc_data['tExp'][i]))
  plt.figure(i)
  occ_dat.append(Lc[i].occ_detect(plot=True))
  plt.xlim([85500,85900])
  name='Curva de luz de ' + Lc_data['Name'][i] 
  plt.title(name)
  plt.legend()
  plt.savefig(ubi_pngCdL[i])
  plt.clf()

#Añade la información de la cuerda
for i in range(n):
  occ.chords.add_chord(name=Lc_data['Name'][i], observer=obs[i], lightcurve=Lc[i])

print('Los observadores que se van a analizar serán:')
for i in (list(occ.chords)):
  print(i)


#Realiza un fit a la curva y obtiene una función Chi^2 de los valores obtenidos vs los valores esperados
out_chi2=[]

print('----------------------------------------------------------')
print('Se va a ajustar cada una de las curvas de luz')
print('Ve por un café, esto va para largo')
print('----------------------------------------------------------')
for i in range(n):
  print('Realizando el ajuste de la curva ',Lc_data['Name'][i])
  out_chi2.append(Lc[i].occ_lcfit(loop=loop))
  num=(n-1)-i
  if num!=0:
    print('   ')
    print('Faltan',num,'curvas para analizar.')
    print('   ')
  else:
    print('   ')
    print('Ya teminó el ajuste de la curva de luz :)')


mid = time.time()
print('   ')
print('Has esperado ',int((mid-inicio)/3600),'horas y' ,  int((mid-inicio)/60)-int((mid-inicio)/3600)*60, 'largos minutos por ahora')
print('    ')
print('----------------------------------------------------------')
print('Falta ahora la elipse')
print('Esta parte también será demorada')
print('Ve por otro café')
print('----------------------------------------------------------')
print('    ')
#Grafica Chi^2 de inmersión
for i in range(n):
  plt.figure(i)
  out_chi2[i].plot_chi2('immersion')
  plt.title(Lc_data['Name'][i])
  plt.savefig(Chi_imer[i])
  plt.clf()

#Grafica Chi^2 de emersión
for i in range(n):
  plt.figure(i)
  out_chi2[i].plot_chi2('emersion')
  plt.title(Lc_data['Name'][i])
  plt.savefig(Chi_emer[i])
  plt.clf()

#Puntos dentro de mask para cada una de las curvas
tmin=[]
tmax=[]
opacity=0.5

#Grafica las curvas de luz con información como los tiempos de inmersión y otros parámetros
for i in range(n):
  plt.figure(i)
  plt.plot(Lc[i].time,Lc[i].flux,'k.-',zorder=1,label='Observation')
  plt.axvline(occ_dat[i]['immersion_time'],color='r',linestyle='-',label='Immersion')
  plt.axvline(occ_dat[i]['emersion_time'],color='r',linestyle='--',label='Emersion')
  plt.xlim([85500,85900])
  plt.legend()
  name='Curva de luz de ' + Lc_data['Name'][i] + 'Con los tiempos de Inmersión y Emersión detectados'
  plt.title(name)
  plt.savefig(ubi_pngOD[i])
  plt.clf()

#Grafica los modelos

for i in range(n):
  plt.figure(i)
  Lc[i].plot_lc()
  name='Modelo de la curva de luz de '+ Lc_data['Name'][i]  +' Luego del ajuste por difracción '
  plt.title(name)
  plt.legend()
  plt.savefig(ubi_pngModelos[i])
  plt.clf()


#Modelos de Inmersión y Emersión

for i in range(n):
  plt.figure(i)
  Lc[i].plot_model()
  name='Ajuste de la emersión de '+Lc_data['Name'][i] + 'Por difracción.'
  plt.title(name)
  plt.xlim([occ_dat[i]['emersion_time']-4, occ_dat[i]['emersion_time']+4])
  plt.ylim([0.8,1.2])
  plt.savefig(ubi_pngM[i])
  plt.clf()



#grafica las cuerdas 
plt.figure()
occ.chords.plot_chords()
occ.chords.plot_chords(segment='error', color='red')
plt.title('Cuerdas para los observadores de Tritón')
plt.legend(ncol=4,frameon=False,labelspacing=0.1, bbox_to_anchor=(1.05, 0.10), loc='')
plt.savefig("/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/Cuerda.png", dpi=1500 , bbox_inches='tight')
plt.clf()


#Realiza el fit de la elipse

ellipse_chi2  = occ.fit_ellipse(center_f=-400, center_g=-650, dcenter_f=250, dcenter_g=250,
                                equatorial_radius=1350 , dequatorial_radius=100, oblateness=0.093,
                                doblateness=0.20, position_angle=90, dposition_angle=90 ,loop=loop*10,
                                dchi_min=10,number_chi=20000 , ellipse_error=50)

print(ellipse_chi2)
plt.figure()
plt.title('Elipse ajustada a las cuerdas de Tritón')
occ.chords.plot_chords()
occ.chords.plot_chords(segment='error', color='red')
draw_ellipse(**ellipse_chi2.get_values())
plt.savefig("/mnt/c/Users/felip/OneDrive/Desktop/Tesis/Triton/Elipse.png")
plt.clf()


#Calcula el tiempo de compilación
fin = time.time()
print('Tardó ',int((fin-inicio)/3600),' horas y' ,  int((fin-inicio)/60)-int((fin-inicio)/3600)*60, 'largos minutos en compilar')
print('Ya terminó :) Agradecemos tu paciencia')