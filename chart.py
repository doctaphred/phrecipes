from ez import ez


class BarChart(ez):
    """Draw quick bar charts in the terminal!

    >>> chart = BarChart(width=10, ceiling=10, template='{value:>2} [{}]')
    >>> chart
    BarChart(width=10, ceiling=10, template='{value:>2} [{}]')

    >>> for value in range(-1, 12):
    ...     print(chart[value])
    -1 [??????????]
     0 [          ]
     1 [#         ]
     2 [##        ]
     3 [###       ]
     4 [####      ]
     5 [#####     ]
     6 [######    ]
     7 [#######   ]
     8 [########  ]
     9 [######### ]
    10 [##########]
    11 [!!!!!!!!!!]

    >>> print(chart(template='|{}|', width=20)[5])
    |##########          |

    """
    template = '[{}]'
    full = '#'
    empty = ' '
    overflow = '!'
    underflow = '?'
    width = 10
    floor = 0
    ceiling = 1

    def fraction(self, value):
        """
        >>> BarChart(floor=0, ceiling=100).fraction(10)
        0.1
        """
        return (value - self.floor) / (self.ceiling - self.floor)

    def n(self, value):
        """
        >>> f = BarChart(floor=0, ceiling=100).n
        >>> [f(value) for value in range(0, 110, 10)]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> f(100)
        10
        >>> f(50)
        5
        >>> f(10.000000000000001)
        2
        >>> [f(value) for value in [10, 1, 0.1, 0.01, 0.001, 0.001]]
        [1, 1, 1, 1, 1, 1]
        >>> f(0)
        0
        """
        from math import ceil
        return ceil(self.fraction(value) * self.width)

    def bar(self, value):
        """
        >>> f = BarChart(floor=0, ceiling=5, width=2).bar
        >>> [f(value) for value in range(-1, 7)]
        ['??', '  ', '# ', '# ', '##', '##', '##', '!!']
        """
        if value < self.floor:
            return self.underflow * self.width
        elif value > self.ceiling:
            return self.overflow * self.width
        else:
            full = self.n(value)
            empty = self.width - full
            return self.full * full + self.empty * empty

    def __getitem__(self, value):
        return self.template.format(self.bar(value), value=value)
