import uproot
import awkward as ak
import numpy as np
from pathlib import Path

# constants
MIN_PT = 3.0
FILENAME = Path("/ceph/users/atuna/CMSSW_15_1_0_pre2/src/ttbar/n100/trackingNtuple.2025_05_09_10h00m00s.ttbar_PU200.n100.root")
TREENAME = "trackingNtuple/tree"
FIELDS = [
    'simhit_px', 'simhit_py', 'simhit_pz',
    'sim_px', 'sim_py', 'sim_pz', 
    'ph2_isUpper', 'ph2_order', 'ph2_rod',
    'ph2_layer', 'ph2_subdet', 'ph2_side',
    'ph2_module', 'ph2_simHitIdx',
    'ph2_x', 'ph2_y', 'ph2_z', 'ph2_clustSize',
]

def main():

    # file chunker
    step_size = "1 GB"
    iterator = uproot.iterate(f"{FILENAME}:{TREENAME}",
                              expressions=FIELDS,
                              step_size=step_size,
                              )

    # iterate over chunks
    for it, data in enumerate(iterator):

        nph2 = len(ak.flatten(data['ph2_x']))
        print(f"Chunk: {nph2} hits {data}")

        # derived fields
        data["simhit_pt"] = np.sqrt(data.simhit_px**2 + data.simhit_py**2)
        data["ph2_simHitIdxFirst"] = ak.firsts(data.ph2_simHitIdx, axis=-1)
        data["ph2_simhit_pt"]      = data.simhit_pt[data.ph2_simHitIdxFirst]
        data["ph2_simhit_pt"]      = ak.fill_none(data.ph2_simhit_pt, 0.0)

        # filter fields
        fields = [field for field in data.fields if field.startswith("ph2_")]
        data = data[fields]

        # filter entries?
        # mask = data["ph2_simhit_pt"] > MIN_PT
        # data = data[mask]

        # write to file
        ak.to_parquet(data, f"output_{it:02}.parquet")

    # demo: load the data back
    data = ak.from_parquet("output_*parquet")
    nph2 = len(ak.flatten(data["ph2_x"]))
    print("")
    print(f"Reloaded number of ph2 hits: {nph2}")

if __name__ == "__main__":
    main()
