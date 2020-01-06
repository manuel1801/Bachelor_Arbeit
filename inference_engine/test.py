
class my_class:
    def __init__(self):
        self.var1 = None
        self.var2 = None
        print('class initialized')

    def initialate_plugin(self, val1, val2):
        self.var1 = val1
        self.var2 = val2
        print('variablen init with ', str(self.var1), str(self.var2))

    def infer_image(self):
        print('doining img inference on ', self.var1)

    def infer_stream(self):
        print('doing inf on stream with ', str(self.var2))


def main():
    a, b = None, None


if __name__ == "__main__":
    main()
