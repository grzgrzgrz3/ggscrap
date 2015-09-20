from base import Control, BaseSender


class Milka(BaseSender):

    def send(self):
        pass

if __name__ == '__main__':
    control = Control(Milka)
    control.loop()
