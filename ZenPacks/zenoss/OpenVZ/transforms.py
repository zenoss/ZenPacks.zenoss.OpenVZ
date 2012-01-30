from ZODB.transact import transact

@transact
def remodel(evt, device):
    if device:
        device.collectDevice(setlog=False, background=True)


