stuNumber = 4003110
p = 174440041
q = 997525853
e = 11
print(f"My Student Number = {stuNumber}")
print(f"p = {p}")
print(f"q = {q}")
print(f"e = {e}")



n = p * q
print(f"Finding n")
print(f"n = {p} * {q} = {n}")

ɸn = (p - 1) * (q - 1)
print(f"Finding ɸn")
print(f"ɸn = ({p} - 1) * ({q} - 1)")
print(f"ɸn = {ɸn}")

d = pow(e, -1, ɸn)
print(f"Finding d")
print(f"d = {e}^-1 mod {ɸn}")
print(f"d = {d}")

s = pow(stuNumber, d, n)
print(f"Signing")
print(f"s = {stuNumber}^{d} mod {n}")
print(f"s = {s}")



stuNumberVerified = pow(s, e, n)
print(f"Verification")
print(f"M'' = {s}^{e} mod {n}")
print(f"M'' = {stuNumberVerified}")
