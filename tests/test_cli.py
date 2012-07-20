from unittest import TestCase

from mock import patch, Mock

from photostash.cli import main, sys
from photostash.exceptions import CommandError


class TestCli(TestCase):

    def call_command(self, args, runner=None):
        if runner is None:
            runner = Mock()
        main(argv=args, runner_class=Mock(return_value=runner))
        return runner

    def test_create_album(self):
        runner = self.call_command(['stash', 'create', 'album'])
        runner.create.assert_called_with(album_name='album')

    def test_list_photo_for_album(self):
        runner = self.call_command(['stash', 'list', 'album'])
        runner.list.assert_called_with(album_name='album')

    def test_delete_photo_from_album(self):
        runner = self.call_command(['stash', 'delete', 'album', 'id'])
        runner.delete.assert_called_with(album_name='album', photo_id='id')

    def test_add_photo_to_album(self):
        runner = self.call_command(['stash', 'add', 'album', 'path'])
        runner.add.assert_called_with(album_name='album', photo_path='path')

    @patch.object(sys, 'exit')
    @patch.object(sys, 'stderr')
    def test_handles_validation_errors(self, mock_stderr, mock_exit):
        runner = Mock()
        runner.create.side_effect = CommandError('Error message')
        self.call_command(['stash', 'create', 'invalid name'], runner=runner)
        mock_exit.called_with(1)
        mock_stderr.write.called_with('Error message')
