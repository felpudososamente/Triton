
Al inicio me solía dar este error que no comprendí del todo bien

ValueError: time must be in the interval [2458032.489583333,2458032.510416667]

Sin embargo, el tiempo de la ocultación (2458032.4941898147) ciertamente está en el intervalo
por lo que no entiendo del todo el motivo del error. (Creo que es más un error del paquete sinceramente)

Lo que hice fue localizar el archivo del código fuente core.py 
python3.9/site-packages/sora/occultation/core.py

Y comentar este pedazo:

 if not time.isscalar:
            if any(time < self.min_time) or any(time > self.max_time):
                raise ValueError('time must be in the interval [{},{}]'.format(
                    self.min_time, self.max_time))
        elif time.isscalar:
            if time < self.min_time or time > self.max_time:
                raise ValueError('time must be in the interval [{},{}]'.format(
                    self.min_time, self.max_time))

Luego de eso, el código corrió perfecto.

Como son demasiadas gráficas, lo que hice fue dividirlas todas en diversos directorios organizados
Hay un apartado en el código para que ubiques donde guardas cada una de ellas
Te recomiendo crear las carpetas donde quieres que vaya cada una y luego añadir en el código la ubicación.