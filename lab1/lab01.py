import sys

from mpi4py import MPI
from time import sleep
from random import randint



comm = MPI.COMM_WORLD

size = comm.size
rank = comm.rank

livi = (rank - 1) % size

desni = (rank + 1) % size

vilice = []

spaces = str(rank) + " " * rank
zahtjevi = []

class Fork:
    def __init__(self, id, dirty, own):
        self.id = id
        self.dirty = dirty
        self.own = own

    def __repr__(self):
        if (self.own):
            return str(self.id) + "/" + str(self.dirty)
        else:
            return ""


def posalji_zahtjeve(comm, vilice, rank, size, space):
    poslani_zahtjevi = []
    livi = (rank - 1) % size
    desni = (rank + 1) % size

    if (own(vilice) == 0):
        comm.send(("Z", rank), dest=livi, tag=99)
        print(spaces + "trazim vilicu (" + str(rank) + ")")
        sys.stdout.flush()
        comm.send(("Z", (rank + 1) % size), dest=desni, tag=99)
        print(spaces + "trazim vilicu (" + str((rank + 1) % size) + ")")
        sys.stdout.flush()
        poslani_zahtjevi.append(livi)
        poslani_zahtjevi.append(desni)
    elif (own(vilice) == 1):
        id = 0
        if (vilice[0].own):
            id = vilice[0].id
        else:
            id = vilice[1].id
        if (id == rank):
            comm.send(("Z", (rank + 1) % size), dest=desni, tag=99)
            print(spaces + "trazim vilicu (" + str((rank + 1) % size) + ")")
            sys.stdout.flush()
            poslani_zahtjevi.append(desni)
        else:
            comm.send(("Z", rank), dest=livi, tag=99)
            print(spaces + "trazim vilicu (" + str(rank) + ")")
            sys.stdout.flush()
            poslani_zahtjevi.append(desni)
    return len(poslani_zahtjevi)


def own(vilice):
    temp = 0
    for vilica in vilice:
        if (vilica.own):
            temp = temp + 1
    return temp


def azuriraj_vilice(id):
    # print(spaces + "azuiram"+str(id))
    for vilica in vilice:
        if (vilica.id == id):
            vilica.own = True
            vilica.dirty = False
    # print(spaces + str(vilice))
    # sys.stdout.flush()

if __name__ == '__main__':

    if (rank == 0):
        vilice.append(Fork(rank, True, True))
        vilice.append(Fork(desni, True, True))
    elif (rank != (size - 1)):
        vilice.append(Fork(rank, True, False))
        vilice.append(Fork(desni, True, True))
    else:
        vilice.append(Fork(rank, True, False))
        vilice.append(Fork(desni, True, False))


    while True:
        print(spaces + "Mislim")
        sys.stdout.flush()
        for i in range(0, randint(3,5)):
            sleep(1)
            if comm.Iprobe(source=livi, tag=99):
                tip, idVilice = comm.recv(source=livi, tag=99)
                if tip == "O":
                    raise Exception(spaces + "Ovo se nebi tribalo dogoditi")
                else:
                    odgovoreno = False
                    for vilica in vilice:
                        if (idVilice != vilica.id):
                            continue
                        if (vilica.own and vilica.dirty):
                            vilica.own = False
                            comm.send(("O", idVilice), dest=livi, tag=99)
                            # print(spaces + "šaljem vilicu (" + str(idVilice) + ")" + str(livi))
                            # print(spaces + str(vilice))
                            # sys.stdout.flush()
                            odgovoreno = True
                    if not odgovoreno:
                        zahtjevi.append((("O", idVilice), livi))
            if comm.Iprobe(source=desni, tag=99):
                tip, idVilice = comm.recv(source=desni, tag=99)
                if tip == "O":
                    raise Exception(spaces + "Ovo se nebi tribalo dogoditi")
                else:
                    odgovoreno = False
                    for vilica in vilice:
                        if (idVilice != vilica.id):
                            continue
                        if (vilica.own and vilica.dirty):
                            vilica.own = False
                            comm.send(("O", idVilice), dest=desni, tag=99)
                            # print(spaces + "šaljem vilicu (" + str(idVilice) + ")" + str(desni))
                            # print(spaces + str(vilice))
                            # sys.stdout.flush()
                            odgovoreno = True
                    if not odgovoreno:
                        zahtjevi.append((("O", idVilice), desni))

        while own(vilice) != 2:
            # print(spaces + str(vilice))
            # sys.stdout.flush()
            poslani_zahtjevi = posalji_zahtjeve(comm, vilice, rank, size, spaces)

            while (poslani_zahtjevi > 0):
                if comm.Iprobe(source=livi, tag=99):
                    tip, idVilice = comm.recv(source=livi, tag=99)
                    if tip == "O":
                        # print(spaces + "primia")
                        # sys.stdout.flush()
                        azuriraj_vilice(idVilice)
                        poslani_zahtjevi = poslani_zahtjevi - 1
                    else:
                        odgovoreno = False
                        for vilica in vilice:
                            if (idVilice != vilica.id):
                                continue
                            if (vilica.own and vilica.dirty):
                                vilica.own = False
                                comm.send(("O", idVilice), dest=livi, tag=99)
                                # print(spaces + "šaljem vilicu (" + str(idVilice) + ")" + str(livi))
                                # print(spaces + str(vilice))
                                # sys.stdout.flush()
                                odgovoreno = True
                        if not odgovoreno:
                            zahtjevi.append((("O", idVilice), livi))
                if comm.Iprobe(source=desni, tag=99):
                    tip, idVilice = comm.recv(source=desni, tag=99)
                    if tip == "O":
                        # print(spaces + "primia")
                        # sys.stdout.flush()
                        azuriraj_vilice(idVilice)
                        poslani_zahtjevi = poslani_zahtjevi - 1
                    else:
                        odgovoreno = False
                        for vilica in vilice:
                            if (idVilice != vilica.id):
                                continue
                            if (vilica.own and vilica.dirty):
                                vilica.own = False
                                comm.send(("O", idVilice), dest=desni, tag=99)
                                # print(spaces + "šaljem vilicu (" + str(idVilice) + ")" + str(desni))
                                # print(spaces + str(vilice))
                                # sys.stdout.flush()
                                odgovoreno = True
                        if not odgovoreno:
                            zahtjevi.append((("O", idVilice), desni))
        print(spaces + "Jedem")
        sys.stdout.flush()
        sleep(1)
        for vilica in vilice:
            vilica.dirty = True
        # print(spaces + str(vilice))
        # print(zahtjevi)
        # sys.stdout.flush()
        for zahtjev, odr in zahtjevi:
            for vilica in vilice:
                if (vilica.id == zahtjev[1]):
                    vilica.own = False
                    comm.send(zahtjev, dest=odr, tag=99)
                    # print(spaces + "šaljem vilicu (" + str(zahtjev[1]) + ")" + str(odr))
                    # print(spaces + str(vilice))
                    # sys.stdout.flush()
        zahtjevi.clear()
