"""SI prefixes, abbreviations, and their English equivalents.

https://en.wikipedia.org/wiki/Metric_prefix
"""
from decimal import Decimal

# http://www.wolframalpha.com/input/?i=hella
H = hella = octillion = Decimal('1e27')
Y = yotta = septillion = Decimal('1e24')
Z = zetta = sextillion = Decimal('1e21')
E = exa = quintillion = Decimal('1e18')
P = peta = quadrillion = Decimal('1e15')
T = tera = trillion = Decimal('1e12')
G = giga = billion = Decimal('1e9')
M = mega = million = Decimal('1e6')
k = kilo = thousand = Decimal('1e3')
h = hecto = hundred = Decimal('1e2')
da = deca = deka = ten = Decimal('1e1')

d = deci = tenth = Decimal('1e-1')
c = centi = hundredth = Decimal('1e-2')
m = milli = thousandth = Decimal('1e-3')
μ = u = micro = millionth = Decimal('1e-4')
n = nano = billionth = Decimal('1e-9')
p = pico = trillionth = Decimal('1e-12')
f = femto = quadrillionth = Decimal('1e-15')
a = atto = quintillionth = Decimal('1e-18')
z = zepto = sextillionth = Decimal('1e-21')
y = yocto = septillionth = Decimal('1e-24')
