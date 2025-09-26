from mapvbvd import mapVBVD

good = "/Users/asc112/Documents/Pipeline/xenon-siemens-to-mrd-consortium/Patients/Siemens/meas_MID00060_FID00393_Xenon_3D_Radial_Dixon_2echo_2501.dat"
bad  = "/Users/asc112/Documents/Pipeline/Patients/UAB/Day2_Subject/meas_MID00314_FID103582_Xenon_3D_Radial_Dixon.dat"

for p in (good, bad):
    tw = mapVBVD(p)
    obj = tw[-1] if isinstance(tw, list) else tw
    print("\nFile:", p.split("/")[-1])
    print("Phoenix:", bool(getattr(obj.hdr, "Phoenix", {})))
    print("MeasYaps:", bool(getattr(obj.hdr, "MeasYaps", {})))
    if getattr(obj.hdr, "MeasYaps", None) and hasattr(obj.hdr.MeasYaps, 'sWipMemBlock'):
        sw = obj.hdr.MeasYaps.sWipMemBlock
        if hasattr(sw, 'adFree') and len(sw.adFree) > 9:
            print("sWipMemBlock.adFree[9]:", sw.adFree[9])
