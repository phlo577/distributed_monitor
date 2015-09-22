import database
import mock
import unittest

# Tests for Database module
class DatabaseTest(unittest.TestCase):

    @mock.patch('database.create_engine')
    @mock.patch('database.declarative_base')
    @mock.patch('database.sessionmaker')
    def setUp(self,
              mock_sessionmaker,
              mock_declarative_base,
              mock_create_engine):
        super(DatabaseTest, self).setUp()
        self.database = database.Database(mock.sentinel.url)

    @mock.patch('database.create_engine')
    @mock.patch('database.Base')
    @mock.patch('database.sessionmaker')
    def test_init(self,
                  mock_sessionmaker,
                  mock_Base,
                  mock_create_engine):

        # Prepare test
        mock_engine = mock_create_engine.return_value
        mock_DBSession = mock_sessionmaker.return_value

        # Test sequence
        db = database.Database(mock.sentinel.url)

        # Check results
        mock_create_engine.assert_called_once_with(mock.sentinel.url)
        mock_Base.metadata.create_all.assert_called_once_with(mock_engine)
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        self.assertEqual(mock_Base.metadata.bind, mock_engine)
        self.assertEqual(mock_DBSession.return_value, db.session)

    @mock.patch('database.MetricTable')
    def test_set_metric(self,
                        mock_MetricTable):

        # Prepare test
        mock_new_entry = mock_MetricTable.insert.return_value

        # Test sequence
        self.database.set_metric(mock.sentinel.metric,
                                 mock.sentinel.timestamp,
                                 mock.sentinel.host,
                                 mock.sentinel.value)

        # Check results
        mock_MetricTable.insert.assert_called_once_with(host=mock.sentinel.host,
                                                        metric=mock.sentinel.metric,
                                                        timestamp=mock.sentinel.timestamp,
                                                        value=mock.sentinel.value)
        self.database.session.add.assert_called_once_with(mock_new_entry)
        self.database.session.commit.assert_called_once_with()

    def test_close_session(self):

        # Test sequence
        self.database.close_session()

        # Check results
        self.database.session.close_all.assert_called_once_with()

    @mock.patch('database.AvailableMemoryTable')
    def test_set_available_memory(self,
                                  mock_AvailableMemoryTable):

        # Test sequence
        self.database.set_metric(metric='available_memory',
                                 timestamp=mock.sentinel.timestamp,
                                 host=mock.sentinel.host,
                                 value=mock.sentinel.value)
        # Check results
        mock_AvailableMemoryTable.assert_called_once_with(timestamp=mock.sentinel.timestamp,
                                                          host=mock.sentinel.host,
                                                          available_memory=mock.sentinel.value)

    @mock.patch('database.TotalMemoryTable')
    def test_set_total_memory(self,
                              mock_TotalMemoryTable):

        # Test sequence
        self.database.set_metric(metric='total_memory',
                                 timestamp=mock.sentinel.timestamp,
                                 host=mock.sentinel.host,
                                 value=mock.sentinel.value)
        # Check results
        mock_TotalMemoryTable.assert_called_once_with(timestamp=mock.sentinel.timestamp,
                                                      host=mock.sentinel.host,
                                                      total_memory=mock.sentinel.value)

    @mock.patch('database.CpuPercentageTable')
    def test_set_cpu_percentage(self,
                                mock_CpuPercentageTable):

        # Test sequence
        self.database.set_metric(metric='cpu_percentage',
                                 timestamp=mock.sentinel.timestamp,
                                 host=mock.sentinel.host,
                                 value=mock.sentinel.value)
        # Check results
        mock_CpuPercentageTable.assert_called_once_with(timestamp=mock.sentinel.timestamp,
                                                        host=mock.sentinel.host,
                                                        cpu_percentage=mock.sentinel.value)

    @mock.patch('database.NetworkBytesSentTable')
    def test_set_network_bytes_sent(self,
                                    mock_NetworkBytesSentTable):

        # Test sequence
        self.database.set_metric(metric='network_bytes_sent',
                                 timestamp=mock.sentinel.timestamp,
                                 host=mock.sentinel.host,
                                 value=mock.sentinel.value)
        # Check results
        mock_NetworkBytesSentTable.assert_called_once_with(timestamp=mock.sentinel.timestamp,
                                                           host=mock.sentinel.host,
                                                           bytes_sent=mock.sentinel.value)

    @mock.patch('database.NetworkBytesReceivedTable')
    def test_set_network_bytes_received(self,
                                        mock_NetworkBytesReceivedTable):

        # Test sequence
        self.database.set_metric(metric='network_bytes_received',
                                 timestamp=mock.sentinel.timestamp,
                                 host=mock.sentinel.host,
                                 value=mock.sentinel.value)
        # Check results
        mock_NetworkBytesReceivedTable.assert_called_once_with(timestamp=mock.sentinel.timestamp,
                                                               host=mock.sentinel.host,
                                                               bytes_received=mock.sentinel.value)

    @mock.patch('database.DiskReadsPerSecTable')
    def test_set_disk_reads_sec(self,
                                mock_DiskReadsPerSecTable):

        # Test sequence
        self.database.set_metric(metric='disk_reads_sec',
                                 timestamp=mock.sentinel.timestamp,
                                 host=mock.sentinel.host,
                                 value=mock.sentinel.value)
        # Check results
        mock_DiskReadsPerSecTable.assert_called_once_with(timestamp=mock.sentinel.timestamp,
                                                          host=mock.sentinel.host,
                                                          reads_sec=mock.sentinel.value)

    @mock.patch('database.DiskWritesPerSecTable')
    def test_set_disk_writes_sec(self,
                                mock_DiskWritesPerSecTable):

        # Test sequence
        self.database.set_metric(metric='disk_writes_sec',
                                 timestamp=mock.sentinel.timestamp,
                                 host=mock.sentinel.host,
                                 value=mock.sentinel.value)
        # Check results
        mock_DiskWritesPerSecTable.assert_called_once_with(timestamp=mock.sentinel.timestamp,
                                                          host=mock.sentinel.host,
                                                          writes_sec=mock.sentinel.value)
