
import unittest
from tests import cinderDiagnosticsCPGTest, cinderDiagnosticsCredentialsTest,cinderDiagnosticsHp3parclientTest,cinderDiagnosticsISCSITest 



alltests = unittest.TestSuite()
alltests.addTest(unittest.makeSuite(cinderDiagnosticsCPGTest.BadCPGTest))
alltests.addTest(unittest.makeSuite(cinderDiagnosticsCredentialsTest.BadCredentialsTest))
alltests.addTest(unittest.makeSuite(cinderDiagnosticsHp3parclientTest.BadHP3PARClientTest))
alltests.addTest(unittest.makeSuite(cinderDiagnosticsISCSITest.BadISCSITest))
unittest.TextTestRunner(verbosity=2).run(alltests)
