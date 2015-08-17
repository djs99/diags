
import unittest
import mock
import time

class BaseCinderDiagnosticsCliToolTest(unittest.TestCase):

    """Base test case class for all 3PAR cinder Diagnostics CLI Tool """


    def _set_ssh_connection_mocks(self):

        client_mock = mock.MagicMock()
        client_mock.connect.return_value = True

        return (self._patch('paramiko.SSHClient'),
                self._patch('paramiko.AutoAddPolicy'),
                client_mock)

    def setUp(self):
         self.mock_instances = []

    def tearDown(self) :
         for mock_instance in self.mock_instances :
             mock_instance.stop()


    def _mock_exec_command(self, return_value):

         c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
         s_mock = self._patch('time.sleep')

         c_mock.return_value = client_mock
         client_mock.exec_command.return_value = [[], client_mock]

         client_mock.read.return_value =  return_value







    def _patch(self, target, **kwargs):
        """
        Returns a started `mock.patch` object for the supplied target.

        The caller may then call the returned patcher to create a mock object.

        The caller does not need to call stop() on the returned
        patcher object, as this method automatically adds a cleanup
        to the test class to stop the patcher.

        :param target: String module.class or module.object expression to patch
        :param **kwargs: Passed as-is to `mock.patch`. See mock documentation
                         for details.
        """
        p = mock.patch(target, **kwargs)
        m = p.start()
        self. mock_instances.append(p)
        return m




