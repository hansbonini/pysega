class Registers:
    def a(self, value):
        return ['MODE_AN', '{0:03b}'.format(int(value))]

    def d(self, value):
        return ['MODE_DN', '{0:03b}'.format(int(value))]
