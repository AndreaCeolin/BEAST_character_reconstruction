from collections import Counter

dict = Counter()

i=0
for line in open('table.table.states.log'):
    if i>3:
    	pars = line.split()[-1]
    	new_pars = pars[1:].strip('"')
    	for index, ch in enumerate(new_pars):
       		dict[index] += int(ch)
    i+=1

print(dict.items())
for item in dict.items():
    print(round(item[1]/float(10001),3))