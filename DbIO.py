from pathlib import Path
import numpy as np
import psycopg
import pandas as pd
from dissonance.io.symphonytrace import SymphonyEpoch
from dissonance.funks import detect_spikes
import dissonance.io as io

class DBIO:

    cnxnargs = dict(
        dbname="DissonanceDB", 
        user="farchj1", 
        password="mypass", 
        host="localhost", 
        port=5432,
        autocommit=True)

    def __init__(self):
        self.cnxn = psycopg.connect(**self.cnxnargs)

    def insert_epoch(self, fin, epoch:SymphonyEpoch):
        with self.cnxn.cursor() as crs:
            q = self.insert_experimentindex(
                epoch.name, "", "2022-04-25")

            #crs.execute(q)

            exid = crs.execute("""select max(exid) from "RigOutput".experimentindex""").fetchone()[0]

            q = self.insert_params(exid, epoch)
            #crs.execute(q)

            data = np.array(fin[epoch.responses["Amp1"]["path"]]['data'])
            values = np.fromiter([x[0] for x in data], dtype=float)
            args = (
                (exid, epoch.epochnumber, ii, val[0])
                for ii, val in enumerate(data))

            #crs.executemany(self.insert_values(), args)

            if epoch.tracetype == "spiketrace":
                spikeinfo = detect_spikes(values)
                args = ((exid, epoch.epochnumber, int(x)) for x in spikeinfo.sp)
                crs.executemany(self.insert_spikes(), args)

    def insert_spikes(self, exid=None, epid=None, spiketime=None):
        q = """
        INSERT INTO "RigOutput".spikeinfo(exid, epid, spiketime)
        VALUES(%s, %s, %s)
        """

        if None in [exid, epid, spiketime]:
            return q

        else: 
            return q.format(exid, epid, spiketime)

    def insert_experimentindex(self, name, notes, expdate):
        q = """
        INSERT INTO "RigOutput".experimentindex(name, date, notes)
        VALUES('{0}', '{1}', '{2}')
        """.format(name, expdate, notes)
        return q

    def insert_params(self, exid, epoch: SymphonyEpoch):
        q = f"""
        INSERT INTO "RigOutput".params(
                exid,
                epid,
                path,
                cellname,
                startdate,
                celltype,
                tracetype,
                protocolname,
                enddate,
                interpulseinterval,
                led,
                lightamplitude,
                lightmean,
                numberofaverages,
                pretime,
                stimtime,
                samplerate,
                tailtime)
        VALUES(
            {exid:0d},
            {epoch.epochnumber:0d},
            '{epoch.path}',
            '{epoch.cellname}',
            '{epoch.startdate}',
            '{epoch.celltype}',
            '{epoch.tracetype}',
            '{epoch.protocolname}',
            '{epoch.enddate}',
            {epoch.interpulseinterval},
            '{epoch.led}',
            {epoch.lightamplitude},
            {epoch.lightmean},
            {epoch.numberofaverages},
            {epoch.pretime},
            {epoch.stimtime},
            {epoch.samplerate},
            {epoch.tailtime}
        )
        """
        return q

    def insert_values(self):
        q = """
        INSERT INTO "RigOutput".values(exid, epid, time, value)
        VALUES(%s, %s, %s, %s)
        """
        return q


    def __del__(self):
        self.cnxn.close()

path = Path("/home/joe/Projects/DataStore/EPhysData/DR/2021-07-06A.h5")

sr = io.symphonyreader.SymphonyReader(path)

dbio  = DBIO()

for epoch in sr._reader():
    dbio.insert_epoch(sr.fin, epoch)
