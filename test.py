z1 =[1,2,3,4,5]
z2 =[5,6,7,8,9,10]
z3 =[1,2,3,5]

zbior = [z1, z2, z3]

out = set(zbior[0]).intersection(*zbior[1:])
print(zbior[1:])
print(out)