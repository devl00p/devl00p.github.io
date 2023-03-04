data = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do \
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim \
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea \
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit \
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat \
cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id \
est laborum."

class ascii85:
    
    @staticmethod
    def encode(s):
        l = len(s)
        nb_blocks = l / 4
        reste = l % 4

        encoded = ""

        for i in range(0,nb_blocks):
            x = int( s[i*4:(i*4) + 4].encode("hex_codec"), 16)
            if x == 0:
                t = "z"
            else:
                t = ""
                for j in range(0,5):
                    t = chr((x % 85) + 33) + t
                    x = x / 85
            encoded += t

        if reste != 0:
            i = i+1
            x = int( s[i*4:].encode("hex_codec").ljust(8, '0'), 16)
            t = ""
            for j in range(0,5):
                t = chr((x % 85) + 33) + t
                x = x / 85
            encoded += t[:reste+1]

        return encoded

    @staticmethod
    def decode(s):
        s = s.replace('z', "!!!!!")

        l = len(s)
        nb_blocks = l / 5
        reste = l % 5

        encoded = ""

        for i in range(0, nb_blocks):
            j = 0
            x = 0
            block = s[i*5:(i*5) + 5]
            for c in block[::-1]:
                x += (ord(c) - 33) * pow(85,j)
                j = j + 1
            encoded += ("%x" % x).decode("hex_codec")

        if reste != 0:
            i = i+1
            j = 0
            x = 0
            block = s[i*5:(i*5) + 5].ljust(5,"u")
            for c in block[::-1]:
                x += (ord(c) - 33) * pow(85,j)
                j = j + 1
            encoded += ("%x" % x).decode("hex_codec")[:reste-1]
            
        return encoded

if __name__ == "__main__":
    print ascii85.encode(data)
    print
    print ascii85.decode(ascii85.encode(data))