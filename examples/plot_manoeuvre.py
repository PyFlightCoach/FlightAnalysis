from flightanalysis import ManDef, SchedDef

from flightanalysis.builders.schedules.baeaglid_intermediate import sdef


md: ManDef = sdef[3]

md.plot().show()
