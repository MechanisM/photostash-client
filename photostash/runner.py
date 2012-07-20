import base64
import sys
import subprocess

from clint.textui import puts, columns
from queryset_client import Client
from queryset_client.client import ObjectDoesNotExist
from slumber.exceptions import HttpServerError

from photostash.exceptions import CommandError


class Runner(object):
    DEFULT_BASE_URL = 'http://photostash.herokuapp.com/api/v1/'

    def __init__(self, base_url=None, client=Client, stream=sys.stdout.write):
        if base_url is None:
            base_url = self.DEFULT_BASE_URL
        self.base_url = base_url
        self.client = client(self.base_url)
        self.stream = stream

    def create(self, album_name):
        try:
            album = self.client.albums.objects.create(name=album_name)
            puts('%s has been created.' % album.name, stream=self.stream)
        except HttpServerError:
            raise CommandError('%s already exists.' % album_name)

    def list(self, album_name):
        album = self._get_album(album_name)
        photos = self._get_photos(album)

        ids = ', '.join([str(photo.id) for photo in photos])

        if ids:
            puts('Photos: %s' % ids, stream=self.stream)
        else:
            puts('%s has no photos.' % album.name, stream=self.stream)
            puts('type "stash add %s <path>' % album.name, stream=self.stream)

    def delete(self, album_name, photo_id):
        album = self._get_album(album_name)
        photo = self._get_photo(photo_id)

        try:
            rel = self.client.albumphotos.objects.filter(photo=photo.id, album=album.id)[0]
            rel.delete()
            puts('%s has been removed from %s.' % (photo.id, album.name), stream=self.stream)
        except IndexError:
            raise CommandError('%s doest not belong to %s.' % (photo.id, album.name))

    def add(self, album_name, photo_path):
        album = self._get_album(album_name)

        try:
            with open(photo_path, 'rb') as fp:
                image = '%s:%s' % (photo_path, base64.b64encode(fp.read()))
                photo = self.client.photos.objects.create(image=image)
        except IOError as e:
            try:
                photo = self._get_photo(photo_path)
            except CommandError:
                raise CommandError(e)

        self.client.albumphotos.objects.create(album=album, photo=photo)

        puts('%s has been added to %s.' % (photo.id, album.name), stream=self.stream)

    def open(self, photo_id):
        puts('Opening %s...' % photo_id, stream=self.stream)
        photo = self._get_photo(photo_id)
        subprocess.call(['open', photo.image])

    def stats(self):
        albums = self.client.albums.objects.all()
        stats = sorted((album.name, self._get_photos(album)) for album in albums)

        names = ['| Album'] + ['| {0}'.format(album) for album, photos in stats]
        col1 = ['\n'.join(names), max([len(name) for name in names]) + 1]

        photos = ['| Photos'] + ['| {0}'.format(', '.join([photo.id for photo in photos]))
                  for album, photos in stats]
        col2 = ['\n'.join(photos), max([len(photo) for photo in photos]) + 1]

        col3 = ['\n'.join(['|' for i in range(len(stats) + 1)]), None]
        table = columns(col1, col2, col3)

        rows = table.splitlines()

        header = rows.pop(0)
        divider = '-' * len(header.strip())

        puts(divider, stream=self.stream)
        puts(header, stream=self.stream)
        puts(divider, stream=self.stream)
        puts('\n'.join(rows), stream=self.stream)
        puts(divider, stream=self.stream)

    def _get_album(self, album_name):
        try:
            return self.client.albums.objects.get(name=album_name)
        except ObjectDoesNotExist:
            raise CommandError('Album {0} does not exist. type "stash create '
                               '{0}" to add this album.'.format(album_name))

    def _get_photo(self, photo_id):
        try:
            return self.client.photos.objects.get(id=photo_id)
        except ObjectDoesNotExist:
            raise CommandError('Photo #{0} does not exist.'.format(photo_id))

    def _get_photos(self, album):
        return self.client.photos.objects.filter(albumphotos__album=album.id)
