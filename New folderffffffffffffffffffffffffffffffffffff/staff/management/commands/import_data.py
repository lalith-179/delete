from django.core.management.base import BaseCommand
from staff.models import film, banner, show
import json
from datetime import datetime, time

class Command(BaseCommand):
    help = 'Import movies, banners, and shows from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing the data')

    def handle(self, *args, **options):
        try:
            with open(options['json_file'], 'r') as file:
                data = json.load(file)
                
                # Import films
                for movie_data in data.get('movies', []):
                    film_obj, created = film.objects.get_or_create(
                        movie_name=movie_data['name'],
                        defaults={
                            'movie_genre': movie_data.get('genre', ''),
                            'movie_lang': movie_data.get('language', ''),
                            'movie_year': movie_data.get('year'),
                            'movie_plot': movie_data.get('plot', ''),
                            'url': movie_data.get('url', '')
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'{"Created" if created else "Updated"} film: {film_obj.movie_name}'))

                # Import banners
                for banner_data in data.get('banners', []):
                    movie = film.objects.get(movie_name=banner_data['movie_name'])
                    banner_obj, created = banner.objects.get_or_create(
                        movie=movie,
                        defaults={
                            'url': banner_data.get('url', '')
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'{"Created" if created else "Updated"} banner for: {movie.movie_name}'))

                # Import shows
                for show_data in data.get('shows', []):
                    movie = film.objects.get(movie_name=show_data['movie_name'])
                    show_obj, created = show.objects.get_or_create(
                        movie=movie,
                        showtime=datetime.strptime(show_data['showtime'], '%H:%M').time(),
                        defaults={
                            'start_date': datetime.strptime(show_data['start_date'], '%Y-%m-%d').date(),
                            'end_date': datetime.strptime(show_data['end_date'], '%Y-%m-%d').date(),
                            'price': show_data['price']
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'{"Created" if created else "Updated"} show for: {movie.movie_name}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}')) 