##########################################################################
#
#   Copyright 2011 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin


class OpenVZ(CommandPlugin):
    command = "TODO"

    def process(self, device, results, log):
        for x in results.split('\n'):
            log.info(x)
