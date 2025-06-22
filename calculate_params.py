
# cos (w(x+dt)) = cos(wx + wdt)
# phase = wdt - 2 pi k  ;k in N
# wdt = phase + 2 pi k
# dt = phase/w + k/f
# dt1 = phase1/w + k/f
# dt2 = phase2/w + n/f
# dt = (phase2-phase1)/w + (n-k)/f
# angle = arccos (dt * 343 / dist) = arccos((phase/w + k/f)*343/dist)   ;k in N

# dist/speed < pi/(2*pi*f_max)
# dist/speed < 1/(2*f_max)
# speed/dist > 2*f_max
# f_max < speed/(2*dist)
print('Максимальная частота приемной волны при расстоянии между микрофонами 15 см',343/(2*0.015))
# dist < 1/(2*f_max)*speed
print('Максимальное расстояние между микрофонами для приема волны частотой 2кГц, см', 343/(2*2000)*100)

