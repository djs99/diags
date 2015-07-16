
import unittest
from tests import cinderDiagnosticsCPGTest, cinderDiagnosticsCredentialsTest



alltests = unittest.TestSuite()
alltests.addTest(unittest.makeSuite(cinderDiagnosticsCPGTest.BadCPGTest))
alltests.addTest(unittest.makeSuite(cinderDiagnosticsCredentialsTest.BadCredentialsTest))

#bad_cpg_suite = unittest.TestLoader().loadTestsFromTestCase(cinderDiagnosticsCPGTest.BadCPGTest)
#bad_credential_suite = unittest.TestLoader().loadTestsFromTestCase(cinderDiagnosticsCredentialsTest.BadCredentialsTest)
unittest.TextTestRunner(verbosity=2).run(alltests)
