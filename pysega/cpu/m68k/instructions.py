class Instructions:

    ASM_MODE = {
        'MODE_DN': '000',
        'MODE_AN': '001'
    }

    def _destination(self, parameters=[]):
        pass

    # Arithmetic Instructions
    def add(self, parameters=[]):
        destination = Instructions._destination(Instructions._destination, parameters[0])

    def sub(self, parameters=[]):
        if (len(parameters)) == 1:
            source = parameters[0][0]
            target = parameters[0][1]
        else:
            source = parameters[1][0]
            target = parameters[1][1]
        destination = 1
        mode = Instructions.ASM_MODE[source[0]]
        print(hex(int('1001'+source[1]+'00'+str(destination)+mode+target[1], 2)))

    def move(self, parameters=[]):
        print(parameters)
        pass
