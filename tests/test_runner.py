from unittest import TestCase

from mock import patch, Mock, MagicMock
from slumber.exceptions import HttpServerError
from queryset_client.client import ObjectDoesNotExist

from photostash.exceptions import CommandError
from photostash.runner import Runner


class RunnerTestCase(TestCase):

    def setUp(self):
        self.url = 'http://hostname/'
        self.mock_client = Mock()
        self.mock_client_class = Mock(return_value=self.mock_client)
        self.mock_stdout = Mock()
        self.mock_album = Mock()
        self.mock_album.id = 1
        self.mock_album.name = 'myphotos'
        self.mock_photo = Mock(id=1, image='image')
        self.runner = Runner(self.url, self.mock_client_class, self.mock_stdout)

    def test_create_with_valid_data(self):
        self.mock_client.albums.objects.create.return_value = self.mock_album

        self.runner.create(album_name='myphotos')

        self.mock_client.albums.objects.create.assert_called_with(name='myphotos')
        self.mock_stdout.assert_called_with('myphotos has been created.\n')

    def test_create_with_error_raises_command_error(self):
        self.mock_client.albums.objects.create.side_effect = HttpServerError

        with self.assertRaisesRegexp(CommandError, 'myphotos already exists.'):
            self.runner.create(album_name='myphotos')

    def test_list_photos_for_album(self):
        self.mock_client.albums.objects.get.return_value = self.mock_album
        self.mock_client.photos.objects.filter.return_value = [self.mock_photo]

        self.runner.list(album_name='myphotos')

        self.mock_client.photos.objects.filter.assert_called_with(albumphotos__album=1)
        self.mock_stdout.assert_called_with('Photos: 1\n')

    def test_list_with_no_photos(self):
        self.mock_client.albums.objects.get.return_value = self.mock_album
        self.mock_client.photos.objects.filter.return_value = []

        self.runner.list(album_name='myphotos')

        self.mock_stdout.assert_called_with('type "stash add myphotos <path>\n')

    def test_deletes_album_photo(self):
        mock_album_photo = Mock()
        self.mock_client.albums.objects.get.return_value = self.mock_album
        self.mock_client.photos.objects.get.return_value = self.mock_photo
        self.mock_client.albumphotos.objects.filter.return_value = [mock_album_photo]

        self.runner.delete(album_name='myphotos', photo_id=1)

        mock_album_photo.delete.assert_called()
        self.mock_client.albumphotos.objects.filter.assert_called_with(album=1, photo=1)
        self.mock_stdout.assert_called_with('1 has been removed from myphotos.\n')

    def test_delete_when_album_photo_does_not_exist(self):
        self.mock_client.albums.objects.get.return_value = self.mock_album
        self.mock_client.photos.objects.get.return_value = self.mock_photo
        self.mock_client.albumphotos.objects.filter.return_value = []

        with self.assertRaisesRegexp(CommandError, '1 doest not belong to myphotos'):
            self.runner.delete(album_name='myphotos', photo_id=1)

    @patch('__builtin__.open')
    def test_add_with_photo(self, mock_open):
        mock_open.return_value = MagicMock(spec=file)
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = 'content'
        self.mock_client.albums.objects.get.return_value = self.mock_album
        self.mock_client.photos.objects.create.return_value = self.mock_photo

        self.runner.add(album_name='myphotos', photo_path='path')

        self.mock_client.photos.objects.create.assert_called_with(image='path:Y29udGVudA==')
        self.mock_client.albumphotos.objects.create.assert_called_with(
            album=self.mock_album,
            photo=self.mock_photo,
        )
        self.mock_stdout.assert_called_with('1 has been added to myphotos.\n')

    @patch('__builtin__.open')
    def test_add_with_photo_path_does_not_exist(self, mock_open):
        mock_open.side_effect = IOError()
        self.mock_client.photos.objects.get.side_effect = CommandError

        with self.assertRaises(CommandError):
            self.runner.add(album_name='myphotos', photo_path='path')

    def test_add_with_photo_id(self):
        self.mock_client.photos.objects.get.return_value = self.mock_photo

        self.runner.add(album_name='myphotos', photo_path='1')

        self.mock_client.photos.objects.get.assert_called_with(id='1')

    @patch('photostash.runner.subprocess')
    def test_open_calls_subprocess(self, mock_subprocess):
        self.mock_client.photos.objects.get.return_value = self.mock_photo

        self.runner.open(photo_id=1)

        mock_subprocess.call.assert_called_with(['open', self.mock_photo.image])

    def test_get_album_returns_album(self):
        self.mock_client.albums.objects.get.side_effect = ObjectDoesNotExist

        regex = r'Album myphotos does not exist. type "stash create myphotos" to add this album.'
        with self.assertRaisesRegexp(CommandError, regex):
            self.runner._get_album(album_name='myphotos')

    def test_get_photo_returns_album(self):
        self.mock_client.photos.objects.get.side_effect = ObjectDoesNotExist

        regex = r'Photo #1 does not exist.'
        with self.assertRaisesRegexp(CommandError, regex):
            self.runner.delete(album_name='myphotos', photo_id=1)
